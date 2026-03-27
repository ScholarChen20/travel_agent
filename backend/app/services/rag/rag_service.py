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
import os
from pathlib import Path

from .embedding_service import EmbeddingService, get_embedding_service, EmbeddingResult
from .vector_store import VectorStore, get_vector_store, SearchResult
from .data_processor import CleanedPost, DataProcessor


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
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'id': self.id,
            'content': self.content,
            'score': self.score,
            'metadata': self.metadata,
            'source': self.source
        }


@dataclass
class RAGConfig:
    """RAG服务配置"""
    default_n_results: int = 5
    max_n_results: int = 20
    min_score_threshold: float = 0.5
    cache_ttl: int = 3600
    enable_cache: bool = True
    batch_index_size: int = 50
    max_concurrent_indexing: int = 5


@dataclass
class IndexProgress:
    """索引进度"""
    total: int = 0
    processed: int = 0
    success: int = 0
    failed: int = 0
    current_file: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'total': self.total,
            'processed': self.processed,
            'success': self.success,
            'failed': self.failed,
            'current_file': self.current_file,
            'progress_percent': round(self.processed / self.total * 100, 2) if self.total > 0 else 0
        }


def measure_time(func):
    """性能监控装饰器"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = await func(*args, **kwargs)
            processing_time = (time.time() - start_time) * 1000
            logger.debug(f"{func.__name__} 执行时间: {processing_time:.2f}ms")
            return result
        except Exception as e:
            processing_time = (time.time() - start_time) * 1000
            logger.error(f"{func.__name__} 执行失败 ({processing_time:.2f}ms): {e}")
            raise
    return wrapper


class RAGService:
    """RAG检索服务类"""
    
    _instance: Optional['RAGService'] = None
    _lock = asyncio.Lock()
    _index_semaphore: Optional[asyncio.Semaphore] = None
    
    def __init__(
        self,
        config: Optional[RAGConfig] = None,
        embedding_service: Optional[EmbeddingService] = None,
        vector_store: Optional[VectorStore] = None,
        data_processor: Optional[DataProcessor] = None
    ):
        """
        初始化RAG服务
        
        Args:
            config: RAG配置
            embedding_service: 向量化服务
            vector_store: 向量数据库
            data_processor: 数据处理器
        """
        self.config = config or RAGConfig()
        self.embedding_service = embedding_service
        self.vector_store = vector_store
        self.data_processor = data_processor or DataProcessor()
        
        self._cache: Dict[str, Any] = {}
        self._index_semaphore = asyncio.Semaphore(self.config.max_concurrent_indexing)
        
        logger.info("RAG检索服务已初始化")
    
    @classmethod
    async def get_instance(
        cls,
        config: Optional[RAGConfig] = None
    ) -> 'RAGService':
        """获取单例实例"""
        async with cls._lock:
            if cls._instance is None:
                embedding_service = get_embedding_service()
                vector_store = await get_vector_store()
                
                cls._instance = cls(
                    config=config,
                    embedding_service=embedding_service,
                    vector_store=vector_store
                )
            return cls._instance
    
    def _generate_cache_key(self, *args, **kwargs) -> str:
        """生成缓存键"""
        key_data = f"{args}_{sorted(kwargs.items())}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def _get_from_cache(self, key: str) -> Optional[Any]:
        """从缓存获取"""
        if not self.config.enable_cache:
            return None
        
        cached = self._cache.get(key)
        if cached:
            timestamp, data = cached
            if time.time() - timestamp < self.config.cache_ttl:
                logger.debug(f"缓存命中: {key}")
                return data
            else:
                del self._cache[key]
        
        return None
    
    def _set_to_cache(self, key: str, data: Any):
        """设置缓存"""
        if self.config.enable_cache:
            self._cache[key] = (time.time(), data)
            logger.debug(f"缓存设置: {key}")
    
    def clear_cache(self):
        """清空缓存"""
        self._cache.clear()
        logger.info("RAG缓存已清空")
    
    @measure_time
    async def search_attractions(
        self,
        city: str,
        query: str = "",
        n_results: int = 5
    ) -> List[RAGSearchResult]:
        """
        搜索景点信息
        
        Args:
            city: 城市名称
            query: 搜索查询（可选）
            n_results: 返回结果数量
            
        Returns:
            景点列表
        """
        if not city:
            logger.warning("城市参数为空")
            return []
        
        city = str(city)[:50]
        query = str(query)[:200] if query else ""
        
        cache_key = self._generate_cache_key(
            "search_attractions",
            city=city,
            query=query,
            n_results=n_results
        )
        
        cached_result = self._get_from_cache(cache_key)
        if cached_result:
            return cached_result
        
        try:
            search_text = f"{city} {query} 景点 推荐" if query else f"{city} 景点 推荐"
            
            embedding_result = await self.embedding_service.embed_text(search_text)
            
            if not embedding_result.success or not embedding_result.embedding:
                logger.error(f"生成查询向量失败: {embedding_result.error}")
                return []
            
            results = await self.vector_store.search_documents(
                query_embedding=embedding_result.embedding,
                n_results=min(n_results, self.config.max_n_results),
                city=city,
                content_type="attraction",
                score_threshold=self.config.min_score_threshold
            )
            
            attractions = [
                RAGSearchResult(
                    id=result.id,
                    content=result.payload.get('content', ''),
                    score=result.score,
                    metadata=result.payload,
                    source='rag_attraction'
                )
                for result in results
            ]
            
            self._set_to_cache(cache_key, attractions)
            
            logger.info(f"搜索景点成功: 城市={city}, 结果数={len(attractions)}")
            return attractions
            
        except Exception as e:
            logger.error(f"搜索景点失败: {e}", exc_info=True)
            return []
    
    @measure_time
    async def search_food(
        self,
        city: str,
        query: str = "",
        n_results: int = 5
    ) -> List[RAGSearchResult]:
        """
        搜索美食推荐
        
        Args:
            city: 城市名称
            query: 搜索查询（可选）
            n_results: 返回结果数量
            
        Returns:
            美食列表
        """
        if not city:
            logger.warning("城市参数为空")
            return []
        
        city = str(city)[:50]
        query = str(query)[:200] if query else ""
        
        cache_key = self._generate_cache_key(
            "search_food",
            city=city,
            query=query,
            n_results=n_results
        )
        
        cached_result = self._get_from_cache(cache_key)
        if cached_result:
            return cached_result
        
        try:
            search_text = f"{city} {query} 美食 推荐" if query else f"{city} 美食 推荐"
            
            embedding_result = await self.embedding_service.embed_text(search_text)
            
            if not embedding_result.success or not embedding_result.embedding:
                logger.error(f"生成查询向量失败: {embedding_result.error}")
                return []
            
            results = await self.vector_store.search_documents(
                query_embedding=embedding_result.embedding,
                n_results=min(n_results, self.config.max_n_results),
                city=city,
                content_type="food",
                score_threshold=self.config.min_score_threshold
            )
            
            foods = [
                RAGSearchResult(
                    id=result.id,
                    content=result.payload.get('content', ''),
                    score=result.score,
                    metadata=result.payload,
                    source='rag_food'
                )
                for result in results
            ]
            
            self._set_to_cache(cache_key, foods)
            
            logger.info(f"搜索美食成功: 城市={city}, 结果数={len(foods)}")
            return foods
            
        except Exception as e:
            logger.error(f"搜索美食失败: {e}", exc_info=True)
            return []
    
    @measure_time
    async def search_hotels(
        self,
        city: str,
        query: str = "",
        n_results: int = 5
    ) -> List[RAGSearchResult]:
        """
        搜索酒店推荐
        
        Args:
            city: 城市名称
            query: 搜索查询（可选）
            n_results: 返回结果数量
            
        Returns:
            酒店列表
        """
        if not city:
            logger.warning("城市参数为空")
            return []
        
        city = str(city)[:50]
        query = str(query)[:200] if query else ""
        
        cache_key = self._generate_cache_key(
            "search_hotels",
            city=city,
            query=query,
            n_results=n_results
        )
        
        cached_result = self._get_from_cache(cache_key)
        if cached_result:
            return cached_result
        
        try:
            search_text = f"{city} {query} 酒店 住宿" if query else f"{city} 酒店 住宿"
            
            embedding_result = await self.embedding_service.embed_text(search_text)
            
            if not embedding_result.success or not embedding_result.embedding:
                logger.error(f"生成查询向量失败: {embedding_result.error}")
                return []
            
            results = await self.vector_store.search_documents(
                query_embedding=embedding_result.embedding,
                n_results=min(n_results, self.config.max_n_results),
                city=city,
                content_type="hotel",
                score_threshold=self.config.min_score_threshold
            )
            
            hotels = [
                RAGSearchResult(
                    id=result.id,
                    content=result.payload.get('content', ''),
                    score=result.score,
                    metadata=result.payload,
                    source='rag_hotel'
                )
                for result in results
            ]
            
            self._set_to_cache(cache_key, hotels)
            
            logger.info(f"搜索酒店成功: 城市={city}, 结果数={len(hotels)}")
            return hotels
            
        except Exception as e:
            logger.error(f"搜索酒店失败: {e}", exc_info=True)
            return []
    
    @measure_time
    async def search_attraction_images(
        self,
        attraction_name: str,
        city: str = "",
        n_results: int = 3
    ) -> List[str]:
        """
        搜索景点图片（兜底方案）
        
        Args:
            attraction_name: 景点名称
            city: 城市名称
            n_results: 返回结果数量
            
        Returns:
            图片URL列表
        """
        if not attraction_name:
            logger.warning("景点名称为空")
            return []
        
        attraction_name = str(attraction_name)[:100]
        city = str(city)[:50] if city else ""
        
        cache_key = self._generate_cache_key(
            "search_attraction_images",
            attraction_name=attraction_name,
            city=city,
            n_results=n_results
        )
        
        cached_result = self._get_from_cache(cache_key)
        if cached_result:
            return cached_result
        
        try:
            search_text = f"{attraction_name} {city} 景点"
            
            embedding_result = await self.embedding_service.embed_text_for_image_search(search_text)
            
            if not embedding_result.success or not embedding_result.embedding:
                logger.error(f"生成查询向量失败: {embedding_result.error}")
                return []
            
            results = await self.vector_store.search_images(
                query_embedding=embedding_result.embedding,
                n_results=min(n_results, self.config.max_n_results),
                city=city if city else None,
                score_threshold=self.config.min_score_threshold
            )
            
            image_urls = [
                result.payload.get('image_url', '')
                for result in results
                if result.payload.get('image_url')
            ]
            
            self._set_to_cache(cache_key, image_urls)
            
            logger.info(f"搜索景点图片成功: 景点={attraction_name}, 结果数={len(image_urls)}")
            return image_urls
            
        except Exception as e:
            logger.error(f"搜索景点图片失败: {e}", exc_info=True)
            return []
    
    @measure_time
    async def get_travel_context(
        self,
        city: str,
        preferences: Optional[List[str]] = None
    ) -> str:
        """
        获取旅行上下文（用于LLM增强）
        
        Args:
            city: 城市名称
            preferences: 用户偏好
            
        Returns:
            上下文文本
        """
        if not city:
            return ""
        
        city = str(city)[:50]
        
        try:
            attractions, foods, hotels = await asyncio.gather(
                self.search_attractions(city, n_results=3),
                self.search_food(city, n_results=3),
                self.search_hotels(city, n_results=3)
            )
            
            context = f"\n=== {city}旅行参考信息 ===\n\n"
            
            if attractions:
                context += "【热门景点】\n"
                for i, attr in enumerate(attractions, 1):
                    title = attr.metadata.get('title', '未知')
                    content = attr.content[:100]
                    context += f"{i}. {title}\n"
                    context += f"   {content}...\n\n"
            
            if foods:
                context += "【美食推荐】\n"
                for i, food in enumerate(foods, 1):
                    title = food.metadata.get('title', '未知')
                    content = food.content[:100]
                    context += f"{i}. {title}\n"
                    context += f"   {content}...\n\n"
            
            if hotels:
                context += "【酒店推荐】\n"
                for i, hotel in enumerate(hotels, 1):
                    title = hotel.metadata.get('title', '未知')
                    content = hotel.content[:100]
                    context += f"{i}. {title}\n"
                    context += f"   {content}...\n\n"
            
            logger.info(f"获取旅行上下文成功: 城市={city}, 长度={len(context)}")
            return context
            
        except Exception as e:
            logger.error(f"获取旅行上下文失败: {e}", exc_info=True)
            return ""
    
    async def index_cleaned_post(self, post: CleanedPost) -> bool:
        """
        索引清洗后的帖子
        
        Args:
            post: 清洗后的帖子
            
        Returns:
            是否成功
        """
        if not post or not isinstance(post, CleanedPost):
            logger.warning("帖子数据无效")
            return False
        
        async with self._index_semaphore:
            try:
                doc_content = f"{post.title}\n{post.content}"
                
                embedding_result = await self.embedding_service.embed_text(doc_content)
                
                if not embedding_result.success or not embedding_result.embedding:
                    logger.error(f"生成文档向量失败: {embedding_result.error}")
                    return False
                
                metadata = {
                    'post_id': post.post_id,
                    'title': post.title,
                    'content_type': post.content_type,
                    'city': post.city,
                    'tags': ','.join(post.tags) if post.tags else '',
                    'author': post.author,
                    'likes': post.likes,
                    'comments': post.comments,
                    'collects': post.collects,
                    'source_url': post.source_url
                }
                
                success = await self.vector_store.add_document(
                    doc_id=post.post_id,
                    content=doc_content,
                    embedding=embedding_result.embedding,
                    metadata=metadata
                )
                
                if success and post.images:
                    await self._index_post_images(post, embedding_result.embedding)
                
                logger.debug(f"索引帖子成功: {post.post_id}")
                return success
                
            except Exception as e:
                logger.error(f"索引帖子失败: {e}", exc_info=True)
                return False
    
    async def _index_post_images(
        self,
        post: CleanedPost,
        doc_embedding: List[float]
    ):
        """索引帖子的图片"""
        if not post.images:
            return
        
        for idx, image_url in enumerate(post.images[:5]):
            try:
                image_embedding_result = await self.embedding_service.embed_image(image_url)
                
                if image_embedding_result.success and image_embedding_result.embedding:
                    image_id = f"{post.post_id}_img_{idx}"
                    
                    await self.vector_store.add_image(
                        image_id=image_id,
                        image_url=image_url,
                        embedding=image_embedding_result.embedding,
                        metadata={
                            'post_id': post.post_id,
                            'city': post.city,
                            'content_type': post.content_type,
                            'tags': ','.join(post.tags) if post.tags else ''
                        }
                    )
                    
            except Exception as e:
                logger.warning(f"索引图片失败: {image_url}, 错误: {e}")
                continue
    
    async def index_posts_batch(
        self,
        posts: List[CleanedPost],
        progress_callback: Optional[callable] = None
    ) -> Dict[str, int]:
        """
        批量索引帖子
        
        Args:
            posts: 帖子列表
            progress_callback: 进度回调函数
            
        Returns:
            索引结果统计
        """
        if not posts:
            return {'total': 0, 'success': 0, 'failed': 0}
        
        progress = IndexProgress(total=len(posts))
        
        results = await asyncio.gather(
            *[self.index_cleaned_post(post) for post in posts],
            return_exceptions=True
        )
        
        for i, result in enumerate(results):
            progress.processed += 1
            if isinstance(result, Exception):
                progress.failed += 1
                logger.error(f"索引帖子失败 (索引 {i}): {result}")
            elif result:
                progress.success += 1
            else:
                progress.failed += 1
            
            if progress_callback and progress.processed % 10 == 0:
                progress_callback(progress.to_dict())
        
        if progress_callback:
            progress_callback(progress.to_dict())
        
        logger.info(f"批量索引完成: 成功={progress.success}, 失败={progress.failed}")
        
        return {
            'total': len(posts),
            'success': progress.success,
            'failed': progress.failed
        }
    
    async def index_from_json_file(
        self,
        file_path: str,
        progress_callback: Optional[callable] = None
    ) -> Dict[str, Any]:
        """
        从JSON文件索引数据
        
        Args:
            file_path: JSON文件路径
            progress_callback: 进度回调函数
            
        Returns:
            索引结果
        """
        if not os.path.exists(file_path):
            raise IndexError(f"文件不存在: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                raw_posts = json.load(f)
        except json.JSONDecodeError as e:
            raise IndexError(f"JSON解析失败: {e}")
        
        if not isinstance(raw_posts, list):
            raise IndexError("JSON文件格式错误，期望列表格式")
        
        cleaned_posts = self.data_processor.clean_posts_batch(raw_posts)
        
        if not cleaned_posts:
            logger.warning(f"没有有效的帖子数据: {file_path}")
            return {
                'file': file_path,
                'raw_count': len(raw_posts),
                'cleaned_count': 0,
                'index_result': {'total': 0, 'success': 0, 'failed': 0}
            }
        
        index_result = await self.index_posts_batch(cleaned_posts, progress_callback)
        
        return {
            'file': file_path,
            'raw_count': len(raw_posts),
            'cleaned_count': len(cleaned_posts),
            'index_result': index_result
        }
    
    async def index_from_directory(
        self,
        directory: str,
        progress_callback: Optional[callable] = None
    ) -> Dict[str, Any]:
        """
        从目录批量索引JSON文件
        
        Args:
            directory: 目录路径
            progress_callback: 进度回调函数
            
        Returns:
            索引结果汇总
        """
        if not os.path.isdir(directory):
            raise IndexError(f"目录不存在: {directory}")
        
        json_files = list(Path(directory).glob('*.json'))
        
        if not json_files:
            logger.warning(f"目录中没有JSON文件: {directory}")
            return {
                'directory': directory,
                'files_processed': 0,
                'total_posts': 0,
                'total_indexed': 0,
                'results': []
            }
        
        total_result = {
            'directory': directory,
            'files_processed': 0,
            'total_posts': 0,
            'total_indexed': 0,
            'results': []
        }
        
        for json_file in json_files:
            try:
                file_result = await self.index_from_json_file(
                    str(json_file),
                    progress_callback
                )
                
                total_result['files_processed'] += 1
                total_result['total_posts'] += file_result['raw_count']
                total_result['total_indexed'] += file_result['index_result']['success']
                total_result['results'].append(file_result)
                
                logger.info(f"文件处理完成: {json_file.name}")
                
            except Exception as e:
                logger.error(f"处理文件失败 {json_file}: {e}")
                total_result['results'].append({
                    'file': str(json_file),
                    'error': str(e)
                })
        
        logger.info(
            f"目录索引完成: 目录={directory}, "
            f"文件数={total_result['files_processed']}, "
            f"总帖子数={total_result['total_posts']}, "
            f"成功索引={total_result['total_indexed']}"
        )
        
        return total_result
    
    async def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        health_status = {
            "status": "healthy",
            "embedding_service": "unknown",
            "vector_store": "unknown",
            "cache_size": len(self._cache),
            "errors": []
        }
        
        try:
            if self.embedding_service:
                embedding_health = await self.embedding_service.health_check()
                if embedding_health.get("status") in ["healthy", "degraded"]:
                    health_status["embedding_service"] = "ok"
                else:
                    health_status["embedding_service"] = "error"
                    health_status["errors"].extend(embedding_health.get("errors", []))
            else:
                health_status["embedding_service"] = "not_initialized"
            
            if self.vector_store:
                vector_health = await self.vector_store.health_check()
                if vector_health.get("status") == "healthy":
                    health_status["vector_store"] = "ok"
                else:
                    health_status["vector_store"] = "error"
                    health_status["errors"].extend(vector_health.get("errors", []))
            else:
                health_status["vector_store"] = "not_initialized"
            
            if health_status["errors"]:
                health_status["status"] = "degraded"
            
        except Exception as e:
            health_status["status"] = "error"
            health_status["errors"].append(str(e))
        
        return health_status


_rag_service: Optional[RAGService] = None


async def get_rag_service(config: Optional[RAGConfig] = None) -> RAGService:
    """获取RAG服务实例（单例模式）"""
    global _rag_service
    
    if _rag_service is None:
        _rag_service = await RAGService.get_instance(config)
    
    return _rag_service
