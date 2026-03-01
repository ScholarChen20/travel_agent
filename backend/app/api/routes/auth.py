"""
认证路由

提供以下API：
- POST /api/auth/register - 用户注册
- POST /api/auth/login - 用户登录
- POST /api/auth/logout - 用户登出
- POST /api/auth/refresh - 刷新Token
- GET /api/auth/captcha - 获取验证码
- POST /api/auth/forgot-password - 忘记密码
- POST /api/auth/reset-password - 重置密码
"""

from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, HTTPException, Request, status, Depends
from pydantic import BaseModel, EmailStr, Field
from loguru import logger

from ...services.auth_service import get_auth_service
from ...services.anti_spam_service import get_anti_spam_service
from ...database.mysql import get_mysql_db
from ...database.redis_client import get_redis_client
from ...database.models import User, UserProfile
from ...middleware.auth_middleware import get_current_user, CurrentUser
from ...config import get_settings
from ...utils.response import ApiResponse


router = APIRouter(prefix="/auth", tags=["认证"])


# ========== 请求模型 ==========

class RegisterRequest(BaseModel):
    """注册请求"""
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    email: EmailStr = Field(..., description="邮箱")
    password: str = Field(..., min_length=8, description="密码")
    captcha_code: str = Field(..., min_length=4, max_length=10, description="验证码")
    captcha_session_id: str = Field(..., description="验证码会话ID")
    device_id: str = Field(..., min_length=10, max_length=128, description="设备唯一标识")


class LoginRequest(BaseModel):
    """登录请求"""
    username: str = Field(..., description="用户名或邮箱")
    password: str = Field(..., description="密码")
    captcha_code: str = Field(..., description="验证码")
    captcha_session_id: str = Field(..., description="验证码会话ID")
    device_id: str = Field(default="default", description="设备ID")


class ForgotPasswordRequest(BaseModel):
    """忘记密码请求"""
    email: EmailStr = Field(..., description="注册邮箱")


class ResetPasswordRequest(BaseModel):
    """重置密码请求"""
    token: str = Field(..., description="重置Token")
    new_password: str = Field(..., min_length=8, description="新密码")


# ========== 辅助函数 ==========

def _get_client_ip(request: Request) -> str:
    """
    从请求中提取客户端真实IP。

    优先级：X-Real-IP → X-Forwarded-For（首个IP）→ request.client.host
    """
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip.strip()

    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()

    if request.client:
        return request.client.host

    return "127.0.0.1"


async def verify_captcha(session_id: str, code: str) -> bool:
    """
    验证验证码

    Args:
        session_id: 会话ID
        code: 用户输入的验证码

    Returns:
        bool: 验证是否通过
    """
    redis_client = get_redis_client()

    # 从Redis获取验证码
    stored_code = await redis_client.get(f"captcha:{session_id}")

    if not stored_code:
        logger.warning(f"验证码不存在或已过期: {session_id}")
        return False

    # 验证码不区分大小写（转换为字符串后比较）
    if str(stored_code).lower() != str(code).lower():
        logger.warning(f"验证码错误: {session_id}")
        return False

    # 验证成功后删除验证码（一次性使用）
    await redis_client.delete(f"captcha:{session_id}")

    return True


def serialize_user(user: User) -> dict:
    """
    序列化用户对象

    Args:
        user: User对象

    Returns:
        dict: 用户信息字典
    """
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "role": user.role,
        "avatar_url": user.avatar_url,
        "is_verified": user.is_verified,
        "created_at": user.created_at.isoformat() if user.created_at else None
    }


# ========== API端点 ==========

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(request: RegisterRequest, http_request: Request):
    """
    用户注册

    流程：
    0. 防刷检查（IP国家/IP频率/设备冷却）
    1. 验证验证码
    2. 检查用户名和邮箱是否已存在
    3. 验证密码强度
    4. 创建用户和用户档案
    5. 生成JWT Token
    6. 存储Token到Redis
    7. 记录设备和IP注册信息
    """
    print(f"========== 注册接口被调用 ==========")
    print(f"用户名: {request.username}")
    print(f"邮箱: {request.email}")
    print(f"密码长度: {len(request.password)} 字符")
    print(f"密码字节数: {len(request.password.encode('utf-8'))} 字节")
    print(f"=====================================")

    logger.info(f"收到注册请求: {request.username}, {request.email}")
    auth_service = get_auth_service()
    settings = get_settings()
    mysql_db = get_mysql_db()
    redis_client = get_redis_client()
    logger.debug(f"注册请求参数: {request.json()}")

    try:
        # 0. 防刷检查（在验证码验证之前，避免消耗验证码）
        if settings.anti_spam_enabled:
            ip = _get_client_ip(http_request)
            anti_spam = get_anti_spam_service()
            allowed, error_code, retry_after = await anti_spam.check_register_allowed(
                request.device_id, ip
            )
            if not allowed:
                headers = {"Retry-After": str(retry_after)} if retry_after else {}
                error_messages = {
                    "SPAM_IP_COUNTRY": (403, "当前地区暂不支持注册"),
                    "SPAM_IP_RATE_LIMIT": (429, "注册过于频繁，请稍后再试"),
                    "SPAM_DEVICE_REGISTERED": (429, "该设备注册过于频繁，请5分钟后再试"),
                }
                http_status, detail = error_messages.get(error_code, (429, "请求过于频繁"))
                raise HTTPException(
                    status_code=http_status, detail=detail, headers=headers
                )

        # 1. 验证验证码
        logger.info(f"验证验证码: {request.captcha_session_id}, {request.captcha_code}")
        if not await verify_captcha(request.captcha_session_id, request.captcha_code):
            logger.warning(f"验证码验证失败: {request.captcha_session_id}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="验证码错误或已过期"
            )
        logger.info(f"验证码验证成功: {request.captcha_session_id}")

        # 2. 验证密码强度
        logger.info(f"验证密码强度: {request.username}")
        is_valid, error_msg = auth_service.validate_password_strength(request.password)
        if not is_valid:
            logger.warning(f"密码强度验证失败: {request.username}, error: {error_msg}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_msg
            )
        logger.info(f"密码强度验证成功: {request.username}")

        # 3. 检查用户名和邮箱是否已存在
        logger.info(f"检查用户名和邮箱是否已存在: {request.username}, {request.email}")
        with mysql_db.get_session() as session:
            existing_user = session.query(User).filter(
                (User.username == request.username) | (User.email == request.email)
            ).first()

            if existing_user:
                if existing_user.username == request.username:
                    logger.warning(f"用户名已被使用: {request.username}")
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="用户名已被使用"
                    )
                else:
                    logger.warning(f"邮箱已被注册: {request.email}")
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="邮箱已被注册"
                    )
            logger.info(f"用户名和邮箱可用: {request.username}, {request.email}")

            # 4. 创建用户
            logger.info(f"创建用户: {request.username}")
            password_hash = auth_service.hash_password(request.password)

            new_user = User(
                username=request.username,
                email=request.email,
                password_hash=password_hash,
                role="user",
                is_active=True,
                is_verified=False
            )

            session.add(new_user)
            session.flush()  # 获取用户ID
            logger.info(f"用户创建成功，ID: {new_user.id}")

            # 5. 创建用户档案
            logger.info(f"创建用户档案: {new_user.id}")
            user_profile = UserProfile(
                user_id=new_user.id,
                travel_preferences=[],
                visited_cities=[],
                travel_stats={"total_trips": 0, "total_cities": 0}
            )
            session.add(user_profile)
            logger.info(f"用户档案创建成功: {new_user.id}")

            # 保存用户信息用于后续操作
            user_id = new_user.id
            username = new_user.username
            role = new_user.role
            user_data = serialize_user(new_user)
            logger.info(f"用户信息保存成功: {username}, {user_id}")

        # 6. 生成JWT Token（数据库事务已提交）
        logger.info(f"生成JWT Token: {user_id}")
        token_data = auth_service.create_access_token(
            user_id=user_id,
            username=username,
            role=role,
            device_id="default"
        )
        logger.info(f"JWT Token生成成功: {user_id}")

        # 7. 存储Token到Redis
        logger.info(f"存储JWT Token到Redis: {user_id}")
        await redis_client.hset(
            f"jwt:user:{user_id}",
            "default",
            token_data["access_token"]
        )
        logger.info(f"JWT Token存储成功: {user_id}")

        await redis_client.expire(
            f"jwt:user:{user_id}",
            settings.jwt_access_token_expire_days * 86400
        )
        logger.info(f"JWT Token过期时间设置成功: {user_id}")

        logger.info(f"新用户注册成功: {username} (ID: {user_id})")

        # 8. 记录设备和IP（注册成功后）
        if settings.anti_spam_enabled:
            _ip = _get_client_ip(http_request)
            _anti_spam = get_anti_spam_service()
            await _anti_spam.mark_device_registered(request.device_id)
            await _anti_spam.increment_ip_counter(_ip)

        return ApiResponse.created(
            data={
                "access_token": token_data["access_token"],
                "token_type": token_data["token_type"],
                "expires_in": token_data["expires_in"],
                "expires_at": token_data["expires_at"],
                "user": user_data
            },
            msg="注册成功"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"注册失败: {request.username}, error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"注册失败: {str(e)}"
        ) from e


@router.post("/login")
async def login(request: LoginRequest):
    """
    用户登录

    流程：
    1. 验证验证码
    2. 检查限流（防止暴力破解）
    3. 验证用户凭证
    4. 生成JWT Token
    5. 存储Token到Redis
    6. 更新最后登录时间
    """
    auth_service = get_auth_service()
    settings = get_settings()
    mysql_db = get_mysql_db()
    redis_client = get_redis_client()

    # 1. 验证验证码
    if not await verify_captcha(request.captcha_session_id, request.captcha_code):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="验证码错误或已过期"
        )

    # 2. 检查限流
    rate_limit_key = f"rate_limit:login:{request.username}"
    attempts = await redis_client.get(rate_limit_key)

    if attempts and int(attempts) >= settings.max_login_attempts:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"登录尝试次数过多，请{settings.max_login_attempts}分钟后再试"
        )

    # 3. 查询用户
    with mysql_db.get_session() as session:
        user = session.query(User).filter(
            (User.username == request.username) | (User.email == request.username)
        ).first()

        if not user:
            # 增加失败计数
            await redis_client.incr(rate_limit_key)
            await redis_client.expire(rate_limit_key, 300)  # 5分钟

            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户名错误"
            )

        # 4. 验证密码
        if not auth_service.verify_password(request.password, user.password_hash):
            # 增加失败计数
            await redis_client.incr(rate_limit_key)
            await redis_client.expire(rate_limit_key, 300)

            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="密码错误"
            )

        # 5. 检查用户状态
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="账户已被禁用，请联系管理员"
            )

        # 6. 生成JWT Token
        token_data = auth_service.create_access_token(
            user_id=user.id,
            username=user.username,
            role=user.role,
            device_id=request.device_id
        )

        # 7. 存储Token到Redis（支持多设备）
        await redis_client.hset(
            f"jwt:user:{user.id}",
            request.device_id,
            token_data["access_token"]
        )
        await redis_client.expire(
            f"jwt:user:{user.id}",
            settings.jwt_access_token_expire_days * 86400
        )

        # 8. 更新最后登录时间
        user.last_login_at = datetime.utcnow()

        # 9. 清除限流计数
        await redis_client.delete(rate_limit_key)

        logger.info(f"用户登录成功: {user.username} (ID: {user.id}, 设备: {request.device_id})")

        return ApiResponse.success(
            data={
                "access_token": token_data["access_token"],
                "token_type": token_data["token_type"],
                "expires_in": token_data["expires_in"],
                "expires_at": token_data["expires_at"],
                "user": serialize_user(user)
            },
            msg="登录成功"
        )


@router.post("/logout")
async def logout(current_user: CurrentUser = Depends(get_current_user)):
    """
    用户登出

    将当前Token加入黑名单
    """
    redis_client = get_redis_client()

    # 删除Redis中的Token
    await redis_client.hdel(
        f"jwt:user:{current_user.id}",
        current_user.device_id
    )

    logger.info(f"用户登出成功: {current_user.username} (ID: {current_user.id})")

    return ApiResponse.success(data={}, msg="登出成功")


@router.post("/refresh")
async def refresh_token(current_user: CurrentUser = Depends(get_current_user)):
    """
    刷新Token

    生成新的Token并返回
    """
    auth_service = get_auth_service()
    redis_client = get_redis_client()
    settings = get_settings()

    # 生成新Token
    token_data = auth_service.create_access_token(
        user_id=current_user.id,
        username=current_user.username,
        role=current_user.role,
        device_id=current_user.device_id
    )

    # 更新Redis
    await redis_client.hset(
        f"jwt:user:{current_user.id}",
        current_user.device_id,
        token_data["access_token"]
    )
    await redis_client.expire(
        f"jwt:user:{current_user.id}",
        settings.jwt_access_token_expire_days * 86400
    )

    logger.info(f"Token刷新成功: {current_user.username} (ID: {current_user.id})")

    # 获取用户完整信息
    mysql_db = get_mysql_db()
    with mysql_db.get_session() as session:
        user = session.query(User).filter(User.id == current_user.id).first()

        return ApiResponse.success(
            data={
                "access_token": token_data["access_token"],
                "token_type": token_data["token_type"],
                "expires_in": token_data["expires_in"],
                "expires_at": token_data["expires_at"],
                "user": serialize_user(user)
            },
            msg="Token刷新成功"
        )


@router.get("/captcha")
async def get_captcha():
    """
    获取验证码

    返回验证码图片和会话ID
    """
    auth_service = get_auth_service()
    redis_client = get_redis_client()
    settings = get_settings()

    # 生成验证码
    code, image_base64 = auth_service.generate_captcha()
    session_id = auth_service.generate_session_id()

    # 存储到Redis
    await redis_client.set(
        f"captcha:{session_id}",
        code,
        ex=settings.captcha_expiry_seconds
    )

    logger.debug(f"生成验证码: {session_id} -> {code}")

    return ApiResponse.success(
        data={
            "session_id": session_id,
            "image_base64": image_base64,
            "expires_in": settings.captcha_expiry_seconds
        },
        msg="获取验证码成功"
    )


@router.post("/forgot-password")
async def forgot_password(request: ForgotPasswordRequest):
    """
    忘记密码

    发送重置密码链接到邮箱（当前仅返回Token，实际应发送邮件）
    """
    auth_service = get_auth_service()
    mysql_db = get_mysql_db()

    # 查询用户
    with mysql_db.get_session() as session:
        user = session.query(User).filter(User.email == request.email).first()

        if not user:
            # 为了安全，不透露用户是否存在
            return ApiResponse.success(data={}, msg="如果该邮箱已注册，您将收到重置密码的邮件")

        # 生成重置Token
        reset_token = auth_service.create_reset_token(user.id, user.email)

        # TODO: 发送邮件
        logger.info(f"生成密码重置Token: {user.email}")
        logger.debug(f"重置Token: {reset_token}")  # 仅用于开发调试

        return ApiResponse.success(data={}, msg="如果该邮箱已注册，您将收到重置密码的邮件")


@router.post("/reset-password")
async def reset_password(request: ResetPasswordRequest):
    """
    重置密码

    使用重置Token设置新密码
    """
    auth_service = get_auth_service()
    mysql_db = get_mysql_db()

    # 验证重置Token
    payload = auth_service.verify_reset_token(request.token)

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="重置Token无效或已过期"
        )

    user_id = payload.get("sub")
    email = payload.get("email")

    # 验证新密码强度
    is_valid, error_msg = auth_service.validate_password_strength(request.new_password)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg
        )

    # 更新密码
    with mysql_db.get_session() as session:
        user = session.query(User).filter(
            User.id == user_id,
            User.email == email
        ).first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="用户不存在"
            )

        # 哈希新密码
        user.password_hash = auth_service.hash_password(request.new_password)

        logger.info(f"密码重置成功: {user.email}")

        return ApiResponse.success(data={}, msg="密码重置成功，请使用新密码登录")


@router.get("/me")
async def get_current_user_info(
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    获取当前登录用户信息

    Returns:
        dict: 当前登录用户的详细信息
    """
    mysql_db = get_mysql_db()

    with mysql_db.get_session() as session:
        user = session.query(User).filter(User.id == current_user.id).first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )

        logger.info(f"获取用户信息: {user.username} (ID: {user.id})")

        return ApiResponse.success(data=serialize_user(user), msg="获取成功")
