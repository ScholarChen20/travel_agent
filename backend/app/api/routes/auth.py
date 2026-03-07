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
import subprocess
from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, HTTPException, Request, status, Depends
from pydantic import BaseModel, EmailStr, Field
from loguru import logger

from ...services.auth_service import get_auth_service
from ...services.anti_spam_service import get_anti_spam_service, AntiSpamRequest
from ...services.feishu_service import get_feishu_service
from ...database.mysql import get_mysql_db
from ...database.redis_client import get_redis_client
from ...database.models import User, UserProfile
from ...middleware.auth_middleware import get_current_user, CurrentUser
from ...config import get_settings
from ...utils.response import ApiResponse
from ...utils.cache_invalidator import get_cache_invalidator


router = APIRouter(prefix="/auth", tags=["认证"])


# ========== 请求模型 ==========

class RegisterRequest(BaseModel):
    """注册请求"""
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    email: EmailStr = Field(..., description="邮箱")
    password: str = Field(..., min_length=8, description="密码")
    nickname: str = Field(..., description="昵称")
    captcha_code: str = Field(..., min_length=4, max_length=10, description="验证码")
    captcha_session_id: str = Field(..., description="验证码会话ID")


class LoginRequest(BaseModel):
    """登录请求"""
    username: str = Field(..., description="用户名或邮箱")
    password: str = Field(..., description="密码")
    captcha_code: str = Field(..., description="验证码")
    captcha_session_id: str = Field(..., description="验证码会话ID")
    # device_id: str = Field(default="default", description="设备ID")


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

def get_device_id():
    """获取设备ID"""
    try:
        command = "wmic csproduct get uuid"   # Windows 获取主板id
        # command = "sudo dmidecode -s system-uuid"   # Linux 获取主板id
        result = subprocess.check_output(command, shell=True).decode().strip()

        device_id = result.split("\n")[1].strip()
        return device_id
    except Exception as e:
        print(f"Error: {e}")
    return None

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

    # 获取客户端信息（需要在防刷检查之前获取）
    ip = _get_client_ip(http_request)
    device_id = get_device_id() or "unknown:" + request.username

    try:
        # 0. 防刷检查（在验证码验证之前，避免消耗验证码）
        if settings.anti_spam_enabled:
            anti_spam = await get_anti_spam_service()
            spam_response = await anti_spam.check_register_allowed(
                AntiSpamRequest(
                    user_name=request.username,
                    device_id=device_id,
                    ip_address=ip,
                    request_type="register"
                )
            )
            if not spam_response.allowed:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=spam_response.reason or "请求过于频繁"
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
                full_name=request.nickname,
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
            device_id=device_id
        )
        logger.info(f"JWT Token生成成功: {user_id}")

        # 7. 存储Token到Redis
        logger.info(f"存储JWT Token到Redis: {user_id}")
        await redis_client.hset(
            f"jwt:user:{user_id}",
            "account",
            token_data["access_token"]
        )
        logger.info(f"JWT Token存储成功: {user_id}")

        await redis_client.expire(
            f"jwt:user:{user_id}",
            settings.jwt_access_token_expire_days * 86400
        )
        logger.info(f"JWT Token过期时间设置成功: {user_id}")

        logger.info(f"新用户注册成功: {username} (ID: {user_id})")

        # 注册成功后失效管理后台统计缓存
        cache_invalidator = get_cache_invalidator()
        await cache_invalidator.invalidate_admin_all_stats()

        # 8. 将设备ID添加到临时黑名单（防止短时间内重复注册）
        if settings.anti_spam_enabled:
            anti_spam = await get_anti_spam_service()
            await anti_spam.add_device_to_temp_blacklist(device_id)
            # 清除注册失败计数
            await anti_spam.clear_register_failure(device_id, ip)
            logger.info(f"设备ID {device_id} 已添加到临时黑名单，并清除失败计数")

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
    except HTTPException as e:
        # 记录注册失败
        if settings.anti_spam_enabled:
            try:
                anti_spam = await get_anti_spam_service()
                await anti_spam.record_register_failure(device_id, ip, f"HTTP {e.status_code}: {e.detail}")
            except Exception as record_error:
                logger.error(f"记录注册失败时发生异常: {str(record_error)}")
        raise
    except Exception as e:
        logger.error(f"注册失败: {request.username}, error: {str(e)}", exc_info=True)
        # 记录注册失败
        if settings.anti_spam_enabled:
            try:
                anti_spam = await get_anti_spam_service()
                await anti_spam.record_register_failure(device_id, ip, f"系统错误: {str(e)}")
            except Exception as record_error:
                logger.error(f"记录注册失败时发生异常: {str(record_error)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"注册失败: {str(e)}"
        ) from e


@router.post("/login")
async def login(request: LoginRequest, http_request: Request):
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

    # 获取客户端信息
    ip = _get_client_ip(http_request)
    device_id = get_device_id() or "unknown:" + request.username

    try:
        # 0. 校验设备id是否在黑名单中
        if settings.anti_spam_enabled:
            _anti_spam = await get_anti_spam_service()
            response = await _anti_spam.check_login_allowed(device_id)
            if not response.allowed:
                raise HTTPException(
                    status_code=429,
                    detail=response.reason or "设备ID在黑名单中"
                )


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
                device_id=device_id
            )

            # 7. 存储Token到Redis（支持多设备）
            await redis_client.hset(
                f"jwt:user:{user.id}",
                device_id,
                token_data["access_token"]
            )
            await redis_client.expire(
                f"jwt:user:{user.id}",
                settings.jwt_access_token_expire_days * 86400
            )

            # 8. 更新最后登录时间
            user.last_login_at = datetime.now()

            # 9. 清除限流计数
            await redis_client.delete(rate_limit_key)

            # 10. 清除登录失败计数
            if settings.anti_spam_enabled:
                _anti_spam = await get_anti_spam_service()
                await _anti_spam.clear_login_failure(device_id, ip)

            logger.info(f"用户登录成功: {user.username} (ID: {user.id}, 设备id: {device_id})")

            return ApiResponse.success(
                data={
                    "access_token": token_data["access_token"],
                    "token_type": token_data["token_type"],
                    "expires_in": token_data["expires_in"],
                    "expires_at": token_data["expires_at"],
                    "user": serialize_user(user),
                    "role": user.role
                },
                msg="登录成功"
            )

    except HTTPException as e:
        # 记录登录失败
        if settings.anti_spam_enabled:
            try:
                _anti_spam = await get_anti_spam_service()
                await _anti_spam.record_login_failure(device_id, ip, f"HTTP {e.status_code}: {e.detail}")
            except Exception as record_error:
                logger.error(f"记录登录失败时发生异常: {str(record_error)}")
        raise
    except Exception as e:
        logger.error(f"登录失败: {request.username}, error: {str(e)}", exc_info=True)
        # 记录登录失败
        if settings.anti_spam_enabled:
            try:
                _anti_spam = await get_anti_spam_service()
                await _anti_spam.record_login_failure(device_id, ip, f"系统错误: {str(e)}")
            except Exception as record_error:
                logger.error(f"记录登录失败时发生异常: {str(record_error)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"登录失败: {str(e)}"
        ) from e


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


# ========== 飞书 OAuth2 登录 ==========

class FeishuCallbackRequest(BaseModel):
    """飞书回调请求"""
    code: str = Field(..., description="飞书授权码")
    state: str = Field(..., description="CSRF 防护随机串")


@router.get("/feishu/authorize")
async def feishu_authorize():
    """
    获取飞书授权跳转 URL

    生成 state 存入 Redis（TTL 10 分钟）防 CSRF，
    返回完整的飞书授权页地址供前端跳转。
    """
    settings = get_settings()

    if not settings.feishu_enabled:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="飞书登录功能未启用"
        )

    import secrets as _secrets
    from urllib.parse import urlencode

    redis_client = get_redis_client()
    state = _secrets.token_urlsafe(32)

    # state 存 Redis，10 分钟有效，防 CSRF / 重放
    await redis_client.set(f"feishu:oauth_state:{state}", "1", ex=600)

    params = urlencode({
        "client_id": settings.feishu_app_id,   # 新版 OIDC 端点用 client_id
        "redirect_uri": settings.feishu_redirect_uri,
        "response_type": "code",                # 新版端点必填
        "state": state,
    })
    authorize_url = f"https://accounts.feishu.cn/open-apis/authen/v1/authorize?{params}"

    logger.info(f"生成飞书授权 URL, state={state[:8]}..., redirect_uri={settings.feishu_redirect_uri}")
    logger.debug(f"完整授权 URL: {authorize_url}")
    return ApiResponse.success(
        data={"authorize_url": authorize_url},
        msg="获取授权地址成功"
    )


@router.post("/feishu/callback")
async def feishu_callback(request: FeishuCallbackRequest):
    """
    飞书授权回调处理

    流程：
    1. 校验 state（防 CSRF）
    2. 用 code 换取飞书 user_access_token
    3. 获取飞书用户信息
    4. 查找已绑定用户 或 自动注册新用户
    5. 签发系统 JWT Token
    """
    settings = get_settings()
    redis_client = get_redis_client()
    mysql_db = get_mysql_db()
    auth_service = get_auth_service()
    feishu_service = get_feishu_service()

    if not settings.feishu_enabled:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="飞书登录功能未启用"
        )

    # 1. 校验 state
    state_key = f"feishu:oauth_state:{request.state}"
    if not await redis_client.exists(state_key):
        logger.warning(f"飞书回调 state 无效或已过期: {request.state[:8]}...")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="授权状态无效或已过期，请重新登录"
        )
    await redis_client.delete(state_key)  # 一次性使用，防重放

    # 2. code 换 user_access_token（同时含用户基础信息）
    token_data = await feishu_service.exchange_code_for_token(request.code)
    user_access_token = token_data.get("access_token")

    # 3. 获取飞书用户详细信息（二次确认身份）
    feishu_user = await feishu_service.get_feishu_user_info(user_access_token)

    open_id = feishu_user.get("open_id") or token_data.get("open_id")
    union_id = feishu_user.get("union_id") or token_data.get("union_id")
    feishu_name = feishu_user.get("name") or feishu_user.get("en_name") or "飞书用户"
    feishu_email = feishu_user.get("email") or feishu_user.get("enterprise_email") or ""
    feishu_avatar = feishu_user.get("avatar_url") or feishu_user.get("avatar_big") or ""
    phone= feishu_user.get("mobile").split("+86")[1] or ""


    if not open_id:
        logger.error("飞书用户信息缺少 open_id")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="飞书服务暂时不可用，请稍后重试"
        )

    # 4. 查找用户 或 自动注册
    import secrets as _secrets
    is_new_user = False

    with mysql_db.get_session() as session:
        user = session.query(User).filter(
            User.feishu_open_id == open_id
        ).first()

        if user:
            # 已绑定用户：同步飞书最新头像
            if feishu_avatar and user.avatar_url != feishu_avatar:
                user.avatar_url = feishu_avatar
            logger.info(f"飞书用户已存在: {user.username} (ID: {user.id})")
        else:
            # 首次飞书登录：自动注册
            is_new_user = True

            # 生成唯一 username
            base_name = feishu_name[:40]
            username = base_name
            if session.query(User).filter(User.username == username).first():
                username = f"{base_name}_{_secrets.token_hex(2)}"

            # 生成唯一 email
            if feishu_email:
                email = feishu_email
                if session.query(User).filter(User.email == email).first():
                    email = f"{open_id}@feishu.local"
            else:
                email = f"{open_id}@feishu.local"

            user = User(
                username=username,
                email=email,
                password_hash=None,       # 飞书用户无密码
                avatar_url=feishu_avatar,
                phone=phone,
                role="user",
                is_active=True,
                is_verified=True,         # 飞书已做身份验证
                feishu_open_id=open_id,
                feishu_union_id=union_id,
            )
            session.add(user)
            session.flush()  # 获取自增 ID

            profile = UserProfile(
                user_id=user.id,
                travel_preferences=[],
                visited_cities=[],
                travel_stats={"total_trips": 0, "total_cities": 0}
            )
            session.add(profile)
            logger.info(f"飞书新用户自动注册: {username} (ID: {user.id})")

        # 检查账号状态
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="账户已被禁用，请联系管理员"
            )

        user.last_login_at = datetime.now()

        user_id = user.id
        username = user.username
        role = user.role
        user_data = serialize_user(user)

    # 5. 签发系统 JWT Token
    token_result = auth_service.create_access_token(
        user_id=user_id,
        username=username,
        role=role,
        device_id="feishu"
    )

    # 6. Token 写入 Redis
    await redis_client.hset(
        f"jwt:user:{user_id}", "feishu", token_result["access_token"]
    )
    await redis_client.expire(
        f"jwt:user:{user_id}",
        settings.jwt_access_token_expire_days * 86400
    )

    logger.info(
        f"飞书登录成功: {username} (ID: {user_id}, 新用户={is_new_user})"
    )

    return ApiResponse.success(
        data={
            "access_token": token_result["access_token"],
            "token_type": token_result["token_type"],
            "expires_in": token_result["expires_in"],
            "expires_at": token_result["expires_at"],
            "user": user_data,
            "is_new_user": is_new_user,
        },
        msg="登录成功"
    )
