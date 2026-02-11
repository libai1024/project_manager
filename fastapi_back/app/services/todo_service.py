"""
待办服务层
"""
from typing import List, Optional, Dict
from datetime import datetime, date, timedelta
from sqlmodel import Session
from app.repositories.project_repository import ProjectRepository
from app.repositories.step_repository import StepRepository
from app.repositories.platform_repository import PlatformRepository
from app.models.project import ProjectStep, StepStatus
from pydantic import BaseModel


class TodoItem(BaseModel):
    step_id: int
    step_name: str
    project_id: int
    project_title: str
    student_name: str
    platform_name: str
    status: str
    deadline: Optional[datetime] = None
    order_index: int
    is_todo: bool
    created_at: datetime


class TodoCalendarItem(BaseModel):
    date: date
    todo_count: int
    completed_count: int


class TodoService:
    """待办服务层"""
    
    def __init__(self, session: Session):
        self.session = session
        self.project_repo = ProjectRepository(session)
        self.step_repo = StepRepository(session)
        self.platform_repo = PlatformRepository(session)
    
    def get_todos_by_date(self, target_date: date, user_id: Optional[int] = None) -> List[TodoItem]:
        """获取指定日期的待办列表（返回所有待办，不按日期过滤）"""
        # 获取项目列表
        if user_id:
            projects = self.project_repo.list_by_user(user_id)
        else:
            projects = self.project_repo.list()
        
        project_ids = [p.id for p in projects]
        
        # 获取所有待办步骤
        todo_steps = self.step_repo.list_todo_steps(project_ids)
        
        todos = []
        for step in todo_steps:
            project = self.project_repo.get_by_id(step.project_id)
            if not project:
                continue
            
            platform = self.platform_repo.get_by_id(project.platform_id)
            
            todos.append(TodoItem(
                step_id=step.id,
                step_name=step.name,
                project_id=step.project_id,
                project_title=project.title,
                student_name=project.student_name or "",
                platform_name=platform.name if platform else '未知平台',
                status=step.status,
                deadline=step.deadline,
                order_index=step.order_index,
                is_todo=step.is_todo,
                created_at=step.created_at
            ))
        
        # 按截止时间排序，没有截止时间的排在后面
        todos.sort(key=lambda x: (
            x.deadline is None,
            x.deadline if x.deadline else datetime.max
        ))
        
        return todos
    
    def get_todo_calendar(self, year: Optional[int] = None, month: Optional[int] = None, user_id: Optional[int] = None) -> List[TodoCalendarItem]:
        """获取待办日历数据"""
        if year is None or month is None:
            today = date.today()
            year = today.year
            month = today.month
        
        # 获取该月的所有日期
        start_date = date(year, month, 1)
        if month == 12:
            end_date = date(year + 1, 1, 1) - timedelta(days=1)
        else:
            end_date = date(year, month + 1, 1) - timedelta(days=1)
        
        # 获取项目列表
        if user_id:
            projects = self.project_repo.list_by_user(user_id)
        else:
            projects = self.project_repo.list()
        
        project_ids = [p.id for p in projects]
        
        # 获取所有待办步骤
        todo_steps = self.step_repo.list_todo_steps(project_ids)
        
        # 按日期统计
        calendar_data: Dict[date, Dict[str, int]] = {}
        current_date = start_date
        while current_date <= end_date:
            calendar_data[current_date] = {'todo': 0, 'completed': 0}
            current_date += timedelta(days=1)
        
        for step in todo_steps:
            # 根据步骤的创建时间判断属于哪些日期
            if step.created_at:
                step_date = step.created_at.date()
            elif step.deadline:
                step_date = step.deadline.date()
            else:
                step_date = date.today()
            
            if start_date <= step_date <= end_date:
                if step.status == '已完成':
                    calendar_data[step_date]['completed'] += 1
                elif step.is_todo:
                    calendar_data[step_date]['todo'] += 1
        
        # 转换为列表
        result = []
        for d, counts in sorted(calendar_data.items()):
            result.append(TodoCalendarItem(
                date=d,
                todo_count=counts['todo'],
                completed_count=counts['completed']
            ))
        
        return result
    
    def toggle_step_todo(self, step_id: int, user_id: int) -> dict:
        """切换步骤的待办状态"""
        step = self.step_repo.get_by_id(step_id)
        if not step:
            raise ValueError("步骤不存在")
        
        # 检查权限
        project = self.project_repo.get_by_id(step.project_id)
        if not project:
            raise ValueError("项目不存在")
        
        # 非管理员只能操作自己的项目
        # 这里可以添加权限检查逻辑
        
        step.is_todo = not step.is_todo
        self.session.add(step)
        self.session.commit()
        self.session.refresh(step)
        
        return {"step_id": step_id, "is_todo": step.is_todo}
    
    def complete_todo(self, step_id: int, user_id: int) -> dict:
        """完成待办（同时完成步骤）"""
        step = self.step_repo.get_by_id(step_id)
        if not step:
            raise ValueError("步骤不存在")
        
        # 检查权限
        project = self.project_repo.get_by_id(step.project_id)
        if not project:
            raise ValueError("项目不存在")
        
        # 更新步骤状态为已完成
        step.status = "已完成"
        step.is_todo = False
        self.session.add(step)
        self.session.commit()
        self.session.refresh(step)
        
        return {"step_id": step_id, "status": step.status}

