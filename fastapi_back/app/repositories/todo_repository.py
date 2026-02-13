"""
待办数据访问层

重构后使用 schemas 中的 DTO。
"""
from typing import Optional, List
from sqlmodel import Session, select
from sqlalchemy import func
from datetime import datetime, date, timezone, timedelta
import json

from app.repositories.base import BaseRepository
from app.models.todo import Todo
from app.schemas.todo import TodoCreate, TodoUpdate


class TodoRepository(BaseRepository[Todo]):
    """待办数据访问层"""

    @staticmethod
    def _today_local() -> date:
        """获取本地（北京时间，UTC+8）的今天日期"""
        return datetime.now(timezone.utc).astimezone(timezone(timedelta(hours=8))).date()

    def __init__(self, session: Session):
        super().__init__(session, Todo)

    def create(self, todo_data: TodoCreate) -> Todo:
        """创建待办"""
        todo = Todo(
            project_id=todo_data.project_id,
            historical_project_id=todo_data.historical_project_id,
            description=todo_data.description,
            step_ids=json.dumps(todo_data.step_ids),
            target_date=todo_data.target_date
        )
        return super().create(todo)
    
    def list_by_date(self, target_date: date, user_id: Optional[int] = None) -> List[Todo]:
        """获取指定日期的待办列表"""
        from sqlalchemy import or_, and_
        query = select(Todo)
        
        # 如果指定了日期，匹配该日期的待办
        if target_date:
            # 计算目标日期在本地时区（UTC+8）的开始和结束时间（UTC）
            # 目标日期的开始：本地时区 00:00:00 转换为 UTC
            target_start_local = datetime.combine(target_date, datetime.min.time()).replace(tzinfo=timezone(timedelta(hours=8)))
            target_start_utc = target_start_local.astimezone(timezone.utc)
            
            # 目标日期的结束：本地时区 23:59:59.999999 转换为 UTC
            from datetime import time as dt_time
            target_end_local = datetime.combine(target_date, dt_time(23, 59, 59, 999999)).replace(tzinfo=timezone(timedelta(hours=8)))
            target_end_utc = target_end_local.astimezone(timezone.utc)
            
            # 匹配逻辑：
            # 1. target_date不为None：target_date在该日期范围内
            # 2. target_date为None：created_at在该日期范围内（使用created_at的日期）
            query = query.where(
                or_(
                    # target_date不为None，且target_date在目标日期范围内
                    and_(
                        Todo.target_date.is_not(None),
                        Todo.target_date >= target_start_utc,
                        Todo.target_date <= target_end_utc
                    ),
                    # target_date为None，但created_at在目标日期范围内
                    and_(
                        Todo.target_date.is_(None),
                        Todo.created_at >= target_start_utc,
                        Todo.created_at <= target_end_utc
                    )
                )
            )
        else:
            # 如果没有指定日期，返回所有待办
            pass
        
        todos = list(self.session.exec(query).all())
        
        # 如果指定了用户ID，过滤项目（包括历史项目）
        if user_id:
            from app.repositories.project_repository import ProjectRepository
            from app.repositories.historical_project_repository import HistoricalProjectRepository
            project_repo = ProjectRepository(self.session)
            historical_project_repo = HistoricalProjectRepository(self.session)
            
            user_projects = project_repo.list_by_user(user_id)
            project_ids = [p.id for p in user_projects]
            
            user_historical_projects = historical_project_repo.list(user_id=user_id, limit=10000)
            historical_project_ids = [p.id for p in user_historical_projects]
            
            todos = [
                t for t in todos 
                if (t.project_id and t.project_id in project_ids) or 
                   (t.historical_project_id and t.historical_project_id in historical_project_ids)
            ]
        
        return todos
    
    def update(self, todo: Todo, update_data: TodoUpdate) -> Todo:
        """更新待办"""
        update_dict = update_data.model_dump(exclude_unset=True)
        return super().update(todo, update_dict)

    def delete(self, todo: Todo) -> bool:
        """删除待办"""
        return super().delete(todo)

