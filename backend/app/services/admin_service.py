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
        username: Optional[str] = None,
        email: Optional[str] = None,
        role: Optional[str] = None,
        is_active: Optional[bool] = None,
        is_verified: Optional[bool] = None,
        limit: int = 50,
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        获取用户列表

        Args:
            username: 用户名搜索
            email: 邮箱搜索
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
                if username:
                    query = query.filter(User.username.ilike(f"%{username}%"))
                if email:
                    query = query.filter(User.email.ilike(f"%{email}%"))
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
                        "feishu_open_id": user.feishu_open_id,
                        "feishu_union_id": user.feishu_union_id,
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

    async def list_comments(
        self,
        content: Optional[str] = None,
        post_id: Optional[str] = None,
        user_id: Optional[int] = None,
        limit: int = 50,
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        获取评论列表

        Args:
            content: 评论内容搜索
            post_id: 帖子ID筛选
            user_id: 用户ID筛选
            limit: 返回数量
            offset: 偏移量

        Returns:
            Dict: {total: int, comments: List[Dict]}
        """
        try:
            collection = self.mongodb.get_collection("social_comments")

            query = {}
            if content:
                query["content"] = {"$regex": content, "$options": "i"}
            if post_id:
                query["post_id"] = post_id
            if user_id is not None:
                query["user_id"] = user_id

            cursor = collection.find(query).sort("created_at", -1).skip(offset).limit(limit)

            comments = []
            async for comment in cursor:
                comment.pop("_id", None)
                if isinstance(comment.get("created_at"), datetime):
                    comment["created_at"] = comment["created_at"].isoformat()
                comments.append(comment)

            total = await collection.count_documents(query)

            return {
                "total": total,
                "comments": comments
            }

        except Exception as e:
            logger.error(f"获取评论列表失败: {str(e)}")
            raise

    async def delete_comment(self, comment_id: str) -> bool:
        """
        删除评论

        Args:
            comment_id: 评论ID

        Returns:
            bool: 是否成功
        """
        try:
            collection = self.mongodb.get_collection("social_comments")

            result = await collection.delete_one({"comment_id": comment_id})

            if result.deleted_count > 0:
                logger.info(f"评论已删除: {comment_id}")
                return True
            else:
                logger.warning(f"删除失败（评论不存在）: {comment_id}")
                return False

        except Exception as e:
            logger.error(f"删除评论失败: {str(e)}")
            raise

    async def get_posts_for_moderation(
        self,
        keyword: Optional[str] = None,
        status: str = "pending",
        limit: int = 50,
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        获取待审核内容

        Args:
            keyword: 关键词搜索
            status: 审核状态（pending/approved/rejected）
            limit: 返回数量
            offset: 偏移量

        Returns:
            Dict: {total: int, posts: List[Dict]}
        """
        try:
            collection = self.mongodb.get_collection("social_posts")

            query = {"moderation_status": status}
            if keyword:
                query["$or"] = [
                    {"title": {"$regex": keyword, "$options": "i"}},
                    {"content": {"$regex": keyword, "$options": "i"}}
                ]
            cursor = collection.find(query).sort("created_at", -1).skip(offset).limit(limit)

            posts = []
            async for post in cursor:
                post.pop("_id", None)
                if isinstance(post.get("created_at"), datetime):
                    post["created_at"] = post["created_at"].isoformat()
                if isinstance(post.get("updated_at"), datetime):
                    post["updated_at"] = post["updated_at"].isoformat()
                posts.append(post)

            total = await collection.count_documents(query)

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
                "updated_at": datetime.now()
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

    async def get_visualization_data(self) -> Dict[str, Any]:
        """
        获取可视化图表数据

        Returns:
            Dict: 可视化数据
        """
        try:
            data = {}
            
            # 最近7天用户注册趋势
            data["user_trend"] = await self._get_user_registration_trend(7)
            
            # 最近7天帖子发布趋势
            data["post_trend"] = await self._get_post_trend(7)
            
            # 内容审核状态分布
            data["moderation_distribution"] = await self._get_moderation_distribution()
            
            # 用户活跃度分布
            data["user_activity"] = await self._get_user_activity_distribution()
            
            # 帖子类型分布
            data["content_type_distribution"] = await self._get_content_type_distribution()
            
            # Top热门内容
            data["top_content"] = await self._get_top_content(5)
            
            # 互动统计
            data["interaction_stats"] = await self._get_interaction_stats()

            return data

        except Exception as e:
            logger.error(f"获取可视化数据失败: {str(e)}")
            raise

    async def _get_user_registration_trend(self, days: int) -> List[Dict[str, Any]]:
        """获取用户注册趋势"""
        try:
            from datetime import datetime, timedelta
            
            trend = []
            for i in range(days - 1, -1, -1):
                date = datetime.now() - timedelta(days=i)
                date_str = date.strftime("%Y-%m-%d")
                next_date = (date + timedelta(days=1)).strftime("%Y-%m-%d")
                
                with self.mysql_db.get_session() as session:
                    count = session.query(User).filter(
                        User.created_at >= date_str,
                        User.created_at < next_date
                    ).count()
                
                trend.append({
                    "date": date_str,
                    "count": count
                })
            
            return trend
        except Exception as e:
            logger.error(f"获取用户注册趋势失败: {str(e)}")
            return []

    async def _get_post_trend(self, days: int) -> List[Dict[str, Any]]:
        """获取帖子发布趋势（从MongoDB获取）"""
        try:
            from datetime import datetime, timedelta
            
            posts_collection = self.mongodb.get_collection("social_posts")
            
            trend = []
            now = datetime.now()
            today = now.date()
            
            logger.info(f"开始查询最近{days}天的帖子趋势, 当前日期: {today}")
            
            # 先查看数据库中帖子的创建时间
            sample_posts = await posts_collection.find(
                {"created_at": {"$exists": True}},
                {"created_at": 1}
            ).limit(5).to_list(5)
            logger.info(f"MongoDB帖子创建时间示例: {[p.get('created_at') for p in sample_posts]}")

            
            # 使用完整的日期时间范围查询
            for i in range(days - 1, -1, -1):
                target_date = today - timedelta(days=i)
                # 当天开始 00:00:00
                start_datetime = datetime(target_date.year, target_date.month, target_date.day, 0, 0, 0)
                # 次天开始 00:00:00
                end_datetime = datetime(target_date.year, target_date.month, target_date.day, 23, 59, 59)
                
                count = await posts_collection.count_documents({
                    "created_at": {
                        "$gte": start_datetime,
                        "$lte": end_datetime
                    }
                })
                
                trend.append({
                    "date": target_date.strftime("%Y-%m-%d"),
                    "count": count
                })
                # logger.info(f"日期 {target_date}, 范围 {start_datetime} - {end_datetime}, 帖子数量: {count}")
            
            return trend
        except Exception as e:
            logger.error(f"获取帖子发布趋势失败: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return []

    async def _get_moderation_distribution(self) -> List[Dict[str, Any]]:
        """获取内容审核状态分布（从MongoDB获取）"""
        try:
            posts_collection = self.mongodb.get_collection("social_posts")
            
            pipeline = [
                {"$group": {"_id": "$moderation_status", "count": {"$sum": 1}}}
            ]
            
            results = await posts_collection.aggregate(pipeline).to_list(length=100)
            
            distribution = []
            status_map = {
                "approved": {"name": "已通过", "color": "#52c41a"},
                "pending": {"name": "待审核", "color": "#faad14"},
                "rejected": {"name": "已拒绝", "color": "#ff4d4f"},
                None: {"name": "未审核", "color": "#d9d9d9"}
            }
            
            for item in results:
                status = item["_id"] if item["_id"] else None
                info = status_map.get(status, {"name": str(status), "color": "#1890ff"})
                distribution.append({
                    "name": info["name"],
                    "value": item["count"],
                    "color": info["color"]
                })
            
            logger.info(f"审核状态分布: {distribution}")
            return distribution
        except Exception as e:
            logger.error(f"获取审核状态分布失败: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return []

    async def _get_user_activity_distribution(self) -> Dict[str, Any]:
        """获取用户活跃度分布"""
        try:
            posts_collection = self.mongodb.get_collection("social_posts")
            plans_collection = self.mongodb.get_collection("travel_plans")
            
            pipeline = [
                {"$group": {"_id": "$user_id", "post_count": {"$sum": 1}}},
                {"$bucket": {
                    "groupBy": "$post_count",
                    "boundaries": [0, 1, 3, 5, 10, float("inf")],
                    "default": "other",
                    "output": {"count": {"$sum": 1}}
                }}
            ]
            
            post_activity = await posts_collection.aggregate(pipeline).to_list(length=100)
            
            pipeline = [
                {"$group": {"_id": "$user_id", "plan_count": {"$sum": 1}}},
                {"$bucket": {
                    "groupBy": "$plan_count",
                    "boundaries": [0, 1, 3, 5, 10, float("inf")],
                    "default": "other",
                    "output": {"count": {"$sum": 1}}
                }}
            ]
            
            plan_activity = await plans_collection.aggregate(pipeline).to_list(length=100)
            
            return {
                "post_activity": post_activity,
                "plan_activity": plan_activity
            }
        except Exception as e:
            logger.error(f"获取用户活跃度分布失败: {str(e)}")
            return {"post_activity": [], "plan_activity": []}

    async def _get_content_type_distribution(self) -> List[Dict[str, Any]]:
        """获取内容类型分布（从MongoDB帖子标签中统计）"""
        try:
            from collections import Counter
            
            posts_collection = self.mongodb.get_collection("social_posts")
            
            pipeline = [
                {"$match": {"tags": {"$exists": True, "$ne": []}}},
                {"$project": {"tags": 1}}
            ]
            
            results = await posts_collection.aggregate(pipeline).to_list(length=1000)
            
            tag_counts = Counter()
            for item in results:
                tags = item.get("tags", [])
                for tag in tags:
                    if isinstance(tag, str):
                        tag_counts[tag] += 1
                    elif isinstance(tag, dict) and "name" in tag:
                        tag_counts[tag["name"]] += 1
            
            top_tags = tag_counts.most_common(10)
            
            colors = ["#5B8FF9", "#5AD8A6", "#5D7092", "#F6BD16", "#E8684A", "#6DC8EC", "#9270CA", "#FF9D4D", "#269A99", "#FF99C3"]
            distribution = []
            
            for i, (name, count) in enumerate(top_tags):
                distribution.append({
                    "name": name,
                    "value": count,
                    "color": colors[i % len(colors)]
                })
            
            logger.info(f"标签分布统计: {distribution}")
            return distribution
        except Exception as e:
            logger.error(f"获取内容类型分布失败: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return []

    async def _get_top_content(self, limit: int) -> List[Dict[str, Any]]:
        """获取热门内容"""
        try:
            posts_collection = self.mongodb.get_collection("social_posts")
            
            pipeline = [
                {"$match": {"moderation_status": "approved"}},
                {"$sort": {"like_count": -1, "view_count": -1}},
                {"$limit": limit},
                {"$project": {
                    "post_id": 1,
                    "title": 1,
                    "content": 1,
                    "author": 1,
                    "like_count": 1,
                    "view_count": 1,
                    "comment_count": 1,
                    "created_at": 1
                }}
            ]
            
            results = await posts_collection.aggregate(pipeline).to_list(length=limit)
            
            top_content = []
            for item in results:
                top_content.append({
                    "post_id": item.get("post_id"),
                    "title": item.get("title", "")[:30],
                    "author": item.get("author", "未知"),
                    "likes": item.get("like_count", 0),
                    "views": item.get("view_count", 0),
                    "comments": item.get("comment_count", 0),
                    "created_at": item.get("created_at")
                })
            
            return top_content
        except Exception as e:
            logger.error(f"获取热门内容失败: {str(e)}")
            return []

    async def _get_interaction_stats(self) -> Dict[str, Any]:
        """获取互动统计数据"""
        try:
            posts_collection = self.mongodb.get_collection("social_posts")
            comments_collection = self.mongodb.get_collection("social_comments")
            
            total_likes = 0
            total_views = 0
            total_comments = 0
            
            posts = await posts_collection.find(
                {"moderation_status": "approved"},
                {"like_count": 1, "view_count": 1}
            ).to_list(length=1000)
            
            for post in posts:
                total_likes += post.get("like_count", 0)
                total_views += post.get("view_count", 0)
            
            comments_count = await comments_collection.count_documents({})
            total_comments = comments_count
            
            return {
                "total_likes": total_likes,
                "total_views": total_views,
                "total_comments": total_comments,
                "avg_likes_per_post": round(total_likes / len(posts), 1) if posts else 0,
                "avg_views_per_post": round(total_views / len(posts), 1) if posts else 0
            }
        except Exception as e:
            logger.error(f"获取互动统计失败: {str(e)}")
            return {
                "total_likes": 0,
                "total_views": 0,
                "total_comments": 0,
                "avg_likes_per_post": 0,
                "avg_views_per_post": 0
            }

    def get_audit_logs(
        self,
        resource_id: Optional[str] = None,
        user_id: Optional[int] = None,
        action: Optional[str] = None,
        resource: Optional[str] = None,
        method: Optional[str] = None,
        path_keyword: Optional[str] = None,
        status_code: Optional[int] = None,
        response_status: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100,
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        获取审计日志

        Args:
            resource_id: 资源ID搜索
            user_id: 用户ID筛选
            action: 操作类型筛选
            resource: 资源类型筛选
            method: HTTP方法筛选 (GET/POST/PUT/DELETE)
            path_keyword: 请求路径模糊匹配
            status_code: 响应状态码筛选（传入 2/4/5 匹配对应 2xx/4xx/5xx）
            response_status: 响应结果筛选 (success/error)
            start_date: 开始日期
            end_date: 结束日期
            limit: 返回数量
            offset: 偏移量

        Returns:
            Dict: {total: int, logs: List[Dict]}
        """
        try:
            from ..database.models import AuditLog

            with self.mysql_db.get_session() as session:
                query = session.query(AuditLog)

                if resource_id:
                    query = query.filter(AuditLog.resource_id.ilike(f"%{resource_id}%"))
                if user_id is not None:
                    query = query.filter(AuditLog.user_id == user_id)
                if action:
                    query = query.filter(AuditLog.action == action)
                if resource:
                    query = query.filter(AuditLog.resource == resource)
                if method:
                    query = query.filter(AuditLog.method == method.upper())
                if path_keyword:
                    query = query.filter(AuditLog.path.ilike(f"%{path_keyword}%"))
                if status_code is not None:
                    if status_code < 10:
                        lower = status_code * 100
                        query = query.filter(AuditLog.status_code.between(lower, lower + 99))
                    else:
                        query = query.filter(AuditLog.status_code == status_code)
                if response_status:
                    query = query.filter(AuditLog.response_status == response_status)
                if start_date:
                    query = query.filter(AuditLog.created_at >= start_date)
                if end_date:
                    query = query.filter(AuditLog.created_at <= end_date)

                total = query.count()

                logs = query.order_by(AuditLog.created_at.desc()).offset(offset).limit(limit).all()

                log_list = []
                for log in logs:
                    log_list.append({
                        "id": log.id,
                        "user_id": log.user_id,
                        "username": log.username,
                        "action": log.action,
                        "resource": log.resource,
                        "resource_id": log.resource_id,
                        "details": log.details,
                        "ip_address": log.ip_address,
                        "user_agent": log.user_agent,
                        "method": log.method,
                        "path": log.path,
                        "status_code": log.status_code,
                        "duration_ms": log.duration_ms,
                        "response_status": log.response_status,
                        "created_at": log.created_at.isoformat() if log.created_at else None
                    })

                return {
                    "total": total,
                    "logs": log_list
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
