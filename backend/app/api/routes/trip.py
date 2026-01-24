"""旅行规划API路由"""

import secrets
import asyncio
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends
from loguru import logger

from ...models.schemas import (
    TripRequest,
    TripPlanResponse,
    ErrorResponse
)
from ...agents.trip_planner_agent import get_trip_planner_agent
from ...middleware.auth_middleware import get_current_user_optional, CurrentUser
from ...services.travel_plan_service import get_travel_plan_service
from ...services.image_service import get_image_service

router = APIRouter(prefix="/trip", tags=["旅行规划"])


@router.post(
    "/plan",
    response_model=TripPlanResponse,
    summary="生成旅行计划",
    description="根据用户输入的旅行需求,生成详细的旅行计划。支持匿名和登录用户。"
)
async def plan_trip(
    request: TripRequest,
    current_user: Optional[CurrentUser] = Depends(get_current_user_optional)
):
    """
    生成旅行计划

    支持可选认证：
    - 匿名用户：生成计划并返回，不保存
    - 登录用户：生成计划，自动保存到MongoDB，返回plan_id

    Args:
        request: 旅行请求参数
        current_user: 当前用户（可选）

    Returns:
        旅行计划响应
    """
    try:
        # 判断用户类型
        is_authenticated = current_user is not None

        logger.info(
            f"{'='*60}\n"
            f"📥 收到旅行规划请求:\n"
            f"   城市: {request.city}\n"
            f"   日期: {request.start_date} - {request.end_date}\n"
            f"   天数: {request.travel_days}\n"
            f"   用户: {'已登录 (' + current_user.username + ')' if is_authenticated else '匿名'}\n"
            f"{'='*60}"
        )

        # 获取Agent实例
        logger.debug("🔄 获取多智能体系统实例...")
        agent = get_trip_planner_agent()

        # 生成旅行计划
        logger.info("🚀 开始生成旅行计划...")
        trip_plan = agent.plan_trip(request)

        logger.info("✅ 旅行计划生成成功")

        # 获取并上传景点图片到 OSS
        logger.info("📸 开始获取景点图片...")
        await process_attraction_images(trip_plan, request.city)
        logger.info("✅ 景点图片处理完成")

        # 如果用户已登录，保存计划到MongoDB
        plan_id = None
        session_id = None

        if is_authenticated:
            try:
                # 生成会话ID（为Phase 3对话系统准备）
                session_id = f"session_{secrets.token_urlsafe(16)}"

                # 保存计划
                plan_service = get_travel_plan_service()
                plan_id = await plan_service.save_plan(
                    user_id=current_user.id,
                    session_id=session_id,
                    city=request.city,
                    start_date=request.start_date,
                    trip_plan=trip_plan.model_dump(),
                    preferences={
                        "travel_days": request.travel_days,
                        "end_date": request.end_date
                    }
                )

                logger.info(f"✅ 计划已保存: {plan_id} (用户: {current_user.username})")

            except Exception as e:
                # 保存失败不影响返回计划
                logger.error(f"⚠️  保存计划失败: {str(e)}")

        # 构建响应
        response_data = trip_plan.model_dump()
        response_data["plan_id"] = plan_id  # 仅登录用户有此字段
        response_data["session_id"] = session_id  # 仅登录用户有此字段

        return TripPlanResponse(
            success=True,
            message="旅行计划生成成功" + (" (已保存)" if plan_id else ""),
            data=response_data
        )

    except Exception as e:
        logger.error(f"❌ 生成旅行计划失败: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"生成旅行计划失败: {str(e)}"
        )


@router.get(
    "/health",
    summary="健康检查",
    description="检查旅行规划服务是否正常"
)
async def health_check():
    """健康检查"""
    try:
        # 检查Agent是否可用
        agent = get_trip_planner_agent()

        return {
            "status": "healthy",
            "service": "trip-planner",
            "agent_name": agent.agent.name,
            "tools_count": len(agent.agent.list_tools())
        }
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"服务不可用: {str(e)}"
        )


async def process_attraction_images(trip_plan, city: str):
    """
    处理旅行计划中的景点图片

    为每个景点获取图片并上传到 OSS

    Args:
        trip_plan: 旅行计划对象
        city: 城市名称
    """
    try:
        image_service = get_image_service()

        # 获取所有天的行程
        days = trip_plan.days if hasattr(trip_plan, 'days') else []

        # 收集所有需要获取图片的景点
        tasks = []
        attraction_refs = []  # 保存景点引用，用于后续更新

        for day in days:
            if hasattr(day, 'attractions') and day.attractions:
                for attraction in day.attractions:
                    # 只处理还没有图片的景点
                    if not getattr(attraction, 'image_url', None):
                        attraction_name = getattr(attraction, 'name', '')
                        if attraction_name:
                            # 创建异步任务
                            task = image_service.get_and_upload_attraction_image(
                                attraction_name,
                                city
                            )
                            tasks.append(task)
                            attraction_refs.append(attraction)

        if not tasks:
            logger.info("没有需要获取图片的景点")
            return

        logger.info(f"开始获取 {len(tasks)} 个景点的图片...")

        # 并发获取所有图片（限制并发数为 5）
        results = []
        for i in range(0, len(tasks), 5):
            batch = tasks[i:i+5]
            batch_results = await asyncio.gather(*batch, return_exceptions=True)
            results.extend(batch_results)

        # 更新景点的图片 URL
        success_count = 0
        for attraction, result in zip(attraction_refs, results):
            if isinstance(result, str) and result:
                # 成功获取图片
                attraction.image_url = result
                success_count += 1
            elif isinstance(result, Exception):
                logger.error(f"获取景点图片失败: {attraction.name}, 错误: {str(result)}")
            else:
                logger.warning(f"未获取到景点图片: {attraction.name}")

        logger.info(f"成功获取 {success_count}/{len(tasks)} 个景点的图片")

    except Exception as e:
        logger.error(f"处理景点图片失败: {str(e)}")
        # 不抛出异常，图片获取失败不应该影响整个旅行计划的生成

