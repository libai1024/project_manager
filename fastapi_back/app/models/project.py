"""
项目数据模型（ORM）

仅包含数据库表定义，DTO已移至schemas目录。
"""
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime

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
    from app.models.tag import ProjectTag


class Project(SQLModel, table=True):
    """项目表"""
    __tablename__ = "project"

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(index=True, max_length=200)
    student_name: Optional[str] = Field(default=None, max_length=100)
    platform_id: int = Field(foreign_key="platform.id")
    user_id: int = Field(foreign_key="user.id")
    price: float = Field(default=0.0)
    actual_income: float = Field(default=0.0, description="实际收入")
    status: str = Field(default="进行中")
    github_url: Optional[str] = Field(default=None, max_length=500)
    requirements: Optional[str] = None
    is_paid: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow, sa_column_kwargs={"onupdate": datetime.utcnow})

    # 关系
    platform: "Platform" = Relationship(back_populates="projects")
    user: "User" = Relationship(back_populates="projects")
    steps: List["ProjectStep"] = Relationship(back_populates="project", sa_relationship_kwargs={"cascade": "all, delete-orphan"})
    attachments: List["Attachment"] = Relationship(back_populates="project", sa_relationship_kwargs={"cascade": "all, delete-orphan"})
    folders: List["AttachmentFolder"] = Relationship(back_populates="project", sa_relationship_kwargs={"cascade": "all, delete-orphan"})
    todos: List["Todo"] = Relationship(back_populates="project", sa_relationship_kwargs={"cascade": "all, delete-orphan"})
    logs: List["ProjectLog"] = Relationship(back_populates="project", sa_relationship_kwargs={"cascade": "all, delete-orphan"})
    parts: List["ProjectPart"] = Relationship(back_populates="project", sa_relationship_kwargs={"cascade": "all, delete-orphan"})
    github_commits: List["GitHubCommit"] = Relationship(back_populates="project", sa_relationship_kwargs={"cascade": "all, delete-orphan"})
    video_playbacks: List["VideoPlayback"] = Relationship(back_populates="project", sa_relationship_kwargs={"cascade": "all, delete-orphan"})
    tags: List["ProjectTag"] = Relationship(back_populates="project", sa_relationship_kwargs={"cascade": "all, delete-orphan"})


class ProjectStep(SQLModel, table=True):
    """项目步骤表"""
    __tablename__ = "projectstep"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=100)
    project_id: Optional[int] = Field(default=None, foreign_key="project.id")
    order_index: int = Field(default=0)
    status: str = Field(default="待开始")
    is_todo: bool = Field(default=False)
    deadline: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow, sa_column_kwargs={"onupdate": datetime.utcnow})

    # 关系
    project: Optional[Project] = Relationship(back_populates="steps")

