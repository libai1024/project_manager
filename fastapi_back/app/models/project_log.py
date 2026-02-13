"""
项目日志数据模型（ORM + DTO）

包含数据库表定义和DTO。
"""
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime
from enum import Enum

if TYPE_CHECKING:
    from app.models.project import Project
    from app.models.historical_project import HistoricalProject
    from app.models.user import User
    from app.models.attachment import Attachment


class LogAction(str, Enum):
    """日志操作类型"""
    CREATE = "create"
    PROJECT_CREATED = "project_created"
    PROJECT_UPDATED = "project_updated"
    PROJECT_DELETED = "project_deleted"
    UPDATE = "update"
    DELETE = "delete"
    STATUS_CHANGE = "status_change"
    COMMENT = "comment"
    SNAPSHOT = "snapshot"
    STEP_UPDATE = "step_update"
    STEP_CREATED = "step_created"
    STEP_DELETED = "step_deleted"
    STEP_UPDATED = "step_updated"
    FILE_UPLOAD = "file_upload"
    FILE_DELETED = "file_deleted"
    TODO_CREATED = "todo_created"
    TODO_COMPLETED = "todo_completed"
    TODO_DELETED = "todo_deleted"
    PROJECT_SNAPSHOT = "project_snapshot"
    OTHER = "other"


class ProjectLog(SQLModel, table=True):
    """项目日志表"""
    __tablename__ = "projectlog"

    id: Optional[int] = Field(default=None, primary_key=True)
    project_id: Optional[int] = Field(default=None, foreign_key="project.id", description="所属项目ID")
    historical_project_id: Optional[int] = Field(default=None, foreign_key="historicalproject.id", description="所属历史项目ID")
    action: str = Field(description="操作类型")
    description: str = Field(description="操作描述")
    details: Optional[str] = Field(default=None, description="详细信息，JSON格式")
    user_id: Optional[int] = Field(default=None, foreign_key="user.id", description="操作用户ID")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # 关系
    project: Optional["Project"] = Relationship(back_populates="logs")
    historical_project: Optional["HistoricalProject"] = Relationship(back_populates="logs")
    user: Optional["User"] = Relationship()


# DTO类（保持向后兼容）
class ProjectLogBase(SQLModel):
    """项目日志基础模型"""
    action: str
    description: str
    details: Optional[str] = None
    user_id: Optional[int] = None


class ProjectLogCreate(ProjectLogBase):
    """创建项目日志"""
    project_id: Optional[int] = None
    historical_project_id: Optional[int] = None


class ProjectLogRead(ProjectLogBase):
    """读取项目日志"""
    id: int
    project_id: Optional[int] = None
    historical_project_id: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ProjectLogReadWithRelations(ProjectLogRead):
    """包含关联的项目日志读取"""
    user_name: Optional[str] = None
    attachments: List["Attachment"] = []


# 解析前向引用 - Pydantic v2 需要手动调用
from app.models.attachment import Attachment
ProjectLogReadWithRelations.model_rebuild()

