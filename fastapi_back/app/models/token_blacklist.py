"""
Token黑名单模型（企业级认证系统）
用于撤销已签发的token
"""
from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime


class TokenBlacklistBase(SQLModel):
    """Token黑名单基础模型"""
    token: str = Field(unique=True, index=True, description="被撤销的token")
    expires_at: datetime = Field(description="token过期时间")


class TokenBlacklist(TokenBlacklistBase, table=True):
    """Token黑名单表"""
    __tablename__ = "tokenblacklist"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, description="加入黑名单时间")
    reason: Optional[str] = Field(default=None, description="撤销原因")


class TokenBlacklistCreate(SQLModel):
    """创建黑名单记录"""
    token: str
    expires_at: datetime
    reason: Optional[str] = None

