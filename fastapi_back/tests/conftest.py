"""
Pytest 配置和共享 fixtures

提供测试所需的数据库会话、测试客户端和认证 fixtures。
"""
import pytest
from typing import Generator
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from app.core.database import get_session
from app.models.user import User
from app.models.project import Project, ProjectStep
from app.models.platform import Platform
from app.models.tag import Tag, ProjectTag
from app.core.security import get_password_hash
from main import app


# 使用内存数据库进行测试
@pytest.fixture(name="engine")
def engine_fixture():
    """创建内存数据库引擎"""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    yield engine


@pytest.fixture(name="session")
def session_fixture(engine) -> Generator[Session, None, None]:
    """创建数据库会话"""
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session) -> Generator[TestClient, None, None]:
    """创建测试客户端"""

    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture(name="test_user")
def test_user_fixture(session: Session) -> User:
    """创建测试用户"""
    user = User(
        username="testuser",
        password_hash=get_password_hash("testpassword"),
        role="user"
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@pytest.fixture(name="admin_user")
def admin_user_fixture(session: Session) -> User:
    """创建管理员用户"""
    user = User(
        username="admin",
        password_hash=get_password_hash("adminpassword"),
        role="admin"
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@pytest.fixture(name="auth_headers")
def auth_headers_fixture(client: TestClient, test_user: User) -> dict:
    """获取认证请求头"""
    response = client.post(
        "/api/auth/login",
        data={"username": "testuser", "password": "testpassword"}
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(name="admin_auth_headers")
def admin_auth_headers_fixture(client: TestClient, admin_user: User) -> dict:
    """获取管理员认证请求头"""
    response = client.post(
        "/api/auth/login",
        data={"username": "admin", "password": "adminpassword"}
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(name="test_platform")
def test_platform_fixture(session: Session) -> Platform:
    """创建测试平台"""
    platform = Platform(name="测试平台")
    session.add(platform)
    session.commit()
    session.refresh(platform)
    return platform


@pytest.fixture(name="test_project")
def test_project_fixture(session: Session, test_user: User, test_platform: Platform) -> Project:
    """创建测试项目"""
    project = Project(
        title="测试项目",
        student_name="测试学生",
        platform_id=test_platform.id,
        user_id=test_user.id,
        status="进行中"
    )
    session.add(project)
    session.commit()
    session.refresh(project)
    return project


@pytest.fixture(name="test_step")
def test_step_fixture(session: Session, test_project: Project) -> ProjectStep:
    """创建测试步骤"""
    step = ProjectStep(
        name="测试步骤",
        project_id=test_project.id,
        status="未开始",
        order_index=0
    )
    session.add(step)
    session.commit()
    session.refresh(step)
    return step


@pytest.fixture(name="test_tag")
def test_tag_fixture(session: Session) -> Tag:
    """创建测试标签"""
    tag = Tag(name="测试标签", color="#409EFF")
    session.add(tag)
    session.commit()
    session.refresh(tag)
    return tag
