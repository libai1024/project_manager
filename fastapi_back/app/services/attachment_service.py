"""
附件服务层
"""
from typing import Optional, List
from sqlmodel import Session
from fastapi import HTTPException, status
from app.repositories.attachment_repository import AttachmentRepository
from app.repositories.project_repository import ProjectRepository
from app.repositories.historical_project_repository import HistoricalProjectRepository
from app.repositories.system_settings_repository import SystemSettingsRepository
from app.models.attachment import Attachment, AttachmentUpdate, AttachmentRead


class AttachmentService:
    """附件服务层"""
    
    def __init__(self, session: Session):
        self.session = session
        self.attachment_repo = AttachmentRepository(session)
        self.project_repo = ProjectRepository(session)
        self.historical_project_repo = HistoricalProjectRepository(session)
        self.settings_repo = SystemSettingsRepository(session)
    
    def create_attachment(
        self,
        project_id: int,
        file_path: str,
        file_name: str,
        file_type: str,
        description: Optional[str] = None,
        folder_id: Optional[int] = None,
        current_user_id: int = None,
        is_admin: bool = False
    ) -> AttachmentRead:
        """创建附件"""
        # 检查项目是否存在和权限
        project = self.project_repo.get_by_id(project_id)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        
        # 权限检查
        if not is_admin and project.user_id != current_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        
        attachment = self.attachment_repo.create(
            project_id=project_id,
            file_path=file_path,
            file_name=file_name,
            file_type=file_type,
            description=description,
            folder_id=folder_id
        )
        
        # 获取文件夹名称
        folder_name = None
        if folder_id:
            from app.repositories.attachment_folder_repository import AttachmentFolderRepository
            folder_repo = AttachmentFolderRepository(self.session)
            folder = folder_repo.get_by_id(folder_id)
            if folder:
                folder_name = folder.name
        
        result = AttachmentRead.model_validate(attachment)
        result.folder_name = folder_name
        return result
    
    def get_attachment_by_id(
        self,
        attachment_id: int,
        current_user_id: int = None,
        is_admin: bool = False
    ) -> AttachmentRead:
        """获取附件详情"""
        attachment = self.attachment_repo.get_by_id(attachment_id)
        if not attachment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Attachment not found"
            )
        
        # 检查是项目还是历史项目
        if attachment.project_id:
            project = self.project_repo.get_by_id(attachment.project_id)
            if not project:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Project not found"
                )
            # 权限检查
            if not is_admin and project.user_id != current_user_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Not enough permissions"
                )
        elif attachment.historical_project_id:
            historical_project = self.historical_project_repo.get_by_id(attachment.historical_project_id)
            if not historical_project:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Historical project not found"
                )
            # 权限检查
            if not is_admin and historical_project.user_id != current_user_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Not enough permissions"
                )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Attachment must belong to a project or historical project"
            )
        
        return AttachmentRead.model_validate(attachment)
    
    def list_attachments_by_project(
        self,
        project_id: int,
        current_user_id: int = None,
        is_admin: bool = False
    ) -> List[AttachmentRead]:
        """获取项目的所有附件"""
        project = self.project_repo.get_by_id(project_id)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        
        # 权限检查
        if not is_admin and project.user_id != current_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        
        attachments = self.attachment_repo.list_by_project(project_id)
        # 获取文件夹信息
        from app.repositories.attachment_folder_repository import AttachmentFolderRepository
        folder_repo = AttachmentFolderRepository(self.session)
        folders = {f.id: f.name for f in folder_repo.list_by_project(project_id)}
        
        # 获取"其他"文件夹，确保存在
        other_folder = folder_repo.get_other_folder(project_id)
        if other_folder:
            folders[other_folder.id] = other_folder.name
        
        result = []
        for att in attachments:
            att_dict = AttachmentRead.model_validate(att)
            # 如果没有 folder_id，自动分配到"其他"文件夹
            if not att.folder_id and other_folder:
                att.folder_id = other_folder.id
                # 更新数据库中的 folder_id
                self.attachment_repo.update(att, {'folder_id': other_folder.id})
                att_dict.folder_id = other_folder.id
                att_dict.folder_name = other_folder.name
            elif att.folder_id and att.folder_id in folders:
                att_dict.folder_name = folders[att.folder_id]
            elif att.folder_id and other_folder and att.folder_id == other_folder.id:
                att_dict.folder_name = other_folder.name
            result.append(att_dict)
        
        return result
    
    def update_attachment(
        self,
        attachment_id: int,
        attachment_data: AttachmentUpdate,
        current_user_id: int = None,
        is_admin: bool = False
    ) -> AttachmentRead:
        """更新附件信息"""
        attachment = self.attachment_repo.get_by_id(attachment_id)
        if not attachment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Attachment not found"
            )
        
        # 检查是项目还是历史项目
        if attachment.project_id:
            project = self.project_repo.get_by_id(attachment.project_id)
            if not project:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Project not found"
                )
            # 权限检查
            if not is_admin and project.user_id != current_user_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Not enough permissions"
                )
        elif attachment.historical_project_id:
            historical_project = self.historical_project_repo.get_by_id(attachment.historical_project_id)
            if not historical_project:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Historical project not found"
                )
            # 权限检查
            if not is_admin and historical_project.user_id != current_user_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Not enough permissions"
                )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Attachment must belong to a project or historical project"
            )
        
        update_data = attachment_data.model_dump(exclude_unset=True)
        attachment = self.attachment_repo.update(attachment, update_data)
        return AttachmentRead.model_validate(attachment)
    
    def delete_attachment(
        self,
        attachment_id: int,
        current_user_id: int = None,
        is_admin: bool = False
    ) -> None:
        """删除附件"""
        attachment = self.attachment_repo.get_by_id(attachment_id)
        if not attachment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Attachment not found"
            )
        
        # 检查是项目还是历史项目
        if attachment.project_id:
            project = self.project_repo.get_by_id(attachment.project_id)
            if not project:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Project not found"
                )
            # 权限检查
            if not is_admin and project.user_id != current_user_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Not enough permissions"
                )
        elif attachment.historical_project_id:
            historical_project = self.historical_project_repo.get_by_id(attachment.historical_project_id)
            if not historical_project:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Historical project not found"
                )
            # 权限检查
            if not is_admin and historical_project.user_id != current_user_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Not enough permissions"
                )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Attachment must belong to a project or historical project"
            )
        
        self.attachment_repo.delete(attachment)
    
    def create_attachment_for_historical_project(
        self,
        historical_project_id: int,
        file_path: str,
        file_name: str,
        file_type: str,
        description: Optional[str] = None,
        folder_id: Optional[int] = None,
        current_user_id: int = None,
        is_admin: bool = False
    ) -> AttachmentRead:
        """为历史项目创建附件"""
        # 检查功能是否启用
        if not self.settings_repo.is_feature_enabled("enable_resource_management"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="历史项目资源管理功能已禁用"
            )
        
        # 检查历史项目是否存在和权限
        historical_project = self.historical_project_repo.get_by_id(historical_project_id)
        if not historical_project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Historical project not found"
            )
        
        # 权限检查
        if not is_admin and historical_project.user_id != current_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        
        attachment = self.attachment_repo.create(
            historical_project_id=historical_project_id,
            file_path=file_path,
            file_name=file_name,
            file_type=file_type,
            description=description,
            folder_id=folder_id
        )
        
        # 获取文件夹名称
        folder_name = None
        if folder_id:
            from app.repositories.attachment_folder_repository import AttachmentFolderRepository
            folder_repo = AttachmentFolderRepository(self.session)
            folder = folder_repo.get_by_id(folder_id)
            if folder:
                folder_name = folder.name
        
        result = AttachmentRead.model_validate(attachment)
        result.folder_name = folder_name
        return result
    
    def list_attachments_by_historical_project(
        self,
        historical_project_id: int,
        current_user_id: int = None,
        is_admin: bool = False
    ) -> List[AttachmentRead]:
        """获取历史项目的所有附件"""
        # 检查功能是否启用
        if not self.settings_repo.is_feature_enabled("enable_resource_management"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="历史项目资源管理功能已禁用"
            )
        
        historical_project = self.historical_project_repo.get_by_id(historical_project_id)
        if not historical_project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Historical project not found"
            )
        
        # 权限检查
        if not is_admin and historical_project.user_id != current_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        
        attachments = self.attachment_repo.list_by_historical_project(historical_project_id)
        
        # 获取文件夹信息
        from app.repositories.attachment_folder_repository import AttachmentFolderRepository
        folder_repo = AttachmentFolderRepository(self.session)
        folders = {}
        # 尝试获取历史项目的文件夹（如果仓库支持）
        if hasattr(folder_repo, 'list_by_historical_project'):
            try:
                folder_list = folder_repo.list_by_historical_project(historical_project_id)
                folders = {f.id: f.name for f in folder_list}
            except:
                pass
        
        result = []
        for att in attachments:
            att_dict = AttachmentRead.model_validate(att)
            if att.folder_id and att.folder_id in folders:
                att_dict.folder_name = folders[att.folder_id]
            result.append(att_dict)
        
        return result

