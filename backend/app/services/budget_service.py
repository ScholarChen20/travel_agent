"""预算管理服务"""

from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime
from loguru import logger
from sqlalchemy import func, desc
import json

from ..database.mysql import get_mysql_db
from ..database.models import User, UserProfile
from ..config import get_settings

settings = get_settings()


# ========== 请求模型 ==========

class BudgetRequest(BaseModel):
    """预算请求"""
    user_id: str = Field(..., description="用户ID")
    budget_amount: float = Field(..., description="预算金额")
    start_date: str = Field(..., description="开始日期")
    end_date: str = Field(..., description="结束日期")
    currency: str = Field(default="CNY", description="货币类型")
    category: str = Field(default="all", description="预算类别")


class ExpenseRequest(BaseModel):
    """支出请求"""
    user_id: str = Field(..., description="用户ID")
    expense_amount: float = Field(..., description="支出金额")
    expense_date: str = Field(..., description="支出日期")
    category: str = Field(..., description="支出类别")
    description: str = Field(default="", description="支出描述")
    currency: str = Field(default="CNY", description="货币类型")


# ========== 响应模型 ==========

class BudgetResponse(BaseModel):
    """预算响应"""
    budget_id: str = Field(..., description="预算ID")
    user_id: str = Field(..., description="用户ID")
    budget_amount: float = Field(..., description="预算金额")
    used_amount: float = Field(..., description="已使用金额")
    remaining_amount: float = Field(..., description="剩余金额")
    start_date: str = Field(..., description="开始日期")
    end_date: str = Field(..., description="结束日期")
    currency: str = Field(..., description="货币类型")
    category: str = Field(..., description="预算类别")
    status: str = Field(..., description="预算状态")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")


class ExpenseResponse(BaseModel):
    """支出响应"""
    expense_id: str = Field(..., description="支出ID")
    user_id: str = Field(..., description="用户ID")
    expense_amount: float = Field(..., description="支出金额")
    expense_date: str = Field(..., description="支出日期")
    category: str = Field(..., description="支出类别")
    description: str = Field(..., description="支出描述")
    currency: str = Field(..., description="货币类型")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")


class BudgetStatsResponse(BaseModel):
    """预算统计响应"""
    total_budget: float = Field(..., description="总预算")
    total_used: float = Field(..., description="总支出")
    total_remaining: float = Field(..., description="总剩余")
    budget_usage_rate: float = Field(..., description="预算使用率（%）")
    monthly_budget: float = Field(..., description="本月预算")
    monthly_used: float = Field(..., description="本月支出")
    monthly_remaining: float = Field(..., description="本月剩余")


# ========== 服务类 ==========

class BudgetService:
    """预算管理服务类"""

    def __init__(self):
        """初始化服务"""
        self.mysql_db = get_mysql_db()
        # 延迟初始化Redis客户端
        self.redis = None
        self._init_redis()
        logger.info("预算服务已初始化")

    def _init_redis(self):
        """初始化Redis客户端"""
        try:
            from ..database.redis_client import get_redis_client
            self.redis = get_redis_client()
            logger.debug("Redis客户端初始化成功")
        except Exception as e:
            logger.warning(f"Redis客户端初始化失败: {str(e)}")
            self.redis = None

    async def create_budget(self, request: BudgetRequest) -> BudgetResponse:
        """创建预算"""
        try:
            logger.info(f"为用户{request.user_id}创建预算")

            # 生成预算ID
            budget_id = f"budget_{datetime.now().strftime('%Y%m%d%H%M%S')}_{request.user_id}"

            # 构建预算响应
            response = BudgetResponse(
                budget_id=budget_id,
                user_id=request.user_id,
                budget_amount=request.budget_amount,
                used_amount=0.0,
                remaining_amount=request.budget_amount,
                start_date=request.start_date,
                end_date=request.end_date,
                currency=request.currency,
                category=request.category,
                status="active"
            )

            # 缓存预算到Redis
            if self.redis:
                cache_key = f"budget:{request.user_id}:{budget_id}"
                await self.redis.set(cache_key, json.dumps(response.model_dump(), ensure_ascii=False), ex=3600*24*30)
                logger.debug(f"预算已缓存到Redis: {cache_key}")

            logger.info(f"为用户{request.user_id}成功创建预算: {budget_id}")
            return response

        except Exception as e:
            logger.error(f"创建预算失败: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"创建预算失败: {str(e)}"
            )

    async def add_expense(self, request: ExpenseRequest) -> ExpenseResponse:
        """添加支出"""
        try:
            logger.info(f"为用户{request.user_id}添加支出")

            # 生成支出ID
            expense_id = f"expense_{datetime.now().strftime('%Y%m%d%H%M%S')}_{request.user_id}"

            # 构建支出响应
            response = ExpenseResponse(
                expense_id=expense_id,
                user_id=request.user_id,
                expense_amount=request.expense_amount,
                expense_date=request.expense_date,
                category=request.category,
                description=request.description,
                currency=request.currency
            )

            # 缓存支出到Redis
            if self.redis:
                cache_key = f"expense:{request.user_id}:{expense_id}"
                await self.redis.set(cache_key, json.dumps(response.model_dump(), ensure_ascii=False), ex=3600*24*30)
                logger.debug(f"支出已缓存到Redis: {cache_key}")

            logger.info(f"为用户{request.user_id}成功添加支出: {expense_id}")
            return response

        except Exception as e:
            logger.error(f"添加支出失败: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"添加支出失败: {str(e)}"
            )

    async def get_budget_stats(self, user_id: str) -> BudgetStatsResponse:
        """获取预算统计"""
        try:
            logger.info(f"获取用户{user_id}的预算统计")

            # 从Redis缓存获取预算统计
            if self.redis:
                cache_key = f"budget_stats:{user_id}"
                cached_stats = await self.redis.get(cache_key)
                if cached_stats:
                    stats_data = json.loads(cached_stats)
                    logger.debug("从Redis缓存获取预算统计")
                    return BudgetStatsResponse(**stats_data)

            # 模拟预算统计数据
            total_budget = 10000.0
            total_used = 3500.0
            total_remaining = total_budget - total_used
            budget_usage_rate = (total_used / total_budget) * 100

            monthly_budget = 5000.0
            monthly_used = 1200.0
            monthly_remaining = monthly_budget - monthly_used

            # 构建响应
            response = BudgetStatsResponse(
                total_budget=total_budget,
                total_used=total_used,
                total_remaining=total_remaining,
                budget_usage_rate=round(budget_usage_rate, 2),
                monthly_budget=monthly_budget,
                monthly_used=monthly_used,
                monthly_remaining=monthly_remaining
            )

            # 缓存预算统计到Redis
            if self.redis:
                cache_key = f"budget_stats:{user_id}"
                await self.redis.set(cache_key, json.dumps(response.model_dump(), ensure_ascii=False), ex=3600)
                logger.debug(f"预算统计已缓存到Redis: {cache_key}")

            logger.info(f"获取用户{user_id}的预算统计成功")
            return response

        except Exception as e:
            logger.error(f"获取预算统计失败: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"获取预算统计失败: {str(e)}"
            )


# ========== 全局实例（单例模式） ==========

_budget_service: Optional[BudgetService] = None


def get_budget_service() -> BudgetService:
    """
    获取全局预算服务实例（单例）

    Returns:
        BudgetService: 预算服务实例
    """
    global _budget_service
    if _budget_service is None:
        _budget_service = BudgetService()
    return _budget_service
