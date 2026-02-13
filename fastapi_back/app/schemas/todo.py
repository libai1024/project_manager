"""
待办相关Schema定义

将DTO与ORM模型分离，符合企业级规范。
"""
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field


class TodoBase(BaseModel):
    """待办基础信息"""
    description: str = Field(description="待办描述")
    step_ids: List[int] = Field(default_factory=list, description="关联步骤ID列表")
    completion_note: Optional[str] = Field(default=None, description="完成说明")
    is_completed: bool = Field(default=False, description="是否已完成")
    target_date: Optional[datetime] = Field(default=None, description="目标日期")


class TodoCreate(BaseModel):
    """创建待办请求"""
    project_id: Optional[int] = Field(default=None, description="所属项目ID")
    historical_project_id: Optional[int] = Field(default=None, description="所属历史项目ID")
    description: str = Field(description="待办描述")
    step_ids: List[int] = Field(default_factory=list, description="关联步骤ID列表")
    target_date: Optional[datetime] = Field(default=None, description="目标日期")


class TodoUpdate(BaseModel):
    """更新待办请求"""
    description: Optional[str] = None
    completion_note: Optional[str] = None
    is_completed: Optional[bool] = None
    target_date: Optional[datetime] = None
    attachment_ids: Optional[List[int]] = Field(default=None, description="附件ID列表")


class TodoRead(BaseModel):
    """待办响应"""
    id: int
    project_id: Optional[int] = None
    historical_project_id: Optional[int] = None
    description: str
    step_ids: List[int]
    completion_note: Optional[str] = None
    is_completed: bool
    target_date: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TodoReadWithRelations(TodoRead):
    """包含关联数据的待办响应"""
    project_title: Optional[str] = None
    step_names: List[str] = []


class TodoList(BaseModel):
    """待办列表响应"""
    items: List[TodoReadWithRelations]
    total: int
