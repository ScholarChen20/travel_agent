"""
认证服务模块

提供：
1. 密码哈希和验证
2. JWT Token生成和验证
3. 验证码生成
4. Token黑名单管理
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import secrets
import jwt
from captcha.image import ImageCaptcha
import bcrypt
import io
import base64
from loguru import logger

from ..config import get_settings


class AuthService:
    """认证服务类"""

    def __init__(self):
        """初始化认证服务"""
        self.settings = get_settings()

        # 验证码生成器
        self.captcha_generator = ImageCaptcha(
            width=160,
            height=60,
            fonts=None,  # 使用默认字体
            font_sizes=(42, 50, 56)
        )

        logger.info("认证服务已初始化")

    # ========== 密码管理 ==========

    def hash_password(self, password: str) -> str:
        """
        哈希密码

        Args:
            password: 明文密码

        Returns:
            str: 哈希后的密码
        """
        # bcrypt限制密码长度为72字节，需要手动截断（按字节计算）
        password_bytes = password.encode('utf-8')[:72]
        
        # 调试日志
        logger.debug(f"原始密码长度: {len(password)} 字符, {len(password.encode('utf-8'))} 字节")
        logger.debug(f"截断后密码长度: {len(password_bytes)} 字节")
        
        # 使用bcrypt库进行哈希
        salt = bcrypt.gensalt(rounds=12)
        hashed_bytes = bcrypt.hashpw(password_bytes, salt)
        return hashed_bytes.decode('utf-8')

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        验证密码

        Args:
            plain_password: 明文密码
            hashed_password: 哈希密码

        Returns:
            bool: 密码是否匹配
        """
        try:
            # 同样需要按字节截断，保持与hash_password一致
            password_bytes = plain_password.encode('utf-8')[:72]
            hashed_bytes = hashed_password.encode('utf-8')
            return bcrypt.checkpw(password_bytes, hashed_bytes)
        except Exception as e:
            logger.error(f"密码验证失败: {str(e)}")
            return False

    def validate_password_strength(self, password: str) -> tuple[bool, Optional[str]]:
        """
        验证密码强度

        规则：
        - 长度至少8个字符
        - 包含大小写字母、数字和特殊字符中的至少3种

        Args:
            password: 密码

        Returns:
            tuple: (是否有效, 错误信息)
        """
        if len(password) < self.settings.password_min_length:
            return False, f"密码长度至少{self.settings.password_min_length}个字符"

        # 检查字符类型
        has_lower = any(c.islower() for c in password)
        has_upper = any(c.isupper() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?/" for c in password)

        char_types = sum([has_lower, has_upper, has_digit, has_special])

        if char_types < 3:
            return False, "密码必须包含大小写字母、数字和特殊字符中的至少3种"

        return True, None

    # ========== JWT Token管理 ==========

    def create_access_token(
        self,
        user_id: int,
        username: str,
        role: str,
        device_id: str = "default",
        expires_delta: Optional[timedelta] = None
    ) -> Dict[str, Any]:
        """
        创建JWT访问Token

        Args:
            user_id: 用户ID
            username: 用户名
            role: 用户角色
            device_id: 设备ID（用于多设备登录）
            expires_delta: 过期时间增量

        Returns:
            dict: {
                "access_token": str,
                "token_type": "bearer",
                "expires_in": int (秒),
                "expires_at": str (ISO格式)
            }
        """
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(days=self.settings.jwt_access_token_expire_days)

        # 生成唯一的JWT ID（用于黑名单）
        jti = secrets.token_urlsafe(32)

        # Token负载
        payload = {
            "sub": user_id,  # Subject: 用户ID
            "username": username,
            "role": role,
            "device_id": device_id,
            "jti": jti,  # JWT ID
            "exp": expire,  # Expiration time
            "iat": datetime.utcnow(),  # Issued at
            "nbf": datetime.utcnow()  # Not before
        }

        # 生成Token
        token = jwt.encode(
            payload,
            self.settings.jwt_secret_key,
            algorithm=self.settings.jwt_algorithm
        )

        # 计算过期时间（秒）
        expires_in = int((expire - datetime.utcnow()).total_seconds())

        return {
            "access_token": token,
            "token_type": "bearer",
            "expires_in": expires_in,
            "expires_at": expire.isoformat(),
            "jti": jti  # 返回JTI用于存储到Redis
        }

    def decode_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        解码并验证JWT Token

        Args:
            token: JWT Token字符串

        Returns:
            dict: Token负载，验证失败返回None
        """
        try:
            payload = jwt.decode(
                token,
                self.settings.jwt_secret_key,
                algorithms=[self.settings.jwt_algorithm]
            )
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("Token已过期")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Token无效: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Token解码失败: {str(e)}")
            return None

    def extract_jti_from_token(self, token: str) -> Optional[str]:
        """
        从Token中提取JTI（不验证签名）

        用于登出时快速提取JTI加入黑名单

        Args:
            token: JWT Token

        Returns:
            str: JTI，失败返回None
        """
        try:
            # 不验证签名，直接解码
            payload = jwt.decode(
                token,
                options={"verify_signature": False}
            )
            return payload.get("jti")
        except Exception as e:
            logger.error(f"提取JTI失败: {str(e)}")
            return None

    # ========== 验证码生成 ==========

    def generate_captcha(self) -> tuple[str, str]:
        """
        生成验证码

        Returns:
            tuple: (验证码文本, 验证码图片Base64编码)
        """
        # 生成4位数字验证码
        code = ''.join(secrets.choice('0123456789') for _ in range(4))

        # 生成图片
        image_bytes = io.BytesIO()
        self.captcha_generator.write(code, image_bytes)
        image_bytes.seek(0)
        
        # 转换为Base64
        image_base64 = base64.b64encode(image_bytes.getvalue()).decode('utf-8')

        return code, f"data:image/png;base64,{image_base64}"

    def generate_session_id(self) -> str:
        """
        生成验证码会话ID

        Returns:
            str: 32位随机字符串
        """
        return secrets.token_urlsafe(32)

    # ========== 密码重置Token ==========

    def create_reset_token(self, user_id: int, email: str) -> str:
        """
        创建密码重置Token

        Args:
            user_id: 用户ID
            email: 用户邮箱

        Returns:
            str: 重置Token（15分钟有效期）
        """
        expire = datetime.utcnow() + timedelta(minutes=15)

        payload = {
            "sub": user_id,
            "email": email,
            "type": "password_reset",
            "exp": expire,
            "iat": datetime.utcnow()
        }

        token = jwt.encode(
            payload,
            self.settings.jwt_secret_key,
            algorithm=self.settings.jwt_algorithm
        )

        return token

    def verify_reset_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        验证密码重置Token

        Args:
            token: 重置Token

        Returns:
            dict: Token负载，验证失败返回None
        """
        try:
            payload = jwt.decode(
                token,
                self.settings.jwt_secret_key,
                algorithms=[self.settings.jwt_algorithm]
            )

            # 检查Token类型
            if payload.get("type") != "password_reset":
                logger.warning("Token类型错误")
                return None

            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("重置Token已过期")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"重置Token无效: {str(e)}")
            return None

    # ========== 辅助方法 ==========

    def generate_random_password(self, length: int = 12) -> str:
        """
        生成随机密码

        Args:
            length: 密码长度（默认12）

        Returns:
            str: 随机密码
        """
        # 包含大小写字母、数字和特殊字符
        chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*"
        password = ''.join(secrets.choice(chars) for _ in range(length))
        return password


# ========== 全局实例（单例模式） ==========

_auth_service: Optional[AuthService] = None


def get_auth_service() -> AuthService:
    """
    获取全局认证服务实例（单例）

    Returns:
        AuthService: 认证服务实例
    """
    global _auth_service
    if _auth_service is None:
        _auth_service = AuthService()
    return _auth_service
