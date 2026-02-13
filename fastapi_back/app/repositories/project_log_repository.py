"""
项目日志仓库

重构后使用 schemas 中的 DTO。
"""
from sqlmodel import Session, select
from typing import List, Optional

from app.repositories.base import BaseRepository
from app.models.project_log import ProjectLog
from app.schemas.project_log import ProjectLogCreate


class ProjectLogRepository(BaseRepository[ProjectLog]):
    """项目日志数据访问层"""

    def __init__(self, session: Session):
        super().__init__(session, ProjectLog)

    def create(self, log_data: ProjectLogCreate) -> ProjectLog:
        """创建日志"""
        if isinstance(log_data, dict):
            log = ProjectLog(**log_data)
        else:
            log = ProjectLog(**log_data.model_dump())
        return super().create(log)

    def list_by_project(self, project_id: int, limit: Optional[int] = None) -> List[ProjectLog]:
        """获取项目的日志列表"""
        query = select(ProjectLog).where(ProjectLog.project_id == project_id).order_by(ProjectLog.created_at.desc())
        if limit:
            query = query.limit(limit)
        return list(self.session.exec(query).all())

    def list_by_historical_project(self, historical_project_id: int, limit: Optional[int] = None) -> List[ProjectLog]:
        """获取历史项目的日志列表"""
        query = select(ProjectLog).where(ProjectLog.historical_project_id == historical_project_id).order_by(ProjectLog.created_at.desc())
        if limit:
            query = query.limit(limit)
        return list(self.session.exec(query).all())
