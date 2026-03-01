"""
用户管理路由

提供以下API：
- GET /api/user/profile - 获取当前用户资料
- PUT /api/user/profile - 更新用户资料
- POST /api/user/avatar - 上传头像
- GET /api/user/stats - 获取旅行统计
- GET /api/user/visited-cities - 获取访问过的城市
- POST /api/user/change-password - 修改密码
"""

from typing import Optional, List
from fastapi import APIRouter, HTTPException, status, Depends, UploadFile, File
from pydantic import BaseModel, EmailStr, Field
from loguru import logger

from ...services.user_service import get_user_service
from ...services.storage_service import get_storage_service
from ...middleware.auth_middleware import get_current_user, CurrentUser
from ...utils.response import ApiResponse


router = APIRouter(prefix="/user", tags=["用户管理"])


# ========== 请求模型 ==========

class UpdateProfileRequest(BaseModel):
    """更新用户资料请求"""
    username: Optional[str] = Field(None, min_length=3, max_length=50, description="用户名")
    email: Optional[EmailStr] = Field(None, description="邮箱")
    travel_preferences: Optional[List[str]] = Field(None, description="旅行偏好")


class UpdateVisitedCitiesRequest(BaseModel):
    """更新访问城市请求"""
    cities: List[str] = Field(..., description="城市列表")


class ChangePasswordRequest(BaseModel):
    """修改密码请求"""
    old_password: str = Field(..., description="旧密码")
    new_password: str = Field(..., min_length=8, description="新密码")


# ========== API端点 ==========

@router.get("/profile")
async def get_profile(current_user: CurrentUser = Depends(get_current_user)):
    """
    获取当前用户资料

    包含基本信息和用户档案
    """
    try:
        user_service = get_user_service()

        profile = await user_service.get_user_profile(current_user.id)

        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户资料不存在"
            )

        return ApiResponse.success(data=profile, msg="获取成功")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取用户资料失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取用户资料失败"
        )


@router.put("/profile")
async def update_profile(
    request: UpdateProfileRequest,
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    更新用户资料

    可更新用户名、邮箱、旅行偏好
    """
    try:
        user_service = get_user_service()

        if not any([request.username, request.email, request.travel_preferences]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="没有提供更新字段"
            )

        success = await user_service.update_user_profile(
            user_id=current_user.id,
            username=request.username,
            email=request.email,
            travel_preferences=request.travel_preferences
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="更新用户资料失败"
            )

        logger.info(f"用户资料已更新: {current_user.username}")

        return ApiResponse.success(data={}, msg="用户资料已更新")

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新用户资料失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="更新用户资料失败"
        )


@router.post("/avatar")
async def upload_avatar(
    file: UploadFile = File(...),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    上传头像

    支持的格式：JPEG, PNG, GIF
    最大文件大小：5MB
    """
    try:
        logger.info(f"开始处理头像上传请求: 用户={current_user.username}, 文件名={file.filename}, MIME类型={file.content_type}")

        # 验证文件类型
        allowed_types = ["image/jpeg", "image/png", "image/gif"]
        if file.content_type not in allowed_types:
            logger.warning(f"文件类型不支持: {file.content_type}, 允许的类型: {allowed_types}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="不支持的文件格式，请上传JPEG、PNG或GIF图片"
            )

        # 验证文件大小（5MB）
        logger.info("开始读取文件内容")
        file_content = await file.read()
        file_size = len(file_content)
        max_size = 5 * 1024 * 1024  # 5MB
        logger.info(f"文件大小: {file_size}字节, 最大允许: {max_size}字节")

        if file_size > max_size:
            logger.warning(f"文件大小超过限制: {file_size}字节 > {max_size}字节")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="文件大小超过5MB限制"
            )

        # 重置文件指针
        await file.seek(0)
        logger.info("文件指针已重置")

        # 上传文件到OSS（如果启用）或本地存储
        logger.info("开始上传文件到存储服务")
        storage_service = get_storage_service()
        avatar_url = await storage_service.upload_avatar(file, current_user.id)
        logger.info(f"文件上传成功，URL: {avatar_url}")

        # 更新用户头像URL
        logger.info("开始更新用户头像URL")
        user_service = get_user_service()
        await user_service.update_avatar(current_user.id, avatar_url)
        logger.info(f"用户头像URL已更新: {current_user.username} -> {avatar_url}")

        return ApiResponse.success(data={"avatar_url": avatar_url}, msg="头像上传成功")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"上传头像失败: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="上传头像失败"
        )


@router.get("/stats")
async def get_stats(current_user: CurrentUser = Depends(get_current_user)):
    """
    获取当前用户的旅行统计

    包括总计划数、已完成数、收藏数、访问城市数
    """
    try:
        user_service = get_user_service()

        stats = await user_service.get_user_stats(current_user.id)

        return ApiResponse.success(data=stats, msg="获取成功")

    except Exception as e:
        logger.error(f"获取用户统计失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取用户统计失败"
        )


@router.get("/visited-cities")
async def get_visited_cities(current_user: CurrentUser = Depends(get_current_user)):
    """
    获取当前用户访问过的城市列表

    按访问时间排序
    """
    try:
        user_service = get_user_service()

        cities = user_service.get_visited_cities(current_user.id)

        return ApiResponse.success(data={"cities": cities}, msg="获取成功")

    except Exception as e:
        logger.error(f"获取访问城市列表失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取访问城市列表失败"
        )


@router.put("/visited-cities")
async def update_visited_cities(
    request: UpdateVisitedCitiesRequest,
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    更新当前用户访问过的城市列表

    允许用户手动管理访问过的城市
    """
    try:
        user_service = get_user_service()

        cities = user_service.update_visited_cities(current_user.id, request.cities)

        logger.info(f"用户 {current_user.username} 更新了访问城市列表")

        return ApiResponse.success(data={"cities": cities}, msg="城市列表已更新")

    except Exception as e:
        logger.error(f"更新访问城市列表失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="更新访问城市列表失败"
        )


@router.post("/change-password")
async def change_password(
    request: ChangePasswordRequest,
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    修改密码

    需要验证旧密码，新密码必须符合强度要求
    """
    try:
        user_service = get_user_service()

        success = user_service.change_password(
            user_id=current_user.id,
            old_password=request.old_password,
            new_password=request.new_password
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="修改密码失败"
            )

        logger.info(f"密码已修改: {current_user.username}")

        return ApiResponse.success(data={}, msg="密码修改成功")

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"修改密码失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="修改密码失败"
        )
