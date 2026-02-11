"""
视频回放服务层
"""
from typing import List, Optional
from sqlmodel import Session
from datetime import datetime, timedelta
import secrets
import hashlib
import os
import uuid
from fastapi import HTTPException, status

from app.repositories.video_playback_repository import (
    VideoPlaybackRepository,
    VideoPlaybackLinkRepository,
    VideoPlaybackStatRepository
)
from app.repositories.project_repository import ProjectRepository
from app.models.video_playback import (
    VideoPlayback,
    VideoPlaybackLink,
    VideoPlaybackStat,
    VideoPlaybackCreate,
    VideoPlaybackUpdate,
    VideoPlaybackLinkCreate,
    VideoStatus
)


class VideoPlaybackService:
    """视频回放服务"""
    
    def __init__(self, session: Session):
        self.session = session
        self.video_repo = VideoPlaybackRepository(session)
        self.link_repo = VideoPlaybackLinkRepository(session)
        self.stat_repo = VideoPlaybackStatRepository(session)
        self.project_repo = ProjectRepository(session)
        self.upload_dir = "uploads/videos"
        os.makedirs(self.upload_dir, exist_ok=True)
    
    def _hash_password(self, password: str) -> str:
        """密码哈希"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def _verify_password(self, password: str, hashed: str) -> bool:
        """验证密码"""
        return self._hash_password(password) == hashed
    
    def _generate_token(self) -> str:
        """生成唯一token"""
        return secrets.token_urlsafe(32)
    
    def create_video(
        self,
        project_id: int,
        title: str,
        file_path: str,
        file_name: str,
        file_size: int,
        current_user_id: int,
        is_admin: bool
    ) -> VideoPlayback:
        """创建视频记录"""
        # 验证项目权限
        project = self.project_repo.get_by_id(project_id)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="项目不存在"
            )
        
        if not is_admin and project.user_id != current_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权访问此项目"
            )
        
        video = VideoPlayback(
            project_id=project_id,
            title=title,
            file_path=file_path,
            file_name=file_name,
            file_size=file_size,
            status=VideoStatus.READY
        )
        return self.video_repo.create(video)
    
    def list_videos(
        self,
        project_id: int,
        current_user_id: int,
        is_admin: bool
    ) -> List[VideoPlayback]:
        """获取项目的所有视频"""
        # 验证项目权限
        project = self.project_repo.get_by_id(project_id)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="项目不存在"
            )
        
        if not is_admin and project.user_id != current_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权访问此项目"
            )
        
        videos = self.video_repo.list_by_project(project_id)
        # 注意：link_count 和 total_views 是计算字段，不在 VideoPlayback 模型中
        # 这些字段会在 API 层通过 VideoPlaybackRead 返回
        return videos
    
    def update_video(
        self,
        video_id: int,
        update_data: VideoPlaybackUpdate,
        current_user_id: int,
        is_admin: bool
    ) -> VideoPlayback:
        """更新视频"""
        video = self.video_repo.get_by_id(video_id)
        if not video:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="视频不存在"
            )
        
        # 验证项目权限
        project = self.project_repo.get_by_id(video.project_id)
        if not is_admin and project.user_id != current_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权访问此项目"
            )
        
        update_dict = update_data.model_dump(exclude_unset=True)
        for key, value in update_dict.items():
            setattr(video, key, value)
        
        video.updated_at = datetime.utcnow()
        return self.video_repo.update(video)
    
    def delete_video(
        self,
        video_id: int,
        current_user_id: int,
        is_admin: bool
    ) -> bool:
        """删除视频"""
        video = self.video_repo.get_by_id(video_id)
        if not video:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="视频不存在"
            )
        
        # 验证项目权限
        project = self.project_repo.get_by_id(video.project_id)
        if not is_admin and project.user_id != current_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权访问此项目"
            )
        
        # 删除文件
        if os.path.exists(video.file_path):
            try:
                os.remove(video.file_path)
            except Exception:
                pass  # 忽略删除文件错误
        
        # 删除缩略图
        if video.thumbnail_path and os.path.exists(video.thumbnail_path):
            try:
                os.remove(video.thumbnail_path)
            except Exception:
                pass
        
        return self.video_repo.delete(video_id)
    
    def create_link(
        self,
        video_id: int,
        link_data: VideoPlaybackLinkCreate,
        current_user_id: int,
        is_admin: bool,
        base_url: str
    ) -> VideoPlaybackLink:
        """创建观看链接"""
        video = self.video_repo.get_by_id(video_id)
        if not video:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="视频不存在"
            )
        
        # 验证项目权限
        project = self.project_repo.get_by_id(video.project_id)
        if not is_admin and project.user_id != current_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权访问此项目"
            )
        
        # 生成token
        token = self._generate_token()
        
        # 计算过期时间
        expires_at = None
        if link_data.expires_in_days:
            expires_at = datetime.utcnow() + timedelta(days=link_data.expires_in_days)
        
        # 哈希密码
        hashed_password = self._hash_password(link_data.password)
        
        link = VideoPlaybackLink(
            video_id=video_id,
            token=token,
            password=hashed_password,
            expires_at=expires_at,
            max_views=link_data.max_views,
            description=link_data.description,
            created_by=current_user_id
        )
        
        link = self.link_repo.create(link)
        
        # 注意：watch_url 不在 VideoPlaybackLink 模型中
        # 将在 API 层通过 VideoPlaybackLinkRead 返回
        
        return link
    
    def verify_link_password(self, token: str, password: str) -> VideoPlaybackLink:
        """验证链接密码"""
        link = self.link_repo.get_by_token(token)
        if not link:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="链接不存在"
            )
        
        # 检查是否激活
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
        
        # 验证密码
        if not self._verify_password(password, link.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="密码错误"
            )
        
        return link
    
    def get_video_by_link(self, token: str) -> VideoPlayback:
        """通过链接token获取视频"""
        link = self.link_repo.get_by_token(token)
        if not link:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="链接不存在"
            )
        
        video = self.video_repo.get_by_id(link.video_id)
        if not video:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="视频不存在"
            )
        
        return video
    
    def record_view(
        self,
        link_id: int,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        watch_duration: Optional[int] = None,
        watch_percentage: Optional[float] = None,
        referer: Optional[str] = None
    ) -> VideoPlaybackStat:
        """记录观看统计"""
        link = self.link_repo.get_by_id(link_id)
        if not link:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="链接不存在"
            )
        
        # 增加观看次数
        self.link_repo.increment_view_count(link_id)
        
        # 创建统计记录
        stat = VideoPlaybackStat(
            video_id=link.video_id,
            link_id=link_id,
            ip_address=ip_address,
            user_agent=user_agent,
            watch_duration=watch_duration,
            watch_percentage=watch_percentage,
            referer=referer
        )
        
        return self.stat_repo.create(stat)
    
    def list_links(
        self,
        video_id: int,
        current_user_id: int,
        is_admin: bool,
        base_url: str
    ) -> List[VideoPlaybackLink]:
        """获取视频的所有链接"""
        video = self.video_repo.get_by_id(video_id)
        if not video:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="视频不存在"
            )
        
        # 验证项目权限
        project = self.project_repo.get_by_id(video.project_id)
        if not is_admin and project.user_id != current_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权访问此项目"
            )
        
        links = self.link_repo.list_by_video(video_id)
        # 注意：watch_url 不在 VideoPlaybackLink 模型中
        # 将在 API 层通过 VideoPlaybackLinkRead 返回
        return links
    
    def get_statistics(
        self,
        video_id: int,
        current_user_id: int,
        is_admin: bool
    ) -> dict:
        """获取视频统计"""
        video = self.video_repo.get_by_id(video_id)
        if not video:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="视频不存在"
            )
        
        # 验证项目权限
        project = self.project_repo.get_by_id(video.project_id)
        if not is_admin and project.user_id != current_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权访问此项目"
            )
        
        return self.stat_repo.get_statistics(video_id)

