"""
项目 Repository 单元测试
"""
import pytest
from sqlmodel import Session

from app.repositories.project_repository import ProjectRepository
from app.models.project import Project, ProjectStep
from app.models.user import User
from app.models.platform import Platform


class TestProjectRepository:
    """项目 Repository 测试类"""

    def test_create_project(self, session: Session, test_user: User, test_platform: Platform):
        """测试创建项目"""
        repo = ProjectRepository(session)

        from app.schemas.project import ProjectCreate
        project_data = ProjectCreate(
            title="新项目",
            student_name="新学生",
            platform_id=test_platform.id,
            user_id=test_user.id
        )

        project = repo.create(project_data)

        assert project.id is not None
        assert project.title == "新项目"
        assert project.student_name == "新学生"
        assert project.platform_id == test_platform.id
        assert project.user_id == test_user.id

    def test_get_by_id(self, session: Session, test_project: Project):
        """测试通过 ID 获取项目"""
        repo = ProjectRepository(session)

        found_project = repo.get_by_id(test_project.id)

        assert found_project is not None
        assert found_project.id == test_project.id
        assert found_project.title == test_project.title

    def test_get_by_id_not_found(self, session: Session):
        """测试获取不存在的项目"""
        repo = ProjectRepository(session)

        found_project = repo.get_by_id(99999)

        assert found_project is None

    def test_list(self, session: Session, test_project: Project):
        """测试获取项目列表"""
        repo = ProjectRepository(session)

        projects = repo.list()

        assert len(projects) == 1
        assert projects[0].id == test_project.id

    def test_list_by_user(self, session: Session, test_user: User, test_project: Project, admin_user: User):
        """测试获取用户的项目列表"""
        repo = ProjectRepository(session)

        # 创建另一个用户的项目
        from app.schemas.project import ProjectCreate
        repo.create(ProjectCreate(
            title="管理员项目",
            platform_id=test_project.platform_id,
            user_id=admin_user.id
        ))

        user_projects = repo.list_by_user(test_user.id)

        assert len(user_projects) == 1
        assert user_projects[0].user_id == test_user.id

    def test_list_by_platform(self, session: Session, test_platform: Platform, test_project: Project):
        """测试获取平台的项目列表"""
        repo = ProjectRepository(session)

        # 创建另一个平台
        other_platform = Platform(name="其他平台")
        session.add(other_platform)
        session.commit()
        session.refresh(other_platform)

        from app.schemas.project import ProjectCreate
        repo.create(ProjectCreate(
            title="其他平台项目",
            platform_id=other_platform.id,
            user_id=test_project.user_id
        ))

        platform_projects = repo.list_by_platform(test_platform.id)

        assert len(platform_projects) == 1
        assert platform_projects[0].platform_id == test_platform.id

    def test_update(self, session: Session, test_project: Project):
        """测试更新项目"""
        repo = ProjectRepository(session)

        updated_project = repo.update(test_project, {"title": "更新后的标题"})

        assert updated_project.title == "更新后的标题"

    def test_delete(self, session: Session, test_project: Project):
        """测试删除项目"""
        repo = ProjectRepository(session)
        project_id = test_project.id

        repo.delete(test_project)

        assert repo.get_by_id(project_id) is None


class TestStepRepository:
    """步骤 Repository 测试类"""

    def test_create_step(self, session: Session, test_project: Project):
        """测试创建步骤"""
        from app.repositories.step_repository import StepRepository
        repo = StepRepository(session)

        from app.schemas.project import ProjectStepCreate
        step_data = ProjectStepCreate(
            name="新步骤",
            project_id=test_project.id
        )

        step = repo.create(step_data)

        assert step.id is not None
        assert step.name == "新步骤"
        assert step.project_id == test_project.id
        assert step.status == "未开始"

    def test_list_by_project(self, session: Session, test_project: Project, test_step: ProjectStep):
        """测试获取项目的步骤列表"""
        from app.repositories.step_repository import StepRepository
        repo = StepRepository(session)

        steps = repo.list_by_project(test_project.id)

        assert len(steps) == 1
        assert steps[0].id == test_step.id

    def test_update_step_status(self, session: Session, test_step: ProjectStep):
        """测试更新步骤状态"""
        from app.repositories.step_repository import StepRepository
        repo = StepRepository(session)

        updated_step = repo.update(test_step, {"status": "已完成"})

        assert updated_step.status == "已完成"

    def test_delete_step(self, session: Session, test_project: Project):
        """测试删除步骤"""
        from app.repositories.step_repository import StepRepository
        repo = StepRepository(session)

        # 创建一个新步骤
        from app.schemas.project import ProjectStepCreate
        step = repo.create(ProjectStepCreate(
            name="要删除的步骤",
            project_id=test_project.id
        ))
        step_id = step.id

        repo.delete(step)

        assert repo.get_by_id(step_id) is None
