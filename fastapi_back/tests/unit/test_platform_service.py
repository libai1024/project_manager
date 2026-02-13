"""
平台 Service 单元测试
"""
import pytest
from sqlmodel import Session

from app.services.platform_service import PlatformService
from app.models.platform import Platform
from app.schemas.platform import PlatformCreate, PlatformUpdate
from app.core.exceptions import NotFoundException


class TestPlatformService:
    """平台 Service 测试类"""

    def test_create_platform(self, session: Session):
        """测试创建平台"""
        service = PlatformService(session)
        platform_data = PlatformCreate(name="新平台")

        platform = service.create_platform(platform_data)

        assert platform.id is not None
        assert platform.name == "新平台"

    def test_get_platform_by_id(self, session: Session, test_platform: Platform):
        """测试通过 ID 获取平台"""
        service = PlatformService(session)

        found_platform = service.get_platform_by_id(test_platform.id)

        assert found_platform.id == test_platform.id
        assert found_platform.name == test_platform.name

    def test_get_platform_by_id_not_found(self, session: Session):
        """测试获取不存在的平台"""
        service = PlatformService(session)

        with pytest.raises(NotFoundException):
            service.get_platform_by_id(99999)

    def test_list_platforms(self, session: Session, test_platform: Platform):
        """测试获取所有平台"""
        service = PlatformService(session)

        # 创建另一个平台
        service.create_platform(PlatformCreate(name="另一个平台"))

        platforms = service.list_platforms()

        assert len(platforms) == 2
        names = [p.name for p in platforms]
        assert test_platform.name in names
        assert "另一个平台" in names

    def test_update_platform(self, session: Session, test_platform: Platform):
        """测试更新平台"""
        service = PlatformService(session)
        update_data = PlatformUpdate(name="更新后的平台")

        updated_platform = service.update_platform(test_platform.id, update_data)

        assert updated_platform.name == "更新后的平台"

    def test_update_platform_not_found(self, session: Session):
        """测试更新不存在的平台"""
        service = PlatformService(session)
        update_data = PlatformUpdate(name="新名称")

        with pytest.raises(NotFoundException):
            service.update_platform(99999, update_data)

    def test_delete_platform(self, session: Session, test_platform: Platform):
        """测试删除平台"""
        service = PlatformService(session)

        service.delete_platform(test_platform.id)

        with pytest.raises(NotFoundException):
            service.get_platform_by_id(test_platform.id)

    def test_delete_platform_not_found(self, session: Session):
        """测试删除不存在的平台"""
        service = PlatformService(session)

        with pytest.raises(NotFoundException):
            service.delete_platform(99999)
