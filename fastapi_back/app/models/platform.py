"""
平台数据模型（ORM + DTO）

包含数据库表定义和DTO。
"""
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime

if TYPE_CHECKING:
    from app.models.project import Project
    from app.models.historical_project import HistoricalProject


class Platform(SQLModel, table=True):
    """平台表"""
    __tablename__ = "platform"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, max_length=100)
    description: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # 关系
    projects: List["Project"] = Relationship(back_populates="platform")
    historical_projects: List["HistoricalProject"] = Relationship(back_populates="platform")


# DTO类（保持向后兼容）
class PlatformBase(SQLModel):
    """平台基础模型"""
    name: str
    description: Optional[str] = None


class PlatformCreate(PlatformBase):
    """创建平台"""
    pass


class PlatformUpdate(SQLModel):
    """更新平台"""
    name: Optional[str] = None
    description: Optional[str] = None


class PlatformRead(PlatformBase):
    """读取平台"""
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
