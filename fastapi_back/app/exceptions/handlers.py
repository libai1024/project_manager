"""
统一异常处理器

提供全局异常处理，将所有异常转换为统一的响应格式。
符合国内互联网企业级规范，响应格式: { code, msg, data, details }

使用示例:
    # 在main.py中
    from app.exceptions.handlers import setup_exception_handlers
    setup_exception_handlers(app)
"""
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi import HTTPException
import logging
import traceback
from typing import Any, Dict

from app.core.exceptions import BusinessException

logger = logging.getLogger(__name__)


def _create_error_response(
    code: int,
    msg: str,
    status_code: int = 200,
    details: Any = None
) -> JSONResponse:
    """
    创建错误响应

    Args:
        code: 业务错误码
        msg: 错误消息
        status_code: HTTP状态码
        details: 附加详情

    Returns:
        JSONResponse
    """
    content: Dict[str, Any] = {
        "code": code,
        "msg": msg,
        "data": None
    }
    if details:
        content["details"] = details

    return JSONResponse(
        status_code=status_code,
        content=content
    )


def setup_exception_handlers(app):
    """
    设置异常处理器

    注册所有异常处理器到FastAPI应用

    Args:
        app: FastAPI应用实例
    """

    @app.exception_handler(BusinessException)
    async def business_exception_handler(request: Request, exc: BusinessException):
        """
        业务异常处理器

        处理所有继承自BusinessException的自定义异常
        """
        logger.warning(
            f"Business Exception: code={exc.code}, msg={exc.msg}, "
            f"path={request.url.path}, method={request.method}"
        )

        # 根据错误码确定HTTP状态码
        if exc.code == 401:
            http_status = status.HTTP_401_UNAUTHORIZED
        elif exc.code == 403:
            http_status = status.HTTP_403_FORBIDDEN
        elif exc.code == 404:
            http_status = status.HTTP_404_NOT_FOUND
        elif exc.code == 422:
            http_status = status.HTTP_422_UNPROCESSABLE_ENTITY
        elif exc.code >= 500:
            http_status = status.HTTP_500_INTERNAL_SERVER_ERROR
        else:
            http_status = status.HTTP_400_BAD_REQUEST

        return _create_error_response(
            code=exc.code,
            msg=exc.msg,
            status_code=http_status,
            details=exc.details if exc.details else None
        )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        """
        HTTP异常处理器

        处理FastAPI的HTTPException
        """
        logger.warning(
            f"HTTP Exception: status={exc.status_code}, detail={exc.detail}, "
            f"path={request.url.path}"
        )

        # 将HTTP状态码映射为业务错误码
        code = exc.status_code
        msg = str(exc.detail) if exc.detail else _get_default_message(exc.status_code)

        return _create_error_response(
            code=code,
            msg=msg,
            status_code=exc.status_code
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """
        请求验证异常处理器

        处理Pydantic验证错误
        """
        errors = exc.errors()
        logger.warning(
            f"Validation Error: path={request.url.path}, errors={errors}"
        )

        # 格式化错误信息
        formatted_errors = _format_validation_errors(errors)

        return _create_error_response(
            code=422,
            msg="数据验证失败",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details=formatted_errors
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """
        通用异常处理器

        处理所有未捕获的异常
        """
        # 记录完整错误堆栈
        logger.error(
            f"Unhandled Exception: path={request.url.path}, method={request.method}, "
            f"error={str(exc)}",
            exc_info=True
        )

        # 生产环境不返回详细错误信息
        return _create_error_response(
            code=500,
            msg="服务器内部错误",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


def _get_default_message(status_code: int) -> str:
    """
    获取HTTP状态码对应的默认消息

    Args:
        status_code: HTTP状态码

    Returns:
        默认消息
    """
    messages = {
        400: "请求参数错误",
        401: "未授权访问",
        403: "权限不足",
        404: "资源不存在",
        405: "请求方法不允许",
        408: "请求超时",
        429: "请求过于频繁",
        500: "服务器内部错误",
        502: "网关错误",
        503: "服务暂时不可用",
        504: "网关超时",
    }
    return messages.get(status_code, "请求失败")


def _format_validation_errors(errors: list) -> list:
    """
    格式化验证错误信息

    Args:
        errors: Pydantic验证错误列表

    Returns:
        格式化后的错误列表
    """
    formatted = []
    for error in errors:
        location = " -> ".join(str(loc) for loc in error.get("loc", []))
        formatted.append({
            "field": location,
            "message": error.get("msg", "验证失败"),
            "type": error.get("type", "value_error")
        })
    return formatted
