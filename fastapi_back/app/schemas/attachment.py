"""
附件相关Schema定义

将DTO与ORM模型分离，符合企业级规范。
"""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum


class AttachmentType(str, Enum):
    """附件类型枚举"""
    REQUIREMENT = "需求"
    PROPOSAL = "开题报告"
    DRAFT = "初稿"
    FINAL = "终稿"
    OTHER = "其他"


class AttachmentBase(BaseModel):
    """附件基础信息"""
    file_path: str = Field(description="文件存储路径")
    file_name: str = Field(description="文件名")
    file_type: str = Field(default="其他", description="文件类型")  # 改为string以兼容现有数据
    description: Optional[str] = Field(default=None, description="文件描述")


class AttachmentCreate(AttachmentBase):
    """创建附件请求"""
    project_id: Optional[int] = Field(default=None, description="所属项目ID")
    historical_project_id: Optional[int] = Field(default=None, description="所属历史项目ID")
    folder_id: Optional[int] = Field(default=None, description="所属文件夹ID")


class AttachmentUpdate(BaseModel):
    """更新附件请求"""
    file_name: Optional[str] = None
    file_type: Optional[str] = None  # 改为string以兼容现有数据
    description: Optional[str] = None
    folder_id: Optional[int] = None


class AttachmentRead(AttachmentBase):
    """附件响应"""
    id: int
    project_id: Optional[int] = None
    historical_project_id: Optional[int] = None
    folder_id: Optional[int] = None
    folder_name: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class AttachmentList(BaseModel):
    """附件列表响应"""
    items: list[AttachmentRead]
    total: int


class AttachmentFolderBase(BaseModel):
    """附件文件夹基础信息"""
    name: str = Field(max_length=100, description="文件夹名称")


class AttachmentFolderCreate(AttachmentFolderBase):
    """创建文件夹请求"""
    project_id: int = Field(description="所属项目ID")
    parent_id: Optional[int] = Field(default=None, description="父文件夹ID")


class AttachmentFolderUpdate(BaseModel):
    """更新文件夹请求"""
    name: Optional[str] = Field(default=None, max_length=100)
    parent_id: Optional[int] = None


class AttachmentFolderRead(AttachmentFolderBase):
    """文件夹响应"""
    id: int
    project_id: int
    parent_id: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True
