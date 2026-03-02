"""实时信息服务API路由"""

from fastapi import APIRouter, Depends, Query, HTTPException
from typing import Optional
from ...services.real_time_service import (
    RealTimeService,
    FlightStatusRequest,
    FlightStatusResponse,
    WeatherRequest,
    WeatherResponse,
    AttractionStatusRequest,
    AttractionStatusResponse
)
from ...utils.response import ApiResponse, ResponseCode

router = APIRouter(prefix="/real-time", tags=["实时信息服务"])


def get_real_time_service() -> RealTimeService:
    """获取实时信息服务实例"""
    return RealTimeService()


@router.post("/flight/status", summary="查询航班动态")
async def get_flight_status(
    request: FlightStatusRequest,
    real_time_service: RealTimeService = Depends(get_real_time_service)
):
    """
    查询航班动态信息
    """
    try:
        result = real_time_service.get_flight_status(request)
        return ApiResponse.success(data=result.model_dump())
    except Exception as e:
        raise HTTPException(
            status_code=ResponseCode.INTERNAL_ERROR,
            detail=f"查询航班动态失败: {str(e)}"
        )


@router.post("/weather", summary="查询天气")
async def get_weather(
    request: WeatherRequest,
    real_time_service: RealTimeService = Depends(get_real_time_service)
):
    """
    查询天气预报
    """
    try:
        result = real_time_service.get_weather(request)
        return ApiResponse.success(data=result.model_dump())
    except Exception as e:
        raise HTTPException(
            status_code=ResponseCode.INTERNAL_ERROR,
            detail=f"查询天气失败: {str(e)}"
        )


@router.post("/attraction/status", summary="查询景点状态")
async def get_attraction_status(
    request: AttractionStatusRequest,
    real_time_service: RealTimeService = Depends(get_real_time_service)
):
    """
    查询景点开放状态、拥挤程度等信息
    """
    try:
        result = real_time_service.get_attraction_status(request)
        return ApiResponse.success(data=result.model_dump())
    except Exception as e:
        raise HTTPException(
            status_code=ResponseCode.INTERNAL_ERROR,
            detail=f"查询景点状态失败: {str(e)}"
        )
