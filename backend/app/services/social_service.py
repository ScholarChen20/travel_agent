"""
社交服务

功能：
1. 创建和管理帖子
2. 内容审核
3. Feed流生成
4. 点赞和评论
5. 关注系统
6. 标签管理
"""

import secrets
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from loguru import logger
from sqlalchemy import text

from ..database.mongodb import get_mongodb_client
from ..database.mysql import get_mysql_db


class SocialService:
    """社交服务类"""

    def __init__(self):
        """初始化服务"""
        self.mongodb = get_mongodb_client()
        self.mysql_db = get_mysql_db()
        from ..database.redis_client import get_redis_client
        self.redis = get_redis_client()
        self.posts_collection = "social_posts"
        self.comments_collection = "social_comments"
        self.likes_collection = "social_likes"
        self.follows_collection = "social_follows"

        # 内容审核黑名单
        self.blacklist_keywords = [
            "广告", "spam", "诈骗", "违法", "色情", "赌博"
        ]

        logger.info("社交服务已初始化")

    async def create_post(
        self,
        user_id: int,
        title: str,
        content: str,
        media_urls: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        location: Optional[str] = None,
        trip_plan_id: Optional[str] = None
    ) -> str:
        """
        创建帖子

        Args:
            user_id: 用户ID
            title: 标题
            content: 内容
            media_urls: 媒体文件URL列表
            tags: 标签列表
            location: 位置
            trip_plan_id: 关联的旅行计划ID

        Returns:
            str: 帖子ID
        """
        try:
            # 内容审核
            moderation_result = await self.moderate_content(content)

            post_id = f"post_{secrets.token_urlsafe(16)}"

            post_doc = {
                "post_id": post_id,
                "user_id": user_id,
                "title": title,
                "content": content,
                "media_urls": media_urls or [],
                "tags": tags or [],
                "location": location,
                "trip_plan_id": trip_plan_id,
                "moderation_status": moderation_result["status"],
                "like_count": 0,
                "comment_count": 0,
                "view_count": 0,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }

            # 保存到MongoDB
            collection = self.mongodb.get_collection(self.posts_collection)
            await collection.insert_one(post_doc)

            logger.info(f"帖子已创建: {post_id} (用户: {user_id}, 审核: {moderation_result['status']})")

            # 清除相关缓存
            # 1. 清除用户的帖子列表缓存
            user_posts_pattern = f"user:{user_id}:posts:*"
            user_posts_keys = await self.redis.keys(user_posts_pattern)
            if user_posts_keys:
                await self.redis.delete(*user_posts_keys)
                logger.debug(f"已清除用户帖子列表缓存: {user_id}, 共 {len(user_posts_keys)} 个缓存项")

            # 2. 清除用户的Feed流缓存（只清除当前用户的，避免影响其他用户）
            user_feed_pattern = f"user:{user_id}:feed:*"
            user_feed_keys = await self.redis.keys(user_feed_pattern)
            if user_feed_keys:
                await self.redis.delete(*user_feed_keys)
                logger.debug(f"已清除用户Feed流缓存: {user_id}, 共 {len(user_feed_keys)} 个缓存项")

            # 3. 清除热门标签缓存
            popular_tags_pattern = f"popular_tags:*"
            popular_tags_keys = await self.redis.keys(popular_tags_pattern)
            if popular_tags_keys:
                await self.redis.delete(*popular_tags_keys)
                logger.debug(f"已清除热门标签缓存，共 {len(popular_tags_keys)} 个缓存项")

            # 4. 清除标签帖子缓存（如果有标签）
            if tags:
                for tag in tags:
                    tag_posts_pattern = f"tag:{tag}:posts:*"
                    tag_posts_keys = await self.redis.keys(tag_posts_pattern)
                    if tag_posts_keys:
                        await self.redis.delete(*tag_posts_keys)
                        logger.debug(f"已清除标签帖子缓存: {tag}, 共 {len(tag_posts_keys)} 个缓存项")

            return post_id

        except Exception as e:
            logger.error(f"创建帖子失败: {str(e)}")
            raise

    async def moderate_content(self, content: str) -> Dict[str, Any]:
        """
        内容审核

        Args:
            content: 待审核内容

        Returns:
            Dict: 审核结果 {status: approved/rejected, reason: str}
        """
        try:
            # 关键词过滤
            content_lower = content.lower()
            for keyword in self.blacklist_keywords:
                if keyword in content_lower:
                    return {
                        "status": "rejected",
                        "reason": f"包含违禁词: {keyword}"
                    }

            # 长度检查（评论至少1个字符，帖子至少10个字符）
            min_length = 1  # 评论可以很短
            if len(content) < min_length:
                return {
                    "status": "rejected",
                    "reason": "内容不能为空"
                }

            return {
                "status": "approved",
                "reason": "审核通过"
            }

        except Exception as e:
            logger.error(f"内容审核失败: {str(e)}")
            return {
                "status": "pending",
                "reason": "审核异常"
            }

    async def get_feed(
        self,
        user_id: int,
        limit: int = 20,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        获取个性化Feed流

        混合策略：
        - 50% 关注用户的最新内容
        - 30% 热门内容（点赞数高）
        - 20% 推荐内容（基于用户偏好）

        Args:
            user_id: 用户ID
            limit: 返回数量
            offset: 偏移量

        Returns:
            List[Dict]: 帖子列表
        """
        try:
            # 构建缓存键
            cache_key = f"user:{user_id}:feed:limit:{limit}:offset:{offset}"

            # 先尝试从Redis获取
            cached_feed = await self.redis.get(cache_key)
            if cached_feed:
                import json
                try:
                    feed = json.loads(cached_feed)
                    logger.debug(f"从Redis缓存获取个性化Feed流: {user_id}")
                    return feed
                except Exception as e:
                    logger.warning(f"解析Redis缓存失败: {str(e)}")

            # 从MongoDB获取
            collection = self.mongodb.get_collection(self.posts_collection)

            # 获取关注的用户列表
            following_ids = await self._get_following_ids(user_id)

            # 计算各部分数量
            following_limit = int(limit * 0.5)
            popular_limit = int(limit * 0.3)
            recommended_limit = limit - following_limit - popular_limit

            posts = []

            # 1. 关注用户的最新内容 (50%)
            if following_ids:
                following_cursor = collection.find({
                    "user_id": {"$in": following_ids},
                    "moderation_status": "approved"
                }).sort("created_at", -1).limit(following_limit)

                async for post in following_cursor:
                    formatted_post = await self._format_post(post, user_id)
                    posts.append(formatted_post)

            # 2. 热门内容 (30%)
            # 时间衰减：只看最近7天的内容
            week_ago = datetime.utcnow() - timedelta(days=7)
            popular_cursor = collection.find({
                "moderation_status": "approved",
                "created_at": {"$gte": week_ago}
            }).sort("like_count", -1).limit(popular_limit)

            async for post in popular_cursor:
                formatted_post = await self._format_post(post, user_id)
                posts.append(formatted_post)

            # 3. 推荐内容 (20%)
            # 基于用户偏好（简化版：随机推荐）
            recommended_cursor = collection.find({
                "moderation_status": "approved"
            }).sort("created_at", -1).limit(recommended_limit)

            async for post in recommended_cursor:
                formatted_post = await self._format_post(post, user_id)
                posts.append(formatted_post)

            # 去重 - 基于post_id
            seen_post_ids = set()
            unique_posts = []
            for post in posts:
                if post['id'] not in seen_post_ids:
                    seen_post_ids.add(post['id'])
                    unique_posts.append(post)

            # 按时间排序
            unique_posts.sort(key=lambda x: x["created_at"], reverse=True)

            # 应用分页
            feed_result = unique_posts[:limit]

            # 缓存到Redis，过期时间10分钟
            import json
            await self.redis.set(cache_key, json.dumps(feed_result, ensure_ascii=False), ex=600
            )
            logger.debug(f"个性化Feed流已缓存到Redis: {user_id}")

            return feed_result

        except Exception as e:
            logger.error(f"获取Feed流失败: {str(e)}")
            raise

    async def like_post(self, user_id: int, post_id: str) -> bool:
        """
        点赞/取消点赞

        Args:
            user_id: 用户ID
            post_id: 帖子ID

        Returns:
            bool: True=已点赞, False=已取消
        """
        try:
            likes_collection = self.mongodb.get_collection(self.likes_collection)
            posts_collection = self.mongodb.get_collection(self.posts_collection)

            # 检查是否已点赞
            existing_like = await likes_collection.find_one({
                "user_id": user_id,
                "post_id": post_id
            })

            if existing_like:
                # 取消点赞
                await likes_collection.delete_one({
                    "user_id": user_id,
                    "post_id": post_id
                })

                # 减少点赞数
                await posts_collection.update_one(
                    {"post_id": post_id},
                    {"$inc": {"like_count": -1}}
                )

                logger.debug(f"取消点赞: {post_id} (用户: {user_id})")
            else:
                # 点赞
                like_doc = {
                    "like_id": f"like_{secrets.token_urlsafe(12)}",
                    "user_id": user_id,
                    "post_id": post_id,
                    "created_at": datetime.utcnow()
                }
                await likes_collection.insert_one(like_doc)

                # 增加点赞数
                await posts_collection.update_one(
                    {"post_id": post_id},
                    {"$inc": {"like_count": 1}}
                )

                logger.debug(f"点赞: {post_id} (用户: {user_id})")

            # 清除相关缓存
            # 1. 清除帖子详情缓存
            await self.redis.delete(f"post:{post_id}:detail")
            logger.debug(f"已清除帖子详情缓存: {post_id}")

            # 2. 清除用户的Feed流缓存（只清除当前用户的，避免影响其他用户）
            user_feed_pattern = f"user:{user_id}:feed:*"
            user_feed_keys = await self.redis.keys(user_feed_pattern)
            if user_feed_keys:
                await self.redis.delete(*user_feed_keys)
                logger.debug(f"已清除用户Feed流缓存: {user_id}, 共 {len(user_feed_keys)} 个缓存项")

            # 3. 尝试获取帖子的用户ID，清除其帖子列表缓存
            try:
                post = await posts_collection.find_one({"post_id": post_id}, {"user_id": 1})
                if post and "user_id" in post:
                    post_user_id = post["user_id"]
                    user_posts_pattern = f"user:{post_user_id}:posts:*"
                    user_posts_keys = await self.redis.keys(user_posts_pattern)
                    if user_posts_keys:
                        await self.redis.delete(*user_posts_keys)
                        logger.debug(f"已清除帖子作者的帖子列表缓存: {post_user_id}, 共 {len(user_posts_keys)} 个缓存项")
            except Exception as e:
                logger.error(f"获取帖子用户ID失败: {str(e)}")

            # 4. 尝试获取帖子的标签，清除标签帖子缓存
            try:
                post = await posts_collection.find_one({"post_id": post_id}, {"tags": 1})
                if post and "tags" in post:
                    tags = post["tags"]
                    for tag in tags:
                        tag_posts_pattern = f"tag:{tag}:posts:*"
                        tag_posts_keys = await self.redis.keys(tag_posts_pattern)
                        if tag_posts_keys:
                            await self.redis.delete(*tag_posts_keys)
                            logger.debug(f"已清除标签帖子缓存: {tag}, 共 {len(tag_posts_keys)} 个缓存项")
            except Exception as e:
                logger.error(f"获取帖子标签失败: {str(e)}")

            return not existing_like

        except Exception as e:
            logger.error(f"点赞操作失败: {str(e)}")
            raise

    async def comment_on_post(
        self,
        user_id: int,
        post_id: str,
        content: str,
        parent_id: Optional[str] = None
    ) -> str:
        """
        发表评论

        Args:
            user_id: 用户ID
            post_id: 帖子ID
            content: 评论内容
            parent_id: 父评论ID（回复评论时使用）

        Returns:
            str: 评论ID
        """
        try:
            # 内容审核
            moderation_result = await self.moderate_content(content)

            if moderation_result["status"] == "rejected":
                raise ValueError(f"评论审核失败: {moderation_result['reason']}")

            comment_id = f"comment_{secrets.token_urlsafe(12)}"

            comment_doc = {
                "comment_id": comment_id,
                "post_id": post_id,
                "user_id": user_id,
                "content": content,
                "parent_id": parent_id,
                "like_count": 0,
                "created_at": datetime.utcnow()
            }

            # 保存评论
            comments_collection = self.mongodb.get_collection(self.comments_collection)
            await comments_collection.insert_one(comment_doc)

            # 增加帖子评论数
            posts_collection = self.mongodb.get_collection(self.posts_collection)
            await posts_collection.update_one(
                {"post_id": post_id},
                {"$inc": {"comment_count": 1}}
            )

            logger.info(f"评论已发表: {comment_id} (帖子: {post_id}, 用户: {user_id})")
            return comment_id

        except Exception as e:
            logger.error(f"发表评论失败: {str(e)}")
            raise

    async def follow_user(self, follower_id: int, following_id: int) -> bool:
        """
        关注/取消关注用户

        Args:
            follower_id: 关注者ID
            following_id: 被关注者ID

        Returns:
            bool: True=已关注, False=已取消
        """
        try:
            if follower_id == following_id:
                raise ValueError("不能关注自己")

            follows_collection = self.mongodb.get_collection(self.follows_collection)

            # 检查是否已关注
            existing_follow = await follows_collection.find_one({
                "follower_id": follower_id,
                "following_id": following_id
            })

            if existing_follow:
                # 取消关注
                await follows_collection.delete_one({
                    "follower_id": follower_id,
                    "following_id": following_id
                })

                logger.info(f"取消关注: {follower_id} -> {following_id}")
                return False
            else:
                # 关注
                follow_doc = {
                    "follow_id": f"follow_{secrets.token_urlsafe(12)}",
                    "follower_id": follower_id,
                    "following_id": following_id,
                    "created_at": datetime.utcnow()
                }
                await follows_collection.insert_one(follow_doc)

                logger.info(f"关注: {follower_id} -> {following_id}")
                return True

        except Exception as e:
            logger.error(f"关注操作失败: {str(e)}")
            raise

    async def get_user_posts(
        self,
        user_id: int,
        limit: int = 20,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        获取用户发布的帖子

        Args:
            user_id: 用户ID
            limit: 返回数量
            offset: 偏移量

        Returns:
            List[Dict]: 帖子列表
        """
        try:
            # 构建缓存键
            cache_key = f"user:{user_id}:posts:limit:{limit}:offset:{offset}"

            # 先尝试从Redis获取
            cached_posts = await self.redis.get(cache_key)
            if cached_posts:
                import json
                try:
                    posts = json.loads(cached_posts)
                    logger.debug(f"从Redis缓存获取用户帖子: {user_id}")
                    return posts
                except Exception as e:
                    logger.warning(f"解析Redis缓存失败: {str(e)}")

            # 从MongoDB获取
            collection = self.mongodb.get_collection(self.posts_collection)

            cursor = collection.find({
                "user_id": user_id,
                "moderation_status": "approved"
            }).sort("created_at", -1).skip(offset).limit(limit)

            posts = []
            async for post in cursor:
                formatted_post = await self._format_post(post, None)
                posts.append(formatted_post)

            # 缓存到Redis，过期时间1小时
            import json
            await self.redis.set(cache_key, json.dumps(posts, ensure_ascii=False), ex=3600
            )
            logger.debug(f"用户帖子已缓存到Redis: {user_id}")

            return posts

        except Exception as e:
            logger.error(f"获取用户帖子失败: {str(e)}")
            raise

    async def get_popular_tags(self, limit: int = 20) -> List[Dict[str, Any]]:
        """
        获取热门标签

        Args:
            limit: 返回数量

        Returns:
            List[Dict]: 标签列表 [{tag: str, count: int}]
        """
        try:
            # 构建缓存键
            cache_key = f"popular_tags:limit:{limit}"

            # 先尝试从Redis获取
            cached_tags = await self.redis.get(cache_key)
            if cached_tags:
                import json
                try:
                    tags = json.loads(cached_tags)
                    logger.debug(f"从Redis缓存获取热门标签")
                    return tags
                except Exception as e:
                    logger.warning(f"解析Redis缓存失败: {str(e)}")

            # 从MongoDB获取
            collection = self.mongodb.get_collection(self.posts_collection)

            # 聚合查询统计标签
            pipeline = [
                {"$match": {"moderation_status": "approved"}},
                {"$unwind": "$tags"},
                {"$group": {
                    "_id": "$tags",
                    "count": {"$sum": 1}
                }},
                {"$sort": {"count": -1}},
                {"$limit": limit}
            ]

            result = await collection.aggregate(pipeline).to_list(length=limit)

            tags = [
                {"tag": item["_id"], "count": item["count"]}
                for item in result
            ]

            # 缓存到Redis，过期时间30分钟
            import json
            await self.redis.set(cache_key, json.dumps(tags, ensure_ascii=False), ex=1800
            )
            logger.debug(f"热门标签已缓存到Redis")

            return tags

        except Exception as e:
            logger.error(f"获取热门标签失败: {str(e)}")
            raise

    async def get_post_by_id(self, post_id: str) -> Optional[Dict[str, Any]]:
        """
        获取帖子详情

        Args:
            post_id: 帖子ID

        Returns:
            Dict: 帖子详情
        """
        try:
            # 构建缓存键
            cache_key = f"post:{post_id}:detail"

            # 先尝试从Redis获取
            cached_post = await self.redis.get(cache_key)
            if cached_post:
                import json
                try:
                    post = json.loads(cached_post)
                    logger.debug(f"从Redis缓存获取帖子详情: {post_id}")
                    
                    # 异步更新浏览数，不阻塞返回
                    async def update_view_count():
                        try:
                            collection = self.mongodb.get_collection(self.posts_collection)
                            await collection.update_one(
                                {"post_id": post_id},
                                {"$inc": {"view_count": 1}}
                            )
                            # 清除缓存，以便下次获取时更新浏览数
                            await self.redis.delete(cache_key)
                        except Exception as e:
                            logger.error(f"更新浏览数失败: {str(e)}")
                    
                    import asyncio
                    asyncio.create_task(update_view_count())
                    
                    return post
                except Exception as e:
                    logger.warning(f"解析Redis缓存失败: {str(e)}")

            # 从MongoDB获取
            collection = self.mongodb.get_collection(self.posts_collection)
            post = await collection.find_one({"post_id": post_id})

            if not post:
                return None

            # 增加浏览数
            await collection.update_one(
                {"post_id": post_id},
                {"$inc": {"view_count": 1}}
            )

            # 格式化帖子
            formatted_post = await self._format_post(post, None)

            # 缓存到Redis，过期时间1小时
            import json
            await self.redis.set(cache_key, json.dumps(formatted_post, ensure_ascii=False), ex=3600
            )
            logger.debug(f"帖子详情已缓存到Redis: {post_id}")

            return formatted_post

        except Exception as e:
            logger.error(f"获取帖子详情失败: {str(e)}")
            raise

    async def get_post_comments(
        self,
        post_id: str,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        获取帖子评论列表

        Args:
            post_id: 帖子ID
            limit: 返回数量
            offset: 偏移量

        Returns:
            List[Dict]: 评论列表
        """
        try:
            collection = self.mongodb.get_collection(self.comments_collection)

            cursor = collection.find({
                "post_id": post_id,
                "parent_id": None  # 只获取顶级评论
            }).sort("created_at", -1).skip(offset).limit(limit)

            comments = []
            async for comment in cursor:
                formatted_comment = await self._format_comment(comment)
                comments.append(formatted_comment)

            return comments

        except Exception as e:
            logger.error(f"获取评论列表失败: {str(e)}")
            raise

    async def get_posts_by_tag(
        self,
        tag: str,
        limit: int = 20,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        按标签查询帖子

        Args:
            tag: 标签名
            limit: 返回数量
            offset: 偏移量

        Returns:
            List[Dict]: 帖子列表
        """
        try:
            # 构建缓存键
            cache_key = f"tag:{tag}:posts:limit:{limit}:offset:{offset}"

            # 先尝试从Redis获取
            cached_posts = await self.redis.get(cache_key)
            if cached_posts:
                import json
                try:
                    posts = json.loads(cached_posts)
                    logger.debug(f"从Redis缓存获取标签帖子: {tag}")
                    return posts
                except Exception as e:
                    logger.warning(f"解析Redis缓存失败: {str(e)}")

            # 从MongoDB获取
            collection = self.mongodb.get_collection(self.posts_collection)

            cursor = collection.find({
                "tags": tag,
                "moderation_status": "approved"
            }).sort("created_at", -1).skip(offset).limit(limit)

            posts = []
            async for post in cursor:
                formatted_post = await self._format_post(post, None)
                posts.append(formatted_post)

            # 缓存到Redis，过期时间1小时
            import json
            await self.redis.set(cache_key, json.dumps(posts, ensure_ascii=False), ex=3600
            )
            logger.debug(f"标签帖子已缓存到Redis: {tag}")

            return posts

        except Exception as e:
            logger.error(f"按标签查询失败: {str(e)}")
            raise

    async def _get_following_ids(self, user_id: int) -> List[int]:
        """获取用户关注的用户ID列表"""
        try:
            collection = self.mongodb.get_collection(self.follows_collection)
            cursor = collection.find({"follower_id": user_id})

            following_ids = []
            async for follow in cursor:
                following_ids.append(follow["following_id"])

            return following_ids

        except Exception as e:
            logger.error(f"获取关注列表失败: {str(e)}")
            return []

    async def _format_post(self, post: Dict[str, Any], current_user_id: Optional[int] = None) -> Dict[str, Any]:
        """格式化帖子数据"""
        post.pop("_id", None)
        if isinstance(post.get("created_at"), datetime):
            post["created_at"] = post["created_at"].isoformat()
        if isinstance(post.get("updated_at"), datetime):
            post["updated_at"] = post["updated_at"].isoformat()

        # Rename fields to match frontend expectations
        if "like_count" in post:
            post["likes_count"] = post.pop("like_count")
        if "comment_count" in post:
            post["comments_count"] = post.pop("comment_count")

        # Add id field (copy of post_id for frontend compatibility)
        if "post_id" in post:
            post["id"] = post["post_id"]

        # Get user information from MySQL
        try:
            user_id = post.get("user_id")
            if user_id:
                with self.mysql_db.get_session() as session:
                    result = session.execute(
                        text("SELECT username, avatar_url FROM users WHERE id = :user_id"),
                        {"user_id": user_id}
                    ).fetchone()

                    if result:
                        post["username"] = result[0]  # username
                        post["user_avatar"] = result[1]  # avatar_url
                    else:
                        post["username"] = "未知用户"
                        post["user_avatar"] = None
        except Exception as e:
            logger.error(f"获取用户信息失败: {str(e)}")
            post["username"] = "未知用户"
            post["user_avatar"] = None

        # Check if current user liked this post
        post["is_liked"] = False
        if current_user_id and post.get("post_id"):
            try:
                likes_collection = self.mongodb.get_collection(self.likes_collection)
                like = await likes_collection.find_one({
                    "user_id": current_user_id,
                    "post_id": post["post_id"]
                })
                post["is_liked"] = like is not None
            except Exception as e:
                logger.error(f"检查点赞状态失败: {str(e)}")

        return post

    async def _format_comment(self, comment: Dict[str, Any]) -> Dict[str, Any]:
        """
        格式化评论数据

        Args:
            comment: 原始评论数据

        Returns:
            Dict: 格式化后的评论数据
        """
        # 移除 MongoDB 的 _id
        comment.pop("_id", None)

        # 格式化时间
        if isinstance(comment.get("created_at"), datetime):
            comment["created_at"] = comment["created_at"].isoformat()

        # 添加 id 字段（复制 comment_id）
        if "comment_id" in comment:
            comment["id"] = comment["comment_id"]

        # 从 MySQL 获取用户信息
        try:
            user_id = comment.get("user_id")
            if user_id:
                with self.mysql_db.get_session() as session:
                    result = session.execute(
                        text("SELECT username, avatar_url FROM users WHERE id = :user_id"),
                        {"user_id": user_id}
                    ).fetchone()

                    if result:
                        comment["username"] = result[0]  # username
                        comment["user_avatar"] = result[1]  # avatar_url
                    else:
                        comment["username"] = "未知用户"
                        comment["user_avatar"] = None
        except Exception as e:
            logger.error(f"获取评论用户信息失败: {str(e)}")
            comment["username"] = "未知用户"
            comment["user_avatar"] = None

        return comment


# ========== 全局实例（单例模式） ==========

_social_service: Optional[SocialService] = None


def get_social_service() -> SocialService:
    """
    获取全局社交服务实例（单例）

    Returns:
        SocialService: 社交服务实例
    """
    global _social_service
    if _social_service is None:
        _social_service = SocialService()
    return _social_service
