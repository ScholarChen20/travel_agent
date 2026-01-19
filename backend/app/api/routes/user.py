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


router = APIRouter(prefix="/user", tags=["用户管理"])


# ========== 请求/响应模型 ==========

class UserProfileResponse(BaseModel):
    """用户资料响应"""
    id: int = Field(..., description="用户ID")
    username: str = Field(..., description="用户名")
    email: str = Field(..., description="邮箱")
    role: str = Field(..., description="角色")
    avatar_url: Optional[str] = Field(None, description="头像URL")
    is_verified: bool = Field(..., description="是否已验证邮箱")
    is_active: bool = Field(..., description="是否激活")
    created_at: Optional[str] = Field(None, description="注册时间")
    last_login_at: Optional[str] = Field(None, description="最后登录时间")
    profile: dict = Field(..., description="用户档案")


class UpdateProfileRequest(BaseModel):
    """更新用户资料请求"""
    username: Optional[str] = Field(None, min_length=3, max_length=50, description="用户名")
    email: Optional[EmailStr] = Field(None, description="邮箱")
    travel_preferences: Optional[List[str]] = Field(None, description="旅行偏好")


class UserStatsResponse(BaseModel):
    """用户统计响应"""
    total_trips: int = Field(..., description="总计划数")
    completed_trips: int = Field(..., description="已完成计划数")
    favorite_trips: int = Field(..., description="收藏计划数")
    total_cities: int = Field(..., description="访问城市数")


class VisitedCitiesResponse(BaseModel):
    """访问城市响应"""
    cities: List[str] = Field(..., description="城市列表")


class ChangePasswordRequest(BaseModel):
    """修改密码请求"""
    old_password: str = Field(..., description="旧密码")
    new_password: str = Field(..., min_length=8, description="新密码")


class AvatarUploadResponse(BaseModel):
    """头像上传响应"""
    avatar_url: str = Field(..., description="头像URL")


class MessageResponse(BaseModel):
    """通用消息响应"""
    message: str = Field(..., description="消息内容")


# ========== API端点 ==========

@router.get("/profile", response_model=UserProfileResponse)
async def get_profile(current_user: CurrentUser = Depends(get_current_user)):
    """
    获取当前用户资料

    包含基本信息和用户档案
    """
    try:
        user_service = get_user_service()

        # 获取用户资料
        profile = user_service.get_user_profile(current_user.id)

        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户资料不存在"
            )

        return UserProfileResponse(**profile)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取用户资料失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取用户资料失败"
        )


@router.put("/profile", response_model=MessageResponse)
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

        # 检查是否有更新字段
        if not any([request.username, request.email, request.travel_preferences]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="没有提供更新字段"
            )

        # 更新用户资料
        success = user_service.update_user_profile(
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

        return MessageResponse(message="用户资料已更新")

    except ValueError as e:
        # 用户名或邮箱冲突
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


@router.post("/avatar", response_model=AvatarUploadResponse)
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
        # 验证文件类型
        allowed_types = ["image/jpeg", "image/png", "image/gif"]
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="不支持的文件格式，请上传JPEG、PNG或GIF图片"
            )

        # 验证文件大小（5MB）
        file_content = await file.read()
        file_size = len(file_content)
        max_size = 5 * 1024 * 1024  # 5MB

        if file_size > max_size:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="文件大小超过5MB限制"
            )

        # 重置文件指针
        await file.seek(0)

        # 上传文件
        storage_service = get_storage_service()
        avatar_url = await storage_service.upload_avatar(file, current_user.id)

        # 更新用户头像URL
        user_service = get_user_service()
        user_service.update_avatar(current_user.id, avatar_url)

        logger.info(f"头像已上传: {current_user.username} -> {avatar_url}")

        return AvatarUploadResponse(avatar_url=avatar_url)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"上传头像失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="上传头像失败"
        )


@router.get("/stats", response_model=UserStatsResponse)
async def get_stats(current_user: CurrentUser = Depends(get_current_user)):
    """
    获取当前用户的旅行统计

    包括总计划数、已完成数、收藏数、访问城市数
    """
    try:
        user_service = get_user_service()

        # 获取统计数据
        stats = await user_service.get_user_stats(current_user.id)

        return UserStatsResponse(**stats)

    except Exception as e:
        logger.error(f"获取用户统计失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取用户统计失败"
        )


@router.get("/visited-cities", response_model=VisitedCitiesResponse)
async def get_visited_cities(current_user: CurrentUser = Depends(get_current_user)):
    """
    获取当前用户访问过的城市列表

    按访问时间排序
    """
    try:
        user_service = get_user_service()

        # 获取城市列表
        cities = user_service.get_visited_cities(current_user.id)

        return VisitedCitiesResponse(cities=cities)

    except Exception as e:
        logger.error(f"获取访问城市列表失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取访问城市列表失败"
        )


@router.post("/change-password", response_model=MessageResponse)
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

        # 修改密码
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

        return MessageResponse(message="密码修改成功")

    except ValueError as e:
        # 密码强度不足或旧密码错误
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
