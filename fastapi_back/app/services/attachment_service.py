"""
附件服务层

重构后使用 schemas 中的 DTO 和自定义异常。
"""
from typing import Optional, List
from sqlmodel import Session

from app.repositories.attachment_repository import AttachmentRepository
from app.repositories.project_repository import ProjectRepository
from app.repositories.historical_project_repository import HistoricalProjectRepository
from app.repositories.system_settings_repository import SystemSettingsRepository
from app.models.attachment import Attachment
from app.schemas.attachment import AttachmentUpdate, AttachmentRead
from app.core.exceptions import NotFoundException, ForbiddenException, BusinessException


class AttachmentService:
    """附件服务层"""

    def __init__(self, session: Session):
        self.session = session
        self.attachment_repo = AttachmentRepository(session)
        self.project_repo = ProjectRepository(session)
        self.historical_project_repo = HistoricalProjectRepository(session)
        self.settings_repo = SystemSettingsRepository(session)

    def _check_project_access(self, project, current_user_id: int, is_admin: bool):
        """检查项目访问权限"""
        if not project:
            raise NotFoundException("项目")
        if not is_admin and project.user_id != current_user_id:
            raise ForbiddenException("无权访问此项目的附件")

    def _check_historical_project_access(self, historical_project, current_user_id: int, is_admin: bool):
        """检查历史项目访问权限"""
        if not historical_project:
            raise NotFoundException("历史项目")
        if not is_admin and historical_project.user_id != current_user_id:
            raise ForbiddenException("无权访问此历史项目的附件")

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
        project = self.project_repo.get_by_id(project_id)
        self._check_project_access(project, current_user_id, is_admin)

        attachment = self.attachment_repo.create(
            project_id=project_id,
            file_path=file_path,
            file_name=file_name,
            file_type=file_type,
            description=description,
            folder_id=folder_id
        )

        folder_name = self._get_folder_name(folder_id)

        result = AttachmentRead.model_validate(attachment)
        result.folder_name = folder_name
        return result

    def _get_folder_name(self, folder_id: Optional[int]) -> Optional[str]:
        """获取文件夹名称"""
        if not folder_id:
            return None
        from app.repositories.attachment_folder_repository import AttachmentFolderRepository
        folder_repo = AttachmentFolderRepository(self.session)
        folder = folder_repo.get_by_id(folder_id)
        return folder.name if folder else None

    def get_attachment_by_id(
        self,
        attachment_id: int,
        current_user_id: int = None,
        is_admin: bool = False
    ) -> AttachmentRead:
        """获取附件详情"""
        attachment = self._get_attachment_or_raise(attachment_id)
        self._check_attachment_permission(attachment, current_user_id, is_admin)
        return AttachmentRead.model_validate(attachment)

    def _get_attachment_or_raise(self, attachment_id: int) -> Attachment:
        """获取附件，不存在则抛出异常"""
        attachment = self.attachment_repo.get_by_id(attachment_id)
        if not attachment:
            raise NotFoundException("附件")
        return attachment

    def _check_attachment_permission(self, attachment: Attachment, current_user_id: int, is_admin: bool):
        """检查附件权限"""
        if attachment.project_id:
            project = self.project_repo.get_by_id(attachment.project_id)
            self._check_project_access(project, current_user_id, is_admin)
        elif attachment.historical_project_id:
            historical_project = self.historical_project_repo.get_by_id(attachment.historical_project_id)
            self._check_historical_project_access(historical_project, current_user_id, is_admin)
        else:
            raise BusinessException(code=400, msg="附件必须属于项目或历史项目")

    def list_attachments_by_project(
        self,
        project_id: int,
        current_user_id: int = None,
        is_admin: bool = False
    ) -> List[AttachmentRead]:
        """获取项目的所有附件"""
        project = self.project_repo.get_by_id(project_id)
        self._check_project_access(project, current_user_id, is_admin)

        attachments = self.attachment_repo.list_by_project(project_id)
        from app.repositories.attachment_folder_repository import AttachmentFolderRepository
        folder_repo = AttachmentFolderRepository(self.session)
        folders = {f.id: f.name for f in folder_repo.list_by_project(project_id)}

        other_folder = folder_repo.get_other_folder(project_id)
        if other_folder:
            folders[other_folder.id] = other_folder.name

        result = []
        for att in attachments:
            att_dict = AttachmentRead.model_validate(att)
            if not att.folder_id and other_folder:
                att.folder_id = other_folder.id
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
        attachment = self._get_attachment_or_raise(attachment_id)
        self._check_attachment_permission(attachment, current_user_id, is_admin)

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
        attachment = self._get_attachment_or_raise(attachment_id)
        self._check_attachment_permission(attachment, current_user_id, is_admin)
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
        if not self.settings_repo.is_feature_enabled("enable_resource_management"):
            raise ForbiddenException("历史项目资源管理功能已禁用")

        historical_project = self.historical_project_repo.get_by_id(historical_project_id)
        self._check_historical_project_access(historical_project, current_user_id, is_admin)

        attachment = self.attachment_repo.create(
            historical_project_id=historical_project_id,
            file_path=file_path,
            file_name=file_name,
            file_type=file_type,
            description=description,
            folder_id=folder_id
        )

        folder_name = self._get_folder_name(folder_id)

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
        if not self.settings_repo.is_feature_enabled("enable_resource_management"):
            raise ForbiddenException("历史项目资源管理功能已禁用")

        historical_project = self.historical_project_repo.get_by_id(historical_project_id)
        self._check_historical_project_access(historical_project, current_user_id, is_admin)

        attachments = self.attachment_repo.list_by_historical_project(historical_project_id)

        from app.repositories.attachment_folder_repository import AttachmentFolderRepository
        folder_repo = AttachmentFolderRepository(self.session)
        folders = {}
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
