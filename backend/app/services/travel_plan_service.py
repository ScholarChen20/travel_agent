"""
旅行计划管理服务

功能：
1. 保存旅行计划到MongoDB
2. 查询用户的旅行计划列表
3. 获取计划详情
4. 更新计划信息
5. 标记收藏/取消收藏
6. 删除计划
7. 同步更新MySQL中的visited_cities
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
import secrets
from loguru import logger

from ..database.mongodb import get_mongodb_client
from ..database.mysql import get_mysql_db
from ..database.models import UserProfile


class TravelPlanService:
    """旅行计划管理服务类"""

    def __init__(self):
        """初始化服务"""
        self.mongodb = get_mongodb_client()
        self.collection_name = "travel_plans"
        logger.info("旅行计划服务已初始化")

    async def save_plan(
        self,
        user_id: int,
        session_id: str,
        city: str,
        start_date: str,
        trip_plan: Dict[str, Any],
        preferences: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        保存旅行计划到MongoDB

        Args:
            user_id: 用户ID
            session_id: 对话会话ID
            city: 城市名称
            start_date: 开始日期
            trip_plan: 旅行计划详情
            preferences: 用户偏好设置

        Returns:
            str: 计划ID (plan_id)
        """
        try:
            # 生成唯一的计划ID
            plan_id = f"plan_{secrets.token_urlsafe(16)}"

            # 构建文档
            plan_document = {
                "plan_id": plan_id,
                "user_id": user_id,
                "session_id": session_id,
                "city": city,
                "start_date": start_date,
                "days": trip_plan.get("days", []),
                "weather_info": trip_plan.get("weather_info", {}),
                "budget": trip_plan.get("budget"),
                "preferences": preferences or {},
                "is_favorite": False,
                "is_completed": False,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }

            # 保存到MongoDB
            collection = self.mongodb.get_collection(self.collection_name)
            await collection.insert_one(plan_document)

            logger.info(f"旅行计划已保存: {plan_id} (用户: {user_id}, 城市: {city})")

            # 更新用户访问过的城市列表
            await self._update_user_visited_cities(user_id, city)

            return plan_id

        except Exception as e:
            logger.error(f"保存旅行计划失败: {str(e)}")
            raise

    async def get_user_plans(
        self,
        user_id: int,
        city: Optional[str] = None,
        is_favorite: Optional[bool] = None,
        is_completed: Optional[bool] = None,
        limit: int = 20,
        skip: int = 0
    ) -> List[Dict[str, Any]]:
        """
        查询用户的旅行计划列表

        Args:
            user_id: 用户ID
            city: 城市筛选（可选）
            is_favorite: 是否收藏筛选（可选）
            is_completed: 是否完成筛选（可选）
            limit: 返回数量限制
            skip: 跳过数量（分页）

        Returns:
            List[Dict]: 计划列表
        """
        try:
            # 构建查询条件
            query = {"user_id": user_id}

            if city is not None:
                query["city"] = city

            if is_favorite is not None:
                query["is_favorite"] = is_favorite

            if is_completed is not None:
                query["is_completed"] = is_completed

            # 查询MongoDB
            collection = self.mongodb.get_collection(self.collection_name)
            cursor = collection.find(query).sort("created_at", -1).skip(skip).limit(limit)

            plans = []
            async for doc in cursor:
                # 移除MongoDB的_id字段
                doc.pop("_id", None)
                # 转换日期为ISO格式
                if isinstance(doc.get("created_at"), datetime):
                    doc["created_at"] = doc["created_at"].isoformat()
                if isinstance(doc.get("updated_at"), datetime):
                    doc["updated_at"] = doc["updated_at"].isoformat()
                plans.append(doc)

            logger.debug(f"查询到 {len(plans)} 个旅行计划 (用户: {user_id})")
            return plans

        except Exception as e:
            logger.error(f"查询旅行计划失败: {str(e)}")
            raise

    async def get_plan_by_id(self, plan_id: str, user_id: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """
        根据ID获取计划详情

        Args:
            plan_id: 计划ID
            user_id: 用户ID（用于权限验证，可选）

        Returns:
            Dict: 计划详情，不存在返回None
        """
        try:
            query = {"plan_id": plan_id}

            # 如果提供了user_id，增加权限检查
            if user_id is not None:
                query["user_id"] = user_id

            collection = self.mongodb.get_collection(self.collection_name)
            doc = await collection.find_one(query)

            if not doc:
                logger.warning(f"计划不存在: {plan_id}")
                return None

            # 移除MongoDB的_id字段
            doc.pop("_id", None)

            # 转换日期为ISO格式
            if isinstance(doc.get("created_at"), datetime):
                doc["created_at"] = doc["created_at"].isoformat()
            if isinstance(doc.get("updated_at"), datetime):
                doc["updated_at"] = doc["updated_at"].isoformat()

            return doc

        except Exception as e:
            logger.error(f"获取计划详情失败: {str(e)}")
            raise

    async def update_plan(
        self,
        plan_id: str,
        user_id: int,
        updates: Dict[str, Any]
    ) -> bool:
        """
        更新计划信息

        Args:
            plan_id: 计划ID
            user_id: 用户ID（权限验证）
            updates: 更新字段

        Returns:
            bool: 是否成功
        """
        try:
            # 不允许更新的字段
            protected_fields = ["plan_id", "user_id", "created_at"]
            for field in protected_fields:
                updates.pop(field, None)

            # 自动更新时间戳
            updates["updated_at"] = datetime.utcnow()

            # 更新MongoDB
            collection = self.mongodb.get_collection(self.collection_name)
            result = await collection.update_one(
                {"plan_id": plan_id, "user_id": user_id},
                {"$set": updates}
            )

            if result.modified_count > 0:
                logger.info(f"计划已更新: {plan_id}")
                return True
            else:
                logger.warning(f"计划未更新（不存在或无变化）: {plan_id}")
                return False

        except Exception as e:
            logger.error(f"更新计划失败: {str(e)}")
            raise

    async def mark_favorite(self, plan_id: str, user_id: int, is_favorite: bool) -> bool:
        """
        标记收藏/取消收藏

        Args:
            plan_id: 计划ID
            user_id: 用户ID
            is_favorite: 是否收藏

        Returns:
            bool: 是否成功
        """
        try:
            collection = self.mongodb.get_collection(self.collection_name)
            result = await collection.update_one(
                {"plan_id": plan_id, "user_id": user_id},
                {
                    "$set": {
                        "is_favorite": is_favorite,
                        "updated_at": datetime.utcnow()
                    }
                }
            )

            if result.modified_count > 0:
                action = "收藏" if is_favorite else "取消收藏"
                logger.info(f"计划已{action}: {plan_id}")
                return True
            else:
                logger.warning(f"标记收藏失败（计划不存在）: {plan_id}")
                return False

        except Exception as e:
            logger.error(f"标记收藏失败: {str(e)}")
            raise

    async def mark_completed(self, plan_id: str, user_id: int, is_completed: bool) -> bool:
        """
        标记为已完成/未完成

        Args:
            plan_id: 计划ID
            user_id: 用户ID
            is_completed: 是否完成

        Returns:
            bool: 是否成功
        """
        try:
            collection = self.mongodb.get_collection(self.collection_name)
            result = await collection.update_one(
                {"plan_id": plan_id, "user_id": user_id},
                {
                    "$set": {
                        "is_completed": is_completed,
                        "updated_at": datetime.utcnow()
                    }
                }
            )

            if result.modified_count > 0:
                action = "已完成" if is_completed else "未完成"
                logger.info(f"计划标记为{action}: {plan_id}")
                return True
            else:
                logger.warning(f"标记完成状态失败（计划不存在）: {plan_id}")
                return False

        except Exception as e:
            logger.error(f"标记完成状态失败: {str(e)}")
            raise

    async def delete_plan(self, plan_id: str, user_id: int) -> bool:
        """
        删除计划

        Args:
            plan_id: 计划ID
            user_id: 用户ID（权限验证）

        Returns:
            bool: 是否成功
        """
        try:
            collection = self.mongodb.get_collection(self.collection_name)
            result = await collection.delete_one(
                {"plan_id": plan_id, "user_id": user_id}
            )

            if result.deleted_count > 0:
                logger.info(f"计划已删除: {plan_id}")
                return True
            else:
                logger.warning(f"删除失败（计划不存在）: {plan_id}")
                return False

        except Exception as e:
            logger.error(f"删除计划失败: {str(e)}")
            raise

    async def get_user_stats(self, user_id: int) -> Dict[str, Any]:
        """
        获取用户旅行统计数据（从MongoDB聚合）

        Args:
            user_id: 用户ID

        Returns:
            Dict: 统计数据
        """
        try:
            collection = self.mongodb.get_collection(self.collection_name)

            # 聚合查询
            pipeline = [
                {"$match": {"user_id": user_id}},
                {
                    "$group": {
                        "_id": None,
                        "total_trips": {"$sum": 1},
                        "completed_trips": {
                            "$sum": {"$cond": ["$is_completed", 1, 0]}
                        },
                        "favorite_trips": {
                            "$sum": {"$cond": ["$is_favorite", 1, 0]}
                        },
                        "cities": {"$addToSet": "$city"}
                    }
                }
            ]

            result = await collection.aggregate(pipeline).to_list(length=1)

            if result:
                stats = result[0]
                return {
                    "total_trips": stats.get("total_trips", 0),
                    "completed_trips": stats.get("completed_trips", 0),
                    "favorite_trips": stats.get("favorite_trips", 0),
                    "total_cities": len(stats.get("cities", []))
                }
            else:
                return {
                    "total_trips": 0,
                    "completed_trips": 0,
                    "favorite_trips": 0,
                    "total_cities": 0
                }

        except Exception as e:
            logger.error(f"获取用户统计失败: {str(e)}")
            raise

    async def _update_user_visited_cities(self, user_id: int, city: str):
        """
        更新MySQL中用户档案的visited_cities字段

        Args:
            user_id: 用户ID
            city: 城市名称
        """
        try:
            mysql_db = get_mysql_db()

            with mysql_db.get_session() as session:
                # 查询用户档案
                profile = session.query(UserProfile).filter(
                    UserProfile.user_id == user_id
                ).first()

                if profile:
                    # 获取当前访问过的城市列表
                    visited_cities = profile.visited_cities or []

                    # 如果城市不在列表中，添加
                    if city not in visited_cities:
                        visited_cities.append(city)
                        profile.visited_cities = visited_cities

                        # 更新travel_stats
                        travel_stats = profile.travel_stats or {}
                        travel_stats["total_cities"] = len(visited_cities)
                        profile.travel_stats = travel_stats

                        logger.debug(f"已更新用户访问城市: {user_id} -> {city}")
                else:
                    logger.warning(f"用户档案不存在: {user_id}")

        except Exception as e:
            logger.error(f"更新访问城市失败: {str(e)}")
            # 不抛出异常，避免影响主流程


# ========== 全局实例（单例模式） ==========

_travel_plan_service: Optional[TravelPlanService] = None


def get_travel_plan_service() -> TravelPlanService:
    """
    获取全局旅行计划服务实例（单例）

    Returns:
        TravelPlanService: 旅行计划服务实例
    """
    global _travel_plan_service
    if _travel_plan_service is None:
        _travel_plan_service = TravelPlanService()
    return _travel_plan_service
