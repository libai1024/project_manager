"""
附件文件夹数据访问层
"""
from typing import Optional, List
from sqlmodel import Session, select
from app.models.attachment_folder import AttachmentFolder, AttachmentFolderCreate, AttachmentFolderUpdate


class AttachmentFolderRepository:
    """附件文件夹数据访问层"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def create(self, folder_data: AttachmentFolderCreate, project_id: Optional[int] = None, historical_project_id: Optional[int] = None, is_default: bool = False) -> AttachmentFolder:
        """创建文件夹"""
        folder = AttachmentFolder(
            project_id=project_id,
            historical_project_id=historical_project_id,
            name=folder_data.name,
            description=folder_data.description,
            is_default=is_default
        )
        self.session.add(folder)
        self.session.commit()
        self.session.refresh(folder)
        return folder
    
    def get_by_id(self, folder_id: int) -> Optional[AttachmentFolder]:
        """根据ID获取文件夹"""
        return self.session.get(AttachmentFolder, folder_id)
    
    def list_by_project(self, project_id: int) -> List[AttachmentFolder]:
        """获取项目的所有文件夹"""
        query = select(AttachmentFolder).where(AttachmentFolder.project_id == project_id)
        return list(self.session.exec(query).all())
    
    def list_by_historical_project(self, historical_project_id: int) -> List[AttachmentFolder]:
        """获取历史项目的所有文件夹"""
        query = select(AttachmentFolder).where(AttachmentFolder.historical_project_id == historical_project_id)
        return list(self.session.exec(query).all())
    
    def update(self, folder: AttachmentFolder, update_data: AttachmentFolderUpdate) -> AttachmentFolder:
        """更新文件夹"""
        if update_data.name is not None:
            folder.name = update_data.name
        if update_data.description is not None:
            folder.description = update_data.description
        
        self.session.add(folder)
        self.session.commit()
        self.session.refresh(folder)
        return folder
    
    def delete(self, folder: AttachmentFolder) -> None:
        """删除文件夹"""
        self.session.delete(folder)
        self.session.commit()
    
    def get_default_folders(self, project_id: int) -> List[AttachmentFolder]:
        """获取项目的默认文件夹"""
        query = select(AttachmentFolder).where(
            AttachmentFolder.project_id == project_id,
            AttachmentFolder.is_default == True
        )
        return list(self.session.exec(query).all())
    
    def create_default_folders(self, project_id: int) -> List[AttachmentFolder]:
        """为项目创建默认文件夹"""
        folders = []
        default_names = ["项目需求", "项目交付", "其他"]
        
        for name in default_names:
            # 检查是否已存在
            existing = self.session.exec(
                select(AttachmentFolder).where(
                    AttachmentFolder.project_id == project_id,
                    AttachmentFolder.name == name
                )
            ).first()
            
            if not existing:
                folder = AttachmentFolder(
                    project_id=project_id,
                    name=name,
                    is_default=True,
                    description=f"默认{name}文件夹"
                )
                self.session.add(folder)
                folders.append(folder)
        
        self.session.commit()
        for folder in folders:
            self.session.refresh(folder)
        
        return folders
    
    def get_other_folder(self, project_id: Optional[int] = None, historical_project_id: Optional[int] = None) -> Optional[AttachmentFolder]:
        """获取项目的"其他"文件夹，如果不存在则创建"""
        if project_id:
            folder = self.session.exec(
                select(AttachmentFolder).where(
                    AttachmentFolder.project_id == project_id,
                    AttachmentFolder.name == "其他"
                )
            ).first()
            
            if not folder:
                folder = AttachmentFolder(
                    project_id=project_id,
                    name="其他",
                    is_default=True,
                    description="默认其他文件夹，用于存放未分类的文件"
                )
                self.session.add(folder)
                self.session.commit()
                self.session.refresh(folder)
            
            return folder
        elif historical_project_id:
            folder = self.session.exec(
                select(AttachmentFolder).where(
                    AttachmentFolder.historical_project_id == historical_project_id,
                    AttachmentFolder.name == "其他"
                )
            ).first()
            
            if not folder:
                folder = AttachmentFolder(
                    historical_project_id=historical_project_id,
                    name="其他",
                    is_default=True,
                    description="默认其他文件夹，用于存放未分类的文件"
                )
                self.session.add(folder)
                self.session.commit()
                self.session.refresh(folder)
            
            return folder
        return None
    
    def create_default_folders_for_historical_project(self, historical_project_id: int) -> List[AttachmentFolder]:
        """为历史项目创建默认文件夹"""
        folders = []
        default_names = ["项目需求", "项目交付", "其他"]
        
        for name in default_names:
            # 检查是否已存在
            existing = self.session.exec(
                select(AttachmentFolder).where(
                    AttachmentFolder.historical_project_id == historical_project_id,
                    AttachmentFolder.name == name
                )
            ).first()
            
            if not existing:
                folder = AttachmentFolder(
                    historical_project_id=historical_project_id,
                    name=name,
                    is_default=True,
                    description=f"默认{name}文件夹"
                )
                self.session.add(folder)
                folders.append(folder)
        
        self.session.commit()
        for folder in folders:
            self.session.refresh(folder)
        
        return folders

