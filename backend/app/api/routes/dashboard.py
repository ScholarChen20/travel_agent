"""首页仪表盘API路由"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
from ...services.dashboard_service import (
    DashboardService,
    DateRangeRequest
)
from ...utils.response import ApiResponse, ResponseCode

router = APIRouter(prefix="/dashboard", tags=["首页仪表盘"])


def get_dashboard_service() -> DashboardService:
    """获取仪表盘服务实例"""
    from ...services.dashboard_service import get_dashboard_service
    return get_dashboard_service()


@router.get("/overview", summary="获取首页综合指标")
async def get_dashboard_overview(
    dashboard_service: DashboardService = Depends(get_dashboard_service)
):
    """
    获取首页所需的所有核心指标，包括用户统计、内容统计和业务指标
    """
    try:
        result = await dashboard_service.get_overview()
        return ApiResponse.success(data=result.model_dump())
    except Exception as e:
        raise HTTPException(
            status_code=ResponseCode.INTERNAL_ERROR,
            detail=f"获取首页综合指标失败: {str(e)}"
        )


@router.get("/user-stats", summary="获取用户统计数据")
async def get_user_stats(
    dashboard_service: DashboardService = Depends(get_dashboard_service)
):
    """
    获取用户相关的统计数据，包括总用户数、活跃用户数、新增用户数等
    """
    try:
        result = await dashboard_service.get_user_stats()
        return ApiResponse.success(data=result.model_dump())
    except Exception as e:
        raise HTTPException(
            status_code=ResponseCode.INTERNAL_ERROR,
            detail=f"获取用户统计数据失败: {str(e)}"
        )


@router.get("/content-stats", summary="获取内容统计数据")
async def get_content_stats(
    dashboard_service: DashboardService = Depends(get_dashboard_service)
):
    """
    获取内容相关的统计数据，包括旅行计划数、景点数、帖子数、评论数等
    """
    try:
        result = await dashboard_service.get_content_stats()
        return ApiResponse.success(data=result.model_dump())
    except Exception as e:
        raise HTTPException(
            status_code=ResponseCode.INTERNAL_ERROR,
            detail=f"获取内容统计数据失败: {str(e)}"
        )


@router.get("/business-stats", summary="获取业务指标数据")
async def get_business_stats(
    dashboard_service: DashboardService = Depends(get_dashboard_service)
):
    """
    获取业务相关的指标数据，包括旅行计划创建量、用户留存率、平均旅行计划长度等
    """
    try:
        result = await dashboard_service.get_business_stats()
        return ApiResponse.success(data=result.model_dump())
    except Exception as e:
        raise HTTPException(
            status_code=ResponseCode.INTERNAL_ERROR,
            detail=f"获取业务指标数据失败: {str(e)}"
        )


@router.get("/business-trend", summary="获取业务趋势数据")
async def get_business_trend(
    start_date: Optional[str] = Query(None, description="开始日期，格式: YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="结束日期，格式: YYYY-MM-DD"),
    dashboard_service: DashboardService = Depends(get_dashboard_service)
):
    """
    获取业务趋势数据，包括旅行计划创建趋势、用户注册趋势、用户活跃趋势等
    """
    try:
        request = DateRangeRequest(start_date=start_date, end_date=end_date) if start_date or end_date else None
        result = await dashboard_service.get_business_trend(request)
        return ApiResponse.success(data=result.model_dump())
    except Exception as e:
        raise HTTPException(
            status_code=ResponseCode.INTERNAL_ERROR,
            detail=f"获取业务趋势数据失败: {str(e)}"
        )
