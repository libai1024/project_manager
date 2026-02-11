"""
项目标签模型
支持为项目添加标签，方便分类和筛选
"""
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.project import Project
    from app.models.historical_project import HistoricalProject


class TagBase(SQLModel):
    """标签基础模型"""
    name: str = Field(unique=True, index=True, description="标签名称")
    color: Optional[str] = Field(default="#409eff", description="标签颜色（十六进制）")
    description: Optional[str] = Field(default=None, description="标签描述")
    user_id: Optional[int] = Field(default=None, foreign_key="user.id", description="创建者ID（None表示系统标签）")
    is_common: bool = Field(default=False, description="是否为常用标签")
    usage_count: int = Field(default=0, description="使用次数")


class Tag(TagBase, table=True):
    """标签表"""
    __tablename__ = "tag"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.utcnow, sa_column_kwargs={"onupdate": datetime.utcnow}, description="更新时间")
    
    # 关系
    user: Optional["User"] = Relationship(back_populates="tags")
    project_tags: List["ProjectTag"] = Relationship(back_populates="tag", sa_relationship_kwargs={"cascade": "all, delete-orphan"})
    historical_project_tags: List["HistoricalProjectTag"] = Relationship(back_populates="tag", sa_relationship_kwargs={"cascade": "all, delete-orphan"})


class TagCreate(SQLModel):
    """创建标签"""
    name: str
    color: Optional[str] = "#409eff"
    description: Optional[str] = None
    is_common: Optional[bool] = False


class TagRead(TagBase):
    """读取标签"""
    id: int
    created_at: datetime
    updated_at: datetime


class TagUpdate(SQLModel):
    """更新标签"""
    name: Optional[str] = None
    color: Optional[str] = None
    description: Optional[str] = None
    is_common: Optional[bool] = None


class ProjectTagBase(SQLModel):
    """项目标签关联基础模型"""
    project_id: int = Field(foreign_key="project.id", description="项目ID")
    tag_id: int = Field(foreign_key="tag.id", description="标签ID")


class ProjectTag(ProjectTagBase, table=True):
    """项目标签关联表"""
    __tablename__ = "projecttag"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, description="创建时间")
    
    # 关系
    project: Optional["Project"] = Relationship(back_populates="tags")
    tag: Tag = Relationship(back_populates="project_tags")


class ProjectTagCreate(SQLModel):
    """创建项目标签关联"""
    tag_id: int


class HistoricalProjectTagBase(SQLModel):
    """历史项目标签关联基础模型"""
    historical_project_id: int = Field(foreign_key="historicalproject.id", description="历史项目ID")
    tag_id: int = Field(foreign_key="tag.id", description="标签ID")


class HistoricalProjectTag(HistoricalProjectTagBase, table=True):
    """历史项目标签关联表"""
    __tablename__ = "historicalprojecttag"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, description="创建时间")
    
    # 关系
    historical_project: Optional["HistoricalProject"] = Relationship(back_populates="tags")
    tag: Tag = Relationship(back_populates="historical_project_tags")


class HistoricalProjectTagCreate(SQLModel):
    """创建历史项目标签关联"""
    tag_id: int

