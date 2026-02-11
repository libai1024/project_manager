"""
附件文件夹管理API路由层
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from sqlalchemy import func, or_
from app.core.database import get_session
from app.core.dependencies import get_current_active_user
from app.repositories.attachment_folder_repository import AttachmentFolderRepository
from app.repositories.project_repository import ProjectRepository
from app.repositories.historical_project_repository import HistoricalProjectRepository
from app.repositories.system_settings_repository import SystemSettingsRepository
from app.models.user import User
from app.models.attachment_folder import AttachmentFolderRead, AttachmentFolderCreate, AttachmentFolderUpdate
from app.models.attachment import Attachment

router = APIRouter()


@router.get("/project/{project_id}", response_model=List[AttachmentFolderRead])
async def list_folders(
    project_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """获取项目的所有文件夹"""
    # 权限检查
    project_repo = ProjectRepository(session)
    project = project_repo.get_by_id(project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    if current_user.role != "admin" and project.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    folder_repo = AttachmentFolderRepository(session)
    folders = folder_repo.list_by_project(project_id)
    
    # 计算每个文件夹的附件数量
    from app.models.attachment import Attachment
    from sqlalchemy import or_
    result = []
    for folder in folders:
        # 如果是"其他"文件夹，统计所有 folder_id 为 NULL 的文件
        if folder.name == "其他":
            count = session.exec(
                select(func.count(Attachment.id)).where(
                    Attachment.project_id == project_id,
                    or_(Attachment.folder_id.is_(None), Attachment.folder_id == folder.id)
                )
            ).one()
        else:
            count = session.exec(
                select(func.count(Attachment.id)).where(Attachment.folder_id == folder.id)
            ).one()
        folder_dict = AttachmentFolderRead.model_validate(folder)
        folder_dict.attachment_count = count
        result.append(folder_dict)
    
    return result


@router.post("/project/{project_id}", response_model=AttachmentFolderRead)
async def create_folder(
    project_id: int,
    folder_data: AttachmentFolderCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """创建文件夹"""
    # 权限检查
    project_repo = ProjectRepository(session)
    project = project_repo.get_by_id(project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    if current_user.role != "admin" and project.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    folder_repo = AttachmentFolderRepository(session)
    folder = folder_repo.create(folder_data, project_id, is_default=False)
    folder_dict = AttachmentFolderRead.model_validate(folder)
    folder_dict.attachment_count = 0
    return folder_dict


@router.put("/{folder_id}", response_model=AttachmentFolderRead)
async def update_folder(
    folder_id: int,
    folder_data: AttachmentFolderUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """更新文件夹"""
    folder_repo = AttachmentFolderRepository(session)
    folder = folder_repo.get_by_id(folder_id)
    if not folder:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Folder not found"
        )
    
    # 权限检查
    project_repo = ProjectRepository(session)
    project = project_repo.get_by_id(folder.project_id)
    if current_user.role != "admin" and project.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    folder = folder_repo.update(folder, folder_data)
    from app.models.attachment import Attachment
    from sqlmodel import select
    count = session.exec(
        select(func.count(Attachment.id)).where(Attachment.folder_id == folder.id)
    ).one()
    folder_dict = AttachmentFolderRead.model_validate(folder)
    folder_dict.attachment_count = count
    return folder_dict


@router.delete("/{folder_id}")
async def delete_folder(
    folder_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """删除文件夹"""
    folder_repo = AttachmentFolderRepository(session)
    folder = folder_repo.get_by_id(folder_id)
    if not folder:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Folder not found"
        )
    
    # 权限检查
    project_repo = ProjectRepository(session)
    project = project_repo.get_by_id(folder.project_id)
    if current_user.role != "admin" and project.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # 默认文件夹不能删除（项目需求、项目交付、其他）
    if folder.is_default or folder.name in ["项目需求", "项目交付", "其他"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete default folder"
        )
    
    folder_repo.delete(folder)
    return {"message": "Folder deleted successfully"}


# 历史项目文件夹相关端点
@router.get("/historical-project/{historical_project_id}", response_model=List[AttachmentFolderRead])
async def list_historical_project_folders(
    historical_project_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """获取历史项目的所有文件夹"""
    # 检查功能是否启用
    settings_repo = SystemSettingsRepository(session)
    if not settings_repo.is_feature_enabled("enable_attachment_management"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="历史项目附件管理功能已禁用")
    
    # 权限检查
    historical_project_repo = HistoricalProjectRepository(session)
    historical_project = historical_project_repo.get_by_id(historical_project_id)
    if not historical_project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Historical project not found"
        )
    
    if current_user.role != "admin" and historical_project.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    folder_repo = AttachmentFolderRepository(session)
    folders = folder_repo.list_by_historical_project(historical_project_id)
    
    # 计算每个文件夹的附件数量
    result = []
    for folder in folders:
        # 如果是"其他"文件夹，统计所有 folder_id 为 NULL 的文件
        if folder.name == "其他":
            count = session.exec(
                select(func.count(Attachment.id)).where(
                    Attachment.historical_project_id == historical_project_id,
                    or_(Attachment.folder_id.is_(None), Attachment.folder_id == folder.id)
                )
            ).one()
        else:
            count = session.exec(
                select(func.count(Attachment.id)).where(Attachment.folder_id == folder.id)
            ).one()
        folder_dict = AttachmentFolderRead.model_validate(folder)
        folder_dict.attachment_count = count
        result.append(folder_dict)
    
    return result


@router.post("/historical-project/{historical_project_id}", response_model=AttachmentFolderRead)
async def create_historical_project_folder(
    historical_project_id: int,
    folder_data: AttachmentFolderCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """创建历史项目文件夹"""
    # 检查功能是否启用
    settings_repo = SystemSettingsRepository(session)
    if not settings_repo.is_feature_enabled("enable_attachment_management"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="历史项目附件管理功能已禁用")
    
    # 权限检查
    historical_project_repo = HistoricalProjectRepository(session)
    historical_project = historical_project_repo.get_by_id(historical_project_id)
    if not historical_project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Historical project not found"
        )
    
    if current_user.role != "admin" and historical_project.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    folder_repo = AttachmentFolderRepository(session)
    folder = folder_repo.create(folder_data, project_id=None, historical_project_id=historical_project_id, is_default=False)
    folder_dict = AttachmentFolderRead.model_validate(folder)
    folder_dict.attachment_count = 0
    return folder_dict

