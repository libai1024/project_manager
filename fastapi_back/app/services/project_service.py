"""
项目服务层

重构后的服务层，使用：
- schemas 中的 DTO
- utils/constants 中的枚举和常量
- utils/permissions 中的权限检查
- core/exceptions 中的自定义异常
"""
import logging
from typing import Optional, List
from sqlmodel import Session

from app.repositories.project_repository import ProjectRepository
from app.repositories.step_repository import StepRepository
from app.repositories.platform_repository import PlatformRepository
from app.models.project import Project, ProjectStep
from app.models.platform import Platform
from app.models.tag import Tag
from app.schemas.project import (
    ProjectCreate, ProjectUpdate, ProjectReadWithRelations,
    ProjectStepCreate, ProjectStepUpdate, ProjectStepRead
)
from app.schemas.platform import PlatformRead
from app.schemas.tag import TagRead
from app.utils.constants import DEFAULT_STEPS, StepStatus, ProjectStatus
from app.utils.permissions import check_project_access_by_id
from app.core.exceptions import NotFoundException, ForbiddenException, BusinessException

logger = logging.getLogger(__name__)


class ProjectService:
    """项目服务层"""

    def __init__(self, session: Session):
        self.session = session
        self.project_repo = ProjectRepository(session)
        self.step_repo = StepRepository(session)
        self.platform_repo = PlatformRepository(session)

    def create_project(self, project_data: ProjectCreate, user_id: int) -> ProjectReadWithRelations:
        """创建项目并自动生成默认步骤和默认文件夹"""
        requirement_files = project_data.requirement_files
        template_id = project_data.template_id

        project = self.project_repo.create(project_data, user_id)

        if template_id:
            self._create_steps_from_template(project.id, template_id)
        else:
            self._create_default_steps(project.id)

        from app.repositories.attachment_folder_repository import AttachmentFolderRepository
        folder_repo = AttachmentFolderRepository(self.session)
        folders = folder_repo.create_default_folders(project.id)

        photo_ids = []
        file_attachment_ids = []
        if requirement_files:
            requirement_folder = next((f for f in folders if f.name == "项目需求"), None)
            if requirement_folder:
                from app.repositories.attachment_repository import AttachmentRepository
                attachment_repo = AttachmentRepository(self.session)
                for file_id in requirement_files:
                    attachment = attachment_repo.get_by_id(file_id)
                    if attachment and attachment.project_id == project.id:
                        attachment.folder_id = requirement_folder.id
                        self.session.add(attachment)
                        if attachment.file_name.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp')):
                            photo_ids.append(file_id)
                        else:
                            file_attachment_ids.append(file_id)
                self.session.commit()

        from app.services.project_log_service import ProjectLogService
        log_service = ProjectLogService(self.session)
        log_service.log_project_created(
            project_id=project.id,
            project_title=project.title,
            attachment_ids=file_attachment_ids if file_attachment_ids else None,
            photo_ids=photo_ids if photo_ids else None,
            user_id=user_id
        )

        return self.get_project_with_relations(project.id)

    def _create_default_steps(self, project_id: int) -> None:
        """为项目创建默认步骤"""
        for index, step_name in enumerate(DEFAULT_STEPS):
            step_data = ProjectStepCreate(
                name=step_name,
                order_index=index
            )
            self.step_repo.create(step_data, project_id)

    def _create_steps_from_template(self, project_id: int, template_id: int) -> None:
        """使用模板为项目创建步骤"""
        from app.services.step_template_service import StepTemplateService
        template_service = StepTemplateService(self.session)
        template = template_service.get_template(template_id)

        for index, step_name in enumerate(template.steps):
            step_data = ProjectStepCreate(
                name=step_name,
                order_index=index
            )
            self.step_repo.create(step_data, project_id)

    def _get_project_or_raise(self, project_id: int) -> Project:
        """获取项目，不存在则抛出异常"""
        project = self.project_repo.get_by_id(project_id)
        if not project:
            raise NotFoundException("项目", id=project_id)
        return project

    def _get_step_or_raise(self, step_id: int) -> ProjectStep:
        """获取步骤，不存在则抛出异常"""
        step = self.step_repo.get_by_id(step_id)
        if not step:
            raise NotFoundException("步骤", id=step_id)
        return step

    def get_project_with_relations(self, project_id: int) -> ProjectReadWithRelations:
        """获取项目详情（包含关联数据）"""
        project = self._get_project_or_raise(project_id)

        platform = self.platform_repo.get_by_id(project.platform_id)
        steps = self.step_repo.list_by_project(project_id)

        from app.repositories.tag_repository import ProjectTagRepository
        project_tag_repo = ProjectTagRepository(self.session)
        project_tags = project_tag_repo.list_by_project(project_id)

        tags = []
        for pt in project_tags:
            tag = self.session.get(Tag, pt.tag_id)
            if tag:
                tags.append(TagRead.model_validate(tag))

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
            "created_at": project.created_at,
            "updated_at": project.updated_at,
        }
        project_dict["platform"] = PlatformRead.model_validate(platform) if platform else None
        project_dict["steps"] = [ProjectStepRead.model_validate(step) for step in steps]
        project_dict["tags"] = tags

        return ProjectReadWithRelations(**project_dict)

    def list_projects(
        self,
        user_id: Optional[int] = None,
        platform_id: Optional[int] = None,
        status: Optional[str] = None,
        tag_ids: Optional[List[int]] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[ProjectReadWithRelations]:
        """获取项目列表（包含关联数据）"""
        projects = self.project_repo.list(user_id, platform_id, status, tag_ids, skip, limit)

        result = []
        for project in projects:
            try:
                project_dict = self._build_project_dict(project)
                result.append(ProjectReadWithRelations(**project_dict))
            except Exception as e:
                logger.error(f"处理项目 {project.id} 时出错: {e}")
                continue

        return result

    def _build_project_dict(self, project: Project) -> dict:
        """构建项目字典，用于返回"""
        platform = self.platform_repo.get_by_id(project.platform_id)
        steps = self.step_repo.list_by_project(project.id)

        from app.repositories.tag_repository import ProjectTagRepository
        project_tag_repo = ProjectTagRepository(self.session)
        project_tags = project_tag_repo.list_by_project(project.id)

        tags = []
        for pt in project_tags:
            tag = self.session.get(Tag, pt.tag_id)
            if tag:
                tags.append(TagRead.model_validate(tag))

        return {
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
            "created_at": project.created_at,
            "updated_at": project.updated_at,
            "platform": PlatformRead.model_validate(platform) if platform else None,
            "steps": [ProjectStepRead.model_validate(step) for step in steps],
            "tags": tags,
        }

    def update_project(
        self,
        project_id: int,
        project_data: ProjectUpdate,
        current_user_id: int,
        admin: bool = False
    ) -> ProjectReadWithRelations:
        """更新项目信息"""
        project = self._get_project_or_raise(project_id)
        check_project_access_by_id(current_user_id, project, is_admin_user=admin, require_owner=not admin)

        update_data = project_data.model_dump(exclude_unset=True)

        # 如果更新了is_paid或status为"已结账"，确保财务数据同步
        if update_data.get('is_paid') is True or update_data.get('status') == "已结账":
            if project.actual_income == 0 and project.price > 0:
                update_data['actual_income'] = project.price
            if update_data.get('is_paid') is True:
                update_data['status'] = "已结账"
            elif update_data.get('status') == "已结账":
                update_data['is_paid'] = True

        self.project_repo.update(project, update_data)
        return self.get_project_with_relations(project_id)

    def settle_project(
        self,
        project_id: int,
        current_user_id: int,
        admin: bool = False
    ) -> ProjectReadWithRelations:
        """项目结账"""
        project = self._get_project_or_raise(project_id)
        check_project_access_by_id(current_user_id, project, is_admin_user=admin, require_owner=not admin)

        if project.is_paid:
            raise BusinessException(code=400, msg="项目已结账，无需重复结账")

        all_steps = self.step_repo.list_by_project(project_id)
        if not all_steps:
            raise BusinessException(code=400, msg="项目没有步骤，无法结账")

        sorted_steps = sorted(all_steps, key=lambda s: s.order_index)
        last_step = sorted_steps[-1]

        if last_step.status != "已完成":
            raise BusinessException(code=400, msg="项目尚未完成最后一个步骤，无法结账")

        update_data = {
            "status": "已结账",
            "is_paid": True
        }

        if project.actual_income == 0 and project.price > 0:
            update_data["actual_income"] = project.price

        self.project_repo.update(project, update_data)
        logger.info(f"项目 {project_id} 手动结账完成")

        return self.get_project_with_relations(project_id)

    def delete_project(
        self,
        project_id: int,
        current_user_id: int,
        admin: bool = False
    ) -> None:
        """删除项目"""
        project = self._get_project_or_raise(project_id)
        check_project_access_by_id(current_user_id, project, is_admin_user=admin, require_owner=not admin)
        self.project_repo.delete(project)

    def create_step(
        self,
        project_id: int,
        step_data: ProjectStepCreate,
        current_user_id: int,
        admin: bool = False
    ) -> ProjectStepRead:
        """为项目添加新步骤"""
        project = self._get_project_or_raise(project_id)
        check_project_access_by_id(current_user_id, project, is_admin_user=admin, require_owner=not admin)

        step = self.step_repo.create(step_data, project_id)
        return ProjectStepRead.model_validate(step)

    def update_step(
        self,
        step_id: int,
        step_data: ProjectStepUpdate,
        current_user_id: int,
        admin: bool = False
    ) -> ProjectStepRead:
        """更新步骤信息"""
        step = self._get_step_or_raise(step_id)
        project = self._get_project_or_raise(step.project_id)
        check_project_access_by_id(current_user_id, project, is_admin_user=admin, require_owner=not admin)

        update_data = step_data.model_dump(exclude_unset=True)
        step = self.step_repo.update(step, update_data)

        self._check_and_update_billing_status(step.project_id)

        return ProjectStepRead.model_validate(step)

    def delete_step(
        self,
        step_id: int,
        current_user_id: int,
        admin: bool = False
    ) -> None:
        """删除步骤"""
        step = self._get_step_or_raise(step_id)
        project = self._get_project_or_raise(step.project_id)
        check_project_access_by_id(current_user_id, project, is_admin_user=admin, require_owner=not admin)

        if step.name == "已结账":
            all_steps = self.step_repo.list_by_project(step.project_id)
            sorted_steps = sorted(all_steps, key=lambda s: s.order_index)
            if sorted_steps and sorted_steps[-1].id == step.id:
                raise BusinessException(code=400, msg="不能删除最后一个'已结账'步骤")

        self.step_repo.delete(step)
        self._check_and_update_billing_status(step.project_id)

    def toggle_step_todo(
        self,
        step_id: int,
        current_user_id: int,
        admin: bool = False
    ) -> ProjectStepRead:
        """切换步骤的Todo状态"""
        step = self._get_step_or_raise(step_id)
        project = self._get_project_or_raise(step.project_id)
        check_project_access_by_id(current_user_id, project, is_admin_user=admin, require_owner=not admin)

        step = self.step_repo.toggle_todo(step)
        return ProjectStepRead.model_validate(step)

    def reorder_steps(
        self,
        step_orders: List[dict],
        current_user_id: int,
        admin: bool = False
    ) -> None:
        """重新排序步骤"""
        for item in step_orders:
            step_id = item.get("step_id")
            step = self.step_repo.get_by_id(step_id)
            if step:
                project = self._get_project_or_raise(step.project_id)
                check_project_access_by_id(current_user_id, project, is_admin_user=admin, require_owner=not admin)

        self.step_repo.bulk_update_order(step_orders)

    def _check_and_update_billing_status(self, project_id: int) -> None:
        """检查项目步骤完成情况，如果所有步骤完成则自动结账"""
        project = self.project_repo.get_by_id(project_id)
        if not project:
            return

        all_steps = self.step_repo.list_by_project(project_id)
        if not all_steps:
            return

        all_completed = all(step.status == "已完成" for step in all_steps)
        has_billing_step = any(step.name == "已结账" for step in all_steps)

        if all_completed and has_billing_step and not project.is_paid:
            update_data = {
                "status": "已结账",
                "is_paid": True
            }

            if project.actual_income == 0 and project.price > 0:
                update_data["actual_income"] = project.price

            self.project_repo.update(project, update_data)
            logger.info(f"项目 {project_id} 自动结账")
