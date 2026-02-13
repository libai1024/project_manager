"""
平台 Repository 单元测试
"""
import pytest
from sqlmodel import Session

from app.repositories.platform_repository import PlatformRepository
from app.models.platform import Platform


class TestPlatformRepository:
    """平台 Repository 测试类"""

    def test_create_platform(self, session: Session):
        """测试创建平台"""
        repo = PlatformRepository(session)

        from app.schemas.platform import PlatformCreate
        platform_data = PlatformCreate(name="新平台")

        platform = repo.create(platform_data)

        assert platform.id is not None
        assert platform.name == "新平台"

    def test_get_by_id(self, session: Session, test_platform: Platform):
        """测试通过 ID 获取平台"""
        repo = PlatformRepository(session)

        found_platform = repo.get_by_id(test_platform.id)

        assert found_platform is not None
        assert found_platform.id == test_platform.id
        assert found_platform.name == test_platform.name

    def test_get_by_id_not_found(self, session: Session):
        """测试获取不存在的平台"""
        repo = PlatformRepository(session)

        found_platform = repo.get_by_id(99999)

        assert found_platform is None

    def test_get_by_name(self, session: Session, test_platform: Platform):
        """测试通过名称获取平台"""
        repo = PlatformRepository(session)

        found_platform = repo.get_by_name(test_platform.name)

        assert found_platform is not None
        assert found_platform.name == test_platform.name

    def test_get_by_name_not_found(self, session: Session):
        """测试获取不存在的平台名称"""
        repo = PlatformRepository(session)

        found_platform = repo.get_by_name("不存在的平台")

        assert found_platform is None

    def test_list_all(self, session: Session, test_platform: Platform):
        """测试获取所有平台"""
        repo = PlatformRepository(session)

        # 创建另一个平台
        from app.schemas.platform import PlatformCreate
        repo.create(PlatformCreate(name="另一个平台"))

        platforms = repo.list_all()

        assert len(platforms) == 2
        names = [p.name for p in platforms]
        assert test_platform.name in names
        assert "另一个平台" in names

    def test_update(self, session: Session, test_platform: Platform):
        """测试更新平台"""
        repo = PlatformRepository(session)

        updated_platform = repo.update(test_platform, {"name": "更新后的平台"})

        assert updated_platform.name == "更新后的平台"

    def test_delete(self, session: Session, test_platform: Platform):
        """测试删除平台"""
        repo = PlatformRepository(session)
        platform_id = test_platform.id

        repo.delete(test_platform)

        assert repo.get_by_id(platform_id) is None

    def test_exists_by_name(self, session: Session, test_platform: Platform):
        """测试检查平台名称是否存在"""
        repo = PlatformRepository(session)

        assert repo.exists_by_name(test_platform.name) is True
        assert repo.exists_by_name("不存在的平台") is False
