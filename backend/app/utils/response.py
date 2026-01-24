"""
统一响应格式工具

提供标准化的API响应格式
"""

from enum import Enum
from typing import Any, Optional, Dict
from fastapi.responses import JSONResponse


class ResponseCode(Enum):
    """响应状态码"""
    SUCCESS = 200
    CREATED = 201
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    INTERNAL_ERROR = 500


class ApiResponse:
    """统一API响应格式"""

    @staticmethod
    def _build_response(
        code: int,
        msg: str,
        data: Optional[Any] = None
    ) -> JSONResponse:
        """构建响应"""
        response_data: Dict[str, Any] = {
            "code": code,
            "msg": msg
        }
        if data is not None:
            response_data["data"] = data

        return JSONResponse(
            status_code=code if code < 500 else 500,
            content=response_data
        )

    @staticmethod
    def success(data: Optional[Any] = None, msg: str = "操作成功") -> JSONResponse:
        """成功响应"""
        return ApiResponse._build_response(
            code=ResponseCode.SUCCESS.value,
            msg=msg,
            data=data
        )

    @staticmethod
    def created(data: Optional[Any] = None, msg: str = "创建成功") -> JSONResponse:
        """创建成功响应"""
        return ApiResponse._build_response(
            code=ResponseCode.CREATED.value,
            msg=msg,
            data=data
        )

    @staticmethod
    def bad_request(msg: str = "请求参数错误", data: Optional[Any] = None) -> JSONResponse:
        """错误请求响应"""
        return ApiResponse._build_response(
            code=ResponseCode.BAD_REQUEST.value,
            msg=msg,
            data=data
        )

    @staticmethod
    def unauthorized(msg: str = "未授权", data: Optional[Any] = None) -> JSONResponse:
        """未授权响应"""
        return ApiResponse._build_response(
            code=ResponseCode.UNAUTHORIZED.value,
            msg=msg,
            data=data
        )

    @staticmethod
    def forbidden(msg: str = "禁止访问", data: Optional[Any] = None) -> JSONResponse:
        """禁止访问响应"""
        return ApiResponse._build_response(
            code=ResponseCode.FORBIDDEN.value,
            msg=msg,
            data=data
        )

    @staticmethod
    def not_found(msg: str = "资源不存在", data: Optional[Any] = None) -> JSONResponse:
        """资源不存在响应"""
        return ApiResponse._build_response(
            code=ResponseCode.NOT_FOUND.value,
            msg=msg,
            data=data
        )

    @staticmethod
    def internal_error(msg: str = "服务器内部错误", data: Optional[Any] = None) -> JSONResponse:
        """服务器错误响应"""
        return ApiResponse._build_response(
            code=ResponseCode.INTERNAL_ERROR.value,
            msg=msg,
            data=data
        )
