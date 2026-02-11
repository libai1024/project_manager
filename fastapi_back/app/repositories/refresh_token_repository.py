"""
刷新令牌数据访问层
"""
from typing import Optional, List
from sqlmodel import Session, select
from datetime import datetime
from app.models.refresh_token import RefreshToken, RefreshTokenCreate


class RefreshTokenRepository:
    """刷新令牌数据访问层"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def create(self, token_data: RefreshTokenCreate) -> RefreshToken:
        """创建刷新令牌"""
        token = RefreshToken(**token_data.model_dump())
        self.session.add(token)
        self.session.commit()
        self.session.refresh(token)
        return token
    
    def get_by_token(self, token: str) -> Optional[RefreshToken]:
        """根据token获取刷新令牌"""
        return self.session.exec(
            select(RefreshToken).where(RefreshToken.token == token)
        ).first()
    
    def get_valid_token(self, token: str) -> Optional[RefreshToken]:
        """获取有效的刷新令牌（未撤销且未过期）"""
        refresh_token = self.get_by_token(token)
        if not refresh_token:
            return None
        
        if refresh_token.is_revoked:
            return None
        
        if refresh_token.expires_at < datetime.utcnow():
            return None
        
        return refresh_token
    
    def revoke_token(self, token: str) -> bool:
        """撤销刷新令牌"""
        refresh_token = self.get_by_token(token)
        if not refresh_token:
            return False
        
        refresh_token.is_revoked = True
        refresh_token.revoked_at = datetime.utcnow()
        self.session.add(refresh_token)
        self.session.commit()
        return True
    
    def revoke_all_user_tokens(self, user_id: int) -> int:
        """撤销用户的所有刷新令牌"""
        tokens = self.session.exec(
            select(RefreshToken).where(
                RefreshToken.user_id == user_id,
                RefreshToken.is_revoked == False
            )
        ).all()
        
        count = 0
        for token in tokens:
            token.is_revoked = True
            token.revoked_at = datetime.utcnow()
            self.session.add(token)
            count += 1
        
        self.session.commit()
        return count
    
    def list_by_user(self, user_id: int) -> List[RefreshToken]:
        """获取用户的所有刷新令牌"""
        return list(self.session.exec(
            select(RefreshToken).where(RefreshToken.user_id == user_id)
            .order_by(RefreshToken.created_at.desc())
        ).all())
    
    def cleanup_expired_tokens(self) -> int:
        """清理过期的刷新令牌"""
        expired_tokens = self.session.exec(
            select(RefreshToken).where(
                RefreshToken.expires_at < datetime.utcnow(),
                RefreshToken.is_revoked == False
            )
        ).all()
        
        count = 0
        for token in expired_tokens:
            self.session.delete(token)
            count += 1
        
        self.session.commit()
        return count

