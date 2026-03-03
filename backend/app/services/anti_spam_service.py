"""反垃圾邮件服务"""

from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime
from loguru import logger
from sqlalchemy import func, desc
import json
import time
import asyncio

from ..database.mysql import get_mysql_db
from ..database.models import User, UserProfile
from ..config import get_settings

settings = get_settings()


# ========== 请求模型 ==========

class AntiSpamRequest(BaseModel):
    """反垃圾邮件请求"""
    user_id: str = Field(..., description="用户ID")
    device_id: str = Field(..., description="设备ID")
    ip_address: str = Field(..., description="IP地址")
    request_type: str = Field(..., description="请求类型")


# ========== 响应模型 ==========

class AntiSpamResponse(BaseModel):
    """反垃圾邮件响应"""
    allowed: bool = Field(..., description="是否允许请求")
    reason: Optional[str] = Field(default=None, description="拒绝原因")
    score: float = Field(..., description="垃圾邮件得分")


# ========== Redis布隆过滤器 ==========

class RedisBloomFilter:
    """Redis布隆过滤器实现"""

    def __init__(self, redis_client, key: str, max_elements: int = 100000, error_rate: float = 0.01):
        """初始化Redis布隆过滤器"""
        self.redis = redis_client
        self.key = key
        self.max_elements = max_elements
        self.error_rate = error_rate
        self._init_bloom_filter()

    def _init_bloom_filter(self):
        """初始化布隆过滤器"""
        try:
            # 检查布隆过滤器是否已经存在
            if not self.redis.exists(self.key):
                # 创建布隆过滤器
                self.redis.execute_command("BF.RESERVE", self.key, self.error_rate, self.max_elements)
                logger.info(f"Redis布隆过滤器{self.key}已初始化")
        except Exception as e:
            logger.error(f"初始化Redis布隆过滤器失败: {str(e)}")

    def add(self, value: str):
        """添加元素到布隆过滤器"""
        try:
            self.redis.execute_command("BF.ADD", self.key, value)
        except Exception as e:
            logger.error(f"添加元素到Redis布隆过滤器失败: {str(e)}")

    def contains(self, value: str) -> bool:
        """判断元素是否在布隆过滤器中"""
        try:
            result = self.redis.execute_command("BF.EXISTS", self.key, value)
            return result == 1
        except Exception as e:
            logger.error(f"判断元素是否在Redis布隆过滤器中失败: {str(e)}")
            return False


# ========== 服务类 ==========

class AntiSpamService:
    """反垃圾邮件服务类"""

    def __init__(self):
        """初始化服务"""
        self.mysql_db = get_mysql_db()
        # 延迟初始化Redis客户端
        self.redis = None
        self._init_redis()
        # 初始化Redis布隆过滤器
        self.device_bloom_filter = None
        self.ip_bloom_filter = None
        self._init_bloom_filters()
        # 启动定时重建任务
        asyncio.create_task(self._rebuild_bloom_filter_periodically())
        logger.info("反垃圾邮件服务已初始化")

    def _init_redis(self):
        """初始化Redis客户端"""
        try:
            from ..database.redis_client import get_redis_client
            self.redis = get_redis_client()
            logger.debug("Redis客户端初始化成功")
        except Exception as e:
            logger.warning(f"Redis客户端初始化失败: {str(e)}")
            self.redis = None

    def _init_bloom_filters(self):
        """初始化Redis布隆过滤器"""
        if self.redis:
            self.device_bloom_filter = RedisBloomFilter(self.redis, "device_blacklist", max_elements=100000, error_rate=0.01)
            self.ip_bloom_filter = RedisBloomFilter(self.redis, "ip_blacklist", max_elements=100000, error_rate=0.01)
            logger.info("Redis布隆过滤器已初始化")
        else:
            logger.warning("Redis客户端未初始化，无法初始化布隆过滤器")

    def _load_blacklist(self):
        """加载黑名单"""
        try:
            # 从数据库加载黑名单设备ID
            with self.mysql_db.get_session() as session:
                # 查询黑名单设备ID
                blacklist_devices = session.query(UserProfile.device_id).filter(
                    UserProfile.is_blacklisted == True
                ).all()
                
                # 将黑名单设备ID添加到Redis布隆过滤器
                for device_id in blacklist_devices:
                    if self.device_bloom_filter:
                        self.device_bloom_filter.add(device_id)
                
                # 查询黑名单IP地址
                blacklist_ips = session.query(UserProfile.ip_address).filter(
                    UserProfile.is_blacklisted == True
                ).all()
                
                # 将黑名单IP地址添加到Redis布隆过滤器
                for ip_address in blacklist_ips:
                    if self.ip_bloom_filter:
                        self.ip_bloom_filter.add(ip_address)
                
                logger.info(f"加载了{len(blacklist_devices)}个黑名单设备ID和{len(blacklist_ips)}个黑名单IP地址")
                
        except Exception as e:
            logger.error(f"加载黑名单失败: {str(e)}")

    async def _rebuild_bloom_filter_periodically(self):
        """
        定时重建布隆过滤器
        """
        while True:
            # 等待一天
            await asyncio.sleep(86400)
            
            # 重建布隆过滤器
            logger.info("开始定时重建布隆过滤器")
            self._load_blacklist()
            logger.info("布隆过滤器定时重建完成")

    async def check_register_allowed(self, request: AntiSpamRequest) -> AntiSpamResponse:
        """检查是否允许注册"""
        try:
            logger.info(f"检查用户{request.user_id}的注册请求")

            # 步骤3.1: 设备ID布隆过滤器层
            # 检查设备ID是否在黑名单中
            if self.device_bloom_filter and self.device_bloom_filter.contains(request.device_id):
                logger.warning(f"设备ID{request.device_id}在黑名单中")
                return AntiSpamResponse(
                    allowed=False,
                    reason="设备ID在黑名单中",
                    score=1.0
                )

            # 步骤3.2: IP地址布隆过滤器层
            # 检查IP地址是否在黑名单中
            if self.ip_bloom_filter and self.ip_bloom_filter.contains(request.ip_address):
                logger.warning(f"IP地址{request.ip_address}在黑名单中")
                return AntiSpamResponse(
                    allowed=False,
                    reason="IP地址在黑名单中",
                    score=0.9
                )

            # 步骤3.3: 请求频率限制层
            # 检查请求频率
            if self.redis:
                cache_key = f"anti_spam:{request.ip_address}:{request.request_type}"
                request_count = await self.redis.incr(cache_key)
                if request_count == 1:
                    await self.redis.expire(cache_key, 60)
                if request_count > 10:
                    logger.warning(f"IP地址{request.ip_address}请求频率过高")
                    return AntiSpamResponse(
                        allowed=False,
                        reason="请求频率过高",
                        score=0.8
                    )

            # 步骤3.4: 内容过滤层
            # 检查请求内容
            # 这里可以添加内容过滤逻辑

            # 步骤3.5: 机器学习模型层
            # 使用机器学习模型判断是否为垃圾邮件
            # 这里可以添加机器学习模型逻辑

            # 允许注册
            logger.info(f"用户{request.user_id}的注册请求被允许")
            return AntiSpamResponse(
                allowed=True,
                score=0.0
            )

        except Exception as e:
            logger.error(f"检查注册请求失败: {str(e)}")
            return AntiSpamResponse(
                allowed=False,
                reason="服务器错误",
                score=0.5
            )


# ========== 全局实例（单例模式） ==========

_anti_spam_service: Optional[AntiSpamService] = None


def get_anti_spam_service() -> AntiSpamService:
    """
    获取全局反垃圾邮件服务实例（单例）

    Returns:
        AntiSpamService: 反垃圾邮件服务实例
    """
    global _anti_spam_service
    if _anti_spam_service is None:
        _anti_spam_service = AntiSpamService()
    return _anti_spam_service


# ========== 手动重建接口 ==========

def rebuild_bloom_filter():
    """
    手动重建布隆过滤器
    """
    anti_spam_service = get_anti_spam_service()
    anti_spam_service._load_blacklist()
    logger.info("布隆过滤器手动重建完成")
    return {"message": "布隆过滤器手动重建完成"}
