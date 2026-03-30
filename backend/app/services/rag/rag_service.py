"""
RAG检索服务
功能：
1. 文本检索：景点、美食、酒店推荐
2. 图片检索：景点图片兜底
3. 混合检索：多模态检索
4. 结果缓存
5. 性能监控
6. 批量数据索引
"""

from typing import List, Dict, Optional, Any
import asyncio
import time
from loguru import logger
from dataclasses import dataclass
from functools import wraps
import hashlib
import json

from .embedding_service import EmbeddingService, get_embedding_service, EmbeddingResult
from .vector_store import VectorStore, get_vector_store, SearchResult


class RAGServiceError(Exception):
    """RAG服务错误基类"""
    pass


class SearchError(RAGServiceError):
    """搜索错误"""
    pass


class IndexError(RAGServiceError):
    """索引错误"""
    pass


@dataclass
class RAGSearchResult:
    """RAG搜索结果"""
    id: str
    content: str
    score: float
    metadata: Dict[str, Any]
    source: str


@dataclass
class RAGConfig:
    """RAG服务配置"""
    enable_cache: bool = True
    cache_ttl: int = 3600  # 缓存有效期（秒）
    min_score_threshold: float = 0.3  # 最小分数阈值
    max_n_results: int = 10  # 最大返回结果数
    batch_index_size: int = 20  # 批量索引大小
    max_concurrent_indexing: int = 5  # 最大并发索引数


class RAGService:
    """RAG检索服务类"""

    _instance: Optional['RAGService'] = None
    _lock = asyncio.Lock()

    def __init__(self, config: RAGConfig):
        """
        初始化RAG服务

        Args:
            config: RAG配置
        """
        self.config = config

        # 初始化各组件
        self._embedding_service: Optional[EmbeddingService] = None
        self._vector_store: Optional[VectorStore] = None

        # 搜索结果缓存
        self._cache: Dict[str, tuple] = {}

        # 统计信息
        self._stats = {
            'total_searches': 0,
            'cache_hits': 0,
            'total_indexed': 0,
            'errors': 0
        }

        # 并发控制
        self._index_semaphore = asyncio.Semaphore(self.config.max_concurrent_indexing)

        logger.info("RAG服务已初始化")

    @classmethod
    async def get_instance(cls, config: Optional[RAGConfig] = None) -> 'RAGService':
        """获取RAG服务单例"""
        if cls._instance is None:
            async with cls._lock:
                if cls._instance is None:
                    cfg = config or RAGConfig()
                    cls._instance = cls(cfg)
                    await cls._instance._initialize()
        return cls._instance

    async def _initialize(self):
        """初始化各个组件"""
        # 初始化向量化服务
        self._embedding_service = await get_embedding_service()

        # 初始化向量存储
        self._vector_store = await get_vector_store()

        logger.info("RAG服务组件初始化完成")

    def _get_cache_key(self, query: str, search_type: str = 'text') -> str:
        """生成缓存键"""
        key = f"{search_type}:{query}"
        return hashlib.md5(key.encode()).hexdigest()

    def _get_from_cache(self, query: str, search_type: str = 'text') -> Optional[List[RAGSearchResult]]:
        """从缓存获取结果"""
        if not self.config.enable_cache:
            return None

        cache_key = self._get_cache_key(query, search_type)
        if cache_key in self._cache:
            timestamp, results = self._cache[cache_key]
            if time.time() - timestamp < self.config.cache_ttl:
                self._stats['cache_hits'] += 1
                return results
            else:
                del self._cache[cache_key]
        return None

    def _add_to_cache(self, query: str, results: List[RAGSearchResult], search_type: str = 'text'):
        """添加结果到缓存"""
        if not self.config.enable_cache:
            return

        cache_key = self._get_cache_key(query, search_type)
        self._cache[cache_key] = (time.time(), results)

    async def search_text(
        self,
        query: str,
        n_results: int = 5,
        filter_params: Optional[Dict[str, Any]] = None
    ) -> List[RAGSearchResult]:
        """
        文本检索

        Args:
            query: 查询文本
            n_results: 返回结果数
            filter_params: 过滤参数

        Returns:
            搜索结果列表
        """
        # 检查缓存
        cached_results = self._get_from_cache(query, 'text')
        if cached_results:
            return cached_results[:n_results]

        self._stats['total_searches'] += 1

        try:
            # 获取查询的向量表示
            query_embedding = await self._embedding_service.embed_text(query)

            # 搜索向量数据库
            search_results = await self._vector_store.search(
                query_vector=query_embedding.embedding,
                n_results=min(n_results, self.config.max_n_results),
                filter_params=filter_params,
                score_threshold=self.config.min_score_threshold
            )

            # 转换为RAG搜索结果
            results = []
            for result in search_results:
                results.append(RAGSearchResult(
                    id=result.id,
                    content=result.content,
                    score=result.score,
                    metadata=result.metadata,
                    source='text'
                ))

            # 添加到缓存
            self._add_to_cache(query, results, 'text')

            return results

        except Exception as e:
            logger.error(f"文本搜索失败: {e}")
            self._stats['errors'] += 1
            raise SearchError(f"文本搜索失败: {e}")

    async def index_posts_batch(
        self,
        posts: List[Dict[str, Any]],
        progress_callback: Optional[callable] = None
    ) -> Dict[str, int]:
        """
        批量索引帖子数据

        Args:
            posts: 帖子列表，每个帖子包含 content 和 metadata
            progress_callback: 进度回调函数

        Returns:
            索引结果统计
        """
        if not posts:
            return {'success': 0, 'failed': 0}

        success_count = 0
        failed_count = 0

        for i in range(0, len(posts), self.config.batch_index_size):
            batch = posts[i:i + self.config.batch_index_size]

            async with self._index_semaphore:
                try:
                    # 提取内容
                    contents = [post.get('content', '') for post in batch]

                    # 批量向量化
                    embeddings_result = await self._embedding_service.embed_texts_batch(contents)
                    embeddings = embeddings_result.embeddings if hasattr(embeddings_result, 'embeddings') else embeddings_result

                    # 生成ID
                    doc_ids = [
                        post.get('metadata', {}).get('post_id', f"doc_{i+j}")
                        for j, post in enumerate(batch)
                    ]

                    # 元数据
                    metadatas = [post.get('metadata', {}) for post in batch]

                    # 批量添加到向量数据库
                    added = await self._vector_store.add_documents(
                        doc_ids=doc_ids,
                        contents=contents,
                        embeddings=embeddings,
                        metadatas=metadatas
                    )

                    success_count += added
                    self._stats['total_indexed'] += added

                except Exception as e:
                    logger.error(f"批量索引失败: {e}")
                    failed_count += len(batch)

            if progress_callback:
                progress_callback({
                    'progress_percent': (i + len(batch)) / len(posts) * 100,
                    'processed': i + len(batch),
                    'total': len(posts)
                })

        return {
            'success': success_count,
            'failed': failed_count
        }

    async def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        status = {
            'status': 'healthy',
            'embedding_service': 'unknown',
            'vector_store': 'unknown',
            'errors': []
        }

        try:
            # 检查向量化服务
            if self._embedding_service:
                status['embedding_service'] = 'ok'
            else:
                status['embedding_service'] = 'not_initialized'

            # 检查向量存储
            if self._vector_store:
                vector_health = await self._vector_store.health_check()
                status['vector_store'] = vector_health['status']
                if vector_health.get('errors'):
                    status['errors'].extend(vector_health['errors'])
            else:
                status['vector_store'] = 'not_initialized'

            # 综合状态
            if status['embedding_service'] != 'ok' or status['vector_store'] != 'healthy':
                status['status'] = 'degraded'

        except Exception as e:
            status['status'] = 'error'
            status['errors'].append(str(e))

        return status

    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        return {
            **self._stats,
            'cache_size': len(self._cache),
            'cache_hit_rate': (
                self._stats['cache_hits'] / self._stats['total_searches']
                if self._stats['total_searches'] > 0 else 0
            )
        }


async def get_rag_service(config: Optional[RAGConfig] = None) -> RAGService:
    """获取RAG服务实例的便捷函数"""
    return await RAGService.get_instance(config)