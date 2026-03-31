"""
图片处理服务

功能：
1. 从 Unsplash 下载景点图片
2. 调用 storage_service 上传图片到 OSS
3. RAG图片兜底方案 - 当Unsplash无法获取时从向量库检索
4. 返回 OSS URL
"""

import httpx
import secrets
from typing import Optional, List
from loguru import logger
from io import BytesIO

from ..services.unsplash_service import get_unsplash_service
from ..services.storage_service import get_storage_service
from ..services.rag import HybridRAGService, get_hybrid_rag_service


class ImageService:
    """图片处理服务类"""

    def __init__(self):
        """初始化服务"""
        self.unsplash_service = get_unsplash_service()
        self.storage_service = get_storage_service()
        self._rag_service: Optional[HybridRAGService] = None
        logger.info("图片处理服务已初始化")

    async def _get_rag_service(self) -> Optional[HybridRAGService]:
        """获取RAG服务实例（延迟初始化）"""
        if self._rag_service is None:
            try:
                self._rag_service = await get_hybrid_rag_service()
                logger.debug("RAG服务初始化成功")
            except Exception as e:
                logger.warning(f"RAG服务初始化失败: {str(e)}")
                return None
        return self._rag_service
    
    async def _get_fallback_images_from_rag(
        self,
        attraction_name: str,
        city: str = ""
    ) -> List[str]:
        """
        从RAG获取景点图片作为兜底方案
        
        Args:
            attraction_name: 景点名称
            city: 城市名称
            
        Returns:
            图片URL列表
        """
        try:
            rag_service = await self._get_rag_service()
            if rag_service is None:
                return []
            
            image_urls = await rag_service.search_attraction_images(
                attraction_name=attraction_name,
                city=city,
                n_results=3
            )
            
            if image_urls:
                logger.info(f"从RAG获取到 {len(image_urls)} 张图片: {attraction_name}")
            
            return image_urls
            
        except Exception as e:
            logger.warning(f"从RAG获取图片失败: {str(e)}")
            return []

    async def get_and_upload_attraction_image(
        self,
        attraction_name: str,
        city: str = ""
    ) -> Optional[str]:
        """
        获取景点图片并上传到 OSS
        
        流程：
        1. 优先从Unsplash获取图片
        2. 如果Unsplash失败，从RAG向量库获取图片作为兜底

        Args:
            attraction_name: 景点名称
            city: 城市名称（可选，用于更精确的搜索）

        Returns:
            str: OSS 图片 URL，失败返回 None
        """
        oss_url = None
        
        try:
            search_query = f"{attraction_name} {city} China landmark" if city else f"{attraction_name} China"
            logger.info(f"搜索景点图片: {search_query}")

            photo_url = self.unsplash_service.get_photo_url(search_query)

            if not photo_url:
                logger.warning(f"未找到图片，尝试简化搜索: {attraction_name}")
                photo_url = self.unsplash_service.get_photo_url(attraction_name)

            if photo_url:
                logger.info(f"Unsplash找到图片 URL: {photo_url}")
                
                image_data = await self._download_image(photo_url)
                if image_data:
                    oss_url = await self._upload_image(
                        image_data,
                        attraction_name,
                        city
                    )
                    
                    if oss_url:
                        logger.info(f"图片已上传: {oss_url}")
                        return oss_url
                    else:
                        logger.warning(f"上传图片失败，尝试RAG兜底: {attraction_name}")
                else:
                    logger.warning(f"下载图片失败，尝试RAG兜底: {attraction_name}")
            else:
                logger.warning(f"Unsplash未找到图片，尝试RAG兜底: {attraction_name}")

        except Exception as e:
            logger.warning(f"Unsplash获取图片失败: {str(e)}，尝试RAG兜底")

        if oss_url is None:
            try:
                logger.info(f"🔄 开始RAG图片兜底检索: {attraction_name}")
                rag_images = await self._get_fallback_images_from_rag(attraction_name, city)
                
                if rag_images:
                    first_image_url = rag_images[0]
                    logger.info(f"RAG找到图片: {first_image_url}")
                    
                    if first_image_url.startswith(('http://', 'https://')):
                        image_data = await self._download_image(first_image_url)
                        if image_data:
                            oss_url = await self._upload_image(
                                image_data,
                                attraction_name,
                                city
                            )
                            if oss_url:
                                logger.info(f"✅ RAG兜底图片上传成功: {oss_url}")
                                return oss_url
                    else:
                        logger.info(f"RAG返回图片URL可直接使用: {first_image_url}")
                        return first_image_url
                        
            except Exception as e:
                logger.error(f"RAG图片兜底失败: {str(e)}")

        if oss_url is None:
            logger.error(f"❌ 所有图片获取方式均失败: {attraction_name}")
            
        return oss_url
    
    async def get_attraction_images_with_fallback(
        self,
        attraction_name: str,
        city: str = "",
        max_images: int = 3
    ) -> List[str]:
        """
        获取景点图片列表（带RAG兜底）
        
        Args:
            attraction_name: 景点名称
            city: 城市名称
            max_images: 最大图片数量
            
        Returns:
            图片URL列表
        """
        images = []
        
        try:
            search_query = f"{attraction_name} {city} China landmark" if city else f"{attraction_name} China"
            
            unsplash_urls = self.unsplash_service.get_photo_urls(search_query, count=max_images)
            
            if unsplash_urls:
                images.extend(unsplash_urls[:max_images])
                logger.info(f"Unsplash获取到 {len(unsplash_urls)} 张图片")
                
        except Exception as e:
            logger.warning(f"Unsplash获取图片列表失败: {str(e)}")
        
        if len(images) < max_images:
            try:
                rag_images = await self._get_fallback_images_from_rag(attraction_name, city)
                
                for img_url in rag_images:
                    if img_url not in images:
                        images.append(img_url)
                        if len(images) >= max_images:
                            break
                            
                if rag_images:
                    logger.info(f"RAG补充获取到 {len(rag_images)} 张图片")
                    
            except Exception as e:
                logger.warning(f"RAG获取图片列表失败: {str(e)}")
        
        return images[:max_images]

    async def _download_image(self, url: str) -> Optional[bytes]:
        """
        下载图片到内存

        Args:
            url: 图片 URL

        Returns:
            bytes: 图片数据，失败返回 None
        """
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url)
                response.raise_for_status()
                return response.content

        except Exception as e:
            logger.error(f"下载图片失败: {url}, 错误: {str(e)}")
            return None

    async def _upload_image(
        self,
        image_data: bytes,
        attraction_name: str,
        city: str = ""
    ) -> Optional[str]:
        """
        上传图片（调用 storage_service）

        Args:
            image_data: 图片数据
            attraction_name: 景点名称
            city: 城市名称

        Returns:
            str: 图片 URL，失败返回 None
        """
        try:
            # 生成唯一文件名
            safe_name = attraction_name.replace(" ", "_").replace("/", "_")
            safe_city = city.replace(" ", "_").replace("/", "_") if city else "unknown"
            filename = f"{safe_city}_{safe_name}_{secrets.token_urlsafe(8)}.jpg"

            # 构建 OSS 对象路径
            object_name = f"attractions/{safe_city}/{filename}"

            # 使用 storage_service 上传
            if self.storage_service.oss_enabled:
                # 上传到 OSS
                logger.info(f"上传图片到 OSS: {object_name}")
                url = await self.storage_service._upload_to_oss(
                    BytesIO(image_data),
                    object_name,
                    "image/jpeg"
                )
            else:
                # 本地存储
                logger.info(f"保存图片到本地: {filename}")
                from pathlib import Path

                # 创建目录
                attractions_dir = self.storage_service.media_dir / "attractions" / safe_city
                attractions_dir.mkdir(parents=True, exist_ok=True)

                # 保存文件
                file_path = attractions_dir / filename
                with open(file_path, 'wb') as f:
                    f.write(image_data)

                # 返回访问 URL
                url = f"/storage/media/attractions/{safe_city}/{filename}"

            return url

        except Exception as e:
            logger.error(f"上传图片失败: {attraction_name}, 错误: {str(e)}")
            return None


# 全局服务实例
_image_service: Optional[ImageService] = None


def get_image_service() -> ImageService:
    """
    获取图片处理服务实例（单例模式）

    Returns:
        ImageService: 图片处理服务实例
    """
    global _image_service

    if _image_service is None:
        _image_service = ImageService()

    return _image_service
