"""
项目数据访问层

重构后继承 BaseRepository，复用通用 CRUD 方法。
"""
from typing import Optional, List
from sqlmodel import Session, select

from app.repositories.base import BaseRepository
from app.repositories.tag_repository import ProjectTagRepository
from app.models.project import Project
from app.schemas.project import ProjectCreate


class ProjectRepository(BaseRepository[Project]):
    """项目数据访问层"""

    def __init__(self, session: Session):
        super().__init__(session, Project)
        self.project_tag_repo = ProjectTagRepository(session)

    def create(self, project_data: ProjectCreate, user_id: int) -> Project:
        """创建项目"""
        tag_ids = project_data.tag_ids if hasattr(project_data, 'tag_ids') else []
        project_dict = project_data.model_dump(exclude={'requirement_files', 'template_id', 'tag_ids'})
        project_dict['user_id'] = user_id
        project = Project(**project_dict)
        self.session.add(project)
        self.session.commit()
        self.session.refresh(project)

        # 添加标签关联
        if tag_ids:
            for tag_id in tag_ids:
                self.project_tag_repo.create(project.id, tag_id)

        return project

    def list(
        self,
        user_id: Optional[int] = None,
        platform_id: Optional[int] = None,
        status: Optional[str] = None,
        tag_ids: Optional[List[int]] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Project]:
        """获取项目列表（支持筛选）"""
        from app.models.tag import ProjectTag

        query = select(Project)

        if user_id is not None:
            query = query.where(Project.user_id == user_id)

        if platform_id is not None:
            query = query.where(Project.platform_id == platform_id)

        if status is not None:
            query = query.where(Project.status == status)

        # 标签筛选
        if tag_ids:
            project_ids_result = self.session.exec(
                select(ProjectTag.project_id).where(ProjectTag.tag_id.in_(tag_ids)).distinct()
            ).all()
            project_ids_list = list(project_ids_result)
            if project_ids_list:
                query = query.where(Project.id.in_(project_ids_list))
            else:
                query = query.where(Project.id == -1)

        query = query.offset(skip).limit(limit)
        return list(self.session.exec(query).all())

    def list_by_user(self, user_id: int) -> List[Project]:
        """获取用户的所有项目"""
        return self.find_many(user_id=user_id)

    def update(self, project: Project, update_data: dict) -> Project:
        """更新项目信息"""
        tag_ids = update_data.pop('tag_ids', None)

        for field, value in update_data.items():
            setattr(project, field, value)
        self.session.add(project)
        self.session.commit()
        self.session.refresh(project)

        # 更新标签关联
        if tag_ids is not None:
            current_project_tags = self.project_tag_repo.list_by_project(project.id)
            current_tag_ids = {pt.tag_id for pt in current_project_tags}
            new_tag_ids = set(tag_ids)

            for tag_id_to_remove in current_tag_ids - new_tag_ids:
                self.project_tag_repo.delete(project.id, tag_id_to_remove)

            for tag_id_to_add in new_tag_ids - current_tag_ids:
                self.project_tag_repo.create(project.id, tag_id_to_add)

            self.session.refresh(project)

        return project

    def delete(self, project: Project) -> None:
        """删除项目"""
        self.project_tag_repo.delete_all_by_project(project.id)
        self.session.delete(project)
        self.session.commit()

    def get_by_status(self, status: str, user_id: Optional[int] = None) -> List[Project]:
        """根据状态获取项目列表"""
        return self.find_many(status=status, user_id=user_id)
