"""
附件文件夹模型
"""
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime

if TYPE_CHECKING:
    from app.models.project import Project
    from app.models.historical_project import HistoricalProject
    from app.models.attachment import Attachment


class AttachmentFolderBase(SQLModel):
    project_id: Optional[int] = Field(default=None, foreign_key="project.id", description="所属项目ID")
    historical_project_id: Optional[int] = Field(default=None, foreign_key="historicalproject.id", description="所属历史项目ID")
    name: str = Field(index=True, description="文件夹名称")
    is_default: bool = Field(default=False, description="是否为默认文件夹")
    description: Optional[str] = None


class AttachmentFolder(AttachmentFolderBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow, sa_column_kwargs={"onupdate": datetime.utcnow})
    
    # 关系
    project: Optional["Project"] = Relationship(back_populates="folders")
    historical_project: Optional["HistoricalProject"] = Relationship(back_populates="folders")
    attachments: List["Attachment"] = Relationship(back_populates="folder", sa_relationship_kwargs={"cascade": "all, delete-orphan"})


class AttachmentFolderCreate(SQLModel):
    name: str
    description: Optional[str] = None


class AttachmentFolderUpdate(SQLModel):
    name: Optional[str] = None
    description: Optional[str] = None


class AttachmentFolderRead(AttachmentFolderBase):
    id: int
    created_at: datetime
    updated_at: datetime
    attachment_count: Optional[int] = 0  # 附件数量

