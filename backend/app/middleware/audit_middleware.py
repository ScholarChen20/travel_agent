"""
审计日志中间件（AOP切面拦截）

功能：
- 自动拦截所有 /api/* 请求
- 记录 HTTP 方法、路径、状态码、耗时、用户信息
- 捕获响应体（成功数据 / 错误消息）存入 details 字段，方便追溯
- 异步写入 MySQL，不阻塞主请求流程
- 排除噪音路径（验证码、健康检查、文档）
"""

import asyncio
import time
import json
from datetime import datetime
from typing import Optional

import jwt
from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp


# 不记录日志的路径集合
EXCLUDE_PATHS = {
    # 管理员段部分接口
    "/api/admin/health",
    "/api/admin/metrics",
    "/api/admin/stats/visualization",
    "/api/admin/stats",
    "/api/admin/logs/audit",

    "/api/auth/captcha",
    "/api/health",
    "/api/docs",
    "/api/openapi.json",
    "/api/redoc",
    "/docs",
    "/redoc",
    "/openapi.json",
    "/health",
}

# 需要脱敏的字段（请求体 & 响应体均适用）
SENSITIVE_FIELDS = {
    "password", "token", "captcha_code", "captcha_session_id",
    "captcha", "access_token", "refresh_token", "password_hash",
}

# 响应体最大存储字节数（超出截断，避免大列表撑爆 details 字段）
MAX_RESPONSE_BYTES = 8 * 1024  # 8 KB


def _get_client_ip(request: Request) -> str:
    """从请求头提取真实客户端IP"""
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip.strip()
    return request.client.host if request.client else "unknown"


def _sanitize(obj):
    """递归脱敏：将字典中敏感字段的值替换为 '***'"""
    if isinstance(obj, dict):
        return {k: "***" if k in SENSITIVE_FIELDS else _sanitize(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_sanitize(item) for item in obj]
    return obj


def _parse_json_bytes(data: bytes) -> Optional[object]:
    """安全解析 JSON bytes，失败返回 None"""
    if not data:
        return None
    try:
        return json.loads(data)
    except Exception:
        return None


def _extract_response_detail(body_bytes: bytes, status_code: int) -> Optional[dict]:
    """
    从响应体中提取关键信息存入 details["response"]：
    - 成功（2xx）：保留精简的响应结构，截断超长 data
    - 失败（4xx/5xx）：只保留 msg / detail / error 字段
    """
    parsed = _parse_json_bytes(body_bytes)
    if parsed is None:
        return None

    if not isinstance(parsed, dict):
        return None

    sanitized = _sanitize(parsed)

    if status_code >= 400:
        # 只保留错误信息字段
        error_keys = ("msg", "detail", "error", "message", "code")
        return {k: sanitized[k] for k in error_keys if k in sanitized} or sanitized

    # 成功响应：截断 data 字段防止过大
    result = {k: v for k, v in sanitized.items() if k != "data"}
    if "data" in sanitized:
        data_str = json.dumps(sanitized["data"], ensure_ascii=False)
        if len(data_str.encode()) <= MAX_RESPONSE_BYTES:
            result["data"] = sanitized["data"]
        else:
            # 截断提示
            result["data"] = f"[响应数据过大，已截断，原始长度 {len(data_str)} 字节]"
    return result


def _extract_user_from_token(authorization: Optional[str]) -> tuple[Optional[int], Optional[str]]:
    """从 Authorization Bearer 头中解码用户信息，无需数据库查询"""
    if not authorization or not authorization.startswith("Bearer "):
        return None, None
    token = authorization[7:]
    try:
        from ..config import get_settings
        settings = get_settings()
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
            options={"verify_exp": False}  # 仅做身份识别，不重复校验过期
        )
        user_id_str = payload.get("sub")
        username = payload.get("username")
        user_id = int(user_id_str) if user_id_str else None
        return user_id, username
    except Exception:
        return None, None


async def _save_log_async(
    user_id: Optional[int],
    username: Optional[str],
    method: str,
    path: str,
    status_code: int,
    duration_ms: int,
    ip_address: str,
    user_agent: str,
    request_body: Optional[object],
    response_detail: Optional[dict],
):
    """异步写入审计日志到 MySQL"""
    try:
        from ..database.mysql import get_mysql_db
        from ..database.models import AuditLog

        response_status = "success" if status_code < 400 else "error"

        # 根据 HTTP 语义推导 action / resource
        parts = [p for p in path.split("/") if p]
        resource = parts[1] if len(parts) > 1 else path
        action_map = {"GET": "查询", "POST": "创建", "PUT": "更新", "PATCH": "更新", "DELETE": "删除"}
        action = action_map.get(method.upper(), method.upper())

        # 组装 details：请求体 + 响应结果
        details: dict = {}
        if request_body:
            details["request"] = request_body
        if response_detail:
            details["response"] = response_detail

        db = get_mysql_db()
        with db.get_session() as session:
            log_entry = AuditLog(
                user_id=user_id,
                username=username,
                action=action,
                resource=resource,
                resource_id=None,
                details=details if details else None,
                ip_address=ip_address,
                user_agent=user_agent[:500] if user_agent else None,
                method=method.upper(),
                path=path,
                status_code=status_code,
                duration_ms=duration_ms,
                response_status=response_status,
                created_at=datetime.now(),
            )
            session.add(log_entry)
            session.commit()
    except Exception as e:
        logger.warning(f"[AuditMiddleware] 写入审计日志失败: {e}")


class AuditMiddleware(BaseHTTPMiddleware):
    """全量 API 审计日志中间件"""

    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next) -> Response:
        path = request.url.path

        # 排除噪音路径
        if path in EXCLUDE_PATHS or not path.startswith("/api/"):
            return await call_next(request)

        start_ts = time.time()

        # ---- 读取并重放请求体（body 只能消费一次）----
        body_bytes = b""
        try:
            body_bytes = await request.body()
        except Exception:
            pass

        # 用缓存的 body_bytes 重建 receive callable，让后续中间件/路由仍能读取 body
        async def receive():
            return {"type": "http.request", "body": body_bytes, "more_body": False}

        request._receive = receive  # type: ignore[attr-defined]

        # 调用下一个处理器
        response = await call_next(request)

        duration_ms = int((time.time() - start_ts) * 1000)

        # ---- 消费响应体，并重建可再次读取的 Response ----
        response_body_bytes = b""
        try:
            chunks = []
            async for chunk in response.body_iterator:
                chunks.append(chunk)
            response_body_bytes = b"".join(chunks)
        except Exception as e:
            logger.warning(f"[AuditMiddleware] 读取响应体失败: {e}")

        # 用原始 body 重建响应（保持 status_code / headers / media_type）
        rebuilt_response = Response(
            content=response_body_bytes,
            status_code=response.status_code,
            headers=dict(response.headers),
            media_type=response.media_type,
        )

        # 提取日志信息
        authorization = request.headers.get("Authorization")
        user_id, username = _extract_user_from_token(authorization)
        ip_address = _get_client_ip(request)
        user_agent = request.headers.get("user-agent", "")

        # 脱敏请求体
        req_parsed = _parse_json_bytes(body_bytes)
        sanitized_request = _sanitize(req_parsed) if req_parsed else None

        # 提取响应摘要
        response_detail = _extract_response_detail(response_body_bytes, response.status_code)

        # 异步写日志，不阻塞响应返回
        asyncio.create_task(
            _save_log_async(
                user_id=user_id,
                username=username,
                method=request.method,
                path=path,
                status_code=response.status_code,
                duration_ms=duration_ms,
                ip_address=ip_address,
                user_agent=user_agent,
                request_body=sanitized_request,
                response_detail=response_detail,
            )
        )

        return rebuilt_response
