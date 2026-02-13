"""
待办数据模型（ORM + DTO）

包含数据库表定义和DTO。
"""
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime, date

if TYPE_CHECKING:
    from app.models.project import Project
    from app.models.historical_project import HistoricalProject


class Todo(SQLModel, table=True):
    """待办表"""
    __tablename__ = "todo"

    id: Optional[int] = Field(default=None, primary_key=True)
    project_id: Optional[int] = Field(default=None, foreign_key="project.id", description="所属项目ID")
    historical_project_id: Optional[int] = Field(default=None, foreign_key="historicalproject.id", description="所属历史项目ID")
    description: str = Field(description="待办描述")
    step_ids: str = Field(description="步骤ID列表，JSON格式字符串")
    completion_note: Optional[str] = Field(default=None, description="完成说明")
    is_completed: bool = Field(default=False, description="是否已完成")
    target_date: Optional[datetime] = Field(default=None, description="目标日期")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow, sa_column_kwargs={"onupdate": datetime.utcnow})

    # 关系
    project: Optional["Project"] = Relationship(back_populates="todos")
    historical_project: Optional["HistoricalProject"] = Relationship(back_populates="todos")


# DTO类（保持向后兼容）
class TodoBase(SQLModel):
    """待办基础模型"""
    description: str
    step_ids: List[int] = []
    completion_note: Optional[str] = None
    is_completed: bool = False
    target_date: Optional[datetime] = None


class TodoCreate(TodoBase):
    """创建待办"""
    project_id: Optional[int] = None
    historical_project_id: Optional[int] = None


class TodoUpdate(SQLModel):
    """更新待办"""
    description: Optional[str] = None
    step_ids: Optional[List[int]] = None
    completion_note: Optional[str] = None
    is_completed: Optional[bool] = None
    target_date: Optional[datetime] = None
    attachment_ids: Optional[List[int]] = None


class TodoRead(TodoBase):
    """读取待办"""
    id: int
    project_id: Optional[int] = None
    historical_project_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TodoReadWithRelations(TodoRead):
    """包含关联的待办读取"""
    project_title: Optional[str] = None
    step_names: List[str] = []
    student_name: Optional[str] = None

