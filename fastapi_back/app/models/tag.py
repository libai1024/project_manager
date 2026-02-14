"""
标签数据模型（ORM + DTO）

包含数据库表定义和DTO。
"""
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime
from pydantic import field_validator

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.project import Project
    from app.models.historical_project import HistoricalProject


class Tag(SQLModel, table=True):
    """标签表"""
    __tablename__ = "tag"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True, index=True, max_length=50, description="标签名称")
    color: Optional[str] = Field(default="#409eff", description="标签颜色")
    description: Optional[str] = Field(default=None, description="标签描述")
    user_id: Optional[int] = Field(default=None, foreign_key="user.id", description="创建者ID")
    is_common: bool = Field(default=False, description="是否为常用标签")
    usage_count: int = Field(default=0, description="使用次数")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow, sa_column_kwargs={"onupdate": datetime.utcnow})

    # 关系
    user: Optional["User"] = Relationship(back_populates="tags")
    project_tags: List["ProjectTag"] = Relationship(back_populates="tag", sa_relationship_kwargs={"cascade": "all, delete-orphan"})
    historical_project_tags: List["HistoricalProjectTag"] = Relationship(back_populates="tag", sa_relationship_kwargs={"cascade": "all, delete-orphan"})


class ProjectTag(SQLModel, table=True):
    """项目标签关联表"""
    __tablename__ = "projecttag"

    id: Optional[int] = Field(default=None, primary_key=True)
    project_id: int = Field(foreign_key="project.id", description="项目ID")
    tag_id: int = Field(foreign_key="tag.id", description="标签ID")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # 关系
    project: Optional["Project"] = Relationship(back_populates="tags")
    tag: Tag = Relationship(back_populates="project_tags")


class HistoricalProjectTag(SQLModel, table=True):
    """历史项目标签关联表"""
    __tablename__ = "historicalprojecttag"

    id: Optional[int] = Field(default=None, primary_key=True)
    historical_project_id: int = Field(foreign_key="historicalproject.id", description="历史项目ID")
    tag_id: int = Field(foreign_key="tag.id", description="标签ID")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # 关系
    historical_project: Optional["HistoricalProject"] = Relationship(back_populates="tags")
    tag: Tag = Relationship(back_populates="historical_project_tags")


# DTO类（保持向后兼容）
class TagBase(SQLModel):
    """标签基础模型"""
    name: str = Field(max_length=50)
    color: Optional[str] = "#409eff"
    description: Optional[str] = None


class TagCreate(SQLModel):
    """创建标签"""
    name: str = Field(min_length=1, max_length=50)
    color: Optional[str] = "#409eff"
    description: Optional[str] = None

    @field_validator('name')
    @classmethod
    def name_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('标签名称不能为空')
        return v.strip()


class TagUpdate(SQLModel):
    """更新标签"""
    name: Optional[str] = None
    color: Optional[str] = None
    description: Optional[str] = None


class TagRead(TagBase):
    """读取标签"""
    id: int
    user_id: Optional[int] = None
    is_common: bool = False
    usage_count: int = 0
    created_at: datetime

    class Config:
        from_attributes = True


class ProjectTagCreate(SQLModel):
    """创建项目标签关联"""
    project_id: int
    tag_id: int

