"""
评估指标计算器
功能：
1. 计算幻觉率指标
2. 计算准确性指标
3. 计算相关性指标
4. 计算完整性指标
5. 生成综合评估报告

指标体系：
- 幻觉率 (Hallucination Rate): 含幻觉的行程数 / 总评估行程数
- 准确性 (Accuracy): 正确信息数 / 总信息数
- 相关性 (Relevance): 与用户需求匹配程度
- 完整性 (Completeness): 信息完整程度
- 时效性 (Timeliness): 信息时效性评估
"""

from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
import statistics
from loguru import logger


@dataclass
class HallucinationMetrics:
    """幻觉指标"""
    hallucination_rate: float
    total_plans: int
    hallucinated_plans: int
    total_issues: int
    avg_issues_per_plan: float
    issue_by_type: Dict[str, int]
    severity_distribution: Dict[str, int]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "hallucination_rate": self.hallucination_rate,
            "total_plans": self.total_plans,
            "hallucinated_plans": self.hallucinated_plans,
            "total_issues": self.total_issues,
            "avg_issues_per_plan": self.avg_issues_per_plan,
            "issue_by_type": self.issue_by_type,
            "severity_distribution": self.severity_distribution
        }


@dataclass
class AccuracyMetrics:
    """准确性指标"""
    overall_accuracy: float
    attraction_accuracy: float
    hotel_accuracy: float
    location_accuracy: float
    details: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "overall_accuracy": self.overall_accuracy,
            "attraction_accuracy": self.attraction_accuracy,
            "hotel_accuracy": self.hotel_accuracy,
            "location_accuracy": self.location_accuracy,
            "details": self.details
        }


@dataclass
class RelevanceMetrics:
    """相关性指标"""
    overall_relevance: float
    preference_match_rate: float
    city_match_rate: float
    details: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "overall_relevance": self.overall_relevance,
            "preference_match_rate": self.preference_match_rate,
            "city_match_rate": self.city_match_rate,
            "details": self.details
        }


@dataclass
class CompletenessMetrics:
    """完整性指标"""
    overall_completeness: float
    has_attractions: float
    has_hotels: float
    has_meals: float
    has_weather: float
    has_budget: float
    has_suggestions: float
    details: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "overall_completeness": self.overall_completeness,
            "has_attractions": self.has_attractions,
            "has_hotels": self.has_hotels,
            "has_meals": self.has_meals,
            "has_weather": self.has_weather,
            "has_budget": self.has_budget,
            "has_suggestions": self.has_suggestions,
            "details": self.details
        }


@dataclass
class EvaluationMetrics:
    """综合评估指标"""
    hallucination: HallucinationMetrics
    accuracy: AccuracyMetrics
    relevance: RelevanceMetrics
    completeness: CompletenessMetrics
    overall_score: float
    timestamp: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "hallucination": self.hallucination.to_dict(),
            "accuracy": self.accuracy.to_dict(),
            "relevance": self.relevance.to_dict(),
            "completeness": self.completeness.to_dict(),
            "overall_score": self.overall_score,
            "timestamp": self.timestamp
        }


class MetricsCalculator:
    """
    指标计算器

    使用方法：
    ```python
    calculator = MetricsCalculator()
    metrics = calculator.calculate_all(trip_plans, hallucination_results, requests)
    ```
    """

    PREFERENCE_KEYWORDS = {
        "历史文化": ["博物馆", "古迹", "遗址", "寺庙", "宫殿", "历史", "文化", "古镇"],
        "自然风光": ["山", "湖", "海", "公园", "湿地", "森林", "瀑布", "峡谷"],
        "美食": ["美食", "小吃", "餐厅", "特色", "当地", "美食街"],
        "购物": ["购物", "商场", "步行街", "免税", "市场"],
        "亲子": ["乐园", "动物园", "海洋馆", "儿童", "亲子"],
        "休闲": ["温泉", "度假", "海滩", "休闲", "SPA"],
    }

    def __init__(self):
        pass

    def calculate_all(
        self,
        trip_plans: List[Dict[str, Any]],
        hallucination_results: List[Any],
        requests: Optional[List[Dict[str, Any]]] = None
    ) -> EvaluationMetrics:
        """
        计算所有指标

        Args:
            trip_plans: 旅行计划列表
            hallucination_results: 幻觉检测结果列表
            requests: 原始请求列表（用于计算相关性）

        Returns:
            综合评估指标
        """
        hallucination_metrics = self._calculate_hallucination_metrics(hallucination_results)

        accuracy_metrics = self._calculate_accuracy_metrics(trip_plans)

        relevance_metrics = self._calculate_relevance_metrics(trip_plans, requests)

        completeness_metrics = self._calculate_completeness_metrics(trip_plans)

        overall_score = self._calculate_overall_score(
            hallucination_metrics,
            accuracy_metrics,
            relevance_metrics,
            completeness_metrics
        )

        return EvaluationMetrics(
            hallucination=hallucination_metrics,
            accuracy=accuracy_metrics,
            relevance=relevance_metrics,
            completeness=completeness_metrics,
            overall_score=overall_score,
            timestamp=datetime.now().isoformat()
        )

    def _calculate_hallucination_metrics(
        self,
        results: List[Any]
    ) -> HallucinationMetrics:
        """计算幻觉指标"""
        if not results:
            return HallucinationMetrics(
                hallucination_rate=0.0,
                total_plans=0,
                hallucinated_plans=0,
                total_issues=0,
                avg_issues_per_plan=0.0,
                issue_by_type={},
                severity_distribution={"high": 0, "medium": 0, "low": 0}
            )

        total_plans = len(results)
        hallucinated_plans = sum(1 for r in results if r.has_hallucination)
        total_issues = sum(r.hallucination_count for r in results)

        hallucination_rate = (hallucinated_plans / total_plans) * 100 if total_plans > 0 else 0
        avg_issues = total_issues / total_plans if total_plans > 0 else 0

        issue_by_type: Dict[str, int] = {}
        severity_count = {"high": 0, "medium": 0, "low": 0}

        for r in results:
            for issue in r.issues:
                t = issue.type.value
                issue_by_type[t] = issue_by_type.get(t, 0) + 1
                severity_count[issue.severity] += 1

        return HallucinationMetrics(
            hallucination_rate=round(hallucination_rate, 2),
            total_plans=total_plans,
            hallucinated_plans=hallucinated_plans,
            total_issues=total_issues,
            avg_issues_per_plan=round(avg_issues, 2),
            issue_by_type=issue_by_type,
            severity_distribution=severity_count
        )

    def _calculate_accuracy_metrics(
        self,
        trip_plans: List[Dict[str, Any]]
    ) -> AccuracyMetrics:
        """计算准确性指标"""
        if not trip_plans:
            return AccuracyMetrics(
                overall_accuracy=0.0,
                attraction_accuracy=0.0,
                hotel_accuracy=0.0,
                location_accuracy=0.0
            )

        attraction_scores = []
        hotel_scores = []
        location_scores = []

        for plan in trip_plans:
            days = plan.get("days", [])

            for day in days:
                attractions = day.get("attractions", [])
                for attr in attractions:
                    score = self._evaluate_attraction_accuracy(attr)
                    attraction_scores.append(score)

                    loc_score = self._evaluate_location_accuracy(attr.get("location", {}))
                    location_scores.append(loc_score)

                hotel = day.get("hotel")
                if hotel:
                    score = self._evaluate_hotel_accuracy(hotel)
                    hotel_scores.append(score)

                    loc_score = self._evaluate_location_accuracy(hotel.get("location", {}))
                    location_scores.append(loc_score)

        attraction_accuracy = statistics.mean(attraction_scores) * 100 if attraction_scores else 0
        hotel_accuracy = statistics.mean(hotel_scores) * 100 if hotel_scores else 0
        location_accuracy = statistics.mean(location_scores) * 100 if location_scores else 0

        overall_accuracy = (attraction_accuracy + hotel_accuracy + location_accuracy) / 3

        return AccuracyMetrics(
            overall_accuracy=round(overall_accuracy, 2),
            attraction_accuracy=round(attraction_accuracy, 2),
            hotel_accuracy=round(hotel_accuracy, 2),
            location_accuracy=round(location_accuracy, 2),
            details={
                "total_attractions": len(attraction_scores),
                "total_hotels": len(hotel_scores),
                "total_locations": len(location_scores)
            }
        )

    def _evaluate_attraction_accuracy(self, attraction: Dict[str, Any]) -> float:
        """评估景点准确性"""
        score = 0.0

        if attraction.get("name"):
            score += 0.2

        if attraction.get("address"):
            score += 0.2

        location = attraction.get("location", {})
        if location.get("longitude") and location.get("latitude"):
            score += 0.3
            lng = location["longitude"]
            lat = location["latitude"]
            if -180 <= lng <= 180 and -90 <= lat <= 90:
                score += 0.1

        if attraction.get("description"):
            score += 0.1

        if attraction.get("visit_duration"):
            score += 0.1

        return score

    def _evaluate_hotel_accuracy(self, hotel: Dict[str, Any]) -> float:
        """评估酒店准确性"""
        score = 0.0

        if hotel.get("name"):
            score += 0.3

        if hotel.get("address"):
            score += 0.3

        location = hotel.get("location", {})
        if location.get("longitude") and location.get("latitude"):
            score += 0.2

        if hotel.get("price_range") or hotel.get("estimated_cost"):
            score += 0.1

        if hotel.get("rating"):
            score += 0.1

        return score

    def _evaluate_location_accuracy(self, location: Dict[str, Any]) -> float:
        """评估位置准确性"""
        if not location:
            return 0.0

        lng = location.get("longitude")
        lat = location.get("latitude")

        if lng is None or lat is None:
            return 0.0

        if not (-180 <= lng <= 180 and -90 <= lat <= 90):
            return 0.0

        return 1.0

    def _calculate_relevance_metrics(
        self,
        trip_plans: List[Dict[str, Any]],
        requests: Optional[List[Dict[str, Any]]]
    ) -> RelevanceMetrics:
        """计算相关性指标"""
        if not trip_plans:
            return RelevanceMetrics(
                overall_relevance=0.0,
                preference_match_rate=0.0,
                city_match_rate=0.0
            )

        city_match_scores = []
        preference_match_scores = []

        for i, plan in enumerate(trip_plans):
            plan_city = plan.get("city", "").lower()

            request = requests[i] if requests and i < len(requests) else None
            if request:
                request_city = request.get("city", "").lower()
                city_match = 1.0 if plan_city == request_city else 0.0
                city_match_scores.append(city_match)

                preferences = request.get("preferences", [])
                if preferences:
                    match_score = self._calculate_preference_match(plan, preferences)
                    preference_match_scores.append(match_score)

        city_match_rate = statistics.mean(city_match_scores) * 100 if city_match_scores else 100.0
        preference_match_rate = statistics.mean(preference_match_scores) * 100 if preference_match_scores else 100.0

        overall_relevance = (city_match_rate + preference_match_rate) / 2

        return RelevanceMetrics(
            overall_relevance=round(overall_relevance, 2),
            preference_match_rate=round(preference_match_rate, 2),
            city_match_rate=round(city_match_rate, 2),
            details={
                "total_plans": len(trip_plans),
                "preference_evaluated": len(preference_match_scores)
            }
        )

    def _calculate_preference_match(
        self,
        plan: Dict[str, Any],
        preferences: List[str]
    ) -> float:
        """计算偏好匹配度"""
        if not preferences:
            return 1.0

        all_text = ""
        days = plan.get("days", [])
        for day in days:
            for attr in day.get("attractions", []):
                all_text += attr.get("name", "") + " "
                all_text += attr.get("description", "") + " "
                all_text += attr.get("category", "") + " "

        all_text = all_text.lower()

        match_count = 0
        for pref in preferences:
            keywords = self.PREFERENCE_KEYWORDS.get(pref, [pref])
            if any(kw in all_text for kw in keywords):
                match_count += 1

        return match_count / len(preferences)

    def _calculate_completeness_metrics(
        self,
        trip_plans: List[Dict[str, Any]]
    ) -> CompletenessMetrics:
        """计算完整性指标"""
        if not trip_plans:
            return CompletenessMetrics(
                overall_completeness=0.0,
                has_attractions=0.0,
                has_hotels=0.0,
                has_meals=0.0,
                has_weather=0.0,
                has_budget=0.0,
                has_suggestions=0.0
            )

        has_attractions = 0
        has_hotels = 0
        has_meals = 0
        has_weather = 0
        has_budget = 0
        has_suggestions = 0

        for plan in trip_plans:
            days = plan.get("days", [])

            attraction_count = sum(len(d.get("attractions", [])) for d in days)
            if attraction_count > 0:
                has_attractions += 1

            hotel_count = sum(1 for d in days if d.get("hotel"))
            if hotel_count > 0:
                has_hotels += 1

            meal_count = sum(len(d.get("meals", [])) for d in days)
            if meal_count > 0:
                has_meals += 1

            if plan.get("weather_info"):
                has_weather += 1

            if plan.get("budget"):
                has_budget += 1

            if plan.get("overall_suggestions"):
                has_suggestions += 1

        total = len(trip_plans)

        return CompletenessMetrics(
            overall_completeness=round(
                (has_attractions + has_hotels + has_meals + has_weather + has_budget + has_suggestions) / (total * 6) * 100, 2
            ),
            has_attractions=round(has_attractions / total * 100, 2),
            has_hotels=round(has_hotels / total * 100, 2),
            has_meals=round(has_meals / total * 100, 2),
            has_weather=round(has_weather / total * 100, 2),
            has_budget=round(has_budget / total * 100, 2),
            has_suggestions=round(has_suggestions / total * 100, 2),
            details={
                "total_plans": total
            }
        )

    def _calculate_overall_score(
        self,
        hallucination: HallucinationMetrics,
        accuracy: AccuracyMetrics,
        relevance: RelevanceMetrics,
        completeness: CompletenessMetrics
    ) -> float:
        """
        计算综合得分

        权重分配：
        - 幻觉率（反向）: 30%
        - 准确性: 30%
        - 相关性: 20%
        - 完整性: 20%
        """
        hallucination_score = 100 - hallucination.hallucination_rate

        accuracy_score = accuracy.overall_accuracy

        relevance_score = relevance.overall_relevance

        completeness_score = completeness.overall_completeness

        overall = (
            hallucination_score * 0.30 +
            accuracy_score * 0.30 +
            relevance_score * 0.20 +
            completeness_score * 0.20
        )

        return round(overall, 2)

    def compare_metrics(
        self,
        metrics_a: EvaluationMetrics,
        metrics_b: EvaluationMetrics,
        label_a: str = "A",
        label_b: str = "B"
    ) -> Dict[str, Any]:
        """
        对比两组指标

        Args:
            metrics_a: 第一组指标
            metrics_b: 第二组指标
            label_a: 第一组标签
            label_b: 第二组标签

        Returns:
            对比结果
        """
        return {
            "comparison": {
                "hallucination_rate": {
                    label_a: metrics_a.hallucination.hallucination_rate,
                    label_b: metrics_b.hallucination.hallucination_rate,
                    "improvement": round(
                        metrics_a.hallucination.hallucination_rate - metrics_b.hallucination.hallucination_rate, 2
                    )
                },
                "accuracy": {
                    label_a: metrics_a.accuracy.overall_accuracy,
                    label_b: metrics_b.accuracy.overall_accuracy,
                    "improvement": round(
                        metrics_b.accuracy.overall_accuracy - metrics_a.accuracy.overall_accuracy, 2
                    )
                },
                "relevance": {
                    label_a: metrics_a.relevance.overall_relevance,
                    label_b: metrics_b.relevance.overall_relevance,
                    "improvement": round(
                        metrics_b.relevance.overall_relevance - metrics_a.relevance.overall_relevance, 2
                    )
                },
                "completeness": {
                    label_a: metrics_a.completeness.overall_completeness,
                    label_b: metrics_b.completeness.overall_completeness,
                    "improvement": round(
                        metrics_b.completeness.overall_completeness - metrics_a.completeness.overall_completeness, 2
                    )
                },
                "overall_score": {
                    label_a: metrics_a.overall_score,
                    label_b: metrics_b.overall_score,
                    "improvement": round(metrics_b.overall_score - metrics_a.overall_score, 2)
                }
            },
            "winner": label_b if metrics_b.overall_score > metrics_a.overall_score else label_a,
            "improvement_percentage": round(
                (metrics_b.overall_score - metrics_a.overall_score) / metrics_a.overall_score * 100, 2
            ) if metrics_a.overall_score > 0 else 0
        }
