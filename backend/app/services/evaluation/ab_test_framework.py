"""
A/B测试框架
功能：
1. 对比有RAG和无RAG的旅行计划生成质量
2. 随机分配测试变体
3. 统计显著性检验
4. 生成对比报告

测试设计：
- 对照组(A): 无RAG增强的传统生成
- 实验组(B): 有RAG增强的生成

评估维度：
1. 幻觉率
2. 信息准确性
3. 内容相关性
4. 用户满意度（模拟）
"""

import asyncio
import json
import random
import hashlib
from typing import List, Dict, Optional, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from loguru import logger

from .hallucination_detector import (
    HallucinationDetector,
    HallucinationResult,
    calculate_hallucination_rate
)


class TestVariant(Enum):
    """测试变体"""
    CONTROL = "control"  # 对照组：无RAG
    TREATMENT = "treatment"  # 实验组：有RAG


@dataclass
class ABTestConfig:
    """A/B测试配置"""
    test_name: str
    sample_size: int = 100
    random_seed: Optional[int] = None
    confidence_level: float = 0.95
    metrics: List[str] = field(default_factory=lambda: [
        "hallucination_rate",
        "accuracy",
        "relevance",
        "completeness"
    ])

    test_cities: List[str] = field(default_factory=lambda: [
        "北京", "上海", "杭州", "成都", "西安",
        "澳门", "香港", "广州", "深圳", "厦门"
    ])

    test_preferences: List[List[str]] = field(default_factory=lambda: [
        ["历史文化"],
        ["自然风光"],
        ["美食"],
        ["购物"],
        ["历史文化", "美食"],
        ["自然风光", "美食"],
        ["历史文化", "自然风光"],
        []
    ])

    travel_days_range: tuple = (2, 5)


@dataclass
class TestCase:
    """测试用例"""
    case_id: str
    city: str
    travel_days: int
    preferences: List[str]
    start_date: str
    end_date: str
    variant: TestVariant

    def to_dict(self) -> Dict[str, Any]:
        return {
            "case_id": self.case_id,
            "city": self.city,
            "travel_days": self.travel_days,
            "preferences": self.preferences,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "variant": self.variant.value
        }


@dataclass
class TestResult:
    """测试结果"""
    case: TestCase
    trip_plan: Optional[Dict[str, Any]]
    hallucination_result: Optional[HallucinationResult]
    generation_time: float
    success: bool
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "case": self.case.to_dict(),
            "trip_plan": self.trip_plan,
            "hallucination_result": self.hallucination_result.to_dict() if self.hallucination_result else None,
            "generation_time": self.generation_time,
            "success": self.success,
            "error": self.error
        }


@dataclass
class ABTestReport:
    """A/B测试报告"""
    test_name: str
    config: ABTestConfig
    start_time: str
    end_time: str

    control_results: List[TestResult]
    treatment_results: List[TestResult]

    control_metrics: Dict[str, Any]
    treatment_metrics: Dict[str, Any]

    statistical_significance: Dict[str, Any]
    improvement: Dict[str, float]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "test_name": self.test_name,
            "config": {
                "sample_size": self.config.sample_size,
                "test_cities": self.config.test_cities,
                "confidence_level": self.config.confidence_level
            },
            "start_time": self.start_time,
            "end_time": self.end_time,
            "control": {
                "sample_size": len(self.control_results),
                "metrics": self.control_metrics
            },
            "treatment": {
                "sample_size": len(self.treatment_results),
                "metrics": self.treatment_metrics
            },
            "statistical_significance": self.statistical_significance,
            "improvement": self.improvement,
            "detailed_results": {
                "control": [r.to_dict() for r in self.control_results],
                "treatment": [r.to_dict() for r in self.treatment_results]
            }
        }


class ABTestFramework:
    """
    A/B测试框架

    使用方法：
    ```python
    framework = ABTestFramework(config)
    report = await framework.run_test(
        control_generator=generate_without_rag,
        treatment_generator=generate_with_rag
    )
    ```
    """

    def __init__(self, config: ABTestConfig):
        self.config = config
        self.detector = HallucinationDetector()

        if config.random_seed is not None:
            random.seed(config.random_seed)

    async def run_test(
        self,
        control_generator: Callable,
        treatment_generator: Callable,
        progress_callback: Optional[Callable] = None
    ) -> ABTestReport:
        """
        运行A/B测试

        Args:
            control_generator: 对照组生成函数（无RAG）
            treatment_generator: 实验组生成函数（有RAG）
            progress_callback: 进度回调函数

        Returns:
            A/B测试报告
        """
        start_time = datetime.now()
        logger.info(f"开始A/B测试: {self.config.test_name}")

        test_cases = self._generate_test_cases()

        control_cases = [c for c in test_cases if c.variant == TestVariant.CONTROL]
        treatment_cases = [c for c in test_cases if c.variant == TestVariant.TREATMENT]

        logger.info(f"对照组样本数: {len(control_cases)}")
        logger.info(f"实验组样本数: {len(treatment_cases)}")

        control_results = await self._run_variant(
            control_cases,
            control_generator,
            "对照组",
            progress_callback
        )

        treatment_results = await self._run_variant(
            treatment_cases,
            treatment_generator,
            "实验组",
            progress_callback
        )

        control_metrics = self._calculate_metrics(control_results)
        treatment_metrics = self._calculate_metrics(treatment_results)

        statistical_significance = self._calculate_statistical_significance(
            control_results,
            treatment_results
        )

        improvement = self._calculate_improvement(
            control_metrics,
            treatment_metrics
        )

        end_time = datetime.now()

        report = ABTestReport(
            test_name=self.config.test_name,
            config=self.config,
            start_time=start_time.isoformat(),
            end_time=end_time.isoformat(),
            control_results=control_results,
            treatment_results=treatment_results,
            control_metrics=control_metrics,
            treatment_metrics=treatment_metrics,
            statistical_significance=statistical_significance,
            improvement=improvement
        )

        logger.info(f"A/B测试完成: {self.config.test_name}")
        self._print_summary(report)

        return report

    def _generate_test_cases(self) -> List[TestCase]:
        """生成测试用例"""
        cases = []
        case_id = 0

        for _ in range(self.config.sample_size):
            city = random.choice(self.config.test_cities)
            preferences = random.choice(self.config.test_preferences)
            travel_days = random.randint(*self.config.travel_days_range)

            from datetime import date, timedelta
            start = date.today() + timedelta(days=random.randint(7, 30))
            end = start + timedelta(days=travel_days)

            variant = TestVariant.CONTROL if case_id % 2 == 0 else TestVariant.TREATMENT

            case = TestCase(
                case_id=f"case_{case_id:04d}",
                city=city,
                travel_days=travel_days,
                preferences=preferences,
                start_date=start.isoformat(),
                end_date=end.isoformat(),
                variant=variant
            )
            cases.append(case)
            case_id += 1

        random.shuffle(cases)

        return cases

    async def _run_variant(
        self,
        cases: List[TestCase],
        generator: Callable,
        variant_name: str,
        progress_callback: Optional[Callable] = None
    ) -> List[TestResult]:
        """运行单个变体的测试"""
        results = []

        for i, case in enumerate(cases):
            logger.info(f"{variant_name} [{i+1}/{len(cases)}] 测试: {case.city}")

            try:
                start = datetime.now()

                trip_plan = await generator(
                    city=case.city,
                    travel_days=case.travel_days,
                    preferences=case.preferences,
                    start_date=case.start_date,
                    end_date=case.end_date
                )

                generation_time = (datetime.now() - start).total_seconds()

                hallucination_result = await self.detector.detect(
                    trip_plan,
                    case.city
                )

                result = TestResult(
                    case=case,
                    trip_plan=trip_plan,
                    hallucination_result=hallucination_result,
                    generation_time=generation_time,
                    success=True
                )

            except Exception as e:
                logger.error(f"测试用例失败: {case.case_id}, 错误: {e}")
                result = TestResult(
                    case=case,
                    trip_plan=None,
                    hallucination_result=None,
                    generation_time=0,
                    success=False,
                    error=str(e)
                )

            results.append(result)

            if progress_callback:
                progress_callback(i + 1, len(cases), variant_name)

            await asyncio.sleep(0.5)

        return results

    def _calculate_metrics(
        self,
        results: List[TestResult]
    ) -> Dict[str, Any]:
        """计算评估指标"""
        successful_results = [r for r in results if r.success]

        if not successful_results:
            return {
                "success_rate": 0,
                "avg_generation_time": 0,
                "hallucination_metrics": {}
            }

        hallucination_results = [
            r.hallucination_result for r in successful_results
            if r.hallucination_result
        ]

        hallucination_metrics = calculate_hallucination_rate(hallucination_results)

        avg_generation_time = sum(
            r.generation_time for r in successful_results
        ) / len(successful_results)

        accuracy = self._calculate_accuracy(successful_results)

        completeness = self._calculate_completeness(successful_results)

        return {
            "success_rate": len(successful_results) / len(results) * 100,
            "avg_generation_time": round(avg_generation_time, 2),
            "hallucination_metrics": hallucination_metrics,
            "accuracy": accuracy,
            "completeness": completeness
        }

    def _calculate_accuracy(
        self,
        results: List[TestResult]
    ) -> Dict[str, float]:
        """计算准确性指标"""
        if not results:
            return {"overall": 0}

        total_items = 0
        accurate_items = 0

        for result in results:
            if not result.trip_plan:
                continue

            days = result.trip_plan.get("days", [])
            for day in days:
                attractions = day.get("attractions", [])
                for attr in attractions:
                    total_items += 1
                    if attr.get("location") and attr.get("name"):
                        loc = attr["location"]
                        if loc.get("longitude") and loc.get("latitude"):
                            accurate_items += 1

                if day.get("hotel"):
                    total_items += 1
                    hotel = day["hotel"]
                    if hotel.get("name") and hotel.get("address"):
                        accurate_items += 1

        accuracy = (accurate_items / total_items * 100) if total_items > 0 else 0

        return {
            "overall": round(accuracy, 2),
            "total_items": total_items,
            "accurate_items": accurate_items
        }

    def _calculate_completeness(
        self,
        results: List[TestResult]
    ) -> Dict[str, float]:
        """计算完整性指标"""
        if not results:
            return {"overall": 0}

        scores = []

        for result in results:
            if not result.trip_plan:
                continue

            score = 0
            max_score = 5

            days = result.trip_plan.get("days", [])
            if days:
                score += 1

            for day in days:
                if day.get("attractions"):
                    score += 0.5
                if day.get("hotel"):
                    score += 0.5
                if day.get("meals"):
                    score += 0.5

            if result.trip_plan.get("weather_info"):
                score += 0.5

            if result.trip_plan.get("overall_suggestions"):
                score += 0.5

            if result.trip_plan.get("budget"):
                score += 0.5

            scores.append(min(score / max_score, 1.0))

        avg_score = sum(scores) / len(scores) * 100 if scores else 0

        return {
            "overall": round(avg_score, 2),
            "avg_score": round(avg_score / 100, 2)
        }

    def _calculate_statistical_significance(
        self,
        control_results: List[TestResult],
        treatment_results: List[TestResult]
    ) -> Dict[str, Any]:
        """计算统计显著性"""
        control_hallucinated = sum(
            1 for r in control_results
            if r.success and r.hallucination_result and r.hallucination_result.has_hallucination
        )
        control_total = sum(1 for r in control_results if r.success)

        treatment_hallucinated = sum(
            1 for r in treatment_results
            if r.success and r.hallucination_result and r.hallucination_result.has_hallucination
        )
        treatment_total = sum(1 for r in treatment_results if r.success)

        if control_total == 0 or treatment_total == 0:
            return {
                "test": "mcnemar",
                "p_value": None,
                "significant": False,
                "note": "样本量不足"
            }

        p_value = self._mcnemar_test(
            control_hallucinated,
            control_total - control_hallucinated,
            treatment_hallucinated,
            treatment_total - treatment_hallucinated
        )

        return {
            "test": "mcnemar",
            "p_value": round(p_value, 4) if p_value is not None else None,
            "significant": bool(p_value is not None and p_value < (1 - self.config.confidence_level)),
            "control_hallucinated": control_hallucinated,
            "control_total": control_total,
            "treatment_hallucinated": treatment_hallucinated,
            "treatment_total": treatment_total,
            "confidence_level": float(self.config.confidence_level)
        }

    def _mcnemar_test(
        self,
        a: int,
        b: int,
        c: int,
        d: int
    ) -> Optional[float]:
        """
        McNemar检验

        用于比较两个相关样本的比例差异

        Args:
            a: 对照组有幻觉数
            b: 对照组无幻觉数
            c: 实验组有幻觉数
            d: 实验组无幻觉数

        Returns:
            p值
        """
        try:
            b_plus_c = b + c
            if b_plus_c == 0:
                return 1.0

            chi_square = (abs(b - c) - 1) ** 2 / b_plus_c

            from scipy import stats
            p_value = 1 - stats.chi2.cdf(chi_square, df=1)

            return p_value

        except Exception as e:
            logger.warning(f"McNemar检验失败: {e}")
            return None

    def _calculate_improvement(
        self,
        control_metrics: Dict[str, Any],
        treatment_metrics: Dict[str, Any]
    ) -> Dict[str, float]:
        """计算改进幅度"""
        improvements = {}

        control_hallucination = control_metrics.get("hallucination_metrics", {}).get("hallucination_rate", 0)
        treatment_hallucination = treatment_metrics.get("hallucination_metrics", {}).get("hallucination_rate", 0)

        if control_hallucination > 0:
            reduction = (control_hallucination - treatment_hallucination) / control_hallucination * 100
            improvements["hallucination_reduction"] = round(reduction, 2)

        control_accuracy = control_metrics.get("accuracy", {}).get("overall", 0)
        treatment_accuracy = treatment_metrics.get("accuracy", {}).get("overall", 0)

        if control_accuracy > 0:
            improvement = (treatment_accuracy - control_accuracy) / control_accuracy * 100
            improvements["accuracy_improvement"] = round(improvement, 2)

        control_completeness = control_metrics.get("completeness", {}).get("overall", 0)
        treatment_completeness = treatment_metrics.get("completeness", {}).get("overall", 0)

        if control_completeness > 0:
            improvement = (treatment_completeness - control_completeness) / control_completeness * 100
            improvements["completeness_improvement"] = round(improvement, 2)

        return improvements

    def _print_summary(self, report: ABTestReport):
        """打印测试摘要"""
        print("\n" + "=" * 60)
        print(f"A/B测试报告: {report.test_name}")
        print("=" * 60)

        print(f"\n对照组 (无RAG):")
        hm = report.control_metrics.get("hallucination_metrics", {})
        print(f"  幻觉率: {hm.get('hallucination_rate', 0)}%")
        print(f"  准确性: {report.control_metrics.get('accuracy', {}).get('overall', 0)}%")
        print(f"  完整性: {report.control_metrics.get('completeness', {}).get('overall', 0)}%")

        print(f"\n实验组 (有RAG):")
        hm = report.treatment_metrics.get("hallucination_metrics", {})
        print(f"  幻觉率: {hm.get('hallucination_rate', 0)}%")
        print(f"  准确性: {report.treatment_metrics.get('accuracy', {}).get('overall', 0)}%")
        print(f"  完整性: {report.treatment_metrics.get('completeness', {}).get('overall', 0)}%")

        print(f"\n改进效果:")
        for key, value in report.improvement.items():
            print(f"  {key}: {value}%")

        sig = report.statistical_significance
        print(f"\n统计显著性:")
        print(f"  检验方法: {sig.get('test', 'N/A')}")
        print(f"  p值: {sig.get('p_value', 'N/A')}")
        print(f"  是否显著: {'是' if sig.get('significant') else '否'}")

        print("=" * 60 + "\n")
