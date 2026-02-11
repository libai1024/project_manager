"""
刷新令牌模型（企业级认证系统）
"""
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING
from datetime import datetime, timedelta

if TYPE_CHECKING:
    from app.models.user import User


class RefreshTokenBase(SQLModel):
    """刷新令牌基础模型"""
    token: str = Field(unique=True, index=True, description="刷新令牌")
    user_id: int = Field(foreign_key="user.id", description="用户ID")
    expires_at: datetime = Field(description="过期时间")
    is_revoked: bool = Field(default=False, description="是否已撤销")
    device_info: Optional[str] = Field(default=None, description="设备信息")
    ip_address: Optional[str] = Field(default=None, description="IP地址")


class RefreshToken(RefreshTokenBase, table=True):
    """刷新令牌表"""
    __tablename__ = "refreshtoken"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, description="创建时间")
    revoked_at: Optional[datetime] = Field(default=None, description="撤销时间")
    
    # 关系
    user: "User" = Relationship(back_populates="refresh_tokens")


class RefreshTokenCreate(SQLModel):
    """创建刷新令牌"""
    token: str
    user_id: int
    expires_at: datetime
    device_info: Optional[str] = None
    ip_address: Optional[str] = None


class RefreshTokenRead(SQLModel):
    """读取刷新令牌"""
    id: int
    token: str
    user_id: int
    expires_at: datetime
    is_revoked: bool
    device_info: Optional[str] = None
    ip_address: Optional[str] = None
    created_at: datetime
    revoked_at: Optional[datetime] = None

