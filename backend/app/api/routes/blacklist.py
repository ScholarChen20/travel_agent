"""黑名单管理API路由"""

from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from loguru import logger

from ...services.anti_spam_service import get_anti_spam_service
from ...utils.response import ApiResponse


router = APIRouter(prefix="/blacklist", tags=["黑名单管理"])


# ========== 请求模型 ==========

class AddDeviceBlacklistRequest(BaseModel):
    """添加设备黑名单请求"""
    device_id: str = Field(..., description="设备ID")
    reason: Optional[str] = Field(None, description="拉黑原因")
    ttl_seconds: Optional[int] = Field(None, description="过期时间（秒），None表示永久")


class AddIPBlacklistRequest(BaseModel):
    """添加IP黑名单请求"""
    ip_address: str = Field(..., description="IP地址")
    reason: Optional[str] = Field(None, description="拉黑原因")
    ttl_seconds: Optional[int] = Field(None, description="过期时间（秒），None表示永久")


# ========== API端点 ==========

@router.post("/device")
async def add_device_to_blacklist(request: AddDeviceBlacklistRequest):
    """
    添加设备ID到黑名单
    """
    try:
        anti_spam = await get_anti_spam_service()
        success = await anti_spam.add_device_to_blacklist(
            device_id=request.device_id,
            reason=request.reason,
            ttl_seconds=request.ttl_seconds
        )

        if success:
            return ApiResponse.success(msg="设备已添加到黑名单")
        else:
            return ApiResponse.error(msg="添加设备到黑名单失败")

    except Exception as e:
        logger.error(f"添加设备到黑名单失败: {str(e)}")
        return ApiResponse.error(msg="服务器错误")


@router.post("/ip")
async def add_ip_to_blacklist(request: AddIPBlacklistRequest):
    """
    添加IP地址到黑名单
    """
    try:
        anti_spam = await get_anti_spam_service()
        success = await anti_spam.add_ip_to_blacklist(
            ip_address=request.ip_address,
            reason=request.reason,
            ttl_seconds=request.ttl_seconds
        )

        if success:
            return ApiResponse.success(msg="IP已添加到黑名单")
        else:
            return ApiResponse.error(msg="添加IP到黑名单失败")

    except Exception as e:
        logger.error(f"添加IP到黑名单失败: {str(e)}")
        return ApiResponse.error(msg="服务器错误")


@router.delete("/device/remove")
async def remove_device_from_blacklist(device_id: str = Query(..., description="设备ID")):
    """
    从黑名单中移除设备ID
    """
    try:
        anti_spam = await get_anti_spam_service()
        success = await anti_spam.remove_device_from_blacklist(device_id)

        if success:
            return ApiResponse.success(msg="设备已从黑名单移除")
        else:
            return ApiResponse.error(msg="设备不在黑名单中")

    except Exception as e:
        logger.error(f"从黑名单移除设备失败: {str(e)}")
        return ApiResponse.error(msg="服务器错误")


@router.delete("/ip/remove")
async def remove_ip_from_blacklist(ip_address: str = Query(..., description="IP地址")):
    """
    从黑名单中移除IP地址
    """
    try:
        anti_spam = await get_anti_spam_service()
        success = await anti_spam.remove_ip_from_blacklist(ip_address)

        if success:
            return ApiResponse.success(msg="IP已从黑名单移除")
        else:
            return ApiResponse.error(msg="IP不在黑名单中")

    except Exception as e:
        logger.error(f"从黑名单移除IP失败: {str(e)}")
        return ApiResponse.error(msg="服务器错误")


@router.post("/rebuild")
async def rebuild_bloom_filter():
    """
    重建布隆过滤器
    """
    try:
        anti_spam = await get_anti_spam_service()
        await anti_spam.rebuild_bloom_filter()
        return ApiResponse.success(msg="布隆过滤器重建完成")

    except Exception as e:
        logger.error(f"重建布隆过滤器失败: {str(e)}")
        return ApiResponse.error(msg="服务器错误")


@router.get("/list")
async def get_all_blacklists():
    """
    获取所有黑名单信息
    """
    try:
        anti_spam = await get_anti_spam_service()
        blacklists = await anti_spam.blacklist_manager.get_all_blacklists()
        return ApiResponse.success(data=blacklists, msg="获取黑名单成功")

    except Exception as e:
        logger.error(f"获取黑名单失败: {str(e)}")
        return ApiResponse.error(msg="服务器错误")
