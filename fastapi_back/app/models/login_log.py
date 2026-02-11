"""
登录日志模型（企业级认证系统）
用于审计和安全性监控
"""
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING
from datetime import datetime
from enum import Enum

if TYPE_CHECKING:
    from app.models.user import User


class LoginStatus(str, Enum):
    """登录状态"""
    SUCCESS = "success"
    FAILED = "failed"
    BLOCKED = "blocked"
    LOCKED = "locked"


class LoginLogBase(SQLModel):
    """登录日志基础模型"""
    user_id: Optional[int] = Field(default=None, foreign_key="user.id", description="用户ID")
    username: str = Field(index=True, description="用户名")
    status: LoginStatus = Field(description="登录状态")
    ip_address: Optional[str] = Field(default=None, description="IP地址")
    user_agent: Optional[str] = Field(default=None, description="用户代理")
    device_info: Optional[str] = Field(default=None, description="设备信息")
    failure_reason: Optional[str] = Field(default=None, description="失败原因")


class LoginLog(LoginLogBase, table=True):
    """登录日志表"""
    __tablename__ = "loginlog"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True, description="创建时间")
    
    # 关系
    user: Optional["User"] = Relationship(back_populates="login_logs")


class LoginLogCreate(SQLModel):
    """创建登录日志"""
    user_id: Optional[int] = None
    username: str
    status: LoginStatus
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    device_info: Optional[str] = None
    failure_reason: Optional[str] = None


class LoginLogRead(SQLModel):
    """读取登录日志"""
    id: int
    user_id: Optional[int] = None
    username: str
    status: LoginStatus
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    device_info: Optional[str] = None
    failure_reason: Optional[str] = None
    created_at: datetime

