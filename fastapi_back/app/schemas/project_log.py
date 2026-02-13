"""
项目日志相关Schema定义

将DTO与ORM模型分离，符合企业级规范。
"""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum


class LogAction(str, Enum):
    """日志操作类型"""
    PROJECT_CREATED = "project_created"
    TODO_CREATED = "todo_created"
    TODO_COMPLETED = "todo_completed"
    TODO_DELETED = "todo_deleted"
    STEP_UPDATED = "step_updated"
    PROJECT_UPDATED = "project_updated"
    PROJECT_SNAPSHOT = "project_snapshot"


class ProjectLogBase(BaseModel):
    """项目日志基础信息"""
    action: LogAction = Field(description="操作类型")
    description: str = Field(description="操作描述")
    details: Optional[str] = Field(default=None, description="详细信息，JSON格式")


class ProjectLogCreate(ProjectLogBase):
    """创建日志请求"""
    project_id: Optional[int] = Field(default=None, description="所属项目ID")
    historical_project_id: Optional[int] = Field(default=None, description="所属历史项目ID")
    user_id: Optional[int] = Field(default=None, description="操作用户ID")


class ProjectLogRead(BaseModel):
    """日志响应"""
    id: int
    project_id: Optional[int] = None
    historical_project_id: Optional[int] = None
    action: str
    description: str
    details: Optional[str] = None
    user_id: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ProjectLogReadWithRelations(ProjectLogRead):
    """包含关联数据的日志响应"""
    user_name: Optional[str] = None


class ProjectLogList(BaseModel):
    """日志列表响应"""
    items: list[ProjectLogReadWithRelations]
    total: int
