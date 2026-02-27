"""
对话管理服务

功能：
1. 创建和管理对话会话
2. 添加和获取对话消息
3. 记录工具调用日志
4. 会话上下文管理（MongoDB持久化 + Redis缓存）
"""

import secrets
from datetime import datetime
from typing import Optional, List, Dict, Any
from loguru import logger

from ..database.mongodb import get_mongodb_client
from ..database.redis_client import get_redis_client


class DialogService:
    """对话管理服务类"""

    def __init__(self):
        """初始化服务"""
        self.mongodb = get_mongodb_client()
        self.redis = get_redis_client()
        self.sessions_collection = "dialog_sessions"
        self.messages_collection = "dialog_messages"
        self.tool_logs_collection = "tool_call_logs"
        logger.info("对话服务已初始化")

    async def create_session(self, user_id: int, initial_context: Optional[Dict[str, Any]] = None) -> str:
        """
        创建新对话会话

        Args:
            user_id: 用户ID
            initial_context: 初始上下文（可选）

        Returns:
            str: 会话ID
        """
        try:
            session_id = f"session_{secrets.token_urlsafe(16)}"

            session_doc = {
                "session_id": session_id,
                "user_id": user_id,
                "title": "",
                "context": initial_context or {},
                "message_count": 0,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "is_active": True
            }

            # 保存到MongoDB
            collection = self.mongodb.get_collection(self.sessions_collection)
            await collection.insert_one(session_doc)

            # 缓存到Redis（24小时过期）
            await self.redis.set(
                f"session:{session_id}",
                session_doc,
                ex=86400
            )

            # 清除用户会话列表缓存，确保下次拉取时获得最新数据
            cache_pattern = f"user:{user_id}:sessions*"
            cached_keys = await self.redis.keys(cache_pattern)
            if cached_keys:
                await self.redis.delete(*cached_keys)

            logger.info(f"对话会话已创建: {session_id} (用户: {user_id})")
            return session_id

        except Exception as e:
            logger.error(f"创建对话会话失败: {str(e)}")
            raise

    async def add_message(
        self,
        session_id: str,
        role: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        添加消息到会话

        Args:
            session_id: 会话ID
            role: 角色（user/assistant/system）
            content: 消息内容
            metadata: 元数据（可选）

        Returns:
            str: 消息ID
        """
        try:
            message_id = f"msg_{secrets.token_urlsafe(12)}"

            message_doc = {
                "message_id": message_id,
                "session_id": session_id,
                "role": role,
                "content": content,
                "metadata": metadata or {},
                "created_at": datetime.utcnow()
            }

            # 保存到MongoDB
            collection = self.mongodb.get_collection(self.messages_collection)
            await collection.insert_one(message_doc)

            # 更新会话的消息计数和时间
            sessions_collection = self.mongodb.get_collection(self.sessions_collection)
            await sessions_collection.update_one(
                {"session_id": session_id},
                {
                    "$inc": {"message_count": 1},
                    "$set": {"updated_at": datetime.utcnow()}
                }
            )

            # 更新Redis缓存中的消息列表
            await self.redis.lpush(f"session:{session_id}:messages", str(message_doc))
            await self.redis.expire(f"session:{session_id}:messages", 86400)

            # 清除会话上下文缓存
            await self.redis.delete(f"session:{session_id}:context")
            logger.debug(f"已清除会话上下文缓存: {session_id}")

            logger.debug(f"消息已添加: {message_id} (会话: {session_id}, 角色: {role})")
            return message_id

        except Exception as e:
            logger.error(f"添加消息失败: {str(e)}")
            raise

    async def get_session_context(
        self,
        session_id: str,
        max_messages: int = 20
    ) -> Dict[str, Any]:
        """
        获取会话上下文

        Args:
            session_id: 会话ID
            max_messages: 最大消息数量

        Returns:
            Dict: 会话上下文
        """
        try:
            # 先尝试从Redis获取完整上下文
            cached_context = await self.redis.get(f"session:{session_id}:context")
            if cached_context:
                import json
                try:
                    context = json.loads(cached_context)
                    # 限制消息数量
                    if len(context.get("messages", [])) > max_messages:
                        context["messages"] = context["messages"][-max_messages:]
                    logger.debug(f"从Redis缓存获取会话上下文: {session_id}")
                    return context
                except Exception as e:
                    logger.warning(f"解析Redis缓存失败: {str(e)}")

            # 从MongoDB获取会话信息
            sessions_collection = self.mongodb.get_collection(self.sessions_collection)
            session = await sessions_collection.find_one({"session_id": session_id})

            if not session:
                logger.warning(f"会话不存在: {session_id}")
                return None

            # 获取最近的消息
            messages_collection = self.mongodb.get_collection(self.messages_collection)
            cursor = messages_collection.find(
                {"session_id": session_id}
            ).sort("created_at", -1).limit(max_messages)

            messages = []
            async for msg in cursor:
                msg.pop("_id", None)
                if isinstance(msg.get("created_at"), datetime):
                    msg["created_at"] = msg["created_at"].isoformat()
                messages.append(msg)

            # 反转消息顺序（从旧到新）
            messages.reverse()

            # 移除MongoDB的_id字段
            session.pop("_id", None)
            if isinstance(session.get("created_at"), datetime):
                session["created_at"] = session["created_at"].isoformat()
            if isinstance(session.get("updated_at"), datetime):
                session["updated_at"] = session["updated_at"].isoformat()

            context = {
                **session,
                "messages": messages
            }

            # 缓存到Redis，过期时间24小时
            import json
            await self.redis.set(
                f"session:{session_id}:context",
                json.dumps(context, ensure_ascii=False),
                ex=86400
            )
            logger.debug(f"会话上下文已缓存到Redis: {session_id}")

            return context

        except Exception as e:
            logger.error(f"获取会话上下文失败: {str(e)}")
            raise

    async def log_tool_call(
        self,
        session_id: str,
        tool_name: str,
        input_params: Dict[str, Any],
        output_result: Any,
        execution_time_ms: float,
        status: str = "success"
    ) -> str:
        """
        记录工具调用日志

        Args:
            session_id: 会话ID
            tool_name: 工具名称
            input_params: 输入参数
            output_result: 输出结果
            execution_time_ms: 执行时间（毫秒）
            status: 状态（success/error）

        Returns:
            str: 日志ID
        """
        try:
            log_id = f"log_{secrets.token_urlsafe(12)}"

            log_doc = {
                "log_id": log_id,
                "session_id": session_id,
                "tool_name": tool_name,
                "input_params": input_params,
                "output_result": output_result,
                "execution_time_ms": execution_time_ms,
                "status": status,
                "created_at": datetime.utcnow()
            }

            # 保存到MongoDB
            collection = self.mongodb.get_collection(self.tool_logs_collection)
            await collection.insert_one(log_doc)

            logger.debug(f"工具调用已记录: {tool_name} (会话: {session_id}, 耗时: {execution_time_ms}ms)")
            return log_id

        except Exception as e:
            logger.error(f"记录工具调用失败: {str(e)}")
            raise

    async def list_user_sessions(
        self,
        user_id: int,
        is_active: Optional[bool] = None,
        limit: int = 20,
        skip: int = 0
    ) -> List[Dict[str, Any]]:
        """
        列出用户的对话会话

        Args:
            user_id: 用户ID
            is_active: 是否活跃（可选）
            limit: 返回数量限制
            skip: 跳过数量

        Returns:
            List[Dict]: 会话列表
        """
        try:
            # 构建缓存键
            cache_key = f"user:{user_id}:sessions"
            if is_active is not None:
                cache_key += f":active:{is_active}"
            cache_key += f":limit:{limit}:skip:{skip}"

            # 先尝试从Redis获取
            cached_sessions = await self.redis.get(cache_key)
            if cached_sessions:
                import json
                try:
                    sessions = json.loads(cached_sessions)
                    logger.debug(f"从Redis缓存获取用户会话列表: {user_id}")
                    return sessions
                except Exception as e:
                    logger.warning(f"解析Redis缓存失败: {str(e)}")

            # 从MongoDB获取
            query = {"user_id": user_id}
            if is_active is not None:
                query["is_active"] = is_active

            collection = self.mongodb.get_collection(self.sessions_collection)
            cursor = collection.find(query).sort("updated_at", -1).skip(skip).limit(limit)

            sessions = []
            async for doc in cursor:
                doc.pop("_id", None)
                if isinstance(doc.get("created_at"), datetime):
                    doc["created_at"] = doc["created_at"].isoformat()
                if isinstance(doc.get("updated_at"), datetime):
                    doc["updated_at"] = doc["updated_at"].isoformat()
                sessions.append(doc)

            # 缓存到Redis，过期时间1小时
            import json
            await self.redis.set(
                cache_key,
                json.dumps(sessions, ensure_ascii=False),
                ex=3600
            )
            logger.debug(f"用户会话列表已缓存到Redis: {user_id}")

            logger.debug(f"查询到 {len(sessions)} 个会话 (用户: {user_id})")
            return sessions

        except Exception as e:
            logger.error(f"列出用户会话失败: {str(e)}")
            raise

    async def update_session_title(self, session_id: str, user_id: int, title: str) -> bool:
        """
        更新会话标题

        Args:
            session_id: 会话ID
            user_id: 用户ID（权限验证）
            title: 新标题

        Returns:
            bool: 是否成功
        """
        try:
            sessions_collection = self.mongodb.get_collection(self.sessions_collection)
            result = await sessions_collection.update_one(
                {"session_id": session_id, "user_id": user_id},
                {"$set": {"title": title, "updated_at": datetime.utcnow()}}
            )

            if result.matched_count > 0:
                # 清除会话上下文缓存
                await self.redis.delete(f"session:{session_id}:context")
                # 清除用户会话列表缓存
                cache_pattern = f"user:{user_id}:sessions*"
                cached_keys = await self.redis.keys(cache_pattern)
                if cached_keys:
                    await self.redis.delete(*cached_keys)
                logger.info(f"会话标题已更新: {session_id} -> {title}")
                return True

            logger.warning(f"更新标题失败（会话不存在）: {session_id}")
            return False

        except Exception as e:
            logger.error(f"更新会话标题失败: {str(e)}")
            raise

    async def delete_session(self, session_id: str, user_id: int) -> bool:
        """
        删除会话

        Args:
            session_id: 会话ID
            user_id: 用户ID（权限验证）

        Returns:
            bool: 是否成功
        """
        try:
            # 删除MongoDB中的会话
            sessions_collection = self.mongodb.get_collection(self.sessions_collection)
            result = await sessions_collection.delete_one({
                "session_id": session_id,
                "user_id": user_id
            })

            if result.deleted_count > 0:
                # 删除相关消息
                messages_collection = self.mongodb.get_collection(self.messages_collection)
                await messages_collection.delete_many({"session_id": session_id})

                # 删除Redis缓存
                await self.redis.delete(f"session:{session_id}")
                await self.redis.delete(f"session:{session_id}:messages")
                await self.redis.delete(f"session:{session_id}:context")

                # 清除用户会话列表缓存（使用通配符删除所有相关缓存）
                cache_pattern = f"user:{user_id}:sessions:*"
                cached_keys = await self.redis.keys(cache_pattern)
                if cached_keys:
                    await self.redis.delete(*cached_keys)
                    logger.debug(f"已清除用户会话列表缓存: {user_id}, 共 {len(cached_keys)} 个缓存项")

                logger.info(f"会话已删除: {session_id}")
                return True
            else:
                logger.warning(f"删除失败（会话不存在）: {session_id}")
                return False

        except Exception as e:
            logger.error(f"删除会话失败: {str(e)}")
            raise

    async def get_session_tool_logs(
        self,
        session_id: str,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        获取会话的工具调用日志

        Args:
            session_id: 会话ID
            limit: 返回数量限制

        Returns:
            List[Dict]: 工具调用日志列表
        """
        try:
            collection = self.mongodb.get_collection(self.tool_logs_collection)
            cursor = collection.find(
                {"session_id": session_id}
            ).sort("created_at", -1).limit(limit)

            logs = []
            async for doc in cursor:
                doc.pop("_id", None)
                if isinstance(doc.get("created_at"), datetime):
                    doc["created_at"] = doc["created_at"].isoformat()
                logs.append(doc)

            return logs

        except Exception as e:
            logger.error(f"获取工具调用日志失败: {str(e)}")
            raise

    def delete_session_cache(
            self,
            user_id: int,
            is_active: Optional[bool] = None,
            limit: int = 20,
            skip: int = 0
    ):
        """
        删除原有的会话缓存
        """
        # 构建缓存键
        cache_key = f"user:{user_id}:sessions"
        if is_active is not None:
            cache_key += f":active:{is_active}"
        cache_key += f":limit:{limit}:skip:{skip}"

        self.redis.delete(cache_key)


# ========== 全局实例（单例模式） ==========

_dialog_service: Optional[DialogService] = None


def get_dialog_service() -> DialogService:
    """
    获取全局对话服务实例（单例）

    Returns:
        DialogService: 对话服务实例
    """
    global _dialog_service
    if _dialog_service is None:
        _dialog_service = DialogService()
    return _dialog_service
