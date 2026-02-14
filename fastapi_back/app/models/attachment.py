"""
附件数据模型（ORM + DTO）

包含数据库表定义和DTO。
"""
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING
from datetime import datetime
from enum import Enum

if TYPE_CHECKING:
    from app.models.project import Project
    from app.models.historical_project import HistoricalProject
    from app.models.attachment_folder import AttachmentFolder


class AttachmentType(str, Enum):
    """附件类型"""
    REQUIREMENT = "需求"
    PROJECT_REQUIREMENT = "项目需求"
    PROJECT_SNAPSHOT = "项目快照"
    PROPOSAL = "开题报告"
    DRAFT = "初稿"
    FINAL = "终稿"
    OTHER = "其他"


class Attachment(SQLModel, table=True):
    """附件表"""
    __tablename__ = "attachment"

    id: Optional[int] = Field(default=None, primary_key=True)
    project_id: Optional[int] = Field(default=None, foreign_key="project.id", description="所属项目ID")
    historical_project_id: Optional[int] = Field(default=None, foreign_key="historicalproject.id", description="所属历史项目ID")
    file_path: str = Field(description="文件存储路径")
    file_name: str = Field(description="文件名")
    file_type: str = Field(default="其他", description="文件类型")
    description: Optional[str] = Field(default=None, description="文件描述")
    folder_id: Optional[int] = Field(default=None, foreign_key="attachmentfolder.id", description="所属文件夹ID")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # 关系
    project: Optional["Project"] = Relationship(back_populates="attachments")
    historical_project: Optional["HistoricalProject"] = Relationship(back_populates="attachments")
    folder: Optional["AttachmentFolder"] = Relationship(back_populates="attachments")


# DTO类（保持向后兼容）
class AttachmentBase(SQLModel):
    """附件基础模型"""
    file_name: str
    file_type: str = "其他"
    description: Optional[str] = None
    folder_id: Optional[int] = None


class AttachmentCreate(AttachmentBase):
    """创建附件"""
    file_path: str
    project_id: Optional[int] = None
    historical_project_id: Optional[int] = None


class AttachmentUpdate(SQLModel):
    """更新附件"""
    file_name: Optional[str] = None
    file_type: Optional[str] = None
    description: Optional[str] = None
    folder_id: Optional[int] = None


class AttachmentRead(AttachmentBase):
    """读取附件"""
    id: int
    project_id: Optional[int] = None
    historical_project_id: Optional[int] = None
    file_path: str
    folder_name: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

