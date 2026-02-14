"""
用户数据访问层

重构后继承 BaseRepository，使用 schemas 中的 DTO。
"""
from typing import Optional, List
from sqlmodel import Session, select

from app.repositories.base import BaseRepository
from app.models.user import User
from app.schemas.user import UserCreate


class UserRepository(BaseRepository[User]):
    """用户数据访问层"""

    def __init__(self, session: Session):
        super().__init__(session, User)

    def create(self, user_data: UserCreate, password_hash: str) -> User:
        """创建用户"""
        user = User(
            username=user_data.username,
            password_hash=password_hash,
            role=user_data.role
        )
        return super().create(user)

    def get_by_username(self, username: str) -> Optional[User]:
        """根据用户名获取用户"""
        return self.find_one(username=username)

    def exists_by_username(self, username: str) -> bool:
        """检查用户名是否存在"""
        return self.get_by_username(username) is not None

