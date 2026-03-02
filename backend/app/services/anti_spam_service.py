"""
防刷服务模块

针对注册接口的防刷攻击，提供：
1. IP 国家限制（仅允许特定国家注册）
2. IP 注册频率限制（每小时最多注册次数）
3. 设备注册冷却（防止同设备短时间内重复注册）
"""

from typing import Optional, Tuple

import httpx
from loguru import logger

from ..config import get_settings
from ..database.redis_client import get_redis_client


class AntiSpamService:
    """防刷服务"""

    def __init__(self):
        self.settings = get_settings()
        self.redis = get_redis_client()

    async def _get_ip_country(self, ip: str) -> Optional[str]:
        """
        查询 IP 所属国家代码，结果写入 Redis 缓存。

        Returns:
            ISO 3166-1 alpha-2 国家代码（如 "CN"），查询失败时返回 None。
        """
        cache_key = f"geoip:{ip}"
        cached = await self.redis.get(cache_key)
        if cached:
            return str(cached)

        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get(
                    f"http://ip-api.com/json/{ip}?fields=status,countryCode"
                )
                data = resp.json()
                if data.get("status") == "success":
                    country = data.get("countryCode", "")
                    await self.redis.set(
                        cache_key, country, ex=self.settings.geoip_cache_ttl
                    )
                    return country
        except Exception as e:
            logger.warning(f"GeoIP 查询失败 (IP={ip}): {e}")

        return None

    async def check_register_allowed(
        self, device_id: str, ip: str
    ) -> Tuple[bool, str, Optional[int]]:
        """
        检查当前设备/IP 是否允许注册。

        Returns:
            (allowed, error_code, retry_after_seconds)
            - allowed: True 表示允许
            - error_code: 拒绝原因代码（SPAM_IP_COUNTRY / SPAM_IP_RATE_LIMIT / SPAM_DEVICE_REGISTERED）
            - retry_after_seconds: 客户端应等待的秒数，无限制时为 None
        """
        # 1. IP 国家检查
        allowed_countries = self.settings.get_allowed_countries()
        if allowed_countries:
            country = await self._get_ip_country(ip)
            if country and country not in allowed_countries:
                logger.warning(f"注册被拒绝（国家限制）: IP={ip}, 国家={country}")
                return False, "SPAM_IP_COUNTRY", None

        # 2. IP 每小时注册次数检查
        ip_key = f"antispam:ip_register:{ip}"
        ip_count = await self.redis.get(ip_key)
        if ip_count and int(ip_count) >= self.settings.ip_register_hourly_limit:
            ttl = await self.redis.ttl(ip_key)
            logger.warning(
                f"注册被拒绝（IP 频率超限）: IP={ip}, 次数={ip_count}, 剩余={ttl}s"
            )
            return False, "SPAM_IP_RATE_LIMIT", max(ttl, 0)

        # 3. 设备冷却检查
        device_key = f"antispam:device:{device_id}"
        if await self.redis.exists(device_key):
            ttl = await self.redis.ttl(device_key)
            logger.warning(
                f"注册被拒绝（设备冷却中）: device={device_id}, 剩余={ttl}s"
            )
            return False, "SPAM_DEVICE_REGISTERED", max(ttl, 0)

        return True, "", None

    async def mark_device_registered(self, device_id: str) -> None:
        """
        标记设备已完成注册，设置冷却期。
        """
        device_key = f"antispam:device:{device_id}"
        await self.redis.set(
            device_key, "1", ex=self.settings.device_register_cooldown
        )
        logger.debug(
            f"设备注册冷却已设置: device={device_id}, "
            f"冷却={self.settings.device_register_cooldown}s"
        )

    async def increment_ip_counter(self, ip: str) -> None:
        """
        注册成功后递增 IP 计数器（1 小时滑动窗口）。
        """
        ip_key = f"antispam:ip_register:{ip}"
        count = await self.redis.incr(ip_key)
        if count == 1:
            # 首次写入时设置 1 小时过期
            await self.redis.expire(ip_key, 3600)
        logger.debug(f"IP 注册计数更新: IP={ip}, 当前次数={count}")


# ========== 全局单例 ==========

_anti_spam_service: Optional[AntiSpamService] = None


def get_anti_spam_service() -> AntiSpamService:
    """
    获取全局防刷服务实例（单例）。
    """
    global _anti_spam_service
    if _anti_spam_service is None:
        _anti_spam_service = AntiSpamService()
    return _anti_spam_service
