"""
附件数据访问层
"""
from typing import Optional, List
from sqlmodel import Session, select
from app.models.attachment import Attachment


class AttachmentRepository:
    """附件数据访问层"""
    
    def __init__(self, session: Session):
        self.session = session
    
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
        self.session.add(attachment)
        self.session.commit()
        self.session.refresh(attachment)
        return attachment
    
    def get_by_id(self, attachment_id: int) -> Optional[Attachment]:
        """根据ID获取附件"""
        return self.session.get(Attachment, attachment_id)
    
    def list_by_project(self, project_id: int) -> List[Attachment]:
        """获取项目的所有附件"""
        return list(self.session.exec(
            select(Attachment).where(Attachment.project_id == project_id)
        ).all())
    
    def list_by_historical_project(self, historical_project_id: int) -> List[Attachment]:
        """获取历史项目的所有附件"""
        return list(self.session.exec(
            select(Attachment).where(Attachment.historical_project_id == historical_project_id)
        ).all())
    
    
    def update(self, attachment: Attachment, update_data: dict) -> Attachment:
        """更新附件信息"""
        for field, value in update_data.items():
            setattr(attachment, field, value)
        self.session.add(attachment)
        self.session.commit()
        self.session.refresh(attachment)
        return attachment
    
    def delete(self, attachment: Attachment) -> None:
        """删除附件"""
        self.session.delete(attachment)
        self.session.commit()

