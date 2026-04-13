"""
幻觉检测器
功能：
1. 检测旅行计划中的虚假景点
2. 检测不存在的酒店
3. 检测错误的地理位置
4. 检测不合理的行程安排
5. 计算幻觉率指标

幻觉类型：
- FAKE_ATTRACTION: 虚假景点（不存在的景点）
- FAKE_HOTEL: 虚假酒店
- WRONG_LOCATION: 错误的地理位置
- UNREASONABLE_SCHEDULE: 不合理的行程安排
- FAKE_FOOD: 虚假美食推荐
"""

import re
import json
import asyncio
from typing import List, Dict, Optional, Any, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from loguru import logger
from pathlib import Path


class HallucinationType(Enum):
    """幻觉类型"""
    FAKE_ATTRACTION = "fake_attraction"
    FAKE_HOTEL = "fake_hotel"
    WRONG_LOCATION = "wrong_location"
    UNREASONABLE_SCHEDULE = "unreasonable_schedule"
    FAKE_FOOD = "fake_food"
    WRONG_COORDINATES = "wrong_coordinates"
    IMPOSSIBLE_DISTANCE = "impossible_distance"


@dataclass
class HallucinationIssue:
    """幻觉问题详情"""
    type: HallucinationType
    description: str
    item_name: str
    severity: str  # high, medium, low
    confidence: float  # 0.0 - 1.0
    evidence: str = ""
    suggestion: str = ""


@dataclass
class HallucinationResult:
    """幻觉检测结果"""
    has_hallucination: bool
    hallucination_count: int
    issues: List[HallucinationIssue]
    hallucination_rate: float
    details: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "has_hallucination": self.has_hallucination,
            "hallucination_count": self.hallucination_count,
            "hallucination_rate": self.hallucination_rate,
            "issues": [
                {
                    "type": issue.type.value,
                    "description": issue.description,
                    "item_name": issue.item_name,
                    "severity": issue.severity,
                    "confidence": issue.confidence,
                    "evidence": issue.evidence,
                    "suggestion": issue.suggestion
                }
                for issue in self.issues
            ],
            "details": self.details
        }


class HallucinationDetector:
    """
    幻觉检测器

    检测策略：
    1. 知识库验证 - 与已知景点/酒店数据库比对
    2. 地理合理性检查 - 验证坐标是否在城市范围内
    3. 时间合理性检查 - 验证行程时间是否合理
    4. 名称模式检测 - 检测可疑的命名模式
    5. 外部API验证 - 调用地图API验证地点存在性
    """

    KNOWN_ATTRACTIONS = {
        "北京": {
            "故宫博物院", "天安门广场", "颐和园", "圆明园", "天坛公园",
            "八达岭长城", "慕田峪长城", "鸟巢", "水立方", "南锣鼓巷",
            "什刹海", "恭王府", "雍和宫", "景山公园", "北海公园",
            "北京动物园", "香山公园", "奥林匹克公园", "798艺术区",
            "北京环球度假区", "玉渊潭公园", "中山公园", "地坛公园",
            "北京欢乐谷", "世界公园", "北京植物园", "潭柘寺", "戒台寺"
        },
        "上海": {
            "外滩", "东方明珠", "豫园", "城隍庙", "南京路步行街",
            "上海迪士尼乐园", "上海野生动物园", "上海科技馆", "田子坊",
            "新天地", "静安寺", "上海中心大厦", "金茂大厦", "环球金融中心",
            "朱家角古镇", "七宝古镇", "上海博物馆", "中华艺术宫",
            "世博园", "陆家嘴", "人民广场", "淮海路", "武康路"
        },
        "杭州": {
            "西湖", "灵隐寺", "雷峰塔", "断桥残雪", "三潭印月",
            "岳王庙", "宋城", "西溪湿地", "千岛湖", "九溪烟树",
            "龙井村", "虎跑泉", "六和塔", "河坊街", "南宋御街",
            "杭州乐园", "烂苹果乐园", "宋城千古情", "印象西湖"
        },
        "成都": {
            "大熊猫繁育研究基地", "宽窄巷子", "锦里古街", "武侯祠",
            "杜甫草堂", "青城山", "都江堰", "春熙路", "太古里",
            "人民公园", "文殊院", "天府广场", "九眼桥", "东郊记忆",
            "成都博物馆", "四川博物院", "金沙遗址博物馆"
        },
        "西安": {
            "兵马俑", "华清池", "大雁塔", "小雁塔", "钟楼", "鼓楼",
            "西安城墙", "回民街", "大唐芙蓉园", "陕西历史博物馆",
            "秦始皇陵", "骊山", "华清宫", "大慈恩寺", "碑林博物馆",
            "永兴坊", "大唐不夜城", "曲江池遗址公园"
        },
        "澳门": {
            "大三巴牌坊", "威尼斯人", "巴黎人", "伦敦人", "新葡京",
            "澳门塔", "妈阁庙", "议事亭前地", "澳门博物馆", "龙环葡韵",
            "黑沙海滩", "路环岛", "氹仔旧城区", "官也街", "银河酒店",
            "美高梅", "永利澳门", "澳门渔人码头", "澳门大赛车博物馆"
        },
        "香港": {
            "维多利亚港", "太平山顶", "迪士尼乐园", "海洋公园",
            "星光大道", "尖沙咀", "旺角", "铜锣湾", "中环",
            "天坛大佛", "黄大仙祠", "兰桂坊", "庙街夜市",
            "浅水湾", "赤柱", "石澳", "昂坪360", "杜莎夫人蜡像馆"
        },
        "广州": {
            "广州塔", "珠江夜游", "陈家祠", "沙面", "白云山",
            "长隆野生动物世界", "长隆欢乐世界", "越秀公园", "中山纪念堂",
            "北京路步行街", "上下九步行街", "荔枝湾", "圣心大教堂",
            "广州动物园", "华南植物园", "南沙天后宫"
        },
        "深圳": {
            "世界之窗", "欢乐谷", "东部华侨城", "大梅沙海滨公园",
            "小梅沙", "深圳湾公园", "莲花山公园", "梧桐山",
            "锦绣中华民俗村", "深圳野生动物园", "海上世界",
            "大鹏古城", "较场尾", "杨梅坑", "西涌海滩"
        },
        "厦门": {
            "鼓浪屿", "南普陀寺", "厦门大学", "曾厝垵", "环岛路",
            "中山路步行街", "胡里山炮台", "集美学村", "厦门植物园",
            "沙坡尾", "铁路文化公园", "白城沙滩", "日光岩", "菽庄花园"
        }
    }

    KNOWN_HOTEL_CHAINS = {
        "希尔顿", "万豪", "洲际", "喜来登", "威斯汀", "香格里拉",
        "凯悦", "丽思卡尔顿", "四季", "半岛", "文华东方", "JW万豪",
        "皇冠假日", "假日酒店", "智选假日", "如家", "汉庭", "全季",
        "亚朵", "维也纳", "锦江之星", "7天", "格林豪泰", "速8",
        "桔子水晶", "和颐酒店", "逸扉酒店", "美居", "诺富特", "铂尔曼"
    }

    SUSPICIOUS_PATTERNS = [
        r"景点\d+$",
        r"酒店\d+$",
        r"餐厅\d+$",
        r".*推荐\d+$",
        r".*必去\d+$",
        r"^第\d+个",
        r"^[A-Z]\d+$",
        r"^景点[一二三四五六七八九十]+$",
    ]

    def __init__(self, enable_api_validation: bool = False):
        """
        初始化幻觉检测器

        Args:
            enable_api_validation: 是否启用外部API验证（需要消耗API配额）
        """
        self.enable_api_validation = enable_api_validation
        self._validation_cache: Dict[str, bool] = {}

    async def detect(
        self,
        trip_plan: Dict[str, Any],
        city: str
    ) -> HallucinationResult:
        """
        检测旅行计划中的幻觉

        Args:
            trip_plan: 旅行计划数据
            city: 城市名称

        Returns:
            幻觉检测结果
        """
        issues: List[HallucinationIssue] = []

        city_attractions = self.KNOWN_ATTRACTIONS.get(city, set())

        days = trip_plan.get("days", [])
        for day_idx, day in enumerate(days):
            attractions = day.get("attractions", [])
            for attr in attractions:
                issue = await self._check_attraction(attr, city, city_attractions)
                if issue:
                    issues.append(issue)

            hotel = day.get("hotel")
            if hotel:
                issue = await self._check_hotel(hotel, city)
                if issue:
                    issues.append(issue)

            meals = day.get("meals", [])
            for meal in meals:
                issue = await self._check_meal(meal, city)
                if issue:
                    issues.append(issue)

            issue = self._check_schedule_reasonability(day, day_idx)
            if issue:
                issues.append(issue)

        total_items = self._count_total_items(trip_plan)
        hallucination_rate = len(issues) / total_items if total_items > 0 else 0.0

        return HallucinationResult(
            has_hallucination=len(issues) > 0,
            hallucination_count=len(issues),
            issues=issues,
            hallucination_rate=hallucination_rate,
            details={
                "city": city,
                "total_days": len(days),
                "total_items": total_items,
                "detection_time": datetime.now().isoformat()
            }
        )

    async def _check_attraction(
        self,
        attraction: Dict[str, Any],
        city: str,
        known_attractions: Set[str]
    ) -> Optional[HallucinationIssue]:
        """检查景点是否存在幻觉"""
        name = attraction.get("name", "")

        if not name:
            return None

        for pattern in self.SUSPICIOUS_PATTERNS:
            if re.match(pattern, name):
                return HallucinationIssue(
                    type=HallucinationType.FAKE_ATTRACTION,
                    description=f"景点名称 '{name}' 符合可疑模式，可能是AI生成的虚假景点",
                    item_name=name,
                    severity="high",
                    confidence=0.9,
                    evidence=f"匹配模式: {pattern}",
                    suggestion="请使用真实存在的景点名称"
                )

        if known_attractions:
            is_known = any(
                known in name or name in known
                for known in known_attractions
            )

            if not is_known and len(name) > 2:
                similarity = self._calculate_similarity(name, known_attractions)
                if similarity < 0.3:
                    return HallucinationIssue(
                        type=HallucinationType.FAKE_ATTRACTION,
                        description=f"景点 '{name}' 不在已知景点列表中，可能是虚假景点",
                        item_name=name,
                        severity="medium",
                        confidence=0.7,
                        evidence=f"与已知景点相似度: {similarity:.2f}",
                        suggestion=f"请验证该景点是否真实存在"
                    )

        location = attraction.get("location", {})
        if location:
            issue = self._check_coordinates(location, city)
            if issue:
                return issue

        return None

    async def _check_hotel(
        self,
        hotel: Dict[str, Any],
        city: str
    ) -> Optional[HallucinationIssue]:
        """检查酒店是否存在幻觉"""
        name = hotel.get("name", "")

        if not name:
            return None

        for pattern in self.SUSPICIOUS_PATTERNS:
            if re.match(pattern, name):
                return HallucinationIssue(
                    type=HallucinationType.FAKE_HOTEL,
                    description=f"酒店名称 '{name}' 符合可疑模式，可能是AI生成的虚假酒店",
                    item_name=name,
                    severity="high",
                    confidence=0.9,
                    evidence=f"匹配模式: {pattern}",
                    suggestion="请使用真实存在的酒店名称"
                )

        is_chain = any(chain in name for chain in self.KNOWN_HOTEL_CHAINS)
        if is_chain:
            return None

        if re.match(r".*(酒店|宾馆|旅馆|民宿|公寓)$", name):
            return None

        return HallucinationIssue(
            type=HallucinationType.FAKE_HOTEL,
            description=f"酒店 '{name}' 名称格式异常，可能是虚假酒店",
            item_name=name,
            severity="medium",
            confidence=0.6,
            evidence="酒店名称不符合常规命名格式",
            suggestion="请验证酒店是否真实存在"
        )

    async def _check_meal(
        self,
        meal: Dict[str, Any],
        city: str
    ) -> Optional[HallucinationIssue]:
        """检查餐饮推荐是否存在幻觉"""
        name = meal.get("name", "")

        if not name:
            return None

        for pattern in self.SUSPICIOUS_PATTERNS:
            if re.match(pattern, name):
                return HallucinationIssue(
                    type=HallucinationType.FAKE_FOOD,
                    description=f"餐厅 '{name}' 符合可疑模式，可能是AI生成的虚假推荐",
                    item_name=name,
                    severity="medium",
                    confidence=0.8,
                    evidence=f"匹配模式: {pattern}",
                    suggestion="请使用真实存在的餐厅名称"
                )

        return None

    def _check_coordinates(
        self,
        location: Dict[str, Any],
        city: str
    ) -> Optional[HallucinationIssue]:
        """检查坐标是否合理"""
        lng = location.get("longitude")
        lat = location.get("latitude")

        if lng is None or lat is None:
            return HallucinationIssue(
                type=HallucinationType.WRONG_COORDINATES,
                description="缺少有效的经纬度坐标",
                item_name=f"坐标({lng}, {lat})",
                severity="low",
                confidence=0.5,
                evidence="坐标值为空或无效",
                suggestion="请提供有效的经纬度坐标"
            )

        city_bounds = self._get_city_bounds(city)
        if city_bounds:
            min_lng, max_lng, min_lat, max_lat = city_bounds
            if not (min_lng <= lng <= max_lng and min_lat <= lat <= max_lat):
                return HallucinationIssue(
                    type=HallucinationType.WRONG_COORDINATES,
                    description=f"坐标({lng}, {lat})不在{city}的合理范围内",
                    item_name=f"坐标({lng:.4f}, {lat:.4f})",
                    severity="high",
                    confidence=0.9,
                    evidence=f"{city}合理范围: 经度[{min_lng:.2f}, {max_lng:.2f}], 纬度[{min_lat:.2f}, {max_lat:.2f}]",
                    suggestion="请使用正确的地理坐标"
                )

        return None

    def _check_schedule_reasonability(
        self,
        day: Dict[str, Any],
        day_idx: int
    ) -> Optional[HallucinationIssue]:
        """检查行程安排是否合理"""
        attractions = day.get("attractions", [])

        if len(attractions) > 5:
            return HallucinationIssue(
                type=HallucinationType.UNREASONABLE_SCHEDULE,
                description=f"第{day_idx + 1}天安排了{len(attractions)}个景点，过于密集",
                item_name=f"第{day_idx + 1}天行程",
                severity="medium",
                confidence=0.7,
                evidence="单日景点数量超过5个",
                suggestion="建议每天安排2-3个景点，确保游览质量"
            )

        total_duration = sum(
            attr.get("visit_duration", 60)
            for attr in attractions
        )

        if total_duration > 600:  # 超过10小时
            return HallucinationIssue(
                type=HallucinationType.UNREASONABLE_SCHEDULE,
                description=f"第{day_idx + 1}天总游览时间{total_duration}分钟，超过10小时",
                item_name=f"第{day_idx + 1}天行程",
                severity="medium",
                confidence=0.8,
                evidence=f"总游览时间: {total_duration}分钟",
                suggestion="建议合理安排游览时间，避免过度疲劳"
            )

        return None

    def _calculate_similarity(
        self,
        name: str,
        known_names: Set[str]
    ) -> float:
        """计算名称与已知名称的相似度"""
        max_similarity = 0.0
        for known in known_names:
            similarity = self._jaccard_similarity(name, known)
            max_similarity = max(max_similarity, similarity)
        return max_similarity

    def _jaccard_similarity(self, s1: str, s2: str) -> float:
        """计算Jaccard相似度"""
        set1 = set(s1)
        set2 = set(s2)
        intersection = len(set1 & set2)
        union = len(set1 | set2)
        return intersection / union if union > 0 else 0.0

    def _get_city_bounds(self, city: str) -> Optional[Tuple[float, float, float, float]]:
        """获取城市边界坐标"""
        city_bounds = {
            "北京": (115.4, 117.5, 39.4, 41.1),
            "上海": (120.9, 122.0, 30.7, 31.9),
            "杭州": (119.9, 120.5, 30.0, 30.5),
            "成都": (103.9, 104.2, 30.5, 30.8),
            "西安": (108.9, 109.1, 34.2, 34.4),
            "澳门": (113.5, 113.6, 22.1, 22.2),
            "香港": (113.8, 114.4, 22.2, 22.6),
            "广州": (113.0, 113.6, 22.9, 23.5),
            "深圳": (113.7, 114.6, 22.4, 22.9),
            "厦门": (118.0, 118.3, 24.4, 24.6),
        }
        return city_bounds.get(city)

    def _count_total_items(self, trip_plan: Dict[str, Any]) -> int:
        """计算旅行计划中的总项目数"""
        count = 0
        days = trip_plan.get("days", [])
        for day in days:
            count += len(day.get("attractions", []))
            if day.get("hotel"):
                count += 1
            count += len(day.get("meals", []))
        return count

    async def batch_detect(
        self,
        trip_plans: List[Dict[str, Any]],
        cities: List[str]
    ) -> List[HallucinationResult]:
        """
        批量检测多个旅行计划

        Args:
            trip_plans: 旅行计划列表
            cities: 对应的城市列表

        Returns:
            检测结果列表
        """
        results = []
        for plan, city in zip(trip_plans, cities):
            result = await self.detect(plan, city)
            results.append(result)
        return results


def calculate_hallucination_rate(
    results: List[HallucinationResult]
) -> Dict[str, float]:
    """
    计算幻觉率指标

    公式：幻觉率 = (含幻觉的行程数 / 总评估行程数) × 100%

    Args:
        results: 幻觉检测结果列表

    Returns:
        幻觉率统计
    """
    if not results:
        return {
            "hallucination_rate": 0.0,
            "total_plans": 0,
            "hallucinated_plans": 0,
            "total_issues": 0
        }

    total_plans = len(results)
    hallucinated_plans = sum(1 for r in results if r.has_hallucination)
    total_issues = sum(r.hallucination_count for r in results)

    hallucination_rate = (hallucinated_plans / total_plans) * 100

    issue_by_type: Dict[str, int] = {}
    for r in results:
        for issue in r.issues:
            t = issue.type.value
            issue_by_type[t] = issue_by_type.get(t, 0) + 1

    severity_count = {"high": 0, "medium": 0, "low": 0}
    for r in results:
        for issue in r.issues:
            severity_count[issue.severity] += 1

    return {
        "hallucination_rate": round(hallucination_rate, 2),
        "total_plans": total_plans,
        "hallucinated_plans": hallucinated_plans,
        "total_issues": total_issues,
        "avg_issues_per_plan": round(total_issues / total_plans, 2),
        "issue_by_type": issue_by_type,
        "severity_distribution": severity_count
    }
