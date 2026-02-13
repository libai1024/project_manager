"""
平台服务层

重构后使用 schemas 中的 DTO 和自定义异常。
"""
from typing import Optional, List
from sqlmodel import Session

from app.repositories.platform_repository import PlatformRepository
from app.models.platform import Platform
from app.schemas.platform import PlatformCreate, PlatformUpdate
from app.core.exceptions import NotFoundException


class PlatformService:
    """平台服务层"""

    def __init__(self, session: Session):
        self.session = session
        self.platform_repo = PlatformRepository(session)

    def create_platform(self, platform_data: PlatformCreate) -> Platform:
        """创建平台"""
        return self.platform_repo.create(platform_data)

    def _get_platform_or_raise(self, platform_id: int) -> Platform:
        """获取平台，不存在则抛出异常"""
        platform = self.platform_repo.get_by_id(platform_id)
        if not platform:
            raise NotFoundException("平台", id=platform_id)
        return platform

    def get_platform_by_id(self, platform_id: int) -> Platform:
        """根据ID获取平台"""
        return self._get_platform_or_raise(platform_id)

    def list_platforms(self) -> List[Platform]:
        """获取所有平台列表"""
        return self.platform_repo.list_all()

    def update_platform(self, platform_id: int, platform_data: PlatformUpdate) -> Platform:
        """更新平台信息"""
        platform = self._get_platform_or_raise(platform_id)
        update_data = platform_data.model_dump(exclude_unset=True)
        return self.platform_repo.update(platform, update_data)

    def delete_platform(self, platform_id: int) -> None:
        """删除平台"""
        platform = self._get_platform_or_raise(platform_id)
        self.platform_repo.delete(platform)

