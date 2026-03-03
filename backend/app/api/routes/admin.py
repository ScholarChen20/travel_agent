"""
管理后台路由

提供以下API（需要admin角色）：
- GET /api/admin/users - 用户列表
- PUT /api/admin/users/{user_id}/status - 激活/禁用用户
- GET /api/admin/comments - 评论列表
- DELETE /api/admin/comments/{comment_id} - 删除评论
- GET /api/admin/posts/moderation - 待审核内容
- PUT /api/admin/posts/{post_id}/moderate - 审核内容
- GET /api/admin/stats - 系统统计
- GET /api/admin/logs/audit - 审计日志
- GET /api/admin/logs/tools - 工具调用日志
- POST /api/admin/backup/mysql - 触发MySQL备份
- POST /api/admin/backup/mongodb - 触发MongoDB备份
- GET /api/admin/health - 系统健康检查
- GET /api/admin/metrics - 性能指标
"""

from typing import Optional
from fastapi import APIRouter, HTTPException, status, Depends, Query, Request
from pydantic import BaseModel, Field
from loguru import logger
import subprocess

from ...services.admin_service import get_admin_service
from ...services.monitoring_service import get_monitoring_service
from ...middleware.auth_middleware import get_current_user, CurrentUser
from ...utils.response import ApiResponse
from ...utils.audit_logger import save_audit_log


router = APIRouter(prefix="/admin", tags=["管理后台"])


# ========== 权限检查 ==========

def require_admin(current_user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
    """
    要求admin角色

    Args:
        current_user: 当前用户

    Returns:
        CurrentUser: 当前用户

    Raises:
        HTTPException: 如果不是admin
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要管理员权限"
        )
    return current_user


# ========== 请求模型 ==========

class UpdateUserStatusRequest(BaseModel):
    """更新用户状态请求"""
    is_active: bool = Field(..., description="激活状态")


class ModeratePostRequest(BaseModel):
    """审核帖子请求"""
    status: str = Field(..., description="审核状态（approved/rejected）")
    reason: Optional[str] = Field(None, description="审核原因")


# ========== API端点 ==========

@router.get("/users")
async def list_users(
    username: Optional[str] = Query(None, description="用户名搜索"),
    email: Optional[str] = Query(None, description="邮箱搜索"),
    role: Optional[str] = Query(None, description="角色筛选(admin/user)"),
    is_active: Optional[bool] = Query(None, description="激活状态筛选"),
    is_verified: Optional[bool] = Query(None, description="验证状态筛选"),
    limit: int = Query(50, ge=1, le=100, description="返回数量"),
    offset: int = Query(0, ge=0, description="偏移量"),
    admin_user: CurrentUser = Depends(require_admin)
):
    """
    获取用户列表

    需要admin角色
    """
    try:
        admin_service = get_admin_service()

        result = admin_service.list_users(
            username=username,
            email=email,
            role=role,
            is_active=is_active,
            is_verified=is_verified,
            limit=limit,
            offset=offset
        )

        return ApiResponse.success(data=result, msg="获取成功")

    except Exception as e:
        logger.error(f"获取用户列表失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取用户列表失败"
        )


@router.put("/users/{user_id}/status")
async def update_user_status(
    user_id: int,
    request: UpdateUserStatusRequest,
    http_request: Request,
    admin_user: CurrentUser = Depends(require_admin)
):
    """
    激活/禁用用户

    需要admin角色
    """
    try:
        admin_service = get_admin_service()

        success = admin_service.update_user_status(
            user_id=user_id,
            is_active=request.is_active
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )

        action = "激活" if request.is_active else "禁用"
        logger.info(f"用户已{action}: {user_id} (操作者: {admin_user.username})")

        await save_audit_log(
            user_id=admin_user.id,
            action=action,
            resource="用户",
            resource_id=str(user_id),
            details={"is_active": request.is_active},
            request=http_request
        )

        return ApiResponse.success(data={}, msg=f"用户已{action}")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新用户状态失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="更新用户状态失败"
        )


@router.get("/comments")
async def list_comments(
    content: Optional[str] = Query(None, description="评论内容搜索"),
    post_id: Optional[str] = Query(None, description="帖子ID筛选"),
    user_id: Optional[int] = Query(None, description="用户ID筛选"),
    limit: int = Query(50, ge=1, le=100, description="返回数量"),
    offset: int = Query(0, ge=0, description="偏移量"),
    admin_user: CurrentUser = Depends(require_admin)
):
    """
    获取评论列表

    需要admin角色
    """
    try:
        admin_service = get_admin_service()

        result = await admin_service.list_comments(
            content=content,
            post_id=post_id,
            user_id=user_id,
            limit=limit,
            offset=offset
        )

        return ApiResponse.success(data=result, msg="获取成功")

    except Exception as e:
        logger.error(f"获取评论列表失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取评论列表失败"
        )


@router.delete("/comments/{comment_id}")
async def delete_comment(
    comment_id: str,
    http_request: Request,
    admin_user: CurrentUser = Depends(require_admin)
):
    """
    删除评论

    需要admin角色
    """
    try:
        admin_service = get_admin_service()

        success = await admin_service.delete_comment(comment_id)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="评论不存在"
            )

        logger.info(f"评论已删除: {comment_id} (操作者: {admin_user.username})")

        await save_audit_log(
            user_id=admin_user.id,
            action="删除",
            resource="评论",
            resource_id=comment_id,
            request=http_request
        )

        return ApiResponse.success(data={}, msg="评论已删除")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除评论失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="删除评论失败"
        )


@router.get("/posts/moderation")
async def get_posts_for_moderation(
    keyword: Optional[str] = Query(None, description="关键词搜索（标题/内容）"),
    status: str = Query("pending", description="审核状态"),
    limit: int = Query(50, ge=1, le=100, description="返回数量"),
    offset: int = Query(0, ge=0, description="偏移量"),
    admin_user: CurrentUser = Depends(require_admin)
):
    """
    获取待审核内容

    需要admin角色
    """
    try:
        admin_service = get_admin_service()

        result = await admin_service.get_posts_for_moderation(
            keyword=keyword,
            status=status,
            limit=limit,
            offset=offset
        )

        return ApiResponse.success(data=result, msg="获取成功")

    except Exception as e:
        logger.error(f"获取待审核内容失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取待审核内容失败"
        )


@router.put("/posts/{post_id}/moderate")
async def moderate_post(
    post_id: str,
    request: ModeratePostRequest,
    admin_user: CurrentUser = Depends(require_admin)
):
    """
    审核帖子

    需要admin角色
    """
    try:
        if request.status not in ["approved", "rejected"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="无效的审核状态"
            )

        admin_service = get_admin_service()

        success = await admin_service.moderate_post(
            post_id=post_id,
            status=request.status,
            reason=request.reason
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="帖子不存在"
            )

        logger.info(f"帖子已审核: {post_id} -> {request.status} (操作者: {admin_user.username})")

        return ApiResponse.success(data={}, msg=f"帖子已{request.status}")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"审核帖子失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="审核帖子失败"
        )


@router.get("/stats")
async def get_system_stats(
    admin_user: CurrentUser = Depends(require_admin)
):
    """
    获取系统统计

    需要admin角色
    """
    try:
        admin_service = get_admin_service()

        stats = await admin_service.get_system_stats()

        return ApiResponse.success(data=stats, msg="获取成功")

    except Exception as e:
        logger.error(f"获取系统统计失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取系统统计失败"
        )


@router.get("/stats/visualization")
async def get_visualization_data(
    admin_user: CurrentUser = Depends(require_admin)
):
    """
    获取可视化图表数据

    需要admin角色
    返回：
    - user_trend: 最近7天用户注册趋势
    - post_trend: 最近7天帖子发布趋势
    - moderation_distribution: 内容审核状态分布
    - user_activity: 用户活跃度分布
    - content_type_distribution: 内容类型分布
    - top_content: Top热门内容
    - interaction_stats: 互动统计数据
    """
    try:
        admin_service = get_admin_service()

        data = await admin_service.get_visualization_data()

        return ApiResponse.success(data=data, msg="获取成功")

    except Exception as e:
        logger.error(f"获取可视化数据失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取可视化数据失败"
        )


@router.get("/logs/audit")
async def get_audit_logs(
    resource_id: Optional[str] = Query(None, description="资源ID搜索"),
    user_id: Optional[int] = Query(None, description="用户ID筛选"),
    action: Optional[str] = Query(None, description="操作类型筛选"),
    resource: Optional[str] = Query(None, description="资源类型筛选"),
    method: Optional[str] = Query(None, description="HTTP方法筛选 (GET/POST/PUT/DELETE)"),
    path_keyword: Optional[str] = Query(None, description="请求路径模糊匹配"),
    status_code: Optional[int] = Query(None, description="响应状态码筛选（传入 2/4/5 匹配 2xx/4xx/5xx）"),
    response_status: Optional[str] = Query(None, description="响应结果筛选 (success/error)"),
    limit: int = Query(100, ge=1, le=500, description="返回数量"),
    offset: int = Query(0, ge=0, description="偏移量"),
    admin_user: CurrentUser = Depends(require_admin)
):
    """
    获取审计日志

    需要admin角色
    """
    try:
        admin_service = get_admin_service()

        result = admin_service.get_audit_logs(
            resource_id=resource_id,
            user_id=user_id,
            action=action,
            resource=resource,
            method=method,
            path_keyword=path_keyword,
            status_code=status_code,
            response_status=response_status,
            limit=limit,
            offset=offset
        )

        return ApiResponse.success(data=result, msg="获取成功")

    except Exception as e:
        logger.error(f"获取审计日志失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取审计日志失败"
        )


@router.get("/logs/tools")
async def get_tool_call_logs(
    admin_user: CurrentUser = Depends(require_admin)
):
    """
    获取工具调用统计

    需要admin角色
    """
    try:
        admin_service = get_admin_service()

        stats = await admin_service.get_tool_call_stats()

        return ApiResponse.success(data=stats, msg="获取成功")

    except Exception as e:
        logger.error(f"获取工具调用统计失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取工具调用统计失败"
        )


@router.post("/backup/mysql")
async def trigger_mysql_backup(
    admin_user: CurrentUser = Depends(require_admin)
):
    """
    触发MySQL备份

    需要admin角色
    """
    try:
        script_path = "backend/scripts/backup_mysql.sh"

        result = subprocess.run(
            ["bash", script_path],
            capture_output=True,
            text=True,
            timeout=300  # 5分钟超时
        )

        if result.returncode == 0:
            logger.info(f"MySQL备份成功 (操作者: {admin_user.username})")
            return ApiResponse.success(data={}, msg="MySQL备份已触发")
        else:
            logger.error(f"MySQL备份失败: {result.stderr}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"备份失败: {result.stderr}"
            )

    except subprocess.TimeoutExpired:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="备份超时"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"触发MySQL备份失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="触发备份失败"
        )


@router.post("/backup/mongodb")
async def trigger_mongodb_backup(
    admin_user: CurrentUser = Depends(require_admin)
):
    """
    触发MongoDB备份

    需要admin角色
    """
    try:
        script_path = "backend/scripts/backup_mongodb.sh"

        result = subprocess.run(
            ["bash", script_path],
            capture_output=True,
            text=True,
            timeout=300  # 5分钟超时
        )

        if result.returncode == 0:
            logger.info(f"MongoDB备份成功 (操作者: {admin_user.username})")
            return ApiResponse.success(data={}, msg="MongoDB备份已触发")
        else:
            logger.error(f"MongoDB备份失败: {result.stderr}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"备份失败: {result.stderr}"
            )

    except subprocess.TimeoutExpired:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="备份超时"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"触发MongoDB备份失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="触发备份失败"
        )


@router.get("/health")
async def get_system_health(
    admin_user: CurrentUser = Depends(require_admin)
):
    """
    获取系统健康状态

    需要admin角色
    """
    try:
        monitoring_service = get_monitoring_service()

        health = await monitoring_service.get_comprehensive_health()

        return ApiResponse.success(data=health, msg="获取成功")

    except Exception as e:
        logger.error(f"获取系统健康状态失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取系统健康状态失败"
        )


@router.get("/metrics")
async def get_performance_metrics(
    admin_user: CurrentUser = Depends(require_admin)
):
    """
    获取性能指标

    需要admin角色
    """
    try:
        monitoring_service = get_monitoring_service()

        metrics = monitoring_service.get_performance_metrics()

        return ApiResponse.success(data=metrics, msg="获取成功")

    except Exception as e:
        logger.error(f"获取性能指标失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取性能指标失败"
        )
