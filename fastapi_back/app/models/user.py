"""
用户数据模型（ORM + DTO）

包含数据库表定义和DTO。
"""
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime
from pydantic import BaseModel

if TYPE_CHECKING:
    from app.models.project import Project
    from app.models.historical_project import HistoricalProject
    from app.models.refresh_token import RefreshToken
    from app.models.login_log import LoginLog
    from app.models.tag import Tag


class User(SQLModel, table=True):
    """用户表"""
    __tablename__ = "user"

    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True, max_length=50)
    password_hash: str
    role: str = Field(default="user")  # admin, user
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # 企业级认证字段
    is_active: bool = Field(default=True, description="账户是否激活")
    is_locked: bool = Field(default=False, description="账户是否锁定")
    locked_until: Optional[datetime] = Field(default=None, description="锁定到期时间")
    failed_login_attempts: int = Field(default=0, description="失败登录次数")
    last_login_at: Optional[datetime] = Field(default=None, description="最后登录时间")
    password_changed_at: Optional[datetime] = Field(default=None, description="密码最后修改时间")
    must_change_password: bool = Field(default=False, description="是否必须修改密码")

    # 关系
    projects: List["Project"] = Relationship(back_populates="user")
    historical_projects: List["HistoricalProject"] = Relationship(back_populates="user")
    refresh_tokens: List["RefreshToken"] = Relationship(back_populates="user", cascade_delete=True)
    login_logs: List["LoginLog"] = Relationship(back_populates="user", cascade_delete=True)
    tags: List["Tag"] = Relationship(back_populates="user")


# DTO类（保持向后兼容）
class UserBase(SQLModel):
    """用户基础信息"""
    username: str
    role: str = "user"


class UserCreate(SQLModel):
    """创建用户请求"""
    username: str
    password: str
    role: str = "user"


class UserUpdate(SQLModel):
    """更新用户请求"""
    username: Optional[str] = None
    password: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None


class UserRead(UserBase):
    """用户信息响应"""
    id: int
    is_active: bool = True
    is_locked: bool = False
    created_at: datetime
    last_login_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class Token(BaseModel):
    """访问令牌响应"""
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"
    expires_in: int

