"""
项目配件清单数据模型
"""
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING, List
from datetime import datetime

if TYPE_CHECKING:
    from app.models.project import Project
    from app.models.historical_project import HistoricalProject


class ProjectPartBase(SQLModel):
    """项目配件基础字段"""
    project_id: Optional[int] = Field(default=None, foreign_key="project.id", description="所属项目ID")
    historical_project_id: Optional[int] = Field(default=None, foreign_key="historicalproject.id", description="所属历史项目ID")
    module_name: str = Field(description="功能模块名称")
    core_component: str = Field(description="核心元器件")
    remark: Optional[str] = Field(default=None, description="主要功能描述 / 备注")
    unit_price: float = Field(default=0.0, description="单价")
    quantity: int = Field(default=1, description="数量")
    purchase_link: Optional[str] = Field(default=None, description="购买链接")
    image_url: Optional[str] = Field(default=None, description="图片链接，用于展示，如果为空使用默认占位图")


class ProjectPart(ProjectPartBase, table=True):
    """项目配件表"""
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow, sa_column_kwargs={"onupdate": datetime.utcnow})

    # 关系
    project: Optional["Project"] = Relationship(back_populates="parts")
    historical_project: Optional["HistoricalProject"] = Relationship(back_populates="parts")


class ProjectPartCreate(SQLModel):
    """创建配件清单条目（project_id 从路径参数获取，不需要在请求体中提供）"""
    module_name: str = Field(description="功能模块名称")
    core_component: str = Field(description="核心元器件")
    remark: Optional[str] = Field(default=None, description="主要功能描述 / 备注")
    unit_price: float = Field(default=0.0, description="单价")
    quantity: int = Field(default=1, description="数量")
    purchase_link: Optional[str] = Field(default=None, description="购买链接")
    image_url: Optional[str] = Field(default=None, description="图片链接，用于展示，如果为空使用默认占位图")


class ProjectPartUpdate(SQLModel):
    """更新配件清单条目"""
    module_name: Optional[str] = None
    core_component: Optional[str] = None
    remark: Optional[str] = None
    unit_price: Optional[float] = None
    quantity: Optional[int] = None
    purchase_link: Optional[str] = None
    image_url: Optional[str] = None


class ProjectPartRead(ProjectPartBase):
    """读取配件清单条目"""
    id: int
    created_at: datetime
    updated_at: datetime


