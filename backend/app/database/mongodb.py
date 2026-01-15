"""MongoDB数据库连接管理"""

from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase, AsyncIOMotorCollection
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError
from loguru import logger


class MongoDBClient:
    """MongoDB异步客户端管理器"""

    def __init__(self, uri: str, database: str):
        """
        初始化MongoDB客户端

        Args:
            uri: MongoDB连接URI，格式：mongodb://username:password@host:port
            database: 数据库名称
        """
        self.uri = uri
        self.database_name = database

        # 创建异步客户端（用于FastAPI异步操作）
        self.async_client = AsyncIOMotorClient(
            uri,
            maxPoolSize=50,  # 最大连接池大小
            minPoolSize=10,  # 最小连接池大小
            maxIdleTimeMS=30000,  # 最大空闲时间（30秒）
            serverSelectionTimeoutMS=5000,  # 服务器选择超时（5秒）
        )

        # 创建同步客户端（用于初始化和健康检查）
        self.sync_client = MongoClient(
            uri,
            maxPoolSize=10,
            serverSelectionTimeoutMS=5000
        )

        # 获取数据库实例
        self.async_db = self.async_client[database]
        self.sync_db = self.sync_client[database]

        logger.info(f"MongoDB客户端已创建：{self._safe_uri()}, 数据库：{database}")

    def _safe_uri(self) -> str:
        """返回隐藏密码的安全URI（用于日志）"""
        if '@' in self.uri:
            parts = self.uri.split('@')
            protocol = parts[0].split('://')[0]
            return f"{protocol}://***@{parts[1]}"
        return "mongodb://***"

    def get_collection(self, collection_name: str) -> AsyncIOMotorCollection:
        """
        获取异步集合对象

        Args:
            collection_name: 集合名称

        Returns:
            AsyncIOMotorCollection: 异步集合对象
        """
        return self.async_db[collection_name]

    def get_sync_collection(self, collection_name: str):
        """
        获取同步集合对象

        Args:
            collection_name: 集合名称

        Returns:
            Collection: 同步集合对象
        """
        return self.sync_db[collection_name]

    @property
    def db(self) -> AsyncIOMotorDatabase:
        """获取异步数据库对象"""
        return self.async_db

    async def health_check(self) -> bool:
        """
        异步健康检查

        Returns:
            bool: True表示连接正常，False表示连接异常
        """
        try:
            await self.async_client.admin.command('ping')
            logger.debug("MongoDB健康检查：连接正常")
            return True
        except Exception as e:
            logger.error(f"MongoDB健康检查失败: {str(e)}")
            return False

    def health_check_sync(self) -> bool:
        """
        同步健康检查

        Returns:
            bool: True表示连接正常，False表示连接异常
        """
        try:
            self.sync_client.admin.command('ping')
            logger.debug("MongoDB健康检查（同步）：连接正常")
            return True
        except ServerSelectionTimeoutError as e:
            logger.error(f"MongoDB健康检查（同步）失败：无法连接到服务器 - {str(e)}")
            return False
        except Exception as e:
            logger.error(f"MongoDB健康检查（同步）失败: {str(e)}")
            return False

    async def close(self):
        """关闭异步客户端连接"""
        if self.async_client:
            self.async_client.close()
            logger.info("MongoDB异步客户端已关闭")

    def close_sync(self):
        """关闭同步客户端连接"""
        if self.sync_client:
            self.sync_client.close()
            logger.info("MongoDB同步客户端已关闭")

    async def create_indexes(self):
        """
        创建所有集合的索引

        注意：这个方法应该在应用启动时调用一次
        """
        logger.info("开始创建MongoDB索引...")

        # dialog_sessions索引
        dialog_sessions = self.get_collection("dialog_sessions")
        await dialog_sessions.create_index([("user_id", 1), ("last_message_at", -1)])
        await dialog_sessions.create_index([("session_id", 1)], unique=True)
        await dialog_sessions.create_index([("status", 1), ("updated_at", -1)])

        # tool_call_logs索引
        tool_call_logs = self.get_collection("tool_call_logs")
        await tool_call_logs.create_index([("session_id", 1), ("created_at", -1)])
        await tool_call_logs.create_index([("user_id", 1), ("tool_name", 1), ("created_at", -1)])
        await tool_call_logs.create_index([("created_at", -1)])

        # travel_plans索引
        travel_plans = self.get_collection("travel_plans")
        await travel_plans.create_index([("user_id", 1), ("created_at", -1)])
        await travel_plans.create_index([("plan_id", 1)], unique=True)
        await travel_plans.create_index([("session_id", 1)])
        await travel_plans.create_index([("city", 1), ("start_date", -1)])

        # agent_context_memory索引
        agent_context_memory = self.get_collection("agent_context_memory")
        await agent_context_memory.create_index([("session_id", 1), ("agent_name", 1)])

        logger.info("MongoDB索引创建完成")

    def list_collections(self) -> list:
        """
        列出所有集合名称（同步）

        Returns:
            list: 集合名称列表
        """
        return self.sync_db.list_collection_names()


# 全局MongoDB客户端实例（单例模式）
_mongodb_client: Optional[MongoDBClient] = None


def get_mongodb_client() -> MongoDBClient:
    """
    获取全局MongoDB客户端实例（单例）

    Returns:
        MongoDBClient: MongoDB客户端实例
    """
    global _mongodb_client
    if _mongodb_client is None:
        raise RuntimeError("MongoDB客户端未初始化，请先调用init_mongodb_client()")
    return _mongodb_client


def init_mongodb_client(uri: str, database: str) -> MongoDBClient:
    """
    初始化全局MongoDB客户端实例

    Args:
        uri: MongoDB连接URI
        database: 数据库名称

    Returns:
        MongoDBClient: MongoDB客户端实例
    """
    global _mongodb_client
    if _mongodb_client is None:
        _mongodb_client = MongoDBClient(uri, database)
    return _mongodb_client
