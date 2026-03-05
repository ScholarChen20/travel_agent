"""反暴力注册请求服务"""

from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime, timedelta
from loguru import logger
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

    async def init_bloom_filter(self):
        """异步初始化布隆过滤器"""
        try:
            exists_result = await self.redis.exists(self.key)
            if not exists_result:
                await self.redis.execute_command("BF.RESERVE", self.key, self.error_rate, self.max_elements)
                logger.info(f"Redis布隆过滤器{self.key}已初始化")
        except Exception as e:
            logger.error(f"初始化Redis布隆过滤器失败: {str(e)}")

    async def add(self, value: str):
        """异步添加元素到布隆过滤器"""
        try:
            await self.redis.execute_command("BF.ADD", self.key, value)
        except Exception as e:
            logger.error(f"添加元素到Redis布隆过滤器失败: {str(e)}")

    async def contains(self, value: str) -> bool:
        """异步判断元素是否在布隆过滤器中"""
        try:
            result = await self.redis.execute_command("BF.EXISTS", self.key, value)
            return result == 1
        except Exception as e:
            logger.error(f"判断元素是否在Redis布隆过滤器中失败: {str(e)}")
            return False


class BlacklistManager:
    """黑名单管理器 - 使用Redis存储黑名单数据"""

    def __init__(self, redis_client):
        """初始化黑名单管理器"""
        self.redis = redis_client

    async def add_device_to_blacklist(
        self,
        device_id: str,
        reason: Optional[str] = None,
        ttl_seconds: Optional[int] = None
    ) -> bool:
        """
        添加设备ID到黑名单

        Args:
            device_id: 设备ID
            reason: 拉黑原因
            ttl_seconds: 过期时间（秒），None表示永久

        Returns:
            bool: 是否成功
        """
        try:
            key = f"blacklist:device:{device_id}"
            
            # 存储黑名单信息
            await self.redis.hset(key, mapping={
                "device_id": device_id,
                "reason": reason or "",
                "created_at": datetime.now().isoformat()
            })
            
            # 设置TTL
            if ttl_seconds is not None:
                await self.redis.expire(key, ttl_seconds)
                logger.info(f"添加设备{device_id}到黑名单，TTL: {ttl_seconds}秒")
            else:
                logger.info(f"添加设备{device_id}到黑名单（永久）")

            return True

        except Exception as e:
            logger.error(f"添加设备到黑名单失败: {str(e)}")
            return False

    async def add_ip_to_blacklist(
        self,
        ip_address: str,
        reason: Optional[str] = None,
        ttl_seconds: Optional[int] = None
    ) -> bool:
        """
        添加IP地址到黑名单

        Args:
            ip_address: IP地址
            reason: 拉黑原因
            ttl_seconds: 过期时间（秒），None表示永久

        Returns:
            bool: 是否成功
        """
        try:
            key = f"blacklist:ip:{ip_address}"
            
            # 存储黑名单信息
            await self.redis.hset(key, mapping={
                "ip_address": ip_address,
                "reason": reason or "",
                "created_at": datetime.now().isoformat()
            })
            
            # 设置TTL
            if ttl_seconds is not None:
                await self.redis.expire(key, ttl_seconds)
                logger.info(f"添加IP{ip_address}到黑名单，TTL: {ttl_seconds}秒")
            else:
                logger.info(f"添加IP{ip_address}到黑名单（永久）")

            return True

        except Exception as e:
            logger.error(f"添加IP到黑名单失败: {str(e)}")
            return False

    async def remove_device_from_blacklist(self, device_id: str) -> bool:
        """
        从黑名单中移除设备ID

        Args:
            device_id: 设备ID

        Returns:
            bool: 是否成功
        """
        try:
            key = f"blacklist:device:{device_id}"
            result = await self.redis.delete(key)
            
            if result > 0:
                logger.info(f"从黑名单移除设备: {device_id}")
                return True
            else:
                logger.warning(f"设备{device_id}不在黑名单中")
                return False

        except Exception as e:
            logger.error(f"从黑名单移除设备失败: {str(e)}")
            return False

    async def remove_ip_from_blacklist(self, ip_address: str) -> bool:
        """
        从黑名单中移除IP地址

        Args:
            ip_address: IP地址

        Returns:
            bool: 是否成功
        """
        try:
            key = f"blacklist:ip:{ip_address}"
            result = await self.redis.delete(key)
            
            if result > 0:
                logger.info(f"从黑名单移除IP: {ip_address}")
                return True
            else:
                logger.warning(f"IP{ip_address}不在黑名单中")
                return False

        except Exception as e:
            logger.error(f"从黑名单移除IP失败: {str(e)}")
            return False

    async def is_device_blacklisted(self, device_id: str) -> bool:
        """
        检查设备是否在黑名单中

        Args:
            device_id: 设备ID

        Returns:
            bool: 是否在黑名单中
        """
        try:
            key = f"blacklist:device:{device_id}"
            result = await self.redis.exists(key)
            return result > 0
        except Exception as e:
            logger.error(f"检查设备黑名单失败: {str(e)}")
            return False

    async def is_ip_blacklisted(self, ip_address: str) -> bool:
        """
        检查IP是否在黑名单中

        Args:
            ip_address: IP地址

        Returns:
            bool: 是否在黑名单中
        """
        try:
            key = f"blacklist:ip:{ip_address}"
            result = await self.redis.exists(key)
            return result > 0
        except Exception as e:
            logger.error(f"检查IP黑名单失败: {str(e)}")
            return False

    async def get_device_blacklist_info(self, device_id: str) -> Optional[Dict[str, Any]]:
        """
        获取设备黑名单信息

        Args:
            device_id: 设备ID

        Returns:
            Dict: 黑名单信息，不存在返回None
        """
        try:
            key = f"blacklist:device:{device_id}"
            data = await self.redis.hgetall(key)
            
            if data:
                return {
                    "device_id": data.get("device_id", "").decode() if isinstance(data.get("device_id"), bytes) else data.get("device_id", ""),
                    "reason": data.get("reason", "").decode() if isinstance(data.get("reason"), bytes) else data.get("reason", ""),
                    "created_at": data.get("created_at", "").decode() if isinstance(data.get("created_at"), bytes) else data.get("created_at", ""),
                    "ttl": await self.redis.ttl(key)
                }
            return None

        except Exception as e:
            logger.error(f"获取设备黑名单信息失败: {str(e)}")
            return None

    async def get_ip_blacklist_info(self, ip_address: str) -> Optional[Dict[str, Any]]:
        """
        获取IP黑名单信息

        Args:
            ip_address: IP地址

        Returns:
            Dict: 黑名单信息，不存在返回None
        """
        try:
            key = f"blacklist:ip:{ip_address}"
            data = await self.redis.hgetall(key)
            
            if data:
                return {
                    "ip_address": data.get("ip_address", "").decode() if isinstance(data.get("ip_address"), bytes) else data.get("ip_address", ""),
                    "reason": data.get("reason", "").decode() if isinstance(data.get("reason"), bytes) else data.get("reason", ""),
                    "created_at": data.get("created_at", "").decode() if isinstance(data.get("created_at"), bytes) else data.get("created_at", ""),
                    "ttl": await self.redis.ttl(key)
                }
            return None

        except Exception as e:
            logger.error(f"获取IP黑名单信息失败: {str(e)}")
            return None

    async def load_all_blacklists_to_bloom_filter(self, bloom_filter_device, bloom_filter_ip):
        """
        加载所有黑名单到布隆过滤器

        Args:
            bloom_filter_device: 设备布隆过滤器
            bloom_filter_ip: IP布隆过滤器
        """
        try:
            # 加载设备黑名单
            device_keys = await self.redis.keys("blacklist:device:*")
            device_count = 0
            for key in device_keys:
                device_id = key.decode().split(":")[-1] if isinstance(key, bytes) else key.split(":")[-1]
                await bloom_filter_device.add(device_id)
                device_count += 1
            
            # 加载IP黑名单
            ip_keys = await self.redis.keys("blacklist:ip:*")
            ip_count = 0
            for key in ip_keys:
                ip_address = key.decode().split(":")[-1] if isinstance(key, bytes) else key.split(":")[-1]
                await bloom_filter_ip.add(ip_address)
                ip_count += 1
            
            logger.info(f"加载了{device_count}个设备黑名单和{ip_count}个IP黑名单到布隆过滤器")

        except Exception as e:
            logger.error(f"加载黑名单到布隆过滤器失败: {str(e)}")

    async def get_all_blacklists(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        获取所有黑名单信息

        Returns:
            Dict: 包含设备和IP黑名单的字典
        """
        try:
            result = {
                "devices": [],
                "ips": []
            }

            # 获取设备黑名单
            device_keys = await self.redis.keys("blacklist:device:*")
            for key in device_keys:
                device_id = key.decode().split(":")[-1] if isinstance(key, bytes) else key.split(":")[-1]
                info = await self.get_device_blacklist_info(device_id)
                if info:
                    result["devices"].append(info)

            # 获取IP黑名单
            ip_keys = await self.redis.keys("blacklist:ip:*")
            for key in ip_keys:
                ip_address = key.decode().split(":")[-1] if isinstance(key, bytes) else key.split(":")[-1]
                info = await self.get_ip_blacklist_info(ip_address)
                if info:
                    result["ips"].append(info)

            return result

        except Exception as e:
            logger.error(f"获取所有黑名单失败: {str(e)}")
            return {"devices": [], "ips": []}


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
        # 初始化黑名单管理器
        self.blacklist_manager = None
        # 初始化标志
        self._initialized = False
        logger.info("反垃圾邮件服务已初始化")

    async def initialize(self):
        """异步初始化布隆过滤器"""
        if not self._initialized:
            await self._init_bloom_filters()
            await self._load_blacklists()
            self._initialized = True
            # 启动定时重建任务
            asyncio.create_task(self._rebuild_bloom_filter_periodically())

    def _init_redis(self):
        """初始化Redis客户端"""
        try:
            from ..database.redis_client import get_redis_client
            self.redis = get_redis_client()
            logger.debug("Redis客户端初始化成功")
        except Exception as e:
            logger.warning(f"Redis客户端初始化失败: {str(e)}")
            self.redis = None

    async def _init_bloom_filters(self):
        """异步初始化Redis布隆过滤器"""
        if self.redis:
            self.device_bloom_filter = RedisBloomFilter(self.redis, "device_blacklist", max_elements=1000000, error_rate=0.01)
            self.ip_bloom_filter = RedisBloomFilter(self.redis, "ip_blacklist", max_elements=1000000, error_rate=0.01)
            self.blacklist_manager = BlacklistManager(self.redis)
            await self.device_bloom_filter.init_bloom_filter()
            await self.ip_bloom_filter.init_bloom_filter()
            logger.info("Redis布隆过滤器已初始化")
        else:
            logger.warning("Redis客户端未初始化，无法初始化布隆过滤器")

    async def _load_blacklists(self):
        """从Redis加载黑名单到布隆过滤器"""
        try:
            if self.blacklist_manager and self.device_bloom_filter and self.ip_bloom_filter:
                await self.blacklist_manager.load_all_blacklists_to_bloom_filter(
                    self.device_bloom_filter,
                    self.ip_bloom_filter
                )
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
            await self.rebuild_bloom_filter()
            logger.info("布隆过滤器定时重建完成")

    async def check_register_allowed(self, request: AntiSpamRequest) -> AntiSpamResponse:
        """检查是否允许注册"""
        try:
            logger.info(f"检查用户{request.user_id}的注册请求")

            # 步骤3.1: 设备ID黑名单层
            # 检查设备ID是否在黑名单中
            if self.blacklist_manager and await self.blacklist_manager.is_device_blacklisted(request.device_id):
                blacklist_info = await self.blacklist_manager.get_device_blacklist_info(request.device_id)
                reason = blacklist_info.get("reason", "设备ID在黑名单中") if blacklist_info else "设备ID在黑名单中"
                logger.warning(f"设备ID{request.device_id}在黑名单中，原因: {reason}")
                return AntiSpamResponse(
                    allowed=False,
                    reason=f"设备ID在黑名单中: {reason}",
                    score=1.0
                )

            # 步骤3.2: IP地址黑名单层
            # 检查IP地址是否在黑名单中
            if self.blacklist_manager and await self.blacklist_manager.is_ip_blacklisted(request.ip_address):
                blacklist_info = await self.blacklist_manager.get_ip_blacklist_info(request.ip_address)
                reason = blacklist_info.get("reason", "IP地址在黑名单中") if blacklist_info else "IP地址在黑名单中"
                logger.warning(f"IP地址{request.ip_address}在黑名单中，原因: {reason}")
                return AntiSpamResponse(
                    allowed=False,
                    reason=f"IP地址在黑名单中: {reason}",
                    score=0.9
                )

            # 步骤3.3: IP请求频率限制层
            # IP检查请求频率
            if self.redis:
                cache_key = f"anti_spam:{request.ip_address}:{request.request_type}"
                request_count = await self.redis.incr(cache_key)
                if request_count == 1:
                    await self.redis.expire(cache_key, 60)
                if request_count > 20:
                    logger.warning(f"IP地址{request.ip_address}请求频率过高")
                    await self.blacklist_manager.add_ip_to_blacklist(request.ip_address, "请求频率过高")
                    return AntiSpamResponse(
                        allowed=False,
                        reason="请求频率过高",
                        score=0.8
                    )

            # 步骤3.4: 设备请求频率限制层
            if self.redis:
                cache_key = f"anti_spam:{request.device_id}:{request.request_type}"
                request_count = await self.redis.incr(cache_key)
                if request_count == 1:
                    await self.redis.expire(cache_key, 60)
                if request_count > 20:
                    logger.warning(f"设备ID{request.device_id}请求频率过高")
                    await self.blacklist_manager.add_device_to_blacklist(request.device_id, "请求频率过高")
                    return AntiSpamResponse(
                        allowed=False,
                        reason="请求频率过高",
                        score=0.7
                    )

            # 步骤3.5: 机器学习模型层

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

    async def check_login_allowed(self, device_id: str) -> AntiSpamResponse:
        """检查是否允许登录"""
        try:
            # 检查设备ID是否在黑名单中
            if self.blacklist_manager and await self.blacklist_manager.is_device_blacklisted(device_id):
                blacklist_info = await self.blacklist_manager.get_device_blacklist_info(device_id)
                reason = blacklist_info.get("reason", "设备ID在黑名单中") if blacklist_info else "设备ID在黑名单中"
                logger.warning(f"设备ID{device_id}在黑名单中，原因: {reason}")
                return AntiSpamResponse(
                    allowed=False,
                    reason=f"设备ID在黑名单中: {reason}",
                    score=1.0
                )
            # 用户允许登录
            return AntiSpamResponse(
                allowed=True,
                score=0.0
            )
        except Exception as e:
            logger.error(f"检查登录请求失败: {str(e)}")
            return AntiSpamResponse(
                allowed=False,
                reason="服务器错误",
                score=0.5
            )

    async def add_device_to_blacklist(
        self,
        device_id: str,
        reason: Optional[str] = None,
        ttl_seconds: Optional[int] = None
    ) -> bool:
        """
        添加设备ID到黑名单

        Args:
            device_id: 设备ID
            reason: 拉黑原因
            ttl_seconds: 过期时间（秒），None表示永久

        Returns:
            bool: 是否成功
        """
        try:
            if not self.blacklist_manager:
                logger.error("黑名单管理器未初始化")
                return False

            # 添加到Redis黑名单
            success = await self.blacklist_manager.add_device_to_blacklist(
                device_id=device_id,
                reason=reason,
                ttl_seconds=ttl_seconds
            )

            if success and self.device_bloom_filter:
                # 添加到布隆过滤器
                await self.device_bloom_filter.add(device_id)

            return success

        except Exception as e:
            logger.error(f"添加设备到黑名单失败: {str(e)}")
            return False

    async def add_ip_to_blacklist(
        self,
        ip_address: str,
        reason: Optional[str] = None,
        ttl_seconds: Optional[int] = None
    ) -> bool:
        """
        添加IP地址到黑名单

        Args:
            ip_address: IP地址
            reason: 拉黑原因
            ttl_seconds: 过期时间（秒），None表示永久

        Returns:
            bool: 是否成功
        """
        try:
            if not self.blacklist_manager:
                logger.error("黑名单管理器未初始化")
                return False

            # 添加到Redis黑名单
            success = await self.blacklist_manager.add_ip_to_blacklist(
                ip_address=ip_address,
                reason=reason,
                ttl_seconds=ttl_seconds
            )

            if success and self.ip_bloom_filter:
                # 添加到布隆过滤器
                await self.ip_bloom_filter.add(ip_address)

            return success

        except Exception as e:
            logger.error(f"添加IP到黑名单失败: {str(e)}")
            return False

    async def remove_device_from_blacklist(self, device_id: str) -> bool:
        """
        从黑名单中移除设备ID

        Args:
            device_id: 设备ID

        Returns:
            bool: 是否成功
        """
        try:
            if not self.blacklist_manager:
                logger.error("黑名单管理器未初始化")
                return False

            # 从Redis黑名单移除
            success = await self.blacklist_manager.remove_device_from_blacklist(device_id)

            if success:
                # 重建布隆过滤器
                await self.rebuild_bloom_filter()

            return success

        except Exception as e:
            logger.error(f"从黑名单移除设备失败: {str(e)}")
            return False

    async def remove_ip_from_blacklist(self, ip_address: str) -> bool:
        """
        从黑名单中移除IP地址

        Args:
            ip_address: IP地址

        Returns:
            bool: 是否成功
        """
        try:
            if not self.blacklist_manager:
                logger.error("黑名单管理器未初始化")
                return False

            # 从Redis黑名单移除
            success = await self.blacklist_manager.remove_ip_from_blacklist(ip_address)

            if success:
                # 重建布隆过滤器
                await self.rebuild_bloom_filter()

            return success

        except Exception as e:
            logger.error(f"从黑名单移除IP失败: {str(e)}")
            return False

    async def rebuild_bloom_filter(self):
        """重建布隆过滤器"""
        try:
            logger.info("开始重建布隆过滤器")
            
            # 重新初始化布隆过滤器
            if self.redis:
                # 删除旧的布隆过滤器
                await self.redis.delete("device_blacklist")
                await self.redis.delete("ip_blacklist")
                
                # 重新初始化
                await self.device_bloom_filter.init_bloom_filter()
                await self.ip_bloom_filter.init_bloom_filter()
                
                # 重新加载黑名单
                await self._load_blacklists()
                
                logger.info("布隆过滤器重建完成")
            
        except Exception as e:
            logger.error(f"重建布隆过滤器失败: {str(e)}")

# ========== 全局实例（单例模式） ==========

_anti_spam_service: Optional[AntiSpamService] = None
_anti_spam_service_initialized = False


async def get_anti_spam_service() -> AntiSpamService:
    """
    获取全局反垃圾邮件服务实例（单例）

    Returns:
        AntiSpamService: 反垃圾邮件服务实例
    """
    global _anti_spam_service, _anti_spam_service_initialized
    if _anti_spam_service is None:
        _anti_spam_service = AntiSpamService()
    
    if not _anti_spam_service_initialized:
        await _anti_spam_service.initialize()
        _anti_spam_service_initialized = True
    
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
