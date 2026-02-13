"""
统一API响应模型

提供标准化的API响应格式，符合国内互联网企业级规范。
响应格式: { code: int, msg: str, data: T }

使用示例:
    from app.api.responses import success, error, ApiResponse

    @router.get("/", response_model=ApiResponse[List[Project]])
    async def list_projects():
        projects = await service.list_all()
        return success(projects)

    @router.get("/{id}", response_model=ApiResponse[Project])
    async def get_project(id: int):
        project = await service.get_by_id(id)
        if not project:
            return error(404, "项目不存在")
        return success(project)
"""
from typing import Generic, TypeVar, Optional, List, Any
from pydantic import BaseModel, Field

T = TypeVar('T')


class ApiResponse(BaseModel, Generic[T]):
    """
    统一API响应模型

    Attributes:
        code: 业务状态码，200表示成功，其他表示错误
        msg: 响应消息
        data: 响应数据
    """
    code: int = Field(default=200, description="业务状态码")
    msg: str = Field(default="success", description="响应消息")
    data: Optional[T] = Field(default=None, description="响应数据")

    class Config:
        json_schema_extra = {
            "example": {
                "code": 200,
                "msg": "success",
                "data": None
            }
        }


class PagedData(BaseModel, Generic[T]):
    """
    分页数据模型

    Attributes:
        items: 数据列表
        total: 总记录数
        page: 当前页码（从1开始）
        page_size: 每页记录数
        total_pages: 总页数
    """
    items: List[T] = Field(default_factory=list, description="数据列表")
    total: int = Field(default=0, ge=0, description="总记录数")
    page: int = Field(default=1, ge=1, description="当前页码")
    page_size: int = Field(default=20, ge=1, le=100, description="每页记录数")
    total_pages: int = Field(default=0, ge=0, description="总页数")

    @classmethod
    def create(cls, items: List[T], total: int, page: int, page_size: int) -> "PagedData[T]":
        """
        创建分页数据

        Args:
            items: 数据列表
            total: 总记录数
            page: 当前页码
            page_size: 每页记录数

        Returns:
            PagedData实例
        """
        import math
        total_pages = math.ceil(total / page_size) if page_size > 0 else 0
        return cls(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )


class PagedResponse(ApiResponse[PagedData[T]], Generic[T]):
    """
    分页响应模型

    继承ApiResponse，data字段为PagedData类型
    """
    data: Optional[PagedData[T]] = Field(default=None, description="分页数据")

    class Config:
        json_schema_extra = {
            "example": {
                "code": 200,
                "msg": "success",
                "data": {
                    "items": [],
                    "total": 0,
                    "page": 1,
                    "page_size": 20,
                    "total_pages": 0
                }
            }
        }


# ==================== 响应构造函数 ====================

def success(data: T = None, msg: str = "success") -> ApiResponse[T]:
    """
    构造成功响应

    Args:
        data: 响应数据
        msg: 响应消息

    Returns:
        ApiResponse实例

    Example:
        return success(user, "获取用户成功")
    """
    return ApiResponse(code=200, msg=msg, data=data)


def error(code: int = 500, msg: str = "error", data: Any = None) -> ApiResponse:
    """
    构造错误响应

    Args:
        code: 错误码
        msg: 错误消息
        data: 附加数据

    Returns:
        ApiResponse实例

    Example:
        return error(404, "用户不存在")
    """
    return ApiResponse(code=code, msg=msg, data=data)


def paged_success(
    items: List[T],
    total: int,
    page: int = 1,
    page_size: int = 20,
    msg: str = "success"
) -> PagedResponse[T]:
    """
    构造分页成功响应

    Args:
        items: 数据列表
        total: 总记录数
        page: 当前页码
        page_size: 每页记录数
        msg: 响应消息

    Returns:
        PagedResponse实例

    Example:
        return paged_success(projects, total, page, page_size)
    """
    paged_data = PagedData.create(items, total, page, page_size)
    return PagedResponse(code=200, msg=msg, data=paged_data)


# ==================== 常用响应码定义 ====================

class ResponseCode:
    """响应码常量定义"""
    SUCCESS = 200
    CREATED = 201
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    VALIDATION_ERROR = 422
    INTERNAL_ERROR = 500
    SERVICE_UNAVAILABLE = 503

    # 业务错误码 (1000+)
    BUSINESS_ERROR = 1000
    DUPLICATE_ERROR = 1001
    RESOURCE_LOCKED = 1002
    OPERATION_FAILED = 1003
