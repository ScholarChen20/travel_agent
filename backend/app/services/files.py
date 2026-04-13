"""文件上传接口"""
import os
import uuid
from datetime import datetime
from io import BytesIO

from fastapi import APIRouter, Depends, UploadFile, File
from loguru import logger

from app.config import settings

router = APIRouter(prefix="/files", tags=["文件管理"])

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "img")

ALLOWED_EXTENSIONS = {
    ".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp", ".svg",
    ".mp4", ".avi", ".mov", ".wmv",
    ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx", ".csv", ".txt",
}

MAX_FILE_SIZE = 20 * 1024 * 1024


def get_minio_client():
    from minio import Minio
    endpoint = settings.minio_endpoint.replace("http://", "").replace("https://", "")
    secure = settings.minio_endpoint.startswith("https://")
    return Minio(
        endpoint,
        access_key=settings.minio_access_key,
        secret_key=settings.minio_secret_key,
        secure=secure,
    )


def ensure_bucket_exists(client, bucket_name: str) -> bool:
    try:
        if not client.bucket_exists(bucket_name):
            client.make_bucket(bucket_name)
            logger.info(f"MinIO bucket '{bucket_name}' created")
        return True
    except Exception as e:
        logger.error(f"Failed to ensure bucket exists: {e}")
        return False


async def upload_to_minio(content: bytes, filename: str, content_type: str) -> str | None:
    try:
        from datetime import timedelta

        client = get_minio_client()
        if not ensure_bucket_exists(client, settings.minio_bucket_name):
            return None

        date_dir = datetime.now().strftime("%Y%m%d")
        ext = os.path.splitext(filename)[1].lower()
        object_name = f"{date_dir}/{uuid.uuid4().hex}{ext}"

        client.put_object(
            settings.minio_bucket_name,
            object_name,
            BytesIO(content),
            len(content),
            content_type=content_type or "application/octet-stream",
        )

        # 设置 bucket 公开读策略，这样前端可以直接通过 URL 访问
        _set_bucket_public_read(client, settings.minio_bucket_name)

        file_url = f"{settings.minio_endpoint}/{settings.minio_bucket_name}/{object_name}"
        logger.info(f"File uploaded to MinIO: {object_name}")
        return file_url
    except Exception as e:
        logger.error(f"MinIO upload failed: {e}")
        return None


# 记录已设置过公开读的 bucket，避免重复设置
_public_buckets: set = set()


def _set_bucket_public_read(client, bucket_name: str):
    """设置 bucket 为公开读（只执行一次）"""
    import json as _json

    if bucket_name in _public_buckets:
        return
    try:
        policy = _json.dumps({
            "Version": "2012-10-17",
            "Statement": [{
                "Effect": "Allow",
                "Principal": {"AWS": ["*"]},
                "Action": ["s3:GetObject"],
                "Resource": [f"arn:aws:s3:::{bucket_name}/*"],
            }],
        })
        client.set_bucket_policy(bucket_name, policy)
        _public_buckets.add(bucket_name)
        logger.info(f"MinIO bucket '{bucket_name}' set to public read")
    except Exception as e:
        logger.warning(f"Failed to set bucket public read policy: {e}")