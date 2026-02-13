"""
用户 Repository 单元测试
"""
import pytest
from sqlmodel import Session

from app.repositories.user_repository import UserRepository
from app.models.user import User
from app.core.security import get_password_hash


class TestUserRepository:
    """用户 Repository 测试类"""

    def test_create_user(self, session: Session):
        """测试创建用户"""
        repo = UserRepository(session)
        password_hash = get_password_hash("testpass")

        from app.schemas.user import UserCreate
        user_data = UserCreate(username="newuser", password="testpass", role="user")

        user = repo.create(user_data, password_hash)

        assert user.id is not None
        assert user.username == "newuser"
        assert user.role == "user"
        assert user.password_hash == password_hash

    def test_get_by_id(self, session: Session, test_user: User):
        """测试通过 ID 获取用户"""
        repo = UserRepository(session)

        found_user = repo.get_by_id(test_user.id)

        assert found_user is not None
        assert found_user.id == test_user.id
        assert found_user.username == test_user.username

    def test_get_by_id_not_found(self, session: Session):
        """测试获取不存在的用户"""
        repo = UserRepository(session)

        found_user = repo.get_by_id(99999)

        assert found_user is None

    def test_get_by_username(self, session: Session, test_user: User):
        """测试通过用户名获取用户"""
        repo = UserRepository(session)

        found_user = repo.get_by_username(test_user.username)

        assert found_user is not None
        assert found_user.username == test_user.username

    def test_get_by_username_not_found(self, session: Session):
        """测试获取不存在的用户名"""
        repo = UserRepository(session)

        found_user = repo.get_by_username("nonexistent")

        assert found_user is None

    def test_exists_by_username(self, session: Session, test_user: User):
        """测试检查用户名是否存在"""
        repo = UserRepository(session)

        assert repo.exists_by_username(test_user.username) is True
        assert repo.exists_by_username("nonexistent") is False

    def test_list_all(self, session: Session, test_user: User, admin_user: User):
        """测试获取所有用户"""
        repo = UserRepository(session)

        users = repo.list_all()

        assert len(users) == 2
        usernames = [u.username for u in users]
        assert test_user.username in usernames
        assert admin_user.username in usernames

    def test_update(self, session: Session, test_user: User):
        """测试更新用户"""
        repo = UserRepository(session)

        updated_user = repo.update(test_user, {"role": "admin"})

        assert updated_user.role == "admin"
        assert updated_user.username == test_user.username

    def test_delete(self, session: Session, test_user: User):
        """测试删除用户"""
        repo = UserRepository(session)
        user_id = test_user.id

        repo.delete(test_user)

        assert repo.get_by_id(user_id) is None
