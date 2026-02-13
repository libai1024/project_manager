"""
自定义业务异常类

提供统一的异常处理机制，符合国内互联网企业级规范。
所有业务异常都应该继承自BusinessException。

使用示例:
    from app.core.exceptions import NotFoundException, ForbiddenException

    def get_project(project_id: int):
        project = repo.get_by_id(project_id)
        if not project:
            raise NotFoundException("项目")
        return project
"""
from typing import Any, Optional, Dict


class BusinessException(Exception):
    """
    业务异常基类

    Attributes:
        code: 业务错误码
        msg: 错误消息
        details: 附加详情
    """

    def __init__(
        self,
        code: int = 400,
        msg: str = "业务错误",
        details: Optional[Dict[str, Any]] = None
    ):
        self.code = code
        self.msg = msg
        self.details = details or {}
        super().__init__(msg)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        result = {
            "code": self.code,
            "msg": self.msg
        }
        if self.details:
            result["details"] = self.details
        return result


class NotFoundException(BusinessException):
    """
    资源未找到异常

    当请求的资源不存在时抛出

    Example:
        raise NotFoundException("项目")
        raise NotFoundException("用户", user_id=123)
    """

    def __init__(self, resource: str = "资源", **identifiers):
        msg = f"{resource}不存在"
        if identifiers:
            ids = ", ".join(f"{k}={v}" for k, v in identifiers.items())
            msg = f"{resource}不存在 ({ids})"
        super().__init__(code=404, msg=msg, details=identifiers if identifiers else None)


class ForbiddenException(BusinessException):
    """
    权限不足异常

    当用户没有权限执行操作时抛出

    Example:
        raise ForbiddenException("无权访问该项目")
        raise ForbiddenException()
    """

    def __init__(self, msg: str = "权限不足，无法执行此操作"):
        super().__init__(code=403, msg=msg)


class UnauthorizedException(BusinessException):
    """
    未授权异常

    当用户未登录或token无效时抛出

    Example:
        raise UnauthorizedException("登录已过期")
    """

    def __init__(self, msg: str = "未登录或登录已过期"):
        super().__init__(code=401, msg=msg)


class ValidationException(BusinessException):
    """
    验证失败异常

    当请求数据验证失败时抛出

    Example:
        raise ValidationException("用户名不能为空")
        raise ValidationException("密码格式不正确", field="password")
    """

    def __init__(self, msg: str = "数据验证失败", field: Optional[str] = None):
        details = {"field": field} if field else None
        super().__init__(code=422, msg=msg, details=details)


class DuplicateException(BusinessException):
    """
    重复异常

    当创建重复资源时抛出

    Example:
        raise DuplicateException("用户名已存在")
        raise DuplicateException("项目名称已存在", field="name")
    """

    def __init__(self, msg: str = "资源已存在", field: Optional[str] = None):
        details = {"field": field} if field else None
        super().__init__(code=1001, msg=msg, details=details)


class OperationFailedException(BusinessException):
    """
    操作失败异常

    当业务操作执行失败时抛出

    Example:
        raise OperationFailedException("创建项目失败")
        raise OperationFailedException("文件上传失败", reason="存储空间不足")
    """

    def __init__(self, msg: str = "操作失败", reason: Optional[str] = None):
        details = {"reason": reason} if reason else None
        super().__init__(code=1003, msg=msg, details=details)


class ResourceLockedException(BusinessException):
    """
    资源锁定异常

    当资源被锁定无法操作时抛出

    Example:
        raise ResourceLockedException("该用户已被锁定")
    """

    def __init__(self, msg: str = "资源已被锁定"):
        super().__init__(code=1002, msg=msg)


class FileUploadException(BusinessException):
    """
    文件上传异常

    当文件上传出现问题时抛出

    Example:
        raise FileUploadException("文件类型不支持")
        raise FileUploadException("文件大小超过限制", max_size="10MB")
    """

    def __init__(self, msg: str = "文件上传失败", **details):
        super().__init__(code=1003, msg=msg, details=details if details else None)


# ==================== 异常工具函数 ====================

def assert_exists(resource: Any, resource_name: str = "资源", **identifiers) -> None:
    """
    断言资源存在，不存在则抛出NotFoundException

    Args:
        resource: 要检查的资源
        resource_name: 资源名称
        identifiers: 资源标识符

    Raises:
        NotFoundException: 资源不存在时抛出

    Example:
        project = repo.get_by_id(project_id)
        assert_exists(project, "项目", project_id=project_id)
    """
    if resource is None:
        raise NotFoundException(resource_name, **identifiers)


def assert_permission(condition: bool, msg: str = "权限不足") -> None:
    """
    断言权限，无权限则抛出ForbiddenException

    Args:
        condition: 权限条件
        msg: 错误消息

    Raises:
        ForbiddenException: 无权限时抛出

    Example:
        assert_permission(user.role == "admin", "需要管理员权限")
    """
    if not condition:
        raise ForbiddenException(msg)
