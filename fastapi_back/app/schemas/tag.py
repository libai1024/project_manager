"""
标签相关Schema定义

将DTO与ORM模型分离，符合企业级规范。
"""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


class TagBase(BaseModel):
    """标签基础信息"""
    name: str = Field(max_length=50, description="标签名称")
    color: Optional[str] = Field(default="#409eff", description="标签颜色（十六进制）")
    description: Optional[str] = Field(default=None, description="标签描述")
    is_common: bool = Field(default=False, description="是否为常用标签")


class TagCreate(TagBase):
    """创建标签请求"""
    pass


class TagUpdate(BaseModel):
    """更新标签请求"""
    name: Optional[str] = Field(default=None, max_length=50)
    color: Optional[str] = None
    description: Optional[str] = None
    is_common: Optional[bool] = None


class TagRead(TagBase):
    """标签信息响应"""
    id: int
    user_id: Optional[int] = Field(default=None, description="创建者ID")
    usage_count: int = Field(default=0, description="使用次数")
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TagList(BaseModel):
    """标签列表响应"""
    items: list[TagRead]
    total: int


class ProjectTagCreate(BaseModel):
    """创建项目标签关联请求"""
    tag_id: int = Field(description="标签ID")


class HistoricalProjectTagCreate(BaseModel):
    """创建历史项目标签关联请求"""
    tag_id: int = Field(description="标签ID")
