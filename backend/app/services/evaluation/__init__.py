"""
评估模块
功能：
1. 幻觉检测 - 检测旅行计划中的虚假信息
2. A/B测试 - 对比有RAG和无RAG的生成质量
3. 指标计算 - 幻觉率、准确性、相关性等
"""

from .hallucination_detector import (
    HallucinationDetector,
    HallucinationType,
    HallucinationResult
)
from .ab_test_framework import (
    ABTestFramework,
    ABTestConfig,
    TestVariant
)
from .metrics_calculator import (
    MetricsCalculator,
    EvaluationMetrics,
    HallucinationMetrics
)
from .evaluation_report import (
    EvaluationReportGenerator,
    TestReport
)

__all__ = [
    "HallucinationDetector",
    "HallucinationType",
    "HallucinationResult",
    "ABTestFramework",
    "ABTestConfig",
    "TestVariant",
    "MetricsCalculator",
    "EvaluationMetrics",
    "HallucinationMetrics",
    "EvaluationReportGenerator",
    "TestReport",
]
