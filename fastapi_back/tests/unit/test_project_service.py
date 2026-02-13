"""
项目 Service 单元测试
"""
import pytest
from sqlmodel import Session

from app.services.project_service import ProjectService
from app.models.project import Project
from app.models.user import User
from app.models.platform import Platform
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectStepCreate, ProjectStepUpdate
from app.core.exceptions import NotFoundException, ForbiddenException


class TestProjectService:
    """项目 Service 测试类"""

    def test_create_project(self, session: Session, test_user: User, test_platform: Platform):
        """测试创建项目"""
        service = ProjectService(session)
        project_data = ProjectCreate(
            title="新项目",
            student_name="新学生",
            platform_id=test_platform.id,
            user_id=test_user.id
        )

        project = service.create_project(project_data)

        assert project.id is not None
        assert project.title == "新项目"
        # 验证默认步骤已创建
        assert len(project.steps) > 0

    def test_get_project_by_id(self, session: Session, test_project: Project):
        """测试通过 ID 获取项目"""
        service = ProjectService(session)

        found_project = service.get_project_by_id(test_project.id)

        assert found_project.id == test_project.id
        assert found_project.title == test_project.title

    def test_get_project_by_id_not_found(self, session: Session):
        """测试获取不存在的项目"""
        service = ProjectService(session)

        with pytest.raises(NotFoundException):
            service.get_project_by_id(99999)

    def test_list_projects(self, session: Session, test_project: Project):
        """测试获取项目列表"""
        service = ProjectService(session)

        projects = service.list_projects()

        assert len(projects) == 1
        assert projects[0].id == test_project.id

    def test_list_projects_by_user(
        self,
        session: Session,
        test_user: User,
        test_project: Project,
        admin_user: User,
        test_platform: Platform
    ):
        """测试获取用户的项目列表"""
        service = ProjectService(session)

        # 创建另一个用户的项目
        service.create_project(ProjectCreate(
            title="管理员项目",
            platform_id=test_platform.id,
            user_id=admin_user.id
        ))

        # 普通用户只能看到自己的项目
        user_projects = service.list_projects(user_id=test_user.id, is_admin=False)

        assert len(user_projects) == 1
        assert user_projects[0].user_id == test_user.id

    def test_update_project(self, session: Session, test_project: Project, test_user: User):
        """测试更新项目"""
        service = ProjectService(session)
        update_data = ProjectUpdate(title="更新后的标题")

        updated_project = service.update_project(
            test_project.id,
            update_data,
            current_user_id=test_user.id,
            is_admin=False
        )

        assert updated_project.title == "更新后的标题"

    def test_update_project_forbidden(self, session: Session, test_project: Project, admin_user: User):
        """测试无权限更新项目"""
        service = ProjectService(session)
        update_data = ProjectUpdate(title="更新后的标题")

        with pytest.raises(ForbiddenException):
            service.update_project(
                test_project.id,
                update_data,
                current_user_id=admin_user.id,
                is_admin=False
            )

    def test_delete_project(self, session: Session, test_project: Project, test_user: User):
        """测试删除项目"""
        service = ProjectService(session)

        service.delete_project(
            test_project.id,
            current_user_id=test_user.id,
            is_admin=False
        )

        with pytest.raises(NotFoundException):
            service.get_project_by_id(test_project.id)


class TestStepService:
    """步骤 Service 测试类"""

    def test_create_step(self, session: Session, test_project: Project):
        """测试创建步骤"""
        service = ProjectService(session)
        step_data = ProjectStepCreate(name="新步骤")

        step = service.create_step(test_project.id, step_data)

        assert step.id is not None
        assert step.name == "新步骤"
        assert step.project_id == test_project.id

    def test_update_step(self, session: Session, test_step, test_user: User):
        """测试更新步骤"""
        service = ProjectService(session)
        step_data = ProjectStepUpdate(status="已完成")

        updated_step = service.update_step(
            test_step.id,
            step_data,
            current_user_id=test_user.id,
            is_admin=False
        )

        assert updated_step.status == "已完成"

    def test_delete_step(self, session: Session, test_project: Project, test_user: User):
        """测试删除步骤"""
        service = ProjectService(session)

        # 创建一个新步骤
        step = service.create_step(test_project.id, ProjectStepCreate(name="要删除的步骤"))
        step_id = step.id

        service.delete_step(
            step_id,
            current_user_id=test_user.id,
            is_admin=False
        )

        # 验证步骤已被删除
        from app.repositories.step_repository import StepRepository
        repo = StepRepository(session)
        assert repo.get_by_id(step_id) is None
