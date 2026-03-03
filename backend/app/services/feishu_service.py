"""
飞书 OAuth2 服务模块

封装与飞书开放平台 API 的所有交互：
1. get_app_access_token  - 获取应用级 token（Redis 缓存）
2. exchange_code_for_token - 用授权码换取用户 token
3. get_feishu_user_info    - 获取飞书用户身份信息
"""

from typing import Optional

import httpx
from fastapi import HTTPException, status
from loguru import logger

from ..config import get_settings
from ..database.redis_client import get_redis_client

# 飞书 API 基础地址
_FEISHU_BASE = "https://open.feishu.cn/open-apis"


class FeishuService:
    """飞书 OAuth2 服务"""

    def __init__(self):
        self.settings = get_settings()
        self.redis = get_redis_client()

    # ------------------------------------------------------------------
    # 1. 获取 app_access_token（应用级，带 Redis 缓存）
    # ------------------------------------------------------------------

    async def get_app_access_token(self) -> str:
        """
        获取飞书应用级 access token。
        结果缓存到 Redis，TTL = 5400s（1.5小时），飞书官方有效期 2 小时。

        Returns:
            app_access_token 字符串

        Raises:
            HTTPException 503: 飞书服务不可用
        """
        cache_key = "feishu:app_access_token"
        cached = await self.redis.get(cache_key)
        if cached:
            logger.debug("飞书 app_access_token 命中缓存")
            return str(cached)

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.post(
                    f"{_FEISHU_BASE}/auth/v3/app_access_token/internal",
                    json={
                        "app_id": self.settings.feishu_app_id,
                        "app_secret": self.settings.feishu_app_secret,
                    },
                )
                resp.raise_for_status()
                data = resp.json()
        except httpx.HTTPError as e:
            logger.error(f"获取飞书 app_access_token 网络异常: {e}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="飞书服务暂时不可用，请稍后重试",
            )

        if data.get("code") != 0:
            logger.error(f"飞书 app_access_token 接口错误: {data}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="飞书服务暂时不可用，请稍后重试",
            )

        token = data["app_access_token"]
        await self.redis.set(cache_key, token, ex=5400)
        logger.debug("飞书 app_access_token 已刷新并缓存")
        return token

    # ------------------------------------------------------------------
    # 2. 用授权码换取用户 access token
    # ------------------------------------------------------------------

    async def exchange_code_for_token(self, code: str) -> dict:
        """
        用飞书授权码换取 user_access_token 及用户基础信息。

        Args:
            code: 飞书回调的一次性授权码（5分钟有效）

        Returns:
            飞书接口 data 字段，包含 access_token / open_id / name / email 等

        Raises:
            HTTPException 400: 授权码无效或已过期
            HTTPException 503: 飞书服务不可用
        """
        app_token = await self.get_app_access_token()

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.post(
                    f"{_FEISHU_BASE}/authen/v1/oidc/access_token",
                    headers={"Authorization": f"Bearer {app_token}"},
                    json={"grant_type": "authorization_code", "code": code},
                )
                resp.raise_for_status()
                data = resp.json()
        except httpx.HTTPError as e:
            logger.error(f"飞书换取 user_access_token 网络异常: {e}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="飞书服务暂时不可用，请稍后重试",
            )

        if data.get("code") != 0:
            logger.warning(f"飞书授权码无效: code={data.get('code')}, msg={data.get('msg')}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="飞书授权码无效或已过期，请重新授权",
            )

        logger.info(f"飞书 code 换 token 成功: open_id={data['data'].get('open_id')}")
        return data["data"]

    # ------------------------------------------------------------------
    # 3. 获取飞书用户身份信息
    # ------------------------------------------------------------------

    async def get_feishu_user_info(self, user_access_token: str) -> dict:
        """
        使用 user_access_token 获取飞书用户详细信息。

        Args:
            user_access_token: 上一步换取的用户级 token

        Returns:
            包含 open_id / union_id / name / avatar_url / email 等字段的字典

        Raises:
            HTTPException 503: 飞书服务不可用
        """
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(
                    f"{_FEISHU_BASE}/authen/v1/user_info",
                    headers={"Authorization": f"Bearer {user_access_token}"},
                )
                resp.raise_for_status()
                data = resp.json()
        except httpx.HTTPError as e:
            logger.error(f"获取飞书用户信息网络异常: {e}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="飞书服务暂时不可用，请稍后重试",
            )

        if data.get("code") != 0:
            logger.error(f"飞书用户信息接口错误: {data}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="飞书服务暂时不可用，请稍后重试",
            )

        user_info = data.get("data", {})
        logger.info(
            f"获取飞书用户信息成功: open_id={user_info.get('open_id')}, "
            f"name={user_info.get('name')}"
        )
        return user_info


# ========== 全局单例 ==========

_feishu_service: Optional[FeishuService] = None


def get_feishu_service() -> FeishuService:
    """获取飞书服务全局单例"""
    global _feishu_service
    if _feishu_service is None:
        _feishu_service = FeishuService()
    return _feishu_service
