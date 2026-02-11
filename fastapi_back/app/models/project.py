from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime
from enum import Enum

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


class ProjectStatus(str, Enum):
    IN_PROGRESS = "进行中"
    COMPLETED = "已完成"
    PAID = "已结账"


class StepStatus(str, Enum):
    PENDING = "待开始"
    IN_PROGRESS = "进行中"
    DONE = "已完成"


# 默认步骤列表
DEFAULT_STEPS = [
    "已接单",
    "已规划",
    "硬件完成",
    "软件完成",
    "软硬调试",
    "实物验收",
    "实物邮寄",
    "论文框架",
    "论文初稿",
    "论文终稿",
    "答辩辅导",
    "毕设通过（待结账）",
    "已结账"
]


class ProjectBase(SQLModel):
    title: str = Field(index=True)
    student_name: Optional[str] = None
    platform_id: int = Field(foreign_key="platform.id")
    user_id: int = Field(foreign_key="user.id")
    price: float = Field(default=0.0)
    actual_income: float = Field(default=0.0, description="实际收入，用于dashboard统计")
    status: str = Field(default=ProjectStatus.IN_PROGRESS)
    github_url: Optional[str] = None
    requirements: Optional[str] = None
    is_paid: bool = Field(default=False)


class Project(ProjectBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
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


class ProjectCreate(ProjectBase):
    requirement_files: Optional[List[int]] = None  # 需求文件附件ID列表（创建项目时上传的文件）
    template_id: Optional[int] = None  # 步骤模板ID（如果提供，则使用模板创建步骤）
    tag_ids: Optional[List[int]] = Field(default_factory=list, description="标签ID列表")


class ProjectRead(ProjectBase):
    id: int
    created_at: datetime
    updated_at: datetime


class ProjectReadWithRelations(ProjectRead):
    """包含关联数据的项目读取模型"""
    platform: Optional["PlatformRead"] = None
    steps: List["ProjectStepRead"] = []
    tags: List["TagRead"] = []  # 项目标签
    # 配件清单在单独接口中获取，这里暂不返回完整列表，避免响应过大


class ProjectUpdate(SQLModel):
    title: Optional[str] = None
    student_name: Optional[str] = None
    platform_id: Optional[int] = None
    price: Optional[float] = None
    actual_income: Optional[float] = None
    status: Optional[str] = None
    github_url: Optional[str] = None
    requirements: Optional[str] = None
    is_paid: Optional[bool] = None
    tag_ids: Optional[List[int]] = Field(default=None, description="标签ID列表")


class ProjectStepBase(SQLModel):
    name: str
    project_id: Optional[int] = Field(default=None, foreign_key="project.id", description="所属项目ID")
    order_index: int = Field(default=0)
    status: str = Field(default=StepStatus.PENDING)
    is_todo: bool = Field(default=False)
    deadline: Optional[datetime] = None


class ProjectStep(ProjectStepBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow, sa_column_kwargs={"onupdate": datetime.utcnow})
    
    # 关系
    project: Optional[Project] = Relationship(back_populates="steps")


class ProjectStepCreate(SQLModel):
    name: str
    order_index: Optional[int] = 0
    deadline: Optional[datetime] = None


class ProjectStepRead(ProjectStepBase):
    id: int
    created_at: datetime
    updated_at: datetime


class ProjectStepUpdate(SQLModel):
    name: Optional[str] = None
    order_index: Optional[int] = None
    status: Optional[str] = None
    is_todo: Optional[bool] = None
    deadline: Optional[datetime] = None

