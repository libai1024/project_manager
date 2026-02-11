"""
历史项目服务层
"""
import logging
from typing import Optional, List
from sqlmodel import Session
from fastapi import HTTPException, status
from app.repositories.historical_project_repository import HistoricalProjectRepository
from app.repositories.attachment_repository import AttachmentRepository
from app.repositories.user_repository import UserRepository
from app.repositories.platform_repository import PlatformRepository
from app.repositories.system_settings_repository import SystemSettingsRepository
from app.models.historical_project import (
    HistoricalProject, HistoricalProjectCreate, HistoricalProjectUpdate,
    HistoricalProjectReadWithRelations, HistoricalProjectImportRequest
)

logger = logging.getLogger(__name__)


class HistoricalProjectService:
    """历史项目服务层"""
    
    def __init__(self, session: Session):
        self.session = session
        self.historical_project_repo = HistoricalProjectRepository(session)
        self.attachment_repo = AttachmentRepository(session)
        self.user_repo = UserRepository(session)
        self.platform_repo = PlatformRepository(session)
        self.settings_repo = SystemSettingsRepository(session)
    
    def check_feature_enabled(self, feature_key: str) -> bool:
        """检查功能是否启用"""
        return self.settings_repo.is_feature_enabled(feature_key)
    
    def create_historical_project(
        self,
        project_data: HistoricalProjectCreate,
        user_id: int
    ) -> HistoricalProjectReadWithRelations:
        """创建历史项目"""
        # 检查功能是否启用
        if not self.check_feature_enabled("enable_project_management"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="历史项目管理功能已禁用"
            )
        
        historical_project = self.historical_project_repo.create(project_data, user_id)
        return self.get_historical_project_with_relations(historical_project.id)
    
    def get_historical_project_with_relations(self, project_id: int) -> HistoricalProjectReadWithRelations:
        """获取历史项目详情（包含关联数据）"""
        project = self.historical_project_repo.get_by_id(project_id)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="历史项目不存在"
            )
        
        # 获取关联数据
        platform_name = None
        if project.platform_id:
            platform = self.platform_repo.get_by_id(project.platform_id)
            platform_name = platform.name if platform else None
        
        user = self.user_repo.get_by_id(project.user_id)
        user_name = user.username if user else None
        
        # 统计关联数据数量（根据功能开关决定是否查询）
        attachment_count = 0
        folder_count = 0
        todo_count = 0
        log_count = 0
        part_count = 0
        
        if self.check_feature_enabled("enable_resource_management"):
            # 统计附件和文件夹
            attachments = self.attachment_repo.list_by_historical_project(project_id)
            attachment_count = len(attachments)
        
        # 加载标签
        from app.repositories.tag_repository import HistoricalProjectTagRepository
        from app.models.tag import TagRead, Tag
        historical_project_tag_repo = HistoricalProjectTagRepository(self.session)
        historical_project_tags = historical_project_tag_repo.list_by_project(project_id)
        tags = []
        for hpt in historical_project_tags:
            # 通过tag_id获取Tag对象
            tag = self.session.get(Tag, hpt.tag_id)
            if tag:
                tags.append(TagRead.model_validate(tag))
        
        # 构建返回数据
        project_dict = {
            "id": project.id,
            "title": project.title,
            "student_name": project.student_name,
            "platform_id": project.platform_id,
            "user_id": project.user_id,
            "price": project.price,
            "actual_income": project.actual_income,
            "status": project.status,
            "github_url": project.github_url,
            "requirements": project.requirements,
            "is_paid": project.is_paid,
            "original_project_id": project.original_project_id,
            "imported_at": project.imported_at,
            "import_source": project.import_source,
            "completion_date": project.completion_date,
            "notes": project.notes,
            "created_at": project.created_at,
            "updated_at": project.updated_at,
            "platform_name": platform_name,
            "user_name": user_name,
            "tags": tags,
            "attachment_count": attachment_count,
            "folder_count": folder_count,
            "todo_count": todo_count,
            "log_count": log_count,
            "part_count": part_count
        }
        
        return HistoricalProjectReadWithRelations(**project_dict)
    
    def list_historical_projects(
        self,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        user_id: Optional[int] = None,
        platform_id: Optional[int] = None,
        status: Optional[str] = None,
        tag_ids: Optional[List[int]] = None
    ) -> List[HistoricalProjectReadWithRelations]:
        """获取历史项目列表"""
        projects = self.historical_project_repo.list(
            skip=skip,
            limit=limit,
            search=search,
            user_id=user_id,
            platform_id=platform_id,
            status=status,
            tag_ids=tag_ids
        )
        
        result = []
        for project in projects:
            try:
                result.append(self.get_historical_project_with_relations(project.id))
            except Exception as e:
                logger.error(f"Error processing historical project {project.id}: {str(e)}", exc_info=True)
                continue
        
        return result
    
    def update_historical_project(
        self,
        project_id: int,
        update_data: HistoricalProjectUpdate,
        current_user_id: int,
        is_admin: bool = False
    ) -> HistoricalProjectReadWithRelations:
        """更新历史项目"""
        project = self.historical_project_repo.get_by_id(project_id)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="历史项目不存在"
            )
        
        # 权限检查：只有创建人或管理员可以编辑
        if not is_admin and project.user_id != current_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权编辑此历史项目"
            )
        
        update_dict = update_data.model_dump(exclude_unset=True)
        self.historical_project_repo.update(project, update_dict)
        
        return self.get_historical_project_with_relations(project_id)
    
    def delete_historical_project(
        self,
        project_id: int,
        current_user_id: int,
        is_admin: bool = False
    ) -> None:
        """删除历史项目"""
        project = self.historical_project_repo.get_by_id(project_id)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="历史项目不存在"
            )
        
        # 权限检查：只有创建人或管理员可以删除
        if not is_admin and project.user_id != current_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权删除此历史项目"
            )
        
        self.historical_project_repo.delete(project)
    
    def import_from_project(self, project_id: int, user_id: int) -> HistoricalProjectReadWithRelations:
        """从现有项目导入为历史项目"""
        historical_project = self.historical_project_repo.import_from_project(project_id, user_id)
        if not historical_project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="原项目不存在"
            )
        
        return self.get_historical_project_with_relations(historical_project.id)
    
    def batch_import(self, import_request: HistoricalProjectImportRequest, user_id: int) -> List[HistoricalProjectReadWithRelations]:
        """批量导入历史项目"""
        results = []
        for project_data in import_request.projects:
            try:
                project_data.import_source = import_request.import_source or project_data.import_source
                historical_project = self.historical_project_repo.create(project_data, user_id)
                results.append(self.get_historical_project_with_relations(historical_project.id))
            except Exception as e:
                logger.error(f"Error importing historical project: {str(e)}", exc_info=True)
                continue
        
        return results
    
    def get_count(
        self,
        search: Optional[str] = None,
        user_id: Optional[int] = None,
        platform_id: Optional[int] = None,
        status: Optional[str] = None,
        tag_ids: Optional[List[int]] = None
    ) -> int:
        """获取历史项目总数"""
        return self.historical_project_repo.count(
            search=search,
            user_id=user_id,
            platform_id=platform_id,
            status=status,
            tag_ids=tag_ids
        )

