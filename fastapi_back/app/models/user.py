from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime, timedelta

if TYPE_CHECKING:
    from app.models.project import Project
    from app.models.historical_project import HistoricalProject
    from app.models.refresh_token import RefreshToken
    from app.models.login_log import LoginLog
    from app.models.tag import Tag


class UserBase(SQLModel):
    username: str = Field(unique=True, index=True)
    role: str = Field(default="user")  # admin, user


class User(UserBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    password_hash: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # 企业级认证字段
    is_active: bool = Field(default=True, description="账户是否激活")
    is_locked: bool = Field(default=False, description="账户是否锁定")
    locked_until: Optional[datetime] = Field(default=None, description="锁定到期时间")
    failed_login_attempts: int = Field(default=0, description="失败登录次数")
    last_login_at: Optional[datetime] = Field(default=None, description="最后登录时间")
    password_changed_at: Optional[datetime] = Field(default=None, description="密码最后修改时间")
    must_change_password: bool = Field(default=False, description="是否必须修改密码")
    
    # 关系 - 使用字符串引用避免循环导入
    projects: List["Project"] = Relationship(back_populates="user")
    historical_projects: List["HistoricalProject"] = Relationship(back_populates="user")
    refresh_tokens: List["RefreshToken"] = Relationship(back_populates="user", cascade_delete=True)
    login_logs: List["LoginLog"] = Relationship(back_populates="user", cascade_delete=True)
    tags: List["Tag"] = Relationship(back_populates="user")


class UserCreate(SQLModel):
    username: str
    password: str
    role: str = "user"


class UserRead(UserBase):
    id: int
    created_at: datetime


class UserUpdate(SQLModel):
    username: Optional[str] = None
    password: Optional[str] = None
    role: Optional[str] = None


class Token(SQLModel):
    """访问令牌响应"""
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"
    expires_in: int  # 过期时间（秒）


class TokenData(SQLModel):
    username: Optional[str] = None

