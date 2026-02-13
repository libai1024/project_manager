"""
用户相关Schema定义

将DTO与ORM模型分离，符合企业级规范。
"""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


class UserBase(BaseModel):
    """用户基础信息"""
    username: str = Field(description="用户名")
    role: str = Field(default="user", description="用户角色：admin/user")


class UserCreate(BaseModel):
    """创建用户请求"""
    username: str = Field(min_length=3, max_length=50, description="用户名")
    password: str = Field(min_length=6, max_length=100, description="密码")
    role: str = Field(default="user", description="用户角色")


class UserUpdate(BaseModel):
    """更新用户请求"""
    username: Optional[str] = Field(default=None, min_length=3, max_length=50)
    password: Optional[str] = Field(default=None, min_length=6, max_length=100)
    role: Optional[str] = None
    is_active: Optional[bool] = None


class UserRead(UserBase):
    """用户信息响应"""
    id: int
    is_active: bool = Field(default=True, description="账户是否激活")
    is_locked: bool = Field(default=False, description="账户是否锁定")
    created_at: datetime
    last_login_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class Token(BaseModel):
    """访问令牌响应"""
    access_token: str = Field(description="访问令牌")
    refresh_token: Optional[str] = Field(default=None, description="刷新令牌")
    token_type: str = Field(default="bearer", description="令牌类型")
    expires_in: int = Field(description="过期时间（秒）")


class TokenData(BaseModel):
    """令牌数据"""
    user_id: Optional[int] = None
    username: Optional[str] = None
    role: Optional[str] = None


class LoginRequest(BaseModel):
    """登录请求"""
    username: str = Field(description="用户名")
    password: str = Field(description="密码")


class RefreshTokenRequest(BaseModel):
    """刷新令牌请求"""
    refresh_token: str = Field(description="刷新令牌")
