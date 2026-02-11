"""
项目步骤模板数据模型
"""
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime

if TYPE_CHECKING:
    from app.models.user import User


class StepTemplateBase(SQLModel):
    name: str = Field(index=True, description="模板名称")
    description: Optional[str] = Field(default=None, description="模板描述")
    is_default: bool = Field(default=False, description="是否为默认模板")
    user_id: Optional[int] = Field(default=None, foreign_key="user.id", description="创建用户ID")


class StepTemplate(StepTemplateBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow, sa_column_kwargs={"onupdate": datetime.utcnow})
    
    # 关系
    user: Optional["User"] = Relationship()
    steps: List["StepTemplateItem"] = Relationship(
        back_populates="template",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )


class StepTemplateItemBase(SQLModel):
    template_id: int = Field(foreign_key="steptemplate.id")
    name: str = Field(description="步骤名称")
    order_index: int = Field(default=0, description="排序索引")


class StepTemplateItem(StepTemplateItemBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # 关系
    template: StepTemplate = Relationship(back_populates="steps")


class StepTemplateCreate(SQLModel):
    name: str
    description: Optional[str] = None
    steps: List[str] = Field(description="步骤名称列表")


class StepTemplateUpdate(SQLModel):
    name: Optional[str] = None
    description: Optional[str] = None
    steps: Optional[List[str]] = None


class StepTemplateRead(StepTemplateBase):
    id: int
    created_at: datetime
    updated_at: datetime
    steps: List[str] = Field(description="步骤名称列表")


class StepTemplateItemRead(SQLModel):
    id: int
    template_id: int
    name: str
    order_index: int

