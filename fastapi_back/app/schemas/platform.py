"""
平台相关Schema定义

将DTO与ORM模型分离，符合企业级规范。
"""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


class PlatformBase(BaseModel):
    """平台基础信息"""
    name: str = Field(max_length=100, description="平台名称")
    description: Optional[str] = Field(default=None, description="平台描述")


class PlatformCreate(PlatformBase):
    """创建平台请求"""
    pass


class PlatformUpdate(BaseModel):
    """更新平台请求"""
    name: Optional[str] = Field(default=None, max_length=100)
    description: Optional[str] = None


class PlatformRead(PlatformBase):
    """平台信息响应"""
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class PlatformList(BaseModel):
    """平台列表响应"""
    items: list[PlatformRead]
    total: int
