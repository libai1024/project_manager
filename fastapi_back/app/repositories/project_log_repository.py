"""
项目日志仓库
"""
from sqlmodel import Session, select
from typing import List, Optional
from app.models.project_log import ProjectLog, ProjectLogCreate


class ProjectLogRepository:
    def __init__(self, session: Session):
        self.session = session
    
    def create(self, log_data: ProjectLogCreate) -> ProjectLog:
        """创建日志"""
        if isinstance(log_data, dict):
            log = ProjectLog(**log_data)
        else:
            log = ProjectLog(**log_data.model_dump())
        self.session.add(log)
        self.session.commit()
        self.session.refresh(log)
        return log
    
    def get_by_id(self, log_id: int) -> Optional[ProjectLog]:
        """根据ID获取日志"""
        return self.session.get(ProjectLog, log_id)
    
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
    
    def delete(self, log: ProjectLog) -> None:
        """删除日志"""
        self.session.delete(log)
        self.session.commit()


