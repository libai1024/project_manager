"""
附件数据访问层

重构后继承 BaseRepository。
"""
from typing import Optional, List
from sqlmodel import Session, select

from app.repositories.base import BaseRepository
from app.models.attachment import Attachment
from app.schemas.attachment import AttachmentCreate


class AttachmentRepository(BaseRepository[Attachment]):
    """附件数据访问层"""

    def __init__(self, session: Session):
        super().__init__(session, Attachment)

    def create(
        self,
        project_id: Optional[int] = None,
        historical_project_id: Optional[int] = None,
        file_path: str = None,
        file_name: str = None,
        file_type: str = None,
        description: Optional[str] = None,
        folder_id: Optional[int] = None
    ) -> Attachment:
        """创建附件记录"""
        attachment = Attachment(
            project_id=project_id,
            historical_project_id=historical_project_id,
            file_path=file_path,
            file_name=file_name,
            file_type=file_type or "其他",
            description=description,
            folder_id=folder_id
        )
        return super().create(attachment)

    def list_by_project(self, project_id: int) -> List[Attachment]:
        """获取项目的所有附件"""
        return self.find_many(project_id=project_id)

    def list_by_historical_project(self, historical_project_id: int) -> List[Attachment]:
        """获取历史项目的所有附件"""
        return self.find_many(historical_project_id=historical_project_id)
