"""
Token黑名单数据访问层
"""
from typing import Optional
from sqlmodel import Session, select
from datetime import datetime
from app.models.token_blacklist import TokenBlacklist, TokenBlacklistCreate


class TokenBlacklistRepository:
    """Token黑名单数据访问层"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def create(self, blacklist_data: TokenBlacklistCreate) -> TokenBlacklist:
        """将token加入黑名单"""
        blacklist_entry = TokenBlacklist(**blacklist_data.model_dump())
        self.session.add(blacklist_entry)
        self.session.commit()
        self.session.refresh(blacklist_entry)
        return blacklist_entry
    
    def is_blacklisted(self, token: str) -> bool:
        """检查token是否在黑名单中"""
        blacklist_entry = self.session.exec(
            select(TokenBlacklist).where(TokenBlacklist.token == token)
        ).first()
        
        if not blacklist_entry:
            return False
        
        # 如果token已过期，从黑名单中移除
        if blacklist_entry.expires_at < datetime.utcnow():
            self.session.delete(blacklist_entry)
            self.session.commit()
            return False
        
        return True
    
    def cleanup_expired_tokens(self) -> int:
        """清理过期的黑名单token"""
        expired_tokens = self.session.exec(
            select(TokenBlacklist).where(TokenBlacklist.expires_at < datetime.utcnow())
        ).all()
        
        count = 0
        for token in expired_tokens:
            self.session.delete(token)
            count += 1
        
        self.session.commit()
        return count

