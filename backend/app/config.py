"""配置管理模块"""

import os
from pathlib import Path
from typing import List
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# 加载环境变量
# 首先尝试加载当前目录的.env
load_dotenv()

# 然后尝试加载HelloAgents的.env(如果存在)
helloagents_env = Path(__file__).parent.parent.parent.parent / "HelloAgents" / ".env"
if helloagents_env.exists():
    load_dotenv(helloagents_env, override=False)  # 不覆盖已有的环境变量


class Settings(BaseSettings):
    """应用配置"""

    # 应用基本配置
    app_name: str = "HelloAgents智能旅行助手"
    app_version: str = "1.0.0"
    debug: bool = False

    # 服务器配置
    host: str = "0.0.0.0"
    port: int = 8000

    # CORS配置 - 使用字符串,在代码中分割
    cors_origins: str = "http://localhost:5173,http://localhost:5174,http://localhost:3000,http://127.0.0.1:5173,http://127.0.0.1:5174,http://127.0.0.1:3000"

    # 高德地图API配置
    amap_api_key: str = "8aa3f70ef5cb613094d14ea0fe797dd7"
    # amap_api_key: str = "5d6e7a8e7ef5fb9ddeed9f7324bb012d"

    # Unsplash API配置
    unsplash_access_key: str = "QuvNEksG7496IMigS5BhLkbiZg5MrFkszr35xutStEE"
    unsplash_secret_key: str = "AHo9Knd1T89YlVwHebQXpP1JOXc_rRFMT8_NlKEOrk8"

    # LLM配置 (从环境变量读取,由HelloAgents管理)
    openai_api_key: str = "ms-7df9fd49-9a59-495d-bf50-f2922001f367"
    openai_base_url: str = "https://api-inference.modelscope.cn/v1/"
    openai_model: str = "Qwen/Qwen2.5-72B-Instruct"

    # ============ 新增：数据库配置 ============
    # MySQL配置
    mysql_host: str = "localhost"
    mysql_port: int = 3306
    mysql_user: str = "root"
    mysql_password: str = "123456"  # 从.env读取
    mysql_database: str = "travel_agent"

    # MongoDB配置
    mongodb_host: str = "localhost"
    mongodb_port: int = 27017
    mongodb_user: str = ""  # 可选，没有用户名则留空
    mongodb_password: str = ""  # 可选，没有密码则留空
    mongodb_database: str = "test"

    # Redis配置
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_password: str = "123456"  # 从.env读取
    redis_db: int = 0

    # ============ 新增：JWT配置 ============
    jwt_secret_key: str = "UoFj5OGotDPJFlQLFTHQDZtB7QDtR3lG01Xk+iDVnY4="  # 必须在.env中设置，用于JWT签名
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_days: int = 7

    # ============ 新增：安全配置 ============
    password_min_length: int = 8
    captcha_expiry_seconds: int = 300  # 验证码有效期5分钟
    max_login_attempts: int = 5  # 最大登录尝试次数

    # ============ 新增：限流配置 ============
    rate_limit_per_minute: int = 60

    # ============ 新增：OSS云存储配置 ============
    # 阿里云OSS配置
    oss_enabled: bool = True  # 是否启用OSS（False则使用本地存储）
    oss_access_key_id: str = "LTAI5tChzi1g1csczkKBbec9"  # 从.env读取
    oss_access_key_secret: str = "b5Q8lM87zbKlbbxfvyYH8W7fXCOISiX"  # 从.env读取
    region: str = "cn-beijing"  # 从.env读取
    oss_endpoint: str = "https://oss-cn-beijing.aliyuncs.com"  # OSS地域节点
    oss_bucket_name: str = "java-webai-1"  # Bucket名称
    oss_url_prefix: str = ""  # 可选：自定义域名前缀，如 https://cdn.example.com
    oss_avatar_dir: str = "avatars"  # 头像存储目录
    oss_media_dir: str = "media"  # 媒体文件存储目录

    # 日志配置
    log_level: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"  # 忽略额外的环境变量

    def get_cors_origins_list(self) -> List[str]:
        """获取CORS origins列表"""
        return [origin.strip() for origin in self.cors_origins.split(',')]

    @property
    def mysql_url(self) -> str:
        """
        组装MySQL连接URL

        格式: mysql+pymysql://user:password@host:port/database?charset=utf8mb4
        """
        if self.mysql_password:
            return f"mysql+pymysql://{self.mysql_user}:{self.mysql_password}@{self.mysql_host}:{self.mysql_port}/{self.mysql_database}?charset=utf8mb4"
        else:
            return f"mysql+pymysql://{self.mysql_user}@{self.mysql_host}:{self.mysql_port}/{self.mysql_database}?charset=utf8mb4"

    @property
    def mongodb_uri(self) -> str:
        """
        组装MongoDB连接URI

        格式: mongodb://username:password@host:port 或 mongodb://host:port
        """
        if self.mongodb_user and self.mongodb_password:
            return f"mongodb://{self.mongodb_user}:{self.mongodb_password}@{self.mongodb_host}:{self.mongodb_port}"
        elif self.mongodb_user:
            return f"mongodb://{self.mongodb_user}@{self.mongodb_host}:{self.mongodb_port}"
        else:
            return f"mongodb://{self.mongodb_host}:{self.mongodb_port}"

    @property
    def redis_url(self) -> str:
        """
        组装Redis连接URL

        格式: redis://:password@host:port/db 或 redis://host:port/db
        """
        if self.redis_password:
            return f"redis://:{self.redis_password}@{self.redis_host}:{self.redis_port}/{self.redis_db}"
        else:
            return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"


# 创建全局配置实例
settings = Settings()


def get_settings() -> Settings:
    """获取配置实例"""
    return settings


# 验证必要的配置
def validate_config():
    """验证配置是否完整"""
    errors = []
    warnings = []

    # 验证高德地图API Key
    if not settings.amap_api_key:
        errors.append("AMAP_API_KEY未配置")

    # HelloAgentsLLM会自动从LLM_API_KEY读取,不强制要求OPENAI_API_KEY
    llm_api_key = os.getenv("LLM_API_KEY") or os.getenv("OPENAI_API_KEY")
    if not llm_api_key:
        warnings.append("LLM_API_KEY或OPENAI_API_KEY未配置,LLM功能可能无法使用")

    # ============ 新增：验证JWT密钥 ============
    if not settings.jwt_secret_key:
        errors.append("JWT_SECRET_KEY未配置，这是必需的安全密钥！请在.env中设置")
    elif len(settings.jwt_secret_key) < 32:
        warnings.append("JWT_SECRET_KEY长度过短（建议至少32个字符），安全性较低")

    # ============ 新增：验证数据库配置 ============
    # MySQL配置验证
    if not settings.mysql_password:
        warnings.append("MYSQL_PASSWORD未配置，将尝试无密码连接MySQL")
    if not settings.mysql_database:
        errors.append("MYSQL_DATABASE未配置")

    # MongoDB配置验证
    if not settings.mongodb_database:
        errors.append("MONGODB_DATABASE未配置")

    # Redis配置验证（密码可选）
    if not settings.redis_password:
        warnings.append("REDIS_PASSWORD未配置，将尝试无密码连接Redis")

    # ============ 新增：验证OSS配置 ============
    if settings.oss_enabled:
        if not settings.oss_access_key_id:
            errors.append("OSS_ACCESS_KEY_ID未配置，但OSS已启用")
        if not settings.oss_access_key_secret:
            errors.append("OSS_ACCESS_KEY_SECRET未配置，但OSS已启用")
        if not settings.oss_bucket_name:
            errors.append("OSS_BUCKET_NAME未配置")
        if not settings.oss_endpoint:
            errors.append("OSS_ENDPOINT未配置")
    else:
        warnings.append("OSS云存储未启用，将使用本地存储")

    if errors:
        error_msg = "配置错误:\n" + "\n".join(f"  - {e}" for e in errors)
        raise ValueError(error_msg)

    if warnings:
        print("\n⚠️  配置警告:")
        for w in warnings:
            print(f"  - {w}")

    return True


# 打印配置信息(用于调试)
def print_config():
    """打印当前配置(隐藏敏感信息)"""
    print(f"应用名称: {settings.app_name}")
    print(f"版本: {settings.app_version}")
    print(f"服务器: {settings.host}:{settings.port}")
    print(f"高德地图API Key: {'已配置' if settings.amap_api_key else '未配置'}")

    # 检查LLM配置
    llm_api_key = os.getenv("LLM_API_KEY") or os.getenv("OPENAI_API_KEY")
    llm_base_url = os.getenv("LLM_BASE_URL") or settings.openai_base_url
    llm_model = os.getenv("LLM_MODEL_ID") or settings.openai_model

    print(f"LLM API Key: {'已配置' if llm_api_key else '未配置'}")
    print(f"LLM Base URL: {llm_base_url}")
    print(f"LLM Model: {llm_model}")

    # ============ 新增：打印数据库配置 ============
    print("\n数据库配置:")
    print(f"  MySQL: {settings.mysql_user}@{settings.mysql_host}:{settings.mysql_port}/{settings.mysql_database}")
    print(f"  MySQL密码: {'已配置' if settings.mysql_password else '未配置（无密码）'}")
    print(f"  MongoDB: {settings.mongodb_host}:{settings.mongodb_port}/{settings.mongodb_database}")
    print(f"  MongoDB认证: {'已配置' if settings.mongodb_user and settings.mongodb_password else '未配置（无认证）'}")
    print(f"  Redis: {settings.redis_host}:{settings.redis_port}/{settings.redis_db}")
    print(f"  Redis密码: {'已配置' if settings.redis_password else '未配置（无密码）'}")

    # ============ 新增：打印JWT配置 ============
    print("\n安全配置:")
    print(f"  JWT密钥: {'已配置' if settings.jwt_secret_key else '❌ 未配置'}")
    print(f"  JWT算法: {settings.jwt_algorithm}")
    print(f"  Token有效期: {settings.jwt_access_token_expire_days}天")
    print(f"  验证码有效期: {settings.captcha_expiry_seconds}秒")

    # ============ 新增：打印OSS配置 ============
    print("\n存储配置:")
    print(f"  OSS云存储: {'✅ 已启用' if settings.oss_enabled else '❌ 未启用（使用本地存储）'}")
    if settings.oss_enabled:
        print(f"  OSS AccessKey: {'已配置' if settings.oss_access_key_id else '❌ 未配置'}")
        print(f"  OSS Endpoint: {settings.oss_endpoint}")
        print(f"  OSS Bucket: {settings.oss_bucket_name}")
        print(f"  OSS URL前缀: {settings.oss_url_prefix or '使用默认OSS域名'}")

    print(f"\n日志级别: {settings.log_level}")

