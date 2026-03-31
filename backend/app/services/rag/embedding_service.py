"""
向量化服务
功能：
1. 文本向量化 (ModelScope Qwen3-Embedding)
2. 图片向量化 (通义多模态嵌入)
3. 批量处理支持
4. 错误处理和重试机制
5. 速率限制支持
6. 安全性验证
"""

from typing import List, Optional, Dict, Any
import asyncio
import time
import re
import hashlib
from urllib.parse import urlparse
from loguru import logger
from dataclasses import dataclass
from enum import Enum
from functools import wraps
import dashscope

from app.config import get_settings


class EmbeddingError(Exception):
    """向量化错误基类"""
    pass


class TextEmbeddingError(EmbeddingError):
    """文本向量化错误"""
    pass


class ImageEmbeddingError(EmbeddingError):
    """图片向量化错误"""
    pass


class RateLimitError(EmbeddingError):
    """速率限制错误"""
    pass


class SecurityError(EmbeddingError):
    """安全性错误"""
    pass


class ValidationError(EmbeddingError):
    """验证错误"""
    pass


class EmbeddingModel(Enum):
    """向量化模型枚举"""
    TEXT_EMBEDDING = "text_embedding"
    IMAGE_EMBEDDING = "image_embedding"
    TEXT_FOR_IMAGE_SEARCH = "text_for_image_search"


@dataclass
class EmbeddingResult:
    """向量化结果"""
    success: bool
    embedding: Optional[List[float]] = None
    error: Optional[str] = None
    model: Optional[str] = None
    dimension: Optional[int] = None
    processing_time_ms: Optional[float] = None


@dataclass
class EmbeddingConfig:
    """向量化配置"""
    text_model: str = "Qwen/Qwen3-Embedding-8B"
    image_model: str = "tongyi-embedding-vision-plus"
    text_embedding_dim: int = 4096
    image_embedding_dim: int = 1152
    max_retries: int = 3
    retry_delay: float = 1.0
    timeout: float = 30.0
    batch_size: int = 10
    rate_limit_delay: float = 0.1
    max_text_length: int = 8000
    max_concurrent_requests: int = 5


ALLOWED_IMAGE_DOMAINS = [
    'xhscdn.com',
    'sns-webpic-qc.xhscdn.com',
    'sns-avatar-qc.xhscdn.com',
    'aliyuncs.com',
    'oss-cn-beijing.aliyuncs.com',
    'qdrant.io',
]

DANGEROUS_PATTERNS = [
    r'javascript:',
    r'data:',
    r'vbscript:',
    r'file:',
    r'ftp:',
]


def retry_on_error(max_retries: int = 3, delay: float = 1.0):
    """重试装饰器"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_error = None
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except RateLimitError as e:
                    last_error = e
                    wait_time = delay * (2 ** attempt) * 2
                    logger.warning(
                        f"{func.__name__} 触发速率限制，{wait_time}秒后重试 ({attempt + 1}/{max_retries}): {e}"
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
    
    @staticmethod
    def validate_text(text: str, max_length: int = 8000) -> str:
        """
        验证并清理文本输入
        
        Args:
            text: 输入文本
            max_length: 最大长度
            
        Returns:
            清理后的文本
            
        Raises:
            ValidationError: 验证失败
        """
        if not isinstance(text, str):
            raise ValidationError(f"文本类型错误: 期望str，实际{type(text)}")
        
        if not text.strip():
            raise ValidationError("文本为空")
        
        cleaned = text.strip()
        
        if len(cleaned) > max_length:
            cleaned = cleaned[:max_length]
            logger.debug(f"文本已截断至{max_length}字符")
        
        return cleaned
    
    @staticmethod
    def validate_image_url(url: str) -> str:
        """
        验证图片URL安全性
        
        Args:
            url: 图片URL
            
        Returns:
            验证后的URL
            
        Raises:
            SecurityError: 安全性错误
            ValidationError: 验证错误
        """
        if not isinstance(url, str):
            raise ValidationError(f"URL类型错误: 期望str，实际{type(url)}")
        
        url = url.strip()
        
        if not url:
            raise ValidationError("URL为空")
        
        for pattern in DANGEROUS_PATTERNS:
            if re.match(pattern, url, re.IGNORECASE):
                raise SecurityError(f"检测到危险协议: {pattern}")
        
        try:
            parsed = urlparse(url)
            
            if parsed.scheme not in ['http', 'https']:
                raise SecurityError(f"不支持的协议: {parsed.scheme}")
            
            hostname = parsed.hostname
            if not hostname:
                raise ValidationError("URL缺少主机名")
            
            if hostname in ['localhost', '127.0.0.1', '0.0.0.0', '::1']:
                raise SecurityError("禁止访问本地地址")
            
            if re.match(r'^(10\.|172\.(1[6-9]|2[0-9]|3[01])\.|192\.168\.)', hostname):
                raise SecurityError("禁止访问私有网络地址")
            
        except Exception as e:
            if isinstance(e, (SecurityError, ValidationError)):
                raise
            raise ValidationError(f"URL解析失败: {e}")
        
        return url


class EmbeddingService:
    """向量化服务类"""
    
    _instance: Optional['EmbeddingService'] = None
    _lock = asyncio.Lock()
    _semaphore: Optional[asyncio.Semaphore] = None
    
    def __init__(self, config: Optional[EmbeddingConfig] = None):
        """
        初始化向量化服务
        
        Args:
            config: 向量化配置
        """
        self.config = config or EmbeddingConfig()
        self.settings = get_settings()
        self.validator = InputValidator()
        
        self._text_client = None
        self._image_initialized = False
        
        self._init_text_client()
        self._init_image_client()
        
        self._semaphore = asyncio.Semaphore(self.config.max_concurrent_requests)
        
        logger.info(
            f"向量化服务已初始化 - "
            f"文本模型: {self.config.text_model}, "
            f"图片模型: {self.config.image_model}, "
            f"最大并发: {self.config.max_concurrent_requests}"
        )
    
    @classmethod
    async def get_instance(cls, config: Optional[EmbeddingConfig] = None) -> 'EmbeddingService':
        """获取单例实例"""
        async with cls._lock:
            if cls._instance is None:
                cls._instance = cls(config)
            return cls._instance
    
    def _init_text_client(self):
        """初始化文本向量化客户端"""
        try:
            from openai import OpenAI
            
            api_key = self.settings.modelscope_api_key
            if not api_key:
                raise TextEmbeddingError("MODELSCOPE_API_KEY未配置")
            
            self._text_client = OpenAI(
                base_url='https://api-inference.modelscope.cn/v1',
                api_key=api_key,
                timeout=self.config.timeout
            )
            self._text_model = self.config.text_model
            
        except ImportError as e:
            logger.error(f"导入OpenAI客户端失败: {e}")
            raise TextEmbeddingError(f"依赖库未安装: {e}")
        except Exception as e:
            logger.error(f"初始化文本向量化客户端失败: {e}")
            raise TextEmbeddingError(f"客户端初始化失败: {e}")
    
    def _init_image_client(self):
        """初始化图片向量化客户端"""
        try:
            api_key = self.settings.dashscope_api_key
            if not api_key:
                logger.warning("DASHSCOPE_API_KEY未配置，图片向量化功能将不可用")
                self._image_initialized = False
                return
            
            dashscope.api_key = api_key
            self._image_model = self.config.image_model
            self._image_initialized = True
            
        except Exception as e:
            logger.error(f"初始化图片向量化客户端失败: {e}")
            self._image_initialized = False
    
    @retry_on_error(max_retries=3, delay=1.0)
    async def embed_text(self, text: str) -> EmbeddingResult:
        """
        文本向量化
        
        Args:
            text: 输入文本
            
        Returns:
            EmbeddingResult对象
        """
        start_time = time.time()
        
        try:
            validated_text = self.validator.validate_text(
                text, 
                max_length=self.config.max_text_length
            )
        except (ValidationError, SecurityError) as e:
            logger.warning(f"文本验证失败: {e}")
            return EmbeddingResult(
                success=False,
                error=str(e)
            )
        
        try:
            async with self._semaphore:
                await asyncio.sleep(self.config.rate_limit_delay)
                
                response = self._text_client.embeddings.create(
                    model=self._text_model,
                    input=validated_text,
                    encoding_format="float"
                )
                
                if response and response.data:
                    embedding = response.data[0].embedding
                    processing_time = (time.time() - start_time) * 1000
                    
                    logger.debug(f"文本向量化成功，维度: {len(embedding)}, 耗时: {processing_time:.2f}ms")
                    
                    return EmbeddingResult(
                        success=True,
                        embedding=embedding,
                        model=self._text_model,
                        dimension=len(embedding),
                        processing_time_ms=processing_time
                    )
                else:
                    raise TextEmbeddingError("API响应为空")
                    
        except Exception as e:
            processing_time = (time.time() - start_time) * 1000
            error_msg = f"文本向量化失败: {str(e)}"
            logger.error(error_msg)
            
            return EmbeddingResult(
                success=False,
                error=error_msg,
                model=self._text_model,
                processing_time_ms=processing_time
            )
    
    async def embed_texts(self, texts: List[str]) -> List[EmbeddingResult]:
        """
        批量文本向量化
        
        Args:
            texts: 文本列表
            
        Returns:
            向量结果列表
        """
        if not texts:
            return []
        
        if not isinstance(texts, list):
            logger.error("texts参数必须是列表")
            return [EmbeddingResult(success=False, error="参数类型错误")]
        
        results = []
        
        for i in range(0, len(texts), self.config.batch_size):
            batch = texts[i:i + self.config.batch_size]
            
            batch_results = await asyncio.gather(
                *[self.embed_text(text) for text in batch],
                return_exceptions=True
            )
            
            for result in batch_results:
                if isinstance(result, Exception):
                    results.append(EmbeddingResult(
                        success=False,
                        error=str(result)
                    ))
                else:
                    results.append(result)
            
            if i + self.config.batch_size < len(texts):
                await asyncio.sleep(0.5)
        
        success_count = sum(1 for r in results if r.success)
        logger.info(f"批量文本向量化完成: {success_count}/{len(texts)} 成功")
        
        return results
    
    @retry_on_error(max_retries=3, delay=1.0)
    async def embed_image(self, image_url: str) -> EmbeddingResult:
        """
        图片向量化
        
        Args:
            image_url: 图片URL
            
        Returns:
            EmbeddingResult对象
        """
        start_time = time.time()
        
        try:
            validated_url = self.validator.validate_image_url(image_url)
        except (ValidationError, SecurityError) as e:
            logger.warning(f"图片URL验证失败: {e}")
            return EmbeddingResult(
                success=False,
                error=str(e)
            )
        
        if not self._image_initialized:
            return EmbeddingResult(
                success=False,
                error="图片向量化客户端未初始化，请配置DASHSCOPE_API_KEY"
            )
        
        try:
            async with self._semaphore:
                await asyncio.sleep(self.config.rate_limit_delay)
                
                input_data = [{'image': validated_url}]
                
                resp = dashscope.MultiModalEmbedding.call(
                    model=self._image_model,
                    input=input_data
                )
                
                if resp.status_code == 200:
                    embedding = resp.output['embeddings'][0]['embedding']
                    processing_time = (time.time() - start_time) * 1000
                    
                    logger.debug(f"图片向量化成功，维度: {len(embedding)}, 耗时: {processing_time:.2f}ms")
                    
                    return EmbeddingResult(
                        success=True,
                        embedding=embedding,
                        model=self._image_model,
                        dimension=len(embedding),
                        processing_time_ms=processing_time
                    )
                else:
                    error_msg = f"API返回错误: {resp.code} - {resp.message}"
                    logger.error(error_msg)
                    return EmbeddingResult(
                        success=False,
                        error=error_msg,
                        model=self._image_model,
                        processing_time_ms=(time.time() - start_time) * 1000
                    )
                
        except Exception as e:
            processing_time = (time.time() - start_time) * 1000
            error_msg = f"图片向量化失败: {str(e)}"
            logger.error(error_msg)
            
            return EmbeddingResult(
                success=False,
                error=error_msg,
                model=self._image_model,
                processing_time_ms=processing_time
            )
    
    async def embed_images(self, image_urls: List[str]) -> List[EmbeddingResult]:
        """
        批量图片向量化
        
        Args:
            image_urls: 图片URL列表
            
        Returns:
            向量结果列表
        """
        if not image_urls:
            return []
        
        if not isinstance(image_urls, list):
            logger.error("image_urls参数必须是列表")
            return [EmbeddingResult(success=False, error="参数类型错误")]
        
        results = []
        
        for i in range(0, len(image_urls), self.config.batch_size):
            batch = image_urls[i:i + self.config.batch_size]
            
            batch_results = await asyncio.gather(
                *[self.embed_image(url) for url in batch],
                return_exceptions=True
            )
            
            for result in batch_results:
                if isinstance(result, Exception):
                    results.append(EmbeddingResult(
                        success=False,
                        error=str(result)
                    ))
                else:
                    results.append(result)
            
            if i + self.config.batch_size < len(image_urls):
                await asyncio.sleep(0.5)
        
        success_count = sum(1 for r in results if r.success)
        logger.info(f"批量图片向量化完成: {success_count}/{len(image_urls)} 成功")
        
        return results
    
    @retry_on_error(max_retries=3, delay=1.0)
    async def embed_text_for_image_search(self, text: str) -> EmbeddingResult:
        """
        为图片搜索生成文本向量 (使用通义多模态嵌入)
        
        Args:
            text: 搜索文本
            
        Returns:
            EmbeddingResult对象
        """
        start_time = time.time()
        
        try:
            validated_text = self.validator.validate_text(text, max_length=500)
        except (ValidationError, SecurityError) as e:
            logger.warning(f"文本验证失败: {e}")
            return EmbeddingResult(
                success=False,
                error=str(e)
            )
        
        if not self._image_initialized:
            return EmbeddingResult(
                success=False,
                error="图片向量化客户端未初始化，请配置DASHSCOPE_API_KEY"
            )
        
        try:
            async with self._semaphore:
                await asyncio.sleep(self.config.rate_limit_delay)
                
                input_data = [{'text': validated_text}]
                
                resp = dashscope.MultiModalEmbedding.call(
                    model=self._image_model,
                    input=input_data
                )
                
                if resp.status_code == 200:
                    embedding = resp.output['embeddings'][0]['embedding']
                    processing_time = (time.time() - start_time) * 1000
                    
                    logger.debug(f"文本向量化(图片搜索)成功，维度: {len(embedding)}, 耗时: {processing_time:.2f}ms")
                    
                    return EmbeddingResult(
                        success=True,
                        embedding=embedding,
                        model=self._image_model,
                        dimension=len(embedding),
                        processing_time_ms=processing_time
                    )
                else:
                    error_msg = f"API返回错误: {resp.code} - {resp.message}"
                    logger.error(error_msg)
                    return EmbeddingResult(
                        success=False,
                        error=error_msg,
                        model=self._image_model,
                        processing_time_ms=(time.time() - start_time) * 1000
                    )
                
        except Exception as e:
            processing_time = (time.time() - start_time) * 1000
            error_msg = f"文本向量化(图片搜索)失败: {str(e)}"
            logger.error(error_msg)
            
            return EmbeddingResult(
                success=False,
                error=error_msg,
                model=self._image_model,
                processing_time_ms=processing_time
            )
    
    async def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        health_status = {
            "status": "healthy",
            "text_embedding": "unknown",
            "image_embedding": "unknown",
            "errors": []
        }
        
        try:
            test_text = "健康检查测试"
            text_result = await self.embed_text(test_text)
            
            if text_result.success:
                health_status["text_embedding"] = "ok"
            else:
                health_status["text_embedding"] = "error"
                if text_result.error:
                    health_status["errors"].append(text_result.error)
                health_status["status"] = "degraded"
        except Exception as e:
            health_status["text_embedding"] = "error"
            health_status["errors"].append(str(e))
            health_status["status"] = "degraded"
        
        if self._image_initialized:
            try:
                test_image = "https://sns-webpic-qc.xhscdn.com/test.jpg"
                image_result = await self.embed_image(test_image)
                
                if image_result.success:
                    health_status["image_embedding"] = "ok"
                else:
                    health_status["image_embedding"] = "error"
                    if image_result.error:
                        health_status["errors"].append(image_result.error)
            except Exception as e:
                health_status["image_embedding"] = "error"
                health_status["errors"].append(str(e))
        else:
            health_status["image_embedding"] = "not_configured"
        
        if len(health_status["errors"]) > 0:
            health_status["status"] = "degraded"
        
        return health_status


_embedding_service: Optional[EmbeddingService] = None


def get_embedding_service(config: Optional[EmbeddingConfig] = None) -> EmbeddingService:
    """获取向量化服务实例（单例模式）"""
    global _embedding_service
    
    if _embedding_service is None:
        _embedding_service = EmbeddingService(config)
    
    return _embedding_service
