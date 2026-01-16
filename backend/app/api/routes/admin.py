"""
管理后台路由

提供以下API（需要admin角色）：
- GET /api/admin/users - 用户列表
- PUT /api/admin/users/{user_id}/status - 激活/禁用用户
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
from datetime import datetime
from fastapi import APIRouter, HTTPException, status, Depends, Query
from pydantic import BaseModel, Field
from loguru import logger
import subprocess

from ...services.admin_service import get_admin_service
from ...services.monitoring_service import get_monitoring_service
from ...middleware.auth_middleware import get_current_user, CurrentUser


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


# ========== 请求/响应模型 ==========

class UpdateUserStatusRequest(BaseModel):
    """更新用户状态请求"""
    is_active: bool = Field(..., description="激活状态")


class ModeratePostRequest(BaseModel):
    """审核帖子请求"""
    status: str = Field(..., description="审核状态（approved/rejected）")
    reason: Optional[str] = Field(None, description="审核原因")


class MessageResponse(BaseModel):
    """通用消息响应"""
    message: str = Field(..., description="消息内容")


# ========== API端点 ==========

@router.get("/users")
async def list_users(
    role: Optional[str] = Query(None, description="角色筛选"),
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
            role=role,
            is_active=is_active,
            is_verified=is_verified,
            limit=limit,
            offset=offset
        )

        return result

    except Exception as e:
        logger.error(f"获取用户列表失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取用户列表失败"
        )


@router.put("/users/{user_id}/status", response_model=MessageResponse)
async def update_user_status(
    user_id: int,
    request: UpdateUserStatusRequest,
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

        return MessageResponse(message=f"用户已{action}")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新用户状态失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="更新用户状态失败"
        )


@router.get("/posts/moderation")
async def get_posts_for_moderation(
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
            status=status,
            limit=limit,
            offset=offset
        )

        return result

    except Exception as e:
        logger.error(f"获取待审核内容失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取待审核内容失败"
        )


@router.put("/posts/{post_id}/moderate", response_model=MessageResponse)
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

        return MessageResponse(message=f"帖子已{request.status}")

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

        return stats

    except Exception as e:
        logger.error(f"获取系统统计失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取系统统计失败"
        )


@router.get("/logs/audit")
async def get_audit_logs(
    user_id: Optional[int] = Query(None, description="用户ID筛选"),
    action: Optional[str] = Query(None, description="操作类型筛选"),
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
            user_id=user_id,
            action=action,
            limit=limit,
            offset=offset
        )

        return result

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

        return stats

    except Exception as e:
        logger.error(f"获取工具调用统计失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取工具调用统计失败"
        )


@router.post("/backup/mysql", response_model=MessageResponse)
async def trigger_mysql_backup(
    admin_user: CurrentUser = Depends(require_admin)
):
    """
    触发MySQL备份

    需要admin角色
    """
    try:
        # 执行备份脚本
        script_path = "backend/scripts/backup_mysql.sh"

        result = subprocess.run(
            ["bash", script_path],
            capture_output=True,
            text=True,
            timeout=300  # 5分钟超时
        )

        if result.returncode == 0:
            logger.info(f"MySQL备份成功 (操作者: {admin_user.username})")
            return MessageResponse(message="MySQL备份已触发")
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
    except Exception as e:
        logger.error(f"触发MySQL备份失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="触发备份失败"
        )


@router.post("/backup/mongodb", response_model=MessageResponse)
async def trigger_mongodb_backup(
    admin_user: CurrentUser = Depends(require_admin)
):
    """
    触发MongoDB备份

    需要admin角色
    """
    try:
        # 执行备份脚本
        script_path = "backend/scripts/backup_mongodb.sh"

        result = subprocess.run(
            ["bash", script_path],
            capture_output=True,
            text=True,
            timeout=300  # 5分钟超时
        )

        if result.returncode == 0:
            logger.info(f"MongoDB备份成功 (操作者: {admin_user.username})")
            return MessageResponse(message="MongoDB备份已触发")
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
    except Exception as e:
        logger.error(f"触发MongoDB备份失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="触发���份失败"
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

        return health

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

        return metrics

    except Exception as e:
        logger.error(f"获取性能指标失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取性能指标失败"
        )
