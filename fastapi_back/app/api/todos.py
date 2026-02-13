"""
待办管理API路由
"""
from fastapi import APIRouter, Depends, Query
from sqlmodel import Session
from typing import List, Optional
from datetime import datetime, date, timezone, timedelta
from app.core.database import get_session
from app.core.dependencies import get_current_active_user
from app.models.user import User
from app.repositories.todo_repository import TodoRepository
from app.repositories.step_repository import StepRepository
from app.services.project_log_service import ProjectLogService
from app.schemas.todo import TodoCreate, TodoUpdate, TodoReadWithRelations
from app.api.responses import ApiResponse, success
import json

router = APIRouter()


def _today_local() -> date:
    """获取本地（北京时间，UTC+8）的今天日期，避免 UTC 跨天问题"""
    return datetime.now(timezone.utc).astimezone(timezone(timedelta(hours=8))).date()


@router.get("/", response_model=ApiResponse[List[TodoReadWithRelations]])
async def get_todos(
    target_date: Optional[date] = Query(None, description="目标日期，默认为今天"),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """获取指定日期的待办列表"""
    todo_repo = TodoRepository(session)
    step_repo = StepRepository(session)

    user_id = None if current_user.role == "admin" else current_user.id
    target = target_date or _today_local()
    todos = todo_repo.list_by_date(target, user_id)

    result = []
    for todo in todos:
        try:
            step_ids = json.loads(todo.step_ids)
            steps = [step_repo.get_by_id(sid) for sid in step_ids]
            step_names = [s.name for s in steps if s]

            # 获取项目信息（支持历史项目）
            project_title = "未知项目"
            if todo.project_id:
                from app.repositories.project_repository import ProjectRepository
                project_repo = ProjectRepository(session)
                project = project_repo.get_by_id(todo.project_id)
                if project:
                    project_title = project.title
            elif todo.historical_project_id:
                from app.repositories.historical_project_repository import HistoricalProjectRepository
                historical_project_repo = HistoricalProjectRepository(session)
                historical_project = historical_project_repo.get_by_id(todo.historical_project_id)
                if historical_project:
                    project_title = f"[历史] {historical_project.title}"

            todo_dict = {
                "id": todo.id,
                "project_id": todo.project_id,
                "historical_project_id": todo.historical_project_id,
                "description": todo.description,
                "step_ids": step_ids,
                "completion_note": todo.completion_note,
                "is_completed": todo.is_completed,
                "target_date": todo.target_date,
                "created_at": todo.created_at,
                "updated_at": todo.updated_at,
                "project_title": project_title,
                "step_names": step_names
            }
            result.append(TodoReadWithRelations(**todo_dict))
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error processing todo {todo.id}: {str(e)}", exc_info=True)
            continue

    return success(result)


@router.post("/", response_model=ApiResponse[TodoReadWithRelations])
async def create_todo(
    todo_data: TodoCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """创建待办（支持历史项目）"""
    todo_repo = TodoRepository(session)
    step_repo = StepRepository(session)

    # 检查权限（支持历史项目）
    project = None
    historical_project = None

    if todo_data.project_id:
        from app.repositories.project_repository import ProjectRepository
        project_repo = ProjectRepository(session)
        project = project_repo.get_by_id(todo_data.project_id)
        if not project:
            from fastapi import HTTPException, status
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="项目不存在")
        if current_user.role != "admin" and project.user_id != current_user.id:
            from fastapi import HTTPException, status
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权访问该项目")
    elif todo_data.historical_project_id:
        from app.repositories.historical_project_repository import HistoricalProjectRepository
        from app.repositories.system_settings_repository import SystemSettingsRepository
        historical_project_repo = HistoricalProjectRepository(session)
        settings_repo = SystemSettingsRepository(session)

        # 检查功能是否启用
        if not settings_repo.is_feature_enabled("enable_todo_management"):
            from fastapi import HTTPException, status
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="历史项目待办管理功能已禁用")

        historical_project = historical_project_repo.get_by_id(todo_data.historical_project_id)
        if not historical_project:
            from fastapi import HTTPException, status
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="历史项目不存在")
        if current_user.role != "admin" and historical_project.user_id != current_user.id:
            from fastapi import HTTPException, status
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权访问该历史项目")
    else:
        from fastapi import HTTPException, status
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="必须指定项目ID或历史项目ID")

    # 创建待办
    todo = todo_repo.create(todo_data)

    # 将相关步骤标记为待办，并将状态改为"进行中"（仅对项目有效，历史项目没有步骤）
    step_names = []
    if todo.project_id:
        for step_id in todo_data.step_ids:
            step = step_repo.get_by_id(step_id)
            if step:
                step.is_todo = True
                # 如果步骤状态是"待开始"，则改为"进行中"
                if step.status == "待开始":
                    step.status = "进行中"
                session.add(step)
                step_names.append(step.name)
    session.commit()

    # 记录日志
    log_service = ProjectLogService(session)
    if todo.project_id:
        log_service.log_todo_created(
            project_id=todo.project_id,
            todo_description=todo.description,
            step_names=step_names,
            user_id=current_user.id
        )
    elif todo.historical_project_id:
        # 历史项目的日志记录
        from app.models.project_log import LogAction
        from app.repositories.project_log_repository import ProjectLogRepository
        log_repo = ProjectLogRepository(session)
        log_repo.create({
            "historical_project_id": todo.historical_project_id,
            "action": LogAction.TODO_CREATED,
            "description": f"创建待办：{todo.description}",
            "user_id": current_user.id
        })

    # 构建返回数据
    step_ids = json.loads(todo.step_ids)
    project_title = project.title if project else (historical_project.title if historical_project else "未知项目")

    todo_read = TodoReadWithRelations(
        id=todo.id,
        project_id=todo.project_id,
        historical_project_id=todo.historical_project_id,
        description=todo.description,
        step_ids=step_ids,
        completion_note=todo.completion_note,
        is_completed=todo.is_completed,
        target_date=todo.target_date,
        created_at=todo.created_at,
        updated_at=todo.updated_at,
        project_title=project_title,
        step_names=step_names
    )
    return success(todo_read, msg="待办创建成功")


@router.put("/{todo_id}", response_model=ApiResponse[TodoReadWithRelations])
async def update_todo(
    todo_id: int,
    todo_data: TodoUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """更新待办"""
    todo_repo = TodoRepository(session)
    step_repo = StepRepository(session)

    todo = todo_repo.get_by_id(todo_id)
    if not todo:
        from fastapi import HTTPException, status
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="待办不存在")

    # 检查权限（支持历史项目）
    project = None
    historical_project = None

    if todo.project_id:
        from app.repositories.project_repository import ProjectRepository
        project_repo = ProjectRepository(session)
        project = project_repo.get_by_id(todo.project_id)
        if not project:
            from fastapi import HTTPException, status
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="项目不存在")
        if current_user.role != "admin" and project.user_id != current_user.id:
            from fastapi import HTTPException, status
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权访问该待办")
    elif todo.historical_project_id:
        from app.repositories.historical_project_repository import HistoricalProjectRepository
        historical_project_repo = HistoricalProjectRepository(session)
        historical_project = historical_project_repo.get_by_id(todo.historical_project_id)
        if not historical_project:
            from fastapi import HTTPException, status
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="历史项目不存在")
        if current_user.role != "admin" and historical_project.user_id != current_user.id:
            from fastapi import HTTPException, status
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权访问该待办")

    # 记录完成前的信息
    was_completed = todo.is_completed
    step_ids = json.loads(todo.step_ids)
    step_names = []
    if todo.project_id:
        steps = [step_repo.get_by_id(sid) for sid in step_ids]
        step_names = [s.name for s in steps if s]

    # 更新待办
    todo = todo_repo.update(todo, todo_data)

    # 如果标记为完成，更新步骤状态并记录日志（仅对项目有效）
    if todo_data.is_completed and not was_completed:
        if todo.project_id:
            for step_id in step_ids:
                step = step_repo.get_by_id(step_id)
                if step:
                    step.status = "已完成"
                    step.is_todo = False
                    session.add(step)
        session.commit()

        # 记录完成日志
        # 区分照片和文件：从附件中识别图片类型
        photo_ids = []
        file_attachment_ids = []
        if todo_data.attachment_ids:
            from app.services.attachment_service import AttachmentService
            attachment_service = AttachmentService(session)
            for att_id in todo_data.attachment_ids:
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
        if todo.project_id:
            log_service.log_todo_completed(
                project_id=todo.project_id,
                todo_description=todo.description,
                completion_note=todo.completion_note,
                step_names=step_names,
                attachment_ids=file_attachment_ids,
                photo_ids=photo_ids,
                user_id=current_user.id
            )
        elif todo.historical_project_id:
            # 历史项目的日志记录
            from app.models.project_log import LogAction
            from app.repositories.project_log_repository import ProjectLogRepository
            log_repo = ProjectLogRepository(session)
            log_repo.create({
                "historical_project_id": todo.historical_project_id,
                "action": LogAction.TODO_COMPLETED,
                "description": f"完成待办：{todo.description}",
                "user_id": current_user.id
            })

    project_title = project.title if project else (historical_project.title if historical_project else "未知项目")

    todo_read = TodoReadWithRelations(
        id=todo.id,
        project_id=todo.project_id,
        historical_project_id=todo.historical_project_id,
        description=todo.description,
        step_ids=step_ids,
        completion_note=todo.completion_note,
        is_completed=todo.is_completed,
        target_date=todo.target_date,
        created_at=todo.created_at,
        updated_at=todo.updated_at,
        project_title=project_title,
        step_names=step_names
    )
    return success(todo_read, msg="待办更新成功")


@router.delete("/{todo_id}", response_model=ApiResponse[None])
async def delete_todo(
    todo_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """删除待办"""
    todo_repo = TodoRepository(session)

    todo = todo_repo.get_by_id(todo_id)
    if not todo:
        from fastapi import HTTPException, status
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="待办不存在")

    # 检查权限（支持历史项目）
    if todo.project_id:
        from app.repositories.project_repository import ProjectRepository
        project_repo = ProjectRepository(session)
        project = project_repo.get_by_id(todo.project_id)
        if not project:
            from fastapi import HTTPException, status
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="项目不存在")
        if current_user.role != "admin" and project.user_id != current_user.id:
            from fastapi import HTTPException, status
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权访问该待办")
    elif todo.historical_project_id:
        from app.repositories.historical_project_repository import HistoricalProjectRepository
        historical_project_repo = HistoricalProjectRepository(session)
        historical_project = historical_project_repo.get_by_id(todo.historical_project_id)
        if not historical_project:
            from fastapi import HTTPException, status
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="历史项目不存在")
        if current_user.role != "admin" and historical_project.user_id != current_user.id:
            from fastapi import HTTPException, status
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权访问该待办")

    # 记录删除日志
    log_service = ProjectLogService(session)
    if todo.project_id:
        log_service.log_todo_deleted(
            project_id=todo.project_id,
            todo_description=todo.description,
            user_id=current_user.id
        )
    elif todo.historical_project_id:
        # 历史项目的日志记录
        from app.models.project_log import LogAction
        from app.repositories.project_log_repository import ProjectLogRepository
        log_repo = ProjectLogRepository(session)
        log_repo.create({
            "historical_project_id": todo.historical_project_id,
            "action": LogAction.TODO_DELETED,
            "description": f"删除待办：{todo.description}",
            "user_id": current_user.id
        })

    todo_repo.delete(todo)
    return success(msg="待办已删除")


@router.get("/calendar", response_model=ApiResponse[List[dict]])
async def get_todo_calendar(
    year: int = Query(None, description="年份"),
    month: int = Query(None, description="月份"),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """获取待办日历数据，包含每日收入"""
    todo_repo = TodoRepository(session)

    if year is None or month is None:
        # 使用本地时区（UTC+8）的今天日期
        today = _today_local()
        year = today.year
        month = today.month

    from datetime import timedelta
    start_date = date(year, month, 1)
    if month == 12:
        end_date = date(year + 1, 1, 1) - timedelta(days=1)
    else:
        end_date = date(year, month + 1, 1) - timedelta(days=1)

    user_id = None if current_user.role == "admin" else current_user.id

    # 获取该月的所有已结账项目，按结账日期分组
    from app.models.project import Project
    from sqlmodel import select

    # 查询该月内结账的项目（通过updated_at判断，因为结账时会更新updated_at）
    projects_query = select(Project).where(
        Project.is_paid == True
    )
    if user_id is not None:
        projects_query = projects_query.where(Project.user_id == user_id)

    all_paid_projects = session.exec(projects_query).all()

    # 按日期分组收入
    daily_revenue: dict[str, float] = {}
    for project in all_paid_projects:
        # 使用updated_at的日期部分作为结账日期
        settle_date = project.updated_at.date() if hasattr(project.updated_at, 'date') else project.updated_at
        if isinstance(settle_date, datetime):
            settle_date = settle_date.date()

        if start_date <= settle_date <= end_date:
            date_str = settle_date.isoformat()
            daily_revenue[date_str] = daily_revenue.get(date_str, 0) + (project.actual_income or 0)

    calendar_data = []
    current_date = start_date
    while current_date <= end_date:
        todos = todo_repo.list_by_date(current_date, user_id)
        todo_count = len([t for t in todos if not t.is_completed])
        completed_count = len([t for t in todos if t.is_completed])
        date_str = current_date.isoformat()
        revenue = daily_revenue.get(date_str, 0.0)

        calendar_data.append({
            "date": date_str,
            "todo_count": todo_count,
            "completed_count": completed_count,
            "revenue": revenue
        })
        current_date += timedelta(days=1)

    return success(calendar_data)
