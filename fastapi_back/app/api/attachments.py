"""
附件管理API路由层（重构后）
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlmodel import Session
from app.core.database import get_session
from app.core.dependencies import get_current_active_user
from app.services.attachment_service import AttachmentService
from app.models.user import User
from app.models.attachment import AttachmentRead, AttachmentUpdate
import os
import uuid

router = APIRouter()

# 附件上传目录
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


def get_file_extension(filename: str) -> str:
    """获取文件扩展名"""
    return os.path.splitext(filename)[1].lower()


@router.get("/project/{project_id}", response_model=List[AttachmentRead])
async def list_attachments(
    project_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """获取项目的所有附件"""
    attachment_service = AttachmentService(session)
    return attachment_service.list_attachments_by_project(
        project_id=project_id,
        current_user_id=current_user.id,
        is_admin=(current_user.role == "admin")
    )


@router.post("/project/{project_id}", response_model=AttachmentRead)
async def upload_attachment(
    project_id: int,
    file: UploadFile = File(...),
    file_type: str = Form("其他"),
    description: Optional[str] = Form(None),
    folder_id: Optional[int] = Form(None),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """上传附件（支持大文件，最大1GB）"""
    # 文件大小限制：1GB
    MAX_FILE_SIZE = 1 * 1024 * 1024 * 1024  # 1GB
    
    # 生成唯一文件名
    file_extension = get_file_extension(file.filename)
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)
    
    # 流式保存文件（支持大文件）
    try:
        file_size = 0
        with open(file_path, "wb") as buffer:
            # 分块读取，避免一次性加载到内存
            while True:
                chunk = await file.read(8192)  # 8KB chunks
                if not chunk:
                    break
                file_size += len(chunk)
                # 检查文件大小
                if file_size > MAX_FILE_SIZE:
                    # 删除已写入的部分文件
                    if os.path.exists(file_path):
                        os.remove(file_path)
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"文件大小超过限制（最大1GB），当前文件大小：{file_size / (1024*1024):.2f}MB"
                    )
                buffer.write(chunk)
    except HTTPException:
        raise
    except Exception as e:
        # 如果出错，删除可能已创建的文件
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except:
                pass
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save file: {str(e)}"
        )
    
    # 创建附件记录
    attachment_service = AttachmentService(session)
    attachment = attachment_service.create_attachment(
        project_id=project_id,
        file_path=file_path,
        file_name=file.filename,
        file_type=file_type,
        description=description,
        folder_id=folder_id,
        current_user_id=current_user.id,
        is_admin=(current_user.role == "admin")
    )
    
    # 如果附件属于"项目需求"文件夹，且项目刚创建（1分钟内），更新项目创建日志
    if attachment.folder_id:
        from app.repositories.attachment_folder_repository import AttachmentFolderRepository
        folder_repo = AttachmentFolderRepository(session)
        folder = folder_repo.get_by_id(attachment.folder_id)
        if folder and folder.name == "项目需求":
            # 检查项目创建时间
            from app.repositories.project_repository import ProjectRepository
            project_repo = ProjectRepository(session)
            project = project_repo.get_by_id(project_id)
            if project:
                from datetime import datetime, timedelta
                time_diff = datetime.utcnow() - project.created_at
                # 如果项目创建时间在1分钟内，更新项目创建日志
                if time_diff < timedelta(minutes=1):
                    from app.services.project_log_service import ProjectLogService
                    from app.repositories.project_log_repository import ProjectLogRepository
                    log_service = ProjectLogService(session)
                    log_repo = ProjectLogRepository(session)
                    
                    # 获取项目的最新日志（应该是创建项目的日志）
                    logs = log_repo.list_by_project(project_id, limit=1)
                    if logs and logs[0].action.value == "project_created":
                        create_log = logs[0]
                        import json
                        # 解析现有details
                        details = json.loads(create_log.details) if create_log.details else {}
                        attachment_ids = details.get("attachment_ids", [])
                        photos = details.get("photos", [])
                        
                        # 区分图片和文件
                        if file.filename.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp')):
                            if str(attachment.id) not in photos:
                                photos.append(str(attachment.id))
                        else:
                            if attachment.id not in attachment_ids:
                                attachment_ids.append(attachment.id)
                        
                        # 更新日志details
                        details["attachment_ids"] = attachment_ids
                        details["photos"] = photos
                        create_log.details = json.dumps(details, ensure_ascii=False)
                        session.add(create_log)
                        session.commit()
    
    # 获取文件夹名称
    if attachment.folder_id:
        from app.repositories.attachment_folder_repository import AttachmentFolderRepository
        folder_repo = AttachmentFolderRepository(session)
        folder = folder_repo.get_by_id(attachment.folder_id)
        if folder:
            attachment_dict = AttachmentRead.model_validate(attachment)
            attachment_dict.folder_name = folder.name
            return attachment_dict
    
    return attachment


@router.get("/{attachment_id}", response_model=AttachmentRead)
async def get_attachment(
    attachment_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """获取附件详情"""
    attachment_service = AttachmentService(session)
    return attachment_service.get_attachment_by_id(
        attachment_id=attachment_id,
        current_user_id=current_user.id,
        is_admin=(current_user.role == "admin")
    )


@router.put("/{attachment_id}", response_model=AttachmentRead)
async def update_attachment(
    attachment_id: int,
    attachment_data: AttachmentUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """更新附件信息"""
    attachment_service = AttachmentService(session)
    return attachment_service.update_attachment(
        attachment_id=attachment_id,
        attachment_data=attachment_data,
        current_user_id=current_user.id,
        is_admin=(current_user.role == "admin")
    )


@router.delete("/{attachment_id}")
async def delete_attachment(
    attachment_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """删除附件"""
    from fastapi.responses import FileResponse
    
    attachment_service = AttachmentService(session)
    
    # 先获取附件信息（用于删除文件）
    attachment = attachment_service.get_attachment_by_id(
        attachment_id=attachment_id,
        current_user_id=current_user.id,
        is_admin=(current_user.role == "admin")
        )
    
    # 删除文件
    if os.path.exists(attachment.file_path):
        try:
            os.remove(attachment.file_path)
        except Exception as e:
            # 记录错误但不阻止删除数据库记录
            print(f"Warning: Failed to delete file {attachment.file_path}: {e}")
    
    # 删除数据库记录
    attachment_service.delete_attachment(
        attachment_id=attachment_id,
        current_user_id=current_user.id,
        is_admin=(current_user.role == "admin")
    )
    
    return {"message": "Attachment deleted successfully"}


@router.post("/{attachment_id}/copy", response_model=AttachmentRead)
async def copy_attachment(
    attachment_id: int,
    target_project_id: Optional[int] = None,
    target_folder_id: Optional[int] = None,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """复制附件到指定项目/文件夹"""
    import shutil
    attachment_service = AttachmentService(session)
    
    # 获取原附件
    attachment = attachment_service.attachment_repo.get_by_id(attachment_id)
    if not attachment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attachment not found"
        )
    
    # 权限检查
    project = attachment_service.project_repo.get_by_id(attachment.project_id)
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
    
    # 确定目标项目
    target_project = attachment.project_id
    if target_project_id:
        target_project_obj = attachment_service.project_repo.get_by_id(target_project_id)
        if not target_project_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Target project not found"
            )
        if current_user.role != "admin" and target_project_obj.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions for target project"
            )
        target_project = target_project_id
    
    # 复制文件
    file_extension = get_file_extension(attachment.file_name)
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    new_file_path = os.path.join(UPLOAD_DIR, unique_filename)
    
    try:
        shutil.copy2(attachment.file_path, new_file_path)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to copy file: {str(e)}"
        )
    
    # 创建新附件记录
    new_attachment = attachment_service.create_attachment(
        project_id=target_project,
        file_path=new_file_path,
        file_name=attachment.file_name,
        file_type=attachment.file_type,
        description=attachment.description,
        folder_id=target_folder_id,
        current_user_id=current_user.id,
        is_admin=(current_user.role == "admin")
    )
    
    return new_attachment


@router.post("/batch", response_model=List[AttachmentRead])
async def get_attachments_batch(
    attachment_ids: List[int],
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """批量获取附件信息"""
    attachment_service = AttachmentService(session)
    attachments = []
    for attachment_id in attachment_ids:
        try:
            attachment = attachment_service.get_attachment_by_id(
                attachment_id=attachment_id,
                current_user_id=current_user.id,
                is_admin=(current_user.role == "admin")
            )
            attachments.append(attachment)
        except HTTPException:
            # 如果附件不存在或无权访问，跳过
            continue
    return attachments


def get_media_type(filename: str) -> str:
    """根据文件扩展名获取MIME类型"""
    extension = get_file_extension(filename).lower()
    media_types = {
        # 图片
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.png': 'image/png',
        '.gif': 'image/gif',
        '.bmp': 'image/bmp',
        '.webp': 'image/webp',
        '.svg': 'image/svg+xml',
        '.ico': 'image/x-icon',
        '.heic': 'image/heic',
        '.heif': 'image/heif',
        '.tiff': 'image/tiff',
        '.tif': 'image/tiff',
        '.psd': 'image/vnd.adobe.photoshop',
        '.raw': 'image/raw',
        '.cr2': 'image/x-canon-cr2',
        '.nef': 'image/x-nikon-nef',
        '.dng': 'image/x-adobe-dng',
        # 文档 - Microsoft Office
        '.pdf': 'application/pdf',
        '.doc': 'application/msword',
        '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        '.xls': 'application/vnd.ms-excel',
        '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        '.ppt': 'application/vnd.ms-powerpoint',
        '.pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
        # 文档 - WPS Office
        '.wps': 'application/vnd.ms-works',
        '.et': 'application/vnd.ms-excel',
        '.dps': 'application/vnd.ms-powerpoint',
        # 文档 - OpenDocument
        '.odt': 'application/vnd.oasis.opendocument.text',
        '.ods': 'application/vnd.oasis.opendocument.spreadsheet',
        '.odp': 'application/vnd.oasis.opendocument.presentation',
        # 文档 - 其他
        '.rtf': 'application/rtf',
        '.txt': 'text/plain',
        '.md': 'text/markdown',
        '.json': 'application/json',
        '.xml': 'application/xml',
        '.csv': 'text/csv',
        # 代码文件
        '.js': 'text/javascript',
        '.html': 'text/html',
        '.css': 'text/css',
        '.py': 'text/x-python',
        '.java': 'text/x-java-source',
        '.cpp': 'text/x-c++src',
        '.c': 'text/x-csrc',
        '.h': 'text/x-cheader',
        '.go': 'text/x-go',
        '.rs': 'text/x-rust',
        '.php': 'text/x-php',
        '.rb': 'text/x-ruby',
        '.sh': 'text/x-shellscript',
        '.vue': 'text/x-vue',
        '.jsx': 'text/javascript',
        '.tsx': 'text/typescript',
        '.swift': 'text/x-swift',
        '.kt': 'text/x-kotlin',
        '.scala': 'text/x-scala',
        '.lua': 'text/x-lua',
        '.sql': 'text/x-sql',
        # 压缩文件
        '.zip': 'application/zip',
        '.rar': 'application/x-rar-compressed',
        '.7z': 'application/x-7z-compressed',
        '.tar': 'application/x-tar',
        '.gz': 'application/gzip',
        '.bz2': 'application/x-bzip2',
        '.xz': 'application/x-xz',
        # 视频 - 主流格式
        '.mp4': 'video/mp4',
        '.webm': 'video/webm',
        '.avi': 'video/x-msvideo',
        '.mov': 'video/quicktime',
        '.mkv': 'video/x-matroska',
        '.flv': 'video/x-flv',
        '.wmv': 'video/x-ms-wmv',
        '.m4v': 'video/x-m4v',
        '.mpeg': 'video/mpeg',
        '.mpg': 'video/mpeg',
        '.3gp': 'video/3gpp',
        '.3g2': 'video/3gpp2',
        '.ts': 'video/mp2t',
        '.mts': 'video/mp2t',
        '.m2ts': 'video/mp2t',
        '.vob': 'video/dvd',
        '.ogv': 'video/ogg',
        # 音频 - 主流格式
        '.mp3': 'audio/mpeg',
        '.wav': 'audio/wav',
        '.flac': 'audio/flac',
        '.aac': 'audio/aac',
        '.ogg': 'audio/ogg',  # ogg 音频
        '.oga': 'audio/ogg',
        '.m4a': 'audio/mp4',
        '.wma': 'audio/x-ms-wma',
        '.aiff': 'audio/aiff',
        '.aif': 'audio/aiff',
        '.au': 'audio/basic',
        '.mid': 'audio/midi',
        '.midi': 'audio/midi',
        '.ape': 'audio/x-ape',
        '.opus': 'audio/opus',
    }
    return media_types.get(extension, 'application/octet-stream')


@router.get("/{attachment_id}/download")
async def download_attachment(
    attachment_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """下载附件"""
    from fastapi.responses import StreamingResponse
    from urllib.parse import quote

    attachment_service = AttachmentService(session)
    attachment = attachment_service.get_attachment_by_id(
        attachment_id=attachment_id,
        current_user_id=current_user.id,
        is_admin=(current_user.role == "admin")
        )

    if not os.path.exists(attachment.file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )

    # 根据文件扩展名确定MIME类型
    media_type = get_media_type(attachment.file_name)

    # 处理中文文件名编码
    encoded_filename = quote(attachment.file_name, safe='')

    def file_generator():
        with open(attachment.file_path, 'rb') as f:
            while True:
                chunk = f.read(8192)
                if not chunk:
                    break
                yield chunk

    return StreamingResponse(
        file_generator(),
        media_type=media_type,
        headers={
            "Content-Disposition": f'attachment; filename="{encoded_filename}"; filename*=UTF-8\'\'{encoded_filename}'
        }
    )


@router.get("/{attachment_id}/preview")
async def preview_attachment(
    attachment_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """预览附件（返回文件内容用于在线预览）"""
    from fastapi.responses import Response, StreamingResponse
    import mimetypes
    from app.core.exceptions import NotFoundException

    try:
        attachment_service = AttachmentService(session)
        attachment = attachment_service.get_attachment_by_id(
            attachment_id=attachment_id,
            current_user_id=current_user.id,
            is_admin=(current_user.role == "admin")
        )
    except NotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.msg
        )

    if not attachment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attachment not found"
        )

    # 处理文件路径（可能是相对路径，需要转换为绝对路径）
    file_path = attachment.file_path
    if not os.path.isabs(file_path):
        # 如果是相对路径，尝试相对于UPLOAD_DIR
        file_path = os.path.join(UPLOAD_DIR, os.path.basename(file_path))

    # 检查文件路径是否存在
    if not file_path or not os.path.exists(file_path):
        # 尝试原始路径
        if os.path.exists(attachment.file_path):
            file_path = attachment.file_path
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"File not found: {attachment.file_path}"
            )

    # 根据文件扩展名确定MIME类型
    media_type = get_media_type(attachment.file_name)

    # 对于文本文件，直接读取并返回
    if media_type.startswith('text/') or media_type in ['application/json', 'application/xml']:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return Response(content=content, media_type=media_type)
        except UnicodeDecodeError:
            # 如果UTF-8解码失败，尝试其他编码
            try:
                with open(file_path, 'r', encoding='gbk') as f:
                    content = f.read()
                return Response(content=content, media_type=media_type)
            except Exception as e:
                # 如果还是失败，返回二进制流
                print(f"Warning: Failed to read text file as text: {e}")
                pass
        except Exception as e:
            print(f"Error reading text file: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to read file: {str(e)}"
            )

    # 对于其他文件，返回文件流
    def file_generator():
        try:
            with open(file_path, 'rb') as f:
                while True:
                    chunk = f.read(8192)
                    if not chunk:
                        break
                    yield chunk
        except Exception as e:
            print(f"Error reading file stream: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to read file stream: {str(e)}"
            )

    # 处理文件名编码，避免中文字符导致的编码错误
    from urllib.parse import quote
    encoded_filename = quote(attachment.file_name, safe='')

    return StreamingResponse(
        file_generator(),
        media_type=media_type,
        headers={
            "Content-Disposition": f'inline; filename="{encoded_filename}"; filename*=UTF-8\'\'{encoded_filename}'
        }
    )


# 历史项目附件相关端点
@router.get("/historical-project/{historical_project_id}", response_model=List[AttachmentRead])
async def list_historical_project_attachments(
    historical_project_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """获取历史项目的所有附件"""
    attachment_service = AttachmentService(session)
    return attachment_service.list_attachments_by_historical_project(
        historical_project_id=historical_project_id,
        current_user_id=current_user.id,
        is_admin=(current_user.role == "admin")
    )


@router.post("/historical-project/{historical_project_id}", response_model=AttachmentRead)
async def upload_historical_project_attachment(
    historical_project_id: int,
    file: UploadFile = File(...),
    file_type: str = Form("其他"),
    description: Optional[str] = Form(None),
    folder_id: Optional[int] = Form(None),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """为历史项目上传附件（支持大文件，最大1GB）"""
    # 文件大小限制：1GB
    MAX_FILE_SIZE = 1 * 1024 * 1024 * 1024  # 1GB
    
    # 生成唯一文件名
    file_extension = get_file_extension(file.filename)
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)
    
    # 流式保存文件（支持大文件）
    try:
        file_size = 0
        with open(file_path, "wb") as buffer:
            # 分块读取，避免一次性加载到内存
            while True:
                chunk = await file.read(8192)  # 8KB chunks
                if not chunk:
                    break
                file_size += len(chunk)
                # 检查文件大小
                if file_size > MAX_FILE_SIZE:
                    # 删除已写入的部分文件
                    if os.path.exists(file_path):
                        os.remove(file_path)
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"文件大小超过限制（最大1GB），当前文件大小：{file_size / (1024*1024):.2f}MB"
                    )
                buffer.write(chunk)
    except HTTPException:
        raise
    except Exception as e:
        # 如果出错，删除可能已创建的文件
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except:
                pass
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save file: {str(e)}"
        )
    
    # 创建附件记录
    attachment_service = AttachmentService(session)
    attachment = attachment_service.create_attachment_for_historical_project(
        historical_project_id=historical_project_id,
        file_path=file_path,
        file_name=file.filename,
        file_type=file_type,
        description=description,
        folder_id=folder_id,
        current_user_id=current_user.id,
        is_admin=(current_user.role == "admin")
    )
    
    return attachment
