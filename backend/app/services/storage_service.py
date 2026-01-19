"""
文件存储服务

功能：
1. 上传头像到本地存储
2. 上传媒体文件（图片、视频）
3. 获取文件访问URL
4. 生成缩略图

支持：
- 本地文件存储
- 可扩展为OSS（阿里云、AWS S3等）
"""

import os
import secrets
from pathlib import Path
from typing import Optional
from datetime import datetime
from fastapi import UploadFile
from PIL import Image
import io
from loguru import logger

from ..config import get_settings


class StorageService:
    """文件存储服务类"""

    def __init__(self):
        """初始化服务"""
        self.settings = get_settings()

        # 设置存储根目录（可从配置读取）
        self.base_dir = Path("storage")
        self.avatar_dir = self.base_dir / "avatars"
        self.media_dir = self.base_dir / "media"

        # 创建目录
        self.avatar_dir.mkdir(parents=True, exist_ok=True)
        self.media_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"存储服务已初始化: {self.base_dir.absolute()}")

    async def upload_avatar(self, file: UploadFile, user_id: int) -> str:
        """
        上传用户头像

        Args:
            file: 上传的文件
            user_id: 用户ID

        Returns:
            str: 文件访问URL
        """
        try:
            # 生成唯一文件名
            file_ext = self._get_file_extension(file.filename)
            filename = f"avatar_{user_id}_{secrets.token_urlsafe(8)}{file_ext}"

            # 保存路径
            file_path = self.avatar_dir / filename

            # 读取并处理图片
            content = await file.read()
            image = Image.open(io.BytesIO(content))

            # 调整图片大小（头像最大200x200）
            max_size = (200, 200)
            image.thumbnail(max_size, Image.Resampling.LANCZOS)

            # 转换为RGB（如果是RGBA）
            if image.mode in ("RGBA", "LA", "P"):
                background = Image.new("RGB", image.size, (255, 255, 255))
                if image.mode == "P":
                    image = image.convert("RGBA")
                background.paste(image, mask=image.split()[-1])
                image = background

            # 保存优化后的图片
            image.save(file_path, format="JPEG", quality=85, optimize=True)

            # 生成访问URL
            url = f"/storage/avatars/{filename}"

            logger.info(f"头像已保存: {filename} (用户: {user_id})")

            return url

        except Exception as e:
            logger.error(f"上传头像失败: {str(e)}")
            raise

    async def upload_media(
        self,
        file: UploadFile,
        user_id: int,
        generate_thumbnail: bool = True
    ) -> dict:
        """
        上传媒体文件（图片或视频）

        Args:
            file: 上传的文件
            user_id: 用户ID
            generate_thumbnail: 是否生成缩略图

        Returns:
            dict: {
                "url": 文件URL,
                "thumbnail_url": 缩略图URL（如果生成）,
                "filename": 文件名,
                "size": 文件大小（字节）
            }
        """
        try:
            # 生成唯一文件名
            file_ext = self._get_file_extension(file.filename)
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            filename = f"media_{user_id}_{timestamp}_{secrets.token_urlsafe(8)}{file_ext}"

            # 保存路径
            file_path = self.media_dir / filename

            # 读取文件内容
            content = await file.read()
            file_size = len(content)

            # 保存原文件
            with open(file_path, "wb") as f:
                f.write(content)

            # 生成访问URL
            url = f"/storage/media/{filename}"

            result = {
                "url": url,
                "filename": filename,
                "size": file_size
            }

            # 如果是图片且需要生成缩略图
            if generate_thumbnail and file.content_type.startswith("image/"):
                thumbnail_url = await self._generate_thumbnail(file_path, filename)
                result["thumbnail_url"] = thumbnail_url

            logger.info(f"媒体文件已保存: {filename} (用户: {user_id}, 大小: {file_size}字节)")

            return result

        except Exception as e:
            logger.error(f"上传媒体文件失败: {str(e)}")
            raise

    async def _generate_thumbnail(self, image_path: Path, original_filename: str) -> str:
        """
        生成图片缩略图

        Args:
            image_path: 原图路径
            original_filename: 原文件名

        Returns:
            str: 缩略图URL
        """
        try:
            # 缩略图文件名
            thumbnail_filename = f"thumb_{original_filename}"
            thumbnail_path = self.media_dir / thumbnail_filename

            # 打开原图
            image = Image.open(image_path)

            # 生成缩略图（最大300x300）
            max_size = (300, 300)
            image.thumbnail(max_size, Image.Resampling.LANCZOS)

            # 转换为RGB
            if image.mode in ("RGBA", "LA", "P"):
                background = Image.new("RGB", image.size, (255, 255, 255))
                if image.mode == "P":
                    image = image.convert("RGBA")
                background.paste(image, mask=image.split()[-1])
                image = background

            # 保存缩略图
            image.save(thumbnail_path, format="JPEG", quality=75, optimize=True)

            # 返回URL
            return f"/storage/media/{thumbnail_filename}"

        except Exception as e:
            logger.warning(f"生成缩略图失败: {str(e)}")
            return None

    def get_file_url(self, file_path: str) -> str:
        """
        获取文件访问URL

        Args:
            file_path: 文件相对路径

        Returns:
            str: 完整URL
        """
        # 在生产环境中，这里应该返回CDN或OSS的完整URL
        # 例如：https://cdn.example.com/storage/avatars/xxx.jpg

        base_url = self.settings.host
        if self.settings.port != 80 and self.settings.port != 443:
            base_url = f"{base_url}:{self.settings.port}"

        return f"http://{base_url}{file_path}"

    def _get_file_extension(self, filename: str) -> str:
        """
        获取文件扩展名

        Args:
            filename: 文件名

        Returns:
            str: 扩展名（包含点号）
        """
        if not filename:
            return ""

        parts = filename.rsplit(".", 1)
        if len(parts) > 1:
            return f".{parts[1].lower()}"
        return ""

    def delete_file(self, file_url: str) -> bool:
        """
        删除文件

        Args:
            file_url: 文件URL

        Returns:
            bool: 是否成功
        """
        try:
            # 从URL提取文件路径
            # 例如：/storage/avatars/xxx.jpg -> storage/avatars/xxx.jpg
            if file_url.startswith("/"):
                file_url = file_url[1:]

            file_path = Path(file_url)

            if file_path.exists():
                file_path.unlink()
                logger.info(f"文件已删除: {file_url}")
                return True
            else:
                logger.warning(f"文件不存在: {file_url}")
                return False

        except Exception as e:
            logger.error(f"删除文件失败: {str(e)}")
            return False


# ========== 全局实例（单例模式） ==========

_storage_service: Optional[StorageService] = None


def get_storage_service() -> StorageService:
    """
    获取全局存储服务实例（单例）

    Returns:
        StorageService: 存储服务实例
    """
    global _storage_service
    if _storage_service is None:
        _storage_service = StorageService()
    return _storage_service
