"""
项目管理API路由层（重构后）

使用统一响应格式和新的Schema导入。
API层只负责请求处理，业务逻辑在Service层。
"""
import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlmodel import Session

from app.core.database import get_session
from app.core.dependencies import get_current_active_user
from app.services.project_service import ProjectService
from app.models.user import User
from app.schemas.project import (
    ProjectCreate, ProjectUpdate, ProjectReadWithRelations,
    ProjectStepCreate, ProjectStepRead, ProjectStepUpdate
)
from app.api.responses import ApiResponse, success

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/", response_model=ApiResponse[List[ProjectReadWithRelations]])
async def list_projects(
    skip: int = Query(0, ge=0),
    limit: int = Query(1000, ge=1, le=1000),
    user_id: Optional[int] = None,
    platform_id: Optional[int] = None,
    status: Optional[str] = None,
    tag_ids: Optional[str] = Query(None, description="标签ID列表，用逗号分隔"),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """获取项目列表"""
    project_service = ProjectService(session)

    # 如果不是管理员，只能查看自己的项目
    if current_user.role != "admin":
        user_id = current_user.id

    # 解析标签ID列表
    tag_id_list = None
    if tag_ids:
        try:
            tag_id_list = [int(tid.strip()) for tid in tag_ids.split(',') if tid.strip()]
        except ValueError:
            tag_id_list = None

    projects = project_service.list_projects(
        user_id=user_id,
        platform_id=platform_id,
        status=status,
        tag_ids=tag_id_list,
        skip=skip,
        limit=limit
    )
    return success(projects)


@router.post("/", response_model=ApiResponse[ProjectReadWithRelations])
async def create_project(
    project_data: ProjectCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """创建新项目"""
    # 设置用户ID（如果不是管理员，强制使用当前用户ID）
    if current_user.role != "admin" or not project_data.user_id:
        project_data.user_id = current_user.id

    project_service = ProjectService(session)
    project = project_service.create_project(project_data, project_data.user_id)
    return success(project, msg="项目创建成功")


@router.get("/{project_id}", response_model=ApiResponse[ProjectReadWithRelations])
async def get_project(
    project_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """获取项目详情"""
    project_service = ProjectService(session)
    project = project_service.get_project_with_relations(project_id)
    return success(project)


@router.put("/{project_id}", response_model=ApiResponse[ProjectReadWithRelations])
async def update_project(
    project_id: int,
    project_data: ProjectUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """更新项目信息"""
    project_service = ProjectService(session)
    project = project_service.update_project(
        project_id=project_id,
        project_data=project_data,
        current_user_id=current_user.id,
        admin=(current_user.role == "admin")
    )
    return success(project, msg="项目更新成功")


@router.post("/{project_id}/settle", response_model=ApiResponse[ProjectReadWithRelations])
async def settle_project(
    project_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """项目结账"""
    project_service = ProjectService(session)
    project = project_service.settle_project(
        project_id=project_id,
        current_user_id=current_user.id,
        admin=(current_user.role == "admin")
    )
    return success(project, msg="项目结账成功")


@router.delete("/{project_id}", response_model=ApiResponse[None])
async def delete_project(
    project_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """删除项目"""
    project_service = ProjectService(session)
    project_service.delete_project(
        project_id=project_id,
        current_user_id=current_user.id,
        admin=(current_user.role == "admin")
    )
    return success(msg="项目删除成功")


# ========== 项目步骤相关API ==========

@router.post("/{project_id}/steps", response_model=ApiResponse[ProjectStepRead])
async def create_step(
    project_id: int,
    step_data: ProjectStepCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """为项目添加新步骤"""
    project_service = ProjectService(session)
    step = project_service.create_step(
        project_id=project_id,
        step_data=step_data,
        current_user_id=current_user.id,
        admin=(current_user.role == "admin")
    )
    return success(step, msg="步骤创建成功")


@router.put("/steps/{step_id}", response_model=ApiResponse[ProjectStepRead])
async def update_step(
    step_id: int,
    step_data: ProjectStepUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """更新步骤信息"""
    project_service = ProjectService(session)

    # 获取更新前的步骤信息（用于日志记录）
    from app.repositories.step_repository import StepRepository
    step_repo = StepRepository(session)
    old_step = step_repo.get_by_id(step_id)
    old_status = old_step.status if old_step else None

    # 更新步骤
    updated_step = project_service.update_step(
        step_id=step_id,
        step_data=step_data,
        current_user_id=current_user.id,
        admin=(current_user.role == "admin")
    )

    # 如果状态发生变化，记录日志
    if old_step and step_data.status and old_status != step_data.status:
        from app.services.project_log_service import ProjectLogService
        log_service = ProjectLogService(session)
        log_service.log_step_updated(
            project_id=old_step.project_id,
            step_name=old_step.name,
            old_status=old_status,
            new_status=step_data.status,
            update_note=None,
            attachment_ids=None,
            user_id=current_user.id
        )

    return success(updated_step, msg="步骤更新成功")


@router.delete("/steps/{step_id}", response_model=ApiResponse[None])
async def delete_step(
    step_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """删除步骤"""
    project_service = ProjectService(session)
    project_service.delete_step(
        step_id=step_id,
        current_user_id=current_user.id,
        admin=(current_user.role == "admin")
    )
    return success(msg="步骤删除成功")


@router.post("/steps/{step_id}/toggle-todo", response_model=ApiResponse[ProjectStepRead])
async def toggle_step_todo(
    step_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """切换步骤的Todo状态"""
    project_service = ProjectService(session)
    step = project_service.toggle_step_todo(
        step_id=step_id,
        current_user_id=current_user.id,
        admin=(current_user.role == "admin")
    )
    return success(step)


@router.post("/steps/reorder", response_model=ApiResponse[None])
async def reorder_steps(
    step_orders: List[dict],
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """重新排序步骤"""
    project_service = ProjectService(session)
    project_service.reorder_steps(
        step_orders=step_orders,
        current_user_id=current_user.id,
        admin=(current_user.role == "admin")
    )
    return success(msg="步骤排序成功")
