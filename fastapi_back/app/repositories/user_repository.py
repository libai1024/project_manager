"""
用户数据访问层
"""
from typing import Optional, List
from sqlmodel import Session, select
from app.models.user import User, UserCreate


class UserRepository:
    """用户数据访问层"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def create(self, user_data: UserCreate, password_hash: str) -> User:
        """创建用户"""
        user = User(
            username=user_data.username,
            password_hash=password_hash,
            role=user_data.role
        )
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        return user
    
    def get_by_id(self, user_id: int) -> Optional[User]:
        """根据ID获取用户"""
        return self.session.get(User, user_id)
    
    def get_by_username(self, username: str) -> Optional[User]:
        """根据用户名获取用户"""
        return self.session.exec(
            select(User).where(User.username == username)
        ).first()
    
    def list_all(self) -> List[User]:
        """获取所有用户列表"""
        return list(self.session.exec(select(User)).all())
    
    def update(self, user: User, update_data: dict) -> User:
        """更新用户信息"""
        for field, value in update_data.items():
            setattr(user, field, value)
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        return user
    
    def delete(self, user: User) -> None:
        """删除用户"""
        self.session.delete(user)
        self.session.commit()
    
    def exists_by_username(self, username: str) -> bool:
        """检查用户名是否存在"""
        user = self.get_by_username(username)
        return user is not None

