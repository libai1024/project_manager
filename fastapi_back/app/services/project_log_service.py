"""
项目日志服务
"""
from sqlmodel import Session
from typing import List, Optional
import json
from app.repositories.project_log_repository import ProjectLogRepository
from app.models.project_log import ProjectLogCreate, ProjectLogRead, ProjectLogReadWithRelations, LogAction


class ProjectLogService:
    def __init__(self, session: Session):
        self.session = session
        self.log_repo = ProjectLogRepository(session)
    
    def create_log(
        self,
        project_id: int,
        action: LogAction,
        description: str,
        details: Optional[dict] = None,
        user_id: Optional[int] = None
    ) -> ProjectLogRead:
        """创建日志"""
        log_data = ProjectLogCreate(
            project_id=project_id,
            action=action,
            description=description,
            details=json.dumps(details, ensure_ascii=False) if details else None,
            user_id=user_id
        )
        log = self.log_repo.create(log_data)
        return ProjectLogRead.model_validate(log)
    
    def get_project_logs(self, project_id: int, limit: Optional[int] = None) -> List[ProjectLogReadWithRelations]:
        """获取项目的日志列表"""
        logs = self.log_repo.list_by_project(project_id, limit)
        result = []
        for log in logs:
            log_dict = ProjectLogReadWithRelations.model_validate(log)
            if log.user_id:
                from app.repositories.user_repository import UserRepository
                user_repo = UserRepository(self.session)
                user = user_repo.get_by_id(log.user_id)
                if user:
                    log_dict.user_name = user.username
            result.append(log_dict)
        return result
    
    def log_todo_created(self, project_id: int, todo_description: str, step_names: List[str], user_id: Optional[int] = None):
        """记录待办创建日志"""
        description = f"创建待办：{todo_description}"
        details = {
            "step_names": step_names
        }
        return self.create_log(project_id, LogAction.TODO_CREATED, description, details, user_id)
    
    def log_todo_completed(self, project_id: int, todo_description: str, completion_note: Optional[str], step_names: List[str], attachment_ids: Optional[List[int]] = None, photo_ids: Optional[List[int]] = None, user_id: Optional[int] = None):
        """记录待办完成日志"""
        description = f"完成待办：{todo_description}"
        # 将照片ID转换为字符串列表（与项目快照保持一致）
        photo_urls = [str(pid) for pid in (photo_ids or [])]
        details = {
            "step_names": step_names,
            "completion_note": completion_note,
            "attachment_ids": attachment_ids or [],
            "photos": photo_urls
        }
        return self.create_log(project_id, LogAction.TODO_COMPLETED, description, details, user_id)
    
    def log_todo_deleted(self, project_id: int, todo_description: str, user_id: Optional[int] = None):
        """记录待办删除日志"""
        description = f"删除待办：{todo_description}"
        return self.create_log(project_id, LogAction.TODO_DELETED, description, None, user_id)
    
    def log_step_updated(self, project_id: int, step_name: str, old_status: str, new_status: str, update_note: Optional[str] = None, attachment_ids: Optional[List[int]] = None, photo_ids: Optional[List[int]] = None, user_id: Optional[int] = None):
        """记录步骤更新日志"""
        description = f"更新步骤：{step_name} ({old_status} → {new_status})"
        # 将照片ID转换为字符串列表（与项目快照保持一致）
        photo_urls = [str(pid) for pid in (photo_ids or [])]
        details = {
            "step_name": step_name,
            "old_status": old_status,
            "new_status": new_status,
            "update_note": update_note,
            "attachment_ids": attachment_ids or [],
            "photos": photo_urls
        }
        return self.create_log(project_id, LogAction.STEP_UPDATED, description, details, user_id)
    
    def log_project_snapshot(self, project_id: int, snapshot_note: Optional[str] = None, photo_urls: Optional[List[str]] = None, attachment_ids: Optional[List[int]] = None, user_id: Optional[int] = None):
        """记录项目快照日志"""
        description = f"项目快照：{snapshot_note or '添加了项目快照'}"
        details = {
            "snapshot_note": snapshot_note,
            "photos": photo_urls or [],
            "attachment_ids": attachment_ids or []
        }
        return self.create_log(project_id, LogAction.PROJECT_SNAPSHOT, description, details, user_id)

    def log_project_created(self, project_id: int, project_title: str, attachment_ids: Optional[List[int]] = None, photo_ids: Optional[List[int]] = None, user_id: Optional[int] = None):
        """记录项目创建日志"""
        description = f"创建项目：{project_title}"
        # 将照片ID转换为字符串列表（与项目快照保持一致）
        photo_urls = [str(pid) for pid in (photo_ids or [])]
        details = {
            "attachment_ids": attachment_ids or [],
            "photos": photo_urls
        }
        return self.create_log(project_id, LogAction.PROJECT_CREATED, description, details, user_id)

