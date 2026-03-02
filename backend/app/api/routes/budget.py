"""预算管理API路由"""

from fastapi import APIRouter, Depends, HTTPException, Path
from ...services.budget_service import (
    BudgetService,
    BudgetCreateRequest,
    ExpenseAddRequest,
    BudgetResponse
)
from ...utils.response import ApiResponse, ResponseCode

router = APIRouter(prefix="/budget", tags=["预算管理模块"])


def get_budget_service() -> BudgetService:
    """获取预算服务实例"""
    return BudgetService()


@router.post("/create", summary="创建预算")
async def create_budget(
    request: BudgetCreateRequest,
    budget_service: BudgetService = Depends(get_budget_service)
):
    """
    创建旅行预算
    """
    try:
        result = budget_service.create_budget(request)
        return ApiResponse.created(data=result.model_dump())
    except Exception as e:
        raise HTTPException(
            status_code=ResponseCode.INTERNAL_ERROR,
            detail=f"创建预算失败: {str(e)}"
        )


@router.post("/expense", summary="添加消费记录")
async def add_expense(
    request: ExpenseAddRequest,
    budget_service: BudgetService = Depends(get_budget_service)
):
    """
    添加消费记录到预算
    """
    try:
        result = budget_service.add_expense(request)
        return ApiResponse.success(data=result.model_dump())
    except Exception as e:
        raise HTTPException(
            status_code=ResponseCode.INTERNAL_ERROR,
            detail=f"添加消费记录失败: {str(e)}"
        )


@router.get("/{budget_id}", summary="获取预算详情")
async def get_budget(
    budget_id: str = Path(..., description="预算ID"),
    budget_service: BudgetService = Depends(get_budget_service)
):
    """
    获取预算详情
    """
    try:
        result = budget_service.get_budget(budget_id)
        return ApiResponse.success(data=result.model_dump())
    except Exception as e:
        raise HTTPException(
            status_code=ResponseCode.NOT_FOUND,
            detail=str(e)
        )
