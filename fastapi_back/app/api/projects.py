"""
项目管理API路由层（重构后）
"""
import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlmodel import Session
from app.core.database import get_session
from app.core.dependencies import get_current_active_user
from app.services.project_service import ProjectService
from app.models.user import User
from app.models.project import (
    ProjectCreate, ProjectReadWithRelations, ProjectUpdate,
    ProjectStepCreate, ProjectStepRead, ProjectStepUpdate
)

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/", response_model=List[ProjectReadWithRelations])
async def list_projects(
    skip: int = Query(0, ge=0),
    limit: int = Query(1000, ge=1, le=1000),  # 资源管理页面需要加载更多项目
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
    
    try:
        return project_service.list_projects(
            user_id=user_id,
            platform_id=platform_id,
            status=status,
            tag_ids=tag_id_list,
            skip=skip,
            limit=limit
    )
    except Exception as e:
        logger.error(f"Error in list_projects API: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.post("/", response_model=ProjectReadWithRelations)
async def create_project(
    project_data: ProjectCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """创建新项目"""
    # 设置用户ID（如果不是管理员，强制使用当前用户ID）
    if current_user.role != "admin":
        project_data.user_id = current_user.id
    
    project_service = ProjectService(session)
    return project_service.create_project(project_data, project_data.user_id)


@router.get("/{project_id}", response_model=ProjectReadWithRelations)
async def get_project(
    project_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """获取项目详情"""
    project_service = ProjectService(session)
    project = project_service.get_project_with_relations(project_id)
    
    # 权限检查
    if current_user.role != "admin" and project.user_id != current_user.id:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    return project


@router.put("/{project_id}", response_model=ProjectReadWithRelations)
async def update_project(
    project_id: int,
    project_data: ProjectUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """更新项目信息"""
    project_service = ProjectService(session)
    return project_service.update_project(
        project_id=project_id,
        project_data=project_data,
        current_user_id=current_user.id,
        is_admin=(current_user.role == "admin")
    )


@router.post("/{project_id}/settle", response_model=ProjectReadWithRelations)
async def settle_project(
    project_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """项目结账"""
    project_service = ProjectService(session)
    return project_service.settle_project(
        project_id=project_id,
        current_user_id=current_user.id,
        is_admin=(current_user.role == "admin")
    )


@router.delete("/{project_id}")
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
        is_admin=(current_user.role == "admin")
    )
    return {"message": "Project deleted successfully"}


# 项目步骤相关API
@router.post("/{project_id}/steps", response_model=ProjectStepRead)
async def create_step(
    project_id: int,
    step_data: ProjectStepCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """为项目添加新步骤"""
    project_service = ProjectService(session)
    return project_service.create_step(
        project_id=project_id,
        step_data=step_data,
        current_user_id=current_user.id,
        is_admin=(current_user.role == "admin")
    )


@router.put("/steps/{step_id}", response_model=ProjectStepRead)
async def update_step(
    step_id: int,
    step_data: ProjectStepUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """更新步骤信息"""
    project_service = ProjectService(session)
    
    # 获取更新前的步骤信息
    from app.repositories.step_repository import StepRepository
    step_repo = StepRepository(session)
    old_step = step_repo.get_by_id(step_id)
    old_status = old_step.status if old_step else None
    
    # 更新步骤
    updated_step = project_service.update_step(
        step_id=step_id,
        step_data=step_data,
        current_user_id=current_user.id,
        is_admin=(current_user.role == "admin")
    )
    
    # 如果状态发生变化，记录日志（注意：这里不记录附件，因为附件是在前端上传后通过其他方式关联的）
    if old_step and step_data.status and old_status != step_data.status:
        from app.services.project_log_service import ProjectLogService
        log_service = ProjectLogService(session)
        log_service.log_step_updated(
            project_id=old_step.project_id,
            step_name=old_step.name,
            old_status=old_status,
            new_status=step_data.status,
            update_note=None,  # 说明和附件在前端处理
            attachment_ids=None,
            user_id=current_user.id
        )
    
    # 检查项目是否自动结账（在update_step中已处理，这里确保状态同步）
    project = project_service.get_project_with_relations(old_step.project_id)
    
    return updated_step


@router.delete("/steps/{step_id}")
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
        is_admin=(current_user.role == "admin")
    )
    return {"message": "Step deleted successfully"}


@router.post("/steps/{step_id}/toggle-todo", response_model=ProjectStepRead)
async def toggle_step_todo(
    step_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """切换步骤的Todo状态"""
    project_service = ProjectService(session)
    return project_service.toggle_step_todo(
        step_id=step_id,
        current_user_id=current_user.id,
        is_admin=(current_user.role == "admin")
    )


@router.post("/steps/reorder")
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
        is_admin=(current_user.role == "admin")
    )
    return {"message": "Steps reordered successfully"}
