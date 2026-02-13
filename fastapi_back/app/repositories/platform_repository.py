"""
平台数据访问层

重构后继承 BaseRepository，使用 schemas 中的 DTO。
"""
from typing import Optional, List
from sqlmodel import Session, select

from app.repositories.base import BaseRepository
from app.models.platform import Platform
from app.schemas.platform import PlatformCreate


class PlatformRepository(BaseRepository[Platform]):
    """平台数据访问层"""

    def __init__(self, session: Session):
        super().__init__(session, Platform)

    def create(self, platform_data: PlatformCreate) -> Platform:
        """创建平台"""
        platform = Platform(**platform_data.model_dump())
        return super().create(platform)

    def get_by_name(self, name: str) -> Optional[Platform]:
        """根据名称获取平台"""
        return self.find_one(name=name)

