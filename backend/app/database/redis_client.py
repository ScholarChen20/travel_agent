"""Redis客户端连接管理"""

from typing import Optional, Any, Union
import json
import redis.asyncio as redis
from redis.asyncio import Redis
from redis.exceptions import RedisError, ConnectionError
from loguru import logger


class RedisClient:
    """Redis异步客户端管理器"""

    def __init__(self, url: str):
        """
        初始化Redis客户端

        Args:
            url: Redis连接URL，格式：redis://[:password]@host:port/db
                示例：redis://localhost:6379/0 或 redis://:password@localhost:6379/0
        """
        self.url = url

        # 创建Redis客户端
        self.client: Redis = redis.Redis.from_url(
            url,
            max_connections=50,  # 最大连接数
            decode_responses=True,  # 自动解码为字符串
            socket_keepalive=True,  # 保持连接活跃
            socket_connect_timeout=5,  # 连接超时（秒）
            retry_on_timeout=True  # 超时时自动重试
        )

        logger.info(f"Redis客户端已创建：{self._safe_url()}")

    def _safe_url(self) -> str:
        """返回隐藏密码的安全URL（用于日志）"""
        if ':' in self.url and '@' in self.url:
            parts = self.url.split('@')
            protocol = parts[0].split('://')[0]
            return f"{protocol}://***@{parts[1]}"
        return self.url

    # ========== 基础键值操作 ==========

    async def set(
        self,
        key: str,
        value: Union[str, dict, list],
        ex: Optional[int] = None
    ) -> bool:
        """
        设置键值

        Args:
            key: 键名
            value: 值（支持字符串、字典、列表，自动转JSON）
            ex: 过期时间（秒）

        Returns:
            bool: 是否设置成功
        """
        try:
            if isinstance(value, (dict, list)):
                value = json.dumps(value, ensure_ascii=False)

            await self.client.set(key, value, ex=ex)
            return True
        except Exception as e:
            logger.error(f"Redis SET失败 - key: {key}, error: {str(e)}")
            return False

    async def get(self, key: str, as_json: bool = False) -> Optional[Any]:
        """
        获取键值

        Args:
            key: 键名
            as_json: 是否解析为JSON

        Returns:
            值（字符串或解析后的对象），不存在返回None
        """
        try:
            value = await self.client.get(key)
            if value is None:
                return None

            if as_json:
                try:
                    return json.loads(value)
                except json.JSONDecodeError:
                    logger.warning(f"Redis GET: key {key} 不是有效的JSON")
                    return value

            return value
        except Exception as e:
            logger.error(f"Redis GET失败 - key: {key}, error: {str(e)}")
            return None

    async def delete(self, *keys: str) -> int:
        """
        删除一个或多个键

        Args:
            keys: 键名列表

        Returns:
            删除的键数量
        """
        try:
            return await self.client.delete(*keys)
        except Exception as e:
            logger.error(f"Redis DELETE失败 - keys: {keys}, error: {str(e)}")
            return 0

    async def exists(self, *keys: str) -> int:
        """
        检查键是否存在

        Args:
            keys: 键名列表

        Returns:
            存在的键数量
        """
        try:
            return await self.client.exists(*keys)
        except Exception as e:
            logger.error(f"Redis EXISTS失败 - keys: {keys}, error: {str(e)}")
            return 0

    async def expire(self, key: str, seconds: int) -> bool:
        """
        设置键的过期时间

        Args:
            key: 键名
            seconds: 过期时间（秒）

        Returns:
            bool: 是否设置成功
        """
        try:
            return await self.client.expire(key, seconds)
        except Exception as e:
            logger.error(f"Redis EXPIRE失败 - key: {key}, error: {str(e)}")
            return False

    async def ttl(self, key: str) -> int:
        """
        获取键的剩余生存时间

        Args:
            key: 键名

        Returns:
            剩余秒数，-1表示永不过期，-2表示键不存在
        """
        try:
            return await self.client.ttl(key)
        except Exception as e:
            logger.error(f"Redis TTL失败 - key: {key}, error: {str(e)}")
            return -2

    # ========== Hash操作 ==========

    async def hset(self, name: str, key: str, value: str) -> int:
        """Hash表设置字段"""
        try:
            return await self.client.hset(name, key, value)
        except Exception as e:
            logger.error(f"Redis HSET失败 - name: {name}, key: {key}, error: {str(e)}")
            return 0

    async def hget(self, name: str, key: str) -> Optional[str]:
        """Hash表获取字段"""
        try:
            return await self.client.hget(name, key)
        except Exception as e:
            logger.error(f"Redis HGET失败 - name: {name}, key: {key}, error: {str(e)}")
            return None

    async def hgetall(self, name: str) -> dict:
        """Hash表获取所有字段"""
        try:
            return await self.client.hgetall(name)
        except Exception as e:
            logger.error(f"Redis HGETALL失败 - name: {name}, error: {str(e)}")
            return {}

    async def hdel(self, name: str, *keys: str) -> int:
        """Hash表删除字段"""
        try:
            return await self.client.hdel(name, *keys)
        except Exception as e:
            logger.error(f"Redis HDEL失败 - name: {name}, keys: {keys}, error: {str(e)}")
            return 0

    # ========== List操作 ==========

    async def lpush(self, key: str, *values: str) -> int:
        """List头部插入"""
        try:
            return await self.client.lpush(key, *values)
        except Exception as e:
            logger.error(f"Redis LPUSH失败 - key: {key}, error: {str(e)}")
            return 0

    async def rpush(self, key: str, *values: str) -> int:
        """List尾部插入"""
        try:
            return await self.client.rpush(key, *values)
        except Exception as e:
            logger.error(f"Redis RPUSH失败 - key: {key}, error: {str(e)}")
            return 0

    async def lrange(self, key: str, start: int, end: int) -> list:
        """获取List范围内的元素"""
        try:
            return await self.client.lrange(key, start, end)
        except Exception as e:
            logger.error(f"Redis LRANGE失败 - key: {key}, error: {str(e)}")
            return []

    async def ltrim(self, key: str, start: int, end: int) -> bool:
        """裁剪List，只保留指定范围"""
        try:
            await self.client.ltrim(key, start, end)
            return True
        except Exception as e:
            logger.error(f"Redis LTRIM失败 - key: {key}, error: {str(e)}")
            return False

    # ========== 自增操作 ==========

    async def incr(self, key: str, amount: int = 1) -> int:
        """
        键值自增

        Args:
            key: 键名
            amount: 增量（默认1）

        Returns:
            增加后的值
        """
        try:
            return await self.client.incr(key, amount)
        except Exception as e:
            logger.error(f"Redis INCR失败 - key: {key}, error: {str(e)}")
            return 0

    async def decr(self, key: str, amount: int = 1) -> int:
        """
        键值自减

        Args:
            key: 键名
            amount: 减量（默认1）

        Returns:
            减少后的值
        """
        try:
            return await self.client.decr(key, amount)
        except Exception as e:
            logger.error(f"Redis DECR失败 - key: {key}, error: {str(e)}")
            return 0

    # ========== 健康检查 ==========

    async def ping(self) -> bool:
        """
        Ping测试连接

        Returns:
            bool: 连接是否正常
        """
        try:
            response = await self.client.ping()
            logger.debug("Redis PING: 连接正常")
            return response is True
        except (RedisError, ConnectionError) as e:
            logger.error(f"Redis PING失败: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Redis PING失败（未知错误）: {str(e)}")
            return False

    async def health_check(self) -> bool:
        """
        健康检查

        Returns:
            bool: True表示连接正常，False表示连接异常
        """
        return await self.ping()

    # ========== 连接管理 ==========

    async def close(self):
        """关闭Redis客户端"""
        if self.client:
            await self.client.aclose()
            logger.info("Redis客户端已关闭")

    # ========== 通用辅助方法 ==========

    async def keys(self, pattern: str = "*") -> list:
        """
        获取所有匹配模式的键（谨慎使用，大数据集会阻塞）

        Args:
            pattern: 模式，如 "user:*"

        Returns:
            键名列表
        """
        try:
            return await self.client.keys(pattern)
        except Exception as e:
            logger.error(f"Redis KEYS失败 - pattern: {pattern}, error: {str(e)}")
            return []

    async def flushdb(self):
        """清空当前数据库（危险操作！）"""
        logger.warning("Redis FLUSHDB: 清空当前数据库（危险操作）")
        await self.client.flushdb()


# 全局Redis客户端实例（单例）
_redis_client: Optional[RedisClient] = None
_redis_url: Optional[str] = None


def get_redis_client() -> RedisClient:
    """
    获取全局Redis客户端实例（单例）

    Returns:
        RedisClient: Redis客户端实例
    """
    global _redis_client, _redis_url
    if _redis_client is None:
        if _redis_url is None:
            raise RuntimeError("Redis客户端未初始化，请先调用init_redis_client()")
        _redis_client = RedisClient(_redis_url)
    return _redis_client


def init_redis_client(url: str) -> RedisClient:
    """
    初始化全局Redis客户端实例

    Args:
        url: Redis连接URL

    Returns:
        RedisClient: Redis客户端实例
    """
    global _redis_client, _redis_url
    _redis_url = url  # 保存URL，用于懒加载
    if _redis_client is None:
        _redis_client = RedisClient(url)
    return _redis_client
