"""
项目日志API路由
"""
from fastapi import APIRouter, Depends, Query, HTTPException, status, Body
from sqlmodel import Session
from typing import List, Optional
from pydantic import BaseModel
from app.core.database import get_session
from app.core.dependencies import get_current_active_user
from app.models.user import User
from app.services.project_log_service import ProjectLogService

router = APIRouter()


class SnapshotCreate(BaseModel):
    """项目快照创建模型"""
    project_id: int
    snapshot_note: Optional[str] = None
    photo_urls: Optional[List[str]] = None
    attachment_ids: Optional[List[int]] = None


class StepUpdateLog(BaseModel):
    """步骤更新日志模型"""
    project_id: int
    step_id: int
    old_status: str
    new_status: str
    update_note: Optional[str] = None
    attachment_ids: Optional[List[int]] = None


@router.get("/project/{project_id}")
async def get_project_logs(
    project_id: int,
    limit: int = Query(50, description="返回数量限制"),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """获取项目的日志列表"""
    # 检查权限
    from app.repositories.project_repository import ProjectRepository
    project_repo = ProjectRepository(session)
    project = project_repo.get_by_id(project_id)
    
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="项目不存在")
    
    if current_user.role != "admin" and project.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权访问该项目")
    
    log_service = ProjectLogService(session)
    logs = log_service.get_project_logs(project_id, limit)
    return logs


@router.get("/historical-project/{historical_project_id}")
async def get_historical_project_logs(
    historical_project_id: int,
    limit: int = Query(50, description="返回数量限制"),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """获取历史项目的日志列表"""
    # 检查功能是否启用
    from app.repositories.system_settings_repository import SystemSettingsRepository
    settings_repo = SystemSettingsRepository(session)
    if not settings_repo.is_feature_enabled("enable_log_management"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="历史项目日志管理功能已禁用")
    
    # 检查权限
    from app.repositories.historical_project_repository import HistoricalProjectRepository
    historical_project_repo = HistoricalProjectRepository(session)
    historical_project = historical_project_repo.get_by_id(historical_project_id)
    
    if not historical_project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="历史项目不存在")
    
    if current_user.role != "admin" and historical_project.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权访问该历史项目")
    
    from app.repositories.project_log_repository import ProjectLogRepository
    log_repo = ProjectLogRepository(session)
    logs = log_repo.list_by_historical_project(historical_project_id, limit)
    
    # 获取用户信息
    from app.repositories.user_repository import UserRepository
    user_repo = UserRepository(session)
    result = []
    for log in logs:
        user_name = None
        if log.user_id:
            user = user_repo.get_by_id(log.user_id)
            user_name = user.username if user else None
        
        result.append({
            "id": log.id,
            "project_id": log.project_id,
            "historical_project_id": log.historical_project_id,
            "action": log.action.value if hasattr(log.action, 'value') else str(log.action),
            "description": log.description,
            "details": log.details,
            "user_id": log.user_id,
            "user_name": user_name,
            "created_at": log.created_at
        })
    
    return result


@router.post("/step-update")
async def log_step_update(
    data: StepUpdateLog = Body(...),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """记录步骤更新日志"""
    # 检查权限
    from app.repositories.project_repository import ProjectRepository
    from app.repositories.step_repository import StepRepository
    project_repo = ProjectRepository(session)
    step_repo = StepRepository(session)
    
    project = project_repo.get_by_id(data.project_id)
    step = step_repo.get_by_id(data.step_id)
    
    if not project or not step:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="项目或步骤不存在")
    
    if current_user.role != "admin" and project.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权访问该项目")
    
    # 区分照片和文件：从附件中识别图片类型
    photo_ids = []
    file_attachment_ids = []
    if data.attachment_ids:
        from app.services.attachment_service import AttachmentService
        attachment_service = AttachmentService(session)
        for att_id in data.attachment_ids:
            try:
                attachment = attachment_service.get_attachment_by_id(
                    attachment_id=att_id,
                    current_user_id=current_user.id,
                    is_admin=(current_user.role == "admin")
                )
                # 检查文件类型是否为图片
                if attachment.file_name.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp')):
                    photo_ids.append(att_id)
                else:
                    file_attachment_ids.append(att_id)
            except:
                # 如果获取失败，默认作为文件处理
                file_attachment_ids.append(att_id)
    
    log_service = ProjectLogService(session)
    log_service.log_step_updated(
        project_id=data.project_id,
        step_name=step.name,
        old_status=data.old_status,
        new_status=data.new_status,
        update_note=data.update_note,
        attachment_ids=file_attachment_ids,
        photo_ids=photo_ids,
        user_id=current_user.id
    )
    return {"message": "日志记录成功"}


@router.post("/snapshot")
async def create_snapshot(
    data: SnapshotCreate = Body(...),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """创建项目快照"""
    # 检查权限
    from app.repositories.project_repository import ProjectRepository
    project_repo = ProjectRepository(session)
    project = project_repo.get_by_id(data.project_id)
    
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="项目不存在")
    
    if current_user.role != "admin" and project.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权访问该项目")
    
    log_service = ProjectLogService(session)
    log_service.log_project_snapshot(
        project_id=data.project_id,
        snapshot_note=data.snapshot_note,
        photo_urls=data.photo_urls or [],
        attachment_ids=data.attachment_ids or [],
        user_id=current_user.id
    )
    return {"message": "快照创建成功"}


@router.post("/")
async def create_log(
    data: dict = Body(...),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """创建项目日志"""
    from app.repositories.project_repository import ProjectRepository
    from app.models.project_log import LogAction
    
    project_id = data.get("project_id")
    action_str = data.get("action")
    description = data.get("description")
    details_str = data.get("details")
    
    if not project_id or not action_str or not description:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="缺少必要参数")
    
    # 检查权限
    project_repo = ProjectRepository(session)
    project = project_repo.get_by_id(project_id)
    
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="项目不存在")
    
    if current_user.role != "admin" and project.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权访问该项目")
    
    # 解析 action
    try:
        action = LogAction(action_str)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"无效的操作类型: {action_str}")
    
    # 解析 details
    details = None
    if details_str:
        try:
            import json
            details = json.loads(details_str) if isinstance(details_str, str) else details_str
        except:
            pass
    
    log_service = ProjectLogService(session)
    log = log_service.create_log(
        project_id=project_id,
        action=action,
        description=description,
        details=details,
        user_id=current_user.id
    )
    return log


@router.delete("/{log_id}")
async def delete_log(
    log_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """删除项目日志"""
    log_service = ProjectLogService(session)
    
    # 获取日志
    from app.repositories.project_log_repository import ProjectLogRepository
    log_repo = ProjectLogRepository(session)
    log = log_repo.get_by_id(log_id)
    
    if not log:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="日志不存在")
    
    # 检查权限：检查日志所属的项目
    from app.repositories.project_repository import ProjectRepository
    project_repo = ProjectRepository(session)
    project = project_repo.get_by_id(log.project_id)
    
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="项目不存在")
    
    if current_user.role != "admin" and project.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权删除该日志")
    
    # 删除日志
    log_repo.delete(log)
    return {"message": "日志删除成功"}

