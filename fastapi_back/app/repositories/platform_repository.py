"""
平台数据访问层
"""
from typing import Optional, List
from sqlmodel import Session, select
from app.models.platform import Platform, PlatformCreate


class PlatformRepository:
    """平台数据访问层"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def create(self, platform_data: PlatformCreate) -> Platform:
        """创建平台"""
        platform = Platform(**platform_data.model_dump())
        self.session.add(platform)
        self.session.commit()
        self.session.refresh(platform)
        return platform
    
    def get_by_id(self, platform_id: int) -> Optional[Platform]:
        """根据ID获取平台"""
        return self.session.get(Platform, platform_id)
    
    def list_all(self) -> List[Platform]:
        """获取所有平台列表"""
        return list(self.session.exec(select(Platform)).all())
    
    def update(self, platform: Platform, update_data: dict) -> Platform:
        """更新平台信息"""
        for field, value in update_data.items():
            setattr(platform, field, value)
        self.session.add(platform)
        self.session.commit()
        self.session.refresh(platform)
        return platform
    
    def delete(self, platform: Platform) -> None:
        """删除平台"""
        self.session.delete(platform)
        self.session.commit()

