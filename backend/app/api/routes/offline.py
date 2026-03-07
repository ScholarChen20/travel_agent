"""离线功能API路由"""

from fastapi import APIRouter, Depends, HTTPException, Path, Query
from typing import Optional
from ...services.offline_service import (
    OfflineService,
    DownloadMapRequest,
    DownloadMapResponse,
    SyncOfflineDataRequest,
    SyncOfflineDataResponse
)
from ...utils.response import ApiResponse, ResponseCode

router = APIRouter(prefix="/offline", tags=["离线功能支持"])


def get_offline_service() -> OfflineService:
    """获取离线功能服务实例"""
    return OfflineService()


@router.post("/map/download", summary="下载离线地图")
async def download_map(
    request: DownloadMapRequest,
    offline_service: OfflineService = Depends(get_offline_service)
):
    """
    下载指定城市的离线地图数据
    """
    try:
        result = offline_service.download_map(request)
        return ApiResponse.success(data=result.model_dump())
    except Exception as e:
        raise HTTPException(
            status_code=ResponseCode.INTERNAL_ERROR,
            detail=f"下载离线地图失败: {str(e)}"
        )


@router.post("/data/sync", summary="同步离线数据")
async def sync_offline_data(
    request: SyncOfflineDataRequest,
    offline_service: OfflineService = Depends(get_offline_service)
):
    """
    同步用户的离线数据到服务器
    """
    try:
        result = offline_service.sync_offline_data(request)
        return ApiResponse.success(data=result.model_dump())
    except Exception as e:
        raise HTTPException(
            status_code=ResponseCode.INTERNAL_ERROR,
            detail=f"同步离线数据失败: {str(e)}"
        )


@router.get("/data/{user_id}", summary="获取离线数据")
async def get_offline_data(
    user_id: str = Path(..., description="用户ID"),
    sync_id: Optional[str] = Query(None, description="同步ID，可选，不指定则返回最新数据"),
    offline_service: OfflineService = Depends(get_offline_service)
):
    """
    获取用户的离线数据
    """
    try:
        data = offline_service.get_offline_data(user_id, sync_id)
        return ApiResponse.success(data=data)
    except Exception as e:
        raise HTTPException(
            status_code=ResponseCode.INTERNAL_ERROR,
            detail=f"获取离线数据失败: {str(e)}"
        )
