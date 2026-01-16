"""
审计日志装饰器

功能：
1. 记录所有写操作（POST, PUT, DELETE）
2. 记录用户ID、操作、资源、IP地址、User-Agent
3. 存储到MongoDB（简化版，实际应该存储到MySQL）
"""

import functools
from datetime import datetime
from typing import Callable
from fastapi import Request
from loguru import logger

from ..database.mongodb import get_mongodb_client


async def log_audit(
    user_id: int,
    action: str,
    resource: str,
    resource_id: str = None,
    ip_address: str = None,
    user_agent: str = None,
    details: dict = None
):
    """
    记录审计日志

    Args:
        user_id: 用户ID
        action: 操作类型（create/update/delete）
        resource: 资源类型（user/post/plan等）
        resource_id: 资源ID
        ip_address: IP地址
        user_agent: User-Agent
        details: 详细信息
    """
    try:
        mongodb = get_mongodb_client()
        collection = mongodb.get_collection("audit_logs")

        log_doc = {
            "user_id": user_id,
            "action": action,
            "resource": resource,
            "resource_id": resource_id,
            "ip_address": ip_address,
            "user_agent": user_agent,
            "details": details or {},
            "created_at": datetime.utcnow()
        }

        await collection.insert_one(log_doc)

        logger.debug(f"审计日志已记录: {action} {resource} by user {user_id}")

    except Exception as e:
        logger.error(f"记录审计日志失败: {str(e)}")
        # 不抛出异常，避免影响主流程


def audit_log(resource: str, action: str = None):
    """
    审计日志装饰器

    Args:
        resource: 资源类型
        action: 操作类型（可选，默认从HTTP方法推断）

    Usage:
        @audit_log(resource="post", action="create")
        async def create_post(...):
            ...
    """
    def decorator(func: Callable):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # 获取request和current_user
            request: Request = None
            current_user = None

            for arg in args:
                if isinstance(arg, Request):
                    request = arg

            for key, value in kwargs.items():
                if key == "request" and isinstance(value, Request):
                    request = value
                elif key == "current_user" or key == "admin_user":
                    current_user = value

            # 执行原函数
            result = await func(*args, **kwargs)

            # 记录审计日志
            if current_user and request:
                # 推断操作类型
                inferred_action = action
                if not inferred_action:
                    method = request.method
                    if method == "POST":
                        inferred_action = "create"
                    elif method == "PUT" or method == "PATCH":
                        inferred_action = "update"
                    elif method == "DELETE":
                        inferred_action = "delete"
                    else:
                        inferred_action = "read"

                # 获取IP和User-Agent
                ip_address = request.client.host if request.client else None
                user_agent = request.headers.get("user-agent")

                # 异步记录日志
                await log_audit(
                    user_id=current_user.id,
                    action=inferred_action,
                    resource=resource,
                    ip_address=ip_address,
                    user_agent=user_agent
                )

            return result

        return wrapper
    return decorator
