"""
登录日志数据访问层
"""
from typing import Optional, List
from sqlmodel import Session, select, func
from datetime import datetime, timedelta
from app.models.login_log import LoginLog, LoginLogCreate, LoginStatus


class LoginLogRepository:
    """登录日志数据访问层"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def create(self, log_data: LoginLogCreate) -> LoginLog:
        """创建登录日志"""
        log = LoginLog(**log_data.model_dump())
        self.session.add(log)
        self.session.commit()
        self.session.refresh(log)
        return log
    
    def get_recent_failed_attempts(
        self, 
        username: str, 
        minutes: int = 30
    ) -> int:
        """获取最近N分钟内的失败登录次数"""
        since = datetime.utcnow() - timedelta(minutes=minutes)
        count = self.session.exec(
            select(func.count(LoginLog.id)).where(
                LoginLog.username == username,
                LoginLog.status == LoginStatus.FAILED,
                LoginLog.created_at >= since
            )
        ).one()
        return count
    
    def list_by_user(
        self, 
        user_id: Optional[int] = None,
        username: Optional[str] = None,
        limit: int = 100
    ) -> List[LoginLog]:
        """获取用户的登录日志"""
        query = select(LoginLog)
        
        if user_id:
            query = query.where(LoginLog.user_id == user_id)
        elif username:
            query = query.where(LoginLog.username == username)
        
        query = query.order_by(LoginLog.created_at.desc()).limit(limit)
        return list(self.session.exec(query).all())
    
    def get_last_successful_login(self, username: str) -> Optional[LoginLog]:
        """获取最后一次成功登录"""
        return self.session.exec(
            select(LoginLog).where(
                LoginLog.username == username,
                LoginLog.status == LoginStatus.SUCCESS
            ).order_by(LoginLog.created_at.desc())
        ).first()

