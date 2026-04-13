"""
混合向量存储服务
适配现有 Qdrant 集合配置

现有集合：
- travel_documents: 4096维单向量（无命名）
- travel_images: 1152维单向量（无命名）

如需启用稀疏向量和多命名向量，需要重建集合
"""

from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import asyncio
import uuid
from loguru import logger

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
    Filter,
    FieldCondition,
    Range,
)
from qdrant_client.http.exceptions import UnexpectedResponse

from app.config import get_settings


@dataclass
class VectorConfig:
    """向量配置"""
    # 集合名称
    posts_collection: str = "travel_documents"
    images_collection: str = "travel_images"

    # 向量维度（匹配现有集合）
    posts_vector_size: int = 4096
    images_vector_size: int = 1152

    # 性能配置
    timeout: float = 30.0
    batch_size: int = 100


@dataclass
class PostPayload:
    """帖子Payload结构"""
    post_id: str
    title: str
    content: str
    tags: List[str]
    credibility: float
    publish_time: Optional[datetime] = None
    image_count: int = 0
    image_urls: List[str] = field(default_factory=list)
    keyword: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "post_id": self.post_id,
            "title": self.title,
            "content": self.content,
            "tags": self.tags,
            "credibility": self.credibility,
            "publish_time": self.publish_time.isoformat() if self.publish_time else None,
            "image_count": self.image_count,
            "image_urls": self.image_urls,
            "keyword": self.keyword,
        }


@dataclass
class ImagePayload:
    """图片Payload结构"""
    post_id: str
    image_idx: int
    image_url: str
    ocr_text: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "post_id": self.post_id,
            "image_idx": self.image_idx,
            "image_url": self.image_url,
            "ocr_text": self.ocr_text,
        }


@dataclass
class SearchResult:
    """搜索结果"""
    id: str
    score: float
    credibility: float = 0.0
    payload: Dict[str, Any] = field(default_factory=dict)


class HybridVectorStore:
    """向量存储（适配现有集合）"""

    _instance: Optional['HybridVectorStore'] = None
    _lock = asyncio.Lock()

    def __init__(self, config: Optional[VectorConfig] = None):
        self.config = config or VectorConfig()
        self.settings = get_settings()
        self._client: Optional[QdrantClient] = None
        self._initialized = False

    @classmethod
    async def get_instance(cls, config: Optional[VectorConfig] = None) -> 'HybridVectorStore':
        """获取单例实例"""
        if cls._instance is None:
            async with cls._lock:
                if cls._instance is None:
                    cls._instance = cls(config)
                    await cls._instance._initialize()
        return cls._instance

    async def _initialize(self):
        """初始化连接"""
        if self._initialized:
            return

        try:
            self._client = QdrantClient(
                url=self.settings.qdrant_url,
                api_key=self.settings.qdrant_api_key,
                timeout=self.config.timeout
            )

            # 自动创建集合（如果不存在）
            await self._ensure_collections_exist()

            self._initialized = True
            logger.info("向量存储连接成功")
        except Exception as e:
            logger.error(f"向量存储初始化失败: {e}")
            raise

    async def _ensure_collections_exist(self):
        """确保所需的集合存在"""
        from qdrant_client.models import VectorParams, Distance

        # 检查并创建帖子集合
        try:
            self._client.get_collection(self.config.posts_collection)
            logger.debug(f"集合 {self.config.posts_collection} 已存在")
        except Exception:
            logger.info(f"创建集合 {self.config.posts_collection}")
            self._client.create_collection(
                collection_name=self.config.posts_collection,
                vectors_config=VectorParams(
                    size=self.config.posts_vector_size,
                    distance=Distance.COSINE
                )
            )

        # 检查并创建图片集合
        try:
            self._client.get_collection(self.config.images_collection)
            logger.debug(f"集合 {self.config.images_collection} 已存在")
        except Exception:
            logger.info(f"创建集合 {self.config.images_collection}")
            self._client.create_collection(
                collection_name=self.config.images_collection,
                vectors_config=VectorParams(
                    size=self.config.images_vector_size,
                    distance=Distance.COSINE
                )
            )

    def _ensure_initialized(self):
        """确保已初始化"""
        if not self._initialized or self._client is None:
            raise RuntimeError("VectorStore未初始化")

    async def upsert_post(
        self,
        post_id: str,
        dense_vector: List[float],
        payload=None
    ) -> bool:
        """
        插入/更新帖子向量

        Args:
            post_id: 帖子ID
            dense_vector: 密集向量 (4096维)
            payload: 可以是 PostPayload 对象或 dict

        Returns:
            是否成功
        """
        self._ensure_initialized()

        if not dense_vector:
            logger.warning(f"帖子向量为空: {post_id}")
            return False

        try:
            point_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, post_id))

            # 处理 payload
            if payload is None:
                payload_dict = {"post_id": post_id}
            elif isinstance(payload, PostPayload):
                payload_dict = payload.to_dict()
            elif isinstance(payload, dict):
                payload_dict = payload
            else:
                payload_dict = {"post_id": post_id}

            # 现有集合使用单向量（无命名）
            point = PointStruct(
                id=point_id,
                vector=dense_vector,  # 直接传向量，不用命名
                payload=payload_dict
            )

            self._client.upsert(
                collection_name=self.config.posts_collection,
                points=[point]
            )

            logger.debug(f"插入帖子向量成功: {post_id}")
            return True

        except Exception as e:
            logger.error(f"插入帖子向量失败: {e}")
            return False

    async def upsert_posts_batch(self, posts: List[Dict[str, Any]]) -> int:
        """
        批量插入帖子

        Args:
            posts: 帖子列表，每个包含:
                - post_id
                - dense_vector (必需)
                - payload

        Returns:
            成功数量
        """
        self._ensure_initialized()

        points = []
        for post in posts:
            try:
                post_id = post['post_id']
                dense_vector = post.get('dense_vector')

                if not dense_vector:
                    logger.debug(f"跳过无向量的帖子: {post_id}")
                    continue

                point_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, post_id))

                payload = post.get('payload', {})
                if isinstance(payload, PostPayload):
                    payload = payload.to_dict()

                # 现有集合使用单向量
                points.append(PointStruct(
                    id=point_id,
                    vector=dense_vector,  # 直接传向量
                    payload=payload
                ))

            except Exception as e:
                logger.warning(f"构建帖子point失败: {e}")
                continue

        if not points:
            logger.warning("没有有效的帖子可插入")
            return 0

        try:
            self._client.upsert(
                collection_name=self.config.posts_collection,
                points=points
            )
            logger.info(f"批量插入帖子: {len(points)} 条")
            return len(points)

        except Exception as e:
            logger.error(f"批量插入帖子失败: {e}")
            return 0

    async def upsert_image(
        self,
        post_id: str,
        image_idx: int,
        dense_vector: List[float],
        payload=None
    ) -> bool:
        """
        插入图片向量

        Args:
            post_id: 帖子ID
            image_idx: 图片索引
            dense_vector: 密集向量 (1152维)
            payload: 可以是 ImagePayload 对象或 dict

        Returns:
            是否成功
        """
        self._ensure_initialized()

        if not dense_vector:
            logger.warning(f"图片向量为空: {post_id}_{image_idx}")
            return False

        try:
            point_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{post_id}_{image_idx}"))

            # 处理 payload
            if payload is None:
                payload_dict = {
                    "post_id": post_id,
                    "image_idx": image_idx
                }
            elif isinstance(payload, ImagePayload):
                payload_dict = payload.to_dict()
            elif isinstance(payload, dict):
                payload_dict = payload
            else:
                payload_dict = {
                    "post_id": post_id,
                    "image_idx": image_idx
                }

            # 现有集合使用单向量
            point = PointStruct(
                id=point_id,
                vector=dense_vector,  # 直接传向量
                payload=payload_dict
            )

            self._client.upsert(
                collection_name=self.config.images_collection,
                points=[point]
            )

            return True

        except Exception as e:
            logger.error(f"插入图片向量失败: {e}")
            return False

    async def search_posts(
        self,
        query_vector: List[float],
        n_results: int = 10,
        credibility_threshold: float = 0.0
    ) -> List[SearchResult]:
        """
        搜索帖子

        Args:
            query_vector: 查询向量
            n_results: 返回数量
            credibility_threshold: 置信度阈值（需要Qdrant索引支持）

        Returns:
            搜索结果
        """
        self._ensure_initialized()

        if not query_vector:
            return []

        try:
            # 注意：credibility过滤需要Qdrant索引
            # 如果索引不存在，Qdrant会返回400错误
            # 因此这里不使用过滤，在结果中后处理
            results = self._client.query_points(
                collection_name=self.config.posts_collection,
                query=query_vector,
                limit=n_results * 2,  # 获取更多结果用于后过滤
                with_payload=True
            )

            search_results = []
            for point in results.points:
                credibility = point.payload.get('credibility', 0) if point.payload else 0

                # 后过滤：跳过低置信度结果
                if credibility_threshold > 0 and credibility < credibility_threshold:
                    continue

                search_results.append(SearchResult(
                    id=str(point.id),
                    score=point.score,
                    credibility=credibility,
                    payload=point.payload or {}
                ))

                # 达到目标数量就停止
                if len(search_results) >= n_results:
                    break

            return search_results

        except Exception as e:
            logger.error(f"搜索帖子失败: {e}")
            return []

    async def search_images(
        self,
        query_vector: List[float],
        n_results: int = 10
    ) -> List[SearchResult]:
        """搜索图片"""
        self._ensure_initialized()

        if not query_vector:
            return []

        try:
            results = self._client.query_points(
                collection_name=self.config.images_collection,
                query=query_vector,
                limit=n_results,
                with_payload=True
            )

            search_results = []
            for point in results.points:
                search_results.append(SearchResult(
                    id=str(point.id),
                    score=point.score,
                    payload=point.payload or {}
                ))

            return search_results

        except Exception as e:
            logger.error(f"搜索图片失败: {e}")
            return []

    def get_collection_stats(self) -> Dict[str, Any]:
        """获取集合统计"""
        self._ensure_initialized()

        stats = {}
        try:
            posts_info = self._client.get_collection(self.config.posts_collection)
            stats['posts'] = {
                'count': posts_info.points_count,
                'status': posts_info.status.value,
                'vector_size': posts_info.config.params.vectors.size if hasattr(posts_info.config.params.vectors, 'size') else 'named_vectors'
            }
        except Exception as e:
            stats['posts'] = {'error': str(e)}

        try:
            images_info = self._client.get_collection(self.config.images_collection)
            stats['images'] = {
                'count': images_info.points_count,
                'status': images_info.status.value,
                'vector_size': images_info.config.params.vectors.size if hasattr(images_info.config.params.vectors, 'size') else 'named_vectors'
            }
        except Exception as e:
            stats['images'] = {'error': str(e)}

        return stats

    async def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        status = {
            'status': 'healthy',
            'qdrant_connection': 'unknown',
            'collections': {},
            'errors': []
        }

        try:
            self._ensure_initialized()
            status['qdrant_connection'] = 'ok'
            status['collections'] = self.get_collection_stats()
        except Exception as e:
            status['status'] = 'error'
            status['errors'].append(str(e))

        return status


async def get_hybrid_vector_store(config: Optional[VectorConfig] = None) -> HybridVectorStore:
    """获取向量存储实例"""
    return await HybridVectorStore.get_instance(config)