"""
视频回放API路由
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Request
from fastapi.responses import StreamingResponse, FileResponse
from sqlmodel import Session
from datetime import datetime

from app.core.database import get_session
from app.core.dependencies import get_current_active_user
from app.core.config import settings
from app.services.video_playback_service import VideoPlaybackService
from app.models.user import User
from app.models.video_playback import (
    VideoPlaybackRead,
    VideoPlaybackCreate,
    VideoPlaybackUpdate,
    VideoPlaybackLinkCreate,
    VideoPlaybackLinkRead,
    VideoPlaybackStatRead,
    VideoPasswordVerify,
    VideoPlayback
)
import os
import uuid

router = APIRouter(prefix="/video-playbacks", tags=["视频回放"])


def get_file_extension(filename: str) -> str:
    """获取文件扩展名"""
    return os.path.splitext(filename)[1].lower()


@router.post("/project/{project_id}/upload", response_model=VideoPlaybackRead)
async def upload_video(
    project_id: int,
    file: UploadFile = File(...),
    title: str = Form(...),
    description: Optional[str] = Form(None),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
    request: Request = None
):
    """上传视频"""
    # 验证文件类型
    allowed_extensions = ['.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm', '.mkv']
    file_extension = get_file_extension(file.filename)
    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"不支持的文件类型，支持的格式：{', '.join(allowed_extensions)}"
        )
    
    # 验证文件大小（最大1GB）
    max_size = 1 * 1024 * 1024 * 1024  # 1GB
    
    # 生成唯一文件名
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    upload_dir = "uploads/videos"
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, unique_filename)
    
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
                if file_size > max_size:
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
            detail=f"保存文件失败: {str(e)}"
        )
    
    # 创建视频记录
    video_service = VideoPlaybackService(session)
    video = video_service.create_video(
        project_id=project_id,
        title=title,
        file_path=file_path,
        file_name=file.filename,
        file_size=file_size,
        current_user_id=current_user.id,
        is_admin=(current_user.role == "admin")
    )
    
    if description:
        video.description = description
        video = video_service.update_video(
            video.id,
            VideoPlaybackUpdate(description=description),
            current_user.id,
            current_user.role == "admin"
        )
    
    # 构建返回数据
    # 使用前端URL
    frontend_url = settings.FRONTEND_URL
    if request:
        origin = request.headers.get("origin")
        if origin:
            frontend_url = origin
    links = video_service.list_links(video.id, current_user.id, current_user.role == "admin", frontend_url)
    
    # 创建响应对象
    video_data = video.model_dump()
    video_data['link_count'] = len(links)
    video_data['total_views'] = sum(link.view_count for link in links)
    
    return VideoPlaybackRead(**video_data)


@router.get("/project/{project_id}", response_model=List[VideoPlaybackRead])
async def list_videos(
    project_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
    request: Request = None
):
    """获取项目的所有视频"""
    video_service = VideoPlaybackService(session)
    videos = video_service.list_videos(
        project_id=project_id,
        current_user_id=current_user.id,
        is_admin=(current_user.role == "admin")
    )
    
    # 构建返回数据，添加计算字段
    result = []
    for video in videos:
        # 使用前端URL
        frontend_url = settings.FRONTEND_URL
        if request:
            origin = request.headers.get("origin")
            if origin:
                frontend_url = origin
        links = video_service.list_links(video.id, current_user.id, current_user.role == "admin", frontend_url)
        video_data = video.model_dump()
        video_data['link_count'] = len(links)
        video_data['total_views'] = sum(link.view_count for link in links)
        result.append(VideoPlaybackRead(**video_data))
    
    return result


@router.put("/{video_id}", response_model=VideoPlaybackRead)
async def update_video(
    video_id: int,
    update_data: VideoPlaybackUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
    request: Request = None
):
    """更新视频信息"""
    video_service = VideoPlaybackService(session)
    video = video_service.update_video(
        video_id=video_id,
        update_data=update_data,
        current_user_id=current_user.id,
        is_admin=(current_user.role == "admin")
    )
    
    # 构建返回数据
    # 使用前端URL
    frontend_url = settings.FRONTEND_URL
    if request:
        origin = request.headers.get("origin")
        if origin:
            frontend_url = origin
    links = video_service.list_links(video.id, current_user.id, current_user.role == "admin", frontend_url)
    
    # 创建响应对象
    video_data = video.model_dump()
    video_data['link_count'] = len(links)
    video_data['total_views'] = sum(link.view_count for link in links)
    
    return VideoPlaybackRead(**video_data)


@router.delete("/{video_id}")
async def delete_video(
    video_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """删除视频"""
    video_service = VideoPlaybackService(session)
    success = video_service.delete_video(
        video_id=video_id,
        current_user_id=current_user.id,
        is_admin=(current_user.role == "admin")
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="视频不存在"
        )
    
    return {"message": "视频已删除"}


@router.post("/{video_id}/links", response_model=VideoPlaybackLinkRead)
async def create_link(
    video_id: int,
    link_data: VideoPlaybackLinkCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
    request: Request = None
):
    """创建观看链接"""
    # 使用前端URL
    frontend_url = settings.FRONTEND_URL
    if request:
        origin = request.headers.get("origin")
        if origin:
            frontend_url = origin
    
    video_service = VideoPlaybackService(session)
    link = video_service.create_link(
        video_id=video_id,
        link_data=link_data,
        current_user_id=current_user.id,
        is_admin=(current_user.role == "admin"),
        base_url=frontend_url
    )
    
    # 构建响应对象
    link_data_dict = {
        "id": link.id,
        "video_id": link.video_id,
        "token": link.token,
        "view_count": link.view_count,
        "max_views": link.max_views,
        "expires_at": link.expires_at,
        "is_active": link.is_active,
        "description": link.description,
        "created_at": link.created_at,
        "watch_url": f"{frontend_url}/video/watch/{link.token}"
    }
    
    return VideoPlaybackLinkRead(**link_data_dict)


@router.get("/{video_id}/links", response_model=List[VideoPlaybackLinkRead])
async def list_links(
    video_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
    request: Request = None
):
    """获取视频的所有链接"""
    # 使用前端URL
    frontend_url = settings.FRONTEND_URL
    if request:
        origin = request.headers.get("origin")
        if origin:
            frontend_url = origin
    
    video_service = VideoPlaybackService(session)
    links = video_service.list_links(
        video_id=video_id,
        current_user_id=current_user.id,
        is_admin=(current_user.role == "admin"),
        base_url=frontend_url
    )
    
    # 构建响应对象列表
    result = []
    for link in links:
        link_data = {
            "id": link.id,
            "video_id": link.video_id,
            "token": link.token,
            "view_count": link.view_count,
            "max_views": link.max_views,
            "expires_at": link.expires_at,
            "is_active": link.is_active,
            "description": link.description,
            "created_at": link.created_at,
            "watch_url": f"{frontend_url}/video/watch/{link.token}",
            "last_watch_position": link.last_watch_position or 0.0
        }
        result.append(VideoPlaybackLinkRead(**link_data))
    
    return result


@router.delete("/links/{link_id}")
async def delete_link(
    link_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """删除观看链接"""
    from app.repositories.video_playback_repository import VideoPlaybackLinkRepository
    from app.repositories.video_playback_repository import VideoPlaybackRepository
    from app.repositories.project_repository import ProjectRepository
    
    link_repo = VideoPlaybackLinkRepository(session)
    video_repo = VideoPlaybackRepository(session)
    project_repo = ProjectRepository(session)
    
    link = link_repo.get_by_id(link_id)
    if not link:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="链接不存在"
        )
    
    video = video_repo.get_by_id(link.video_id)
    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="视频不存在"
        )
    
    project = project_repo.get_by_id(video.project_id)
    if current_user.role != "admin" and project.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权访问此项目"
        )
    
    link_repo.delete(link_id)
    return {"message": "链接已删除"}


@router.get("/{video_id}/statistics")
async def get_statistics(
    video_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """获取视频统计"""
    video_service = VideoPlaybackService(session)
    return video_service.get_statistics(
        video_id=video_id,
        current_user_id=current_user.id,
        is_admin=(current_user.role == "admin")
    )


@router.post("/watch/{token}/verify")
async def verify_password(
    token: str,
    password_data: VideoPasswordVerify,
    session: Session = Depends(get_session),
    request: Request = None
):
    """验证观看链接密码"""
    from app.repositories.video_playback_repository import VideoPlaybackRepository
    
    video_service = VideoPlaybackService(session)
    link = video_service.verify_link_password(token, password_data.password)
    
    # 获取视频信息
    video_repo = VideoPlaybackRepository(session)
    video = video_repo.get_by_id(link.video_id)
    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="视频不存在"
        )
    
    # 构建响应数据
    # 使用前端URL
    frontend_url = settings.FRONTEND_URL
    if request:
        origin = request.headers.get("origin")
        if origin:
            frontend_url = origin
    
    video_data = video.model_dump()
    video_data['link_count'] = 0  # 观看页面不需要这个信息
    video_data['total_views'] = link.view_count  # 使用当前链接的观看次数
    
    link_data = {
        "id": link.id,
        "video_id": link.video_id,
        "token": link.token,
        "view_count": link.view_count,
        "max_views": link.max_views,
        "expires_at": link.expires_at.isoformat() if link.expires_at else None,
        "is_active": link.is_active,
        "description": link.description,
        "created_at": link.created_at.isoformat(),
        "watch_url": f"{frontend_url}/video/watch/{link.token}",
        "last_watch_position": link.last_watch_position or 0.0
    }
    
    return {
        "success": True,
        "message": "密码验证成功",
        "video_id": link.video_id,
        "link_id": link.id,
        "video": VideoPlaybackRead(**video_data),
        "link": link_data
    }


@router.get("/watch/{token}/video")
async def get_video_file(
    token: str,
    session: Session = Depends(get_session)
):
    """获取视频文件（需要先验证密码，但这里只检查链接有效性）"""
    from app.repositories.video_playback_repository import VideoPlaybackLinkRepository
    
    # 检查链接是否存在且有效（不验证密码，因为密码已在verify接口验证）
    link_repo = VideoPlaybackLinkRepository(session)
    link = link_repo.get_by_token(token)
    
    if not link:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="链接不存在"
        )
    
    # 检查链接是否激活
    if not link.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="链接已禁用"
        )
    
    # 检查是否过期
    if link.expires_at and link.expires_at < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="链接已过期"
        )
    
    # 检查观看次数
    if link.max_views and link.view_count >= link.max_views:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="已达到最大观看次数"
        )
    
    # 获取视频
    video_service = VideoPlaybackService(session)
    video = video_service.get_video_by_link(token)
    
    if not os.path.exists(video.file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="视频文件不存在"
        )
    
    return FileResponse(
        video.file_path,
        media_type="video/mp4",
        filename=video.file_name
    )


@router.post("/watch/{token}/record")
async def record_view(
    token: str,
    watch_duration: Optional[int] = None,
    watch_percentage: Optional[float] = None,
    request: Request = None,
    session: Session = Depends(get_session)
):
    """记录观看统计"""
    from app.repositories.video_playback_repository import VideoPlaybackLinkRepository
    
    link_repo = VideoPlaybackLinkRepository(session)
    link = link_repo.get_by_token(token)
    
    if not link:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="链接不存在"
        )
    
    # 获取客户端信息
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    referer = request.headers.get("referer")
    
    video_service = VideoPlaybackService(session)
    stat = video_service.record_view(
        link_id=link.id,
        ip_address=ip_address,
        user_agent=user_agent,
        watch_duration=watch_duration,
        watch_percentage=watch_percentage,
        referer=referer
    )
    
    return {"message": "统计已记录", "stat_id": stat.id}


@router.put("/watch/{token}/progress")
async def save_watch_progress(
    token: str,
    position: float = Form(...),
    session: Session = Depends(get_session)
):
    """保存观看进度"""
    from app.repositories.video_playback_repository import VideoPlaybackLinkRepository
    
    link_repo = VideoPlaybackLinkRepository(session)
    link = link_repo.get_by_token(token)
    
    if not link:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="链接不存在"
        )
    
    # 更新观看进度
    link.last_watch_position = max(0.0, position)  # 确保进度不为负数
    link_repo.update(link)
    
    return {"message": "进度已保存", "position": link.last_watch_position}


@router.get("/watch/{token}/progress")
async def get_watch_progress(
    token: str,
    session: Session = Depends(get_session)
):
    """获取观看进度"""
    from app.repositories.video_playback_repository import VideoPlaybackLinkRepository
    
    link_repo = VideoPlaybackLinkRepository(session)
    link = link_repo.get_by_token(token)
    
    if not link:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="链接不存在"
        )
    
    return {
        "position": link.last_watch_position or 0.0,
        "has_progress": (link.last_watch_position or 0.0) > 0
    }

