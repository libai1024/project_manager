"""
用户服务层

重构后使用 schemas 中的 DTO 和自定义异常。
"""
from typing import Optional, List
from sqlmodel import Session

from app.repositories.user_repository import UserRepository
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash
from app.core.exceptions import NotFoundException, BusinessException


class UserService:
    """用户服务层"""

    def __init__(self, session: Session):
        self.session = session
        self.user_repo = UserRepository(session)

    def create_user(self, user_data: UserCreate) -> User:
        """创建用户"""
        if self.user_repo.exists_by_username(user_data.username):
            raise BusinessException(code=400, msg="用户名已存在")

        password_hash = get_password_hash(user_data.password)
        return self.user_repo.create(user_data, password_hash)

    def _get_user_or_raise(self, user_id: int) -> User:
        """获取用户，不存在则抛出异常"""
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundException("用户", id=user_id)
        return user

    def get_user_by_id(self, user_id: int) -> User:
        """根据ID获取用户"""
        return self._get_user_or_raise(user_id)

    def get_user_by_username(self, username: str) -> Optional[User]:
        """根据用户名获取用户"""
        return self.user_repo.get_by_username(username)

    def list_users(self) -> List[User]:
        """获取所有用户列表"""
        return self.user_repo.list_all()

    def update_user(self, user_id: int, user_data: UserUpdate, current_user: User) -> User:
        """更新用户信息"""
        user = self._get_user_or_raise(user_id)

        if user.username == "admin" and user_data.role and user_data.role != "admin":
            raise BusinessException(code=400, msg="不能修改管理员用户角色")

        if user.id == current_user.id and user_data.role and user_data.role != user.role:
            raise BusinessException(code=400, msg="不能修改自己的角色")

        update_data = user_data.model_dump(exclude_unset=True)

        if "password" in update_data:
            update_data["password_hash"] = get_password_hash(update_data.pop("password"))

        return self.user_repo.update(user, update_data)

    def delete_user(self, user_id: int, current_user: User) -> None:
        """删除用户"""
        user = self._get_user_or_raise(user_id)

        if user.username == "admin":
            raise BusinessException(code=400, msg="不能删除管理员用户")

        if user.id == current_user.id:
            raise BusinessException(code=400, msg="不能删除自己")

        self.user_repo.delete(user)

