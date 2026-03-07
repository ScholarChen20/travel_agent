"""预算管理系统API路由"""

from fastapi import APIRouter, Depends, Query, HTTPException
from typing import Optional, List
from ...services.budget_service import (
    BudgetService,
    BudgetRequest,
    ExpenseRequest,
    BudgetResponse,
    ExpenseResponse,
    BudgetStatsResponse
)
from ...utils.response import ApiResponse, ResponseCode

router = APIRouter(prefix="/budget", tags=["预算管理系统"])


def get_budget_service() -> BudgetService:
    """获取预算服务实例"""
    from ...services.budget_service import get_budget_service
    return get_budget_service()


@router.post("/create", summary="创建预算", response_model=BudgetResponse)
async def create_budget(
    request: BudgetRequest,
    budget_service: BudgetService = Depends(get_budget_service)
):
    """
    创建预算，设置旅行预算和时间范围
    """
    try:
        result = await budget_service.create_budget(request)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=ResponseCode.INTERNAL_ERROR,
            detail=f"创建预算失败: {str(e)}"
        )


@router.post("/expense/add", summary="添加支出", response_model=ExpenseResponse)
async def add_expense(
    request: ExpenseRequest,
    budget_service: BudgetService = Depends(get_budget_service)
):
    """
    添加旅行支出记录
    """
    try:
        result = await budget_service.add_expense(request)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=ResponseCode.INTERNAL_ERROR,
            detail=f"添加支出失败: {str(e)}"
        )


@router.get("/stats", summary="获取预算统计", response_model=BudgetStatsResponse)
async def get_budget_stats(
    user_id: str = Query(..., description="用户ID"),
    budget_service: BudgetService = Depends(get_budget_service)
):
    """
    获取预算统计信息，包括总预算、已使用金额、剩余金额等
    """
    try:
        result = await budget_service.get_budget_stats(user_id)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=ResponseCode.INTERNAL_ERROR,
            detail=f"获取预算统计失败: {str(e)}"
        )


@router.get("/overview", summary="获取预算概览")
async def get_budget_overview(
    user_id: str = Query(..., description="用户ID"),
    budget_service: BudgetService = Depends(get_budget_service)
):
    """
    获取预算概览信息，包括预算使用情况、支出分布等
    """
    try:
        stats = await budget_service.get_budget_stats(user_id)
        return ApiResponse.success(data=stats.model_dump())
    except Exception as e:
        raise HTTPException(
            status_code=ResponseCode.INTERNAL_ERROR,
            detail=f"获取预算概览失败: {str(e)}"
        )
