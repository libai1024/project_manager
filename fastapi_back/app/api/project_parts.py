"""
项目配件清单 API
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.core.database import get_session
from app.core.dependencies import get_current_active_user
from app.models.user import User
from app.models.project import Project
from app.models.historical_project import HistoricalProject
from app.models.project_part import ProjectPart, ProjectPartCreate, ProjectPartUpdate, ProjectPartRead
from app.repositories.system_settings_repository import SystemSettingsRepository


router = APIRouter()


def _check_project_permission(session: Session, project_id: int, current_user: User) -> Project:
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    if current_user.role != "admin" and project.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return project


def _check_historical_project_permission(session: Session, historical_project_id: int, current_user: User) -> HistoricalProject:
    """检查历史项目权限"""
    from app.repositories.system_settings_repository import SystemSettingsRepository
    settings_repo = SystemSettingsRepository(session)
    if not settings_repo.is_feature_enabled("enable_part_management"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="历史项目配件管理功能已禁用")
    
    from app.repositories.historical_project_repository import HistoricalProjectRepository
    historical_project_repo = HistoricalProjectRepository(session)
    historical_project = historical_project_repo.get_by_id(historical_project_id)
    if not historical_project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Historical project not found"
        )
    if current_user.role != "admin" and historical_project.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return historical_project


@router.get("/project/{project_id}", response_model=List[ProjectPartRead])
async def list_project_parts(
    project_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
):
    """获取项目的配件清单"""
    _check_project_permission(session, project_id, current_user)
    statement = select(ProjectPart).where(ProjectPart.project_id == project_id).order_by(ProjectPart.id)
    parts = session.exec(statement).all()
    return [ProjectPartRead.model_validate(p) for p in parts]


@router.post("/project/{project_id}", response_model=List[ProjectPartRead])
async def create_project_parts(
    project_id: int,
    parts_data: List[ProjectPartCreate],
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
):
    """
    批量创建项目配件条目
    """
    _check_project_permission(session, project_id, current_user)
    created_parts: List[ProjectPart] = []
    for item in parts_data:
        # 从路径参数获取 project_id，创建配件条目
        part_data = item.model_dump()
        part_data["project_id"] = project_id
        part = ProjectPart(**part_data)
        session.add(part)
        created_parts.append(part)
    session.commit()
    for part in created_parts:
        session.refresh(part)
    return [ProjectPartRead.model_validate(p) for p in created_parts]


@router.put("/{part_id}", response_model=ProjectPartRead)
async def update_project_part(
    part_id: int,
    part_data: ProjectPartUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
):
    """更新单个配件条目"""
    part = session.get(ProjectPart, part_id)
    if not part:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Part not found"
        )
    if part.project_id:
        _check_project_permission(session, part.project_id, current_user)
    elif part.historical_project_id:
        _check_historical_project_permission(session, part.historical_project_id, current_user)
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Part must belong to a project or historical project")

    update_data = part_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(part, key, value)

    session.add(part)
    session.commit()
    session.refresh(part)
    return ProjectPartRead.model_validate(part)


@router.delete("/{part_id}")
async def delete_project_part(
    part_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
):
    """删除单个配件条目"""
    part = session.get(ProjectPart, part_id)
    if not part:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Part not found"
        )
    if part.project_id:
        _check_project_permission(session, part.project_id, current_user)
    elif part.historical_project_id:
        _check_historical_project_permission(session, part.historical_project_id, current_user)
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Part must belong to a project or historical project")

    session.delete(part)
    session.commit()
    return {"message": "Part deleted successfully"}


# 历史项目配件相关端点
@router.get("/historical-project/{historical_project_id}", response_model=List[ProjectPartRead])
async def list_historical_project_parts(
    historical_project_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
):
    """获取历史项目的配件清单"""
    _check_historical_project_permission(session, historical_project_id, current_user)
    statement = select(ProjectPart).where(ProjectPart.historical_project_id == historical_project_id).order_by(ProjectPart.id)
    parts = session.exec(statement).all()
    return [ProjectPartRead.model_validate(p) for p in parts]


@router.post("/historical-project/{historical_project_id}", response_model=List[ProjectPartRead])
async def create_historical_project_parts(
    historical_project_id: int,
    parts_data: List[ProjectPartCreate],
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
):
    """批量创建历史项目配件条目"""
    _check_historical_project_permission(session, historical_project_id, current_user)
    created_parts: List[ProjectPart] = []
    for item in parts_data:
        part_data = item.model_dump()
        part_data["historical_project_id"] = historical_project_id
        part = ProjectPart(**part_data)
        session.add(part)
        created_parts.append(part)
    session.commit()
    for part in created_parts:
        session.refresh(part)
    return [ProjectPartRead.model_validate(p) for p in created_parts]


