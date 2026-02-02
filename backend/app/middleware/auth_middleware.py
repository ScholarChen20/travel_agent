"""
认证中间件

功能：
1. 从请求头提取Bearer Token
2. 验证JWT Token
3. 检查Redis黑名单
4. 注入用户信息到request.state
5. 支持必需认证和可选认证两种模式
"""

from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from loguru import logger

from ..services.auth_service import get_auth_service
from ..database.redis_client import get_redis_client
from ..database.mysql import get_mysql_db
from ..database.models import User


# HTTP Bearer认证方案
security = HTTPBearer(auto_error=False)


class CurrentUser:
    """当前用户信息类"""

    def __init__(
        self,
        id: int,
        username: str,
        email: str,
        role: str,
        is_active: bool,
        device_id: str,
        avatar_url: Optional[str] = None
    ):
        self.id = id
        self.username = username
        self.email = email
        self.role = role
        self.is_active = is_active
        self.device_id = device_id
        self.avatar_url = avatar_url

    def __repr__(self):
        return f"<CurrentUser(id={self.id}, username='{self.username}', role='{self.role}')>"


async def verify_token(token: str) -> Optional[CurrentUser]:
    """
    验证Token并返回用户信息

    Args:
        token: JWT Token

    Returns:
        CurrentUser: 用户信息对象，验证失败返回None
    """
    # 1. 解码Token
    auth_service = get_auth_service()
    payload = auth_service.decode_token(token)

    if not payload:
        logger.warning("Token解码失败")
        return None

    # 2. 检查Redis黑名单
    try:
        redis_client = get_redis_client()
        jti = payload.get("jti")
        if jti:
            is_blacklisted = await redis_client.exists(f"blacklist:token:{jti}")
            if is_blacklisted:
                logger.warning(f"Token已被加入黑名单: {jti[:8]}...")
                return None
    except RuntimeError as e:
        if "Redis客户端未初始化" in str(e):
            logger.warning("Redis客户端未初始化，跳过黑名单检查")
            # Redis未初始化时跳过黑名单检查，继续处理
            pass
        else:
            logger.error(f"检查Token黑名单失败: {str(e)}")
            # 其他Redis错误不应阻止认证，继续处理
            pass
    except Exception as e:
        logger.error(f"检查Token黑名单失败: {str(e)}")
        # 其他Redis错误不应阻止认证，继续处理
        pass

    # 3. 从数据库验证用户是否存在且激活
    user_id_str = payload.get("sub")
    if not user_id_str:
        logger.warning("Token中缺少用户ID")
        return None
    
    try:
        user_id = int(user_id_str)  # 将字符串类型的user_id转换为整数
    except ValueError:
        logger.warning(f"Token中用户ID格式错误: {user_id_str}")
        return None

    try:
        mysql_db = get_mysql_db()
        with mysql_db.get_session() as session:
            user = session.query(User).filter(User.id == user_id).first()

            if not user:
                logger.warning(f"用户不存在: {user_id}")
                return None

            if not user.is_active:
                logger.warning(f"用户已被禁用: {user_id}")
                return None

            # 4. 构造CurrentUser对象
            return CurrentUser(
                id=user.id,
                username=user.username,
                email=user.email,
                role=user.role,
                is_active=user.is_active,
                device_id=payload.get("device_id", "default"),
                avatar_url=user.avatar_url
            )

    except Exception as e:
        logger.error(f"验证用户失败: {str(e)}")
        return None


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> CurrentUser:
    """
    获取当前用户（必需认证）

    依赖注入函数，用于需要认证的路由

    Args:
        credentials: HTTP Bearer凭证

    Returns:
        CurrentUser: 当前用户信息

    Raises:
        HTTPException: 401 未认证或Token无效
    """
    # 检查是否提供了Token
    if not credentials:
        logger.warning("未提供认证Token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="未提供认证凭证",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 验证Token
    token = credentials.credentials
    user = await verify_token(token)

    if not user:
        logger.warning("Token验证失败")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="认证凭证无效或已过期",
            headers={"WWW-Authenticate": "Bearer"},
        )

    logger.debug(f"用户认证成功: {user.username} (ID: {user.id})")
    return user


async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[CurrentUser]:
    """
    获取当前用户（可选认证）

    用于可选认证的路由（如：既可匿名也可登录使用）

    Args:
        credentials: HTTP Bearer凭证

    Returns:
        CurrentUser: 当前用户信息，未登录返回None
    """
    # 如果没有提供Token，返回None（匿名用户）
    if not credentials:
        logger.debug("匿名用户访问")
        return None

    # 尝试验证Token
    token = credentials.credentials
    user = await verify_token(token)

    if not user:
        logger.debug("Token验证失败，作为匿名用户处理")
        return None

    logger.debug(f"已登录用户访问: {user.username} (ID: {user.id})")
    return user


def require_role(required_role: str):
    """
    角色权限装饰器

    用于检查用户是否具有特定角色

    Args:
        required_role: 需要的角色（如 "admin"）

    Returns:
        依赖函数

    Example:
        @router.get("/admin/users", dependencies=[Depends(require_role("admin"))])
        async def list_users():
            ...
    """
    async def role_checker(current_user: CurrentUser = Depends(get_current_user)):
        if current_user.role != required_role:
            logger.warning(f"用户 {current_user.username} 尝试访问需要 {required_role} 角色的资源")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"需要 {required_role} 角色权限"
            )
        return current_user

    return role_checker


async def get_current_admin(
    current_user: CurrentUser = Depends(get_current_user)
) -> CurrentUser:
    """
    获取当前管理员用户

    便捷函数，用于需要管理员权限的路由

    Args:
        current_user: 当前用户

    Returns:
        CurrentUser: 管理员用户

    Raises:
        HTTPException: 403 权限不足
    """
    if current_user.role != "admin":
        logger.warning(f"非管理员用户 {current_user.username} 尝试访问管理员资源")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要管理员权限"
        )

    return current_user
