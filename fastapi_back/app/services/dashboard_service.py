"""
Dashboard服务层
"""
from typing import List, Dict, Optional
from datetime import datetime
from sqlmodel import Session
from app.repositories.project_repository import ProjectRepository
from app.repositories.step_repository import StepRepository
from app.repositories.platform_repository import PlatformRepository
from app.models.project import ProjectStep, StepStatus
from app.models.platform import Platform
from pydantic import BaseModel


class DashboardStats(BaseModel):
    today_todos: List[dict]  # 使用dict以支持灵活的字段
    total_revenue: float
    platform_revenue: Dict[str, float]
    pending_projects_count: int
    in_progress_steps_count: int


class DashboardService:
    """Dashboard服务层"""
    
    def __init__(self, session: Session):
        self.session = session
        self.project_repo = ProjectRepository(session)
        self.step_repo = StepRepository(session)
        self.platform_repo = PlatformRepository(session)
    
    def get_dashboard_stats(self, user_id: Optional[int], is_admin: bool) -> DashboardStats:
        """获取Dashboard统计数据"""
        # 获取项目列表
        if is_admin:
            projects = self.project_repo.list()
        else:
            projects = self.project_repo.list_by_user(user_id)
        
        project_ids = [p.id for p in projects]
        
        # 获取今日Todo列表（从新的待办表）
        from app.repositories.todo_repository import TodoRepository
        from datetime import date
        import json
        
        todo_repo = TodoRepository(self.session)
        todos = todo_repo.list_by_date(date.today(), user_id if not is_admin else None)
        
        today_todos = []
        for todo in todos:
            # 显示所有待办，包括已完成的
            step_ids = json.loads(todo.step_ids)
            steps = [self.step_repo.get_by_id(sid) for sid in step_ids]
            step_names = [s.name for s in steps if s]
            project = self.project_repo.get_by_id(todo.project_id)
            
            # 返回完整的待办数据结构，匹配前端期望
            todo_dict = {
                "id": todo.id,
                "project_id": todo.project_id,
                "project_title": project.title if project else "未知项目",
                "description": todo.description,
                "step_ids": step_ids,
                "step_names": step_names,
                "completion_note": todo.completion_note,
                "is_completed": todo.is_completed,
                "student_name": project.student_name or "" if project else ""
            }
            
            # 处理日期字段
            if todo.target_date:
                todo_dict["target_date"] = todo.target_date.isoformat()
            if todo.created_at:
                todo_dict["created_at"] = todo.created_at.isoformat()
            if todo.updated_at:
                todo_dict["updated_at"] = todo.updated_at.isoformat()
            
            today_todos.append(todo_dict)
        
        # 计算总收益（使用实际收入字段）
        total_revenue = sum(
            p.actual_income for p in projects if p.is_paid and p.actual_income > 0
        )
        
        # 按平台统计收益（使用实际收入字段）
        platform_revenue: Dict[str, float] = {}
        for project in projects:
            if project.is_paid and project.actual_income > 0:
                platform = self.platform_repo.get_by_id(project.platform_id)
                platform_name = platform.name if platform else "未知平台"
                platform_revenue[platform_name] = platform_revenue.get(platform_name, 0) + project.actual_income
        
        # 待处理项目数（状态不是"已结账"的项目）
        pending_projects = [
            p for p in projects 
            if p.status != "已结账"
        ]
        pending_projects_count = len(pending_projects)
        
        # 进行中步骤数
        in_progress_steps = self.step_repo.list_in_progress_steps(project_ids)
        
        return DashboardStats(
            today_todos=today_todos,
            total_revenue=total_revenue,
            platform_revenue=platform_revenue,
            pending_projects_count=pending_projects_count,
            in_progress_steps_count=len(in_progress_steps)
        )

