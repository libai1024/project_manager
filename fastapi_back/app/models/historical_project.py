"""
历史项目模型
支持导入历史项目和文件，兼容现有所有模块
"""
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime
from pydantic import field_validator

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.platform import Platform
    from app.models.attachment import Attachment
    from app.models.attachment_folder import AttachmentFolder
    from app.models.todo import Todo
    from app.models.project_log import ProjectLog
    from app.models.project_part import ProjectPart
    from app.models.github_commit import GitHubCommit
    from app.models.video_playback import VideoPlayback
    from app.models.tag import HistoricalProjectTag


class HistoricalProjectBase(SQLModel):
    """历史项目基础模型"""
    title: str = Field(index=True, description="项目标题")
    student_name: Optional[str] = Field(default=None, description="学生姓名")
    platform_id: Optional[int] = Field(default=None, foreign_key="platform.id", description="平台ID")
    user_id: int = Field(foreign_key="user.id", description="创建人ID")
    price: float = Field(default=0.0, description="项目价格")
    actual_income: float = Field(default=0.0, description="实际收入")
    status: str = Field(default="已完成", description="项目状态")
    github_url: Optional[str] = Field(default=None, description="GitHub地址")
    requirements: Optional[str] = Field(default=None, description="需求描述")
    is_paid: bool = Field(default=False, description="是否已结账")
    
    # 历史项目特有字段
    original_project_id: Optional[int] = Field(default=None, description="原始项目ID（如果从现有项目导入）")
    imported_at: datetime = Field(default_factory=datetime.utcnow, description="导入时间")
    import_source: Optional[str] = Field(default=None, description="导入来源（手动导入/批量导入等）")
    completion_date: Optional[datetime] = Field(default=None, description="完成日期")
    notes: Optional[str] = Field(default=None, description="备注")


class HistoricalProject(HistoricalProjectBase, table=True):
    """历史项目表"""
    __tablename__ = "historicalproject"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.utcnow, sa_column_kwargs={"onupdate": datetime.utcnow}, description="更新时间")
    
    # 关系 - 兼容现有所有模块
    platform: Optional["Platform"] = Relationship(back_populates="historical_projects")
    user: "User" = Relationship(back_populates="historical_projects")
    attachments: List["Attachment"] = Relationship(
        back_populates="historical_project",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
    folders: List["AttachmentFolder"] = Relationship(
        back_populates="historical_project",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
    todos: List["Todo"] = Relationship(
        back_populates="historical_project",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
    logs: List["ProjectLog"] = Relationship(
        back_populates="historical_project",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
    parts: List["ProjectPart"] = Relationship(
        back_populates="historical_project",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
    github_commits: List["GitHubCommit"] = Relationship(
        back_populates="historical_project",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
    video_playbacks: List["VideoPlayback"] = Relationship(
        back_populates="historical_project",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
    tags: List["HistoricalProjectTag"] = Relationship(
        back_populates="historical_project",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )


class HistoricalProjectCreate(SQLModel):
    """创建历史项目"""
    title: str = Field(min_length=1, max_length=200)
    student_name: Optional[str] = None
    platform_id: Optional[int] = None
    price: float = 0.0
    actual_income: float = 0.0
    status: str = "已完成"
    github_url: Optional[str] = None
    requirements: Optional[str] = None
    is_paid: bool = False
    original_project_id: Optional[int] = None
    import_source: Optional[str] = None
    completion_date: Optional[datetime] = None
    notes: Optional[str] = None
    requirement_files: Optional[List[int]] = None  # 需求文件附件ID列表

    @field_validator('title')
    @classmethod
    def title_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('项目标题不能为空')
        return v.strip()


class HistoricalProjectRead(HistoricalProjectBase):
    """读取历史项目"""
    id: int
    created_at: datetime
    updated_at: datetime
    imported_at: datetime


class HistoricalProjectReadWithRelations(HistoricalProjectRead):
    """包含关联数据的历史项目读取模型"""
    platform_name: Optional[str] = None
    user_name: Optional[str] = None
    tags: List["TagRead"] = []  # 历史项目标签
    attachment_count: int = 0
    folder_count: int = 0
    todo_count: int = 0
    log_count: int = 0
    part_count: int = 0


class HistoricalProjectUpdate(SQLModel):
    """更新历史项目"""
    title: Optional[str] = None
    student_name: Optional[str] = None
    platform_id: Optional[int] = None
    price: Optional[float] = None
    actual_income: Optional[float] = None
    status: Optional[str] = None
    github_url: Optional[str] = None
    requirements: Optional[str] = None
    is_paid: Optional[bool] = None
    completion_date: Optional[datetime] = None
    notes: Optional[str] = None


class HistoricalProjectImportRequest(SQLModel):
    """历史项目导入请求"""
    projects: List[HistoricalProjectCreate]  # 批量导入多个项目
    import_source: Optional[str] = "手动导入"

