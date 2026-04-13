"""
混合检索服务
整合置信度过滤、多模态检索、重排序

检索流程：
1. 用户查询 -> 向量化
2. 时效过滤 + 置信度过滤
3. 密集向量检索 + 稀疏向量检索
4. 结果融合与重排
5. 返回结果
"""

from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import re
from loguru import logger

from .hybrid_vector_store import (
    HybridVectorStore,
    SearchResult,
    get_hybrid_vector_store
)
from .credibility_calculator import CredibilityCalculator


# 视觉关键词（用于判断是否启用图像检索）
VISUAL_KEYWORDS = [
    "夜景", "日出", "日落", "樱花", "枫叶", "雪景", "海滩",
    "露台", "花园", "湖景", "山景", "城市景观", "拍照",
    "打卡", "网红", "出片", "景色", "风景"
]


@dataclass
class HybridRAGConfig:
    """混合检索配置"""
    # 检索参数
    n_results: int = 10
    credibility_threshold: float = 0.65
    max_age_days: int = 730  # 2年

    # 重排权重
    dense_weight: float = 0.5
    sparse_weight: float = 0.3
    credibility_weight: float = 0.2

    # 多模态权重
    image_weight: float = 0.3
    enable_image_search: bool = True

    # 视觉关键词增强
    visual_keyword_boost: float = 0.1


@dataclass
class RAGSearchResult:
    """RAG检索结果"""
    post_id: str
    title: str
    content: str
    score: float
    credibility: float
    tags: List[str]
    image_urls: List[str]
    publish_time: Optional[str] = None

    # 评分明细
    dense_score: float = 0.0
    sparse_score: float = 0.0
    image_score: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "post_id": self.post_id,
            "title": self.title,
            "content": self.content,
            "score": self.score,
            "credibility": self.credibility,
            "tags": self.tags,
            "image_urls": self.image_urls,
            "publish_time": self.publish_time,
            "dense_score": self.dense_score,
            "sparse_score": self.sparse_score,
            "image_score": self.image_score,
        }


class HybridRAGService:
    """混合检索服务"""

    _instance: Optional['HybridRAGService'] = None

    def __init__(self, config: Optional[HybridRAGConfig] = None):
        self.config = config or HybridRAGConfig()
        self._vector_store: Optional[HybridVectorStore] = None
        self._embedding_service = None
        self._initialized = False

    @classmethod
    async def get_instance(cls, config: Optional[HybridRAGConfig] = None) -> 'HybridRAGService':
        """获取单例实例"""
        if cls._instance is None:
            cls._instance = cls(config)
            await cls._instance._initialize()
        return cls._instance

    async def _initialize(self):
        """初始化服务"""
        if self._initialized:
            return

        try:
            self._vector_store = await get_hybrid_vector_store()

            # 初始化向量化服务
            try:
                from .embedding_service import get_embedding_service
                self._embedding_service = get_embedding_service()
            except Exception as e:
                logger.warning(f"向量化服务不可用: {e}")

            self._initialized = True
            logger.info("混合检索服务初始化成功")

        except Exception as e:
            logger.error(f"混合检索服务初始化失败: {e}")
            raise

    async def search(
        self,
        query: str,
        n_results: Optional[int] = None,
        credibility_threshold: Optional[float] = None,
        enable_image: Optional[bool] = None
    ) -> List[RAGSearchResult]:
        """
        执行检索

        Args:
            query: 查询文本
            n_results: 返回结果数
            credibility_threshold: 置信度阈值
            enable_image: 是否启用图像检索

        Returns:
            检索结果列表
        """
        self._ensure_initialized()

        n_results = n_results or self.config.n_results
        credibility_threshold = credibility_threshold or self.config.credibility_threshold

        # 1. 向量化查询
        dense_vector = None
        sparse_vector = None

        if self._embedding_service:
            try:
                emb_result = await self._embedding_service.embed_text(query)
                if emb_result.success:
                    dense_vector = emb_result.embedding
            except Exception as e:
                logger.warning(f"查询向量化失败: {e}")

        # 生成稀疏向量
        sparse_vector = self._generate_sparse_vector(query)

        # 2. 判断是否包含视觉关键词
        has_visual_keyword = self._has_visual_keywords(query)
        image_weight = self.config.image_weight
        if has_visual_keyword:
            image_weight += self.config.visual_keyword_boost

        enable_image = enable_image if enable_image is not None else (
            self.config.enable_image_search and has_visual_keyword
        )

        # 3. 执行检索
        results = []

        if dense_vector:
            # 密集向量检索（现有集合不支持混合检索）
            results = await self._vector_store.search_posts(
                query_vector=dense_vector,
                n_results=n_results,
                credibility_threshold=credibility_threshold
            )
        else:
            # 向量化失败时，回退到简单文本检索
            logger.warning(f"查询向量化失败，回退到简单文本检索: {query}")
            from .simple_rag_service import get_simple_rag_service
            simple_service = get_simple_rag_service()
            simple_results = simple_service.search(query, n_results=n_results)

            # 转换结果格式
            for r in simple_results:
                results.append(SearchResult(
                    id=r.id,
                    score=r.score,
                    credibility=0.5,  # 默认置信度
                    payload={
                        'post_id': r.id,
                        'title': r.title,
                        'content': r.content,
                        'tags': r.tags,
                        'image_urls': r.image_urls
                    }
                ))

        # 4. 图像检索增强（如果启用）
        if enable_image and self._embedding_service:
            image_results = await self._search_images(query, n_results)
            results = self._merge_results(results, image_results, image_weight)

        # 5. 转换结果格式
        rag_results = []
        for r in results[:n_results]:
            rag_results.append(RAGSearchResult(
                post_id=r.payload.get('post_id', ''),
                title=r.payload.get('title', ''),
                content=r.payload.get('content', ''),
                score=r.score,
                credibility=r.credibility,
                tags=r.payload.get('tags', []),
                image_urls=r.payload.get('image_urls', []),
                publish_time=r.payload.get('publish_time'),
                dense_score=r.score,
                sparse_score=0.0,
                image_score=0.0
            ))

        logger.info(f"检索 '{query}' 返回 {len(rag_results)} 条结果")
        return rag_results

    async def search_by_city(
        self,
        query: str,
        city: str,
        n_results: int = 5
    ) -> List[RAGSearchResult]:
        """
        按城市过滤检索

        Args:
            query: 查询文本
            city: 城市名称
            n_results: 返回结果数

        Returns:
            检索结果
        """
        # 城市关键词加入查询
        enhanced_query = f"{city} {query}"
        results = await self.search(enhanced_query, n_results=n_results)

        # 后过滤确保城市相关
        filtered = []
        city_lower = city.lower()
        for r in results:
            # 检查标签或内容是否包含城市
            if (city_lower in r.title.lower() or
                city_lower in r.content.lower() or
                any(city_lower in tag.lower() for tag in r.tags)):
                filtered.append(r)

        return filtered[:n_results]

    async def _search_images(
        self,
        query: str,
        n_results: int
    ) -> List[SearchResult]:
        """
        图像检索（文本到图片搜索）

        Args:
            query: 搜索文本（如景点名称）
            n_results: 返回结果数

        Returns:
            图片搜索结果列表
        """
        if not self._embedding_service:
            logger.warning("向量化服务未初始化，无法进行图片检索")
            return []

        try:
            # 1. 将文本转换为图片搜索向量（1152维多模态嵌入）
            emb_result = await self._embedding_service.embed_text_for_image_search(query)

            if not emb_result.success or not emb_result.embedding:
                logger.warning(f"图片搜索文本向量化失败: {emb_result.error}")
                return []

            # 2. 使用向量搜索图片
            results = await self._vector_store.search_images(
                query_vector=emb_result.embedding,
                n_results=n_results
            )

            logger.info(f"图片检索 '{query}' 返回 {len(results)} 条结果")
            return results

        except Exception as e:
            logger.warning(f"图像检索失败: {e}")
            return []

    async def search_images_by_text(
        self,
        query: str,
        n_results: int = 10
    ) -> List[RAGSearchResult]:
        """
        通过文本搜索图片（公开接口）

        Args:
            query: 搜索文本（如景点名称）
            n_results: 返回结果数

        Returns:
            RAGSearchResult列表，包含image_urls
        """
        self._ensure_initialized()

        results = await self._search_images(query, n_results)

        # 转换为RAGSearchResult格式
        rag_results = []
        for r in results:
            rag_results.append(RAGSearchResult(
                post_id=r.payload.get('post_id', ''),
                title=r.payload.get('title', ''),
                content=r.payload.get('ocr_text', ''),
                score=r.score,
                credibility=0.5,  # 图片默认置信度
                tags=[],
                image_urls=[r.payload.get('image_url', '')] if r.payload.get('image_url') else [],
                image_score=r.score
            ))

        return rag_results

    def _merge_results(
        self,
        text_results: List[SearchResult],
        image_results: List[SearchResult],
        image_weight: float
    ) -> List[SearchResult]:
        """融合文本和图像结果"""
        if not image_results:
            return text_results

        # 以post_id为key合并
        merged = {r.payload.get('post_id', r.id): r for r in text_results}

        for img_r in image_results:
            post_id = img_r.payload.get('post_id')
            if post_id in merged:
                # 更新分数（简单融合）
                existing = merged[post_id]
                existing.score = existing.score * (1 - image_weight) + img_r.score * image_weight

        return sorted(merged.values(), key=lambda x: x.score, reverse=True)

    def _has_visual_keywords(self, query: str) -> bool:
        """判断查询是否包含视觉关键词"""
        query_lower = query.lower()
        for keyword in VISUAL_KEYWORDS:
            if keyword in query_lower:
                return True
        return False

    def _generate_sparse_vector(self, text: str) -> Dict[int, float]:
        """生成稀疏向量（使用hashlib确保跨进程一致性）"""
        import hashlib

        words = re.findall(r'\w+', text.lower())
        word_freq = {}
        for word in words:
            word_hash = int(hashlib.md5(word.encode()).hexdigest()[:8], 16) % 100000
            word_freq[word_hash] = word_freq.get(word_hash, 0) + 1

        max_freq = max(word_freq.values()) if word_freq else 1
        return {k: v / max_freq for k, v in word_freq.items()}

    def _ensure_initialized(self):
        """确保已初始化"""
        if not self._initialized:
            raise RuntimeError("HybridRAGService未初始化")

    async def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        status = {
            'status': 'healthy',
            'vector_store': 'unknown',
            'embedding_service': 'unknown',
            'errors': []
        }

        try:
            self._ensure_initialized()
            if self._vector_store:
                vs_health = await self._vector_store.health_check()
                status['vector_store'] = vs_health.get('status', 'ok')
            else:
                status['vector_store'] = 'not_initialized'

            status['embedding_service'] = 'ok' if self._embedding_service else 'not_configured'

        except Exception as e:
            status['status'] = 'error'
            status['errors'].append(str(e))

        return status

    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        if not self._vector_store:
            return {'status': 'not_initialized'}

        return self._vector_store.get_collection_stats()


async def get_hybrid_rag_service(config: Optional[HybridRAGConfig] = None) -> HybridRAGService:
    """获取混合检索服务实例"""
    return await HybridRAGService.get_instance(config)