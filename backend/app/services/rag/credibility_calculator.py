"""
帖子置信度评分模块
基于四维加权评分卡计算帖子可信度

维度权重：
- 创作者可信度: 30%
- 内容质量: 40%
- 社区反馈: 20%
- 时效性: 10%
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import math
import re
from loguru import logger


@dataclass
class CredibilityScore:
    """置信度评分结果"""
    final_score: float  # 最终得分 [0, 1]
    creator_score: float  # 创作者得分
    content_score: float  # 内容质量得分
    community_score: float  # 社区反馈得分
    freshness_score: float  # 时效性得分
    details: Dict[str, Any]  # 评分明细


# 广告关键词列表
AD_KEYWORDS = [
    "合作", "赞助", "广告", "推广", "福利", "抽奖",
    "品牌方", "商单", "恰饭", "植入", "代言"
]

# 结构化信息关键词（地址、价格、营业时间等）
STRUCTURED_INFO_PATTERNS = [
    r'地址[：:]\s*[^\n]+',
    r'营业时间[：:]\s*[^\n]+',
    r'票价[：:]\s*[^\n]+',
    r'门票[：:]\s*[^\n]+',
    r'价格[：:]\s*[^\n]+',
    r'人均[：:]\s*[^\n]+',
    r'交通[：:]\s*[^\n]+',
    r'路线[：:]\s*[^\n]+',
    r'\d+路[公交地]车',
    r'地铁\d+号线',
]


class CredibilityCalculator:
    """置信度计算器"""

    def __init__(
        self,
        creator_weight: float = 0.3,
        content_weight: float = 0.4,
        community_weight: float = 0.2,
        freshness_weight: float = 0.1,
        credibility_threshold: float = 0.65,
        max_age_days: int = 730,  # 最大有效天数（2年）
        min_images_for_quality: int = 3,
        min_desc_length: int = 200
    ):
        self.creator_weight = creator_weight
        self.content_weight = content_weight
        self.community_weight = community_weight
        self.freshness_weight = freshness_weight
        self.credibility_threshold = credibility_threshold
        self.max_age_days = max_age_days
        self.min_images_for_quality = min_images_for_quality
        self.min_desc_length = min_desc_length

    def calculate(self, post: Dict[str, Any]) -> CredibilityScore:
        """
        计算帖子置信度

        Args:
            post: 帖子数据，包含以下字段：
                - creator_level: 创作者等级 (0-6)
                - is_verified: 是否认证
                - followers: 粉丝数
                - report_rate: 举报率
                - image_count: 图片数量
                - images: 图片URL列表
                - desc: 描述文本
                - tags: 标签列表
                - likes: 点赞数
                - comments: 评论数
                - collects: 收藏数
                - publish_time: 发布时间 (datetime 或 timestamp)
                - has_real_photos: 是否实拍图 (可选，默认True)
                - useful_comments_ratio: 有用评论比例 (可选)

        Returns:
            CredibilityScore 评分结果
        """
        details = {}

        # 1. 创作者可信度 (权重30%)
        creator_score, creator_details = self._calc_creator_score(post)
        details['creator'] = creator_details

        # 2. 内容质量 (权重40%)
        content_score, content_details = self._calc_content_score(post)
        details['content'] = content_details

        # 3. 社区反馈 (权重20%)
        community_score, community_details = self._calc_community_score(post)
        details['community'] = community_details

        # 4. 时效性 (权重10%)
        freshness_score, freshness_details = self._calc_freshness_score(post)
        details['freshness'] = freshness_details

        # 加权融合
        final_score = (
            creator_score * self.creator_weight +
            content_score * self.content_weight +
            community_score * self.community_weight +
            freshness_score * self.freshness_weight
        )

        return CredibilityScore(
            final_score=round(final_score, 3),
            creator_score=round(creator_score, 3),
            content_score=round(content_score, 3),
            community_score=round(community_score, 3),
            freshness_score=round(freshness_score, 3),
            details=details
        )

    def _calc_creator_score(self, post: Dict) -> tuple:
        """计算创作者可信度"""
        score = 0.0
        details = {}

        # 是否认证博主 (0.3分)
        is_verified = post.get('is_verified', False)
        if is_verified:
            score += 0.3
        details['is_verified'] = is_verified

        # 粉丝量对数缩放 (最高0.2分，5万粉=0.2)
        followers = post.get('followers', 0)
        follower_score = min(0.2, 0.2 * math.log10(followers + 1) / math.log10(50001))
        score += follower_score
        details['followers'] = followers
        details['follower_score'] = round(follower_score, 3)

        # 历史举报率<5% (0.1分)
        report_rate = post.get('report_rate', 0)
        if report_rate < 0.05:
            score += 0.1
        details['report_rate'] = report_rate
        details['low_report'] = report_rate < 0.05

        return min(score, 1.0), details

    def _calc_content_score(self, post: Dict) -> tuple:
        """计算内容质量"""
        score = 0.0
        details = {}

        # 图片数量 >= 3张实拍图 (0.25分)
        images = post.get('images', [])
        image_count = post.get('image_count', len(images))
        has_real_photos = post.get('has_real_photos', True)  # 默认为实拍

        if image_count >= self.min_images_for_quality and has_real_photos:
            score += 0.25
        details['image_count'] = image_count
        details['has_real_photos'] = has_real_photos

        # 描述 > 200字 (0.15分)
        desc = post.get('desc', '')
        desc_length = len(desc)
        if desc_length > self.min_desc_length:
            score += 0.15
        details['desc_length'] = desc_length

        # 含结构化信息（地址/价格/营业时间）(0.2分)
        has_structured = self._has_structured_info(desc)
        if has_structured:
            score += 0.2
        details['has_structured_info'] = has_structured

        # 无广告关键词 (0.15分)
        has_ad = self._contains_ad_keywords(desc)
        if not has_ad:
            score += 0.15
        details['contains_ad'] = has_ad

        return min(score, 1.0), details

    def _calc_community_score(self, post: Dict) -> tuple:
        """计算社区反馈"""
        score = 0.0
        details = {}

        # 收藏/点赞比 > 0.3 (0.2分)
        likes = post.get('likes', 0)
        collects = post.get('collects', 0)
        comments = post.get('comments', 0)

        engagement_ratio = collects / max(likes, 1)
        if engagement_ratio > 0.3:
            score += 0.2
        details['engagement_ratio'] = round(engagement_ratio, 3)
        details['likes'] = likes
        details['collects'] = collects

        # 有用评论占比 > 50% (0.1分)
        useful_ratio = post.get('useful_comments_ratio', 0.5)  # 默认50%
        if useful_ratio > 0.5:
            score += 0.1
        details['useful_comments_ratio'] = useful_ratio

        return min(score, 1.0), details

    def _calc_freshness_score(self, post: Dict) -> tuple:
        """计算时效性"""
        details = {}

        publish_time = post.get('publish_time')
        if publish_time is None:
            # 如果没有发布时间，假设为较老内容
            days_old = 365
        elif isinstance(publish_time, (int, float)):
            # timestamp
            publish_time = datetime.fromtimestamp(publish_time)
            days_old = (datetime.now() - publish_time).days
        elif isinstance(publish_time, datetime):
            days_old = (datetime.now() - publish_time).days
        else:
            days_old = 365

        # 线性衰减：max_age_days天内有效
        freshness_score = max(0, 1.0 - days_old / self.max_age_days)

        details['days_old'] = days_old
        details['publish_time'] = str(publish_time) if publish_time else None

        return freshness_score, details

    def _has_structured_info(self, text: str) -> bool:
        """检查是否包含结构化信息"""
        for pattern in STRUCTURED_INFO_PATTERNS:
            if re.search(pattern, text):
                return True
        return False

    def _contains_ad_keywords(self, text: str) -> bool:
        """检查是否包含广告关键词"""
        text_lower = text.lower()
        for keyword in AD_KEYWORDS:
            if keyword in text_lower:
                return True
        return False

    def is_credible(self, post: Dict) -> bool:
        """判断帖子是否可信（超过阈值）"""
        score = self.calculate(post)
        return score.final_score >= self.credibility_threshold

    def get_filter_condition(self):
        """获取Qdrant过滤条件（用于检索时过滤）"""
        from qdrant_client.models import FieldCondition, Range

        return FieldCondition(
            key="credibility",
            range=Range(gte=self.credibility_threshold)
        )


# 默认实例
default_calculator = CredibilityCalculator()


def calculate_credibility(post: Dict[str, Any]) -> CredibilityScore:
    """计算帖子置信度（便捷函数）"""
    return default_calculator.calculate(post)


def is_credible_post(post: Dict[str, Any]) -> bool:
    """判断帖子是否可信（便捷函数）"""
    return default_calculator.is_credible(post)