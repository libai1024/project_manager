from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING
from datetime import datetime
from enum import Enum

if TYPE_CHECKING:
    from app.models.project import Project
    from app.models.historical_project import HistoricalProject
    from app.models.attachment_folder import AttachmentFolder


class AttachmentType(str, Enum):
    REQUIREMENT = "需求"
    PROPOSAL = "开题报告"
    DRAFT = "初稿"
    FINAL = "终稿"
    OTHER = "其他"


class AttachmentBase(SQLModel):
    project_id: Optional[int] = Field(default=None, foreign_key="project.id", description="所属项目ID")
    historical_project_id: Optional[int] = Field(default=None, foreign_key="historicalproject.id", description="所属历史项目ID")
    file_path: str
    file_name: str
    file_type: str = Field(default=AttachmentType.OTHER)
    description: Optional[str] = None
    folder_id: Optional[int] = Field(default=None, foreign_key="attachmentfolder.id", description="所属文件夹ID")


class Attachment(AttachmentBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # 关系
    project: Optional["Project"] = Relationship(back_populates="attachments")
    historical_project: Optional["HistoricalProject"] = Relationship(back_populates="attachments")
    folder: Optional["AttachmentFolder"] = Relationship(back_populates="attachments")


class AttachmentCreate(AttachmentBase):
    pass


class AttachmentRead(AttachmentBase):
    id: int
    created_at: datetime
    folder_name: Optional[str] = None  # 文件夹名称


class AttachmentUpdate(SQLModel):
    file_name: Optional[str] = None
    file_type: Optional[str] = None
    description: Optional[str] = None
    folder_id: Optional[int] = None

