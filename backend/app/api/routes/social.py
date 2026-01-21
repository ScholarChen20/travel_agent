"""
社交功能路由

提供以下API：
- POST /api/social/posts - 创建帖子
- POST /api/social/posts/media - 上传媒体文件
- GET /api/social/posts - 获取Feed流
- GET /api/social/posts/{post_id} - 获取帖子详情
- POST /api/social/posts/{post_id}/like - 点赞/取消
- POST /api/social/posts/{post_id}/comments - 发表评论
- GET /api/social/posts/{post_id}/comments - 获取评论列表
- POST /api/social/users/{user_id}/follow - 关注/取消关注
- GET /api/social/users/{user_id}/posts - 用户主页帖子
- GET /api/social/tags - 热门标签
- GET /api/social/tags/{tag_name}/posts - 按标签查询
"""

from typing import Optional, List
from datetime import datetime
from fastapi import APIRouter, HTTPException, status, Depends, UploadFile, File, Query
from pydantic import BaseModel, Field
from loguru import logger

from ...services.social_service import get_social_service
from ...services.storage_service import get_storage_service
from ...middleware.auth_middleware import get_current_user, CurrentUser
from ...utils.response import ApiResponse, ResponseCode


router = APIRouter(prefix="/social", tags=["社交功能"])


# ========== 请求/响应模型 ==========

class CreatePostRequest(BaseModel):
    """创建帖子请求"""
    title: Optional[str] = Field(None, min_length=1, max_length=200, description="标题")
    content: str = Field(..., min_length=1, max_length=5000, description="内容")
    media_urls: Optional[List[str]] = Field(None, description="媒体文件URL列表")
    tags: Optional[List[str]] = Field(None, description="标签列表")
    location: Optional[str] = Field(None, description="位置")
    trip_plan_id: Optional[str] = Field(None, description="关联的旅行计划ID")


class PostResponse(BaseModel):
    """帖子响应"""
    post_id: str = Field(..., description="帖子ID")
    message: str = Field(..., description="消息")


class FeedResponse(BaseModel):
    """Feed流响应"""
    total: int = Field(..., description="总数")
    posts: List[dict] = Field(..., description="帖子列表")


class CommentRequest(BaseModel):
    """评论请求"""
    content: str = Field(..., min_length=1, max_length=500, description="评论内容")
    parent_id: Optional[str] = Field(None, description="父评论ID")


class CommentResponse(BaseModel):
    """评论响应"""
    comment_id: str = Field(..., description="评论ID")
    message: str = Field(..., description="消息")


class LikeResponse(BaseModel):
    """点赞响应"""
    liked: bool = Field(..., description="是否已点赞")
    message: str = Field(..., description="消息")


class FollowResponse(BaseModel):
    """关注响应"""
    following: bool = Field(..., description="是否已关注")
    message: str = Field(..., description="消息")


class MediaUploadResponse(BaseModel):
    """媒体上传响应"""
    url: str = Field(..., description="文件URL")
    thumbnail_url: Optional[str] = Field(None, description="缩略图URL")


# ========== API端点 ==========

@router.post("/posts")
async def create_post(
    request: CreatePostRequest,
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    创建帖子

    支持：
    - 文本内容
    - 媒体文件（图片/视频）
    - 标签
    - 位置
    - 关联旅行计划
    """
    try:
        social_service = get_social_service()

        # Use first 50 chars of content as title if not provided
        title = request.title or request.content[:50]

        post_id = await social_service.create_post(
            user_id=current_user.id,
            title=title,
            content=request.content,
            media_urls=request.media_urls,
            tags=request.tags,
            location=request.location,
            trip_plan_id=request.trip_plan_id
        )

        logger.info(f"帖子已创建: {post_id} (用户: {current_user.username})")

        return ApiResponse.created(
            data={"post_id": post_id},
            msg="帖子创建成功"
        )

    except ValueError as e:
        return ApiResponse.bad_request(msg=str(e))
    except Exception as e:
        logger.error(f"创建帖子失败: {str(e)}")
        return ApiResponse.internal_error(msg="创建帖子失败")


@router.post("/posts/media", response_model=MediaUploadResponse)
async def upload_media(
    file: UploadFile = File(...),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    上传媒体文件

    支持：
    - 图片：JPEG, PNG, GIF（最大5MB）
    - 视频：MP4（最大50MB）
    """
    try:
        # 验证文件类型
        allowed_image_types = ["image/jpeg", "image/png", "image/gif"]
        allowed_video_types = ["video/mp4"]
        allowed_types = allowed_image_types + allowed_video_types

        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="不支持的文件格式"
            )

        # 验证文件大小
        file_content = await file.read()
        file_size = len(file_content)

        if file.content_type in allowed_image_types:
            max_size = 5 * 1024 * 1024  # 5MB
        else:
            max_size = 50 * 1024 * 1024  # 50MB

        if file_size > max_size:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"文件大小超过限制（{max_size // (1024 * 1024)}MB）"
            )

        # 重置文件指针
        await file.seek(0)

        # 上传文件
        storage_service = get_storage_service()
        result = await storage_service.upload_media(
            file=file,
            user_id=current_user.id,
            generate_thumbnail=True
        )

        logger.info(f"媒体文件已上传: {result['url']} (用户: {current_user.username})")

        return MediaUploadResponse(
            url=result["url"],
            thumbnail_url=result.get("thumbnail_url")
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"上传媒体文件失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="上传媒体文件失败"
        )


@router.get("/posts")
async def get_feed(
    limit: int = Query(20, ge=1, le=100, description="返回数量"),
    offset: int = Query(0, ge=0, description="偏移量"),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    获取个性化Feed流

    混合策略：
    - 50% 关注用户的最新内容
    - 30% 热门内容
    - 20% 推荐内容
    """
    try:
        social_service = get_social_service()

        posts = await social_service.get_feed(
            user_id=current_user.id,
            limit=limit,
            offset=offset
        )

        return ApiResponse.success(
            data={
                "total": len(posts),
                "posts": posts
            },
            msg="获取成功"
        )

    except Exception as e:
        logger.error(f"获取Feed流失败: {str(e)}")
        return ApiResponse.internal_error(msg="获取Feed流失败")


@router.get("/posts/{post_id}")
async def get_post_detail(
    post_id: str,
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    获取帖子详情

    包含完整的帖子信息
    """
    try:
        social_service = get_social_service()

        post = await social_service.get_post_by_id(post_id)

        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="帖子不存在"
            )

        return post

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取帖子详情失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取帖子详情失败"
        )


@router.post("/posts/{post_id}/like")
async def like_post(
    post_id: str,
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    点赞/取消点赞

    切换点赞状态
    """
    try:
        social_service = get_social_service()

        liked = await social_service.like_post(
            user_id=current_user.id,
            post_id=post_id
        )

        message = "已点赞" if liked else "已取消点赞"
        logger.info(f"{message}: {post_id} (用户: {current_user.username})")

        return ApiResponse.success(
            data={"liked": liked},
            msg=message
        )

    except Exception as e:
        logger.error(f"点赞操作失败: {str(e)}")
        return ApiResponse.internal_error(msg="点赞操作失败")


@router.post("/posts/{post_id}/comments")
async def create_comment(
    post_id: str,
    request: CommentRequest,
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    发表评论

    支持回复评论（提供parent_id）
    """
    try:
        social_service = get_social_service()

        comment_id = await social_service.comment_on_post(
            user_id=current_user.id,
            post_id=post_id,
            content=request.content,
            parent_id=request.parent_id
        )

        logger.info(f"评论已发表: {comment_id} (帖子: {post_id}, 用户: {current_user.username})")

        # 返回完整的评论数据
        return ApiResponse.created(
            data={
                "comment_id": comment_id,
                "id": comment_id,
                "content": request.content,
                "user_id": current_user.id,
                "username": current_user.username,
                "user_avatar": current_user.avatar_url,
                "post_id": post_id,
                "parent_id": request.parent_id,
                "created_at": datetime.utcnow().isoformat()
            },
            msg="评论发表成功"
        )

    except ValueError as e:
        return ApiResponse.bad_request(msg=str(e))
    except Exception as e:
        logger.error(f"发表评论失败: {str(e)}")
        return ApiResponse.internal_error(msg="发表评论失败")


@router.get("/posts/{post_id}/comments")
async def get_comments(
    post_id: str,
    limit: int = Query(50, ge=1, le=100, description="返回数量"),
    offset: int = Query(0, ge=0, description="偏移量"),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    获取评论列表

    只返回顶级评论，回复需要单独查询
    """
    try:
        social_service = get_social_service()

        comments = await social_service.get_post_comments(
            post_id=post_id,
            limit=limit,
            offset=offset
        )

        return ApiResponse.success(
            data={
                "post_id": post_id,
                "total": len(comments),
                "comments": comments
            },
            msg="获取成功"
        )

    except Exception as e:
        logger.error(f"获取评论列表失败: {str(e)}")
        return ApiResponse.internal_error(msg="获取评论列表失败")


@router.post("/users/{user_id}/follow", response_model=FollowResponse)
async def follow_user(
    user_id: int,
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    关注/取消关注用户

    切换关注状态
    """
    try:
        social_service = get_social_service()

        following = await social_service.follow_user(
            follower_id=current_user.id,
            following_id=user_id
        )

        message = "已关注" if following else "已取消关注"
        logger.info(f"{message}: {current_user.id} -> {user_id}")

        return FollowResponse(
            following=following,
            message=message
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"关注操作失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="关注操作失败"
        )


@router.get("/users/{user_id}/posts", response_model=FeedResponse)
async def get_user_posts(
    user_id: int,
    limit: int = Query(20, ge=1, le=100, description="返回数量"),
    offset: int = Query(0, ge=0, description="偏移量"),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    获取用户主页帖子

    显示用户发布的所有帖子
    """
    try:
        social_service = get_social_service()

        posts = await social_service.get_user_posts(
            user_id=user_id,
            limit=limit,
            offset=offset
        )

        return FeedResponse(
            total=len(posts),
            posts=posts
        )

    except Exception as e:
        logger.error(f"获取用户帖子失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取用户帖子失败"
        )


@router.get("/tags")
async def get_popular_tags(
    limit: int = Query(20, ge=1, le=100, description="返回数量"),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    获取热门标签

    按使用次数排序
    """
    try:
        social_service = get_social_service()

        tags = await social_service.get_popular_tags(limit=limit)

        return {
            "total": len(tags),
            "tags": tags
        }

    except Exception as e:
        logger.error(f"获取热门标签失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取热门标签失败"
        )


@router.get("/tags/{tag_name}/posts", response_model=FeedResponse)
async def get_posts_by_tag(
    tag_name: str,
    limit: int = Query(20, ge=1, le=100, description="返回数量"),
    offset: int = Query(0, ge=0, description="偏移量"),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    按标签查询帖子

    获取包含指定标签的所有帖子
    """
    try:
        social_service = get_social_service()

        posts = await social_service.get_posts_by_tag(
            tag=tag_name,
            limit=limit,
            offset=offset
        )

        return FeedResponse(
            total=len(posts),
            posts=posts
        )

    except Exception as e:
        logger.error(f"按标签查询失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="按标签查询失败"
        )
