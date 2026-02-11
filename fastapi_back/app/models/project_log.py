"""
项目日志数据模型
"""
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING
from datetime import datetime
from enum import Enum

if TYPE_CHECKING:
    from app.models.project import Project
    from app.models.historical_project import HistoricalProject
    from app.models.user import User


class LogAction(str, Enum):
    """日志操作类型"""
    PROJECT_CREATED = "project_created"  # 创建项目
    TODO_CREATED = "todo_created"  # 创建待办
    TODO_COMPLETED = "todo_completed"  # 完成待办
    TODO_DELETED = "todo_deleted"  # 删除待办
    STEP_UPDATED = "step_updated"  # 更新步骤
    PROJECT_UPDATED = "project_updated"  # 更新项目
    PROJECT_SNAPSHOT = "project_snapshot"  # 项目快照


class ProjectLogBase(SQLModel):
    project_id: Optional[int] = Field(default=None, foreign_key="project.id", description="所属项目ID")
    historical_project_id: Optional[int] = Field(default=None, foreign_key="historicalproject.id", description="所属历史项目ID")
    action: LogAction = Field(description="操作类型")
    description: str = Field(description="操作描述")
    details: Optional[str] = Field(default=None, description="详细信息，JSON格式字符串")
    user_id: Optional[int] = Field(default=None, foreign_key="user.id", description="操作用户ID")


class ProjectLog(ProjectLogBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # 关系
    project: Optional["Project"] = Relationship(back_populates="logs")
    historical_project: Optional["HistoricalProject"] = Relationship(back_populates="logs")
    user: Optional["User"] = Relationship()


class ProjectLogCreate(SQLModel):
    project_id: Optional[int] = None
    historical_project_id: Optional[int] = None
    action: LogAction
    description: str
    details: Optional[str] = None
    user_id: Optional[int] = None


class ProjectLogRead(SQLModel):
    id: int
    project_id: Optional[int] = None
    historical_project_id: Optional[int] = None
    action: str
    description: str
    details: Optional[str] = None
    user_id: Optional[int] = None
    created_at: datetime


class ProjectLogReadWithRelations(ProjectLogRead):
    """包含关联数据的日志读取模型"""
    user_name: Optional[str] = None

