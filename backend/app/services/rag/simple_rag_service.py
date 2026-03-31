"""
简单的文本检索服务 - 从Qdrant数据库检索
功能：
1. 从Qdrant travel_documents集合中检索文档
2. 关键词匹配搜索（基于payload内容）
3. 标签匹配搜索
4. 不使用向量相似度，纯文本匹配
"""

from typing import List, Dict, Optional, Any
from dataclasses import dataclass
import re
import json
from loguru import logger

from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchText

from app.config import get_settings


@dataclass
class SearchResult:
    """搜索结果"""
    id: str
    title: str
    content: str
    score: float
    tags: List[str]
    image_urls: List[str]
    keyword: str


@dataclass
class SimpleRAGConfig:
    """简单RAG配置"""
    collection_name: str = "travel_documents"
    min_score_threshold: float = 0.1
    max_results: int = 10


class SimpleRAGService:
    """简单文本检索服务 - Qdrant"""

    _instance: Optional['SimpleRAGService'] = None

    def __init__(self, config: Optional[SimpleRAGConfig] = None):
        self.config = config or SimpleRAGConfig()
        self.settings = get_settings()
        self._client: Optional[QdrantClient] = None
        self._initialized = False

    @classmethod
    def get_instance(cls, config: Optional[SimpleRAGConfig] = None) -> 'SimpleRAGService':
        """获取单例实例"""
        if cls._instance is None:
            cls._instance = cls(config)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        """初始化Qdrant连接"""
        if self._initialized:
            return

        try:
            self._client = QdrantClient(
                url=self.settings.qdrant_url,
                api_key=self.settings.qdrant_api_key,
                timeout=30
            )
            self._initialized = True
            logger.info("Qdrant连接成功")
        except Exception as e:
            logger.error(f"Qdrant连接失败: {e}")
            raise

    def _parse_tags(self, tags) -> List[str]:
        """解析tags"""
        if not tags:
            return []
        if isinstance(tags, list):
            return tags
        # 字符串格式: "旅游攻略[话题],本地人做的攻略[话题],..."
        tags_str = str(tags)
        parsed = re.findall(r'([^,\[\]]+)\[话题\]', tags_str)
        if not parsed:
            parsed = [t.strip() for t in tags_str.split(',') if t.strip()]
        return parsed

    def _parse_image_urls(self, urls) -> List[str]:
        """解析image_urls"""
        if not urls:
            return []
        if isinstance(urls, list):
            return urls
        # 字符串格式需要JSON解析
        try:
            parsed = json.loads(str(urls))
            return parsed if isinstance(parsed, list) else []
        except json.JSONDecodeError:
            return []

    def _calculate_text_score(self, query: str, payload: Dict) -> float:
        """计算文本匹配分数"""
        score = 0.0
        query_lower = query.lower()
        query_words = re.findall(r'\w+', query_lower)

        title = payload.get('title', '').lower()
        content = payload.get('content', '').lower()
        tags_str = payload.get('tags', '')

        # 标题匹配（权重最高）
        for word in query_words:
            if word in title:
                score += 0.5
        if query_lower in title:
            score += 0.5

        # 内容匹配（权重较低）
        for word in query_words:
            if word in content:
                score += 0.1

        # 标签匹配（权重较高）
        tags = self._parse_tags(tags_str)
        for tag in tags:
            tag_lower = tag.lower()
            for word in query_words:
                if word in tag_lower:
                    score += 0.3
            if query_lower == tag_lower:
                score += 0.6

        return min(score, 1.0)

    def search(
        self,
        query: str,
        n_results: int = 5,
        score_threshold: Optional[float] = None
    ) -> List[SearchResult]:
        """
        文本检索

        Args:
            query: 搜索关键词
            n_results: 返回结果数量
            score_threshold: 分数阈值

        Returns:
            搜索结果列表
        """
        self._ensure_initialized()

        threshold = score_threshold or self.config.min_score_threshold
        n_results = min(n_results, self.config.max_results)

        try:
            # scroll获取数据进行文本匹配
            points, _ = self._client.scroll(
                collection_name=self.config.collection_name,
                limit=1000,
                with_payload=True,
                with_vectors=False
            )

            # 计算分数并排序
            scored_results = []
            for point in points:
                payload = point.payload or {}
                score = self._calculate_text_score(query, payload)
                if score >= threshold:
                    scored_results.append((score, point))

            # 按分数降序排序
            scored_results.sort(key=lambda x: x[0], reverse=True)

            # 构建返回结果
            results = []
            for score, point in scored_results[:n_results]:
                payload = point.payload or {}
                results.append(SearchResult(
                    id=str(point.id),
                    title=payload.get('title', ''),
                    content=payload.get('content', ''),
                    score=score,
                    tags=self._parse_tags(payload.get('tags', '')),
                    image_urls=self._parse_image_urls(payload.get('image_urls', '')),
                    keyword=payload.get('keyword', '')
                ))

            logger.info(f"文本搜索 '{query}' 找到 {len(results)} 条结果")
            return results

        except Exception as e:
            logger.error(f"文本搜索失败: {e}")
            return []

    def get_collection_stats(self) -> Dict[str, Any]:
        """获取集合统计信息"""
        self._ensure_initialized()

        try:
            info = self._client.get_collection(self.config.collection_name)
            return {
                'points_count': info.points_count,
                'status': info.status.value,
                'collection_name': self.config.collection_name
            }
        except Exception as e:
            logger.error(f"获取集合信息失败: {e}")
            return {'error': str(e)}

    def _ensure_initialized(self):
        """确保已初始化"""
        if not self._initialized or self._client is None:
            raise RuntimeError("Qdrant未初始化，请先调用get_instance()")

    def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        status = {
            'status': 'healthy',
            'qdrant_connection': 'unknown',
            'collection': 'unknown',
            'errors': []
        }

        try:
            self._ensure_initialized()
            stats = self.get_collection_stats()
            status['qdrant_connection'] = 'ok'
            status['collection'] = 'ok'
            status['points_count'] = stats.get('points_count', 0)
        except Exception as e:
            status['status'] = 'error'
            status['errors'].append(str(e))

        return status


def get_simple_rag_service(config: Optional[SimpleRAGConfig] = None) -> SimpleRAGService:
    """获取简单RAG服务实例"""
    return SimpleRAGService.get_instance(config)