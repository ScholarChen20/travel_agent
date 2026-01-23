"""
统一响应格式工具

提供标准的API响应格式：
{
    "code": 200,
    "msg": "请求成功",
    "data": {...}
}
"""

from typing import Any, Optional, Dict
from fastapi.responses import JSONResponse
from fastapi import status


class ResponseCode:
    """响应状态码"""
    SUCCESS = 200  # 成功
    CREATED = 201  # 创建成功
    BAD_REQUEST = 400  # 请求参数错误
    UNAUTHORIZED = 401  # 未授权
    FORBIDDEN = 403  # 禁止访问
    NOT_FOUND = 404  # 资源不存在
    INTERNAL_ERROR = 500  # 服务器内部错误


class ApiResponse:
    """统一响应格式"""

    @staticmethod
    def success(
        data: Any = None,
        msg: str = "请求成功",
        code: int = ResponseCode.SUCCESS
    ) -> Dict[str, Any]:
        """
        成功响应

        Args:
            data: 响应数据
            msg: 响应消息
            code: 响应码

        Returns:
            Dict: 标准响应格式
        """
        return {
            "code": code,
            "msg": msg,
            "data": data if data is not None else {}
        }

    @staticmethod
    def error(
        msg: str = "请求失败",
        code: int = ResponseCode.BAD_REQUEST,
        data: Any = None
    ) -> Dict[str, Any]:
        """
        错误响应

        Args:
            msg: 错误消息
            code: 错误码
            data: 额外数据

        Returns:
            Dict: 标准响应格式
        """
        return {
            "code": code,
            "msg": msg,
            "data": data if data is not None else {}
        }

    @staticmethod
    def created(
        data: Any = None,
        msg: str = "创建成功"
    ) -> Dict[str, Any]:
        """创建成功响应"""
        return ApiResponse.success(data=data, msg=msg, code=ResponseCode.CREATED)

    @staticmethod
    def bad_request(msg: str = "请求参数错误", data: Any = None) -> Dict[str, Any]:
        """请求参数错误响应"""
        return ApiResponse.error(msg=msg, code=ResponseCode.BAD_REQUEST, data=data)

    @staticmethod
    def unauthorized(msg: str = "未授权", data: Any = None) -> Dict[str, Any]:
        """未授权响应"""
        return ApiResponse.error(msg=msg, code=ResponseCode.UNAUTHORIZED, data=data)

    @staticmethod
    def forbidden(msg: str = "禁止访问", data: Any = None) -> Dict[str, Any]:
        """禁止访问响应"""
        return ApiResponse.error(msg=msg, code=ResponseCode.FORBIDDEN, data=data)

    @staticmethod
    def not_found(msg: str = "资源不存在", data: Any = None) -> Dict[str, Any]:
        """资源不存在响应"""
        return ApiResponse.error(msg=msg, code=ResponseCode.NOT_FOUND, data=data)

    @staticmethod
    def internal_error(msg: str = "服务器内部错误", data: Any = None) -> Dict[str, Any]:
        """服务器内部错误响应"""
        return ApiResponse.error(msg=msg, code=ResponseCode.INTERNAL_ERROR, data=data)


# 便捷函数
def success_response(data: Any = None, msg: str = "请求成功") -> Dict[str, Any]:
    """成功响应的便捷函数"""
    return ApiResponse.success(data=data, msg=msg)


def error_response(msg: str = "请求失败", code: int = ResponseCode.BAD_REQUEST) -> Dict[str, Any]:
    """错误响应的便捷函数"""
    return ApiResponse.error(msg=msg, code=code)
