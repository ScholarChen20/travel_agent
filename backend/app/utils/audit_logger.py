"""
AOP风格的日志记录装饰器

使用方式:
    @log_action(action="用户登录", resource="auth")
    async def login(request, ...):
        ...
"""

import functools
import inspect
from typing import Callable, Optional, Any
from datetime import datetime
from loguru import logger

from ..database.mysql import get_mysql_db
from ..database.models import AuditLog
from starlette.requests import Request
from starlette.responses import Response


def get_client_ip(request: Request) -> str:
    """获取客户端IP地址"""
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip
    return request.client.host if request.client else "unknown"


def extract_user_info(request: Request) -> tuple[Optional[int], Optional[str]]:
    """从请求中提取用户信息"""
    user_id = None
    username = None
    
    # 尝试从state获取用户信息（FastAPI/Starlette）
    if hasattr(request.state, "user"):
        user = request.state.user
        if user:
            user_id = getattr(user, "id", None)
            username = getattr(user, "username", None)
    
    # 尝试从依赖注入获取
    if hasattr(request, "user"):
        user = request.user
        if user and hasattr(user, "id"):
            user_id = user.id
            username = getattr(user, "username", None)
    
    return user_id, username


def log_action(
    action: str,
    resource: str,
    include_request: bool = True,
    include_response: bool = False,
    log_level: str = "INFO"
):
    """
    日志记录装饰器
    
    Args:
        action: 操作类型，如 "创建", "更新", "删除", "登录"
        resource: 资源类型，如 "用户", "帖子", "评论"
        include_request: 是否记录请求参数
        include_response: 是否记录响应数据
        log_level: 日志级别
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            request: Optional[Request] = None
            start_time = datetime.now()
            
            # 提取请求对象
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break
            if not request:
                request = kwargs.get('request')
            
            # 提取用户信息
            user_id, username = None, None
            if request:
                user_id, username = extract_user_info(request)
            
            # 记录请求参数
            request_details = {}
            if include_request and request:
                try:
                    # 提取路径参数和查询参数
                    if hasattr(request, 'path_params'):
                        request_details['path_params'] = dict(request.path_params)
                    if hasattr(request, 'query_params'):
                        request_details['query_params'] = dict(request.query_params)
                    
                    # 提取请求体（排除敏感字段）
                    if hasattr(request, 'json'):
                        try:
                            body = await request.json()
                            # 过滤敏感字段
                            sensitive_fields = {'password', 'token', 'captcha_code', 'captcha_session_id'}
                            body_copy = {k: v for k, v in body.items() if k not in sensitive_fields}
                            request_details['body'] = body_copy
                        except:
                            pass
                except Exception as e:
                    logger.warning(f"记录请求参数失败: {e}")
            
            # 构建操作描述
            action_desc = f"{action}{resource}"
            if username:
                action_desc = f"{username} {action_desc}"
            
            log_message = f"📝 {action_desc}"
            if user_id:
                log_message += f" (用户ID: {user_id})"
            
            # 记录日志
            if log_level == "INFO":
                logger.info(log_message)
            elif log_level == "WARNING":
                logger.warning(log_message)
            elif log_level == "ERROR":
                logger.error(log_message)
            
            # 执行原函数
            try:
                result = await func(*args, **kwargs)
                
                # 记录响应
                if include_response:
                    response_details = {}
                    if isinstance(result, dict):
                        # 过滤敏感响应字段
                        sensitive_fields = {'password', 'token', 'access_token', 'refresh_token'}
                        response_details = {k: v for k, v in result.items() if k not in sensitive_fields}
                    logger.info(f"响应: {response_details}")
                
                # 保存到数据库
                try:
                    await save_audit_log(
                        user_id=user_id,
                        action=action,
                        resource=resource,
                        resource_id=extract_resource_id(result),
                        details={
                            'request': request_details,
                            'response': response_details if include_response else None,
                            'status': 'success'
                        } if include_request or include_response else None,
                        request=request
                    )
                except Exception as e:
                    logger.warning(f"保存审计日志失败: {e}")
                
                return result
                
            except Exception as e:
                # 记录失败
                error_message = str(e)
                logger.error(f"❌ {action_desc}失败: {error_message}")
                
                # 保存失败日志
                try:
                    await save_audit_log(
                        user_id=user_id,
                        action=action,
                        resource=resource,
                        resource_id=None,
                        details={
                            'request': request_details,
                            'error': error_message,
                            'status': 'failed'
                        } if include_request else None,
                        request=request
                    )
                except:
                    pass
                
                raise
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            request: Optional[Request] = None
            
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break
            
            user_id, username = None, None
            if request:
                user_id, username = extract_user_info(request)
            
            action_desc = f"{action}{resource}"
            if username:
                action_desc = f"{username} {action_desc}"
            
            logger.info(f"📝 {action_desc}")
            
            try:
                result = func(*args, **kwargs)
                
                try:
                    save_audit_log_sync(
                        user_id=user_id,
                        action=action,
                        resource=resource,
                        resource_id=extract_resource_id(result),
                        request=request
                    )
                except Exception as e:
                    logger.warning(f"保存审计日志失败: {e}")
                
                return result
            except Exception as e:
                logger.error(f"❌ {action_desc}失败: {str(e)}")
                raise
        
        # 根据函数类型返回对应的包装器
        if inspect.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


def extract_resource_id(result: Any) -> Optional[str]:
    """从响应结果中提取资源ID"""
    if not result:
        return None
    
    # 如果是字典，查找常见的ID字段
    if isinstance(result, dict):
        id_fields = ['id', 'user_id', 'post_id', 'comment_id', 'session_id', 'plan_id', 'item_id']
        for field in id_fields:
            if field in result:
                return str(result[field])
    
    return None


async def save_audit_log(
    user_id: Optional[int],
    action: str,
    resource: str,
    resource_id: Optional[str] = None,
    details: Optional[dict] = None,
    request: Optional[Request] = None
):
    """异步保存审计日志到数据库"""
    try:
        db = get_mysql_db()
        
        ip_address = None
        user_agent = None
        if request:
            ip_address = get_client_ip(request)
            user_agent = request.headers.get("user-agent", "")[:500]
        
        with db.get_session() as session:
            log_entry = AuditLog(
                user_id=user_id,
                action=action,
                resource=resource,
                resource_id=resource_id,
                details=details,
                ip_address=ip_address,
                user_agent=user_agent,
                created_at=datetime.now()
            )
            session.add(log_entry)
            session.commit()
    except Exception as e:
        logger.error(f"保存审计日志失败: {e}")


def save_audit_log_sync(
    user_id: Optional[int],
    action: str,
    resource: str,
    resource_id: Optional[str] = None,
    details: Optional[dict] = None,
    request: Optional[Request] = None
):
    """同步保存审计日志到数据库"""
    try:
        db = get_mysql_db()
        
        ip_address = None
        user_agent = None
        if request:
            ip_address = get_client_ip(request)
            user_agent = request.headers.get("user-agent", "")[:500]
        
        with db.get_session() as session:
            log_entry = AuditLog(
                user_id=user_id,
                action=action,
                resource=resource,
                resource_id=resource_id,
                details=details,
                ip_address=ip_address,
                user_agent=user_agent,
                created_at=datetime.now()
            )
            session.add(log_entry)
            session.commit()
    except Exception as e:
        logger.error(f"保存审计日志失败: {e}")
