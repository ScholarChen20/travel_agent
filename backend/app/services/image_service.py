"""
图片处理服务

功能：
1. 从 Unsplash 下载景点图片
2. 调用 storage_service 上传图片到 OSS
3. 返回 OSS URL
"""

import httpx
import secrets
from typing import Optional
from loguru import logger
from io import BytesIO

from ..services.unsplash_service import get_unsplash_service
from ..services.storage_service import get_storage_service


class ImageService:
    """图片处理服务类"""

    def __init__(self):
        """初始化服务"""
        self.unsplash_service = get_unsplash_service()
        self.storage_service = get_storage_service()
        logger.info("图片处理服务已初始化")

    async def get_and_upload_attraction_image(
        self,
        attraction_name: str,
        city: str = ""
    ) -> Optional[str]:
        """
        获取景点图片并上传到 OSS

        Args:
            attraction_name: 景点名称
            city: 城市名称（可选，用于更精确的搜索）

        Returns:
            str: OSS 图片 URL，失败返回 None
        """
        try:
            # 1. 从 Unsplash 搜索图片
            search_query = f"{attraction_name} {city} China landmark" if city else f"{attraction_name} China"
            logger.info(f"搜索景点图片: {search_query}")

            photo_url = self.unsplash_service.get_photo_url(search_query)

            if not photo_url:
                # 如果没找到，尝试只用景点名称搜索
                logger.warning(f"未找到图片，尝试简化搜索: {attraction_name}")
                photo_url = self.unsplash_service.get_photo_url(attraction_name)

            if not photo_url:
                logger.warning(f"未找到景点图片: {attraction_name}")
                return None

            logger.info(f"找到图片 URL: {photo_url}")

            # 2. 下载图片到内存
            image_data = await self._download_image(photo_url)
            if not image_data:
                logger.error(f"下载图片失败: {photo_url}")
                return None

            # 3. 上传到 OSS（使用 storage_service）
            oss_url = await self._upload_image(
                image_data,
                attraction_name,
                city
            )

            if oss_url:
                logger.info(f"图片已上传: {oss_url}")
            else:
                logger.error(f"上传图片失败: {attraction_name}")

            return oss_url

        except Exception as e:
            logger.error(f"获取并上传景点图片失败: {attraction_name}, 错误: {str(e)}")
            return None

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
