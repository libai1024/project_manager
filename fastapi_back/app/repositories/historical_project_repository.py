"""
历史项目数据访问层
"""
from typing import Optional, List
from sqlmodel import Session, select, func
from app.models.historical_project import HistoricalProject, HistoricalProjectCreate


class HistoricalProjectRepository:
    """历史项目数据访问层"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def create(self, project_data: HistoricalProjectCreate, user_id: int) -> HistoricalProject:
        """创建历史项目"""
        project_dict = project_data.model_dump()
        project_dict['user_id'] = user_id
        project = HistoricalProject(**project_dict)
        self.session.add(project)
        self.session.commit()
        self.session.refresh(project)
        return project
    
    def get_by_id(self, project_id: int) -> Optional[HistoricalProject]:
        """根据ID获取历史项目"""
        return self.session.get(HistoricalProject, project_id)
    
    def list(
        self,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        user_id: Optional[int] = None,
        platform_id: Optional[int] = None,
        status: Optional[str] = None,
        tag_ids: Optional[List[int]] = None
    ) -> List[HistoricalProject]:
        """获取历史项目列表（支持搜索和筛选）"""
        from app.models.tag import HistoricalProjectTag
        
        query = select(HistoricalProject)
        
        if user_id is not None:
            query = query.where(HistoricalProject.user_id == user_id)
        
        if platform_id is not None:
            query = query.where(HistoricalProject.platform_id == platform_id)
        
        if status is not None:
            query = query.where(HistoricalProject.status == status)
        
        if search:
            # 搜索标题、学生姓名、需求描述
            search_filter = (
                HistoricalProject.title.contains(search) |
                HistoricalProject.student_name.contains(search) |
                HistoricalProject.requirements.contains(search)
            )
            query = query.where(search_filter)
        
        # 标签筛选
        if tag_ids:
            # 找到有这些标签的项目ID
            project_ids_result = self.session.exec(
                select(HistoricalProjectTag.historical_project_id).where(
                    HistoricalProjectTag.tag_id.in_(tag_ids)
                ).distinct()
            ).all()
            project_ids_list = list(project_ids_result)
            if project_ids_list:
                query = query.where(HistoricalProject.id.in_(project_ids_list))
            else:
                # 如果没有项目匹配，返回空结果
                query = query.where(HistoricalProject.id == -1)  # 不存在的ID，确保返回空
        
        query = query.order_by(HistoricalProject.imported_at.desc()).offset(skip).limit(limit)
        return list(self.session.exec(query).all())
    
    def count(
        self,
        search: Optional[str] = None,
        user_id: Optional[int] = None,
        platform_id: Optional[int] = None,
        status: Optional[str] = None,
        tag_ids: Optional[List[int]] = None
    ) -> int:
        """获取历史项目总数"""
        from app.models.tag import HistoricalProjectTag
        
        query = select(func.count(HistoricalProject.id))
        
        if user_id is not None:
            query = query.where(HistoricalProject.user_id == user_id)
        
        if platform_id is not None:
            query = query.where(HistoricalProject.platform_id == platform_id)
        
        if status is not None:
            query = query.where(HistoricalProject.status == status)
        
        if search:
            search_filter = (
                HistoricalProject.title.contains(search) |
                HistoricalProject.student_name.contains(search) |
                HistoricalProject.requirements.contains(search)
            )
            query = query.where(search_filter)
        
        # 标签筛选
        if tag_ids:
            project_ids_result = self.session.exec(
                select(HistoricalProjectTag.historical_project_id).where(
                    HistoricalProjectTag.tag_id.in_(tag_ids)
                ).distinct()
            ).all()
            project_ids_list = list(project_ids_result)
            if project_ids_list:
                query = query.where(HistoricalProject.id.in_(project_ids_list))
            else:
                # 如果没有项目匹配，返回空结果
                query = query.where(HistoricalProject.id == -1)  # 不存在的ID，确保返回空
        
        return self.session.exec(query).one()
    
    def update(self, project: HistoricalProject, update_data: dict) -> HistoricalProject:
        """更新历史项目信息"""
        for field, value in update_data.items():
            setattr(project, field, value)
        self.session.add(project)
        self.session.commit()
        self.session.refresh(project)
        return project
    
    def delete(self, project: HistoricalProject) -> None:
        """删除历史项目"""
        self.session.delete(project)
        self.session.commit()
    
    def import_from_project(self, project_id: int, user_id: int) -> Optional[HistoricalProject]:
        """从现有项目导入为历史项目"""
        from app.models.project import Project
        from app.repositories.project_repository import ProjectRepository
        
        project_repo = ProjectRepository(self.session)
        original_project = project_repo.get_by_id(project_id)
        
        if not original_project:
            return None
        
        # 创建历史项目
        historical_project = HistoricalProject(
            title=original_project.title,
            student_name=original_project.student_name,
            platform_id=original_project.platform_id,
            user_id=user_id,
            price=original_project.price,
            actual_income=original_project.actual_income,
            status="已完成",
            github_url=original_project.github_url,
            requirements=original_project.requirements,
            is_paid=original_project.is_paid,
            original_project_id=project_id,
            import_source="从项目导入",
            completion_date=original_project.updated_at
        )
        
        self.session.add(historical_project)
        self.session.commit()
        self.session.refresh(historical_project)
        
        return historical_project

