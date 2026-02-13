"""
用户 Service 单元测试
"""
import pytest
from sqlmodel import Session

from app.services.user_service import UserService
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.core.exceptions import NotFoundException, BusinessException


class TestUserService:
    """用户 Service 测试类"""

    def test_create_user(self, session: Session):
        """测试创建用户"""
        service = UserService(session)
        user_data = UserCreate(username="newuser", password="testpass", role="user")

        user = service.create_user(user_data)

        assert user.id is not None
        assert user.username == "newuser"
        assert user.role == "user"

    def test_create_duplicate_user(self, session: Session, test_user: User):
        """测试创建重复用户名"""
        service = UserService(session)
        user_data = UserCreate(username=test_user.username, password="testpass", role="user")

        with pytest.raises(BusinessException) as exc_info:
            service.create_user(user_data)

        assert exc_info.value.code == 400
        assert "已存在" in exc_info.value.msg

    def test_get_user_by_id(self, session: Session, test_user: User):
        """测试通过 ID 获取用户"""
        service = UserService(session)

        found_user = service.get_user_by_id(test_user.id)

        assert found_user.id == test_user.id
        assert found_user.username == test_user.username

    def test_get_user_by_id_not_found(self, session: Session):
        """测试获取不存在的用户"""
        service = UserService(session)

        with pytest.raises(NotFoundException):
            service.get_user_by_id(99999)

    def test_get_user_by_username(self, session: Session, test_user: User):
        """测试通过用户名获取用户"""
        service = UserService(session)

        found_user = service.get_user_by_username(test_user.username)

        assert found_user is not None
        assert found_user.username == test_user.username

    def test_list_users(self, session: Session, test_user: User, admin_user: User):
        """测试获取所有用户"""
        service = UserService(session)

        users = service.list_users()

        assert len(users) == 2
        usernames = [u.username for u in users]
        assert test_user.username in usernames
        assert admin_user.username in usernames

    def test_update_user(self, session: Session, test_user: User, admin_user: User):
        """测试更新用户"""
        service = UserService(session)
        update_data = UserUpdate(role="admin")

        updated_user = service.update_user(test_user.id, update_data, admin_user)

        assert updated_user.role == "admin"

    def test_update_user_password(self, session: Session, test_user: User, admin_user: User):
        """测试更新用户密码"""
        service = UserService(session)
        update_data = UserUpdate(password="newpassword")

        updated_user = service.update_user(test_user.id, update_data, admin_user)

        assert updated_user.password_hash != test_user.password_hash

    def test_update_admin_role_forbidden(self, session: Session, admin_user: User):
        """测试禁止修改管理员角色"""
        service = UserService(session)
        update_data = UserUpdate(role="user")

        with pytest.raises(BusinessException) as exc_info:
            service.update_user(admin_user.id, update_data, admin_user)

        assert "管理员" in exc_info.value.msg

    def test_update_self_role_forbidden(self, session: Session, test_user: User):
        """测试禁止修改自己的角色"""
        service = UserService(session)
        update_data = UserUpdate(role="admin")

        with pytest.raises(BusinessException) as exc_info:
            service.update_user(test_user.id, update_data, test_user)

        assert "不能修改自己的角色" in exc_info.value.msg

    def test_delete_user(self, session: Session, test_user: User, admin_user: User):
        """测试删除用户"""
        service = UserService(session)

        service.delete_user(test_user.id, admin_user)

        with pytest.raises(NotFoundException):
            service.get_user_by_id(test_user.id)

    def test_delete_admin_forbidden(self, session: Session, admin_user: User):
        """测试禁止删除管理员"""
        service = UserService(session)

        with pytest.raises(BusinessException) as exc_info:
            service.delete_user(admin_user.id, admin_user)

        assert "不能删除管理员" in exc_info.value.msg

    def test_delete_self_forbidden(self, session: Session, test_user: User):
        """测试禁止删除自己"""
        service = UserService(session)

        with pytest.raises(BusinessException) as exc_info:
            service.delete_user(test_user.id, test_user)

        assert "不能删除自己" in exc_info.value.msg
