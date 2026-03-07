"""实时信息系统API路由"""

from fastapi import APIRouter, Depends, Query, HTTPException
from typing import Optional, List
from ...services.real_time_service import (
    RealTimeService,
    RealTimeRequest,
    RealTimeResponse
)
from ...utils.response import ApiResponse, ResponseCode

router = APIRouter(prefix="/real-time", tags=["实时信息系统"])


def get_real_time_service() -> RealTimeService:
    """获取实时信息服务实例"""
    from ...services.real_time_service import get_real_time_service
    return get_real_time_service()


@router.post("/info", summary="获取实时信息", response_model=RealTimeResponse)
async def get_real_time_info(
    request: RealTimeRequest,
    real_time_service: RealTimeService = Depends(get_real_time_service)
):
    """
    获取实时信息，包括交通、天气、活动等
    """
    try:
        result = await real_time_service.get_real_time_info(request)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=ResponseCode.INTERNAL_ERROR,
            detail=f"获取实时信息失败: {str(e)}"
        )


@router.get("/overview", summary="获取实时信息概览")
async def get_real_time_overview(
    user_id: str = Query(..., description="用户ID"),
    location: Optional[str] = Query(None, description="当前位置"),
    real_time_service: RealTimeService = Depends(get_real_time_service)
):
    """
    获取实时信息概览，包括交通、天气、活动等
    """
    try:
        request = RealTimeRequest(
            user_id=user_id,
            location=location,
            type="all"
        )
        result = await real_time_service.get_real_time_info(request)
        return ApiResponse.success(data=result.model_dump())
    except Exception as e:
        raise HTTPException(
            status_code=ResponseCode.INTERNAL_ERROR,
            detail=f"获取实时信息概览失败: {str(e)}"
        )
