"""缓存失效工具"""

from typing import List
from loguru import logger
from ..database.redis_client import get_redis_client


class CacheInvalidator:
    """缓存失效器"""
    
    def __init__(self):
        """初始化缓存失效器"""
        self.redis = None
        self._init_redis()
    
    def _init_redis(self):
        """初始化Redis客户端"""
        try:
            self.redis = get_redis_client()
            logger.debug("缓存失效器Redis客户端初始化成功")
        except Exception as e:
            logger.warning(f"缓存失效器Redis客户端初始化失败: {str(e)}")
            self.redis = None
    
    async def invalidate_dashboard_cache(self):
        """失效所有仪表盘缓存"""
        if not self.redis:
            return
        
        try:
            cache_keys = [
                "dashboard:user_stats",
                "dashboard:content_stats",
                "dashboard:business_stats"
            ]
            
            await self.redis.delete(*cache_keys)
            logger.info(f"仪表盘缓存已失效: {cache_keys}")
        except Exception as e:
            logger.error(f"失效仪表盘缓存失败: {str(e)}")
    
    async def invalidate_user_stats_cache(self):
        """失效用户统计缓存"""
        if not self.redis:
            return
        
        try:
            await self.redis.delete("dashboard:user_stats")
            logger.info("用户统计缓存已失效")
        except Exception as e:
            logger.error(f"失效用户统计缓存失败: {str(e)}")
    
    async def invalidate_content_stats_cache(self):
        """失效内容统计缓存"""
        if not self.redis:
            return
        
        try:
            await self.redis.delete("dashboard:content_stats")
            logger.info("内容统计缓存已失效")
        except Exception as e:
            logger.error(f"失效内容统计缓存失败: {str(e)}")
    
    async def invalidate_business_stats_cache(self):
        """失效业务指标缓存"""
        if not self.redis:
            return

        try:
            await self.redis.delete("dashboard:business_stats")
            logger.info("业务指标缓存已失效")
        except Exception as e:
            logger.error(f"失效业务指标缓存失败: {str(e)}")

    async def invalidate_admin_visualization(self):
        """失效管理后台可视化缓存"""
        if not self.redis:
            return
        try:
            await self.redis.delete("admin:visualization")
            logger.info("管理后台可视化缓存已失效")
        except Exception as e:
            logger.error(f"失效管理后台可视化缓存失败: {str(e)}")

    async def invalidate_admin_system_stats(self):
        """失效管理后台系统统计缓存"""
        if not self.redis:
            return
        try:
            await self.redis.delete("admin:system_stats")
            logger.info("管理后台系统统计缓存已失效")
        except Exception as e:
            logger.error(f"失效管理后台系统统计缓存失败: {str(e)}")

    async def invalidate_admin_user_trends(self):
        """失效管理后台用户趋势缓存（所有变体）"""
        if not self.redis:
            return
        try:
            keys = []
            async for key in self.redis.scan_iter("admin:user_trend:*"):
                keys.append(key)
            if keys:
                await self.redis.delete(*keys)
                logger.info(f"管理后台用户趋势缓存已失效: {len(keys)} 个 key")
        except Exception as e:
            logger.error(f"失效管理后台用户趋势缓存失败: {str(e)}")

    async def invalidate_admin_all_stats(self):
        """失效所有管理后台统计缓存"""
        await self.invalidate_admin_visualization()
        await self.invalidate_admin_system_stats()
        await self.invalidate_admin_user_trends()


# 全局实例（单例）
_cache_invalidator: CacheInvalidator = None


def get_cache_invalidator() -> CacheInvalidator:
    """获取全局缓存失效器实例（单例）"""
    global _cache_invalidator
    if _cache_invalidator is None:
        _cache_invalidator = CacheInvalidator()
    return _cache_invalidator