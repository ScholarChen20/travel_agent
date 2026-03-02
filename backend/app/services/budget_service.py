"""预算管理服务"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime
import json
from ..database.mongodb import get_mongodb_client
from ..database.redis_client import get_redis_client

redis_client = get_redis_client()
mongodb_client = get_mongodb_client()


class BudgetCategory(BaseModel):
    """预算分类"""
    name: str = Field(..., description="预算分类名称")
    budget: float = Field(..., description="预算金额")
    spent: float = Field(default=0.0, description="已花费金额")


class BudgetCreateRequest(BaseModel):
    """创建预算请求"""
    trip_id: str = Field(..., description="旅行计划ID")
    total_budget: float = Field(..., description="总预算")
    categories: List[BudgetCategory] = Field(..., description="预算分类列表")


class BudgetResponse(BaseModel):
    """预算响应"""
    budget_id: str = Field(..., description="预算ID")
    trip_id: str = Field(..., description="旅行计划ID")
    total_budget: float = Field(..., description="总预算")
    remaining_budget: float = Field(..., description="剩余预算")
    categories: List[BudgetCategory] = Field(..., description="预算分类列表")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新时间")


class ExpenseAddRequest(BaseModel):
    """添加消费请求"""
    budget_id: str = Field(..., description="预算ID")
    category: str = Field(..., description="分类名称")
    amount: float = Field(..., gt=0, description="消费金额")
    description: str = Field(default="", description="消费描述")


class BudgetService:
    """预算管理服务"""

    def __init__(self):
        if mongodb_client:
            self.budgets_collection = mongodb_client["budgets"]
            self.expenses_collection = mongodb_client["expenses"]
        else:
            self.budgets_collection = None
            self.expenses_collection = None

    def create_budget(self, request: BudgetCreateRequest) -> BudgetResponse:
        """创建预算"""
        budget_id = f"budget_{int(datetime.now().timestamp())}"
        
        remaining_budget = request.total_budget - sum(category.spent for category in request.categories)
        
        budget_data = {
            "budget_id": budget_id,
            "trip_id": request.trip_id,
            "total_budget": request.total_budget,
            "remaining_budget": remaining_budget,
            "categories": [cat.model_dump() for cat in request.categories],
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }

        if self.budgets_collection:
            self.budgets_collection.insert_one(budget_data)
        
        cache_key = f"budget:{budget_id}"
        redis_client.setex(cache_key, 3600, json.dumps(budget_data, default=str))

        return BudgetResponse(**budget_data)

    def add_expense(self, request: ExpenseAddRequest) -> BudgetResponse:
        """添加消费记录"""
        budget = self._get_budget_from_db(request.budget_id)
        if not budget:
            raise Exception("预算不存在")

        category_found = False
        for category in budget["categories"]:
            if category["name"] == request.category:
                category["spent"] += request.amount
                category_found = True
                break
        
        if not category_found:
            raise Exception(f"分类 {request.category} 不存在")

        total_spent = sum(category["spent"] for category in budget["categories"])
        budget["remaining_budget"] = budget["total_budget"] - total_spent
        budget["updated_at"] = datetime.now()

        if self.budgets_collection:
            self.budgets_collection.update_one(
                {"budget_id": request.budget_id},
                {"$set": budget}
            )

        expense_record = {
            "budget_id": request.budget_id,
            "category": request.category,
            "amount": request.amount,
            "description": request.description,
            "created_at": datetime.now()
        }

        if self.expenses_collection:
            self.expenses_collection.insert_one(expense_record)

        cache_key = f"budget:{request.budget_id}"
        redis_client.setex(cache_key, 3600, json.dumps(budget, default=str))

        return BudgetResponse(
            budget_id=budget["budget_id"],
            trip_id=budget["trip_id"],
            total_budget=budget["total_budget"],
            remaining_budget=budget["remaining_budget"],
            categories=[BudgetCategory(**cat) for cat in budget["categories"]],
            created_at=budget["created_at"],
            updated_at=budget["updated_at"]
        )

    def get_budget(self, budget_id: str) -> BudgetResponse:
        """获取预算详情"""
        cache_key = f"budget:{budget_id}"
        cached_budget = redis_client.get(cache_key)
        
        if cached_budget:
            budget_data = json.loads(cached_budget)
            return BudgetResponse(
                budget_id=budget_data["budget_id"],
                trip_id=budget_data["trip_id"],
                total_budget=budget_data["total_budget"],
                remaining_budget=budget_data["remaining_budget"],
                categories=[BudgetCategory(**cat) for cat in budget_data["categories"]],
                created_at=datetime.fromisoformat(budget_data["created_at"]),
                updated_at=datetime.fromisoformat(budget_data["updated_at"])
            )

        budget = self._get_budget_from_db(budget_id)
        if not budget:
            raise Exception("预算不存在")

        redis_client.setex(cache_key, 3600, json.dumps(budget, default=str))

        return BudgetResponse(
            budget_id=budget["budget_id"],
            trip_id=budget["trip_id"],
            total_budget=budget["total_budget"],
            remaining_budget=budget["remaining_budget"],
            categories=[BudgetCategory(**cat) for cat in budget["categories"]],
            created_at=budget["created_at"],
            updated_at=budget["updated_at"]
        )

    def _get_budget_from_db(self, budget_id: str) -> Optional[Dict]:
        """从数据库获取预算"""
        if not self.budgets_collection:
            return None
        budget = self.budgets_collection.find_one({"budget_id": budget_id})
        if budget:
            budget.pop("_id", None)
        return budget
