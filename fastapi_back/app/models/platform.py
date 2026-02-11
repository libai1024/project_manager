from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime

if TYPE_CHECKING:
    from app.models.project import Project
    from app.models.historical_project import HistoricalProject


class PlatformBase(SQLModel):
    name: str = Field(index=True)
    description: Optional[str] = None


class Platform(PlatformBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # 关系 - 使用字符串引用避免循环导入
    projects: List["Project"] = Relationship(back_populates="platform")
    historical_projects: List["HistoricalProject"] = Relationship(back_populates="platform")


class PlatformCreate(PlatformBase):
    pass


class PlatformRead(PlatformBase):
    id: int
    created_at: datetime


class PlatformUpdate(SQLModel):
    name: Optional[str] = None
    description: Optional[str] = None

