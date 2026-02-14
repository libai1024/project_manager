"""
项目相关Schema定义

将DTO与ORM模型分离，符合企业级规范。
"""
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, field_validator

from app.schemas.platform import PlatformRead
from app.schemas.tag import TagRead


class ProjectBase(BaseModel):
    """项目基础信息"""
    title: str = Field(min_length=1, max_length=200, description="项目标题")
    student_name: Optional[str] = Field(default=None, max_length=100, description="学生姓名")
    platform_id: int = Field(description="平台ID")
    price: float = Field(default=0.0, ge=0, description="项目价格")
    actual_income: float = Field(default=0.0, ge=0, description="实际收入")
    github_url: Optional[str] = Field(default=None, max_length=500, description="GitHub地址")
    requirements: Optional[str] = Field(default=None, description="需求描述")

    @field_validator('title')
    @classmethod
    def title_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('项目标题不能为空')
        return v.strip()


class ProjectCreate(ProjectBase):
    """创建项目请求"""
    user_id: Optional[int] = Field(default=None, description="负责人ID（管理员可指定）")
    requirement_files: Optional[List[int]] = Field(
        default=None,
        description="需求文件附件ID列表"
    )
    template_id: Optional[int] = Field(
        default=None,
        description="步骤模板ID"
    )
    tag_ids: Optional[List[int]] = Field(
        default_factory=list,
        description="标签ID列表"
    )


class ProjectUpdate(BaseModel):
    """更新项目请求"""
    title: Optional[str] = Field(default=None, max_length=200)
    student_name: Optional[str] = Field(default=None, max_length=100)
    platform_id: Optional[int] = None
    price: Optional[float] = Field(default=None, ge=0)
    actual_income: Optional[float] = Field(default=None, ge=0)
    status: Optional[str] = None
    github_url: Optional[str] = Field(default=None, max_length=500)
    requirements: Optional[str] = None
    is_paid: Optional[bool] = None
    tag_ids: Optional[List[int]] = None


class ProjectRead(ProjectBase):
    """项目信息响应"""
    id: int
    user_id: int = Field(description="负责人ID")
    status: str = Field(description="项目状态")
    is_paid: bool = Field(default=False, description="是否已结账")
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ProjectReadWithRelations(ProjectRead):
    """包含关联数据的项目响应"""
    platform: Optional[PlatformRead] = None
    steps: List["ProjectStepRead"] = []
    tags: List[TagRead] = []


class ProjectList(BaseModel):
    """项目列表响应"""
    items: List[ProjectReadWithRelations]
    total: int


# ========== 项目步骤 ==========

class ProjectStepBase(BaseModel):
    """项目步骤基础信息"""
    name: str = Field(max_length=100, description="步骤名称")
    order_index: int = Field(default=0, description="排序索引")
    status: str = Field(default="待开始", description="步骤状态")
    is_todo: bool = Field(default=False, description="是否在待办中")
    deadline: Optional[datetime] = Field(default=None, description="截止日期")


class ProjectStepCreate(BaseModel):
    """创建项目步骤请求"""
    name: str = Field(max_length=100, description="步骤名称")
    order_index: Optional[int] = Field(default=0, description="排序索引")
    deadline: Optional[datetime] = Field(default=None, description="截止日期")


class ProjectStepUpdate(BaseModel):
    """更新项目步骤请求"""
    name: Optional[str] = Field(default=None, max_length=100)
    order_index: Optional[int] = None
    status: Optional[str] = None
    is_todo: Optional[bool] = None
    deadline: Optional[datetime] = None


class ProjectStepRead(ProjectStepBase):
    """项目步骤响应"""
    id: int
    project_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class StepReorderItem(BaseModel):
    """步骤重排序项"""
    step_id: int
    order_index: int


class StepReorderRequest(BaseModel):
    """步骤重排序请求"""
    steps: List[StepReorderItem]


# 更新前向引用
ProjectReadWithRelations.model_rebuild()
