"""
待办数据模型
"""
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime

if TYPE_CHECKING:
    from app.models.project import Project
    from app.models.historical_project import HistoricalProject


class TodoBase(SQLModel):
    project_id: Optional[int] = Field(default=None, foreign_key="project.id", description="所属项目ID")
    historical_project_id: Optional[int] = Field(default=None, foreign_key="historicalproject.id", description="所属历史项目ID")
    description: str
    step_ids: str = Field(description="步骤ID列表，JSON格式字符串，如 '[1,2,3]'")
    completion_note: Optional[str] = Field(default=None, description="完成描述")
    is_completed: bool = Field(default=False)
    target_date: Optional[datetime] = Field(default=None, description="目标日期")


class Todo(TodoBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow, sa_column_kwargs={"onupdate": datetime.utcnow})
    
    # 关系
    project: Optional["Project"] = Relationship(back_populates="todos")
    historical_project: Optional["HistoricalProject"] = Relationship(back_populates="todos")


class TodoCreate(SQLModel):
    project_id: Optional[int] = None
    historical_project_id: Optional[int] = None
    description: str
    step_ids: List[int]
    target_date: Optional[datetime] = None


class TodoUpdate(SQLModel):
    description: Optional[str] = None
    completion_note: Optional[str] = None
    is_completed: Optional[bool] = None
    target_date: Optional[datetime] = None
    attachment_ids: Optional[List[int]] = None  # 附件ID列表


class TodoRead(SQLModel):
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


class TodoReadWithRelations(TodoRead):
    """包含关联数据的待办读取模型"""
    project_title: Optional[str] = None
    step_names: List[str] = []

