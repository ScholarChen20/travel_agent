"""
评估报告生成器
功能：
1. 生成A/B测试报告
2. 生成可视化图表
3. 生成面试展示材料
4. 导出多种格式（JSON、Markdown、HTML）
"""

import json
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from loguru import logger


@dataclass
class TestReport:
    """测试报告数据"""
    test_name: str
    test_date: str
    config: Dict[str, Any]
    results: Dict[str, Any]
    metrics: Dict[str, Any]
    statistical_analysis: Dict[str, Any]
    conclusions: List[str]
    recommendations: List[str]


class EvaluationReportGenerator:
    """
    评估报告生成器

    生成多种格式的报告：
    - JSON: 机器可读格式
    - Markdown: 文档格式
    - HTML: 可视化报告
    """

    def __init__(self, output_dir: str = "./evaluation_reports"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_report(
        self,
        ab_test_report: Any,
        format: str = "all"
    ) -> Dict[str, Path]:
        """
        生成报告

        Args:
            ab_test_report: A/B测试报告对象
            format: 输出格式 (json, markdown, html, all)

        Returns:
            生成的文件路径字典
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_name = f"{ab_test_report.test_name}_{timestamp}"

        output_files = {}

        if format in ("json", "all"):
            json_path = self._generate_json_report(ab_test_report, base_name)
            output_files["json"] = json_path

        if format in ("markdown", "all"):
            md_path = self._generate_markdown_report(ab_test_report, base_name)
            output_files["markdown"] = md_path

        if format in ("html", "all"):
            html_path = self._generate_html_report(ab_test_report, base_name)
            output_files["html"] = html_path

        return output_files

    def _generate_json_report(
        self,
        report: Any,
        base_name: str
    ) -> Path:
        """生成JSON报告"""
        file_path = self.output_dir / f"{base_name}.json"

        data = report.to_dict()

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        logger.info(f"JSON报告已生成: {file_path}")
        return file_path

    def _generate_markdown_report(
        self,
        report: Any,
        base_name: str
    ) -> Path:
        """生成Markdown报告"""
        file_path = self.output_dir / f"{base_name}.md"

        md_content = self._build_markdown_content(report)

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(md_content)

        logger.info(f"Markdown报告已生成: {file_path}")
        return file_path

    def _build_markdown_content(self, report: Any) -> str:
        """构建Markdown内容"""
        control_metrics = report.control_metrics
        treatment_metrics = report.treatment_metrics
        sig = report.statistical_significance
        improvement = report.improvement

        control_hm = control_metrics.get("hallucination_metrics", {})
        treatment_hm = treatment_metrics.get("hallucination_metrics", {})

        md = f"""# RAG效果评估报告

## 测试概述

- **测试名称**: {report.test_name}
- **测试时间**: {report.start_time} ~ {report.end_time}
- **样本规模**: 对照组 {len(report.control_results)} / 实验组 {len(report.treatment_results)}
- **置信水平**: {report.config.confidence_level * 100}%

---

## 核心指标对比

### 幻觉率 (Hallucination Rate)

> **计算公式**: `幻觉率 = (含幻觉的行程数 / 总评估行程数) × 100%`

| 指标 | 对照组 (无RAG) | 实验组 (有RAG) | 改进 |
|------|---------------|---------------|------|
| **幻觉率** | {control_hm.get('hallucination_rate', 0)}% | {treatment_hm.get('hallucination_rate', 0)}% | {improvement.get('hallucination_reduction', 0)}% ↓ |
| 含幻觉行程数 | {control_hm.get('hallucinated_plans', 0)} | {treatment_hm.get('hallucinated_plans', 0)} | - |
| 总问题数 | {control_hm.get('total_issues', 0)} | {treatment_hm.get('total_issues', 0)} | - |

### 准确性 (Accuracy)

| 指标 | 对照组 | 实验组 | 改进 |
|------|--------|--------|------|
| **整体准确性** | {control_metrics.get('accuracy', {}).get('overall', 0)}% | {treatment_metrics.get('accuracy', {}).get('overall', 0)}% | {improvement.get('accuracy_improvement', 0)}% ↑ |
| 景点准确性 | {control_metrics.get('accuracy', {}).get('attraction_accuracy', 0)}% | {treatment_metrics.get('accuracy', {}).get('attraction_accuracy', 0)}% | - |
| 酒店准确性 | {control_metrics.get('accuracy', {}).get('hotel_accuracy', 0)}% | {treatment_metrics.get('accuracy', {}).get('hotel_accuracy', 0)}% | - |

### 完整性 (Completeness)

| 指标 | 对照组 | 实验组 | 改进 |
|------|--------|--------|------|
| **整体完整性** | {control_metrics.get('completeness', {}).get('overall', 0)}% | {treatment_metrics.get('completeness', {}).get('overall', 0)}% | {improvement.get('completeness_improvement', 0)}% ↑ |
| 包含景点 | {control_metrics.get('completeness', {}).get('has_attractions', 0)}% | {treatment_metrics.get('completeness', {}).get('has_attractions', 0)}% | - |
| 包含酒店 | {control_metrics.get('completeness', {}).get('has_hotels', 0)}% | {treatment_metrics.get('completeness', {}).get('has_hotels', 0)}% | - |
| 包含餐饮 | {control_metrics.get('completeness', {}).get('has_meals', 0)}% | {treatment_metrics.get('completeness', {}).get('has_meals', 0)}% | - |

---

## 统计显著性分析

### McNemar检验

用于比较两个相关样本的比例差异。

| 参数 | 值 |
|------|-----|
| 检验方法 | McNemar检验 |
| p值 | {sig.get('p_value', 'N/A')} |
| 是否显著 | {'✅ 是' if sig.get('significant') else '❌ 否'} |
| 置信水平 | {sig.get('confidence_level', 0.95) * 100}% |

> **结论**: {'差异具有统计显著性 (p < 0.05)' if sig.get('significant') else '差异不具有统计显著性'}

---

## 幻觉问题分析

### 问题类型分布

"""
        control_issues = control_hm.get('issue_by_type', {})
        treatment_issues = treatment_hm.get('issue_by_type', {})

        all_types = set(control_issues.keys()) | set(treatment_issues.keys())

        md += "| 问题类型 | 对照组 | 实验组 | 减少 |\n"
        md += "|----------|--------|--------|------|\n"

        issue_type_names = {
            "fake_attraction": "虚假景点",
            "fake_hotel": "虚假酒店",
            "wrong_location": "错误位置",
            "unreasonable_schedule": "不合理行程",
            "fake_food": "虚假美食",
            "wrong_coordinates": "错误坐标"
        }

        for issue_type in all_types:
            control_count = control_issues.get(issue_type, 0)
            treatment_count = treatment_issues.get(issue_type, 0)
            reduction = control_count - treatment_count
            type_name = issue_type_names.get(issue_type, issue_type)
            md += f"| {type_name} | {control_count} | {treatment_count} | {reduction} |\n"

        md += """
### 严重程度分布

"""
        control_severity = control_hm.get('severity_distribution', {})
        treatment_severity = treatment_hm.get('severity_distribution', {})

        md += "| 严重程度 | 对照组 | 实验组 |\n"
        md += "|----------|--------|--------|\n"
        for severity in ["high", "medium", "low"]:
            severity_names = {"high": "高", "medium": "中", "low": "低"}
            md += f"| {severity_names[severity]} | {control_severity.get(severity, 0)} | {treatment_severity.get(severity, 0)} |\n"

        md += f"""
---

## 结论与建议

### 主要结论

"""
        conclusions = []

        if improvement.get('hallucination_reduction', 0) > 0:
            conclusions.append(f"1. RAG增强显著降低了幻觉率，降幅达 **{improvement['hallucination_reduction']}%**")

        if improvement.get('accuracy_improvement', 0) > 0:
            conclusions.append(f"2. 信息准确性提升 **{improvement['accuracy_improvement']}%**")

        if sig.get('significant'):
            conclusions.append(f"3. 统计检验结果显著 (p={sig.get('p_value')}), 结果可信")
        else:
            conclusions.append(f"3. 统计检验结果不显著，建议增加样本量")

        for c in conclusions:
            md += f"- {c}\n"

        md += """
### 改进建议

1. **持续优化RAG检索质量**
   - 扩充知识库覆盖范围
   - 提高检索相关性

2. **增强幻觉检测能力**
   - 添加更多已知景点数据
   - 集成外部API验证

3. **提升用户体验**
   - 提供信息来源标注
   - 支持用户反馈纠错

---

## 附录

### 测试配置

```json
"""
        md += json.dumps(report.config.__dict__ if hasattr(report.config, '__dict__') else {}, ensure_ascii=False, indent=2)
        md += """
```

### 指标说明

| 指标 | 说明 | 计算方式 |
|------|------|----------|
| 幻觉率 | 包含虚假信息的行程比例 | (含幻觉行程数 / 总行程数) × 100% |
| 准确性 | 信息正确完整程度 | 正确信息数 / 总信息数 × 100% |
| 相关性 | 与用户需求匹配程度 | 匹配项数 / 总需求数 × 100% |
| 完整性 | 信息完整程度 | 完整项数 / 总项数 × 100% |

---

*报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""

        return md

    def _generate_html_report(
        self,
        report: Any,
        base_name: str
    ) -> Path:
        """生成HTML可视化报告"""
        file_path = self.output_dir / f"{base_name}.html"

        html_content = self._build_html_content(report)

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(html_content)

        logger.info(f"HTML报告已生成: {file_path}")
        return file_path

    def _build_html_content(self, report: Any) -> str:
        """构建HTML内容"""
        control_metrics = report.control_metrics
        treatment_metrics = report.treatment_metrics
        sig = report.statistical_significance
        improvement = report.improvement

        control_hm = control_metrics.get("hallucination_metrics", {})
        treatment_hm = treatment_metrics.get("hallucination_metrics", {})

        return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>RAG效果评估报告 - {report.test_name}</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        .header {{
            text-align: center;
            color: white;
            margin-bottom: 30px;
        }}
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
        }}
        .header p {{
            opacity: 0.9;
            font-size: 1.1em;
        }}
        .card {{
            background: white;
            border-radius: 16px;
            padding: 24px;
            margin-bottom: 20px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.1);
        }}
        .card h2 {{
            color: #333;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid #eee;
        }}
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
        }}
        .metric-card {{
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            border-radius: 12px;
            padding: 20px;
            text-align: center;
        }}
        .metric-card.highlight {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }}
        .metric-value {{
            font-size: 2.5em;
            font-weight: bold;
            margin: 10px 0;
        }}
        .metric-label {{
            font-size: 0.9em;
            opacity: 0.8;
        }}
        .metric-change {{
            font-size: 0.85em;
            margin-top: 5px;
        }}
        .metric-change.positive {{
            color: #10b981;
        }}
        .metric-change.negative {{
            color: #ef4444;
        }}
        .comparison-table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
        }}
        .comparison-table th,
        .comparison-table td {{
            padding: 12px 15px;
            text-align: left;
            border-bottom: 1px solid #eee;
        }}
        .comparison-table th {{
            background: #f8f9fa;
            font-weight: 600;
        }}
        .comparison-table tr:hover {{
            background: #f8f9fa;
        }}
        .chart-container {{
            position: relative;
            height: 300px;
            margin-top: 20px;
        }}
        .stat-box {{
            display: inline-block;
            padding: 10px 20px;
            border-radius: 8px;
            margin: 5px;
        }}
        .stat-box.success {{
            background: #d1fae5;
            color: #065f46;
        }}
        .stat-box.warning {{
            background: #fef3c7;
            color: #92400e;
        }}
        .stat-box.info {{
            background: #dbeafe;
            color: #1e40af;
        }}
        .conclusion-list {{
            list-style: none;
        }}
        .conclusion-list li {{
            padding: 10px 15px;
            margin: 8px 0;
            background: #f0fdf4;
            border-left: 4px solid #10b981;
            border-radius: 0 8px 8px 0;
        }}
        .formula-box {{
            background: #1e293b;
            color: #e2e8f0;
            padding: 15px 20px;
            border-radius: 8px;
            font-family: 'Courier New', monospace;
            margin: 15px 0;
        }}
        .footer {{
            text-align: center;
            color: white;
            opacity: 0.8;
            margin-top: 30px;
            padding: 20px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🧪 RAG效果评估报告</h1>
            <p>{report.test_name} | 测试时间: {report.start_time[:10]}</p>
        </div>

        <div class="card">
            <h2>📊 核心指标概览</h2>
            <div class="metrics-grid">
                <div class="metric-card highlight">
                    <div class="metric-label">幻觉率降低</div>
                    <div class="metric-value">{improvement.get('hallucination_reduction', 0)}%</div>
                    <div class="metric-change">从 {control_hm.get('hallucination_rate', 0)}% → {treatment_hm.get('hallucination_rate', 0)}%</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">准确性提升</div>
                    <div class="metric-value">{improvement.get('accuracy_improvement', 0)}%</div>
                    <div class="metric-change">从 {control_metrics.get('accuracy', {}).get('overall', 0)}% → {treatment_metrics.get('accuracy', {}).get('overall', 0)}%</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">完整性提升</div>
                    <div class="metric-value">{improvement.get('completeness_improvement', 0)}%</div>
                    <div class="metric-change">从 {control_metrics.get('completeness', {}).get('overall', 0)}% → {treatment_metrics.get('completeness', {}).get('overall', 0)}%</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">样本规模</div>
                    <div class="metric-value">{len(report.control_results) + len(report.treatment_results)}</div>
                    <div class="metric-change">对照组 {len(report.control_results)} / 实验组 {len(report.treatment_results)}</div>
                </div>
            </div>
        </div>

        <div class="card">
            <h2>📈 幻觉率详细分析</h2>
            <div class="formula-box">
                幻觉率 = (含幻觉的行程数 / 总评估行程数) × 100%
            </div>
            <table class="comparison-table">
                <thead>
                    <tr>
                        <th>指标</th>
                        <th>对照组 (无RAG)</th>
                        <th>实验组 (有RAG)</th>
                        <th>改进</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td><strong>幻觉率</strong></td>
                        <td>{control_hm.get('hallucination_rate', 0)}%</td>
                        <td>{treatment_hm.get('hallucination_rate', 0)}%</td>
                        <td class="positive">↓ {improvement.get('hallucination_reduction', 0)}%</td>
                    </tr>
                    <tr>
                        <td>含幻觉行程数</td>
                        <td>{control_hm.get('hallucinated_plans', 0)}</td>
                        <td>{treatment_hm.get('hallucinated_plans', 0)}</td>
                        <td>-</td>
                    </tr>
                    <tr>
                        <td>总问题数</td>
                        <td>{control_hm.get('total_issues', 0)}</td>
                        <td>{treatment_hm.get('total_issues', 0)}</td>
                        <td>-</td>
                    </tr>
                    <tr>
                        <td>平均问题数/行程</td>
                        <td>{control_hm.get('avg_issues_per_plan', 0)}</td>
                        <td>{treatment_hm.get('avg_issues_per_plan', 0)}</td>
                        <td>-</td>
                    </tr>
                </tbody>
            </table>
            <div class="chart-container">
                <canvas id="hallucinationChart"></canvas>
            </div>
        </div>

        <div class="card">
            <h2>🔬 统计显著性分析</h2>
            <div style="margin: 20px 0;">
                <span class="stat-box {'success' if sig.get('significant') else 'warning'}">
                    {'✅ 结果显著' if sig.get('significant') else '⚠️ 结果不显著'}
                </span>
                <span class="stat-box info">
                    p值 = {sig.get('p_value', 'N/A')}
                </span>
                <span class="stat-box info">
                    置信水平 = {sig.get('confidence_level', 0.95) * 100}%
                </span>
            </div>
            <p>
                <strong>McNemar检验</strong>: 用于比较两个相关样本的比例差异。
                {'差异具有统计显著性 (p < 0.05)，结果可信。' if sig.get('significant') else '差异不具有统计显著性，建议增加样本量。'}
            </p>
        </div>

        <div class="card">
            <h2>📋 主要结论</h2>
            <ul class="conclusion-list">
                <li>RAG增强显著降低了幻觉率，降幅达 <strong>{improvement.get('hallucination_reduction', 0)}%</strong></li>
                <li>信息准确性提升 <strong>{improvement.get('accuracy_improvement', 0)}%</strong></li>
                <li>完整性提升 <strong>{improvement.get('completeness_improvement', 0)}%</strong></li>
                <li>{'统计检验结果显著，结果可信' if sig.get('significant') else '建议增加样本量以获得更可靠的结论'}</li>
            </ul>
        </div>

        <div class="footer">
            <p>报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p>智能旅行助手 RAG评估系统</p>
        </div>
    </div>

    <script>
        const ctx = document.getElementById('hallucinationChart').getContext('2d');
        new Chart(ctx, {{
            type: 'bar',
            data: {{
                labels: ['虚假景点', '虚假酒店', '错误位置', '不合理行程', '虚假美食'],
                datasets: [{{
                    label: '对照组 (无RAG)',
                    data: [
                        {control_hm.get('issue_by_type', {}).get('fake_attraction', 0)},
                        {control_hm.get('issue_by_type', {}).get('fake_hotel', 0)},
                        {control_hm.get('issue_by_type', {}).get('wrong_location', 0)},
                        {control_hm.get('issue_by_type', {}).get('unreasonable_schedule', 0)},
                        {control_hm.get('issue_by_type', {}).get('fake_food', 0)}
                    ],
                    backgroundColor: 'rgba(239, 68, 68, 0.7)',
                    borderColor: 'rgba(239, 68, 68, 1)',
                    borderWidth: 1
                }}, {{
                    label: '实验组 (有RAG)',
                    data: [
                        {treatment_hm.get('issue_by_type', {}).get('fake_attraction', 0)},
                        {treatment_hm.get('issue_by_type', {}).get('fake_hotel', 0)},
                        {treatment_hm.get('issue_by_type', {}).get('wrong_location', 0)},
                        {treatment_hm.get('issue_by_type', {}).get('unreasonable_schedule', 0)},
                        {treatment_hm.get('issue_by_type', {}).get('fake_food', 0)}
                    ],
                    backgroundColor: 'rgba(16, 185, 129, 0.7)',
                    borderColor: 'rgba(16, 185, 129, 1)',
                    borderWidth: 1
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{
                        position: 'top',
                    }},
                    title: {{
                        display: true,
                        text: '幻觉问题类型分布对比'
                    }}
                }},
                scales: {{
                    y: {{
                        beginAtZero: true
                    }}
                }}
            }}
        }});
    </script>
</body>
</html>
"""

    def generate_interview_summary(self, report: Any) -> str:
        """
        生成面试展示摘要

        返回适合面试时口述的简洁摘要
        """
        control_hm = report.control_metrics.get("hallucination_metrics", {})
        treatment_hm = report.treatment_metrics.get("hallucination_metrics", {})
        improvement = report.improvement
        sig = report.statistical_significance

        return f"""
【RAG效果评估 - 面试要点】

1. 项目背景
   - 问题：AI生成旅行计划存在"幻觉"问题，会生成不存在的景点、酒店等虚假信息
   - 解决方案：引入RAG（检索增强生成）技术，基于真实游记数据增强生成质量

2. 核心指标：幻觉率
   - 定义：幻觉率 = (含幻觉的行程数 / 总评估行程数) × 100%
   - 优化前：{control_hm.get('hallucination_rate', 0)}%
   - 优化后：{treatment_hm.get('hallucination_rate', 0)}%
   - 降低幅度：{improvement.get('hallucination_reduction', 0)}%

3. A/B测试方法
   - 对照组：无RAG增强的传统生成
   - 实验组：有RAG增强的生成
   - 样本量：{len(report.control_results) + len(report.treatment_results)}个旅行计划
   - 统计检验：McNemar检验，p值={sig.get('p_value', 'N/A')}

4. 其他改进
   - 准确性提升：{improvement.get('accuracy_improvement', 0)}%
   - 完整性提升：{improvement.get('completeness_improvement', 0)}%

5. 结论
   - {'RAG显著提升了旅行计划质量，统计检验结果显著' if sig.get('significant') else 'RAG有积极效果，建议继续优化'}
   - 幻觉率从{control_hm.get('hallucination_rate', 0)}%降至{treatment_hm.get('hallucination_rate', 0)}%
"""
