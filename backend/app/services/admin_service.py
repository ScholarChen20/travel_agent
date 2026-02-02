"""
管理服务

功能：
1. 用户管理
2. 内容审核
3. 系统统计
4. 审计日志
5. 工具调用统计
"""

from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from loguru import logger

from ..database.mongodb import get_mongodb_client
from ..database.mysql import get_mysql_db
from ..database.models import User, UserProfile


class AdminService:
    """管理服务类"""

    def __init__(self):
        """初始化服务"""
        self.mongodb = get_mongodb_client()
        self.mysql_db = get_mysql_db()
        logger.info("管理服务已初始化")

    def list_users(
        self,
        role: Optional[str] = None,
        is_active: Optional[bool] = None,
        is_verified: Optional[bool] = None,
        limit: int = 50,
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        获取用户列表

        Args:
            role: 角色筛选
            is_active: 激活状态筛选
            is_verified: 验证状态筛选
            limit: 返回数量
            offset: 偏移量

        Returns:
            Dict: {total: int, users: List[Dict]}
        """
        try:
            with self.mysql_db.get_session() as session:
                query = session.query(User)

                # 应用筛选
                if role is not None:
                    query = query.filter(User.role == role)
                if is_active is not None:
                    query = query.filter(User.is_active == is_active)
                if is_verified is not None:
                    query = query.filter(User.is_verified == is_verified)

                # 获取总数
                total = query.count()

                # 分页
                users = query.order_by(User.created_at.desc()).offset(offset).limit(limit).all()

                # 格式化结果
                user_list = []
                for user in users:
                    user_list.append({
                        "id": user.id,
                        "username": user.username,
                        "email": user.email,
                        "role": user.role,
                        "is_active": user.is_active,
                        "is_verified": user.is_verified,
                        "avatar_url": user.avatar_url,
                        "created_at": user.created_at.isoformat() if user.created_at else None,
                        "last_login_at": user.last_login_at.isoformat() if user.last_login_at else None
                    })

                return {
                    "total": total,
                    "users": user_list
                }

        except Exception as e:
            logger.error(f"获取用户列表失败: {str(e)}")
            raise

    def update_user_status(self, user_id: int, is_active: bool) -> bool:
        """
        激活/禁用用户

        Args:
            user_id: 用户ID
            is_active: 激活状态

        Returns:
            bool: 是否成功
        """
        try:
            with self.mysql_db.get_session() as session:
                user = session.query(User).filter(User.id == user_id).first()

                if not user:
                    logger.warning(f"用户不存在: {user_id}")
                    return False

                user.is_active = is_active

                action = "激活" if is_active else "禁用"
                logger.info(f"用户已{action}: {user_id}")
                return True

        except Exception as e:
            logger.error(f"更新用户状态失败: {str(e)}")
            raise

    async def get_posts_for_moderation(
        self,
        status: str = "pending",
        limit: int = 50,
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        获取待审核内容

        Args:
            status: 审核状态（pending/approved/rejected）
            limit: 返回数量
            offset: 偏移量

        Returns:
            Dict: {total: int, posts: List[Dict]}
        """
        try:
            collection = self.mongodb.get_collection("social_posts")

            # 查询
            cursor = collection.find({
                "moderation_status": status
            }).sort("created_at", -1).skip(offset).limit(limit)

            posts = []
            async for post in cursor:
                post.pop("_id", None)
                if isinstance(post.get("created_at"), datetime):
                    post["created_at"] = post["created_at"].isoformat()
                if isinstance(post.get("updated_at"), datetime):
                    post["updated_at"] = post["updated_at"].isoformat()
                posts.append(post)

            # 获取总数
            total = await collection.count_documents({"moderation_status": status})

            return {
                "total": total,
                "posts": posts
            }

        except Exception as e:
            logger.error(f"获取待审核内容失败: {str(e)}")
            raise

    async def moderate_post(
        self,
        post_id: str,
        status: str,
        reason: Optional[str] = None
    ) -> bool:
        """
        审核帖子

        Args:
            post_id: 帖子ID
            status: 审核状态（approved/rejected）
            reason: 审核原因

        Returns:
            bool: 是否成功
        """
        try:
            collection = self.mongodb.get_collection("social_posts")

            update_data = {
                "moderation_status": status,
                "updated_at": datetime.utcnow()
            }

            if reason:
                update_data["moderation_reason"] = reason

            result = await collection.update_one(
                {"post_id": post_id},
                {"$set": update_data}
            )

            if result.modified_count > 0:
                logger.info(f"帖子已审核: {post_id} -> {status}")
                return True
            else:
                logger.warning(f"审核失败（帖子不存在）: {post_id}")
                return False

        except Exception as e:
            logger.error(f"审核帖子失败: {str(e)}")
            raise

    async def get_system_stats(self) -> Dict[str, Any]:
        """
        获取系统统计数据

        Returns:
            Dict: 系统统计
        """
        try:
            stats = {}

            # MySQL统计
            with self.mysql_db.get_session() as session:
                # 用户统计
                total_users = session.query(User).count()
                active_users = session.query(User).filter(User.is_active == True).count()
                verified_users = session.query(User).filter(User.is_verified == True).count()

                stats["users"] = {
                    "total": total_users,
                    "active": active_users,
                    "verified": verified_users
                }

            # MongoDB统计
            posts_collection = self.mongodb.get_collection("social_posts")
            plans_collection = self.mongodb.get_collection("travel_plans")
            sessions_collection = self.mongodb.get_collection("dialog_sessions")

            stats["posts"] = {
                "total": await posts_collection.count_documents({}),
                "approved": await posts_collection.count_documents({"moderation_status": "approved"}),
                "pending": await posts_collection.count_documents({"moderation_status": "pending"}),
                "rejected": await posts_collection.count_documents({"moderation_status": "rejected"})
            }

            stats["plans"] = {
                "total": await plans_collection.count_documents({})
            }

            stats["sessions"] = {
                "total": await sessions_collection.count_documents({}),
                "active": await sessions_collection.count_documents({"is_active": True})
            }

            return stats

        except Exception as e:
            logger.error(f"获取系统统计失败: {str(e)}")
            raise

    def get_audit_logs(
        self,
        user_id: Optional[int] = None,
        action: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100,
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        获取审计日志

        Args:
            user_id: 用户ID筛选
            action: 操作类型筛选
            start_date: 开始日期
            end_date: 结束日期
            limit: 返回数量
            offset: 偏移量

        Returns:
            Dict: {total: int, logs: List[Dict]}
        """
        try:
            # 注意：需要在MySQL中创建audit_logs表
            # 这里返回模拟数据，实际应该查询数据库
            return {
                "total": 0,
                "logs": []
            }

        except Exception as e:
            logger.error(f"获取审计日志失败: {str(e)}")
            raise

    async def get_tool_call_stats(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        获取工具调用统计

        Args:
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            Dict: 工具调用统计
        """
        try:
            collection = self.mongodb.get_collection("tool_call_logs")

            # 构建查询条件
            query = {}
            if start_date or end_date:
                query["created_at"] = {}
                if start_date:
                    query["created_at"]["$gte"] = start_date
                if end_date:
                    query["created_at"]["$lte"] = end_date

            # 聚合统计
            pipeline = [
                {"$match": query},
                {
                    "$group": {
                        "_id": "$tool_name",
                        "count": {"$sum": 1},
                        "avg_execution_time": {"$avg": "$execution_time_ms"},
                        "success_count": {
                            "$sum": {"$cond": [{"$eq": ["$status", "success"]}, 1, 0]}
                        },
                        "error_count": {
                            "$sum": {"$cond": [{"$eq": ["$status", "error"]}, 1, 0]}
                        }
                    }
                },
                {"$sort": {"count": -1}}
            ]

            result = await collection.aggregate(pipeline).to_list(length=100)

            stats = []
            for item in result:
                stats.append({
                    "tool_name": item["_id"],
                    "count": item["count"],
                    "avg_execution_time_ms": round(item["avg_execution_time"], 2),
                    "success_count": item["success_count"],
                    "error_count": item["error_count"],
                    "success_rate": round(item["success_count"] / item["count"] * 100, 2) if item["count"] > 0 else 0
                })

            return {
                "total_calls": sum(s["count"] for s in stats),
                "tools": stats
            }

        except Exception as e:
            logger.error(f"获取工具调用统计失败: {str(e)}")
            raise


# ========== 全局实例（单例模式） ==========

_admin_service: Optional[AdminService] = None


def get_admin_service() -> AdminService:
    """
    获取全局管理服务实例（单例）

    Returns:
        AdminService: 管理服务实例
    """
    global _admin_service
    if _admin_service is None:
        _admin_service = AdminService()
    return _admin_service
