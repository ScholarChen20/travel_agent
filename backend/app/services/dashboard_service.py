"""首页仪表盘服务"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime, timedelta
from loguru import logger
from sqlalchemy import func, desc
import time

from ..database.mysql import get_mysql_db
from ..database.models import User, UserProfile, Post, Comment
from ..database.mongodb import get_mongodb_client
from ..config import get_settings

settings = get_settings()


# ========== 请求模型 ==========

class DateRangeRequest(BaseModel):
    """日期范围请求"""
    start_date: Optional[str] = Field(default=None, description="开始日期")
    end_date: Optional[str] = Field(default=None, description="结束日期")


# ========== 响应模型 ==========

class UserStatsResponse(BaseModel):
    """用户统计响应"""
    total_users: int = Field(..., description="总用户数")
    active_users_today: int = Field(..., description="今日活跃用户")
    active_users_week: int = Field(..., description="本周活跃用户")
    new_users_today: int = Field(..., description="今日新增用户")
    new_users_week: int = Field(..., description="本周新增用户")
    new_users_month: int = Field(..., description="本月新增用户")
    user_growth_rate: float = Field(..., description="用户增长率（%）")


class ContentStatsResponse(BaseModel):
    """内容统计响应"""
    total_plans: int = Field(..., description="总旅行计划数")
    total_pois: int = Field(..., description="总景点数")
    total_posts: int = Field(..., description="总帖子数")
    total_comments: int = Field(..., description="总评论数")
    plans_created_today: int = Field(..., description="今日创建的旅行计划数")
    posts_created_today: int = Field(..., description="今日创建的帖子数")


class BusinessStatsResponse(BaseModel):
    """业务指标响应"""
    daily_plan_creation: int = Field(..., description="每日旅行计划创建量")
    weekly_plan_creation: int = Field(..., description="每周旅行计划创建量")
    monthly_plan_creation: int = Field(..., description="每月旅行计划创建量")
    user_retention_rate: float = Field(..., description="用户留存率（%）")
    average_plan_length: float = Field(..., description="平均旅行计划长度（天）")


class DashboardOverviewResponse(BaseModel):
    """首页综合指标响应"""
    user_stats: UserStatsResponse = Field(..., description="用户统计数据")
    content_stats: ContentStatsResponse = Field(..., description="内容统计数据")
    business_stats: BusinessStatsResponse = Field(..., description="业务指标数据")
    updated_at: datetime = Field(default_factory=datetime.now, description="数据更新时间")


class BusinessTrendResponse(BaseModel):
    """业务趋势响应"""
    date_range: List[str] = Field(..., description="日期范围")
    plan_creation_trend: List[int] = Field(..., description="旅行计划创建趋势")
    user_registration_trend: List[int] = Field(..., description="用户注册趋势")
    user_activity_trend: List[int] = Field(..., description="用户活跃趋势")


# ========== 服务类 ==========

class DashboardService:
    """首页仪表盘服务类"""

    def __init__(self):
        """初始化服务"""
        self.mysql_db = get_mysql_db()
        self.mongodb_client = get_mongodb_client()
        self.plans_collection = "travel_plans"
        self.posts_collection = "social_posts"
        self.comments_collection = "social_comments"
        # 延迟初始化Redis客户端
        self.redis = None
        self._init_redis()
        logger.info("仪表盘服务已初始化")

    def _init_redis(self):
        """初始化Redis客户端"""
        try:
            from ..database.redis_client import get_redis_client
            self.redis = get_redis_client()
            logger.debug("Redis客户端初始化成功")
        except Exception as e:
            logger.warning(f"Redis客户端初始化失败: {str(e)}")
            self.redis = None

    async def get_user_stats(self) -> UserStatsResponse:
        """获取用户统计数据"""
        try:
            # 先尝试从Redis缓存获取
            if self.redis:
                cache_key = "dashboard:user_stats"
                cached_stats = await self.redis.get(cache_key)
                if cached_stats:
                    import json
                    try:
                        stats_data = json.loads(cached_stats)
                        logger.debug("从Redis缓存获取用户统计数据")
                        return UserStatsResponse(**stats_data)
                    except Exception as e:
                        logger.warning(f"解析Redis缓存失败: {str(e)}")

            # 从MySQL数据库查询
            with self.mysql_db.get_session() as session:
                # 总用户数
                total_users = session.query(User).count()

                # 今日活跃用户（假设last_login_at不为空即为活跃）
                today = datetime.now().date()
                active_users_today = session.query(User).filter(
                    func.date(User.last_login_at) == today
                ).count()

                # 本周活跃用户
                week_ago = today - timedelta(days=7)
                active_users_week = session.query(User).filter(
                    func.date(User.last_login_at) >= week_ago
                ).count()

                # 今日新增用户
                new_users_today = session.query(User).filter(
                    func.date(User.created_at) == today
                ).count()

                # 本周新增用户
                new_users_week = session.query(User).filter(
                    func.date(User.created_at) >= week_ago
                ).count()

                # 本月新增用户
                month_ago = today - timedelta(days=30)
                new_users_month = session.query(User).filter(
                    func.date(User.created_at) >= month_ago
                ).count()

                # 用户增长率（本月新增/上月新增）
                last_month_ago = today - timedelta(days=60)
                last_month_new = session.query(User).filter(
                    func.date(User.created_at) >= last_month_ago,
                    func.date(User.created_at) < month_ago
                ).count()
                user_growth_rate = 0.0
                if last_month_new > 0:
                    user_growth_rate = ((new_users_month - last_month_new) / last_month_new) * 100

                # 构建响应
                response = UserStatsResponse(
                    total_users=total_users,
                    active_users_today=active_users_today,
                    active_users_week=active_users_week,
                    new_users_today=new_users_today,
                    new_users_week=new_users_week,
                    new_users_month=new_users_month,
                    user_growth_rate=round(user_growth_rate, 2)
                )

                # 缓存到Redis，过期时间5分钟
                if self.redis:
                    import json
                    await self.redis.set(cache_key, json.dumps(response.model_dump(), ensure_ascii=False), ex=300)
                    logger.debug("用户统计数据已缓存到Redis")

                return response

        except Exception as e:
            logger.error(f"获取用户统计数据失败: {str(e)}")
            # 返回默认数据
            return UserStatsResponse(
                total_users=0,
                active_users_today=0,
                active_users_week=0,
                new_users_today=0,
                new_users_week=0,
                new_users_month=0,
                user_growth_rate=0.0
            )

    async def get_content_stats(self) -> ContentStatsResponse:
        """获取内容统计数据"""
        try:
            # 先尝试从Redis缓存获取
            if self.redis:
                cache_key = "dashboard:content_stats"
                cached_stats = await self.redis.get(cache_key)
                if cached_stats:
                    import json
                    try:
                        stats_data = json.loads(cached_stats)
                        logger.debug("从Redis缓存获取内容统计数据")
                        return ContentStatsResponse(**stats_data)
                    except Exception as e:
                        logger.warning(f"解析Redis缓存失败: {str(e)}")

            logger.info("开始从MongoDB获取内容统计数据")
            post_collection = self.mongodb_client.get_collection(self.posts_collection)
            total_posts = await post_collection.count_documents({})

            comment_collection = self.mongodb_client.get_collection(self.comments_collection)
            total_comments = await comment_collection.count_documents({})

            today = datetime.now().date()
            posts_created_today = await post_collection.count_documents({
                "created_at": {
                    "$gte": datetime(today.year, today.month, today.day),
                    "$lt": datetime(today.year, today.month, today.day) + timedelta(days=1)
                }
            })

            # 从MongoDB查询旅行计划
            logger.info("开始从MongoDB获取旅行计划统计数据")
            collection = self.mongodb_client.get_collection(self.plans_collection)
            total_plans = await collection.count_documents({})
            plans_created_today = await collection.count_documents({
                "created_at": {
                    "$gte": datetime(today.year, today.month, today.day),
                    "$lt": datetime(today.year, today.month, today.day) + timedelta(days=1)
                }
            })

            # 统计景点数（假设从旅行计划中统计）
            pois = await collection.distinct("days")
            total_pois = 0
            for poi in pois:
                total_pois += len((poi.get("attractions", [])))

            # 构建响应
            response = ContentStatsResponse(
                total_plans=total_plans,
                total_pois=total_pois,
                total_posts=total_posts,
                total_comments=total_comments,
                plans_created_today=plans_created_today,
                posts_created_today=posts_created_today
            )

            # 缓存到Redis，过期时间5分钟
            if self.redis:
                import json
                await self.redis.set(cache_key, json.dumps(response.model_dump(), ensure_ascii=False), ex=300)
                logger.debug("内容统计数据已缓存到Redis")

            return response

        except Exception as e:
            logger.error(f"获取内容统计数据失败: {str(e)}")
            # 返回默认数据
            return ContentStatsResponse(
                total_plans=0,
                total_pois=0,
                total_posts=0,
                total_comments=0,
                plans_created_today=0,
                posts_created_today=0
            )

    async def get_business_stats(self) -> BusinessStatsResponse:
        """获取业务指标数据"""
        try:
            # 先尝试从Redis缓存获取
            if self.redis:
                cache_key = "dashboard:business_stats"
                cached_stats = await self.redis.get(cache_key)
                if cached_stats:
                    import json
                    try:
                        stats_data = json.loads(cached_stats)
                        logger.debug("从Redis缓存获取业务指标数据")
                        return BusinessStatsResponse(**stats_data)
                    except Exception as e:
                        logger.warning(f"解析Redis缓存失败: {str(e)}")

            # 从MongoDB查询旅行计划
            travel_plans = self.mongodb_client.get_collection(self.plans_collection)
            today = datetime.now().date()

            # 每日旅行计划创建量
            daily_plan_creation = await travel_plans.count_documents({
                "created_at": {
                    "$gte": datetime(today.year, today.month, today.day),
                    "$lt": datetime(today.year, today.month, today.day) + timedelta(days=1)
                }
            })

            # 每周旅行计划创建量
            week_ago = today - timedelta(days=7)
            weekly_plan_creation = await travel_plans.count_documents({
                "created_at": {
                    "$gte": datetime(week_ago.year, week_ago.month, week_ago.day),
                    "$lt": datetime(today.year, today.month, today.day) + timedelta(days=1)
                }
            })

            # 每月旅行计划创建量
            month_ago = today - timedelta(days=30)
            monthly_plan_creation = await travel_plans.count_documents({
                "created_at": {
                    "$gte": datetime(month_ago.year, month_ago.month, month_ago.day),
                    "$lt": datetime(today.year, today.month, today.day) + timedelta(days=1)
                }
            })

            # 用户留存率（7日留存）
            # 计算7天前注册的用户中，今天仍活跃的比例
            with self.mysql_db.get_session() as session:
                seven_days_ago = today - timedelta(days=7)
                registered_users = session.query(User).filter(
                    func.date(User.created_at) == seven_days_ago
                ).count()
                if registered_users > 0:
                    active_users = session.query(User).filter(
                        func.date(User.created_at) == seven_days_ago,
                        func.date(User.last_login_at) == today
                    ).count()
                    user_retention_rate = (active_users / registered_users) * 100
                else:
                    user_retention_rate = 0.0

            # 平均旅行计划长度（天）
            total_days = await travel_plans.distinct("days")
            total_plans = await travel_plans.count_documents({})
            avg_plan_length = float(len(total_days) / total_plans) if total_plans > 0 else 0.0

            # 构建响应
            response = BusinessStatsResponse(
                daily_plan_creation=daily_plan_creation,
                weekly_plan_creation=weekly_plan_creation,
                monthly_plan_creation=monthly_plan_creation,
                user_retention_rate=round(user_retention_rate, 2),
                average_plan_length=round(avg_plan_length, 2)
            )

            # 缓存到Redis，过期时间5分钟
            if self.redis:
                import json
                await self.redis.set(cache_key, json.dumps(response.model_dump(), ensure_ascii=False), ex=300)
                logger.debug("业务指标数据已缓存到Redis")

            return response

        except Exception as e:
            logger.error(f"获取业务指标数据失败: {str(e)}")
            # 返回默认数据
            return BusinessStatsResponse(
                daily_plan_creation=0,
                weekly_plan_creation=0,
                monthly_plan_creation=0,
                user_retention_rate=0.0,
                average_plan_length=0.0
            )

    async def get_overview(self) -> DashboardOverviewResponse:
        """获取首页综合指标"""
        try:
            # 并行获取所有统计数据
            user_stats = await self.get_user_stats()
            content_stats = await self.get_content_stats()
            business_stats = await self.get_business_stats()

            # 构建响应
            response = DashboardOverviewResponse(
                user_stats=user_stats,
                content_stats=content_stats,
                business_stats=business_stats
            )

            logger.debug("获取首页综合指标成功")
            return response

        except Exception as e:
            logger.error(f"获取首页综合指标失败: {str(e)}")
            # 返回默认数据
            return DashboardOverviewResponse(
                user_stats=UserStatsResponse(
                    total_users=0,
                    active_users_today=0,
                    active_users_week=0,
                    new_users_today=0,
                    new_users_week=0,
                    new_users_month=0,
                    user_growth_rate=0.0
                ),
                content_stats=ContentStatsResponse(
                    total_plans=0,
                    total_pois=0,
                    total_posts=0,
                    total_comments=0,
                    plans_created_today=0,
                    posts_created_today=0
                ),
                business_stats=BusinessStatsResponse(
                    daily_plan_creation=0,
                    weekly_plan_creation=0,
                    monthly_plan_creation=0,
                    user_retention_rate=0.0,
                    average_plan_length=0.0
                )
            )

    async def get_business_trend(self, request: Optional[DateRangeRequest] = None) -> BusinessTrendResponse:
        """获取业务趋势数据"""
        try:
            # 确定日期范围
            if request and request.start_date and request.end_date:
                start_date = datetime.strptime(request.start_date, "%Y-%m-%d").date()
                end_date = datetime.strptime(request.end_date, "%Y-%m-%d").date()
            else:
                # 默认返回最近7天的数据
                end_date = datetime.now().date()
                start_date = end_date - timedelta(days=6)

            # 生成日期范围
            date_range = []
            current_date = start_date
            while current_date <= end_date:
                date_range.append(current_date.strftime("%Y-%m-%d"))
                current_date += timedelta(days=1)

            # 查询每日数据
            travel_plans = self.mongodb_client.get_collection(self.plans_collection)
            plan_creation_trend = []

            for date_str in date_range:
                date = datetime.strptime(date_str, "%Y-%m-%d").date()
                plan_count = await travel_plans.count_documents({
                    "created_at": {
                        "$gte": datetime(date.year, date.month, date.day),
                        "$lt": datetime(date.year, date.month, date.day) + timedelta(days=1)
                    }
                })
                plan_creation_trend.append(plan_count)

            # 查询用户注册和活跃趋势
            with self.mysql_db.get_session() as session:
                user_registration_trend = []
                user_activity_trend = []

                for date_str in date_range:
                    date = datetime.strptime(date_str, "%Y-%m-%d").date()

                    # 用户注册量
                    user_count = session.query(User).filter(
                        func.date(User.created_at) == date
                    ).count()
                    user_registration_trend.append(user_count)

                    # 用户活跃量
                    active_count = session.query(User).filter(
                        func.date(User.last_login_at) == date
                    ).count()
                    user_activity_trend.append(active_count)

            # 构建响应
            response = BusinessTrendResponse(
                date_range=date_range,
                plan_creation_trend=plan_creation_trend,
                user_registration_trend=user_registration_trend,
                user_activity_trend=user_activity_trend
            )

            logger.debug(f"获取业务趋势数据成功，日期范围: {start_date} 至 {end_date}")
            return response

        except Exception as e:
            logger.error(f"获取业务趋势数据失败: {str(e)}")
            # 返回空数据
            return BusinessTrendResponse(
                date_range=[],
                plan_creation_trend=[],
                user_registration_trend=[],
                user_activity_trend=[]
            )


# ========== 全局实例（单例模式） ==========

_dashboard_service: Optional[DashboardService] = None


def get_dashboard_service() -> DashboardService:
    """
    获取全局仪表盘服务实例（单例）

    Returns:
        DashboardService: 仪表盘服务实例
    """
    global _dashboard_service
    if _dashboard_service is None:
        _dashboard_service = DashboardService()
    return _dashboard_service
