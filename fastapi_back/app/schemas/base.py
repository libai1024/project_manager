"""
基础Schema定义

提供通用的Pydantic Schema，包括分页参数和基础模型。
符合国内互联网企业级规范。

使用示例:
    from app.schemas.base import PaginationParams, BaseEntity

    class ProjectQuery(PaginationParams):
        status: Optional[str] = None
"""
from typing import Optional, Generic, TypeVar, List, Any
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

T = TypeVar('T')


class BaseSchema(BaseModel):
    """
    基础Schema配置

    所有Schema都应该继承此类
    """
    model_config = ConfigDict(
        from_attributes=True,  # 允许从ORM模型创建
        populate_by_name=True,  # 允许通过字段名填充
        use_enum_values=True,   # 枚举使用值而非枚举对象
    )


class BaseEntity(BaseSchema):
    """
    基础实体Schema

    包含通用字段：id, created_at, updated_at
    """
    id: int = Field(..., description="主键ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")


class PaginationParams(BaseSchema):
    """
    分页参数

    用于API请求的分页参数

    Attributes:
        page: 页码，从1开始
        page_size: 每页数量
    """
    page: int = Field(default=1, ge=1, description="页码，从1开始")
    page_size: int = Field(default=20, ge=1, le=100, description="每页数量")

    @property
    def skip(self) -> int:
        """计算跳过的记录数"""
        return (self.page - 1) * self.page_size

    @property
    def limit(self) -> int:
        """返回每页数量"""
        return self.page_size


class PagedResult(BaseSchema, Generic[T]):
    """
    分页结果

    用于封装分页查询结果

    Attributes:
        items: 数据列表
        total: 总记录数
        page: 当前页码
        page_size: 每页数量
        total_pages: 总页数
    """
    items: List[T] = Field(default_factory=list, description="数据列表")
    total: int = Field(default=0, ge=0, description="总记录数")
    page: int = Field(default=1, ge=1, description="当前页码")
    page_size: int = Field(default=20, ge=1, description="每页数量")
    total_pages: int = Field(default=0, ge=0, description="总页数")

    @classmethod
    def create(
        cls,
        items: List[T],
        total: int,
        page: int = 1,
        page_size: int = 20
    ) -> "PagedResult[T]":
        """
        创建分页结果

        Args:
            items: 数据列表
            total: 总记录数
            page: 当前页码
            page_size: 每页数量

        Returns:
            PagedResult实例
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

    @property
    def has_next(self) -> bool:
        """是否有下一页"""
        return self.page < self.total_pages

    @property
    def has_prev(self) -> bool:
        """是否有上一页"""
        return self.page > 1


class SimpleResponse(BaseSchema):
    """
    简单响应

    用于只需要返回成功/失败的场景

    Attributes:
        success: 是否成功
        message: 消息
    """
    success: bool = Field(default=True, description="是否成功")
    message: str = Field(default="操作成功", description="消息")


class IDResponse(BaseSchema):
    """
    ID响应

    用于创建操作返回新ID

    Attributes:
        id: 新创建的ID
    """
    id: int = Field(..., description="ID")


class CountResponse(BaseSchema):
    """
    计数响应

    用于返回数量的场景

    Attributes:
        count: 数量
    """
    count: int = Field(..., ge=0, description="数量")


# ==================== 通用查询参数 ====================

class DateRangeParams(BaseSchema):
    """
    日期范围参数

    用于按日期范围筛选
    """
    start_date: Optional[datetime] = Field(default=None, description="开始日期")
    end_date: Optional[datetime] = Field(default=None, description="结束日期")


class SearchParams(BaseSchema):
    """
    搜索参数

    用于关键词搜索
    """
    keyword: Optional[str] = Field(default=None, max_length=100, description="搜索关键词")


class OrderParams(BaseSchema):
    """
    排序参数

    用于指定排序方式
    """
    order_by: Optional[str] = Field(default=None, description="排序字段")
    order_desc: bool = Field(default=False, description="是否降序")


# ==================== 混合查询参数 ====================

class QueryParams(PaginationParams, SearchParams, OrderParams):
    """
    通用查询参数

    包含分页、搜索、排序
    """
    pass


class DateQueryParams(QueryParams, DateRangeParams):
    """
    带日期范围的查询参数
    """
    pass
