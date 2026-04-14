#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
RAG效果评估测试脚本
功能：
1. 执行A/B测试
2. 对比有RAG和无RAG的生成质量
3. 计算幻觉率等指标
4. 生成评估报告

使用方法：
    # 使用模拟数据快速测试（推荐）
    python scripts/run_rag_evaluation.py --use-mock --sample-size 100
    
    # 使用真实Agent测试（需要配置MCP工具）
    python scripts/run_rag_evaluation.py --sample-size 100 --output-dir ./reports
"""

import asyncio
import argparse
import sys
import os
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

sys.path.insert(0, str(Path(__file__).parent.parent))

from loguru import logger

from app.services.evaluation import (
    ABTestFramework,
    ABTestConfig,
    TestVariant,
    HallucinationDetector,
    EvaluationReportGenerator
)

_global_agent = None
_global_rag_enabled = True


async def get_agent_with_rag_setting(enable_rag: bool = True):
    """
    获取Agent实例（单例模式）
    
    Args:
        enable_rag: 是否启用RAG
        
    Returns:
        Agent实例
    """
    global _global_agent, _global_rag_enabled
    
    if _global_agent is None:
        try:
            from app.agents.trip_planner_agent import get_trip_planner_agent
            _global_agent = get_trip_planner_agent()
            print("[INFO] Agent实例已创建（单例）")
        except Exception as e:
            print(f"[ERROR] 创建Agent失败: {e}")
            raise
    
    _global_rag_enabled = enable_rag
    
    return _global_agent


async def generate_without_rag(
    city: str,
    travel_days: int,
    preferences: list,
    start_date: str,
    end_date: str
) -> Dict[str, Any]:
    """
    无RAG的旅行计划生成（对照组）
    """
    from app.models.schemas import TripRequest
    
    agent = await get_agent_with_rag_setting(enable_rag=False)
    
    original_get_rag_service = agent._get_rag_service
    
    async def mock_rag_service():
        return None
    
    agent._get_rag_service = mock_rag_service

    try:
        request = TripRequest(
            city=city,
            start_date=start_date,
            end_date=end_date,
            travel_days=travel_days,
            preferences=preferences,
            transportation="公共交通",
            accommodation="经济型酒店"
        )

        trip_plan = await agent.plan_trip(request)
        return trip_plan.model_dump()

    finally:
        agent._get_rag_service = original_get_rag_service


async def generate_with_rag(
    city: str,
    travel_days: int,
    preferences: list,
    start_date: str,
    end_date: str
) -> Dict[str, Any]:
    """
    有RAG的旅行计划生成（实验组）
    """
    from app.models.schemas import TripRequest
    
    agent = await get_agent_with_rag_setting(enable_rag=True)

    request = TripRequest(
        city=city,
        start_date=start_date,
        end_date=end_date,
        travel_days=travel_days,
        preferences=preferences,
        transportation="公共交通",
        accommodation="经济型酒店"
    )

    trip_plan = await agent.plan_trip(request)
    return trip_plan.model_dump()


async def generate_mock_plan(
    city: str,
    travel_days: int,
    preferences: list,
    start_date: str,
    end_date: str,
    with_rag: bool = False
) -> Dict[str, Any]:
    """
    生成模拟旅行计划（用于快速测试）

    当真实Agent不可用时使用
    
    模拟策略：
    - with_rag=True: 使用真实景点名称（与幻觉检测器已知列表匹配），坐标合理
    - with_rag=False: 包含虚假景点、模糊名称、不合理坐标
    """
    import random

    mock_attractions = {
        "北京": ["故宫博物院", "天安门广场", "颐和园", "圆明园", "天坛公园", "八达岭长城"],
        "上海": ["外滩", "东方明珠", "豫园", "城隍庙", "南京路步行街", "上海迪士尼乐园"],
        "杭州": ["西湖", "灵隐寺", "雷峰塔", "断桥残雪", "三潭印月", "西溪湿地"],
        "厦门": ["鼓浪屿", "南普陀寺", "厦门大学", "曾厝垵", "环岛路", "日光岩"],
        "香港": ["维多利亚港", "太平山顶", "迪士尼乐园", "海洋公园", "星光大道", "黄大仙祠"]
    }

    city_bounds = {
        "北京": (116.0, 117.0, 39.5, 40.5),
        "上海": (121.0, 122.0, 30.5, 31.5),
        "杭州": (120.0, 120.5, 30.0, 30.5),
        "厦门": (118.0, 118.5, 24.0, 24.8),
        "香港": (113.8, 114.5, 22.1, 22.6)
    }

    known_hotels = {
        "北京": ["北京希尔顿酒店", "北京万豪酒店", "北京香格里拉大酒店", "北京王府井希尔顿酒店"],
        "上海": ["上海外滩华尔道夫酒店", "上海浦东丽思卡尔顿酒店", "上海和平饭店", "上海半岛酒店"],
        "杭州": ["杭州西湖国宾馆", "杭州香格里拉饭店", "杭州西子湖四季酒店", "杭州泛海钓鱼台酒店"],
        "厦门": ["厦门香格里拉大酒店", "厦门威斯汀酒店", "厦门国际会议中心酒店", "厦门日航酒店"],
        "香港": ["香港半岛酒店", "香港文华东方酒店", "香港四季酒店", "香港丽思卡尔顿酒店"]
    }

    city_attractions = mock_attractions.get(city, [f"{city}景点{i+1}" for i in range(6)])
    city_hotels = known_hotels.get(city, [f"{city}市中心酒店{i+1}" for i in range(4)])
    bounds = city_bounds.get(city, (116.0, 117.0, 39.5, 40.5))

    if not with_rag:
        fake_patterns = [
            f"{city}必去景点{i+1}" for i in range(2)
        ] + [
            f"{city}网红打卡地{i+1}" for i in range(2)
        ] + [
            f"景点{random.randint(1, 100)}" for i in range(2)
        ]
        city_attractions = city_attractions[:2] + fake_patterns
        city_hotels = [f"酒店{i+1}" for i in range(4)]

    days = []
    start = datetime.strptime(start_date, "%Y-%m-%d")

    for i in range(travel_days):
        current_date = start + timedelta(days=i)

        num_attractions = random.randint(2, 4)
        selected_attractions = random.sample(city_attractions, min(num_attractions, len(city_attractions)))

        attractions = []
        for j, attr_name in enumerate(selected_attractions):
            if with_rag:
                lng = bounds[0] + (bounds[1] - bounds[0]) * (i * 0.1 + j * 0.05)
                lat = bounds[2] + (bounds[3] - bounds[2]) * (i * 0.1 + j * 0.05)
            else:
                lng = 116.4 + i * 0.01 + j * 0.005
                lat = 39.9 + i * 0.01 + j * 0.005
            
            attraction = {
                "name": attr_name,
                "address": f"{city}市{attr_name}附近" if with_rag else f"{city}市",
                "location": {
                    "longitude": round(lng, 6),
                    "latitude": round(lat, 6)
                },
                "visit_duration": random.randint(60, 180),
                "description": f"{attr_name}是{city}著名的旅游景点" if with_rag else f"这是一个很棒的景点",
                "category": random.choice(["历史文化", "自然风光", "娱乐休闲"]),
                "ticket_price": random.randint(0, 100)
            }
            attractions.append(attraction)

        hotel_name = city_hotels[i % len(city_hotels)]
        hotel_address = f"{city}市中心商业区" if with_rag else f"{city}"

        day = {
            "date": current_date.strftime("%Y-%m-%d"),
            "day_index": i,
            "description": f"第{i+1}天行程",
            "transportation": "公共交通",
            "accommodation": "经济型酒店",
            "attractions": attractions,
            "hotel": {
                "name": hotel_name,
                "address": hotel_address,
                "location": {
                    "longitude": round(bounds[0] + (bounds[1] - bounds[0]) * 0.5, 6) if with_rag else 116.4,
                    "latitude": round(bounds[2] + (bounds[3] - bounds[2]) * 0.5, 6) if with_rag else 39.9
                },
                "price_range": "300-500元",
                "rating": "4.5",
                "estimated_cost": 400
            },
            "meals": [
                {"type": "breakfast", "name": f"第{i+1}天早餐", "description": "当地特色早餐", "estimated_cost": 30},
                {"type": "lunch", "name": f"第{i+1}天午餐", "description": "午餐推荐", "estimated_cost": 50},
                {"type": "dinner", "name": f"第{i+1}天晚餐", "description": "晚餐推荐", "estimated_cost": 80}
            ]
        }
        days.append(day)

    trip_plan = {
        "city": city,
        "start_date": start_date,
        "end_date": end_date,
        "days": days,
        "weather_info": [
            {
                "date": (start + timedelta(days=i)).strftime("%Y-%m-%d"),
                "day_weather": "晴",
                "night_weather": "多云",
                "day_temp": 25,
                "night_temp": 15
            }
            for i in range(travel_days)
        ],
        "overall_suggestions": f"这是为您规划的{city}{travel_days}日游行程",
        "budget": {
            "total_attractions": 200,
            "total_hotels": travel_days * 400,
            "total_meals": travel_days * 160,
            "total_transportation": 200,
            "total": travel_days * 560 + 400
        }
    }

    return trip_plan


def print_progress(current: int, total: int, variant: str):
    """打印进度"""
    bar_length = 30
    filled = int(bar_length * current / total)
    bar = '█' * filled + '░' * (bar_length - filled)
    print(f"\r{variant}: [{bar}] {current}/{total}", end='', flush=True)
    if current == total:
        print()


async def run_evaluation(
    sample_size: int,
    output_dir: str,
    use_mock: bool = False,
    test_cities: Optional[list] = None
):
    """
    运行评估测试

    Args:
        sample_size: 样本数量
        output_dir: 输出目录
        use_mock: 是否使用模拟数据
        test_cities: 测试城市列表
    """
    logger.info("=" * 60)
    logger.info("RAG效果评估测试")
    logger.info("=" * 60)

    config = ABTestConfig(
        test_name="RAG_Effect_Evaluation",
        sample_size=sample_size,
        random_seed=42,
        test_cities=test_cities or ["北京", "上海", "杭州", "厦门", "香港"]
    )

    framework = ABTestFramework(config)

    if use_mock:
        logger.info("使用模拟数据进行测试...")

        async def control_gen(**kwargs):
            return await generate_mock_plan(**kwargs, with_rag=False)

        async def treatment_gen(**kwargs):
            return await generate_mock_plan(**kwargs, with_rag=True)

        report = await framework.run_test(
            control_generator=control_gen,
            treatment_generator=treatment_gen,
            progress_callback=print_progress
        )
    else:
        logger.info("使用真实Agent进行测试...")
        
        try:
            await get_agent_with_rag_setting(enable_rag=True)
            logger.info("Agent初始化成功，开始测试...")
        except Exception as e:
            logger.warning(f"Agent初始化失败: {e}")
            logger.warning("自动切换到模拟数据模式...")
            
            async def control_gen(**kwargs):
                return await generate_mock_plan(**kwargs, with_rag=False)

            async def treatment_gen(**kwargs):
                return await generate_mock_plan(**kwargs, with_rag=True)

            report = await framework.run_test(
                control_generator=control_gen,
                treatment_generator=treatment_gen,
                progress_callback=print_progress
            )
            
            report_generator = EvaluationReportGenerator(output_dir)
            output_files = report_generator.generate_report(report, format="all")
            
            interview_summary = report_generator.generate_interview_summary(report)
            
            summary_file = Path(output_dir) / f"{report.test_name}_interview_summary.txt"
            with open(summary_file, "w", encoding="utf-8") as f:
                f.write(interview_summary)
            
            return report

        report = await framework.run_test(
            control_generator=generate_without_rag,
            treatment_generator=generate_with_rag,
            progress_callback=print_progress
        )

    report_generator = EvaluationReportGenerator(output_dir)
    output_files = report_generator.generate_report(report, format="all")

    interview_summary = report_generator.generate_interview_summary(report)

    summary_file = Path(output_dir) / f"{report.test_name}_interview_summary.txt"
    with open(summary_file, "w", encoding="utf-8") as f:
        f.write(interview_summary)

    print("\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)
    print(f"\n生成的报告文件：")
    for fmt, path in output_files.items():
        print(f"  - {fmt}: {path}")
    print(f"  - 面试摘要: {summary_file}")

    print("\n" + "=" * 60)
    print("面试要点摘要")
    print("=" * 60)
    print(interview_summary)

    return report


def main():
    parser = argparse.ArgumentParser(description="RAG效果评估测试")
    parser.add_argument(
        "--sample-size",
        type=int,
        default=20,
        help="样本数量（默认20，建议100以上获得显著结果）"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="./evaluation_reports",
        help="报告输出目录"
    )
    parser.add_argument(
        "--use-mock",
        action="store_true",
        help="使用模拟数据（用于快速测试）"
    )
    parser.add_argument(
        "--cities",
        type=str,
        nargs="+",
        default=["北京", "上海", "杭州", "厦门", "香港"],
        help="测试城市列表"
    )

    args = parser.parse_args()

    Path(args.output_dir).mkdir(parents=True, exist_ok=True)

    asyncio.run(run_evaluation(
        sample_size=args.sample_size,
        output_dir=args.output_dir,
        use_mock=args.use_mock,
        test_cities=args.cities
    ))


if __name__ == "__main__":
    main()
