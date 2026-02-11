"""
标签数据访问层
"""
from typing import List, Optional
from sqlmodel import Session, select, or_
from app.models.tag import Tag, TagCreate, TagUpdate, ProjectTag, ProjectTagCreate, HistoricalProjectTag, HistoricalProjectTagCreate


class TagRepository:
    """标签数据访问层"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def create(self, tag_data: TagCreate, user_id: Optional[int] = None) -> Tag:
        """创建标签"""
        tag_dict = tag_data.model_dump()
        tag_dict['user_id'] = user_id
        tag = Tag(**tag_dict)
        self.session.add(tag)
        self.session.commit()
        self.session.refresh(tag)
        return tag
    
    def get_by_id(self, tag_id: int) -> Optional[Tag]:
        """根据ID获取标签"""
        return self.session.get(Tag, tag_id)
    
    def get_by_name(self, name: str) -> Optional[Tag]:
        """根据名称获取标签"""
        return self.session.exec(
            select(Tag).where(Tag.name == name)
        ).first()
    
    def list_all(self, user_id: Optional[int] = None, include_common: bool = True) -> List[Tag]:
        """获取所有标签（全局共享，不区分用户）"""
        query = select(Tag)
        
        # 标签全局共享，返回所有标签
        # 如果指定了include_common，可以按常用标签排序
        if include_common:
            # 按使用次数和名称排序，常用标签优先
            query = query.order_by(Tag.is_common.desc(), Tag.usage_count.desc(), Tag.name.asc())
        else:
            query = query.order_by(Tag.usage_count.desc(), Tag.name.asc())
        
        return list(self.session.exec(query).all())
    
    def list_common(self) -> List[Tag]:
        """获取常用标签"""
        return list(self.session.exec(
            select(Tag).where(Tag.is_common == True).order_by(Tag.usage_count.desc(), Tag.name.asc())
        ).all())
    
    def update(self, tag_id: int, tag_data: TagUpdate) -> Optional[Tag]:
        """更新标签"""
        tag = self.get_by_id(tag_id)
        if not tag:
            return None
        
        update_data = tag_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(tag, key, value)
        
        self.session.add(tag)
        self.session.commit()
        self.session.refresh(tag)
        return tag
    
    def delete(self, tag_id: int) -> bool:
        """删除标签"""
        tag = self.get_by_id(tag_id)
        if not tag:
            return False
        
        self.session.delete(tag)
        self.session.commit()
        return True
    
    def increment_usage(self, tag_id: int):
        """增加标签使用次数"""
        tag = self.get_by_id(tag_id)
        if tag:
            tag.usage_count += 1
            self.session.add(tag)
            self.session.commit()
    
    def decrement_usage(self, tag_id: int):
        """减少标签使用次数"""
        tag = self.get_by_id(tag_id)
        if tag and tag.usage_count > 0:
            tag.usage_count -= 1
            self.session.add(tag)
            self.session.commit()


class ProjectTagRepository:
    """项目标签关联数据访问层"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def create(self, project_id: int, tag_id: int) -> ProjectTag:
        """为项目添加标签"""
        # 检查是否已存在
        existing = self.session.exec(
            select(ProjectTag).where(
                ProjectTag.project_id == project_id,
                ProjectTag.tag_id == tag_id
            )
        ).first()
        
        if existing:
            return existing
        
        project_tag = ProjectTag(project_id=project_id, tag_id=tag_id)
        self.session.add(project_tag)
        self.session.commit()
        self.session.refresh(project_tag)
        
        # 增加标签使用次数
        tag_repo = TagRepository(self.session)
        tag_repo.increment_usage(tag_id)
        
        return project_tag
    
    def list_by_project(self, project_id: int) -> List[ProjectTag]:
        """获取项目的所有标签"""
        return list(self.session.exec(
            select(ProjectTag).where(ProjectTag.project_id == project_id)
        ).all())
    
    def delete(self, project_id: int, tag_id: int) -> bool:
        """移除项目的标签"""
        project_tag = self.session.exec(
            select(ProjectTag).where(
                ProjectTag.project_id == project_id,
                ProjectTag.tag_id == tag_id
            )
        ).first()
        
        if not project_tag:
            return False
        
        self.session.delete(project_tag)
        self.session.commit()
        
        # 减少标签使用次数
        tag_repo = TagRepository(self.session)
        tag_repo.decrement_usage(tag_id)
        
        return True
    
    def delete_all_by_project(self, project_id: int):
        """删除项目的所有标签"""
        project_tags = self.list_by_project(project_id)
        tag_repo = TagRepository(self.session)
        
        for project_tag in project_tags:
            tag_repo.decrement_usage(project_tag.tag_id)
            self.session.delete(project_tag)
        
        self.session.commit()


class HistoricalProjectTagRepository:
    """历史项目标签关联数据访问层"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def create(self, historical_project_id: int, tag_id: int) -> HistoricalProjectTag:
        """为历史项目添加标签"""
        # 检查是否已存在
        existing = self.session.exec(
            select(HistoricalProjectTag).where(
                HistoricalProjectTag.historical_project_id == historical_project_id,
                HistoricalProjectTag.tag_id == tag_id
            )
        ).first()
        
        if existing:
            return existing
        
        project_tag = HistoricalProjectTag(historical_project_id=historical_project_id, tag_id=tag_id)
        self.session.add(project_tag)
        self.session.commit()
        self.session.refresh(project_tag)
        
        # 增加标签使用次数
        tag_repo = TagRepository(self.session)
        tag_repo.increment_usage(tag_id)
        
        return project_tag
    
    def list_by_project(self, historical_project_id: int) -> List[HistoricalProjectTag]:
        """获取历史项目的所有标签"""
        return list(self.session.exec(
            select(HistoricalProjectTag).where(HistoricalProjectTag.historical_project_id == historical_project_id)
        ).all())
    
    def delete(self, historical_project_id: int, tag_id: int) -> bool:
        """移除历史项目的标签"""
        project_tag = self.session.exec(
            select(HistoricalProjectTag).where(
                HistoricalProjectTag.historical_project_id == historical_project_id,
                HistoricalProjectTag.tag_id == tag_id
            )
        ).first()
        
        if not project_tag:
            return False
        
        self.session.delete(project_tag)
        self.session.commit()
        
        # 减少标签使用次数
        tag_repo = TagRepository(self.session)
        tag_repo.decrement_usage(tag_id)
        
        return True
    
    def delete_all_by_project(self, historical_project_id: int):
        """删除历史项目的所有标签"""
        project_tags = self.list_by_project(historical_project_id)
        tag_repo = TagRepository(self.session)
        
        for project_tag in project_tags:
            tag_repo.decrement_usage(project_tag.tag_id)
            self.session.delete(project_tag)
        
        self.session.commit()

