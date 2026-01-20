"""
文件存储服务

功能：
1. 上传头像（支持本地/OSS）
2. 上传媒体文件（图片、视频）
3. 获取文件访问URL
4. 生成缩略图

支持：
- 本地文件存储
- 阿里云OSS云存储
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

# 导入OSS SDK（如果启用）
try:
    import alibabacloud_oss_v2 as oss
    from alibabacloud_oss_v2.models import PutObjectRequest, DeleteObjectRequest
    OSS_AVAILABLE = True
except ImportError:
    OSS_AVAILABLE = False
    logger.warning("alibabacloud_oss_v2 SDK未安装，OSS功能将不可用。安装命令: pip install alibabacloud-oss-v2")


class StorageService:
    """文件存储服务类"""

    def __init__(self):
        """初始化服务"""
        self.settings = get_settings()
        self.oss_enabled = self.settings.oss_enabled
        self.oss_client = None

        # 如果启用OSS，初始化OSS客户端
        if self.oss_enabled:
            if not OSS_AVAILABLE:
                logger.error("OSS已启用但SDK未安装，将回退到本地存储")
                self.oss_enabled = False
            else:
                try:
                    # 使用静态凭证认证
                    credentials = oss.credentials.StaticCredentials(
                        access_key_id=self.settings.oss_access_key_id,
                        access_key_secret=self.settings.oss_access_key_secret
                    )
                    config = oss.config.load_default()
                    config.credentials_provider = oss.credentials.StaticCredentialsProvider(credentials)
                    # 配置OSS客户端
                    config.region = self.settings.oss_endpoint.split('.')[0].split('-')[-1]  # 从endpoint提取region
                    config.endpoint = self.settings.oss_endpoint
                    # 创建OSS客户端
                    self.oss_client = oss.Client(config)
                    logger.info(f"OSS云存储已初始化: {self.settings.oss_bucket_name}")
                except Exception as e:
                    logger.error(f"OSS初始化失败: {str(e)}，将回退到本地存储")
                    self.oss_enabled = False

        # 本地存储配置（作为备用或主存储）
        if not self.oss_enabled:
            self.base_dir = Path("storage")
            self.avatar_dir = self.base_dir / "avatars"
            self.media_dir = self.base_dir / "media"

            # 创建目录
            self.avatar_dir.mkdir(parents=True, exist_ok=True)
            self.media_dir.mkdir(parents=True, exist_ok=True)

            logger.info(f"本地存储已初始化: {self.base_dir.absolute()}")

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
            logger.info(f"开始处理头像上传: 用户ID={user_id}, 文件名={file.filename}")
            
            # 生成唯一文件名
            file_ext = self._get_file_extension(file.filename)
            filename = f"avatar_{user_id}_{secrets.token_urlsafe(8)}{file_ext}"
            logger.info(f"生成文件名: {filename}")

            # 确保文件指针在开始位置
            await file.seek(0)
            logger.info("文件指针已重置到开始位置")
            
            # 读取并处理图片
            content = await file.read()
            logger.info(f"读取文件成功，大小: {len(content)}字节")
            
            # 检查图片内容是否有效
            if not content:
                raise ValueError("图片内容为空")
                
            image = Image.open(io.BytesIO(content))
            logger.info(f"打开图片成功，格式: {image.format}, 尺寸: {image.size}, 模式: {image.mode}")

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

            # 将处理后的图片保存到字节流
            output = io.BytesIO()
            image.save(output, format="JPEG", quality=85, optimize=True)
            output.seek(0)

            # 上传到OSS或本地
            if self.oss_enabled:
                url = await self._upload_to_oss(
                    output,
                    f"{self.settings.oss_avatar_dir}/{filename}",
                    "image/jpeg"
                )
            else:
                # 本地存储
                file_path = self.avatar_dir / filename
                with open(file_path, "wb") as f:
                    f.write(output.read())
                # 生成完整的绝对URL
                base_url = f"http://localhost:{self.settings.port}"
                url = f"{base_url}/storage/avatars/{filename}"

            logger.info(f"头像已保存: {filename} (用户: {user_id}, 存储: {'OSS' if self.oss_enabled else '本地'})")

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

            # 读取文件内容
            content = await file.read()
            file_size = len(content)

            # 上传到OSS或本地
            if self.oss_enabled:
                # 上传到OSS
                object_name = f"{self.settings.oss_media_dir}/{filename}"
                url = await self._upload_to_oss(
                    io.BytesIO(content),
                    object_name,
                    file.content_type
                )
            else:
                # 本地存储
                file_path = self.media_dir / filename
                with open(file_path, "wb") as f:
                    f.write(content)
                url = f"/storage/media/{filename}"

            result = {
                "url": url,
                "filename": filename,
                "size": file_size
            }

            # 如果是图片且需要生成缩略图
            if generate_thumbnail and file.content_type and file.content_type.startswith("image/"):
                if self.oss_enabled:
                    # OSS缩略图
                    thumbnail_url = await self._generate_thumbnail_oss(
                        io.BytesIO(content),
                        filename
                    )
                else:
                    # 本地缩略图
                    thumbnail_url = await self._generate_thumbnail_local(
                        self.media_dir / filename,
                        filename
                    )
                result["thumbnail_url"] = thumbnail_url

            logger.info(f"媒体文件已保存: {filename} (用户: {user_id}, 大小: {file_size}字节, 存储: {'OSS' if self.oss_enabled else '本地'})")

            return result

        except Exception as e:
            logger.error(f"上传媒体文件失败: {str(e)}")
            raise

    async def _upload_to_oss(
        self,
        file_data: io.BytesIO,
        object_name: str,
        content_type: str
    ) -> str:
        """
        上传文件到OSS

        Args:
            file_data: 文件数据流
            object_name: OSS对象名称（包含路径）
            content_type: 文件MIME类型

        Returns:
            str: 文件访问URL
        """
        try:
            # 创建上传请求
            request = PutObjectRequest(
                bucket=self.settings.oss_bucket_name,
                key=object_name,
                body=file_data.read()
            )

            # 上传到OSS
            self.oss_client.put_object(request)

            # 生成访问URL
            if self.settings.oss_url_prefix:
                # 使用自定义域名
                url = f"{self.settings.oss_url_prefix}/{object_name}"
            else:
                # 使用默认OSS域名
                url = f"https://{self.settings.oss_bucket_name}.{self.settings.oss_endpoint}/{object_name}"

            return url

        except Exception as e:
            logger.error(f"上传到OSS失败: {str(e)}")
            raise

    async def _generate_thumbnail_local(self, image_path: Path, original_filename: str) -> Optional[str]:
        """
        生成本地图片缩略图

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
            logger.warning(f"生成本地缩略图失败: {str(e)}")
            return None

    async def _generate_thumbnail_oss(
        self,
        image_data: io.BytesIO,
        original_filename: str
    ) -> Optional[str]:
        """
        生成OSS图片缩略图

        Args:
            image_data: 原图数据流
            original_filename: 原文件名

        Returns:
            str: 缩略图URL
        """
        try:
            # 打开原图
            image = Image.open(image_data)

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

            # 保存到字节流
            output = io.BytesIO()
            image.save(output, format="JPEG", quality=75, optimize=True)
            output.seek(0)

            # 上传到OSS
            thumbnail_filename = f"thumb_{original_filename}"
            object_name = f"{self.settings.oss_media_dir}/{thumbnail_filename}"
            thumbnail_url = await self._upload_to_oss(
                output,
                object_name,
                "image/jpeg"
            )

            return thumbnail_url

        except Exception as e:
            logger.warning(f"生成OSS缩略图失败: {str(e)}")
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
        删除文件（支持OSS和本地）

        Args:
            file_url: 文件URL

        Returns:
            bool: 是否成功
        """
        try:
            if self.oss_enabled:
                # OSS删除
                # 从URL提取对象名称
                # 例如：https://bucket.oss-cn-hangzhou.aliyuncs.com/avatars/xxx.jpg -> avatars/xxx.jpg
                if self.settings.oss_url_prefix:
                    object_name = file_url.replace(f"{self.settings.oss_url_prefix}/", "")
                else:
                    # 解析默认OSS URL
                    oss_prefix = f"https://{self.settings.oss_bucket_name}.{self.settings.oss_endpoint}/"
                    object_name = file_url.replace(oss_prefix, "")

                self.oss_client.delete_object(DeleteObjectRequest(
                    bucket=self.settings.oss_bucket_name,
                    key=object_name
                ))
                logger.info(f"OSS文件已删除: {object_name}")
                return True
            else:
                # 本地删除
                # 从URL提取文件路径
                # 例如：/storage/avatars/xxx.jpg -> storage/avatars/xxx.jpg
                if file_url.startswith("/"):
                    file_url = file_url[1:]

                file_path = Path(file_url)

                if file_path.exists():
                    file_path.unlink()
                    logger.info(f"本地文件已删除: {file_url}")
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
