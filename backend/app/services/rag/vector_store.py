"""
向量数据库管理
使用Qdrant Cloud作为向量存储
功能：
1. 集合管理（创建、删除、更新）
2. 向量操作（添加、搜索、删除）
3. 批量操作支持
4. 错误处理和重试机制
5. 连接池管理
6. 输入验证和安全检查
"""

from typing import List, Dict, Optional, Any, Union
import asyncio
from loguru import logger
from dataclasses import dataclass
from enum import Enum
from functools import wraps
import uuid
import time
import re

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue,
    OptimizersConfigDiff,
    HnswConfigDiff,
    PointsSelector,
    PointIdsList,
)
from qdrant_client.http.exceptions import UnexpectedResponse

from ..config import get_settings


class VectorStoreError(Exception):
    """向量数据库错误基类"""
    pass


class CollectionNotFoundError(VectorStoreError):
    """集合不存在错误"""
    pass


class VectorDimensionError(VectorStoreError):
    """向量维度错误"""
    pass


class ValidationError(VectorStoreError):
    """验证错误"""
    pass


class ConnectionError(VectorStoreError):
    """连接错误"""
    pass


class CollectionType(Enum):
    """集合类型枚举"""
    DOCUMENTS = "travel_documents"
    IMAGES = "travel_images"


@dataclass
class VectorConfig:
    """向量数据库配置"""
    documents_collection: str = "travel_documents"
    images_collection: str = "travel_images"
    documents_vector_size: int = 1024
    images_vector_size: int = 1024
    distance: str = "Cosine"
    max_retries: int = 3
    retry_delay: float = 1.0
    timeout: float = 30.0
    batch_size: int = 100
    max_concurrent_operations: int = 10


@dataclass
class SearchResult:
    """搜索结果"""
    id: str
    score: float
    payload: Dict[str, Any]


def retry_on_error(max_retries: int = 3, delay: float = 1.0):
    """重试装饰器"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_error = None
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except ConnectionError as e:
                    last_error = e
                    wait_time = delay * (2 ** attempt) * 2
                    logger.warning(
                        f"{func.__name__} 连接错误，{wait_time}秒后重试 ({attempt + 1}/{max_retries}): {e}"
                    )
                    await asyncio.sleep(wait_time)
                except Exception as e:
                    last_error = e
                    if attempt < max_retries - 1:
                        wait_time = delay * (2 ** attempt)
                        logger.warning(
                            f"{func.__name__} 失败，{wait_time}秒后重试 ({attempt + 1}/{max_retries}): {e}"
                        )
                        await asyncio.sleep(wait_time)
                    else:
                        logger.error(f"{func.__name__} 达到最大重试次数: {e}")
            raise last_error
        return wrapper
    return decorator


class InputValidator:
    """输入验证器"""
    
    MAX_ID_LENGTH = 256
    MAX_CONTENT_LENGTH = 10000
    MAX_PAYLOAD_SIZE = 100
    MAX_METADATA_VALUE_LENGTH = 1000
    
    @staticmethod
    def validate_id(id_value: str) -> str:
        """验证ID"""
        if not isinstance(id_value, str):
            raise ValidationError(f"ID类型错误: 期望str，实际{type(id_value)}")
        
        id_value = id_value.strip()
        
        if not id_value:
            raise ValidationError("ID不能为空")
        
        if len(id_value) > InputValidator.MAX_ID_LENGTH:
            raise ValidationError(f"ID长度超过限制: {len(id_value)} > {InputValidator.MAX_ID_LENGTH}")
        
        if not re.match(r'^[\w\-:.]+$', id_value):
            raise ValidationError(f"ID包含非法字符: {id_value}")
        
        return id_value
    
    @staticmethod
    def validate_content(content: str) -> str:
        """验证内容"""
        if not isinstance(content, str):
            raise ValidationError(f"内容类型错误: 期望str，实际{type(content)}")
        
        if len(content) > InputValidator.MAX_CONTENT_LENGTH:
            content = content[:InputValidator.MAX_CONTENT_LENGTH]
            logger.debug(f"内容已截断至{InputValidator.MAX_CONTENT_LENGTH}字符")
        
        return content
    
    @staticmethod
    def validate_embedding(embedding: List[float], expected_dim: int) -> List[float]:
        """验证向量"""
        if not isinstance(embedding, list):
            raise ValidationError(f"向量类型错误: 期望list，实际{type(embedding)}")
        
        if len(embedding) != expected_dim:
            raise VectorDimensionError(
                f"向量维度错误: 期望 {expected_dim}, 实际 {len(embedding)}"
            )
        
        for i, val in enumerate(embedding):
            if not isinstance(val, (int, float)):
                raise ValidationError(f"向量值类型错误: 索引{i}的值类型为{type(val)}")
        
        return embedding
    
    @staticmethod
    def validate_metadata(metadata: Dict[str, Any]) -> Dict[str, Any]:
        """验证元数据"""
        if not isinstance(metadata, dict):
            raise ValidationError(f"元数据类型错误: 期望dict，实际{type(metadata)}")
        
        if len(metadata) > InputValidator.MAX_PAYLOAD_SIZE:
            raise ValidationError(f"元数据字段数量超过限制: {len(metadata)} > {InputValidator.MAX_PAYLOAD_SIZE}")
        
        validated = {}
        for key, value in metadata.items():
            if not isinstance(key, str):
                raise ValidationError(f"元数据键类型错误: {key}")
            
            if len(key) > 100:
                raise ValidationError(f"元数据键长度超过限制: {key}")
            
            if isinstance(value, str):
                if len(value) > InputValidator.MAX_METADATA_VALUE_LENGTH:
                    value = value[:InputValidator.MAX_METADATA_VALUE_LENGTH]
            elif isinstance(value, (list, dict)):
                if len(str(value)) > InputValidator.MAX_METADATA_VALUE_LENGTH:
                    value = str(value)[:InputValidator.MAX_METADATA_VALUE_LENGTH]
            elif not isinstance(value, (int, float, bool, type(None))):
                value = str(value)
            
            validated[key] = value
        
        return validated


class VectorStore:
    """向量数据库管理类"""
    
    _instance: Optional['VectorStore'] = None
    _lock = asyncio.Lock()
    _semaphore: Optional[asyncio.Semaphore] = None
    
    def __init__(self, config: Optional[VectorConfig] = None):
        """
        初始化向量数据库
        
        Args:
            config: 向量数据库配置
        """
        self.config = config or VectorConfig()
        self.settings = get_settings()
        self.validator = InputValidator()
        
        self._client: Optional[QdrantClient] = None
        self._initialized = False
        
        self._semaphore = asyncio.Semaphore(self.config.max_concurrent_operations)
        
        logger.info(
            f"向量数据库管理器已初始化 - "
            f"集合: {self.config.documents_collection}, {self.config.images_collection}, "
            f"最大并发: {self.config.max_concurrent_operations}"
        )
    
    @classmethod
    async def get_instance(cls, config: Optional[VectorConfig] = None) -> 'VectorStore':
        """获取单例实例"""
        async with cls._lock:
            if cls._instance is None:
                cls._instance = cls(config)
                await cls._instance._initialize()
            return cls._instance
    
    async def _initialize(self):
        """初始化连接和集合"""
        if self._initialized:
            return
        
        try:
            if not self.settings.qdrant_url:
                raise ConnectionError("QDRANT_URL未配置")
            
            if not self.settings.qdrant_api_key:
                raise ConnectionError("QDRANT_API_KEY未配置")
            
            self._client = QdrantClient(
                url=self.settings.qdrant_url,
                api_key=self.settings.qdrant_api_key,
                timeout=self.config.timeout
            )
            
            await self._init_collections()
            
            self._initialized = True
            logger.info("Qdrant向量数据库连接成功")
            
        except Exception as e:
            logger.error(f"初始化向量数据库失败: {e}")
            raise VectorStoreError(f"初始化失败: {e}")
    
    async def _init_collections(self):
        """初始化集合"""
        try:
            collections = self._client.get_collections().collections
            collection_names = [c.name for c in collections]
            
            if self.config.documents_collection not in collection_names:
                self._client.create_collection(
                    collection_name=self.config.documents_collection,
                    vectors_config=VectorParams(
                        size=self.config.documents_vector_size,
                        distance=Distance.COSINE
                    ),
                    optimizers_config=OptimizersConfigDiff(
                        indexing_threshold=10000,
                    ),
                    hnsw_config=HnswConfigDiff(
                        m=16,
                        ef_construct=100,
                    )
                )
                logger.info(f"创建文档集合: {self.config.documents_collection}")
            
            if self.config.images_collection not in collection_names:
                self._client.create_collection(
                    collection_name=self.config.images_collection,
                    vectors_config=VectorParams(
                        size=self.config.images_vector_size,
                        distance=Distance.COSINE
                    ),
                    optimizers_config=OptimizersConfigDiff(
                        indexing_threshold=10000,
                    ),
                    hnsw_config=HnswConfigDiff(
                        m=16,
                        ef_construct=100,
                    )
                )
                logger.info(f"创建图片集合: {self.config.images_collection}")
                
        except Exception as e:
            logger.error(f"初始化集合失败: {e}")
            raise VectorStoreError(f"初始化集合失败: {e}")
    
    def _ensure_initialized(self):
        """确保已初始化"""
        if not self._initialized or self._client is None:
            raise VectorStoreError("向量数据库未初始化，请先调用 _initialize()")
    
    @retry_on_error(max_retries=3, delay=1.0)
    async def add_document(
        self,
        doc_id: str,
        content: str,
        embedding: List[float],
        metadata: Dict[str, Any]
    ) -> bool:
        """
        添加文档到向量库
        
        Args:
            doc_id: 文档ID
            content: 文档内容
            embedding: 向量
            metadata: 元数据
            
        Returns:
            是否成功
        """
        self._ensure_initialized()
        
        try:
            doc_id = self.validator.validate_id(doc_id)
            content = self.validator.validate_content(content)
            embedding = self.validator.validate_embedding(
                embedding, 
                self.config.documents_vector_size
            )
            metadata = self.validator.validate_metadata(metadata)
        except (ValidationError, VectorDimensionError) as e:
            logger.error(f"文档验证失败: {e}")
            return False
        
        try:
            async with self._semaphore:
                point = PointStruct(
                    id=doc_id,
                    vector=embedding,
                    payload={
                        "content": content,
                        **metadata
                    }
                )
                
                self._client.upsert(
                    collection_name=self.config.documents_collection,
                    points=[point]
                )
                
                logger.debug(f"添加文档成功: {doc_id}")
                return True
            
        except Exception as e:
            logger.error(f"添加文档失败: {e}")
            return False
    
    @retry_on_error(max_retries=3, delay=1.0)
    async def add_documents(
        self,
        doc_ids: List[str],
        contents: List[str],
        embeddings: List[List[float]],
        metadatas: List[Dict[str, Any]]
    ) -> int:
        """
        批量添加文档
        
        Args:
            doc_ids: 文档ID列表
            contents: 文档内容列表
            embeddings: 向量列表
            metadatas: 元数据列表
            
        Returns:
            成功添加的数量
        """
        self._ensure_initialized()
        
        if not all([doc_ids, contents, embeddings, metadatas]):
            logger.error("参数不能为空")
            return 0
        
        if not (len(doc_ids) == len(contents) == len(embeddings) == len(metadatas)):
            logger.error("参数长度不一致")
            return 0
        
        success_count = 0
        failed_items = []
        
        for i in range(0, len(doc_ids), self.config.batch_size):
            batch_doc_ids = doc_ids[i:i + self.config.batch_size]
            batch_contents = contents[i:i + self.config.batch_size]
            batch_embeddings = embeddings[i:i + self.config.batch_size]
            batch_metadatas = metadatas[i:i + self.config.batch_size]
            
            points = []
            for j, (doc_id, content, embedding, metadata) in enumerate(zip(
                batch_doc_ids, batch_contents, batch_embeddings, batch_metadatas
            )):
                try:
                    validated_id = self.validator.validate_id(doc_id)
                    validated_content = self.validator.validate_content(content)
                    validated_embedding = self.validator.validate_embedding(
                        embedding, 
                        self.config.documents_vector_size
                    )
                    validated_metadata = self.validator.validate_metadata(metadata)
                    
                    points.append(PointStruct(
                        id=validated_id,
                        vector=validated_embedding,
                        payload={
                            "content": validated_content,
                            **validated_metadata
                        }
                    ))
                except (ValidationError, VectorDimensionError) as e:
                    failed_items.append((i + j, str(e)))
                    logger.warning(f"文档验证失败 (索引 {i + j}): {e}")
            
            if points:
                try:
                    async with self._semaphore:
                        self._client.upsert(
                            collection_name=self.config.documents_collection,
                            points=points
                        )
                    success_count += len(points)
                    logger.debug(f"批量添加文档成功: {len(points)} 条")
                    
                except Exception as e:
                    logger.error(f"批量添加文档失败: {e}")
            
            if i + self.config.batch_size < len(doc_ids):
                await asyncio.sleep(0.1)
        
        if failed_items:
            logger.warning(f"批量添加文档有 {len(failed_items)} 条验证失败")
        
        logger.info(f"批量添加文档完成: {success_count}/{len(doc_ids)} 成功")
        return success_count
    
    @retry_on_error(max_retries=3, delay=1.0)
    async def add_image(
        self,
        image_id: str,
        image_url: str,
        embedding: List[float],
        metadata: Dict[str, Any]
    ) -> bool:
        """
        添加图片到向量库
        
        Args:
            image_id: 图片ID
            image_url: 图片URL
            embedding: 向量
            metadata: 元数据
            
        Returns:
            是否成功
        """
        self._ensure_initialized()
        
        try:
            image_id = self.validator.validate_id(image_id)
            embedding = self.validator.validate_embedding(
                embedding, 
                self.config.images_vector_size
            )
            metadata = self.validator.validate_metadata(metadata)
            
            if image_url:
                metadata['image_url'] = image_url[:InputValidator.MAX_METADATA_VALUE_LENGTH]
            
        except (ValidationError, VectorDimensionError) as e:
            logger.error(f"图片验证失败: {e}")
            return False
        
        try:
            async with self._semaphore:
                point = PointStruct(
                    id=image_id,
                    vector=embedding,
                    payload=metadata
                )
                
                self._client.upsert(
                    collection_name=self.config.images_collection,
                    points=[point]
                )
                
                logger.debug(f"添加图片成功: {image_id}")
                return True
            
        except Exception as e:
            logger.error(f"添加图片失败: {e}")
            return False
    
    @retry_on_error(max_retries=3, delay=1.0)
    async def add_images(
        self,
        image_ids: List[str],
        image_urls: List[str],
        embeddings: List[List[float]],
        metadatas: List[Dict[str, Any]]
    ) -> int:
        """
        批量添加图片
        
        Args:
            image_ids: 图片ID列表
            image_urls: 图片URL列表
            embeddings: 向量列表
            metadatas: 元数据列表
            
        Returns:
            成功添加的数量
        """
        self._ensure_initialized()
        
        if not all([image_ids, image_urls, embeddings, metadatas]):
            logger.error("参数不能为空")
            return 0
        
        if not (len(image_ids) == len(image_urls) == len(embeddings) == len(metadatas)):
            logger.error("参数长度不一致")
            return 0
        
        success_count = 0
        failed_items = []
        
        for i in range(0, len(image_ids), self.config.batch_size):
            batch_ids = image_ids[i:i + self.config.batch_size]
            batch_urls = image_urls[i:i + self.config.batch_size]
            batch_embeddings = embeddings[i:i + self.config.batch_size]
            batch_metadatas = metadatas[i:i + self.config.batch_size]
            
            points = []
            for j, (img_id, img_url, embedding, metadata) in enumerate(zip(
                batch_ids, batch_urls, batch_embeddings, batch_metadatas
            )):
                try:
                    validated_id = self.validator.validate_id(img_id)
                    validated_embedding = self.validator.validate_embedding(
                        embedding, 
                        self.config.images_vector_size
                    )
                    validated_metadata = self.validator.validate_metadata(metadata)
                    
                    if img_url:
                        validated_metadata['image_url'] = img_url[:InputValidator.MAX_METADATA_VALUE_LENGTH]
                    
                    points.append(PointStruct(
                        id=validated_id,
                        vector=validated_embedding,
                        payload=validated_metadata
                    ))
                except (ValidationError, VectorDimensionError) as e:
                    failed_items.append((i + j, str(e)))
                    logger.warning(f"图片验证失败 (索引 {i + j}): {e}")
            
            if points:
                try:
                    async with self._semaphore:
                        self._client.upsert(
                            collection_name=self.config.images_collection,
                            points=points
                        )
                    success_count += len(points)
                    logger.debug(f"批量添加图片成功: {len(points)} 条")
                    
                except Exception as e:
                    logger.error(f"批量添加图片失败: {e}")
            
            if i + self.config.batch_size < len(image_ids):
                await asyncio.sleep(0.1)
        
        if failed_items:
            logger.warning(f"批量添加图片有 {len(failed_items)} 条验证失败")
        
        logger.info(f"批量添加图片完成: {success_count}/{len(image_ids)} 成功")
        return success_count
    
    @retry_on_error(max_retries=3, delay=1.0)
    async def search_documents(
        self,
        query_embedding: List[float],
        n_results: int = 5,
        city: Optional[str] = None,
        content_type: Optional[str] = None,
        score_threshold: Optional[float] = None
    ) -> List[SearchResult]:
        """
        搜索文档
        
        Args:
            query_embedding: 查询向量
            n_results: 返回结果数量
            city: 城市过滤
            content_type: 内容类型过滤
            score_threshold: 分数阈值
            
        Returns:
            搜索结果列表
        """
        self._ensure_initialized()
        
        try:
            query_embedding = self.validator.validate_embedding(
                query_embedding, 
                self.config.documents_vector_size
            )
        except (ValidationError, VectorDimensionError) as e:
            logger.error(f"查询向量验证失败: {e}")
            return []
        
        n_results = min(max(1, n_results), 100)
        
        if score_threshold is not None:
            score_threshold = max(0.0, min(1.0, score_threshold))
        
        try:
            async with self._semaphore:
                filter_conditions = []
                
                if city:
                    city = str(city)[:100]
                    filter_conditions.append(
                        FieldCondition(key="city", match=MatchValue(value=city))
                    )
                
                if content_type:
                    content_type = str(content_type)[:50]
                    filter_conditions.append(
                        FieldCondition(key="content_type", match=MatchValue(value=content_type))
                    )
                
                query_filter = Filter(must=filter_conditions) if filter_conditions else None
                
                results = self._client.search(
                    collection_name=self.config.documents_collection,
                    query_vector=query_embedding,
                    limit=n_results,
                    query_filter=query_filter,
                    score_threshold=score_threshold
                )
                
                documents = []
                for result in results:
                    documents.append(SearchResult(
                        id=str(result.id),
                        score=result.score,
                        payload=result.payload if result.payload else {}
                    ))
                
                logger.debug(f"搜索文档成功: {len(documents)} 条结果")
                return documents
            
        except Exception as e:
            logger.error(f"搜索文档失败: {e}")
            return []
    
    @retry_on_error(max_retries=3, delay=1.0)
    async def search_images(
        self,
        query_embedding: List[float],
        n_results: int = 5,
        city: Optional[str] = None,
        score_threshold: Optional[float] = None
    ) -> List[SearchResult]:
        """
        搜索图片
        
        Args:
            query_embedding: 查询向量
            n_results: 返回结果数量
            city: 城市过滤
            score_threshold: 分数阈值
            
        Returns:
            搜索结果列表
        """
        self._ensure_initialized()
        
        try:
            query_embedding = self.validator.validate_embedding(
                query_embedding, 
                self.config.images_vector_size
            )
        except (ValidationError, VectorDimensionError) as e:
            logger.error(f"查询向量验证失败: {e}")
            return []
        
        n_results = min(max(1, n_results), 100)
        
        if score_threshold is not None:
            score_threshold = max(0.0, min(1.0, score_threshold))
        
        try:
            async with self._semaphore:
                filter_conditions = []
                
                if city:
                    city = str(city)[:100]
                    filter_conditions.append(
                        FieldCondition(key="city", match=MatchValue(value=city))
                    )
                
                query_filter = Filter(must=filter_conditions) if filter_conditions else None
                
                results = self._client.search(
                    collection_name=self.config.images_collection,
                    query_vector=query_embedding,
                    limit=n_results,
                    query_filter=query_filter,
                    score_threshold=score_threshold
                )
                
                images = []
                for result in results:
                    images.append(SearchResult(
                        id=str(result.id),
                        score=result.score,
                        payload=result.payload if result.payload else {}
                    ))
                
                logger.debug(f"搜索图片成功: {len(images)} 条结果")
                return images
            
        except Exception as e:
            logger.error(f"搜索图片失败: {e}")
            return []
    
    @retry_on_error(max_retries=3, delay=1.0)
    async def delete_document(self, doc_id: str) -> bool:
        """删除文档"""
        self._ensure_initialized()
        
        try:
            doc_id = self.validator.validate_id(doc_id)
        except ValidationError as e:
            logger.error(f"文档ID验证失败: {e}")
            return False
        
        try:
            async with self._semaphore:
                self._client.delete(
                    collection_name=self.config.documents_collection,
                    points_selector=PointIdsList(
                        points=[doc_id]
                    )
                )
            logger.debug(f"删除文档成功: {doc_id}")
            return True
        except Exception as e:
            logger.error(f"删除文档失败: {e}")
            return False
    
    @retry_on_error(max_retries=3, delay=1.0)
    async def delete_documents(self, doc_ids: List[str]) -> int:
        """批量删除文档"""
        self._ensure_initialized()
        
        if not doc_ids:
            return 0
        
        valid_ids = []
        for doc_id in doc_ids:
            try:
                valid_ids.append(self.validator.validate_id(doc_id))
            except ValidationError as e:
                logger.warning(f"文档ID验证失败: {doc_id}, 错误: {e}")
        
        if not valid_ids:
            return 0
        
        success_count = 0
        
        for i in range(0, len(valid_ids), self.config.batch_size):
            batch_ids = valid_ids[i:i + self.config.batch_size]
            
            try:
                async with self._semaphore:
                    self._client.delete(
                        collection_name=self.config.documents_collection,
                        points_selector=PointIdsList(
                            points=batch_ids
                        )
                    )
                success_count += len(batch_ids)
                logger.debug(f"批量删除文档成功: {len(batch_ids)} 条")
            except Exception as e:
                logger.error(f"批量删除文档失败: {e}")
        
        logger.info(f"批量删除文档完成: {success_count}/{len(doc_ids)} 成功")
        return success_count
    
    @retry_on_error(max_retries=3, delay=1.0)
    async def delete_image(self, image_id: str) -> bool:
        """删除图片"""
        self._ensure_initialized()
        
        try:
            image_id = self.validator.validate_id(image_id)
        except ValidationError as e:
            logger.error(f"图片ID验证失败: {e}")
            return False
        
        try:
            async with self._semaphore:
                self._client.delete(
                    collection_name=self.config.images_collection,
                    points_selector=PointIdsList(
                        points=[image_id]
                    )
                )
            logger.debug(f"删除图片成功: {image_id}")
            return True
        except Exception as e:
            logger.error(f"删除图片失败: {e}")
            return False
    
    @retry_on_error(max_retries=3, delay=1.0)
    async def delete_images(self, image_ids: List[str]) -> int:
        """批量删除图片"""
        self._ensure_initialized()
        
        if not image_ids:
            return 0
        
        valid_ids = []
        for img_id in image_ids:
            try:
                valid_ids.append(self.validator.validate_id(img_id))
            except ValidationError as e:
                logger.warning(f"图片ID验证失败: {img_id}, 错误: {e}")
        
        if not valid_ids:
            return 0
        
        success_count = 0
        
        for i in range(0, len(valid_ids), self.config.batch_size):
            batch_ids = valid_ids[i:i + self.config.batch_size]
            
            try:
                async with self._semaphore:
                    self._client.delete(
                        collection_name=self.config.images_collection,
                        points_selector=PointIdsList(
                            points=batch_ids
                        )
                    )
                success_count += len(batch_ids)
                logger.debug(f"批量删除图片成功: {len(batch_ids)} 条")
            except Exception as e:
                logger.error(f"批量删除图片失败: {e}")
        
        logger.info(f"批量删除图片完成: {success_count}/{len(image_ids)} 成功")
        return success_count
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """获取集合统计信息"""
        try:
            if not self._initialized or self._client is None:
                return {
                    "documents_count": 0,
                    "images_count": 0,
                    "status": "not_initialized"
                }
            
            doc_info = self._client.get_collection(self.config.documents_collection)
            img_info = self._client.get_collection(self.config.images_collection)
            
            return {
                "documents_count": doc_info.points_count,
                "images_count": img_info.points_count,
                "documents_status": doc_info.status.value,
                "images_status": img_info.status.value,
                "status": "healthy"
            }
        except Exception as e:
            logger.error(f"获取统计信息失败: {e}")
            return {
                "documents_count": 0,
                "images_count": 0,
                "status": "error",
                "error": str(e)
            }
    
    async def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        health_status = {
            "status": "healthy",
            "qdrant_connection": "unknown",
            "documents_collection": "unknown",
            "images_collection": "unknown",
            "errors": []
        }
        
        try:
            if not self._initialized or self._client is None:
                await self._initialize()
            
            collections = self._client.get_collections().collections
            collection_names = [c.name for c in collections]
            
            if self.config.documents_collection in collection_names:
                health_status["documents_collection"] = "ok"
            else:
                health_status["documents_collection"] = "missing"
                health_status["errors"].append("文档集合不存在")
            
            if self.config.images_collection in collection_names:
                health_status["images_collection"] = "ok"
            else:
                health_status["images_collection"] = "missing"
                health_status["errors"].append("图片集合不存在")
            
            health_status["qdrant_connection"] = "ok"
            
        except Exception as e:
            health_status["status"] = "error"
            health_status["qdrant_connection"] = "error"
            health_status["errors"].append(str(e))
        
        if health_status["errors"]:
            health_status["status"] = "degraded"
        
        return health_status


_vector_store: Optional[VectorStore] = None


async def get_vector_store(config: Optional[VectorConfig] = None) -> VectorStore:
    """获取向量数据库实例（单例模式）"""
    global _vector_store
    
    if _vector_store is None:
        _vector_store = VectorStore(config)
        await _vector_store._initialize()
    
    return _vector_store
