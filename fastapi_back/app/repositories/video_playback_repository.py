"""
视频回放仓库层
"""
from typing import List, Optional
from sqlmodel import Session, select
from app.models.video_playback import VideoPlayback, VideoPlaybackLink, VideoPlaybackStat


class VideoPlaybackRepository:
    """视频回放仓库"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def create(self, video: VideoPlayback) -> VideoPlayback:
        """创建视频"""
        self.session.add(video)
        self.session.commit()
        self.session.refresh(video)
        return video
    
    def get_by_id(self, video_id: int) -> Optional[VideoPlayback]:
        """根据ID获取视频"""
        return self.session.get(VideoPlayback, video_id)
    
    def list_by_project(self, project_id: int) -> List[VideoPlayback]:
        """获取项目的所有视频"""
        statement = select(VideoPlayback).where(VideoPlayback.project_id == project_id)
        return list(self.session.exec(statement))
    
    def update(self, video: VideoPlayback) -> VideoPlayback:
        """更新视频"""
        self.session.add(video)
        self.session.commit()
        self.session.refresh(video)
        return video
    
    def delete(self, video_id: int) -> bool:
        """删除视频"""
        video = self.get_by_id(video_id)
        if video:
            self.session.delete(video)
            self.session.commit()
            return True
        return False


class VideoPlaybackLinkRepository:
    """视频观看链接仓库"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def create(self, link: VideoPlaybackLink) -> VideoPlaybackLink:
        """创建链接"""
        self.session.add(link)
        self.session.commit()
        self.session.refresh(link)
        return link
    
    def get_by_id(self, link_id: int) -> Optional[VideoPlaybackLink]:
        """根据ID获取链接"""
        return self.session.get(VideoPlaybackLink, link_id)
    
    def get_by_token(self, token: str) -> Optional[VideoPlaybackLink]:
        """根据token获取链接"""
        statement = select(VideoPlaybackLink).where(VideoPlaybackLink.token == token)
        return self.session.exec(statement).first()
    
    def list_by_video(self, video_id: int) -> List[VideoPlaybackLink]:
        """获取视频的所有链接"""
        statement = select(VideoPlaybackLink).where(VideoPlaybackLink.video_id == video_id)
        return list(self.session.exec(statement))
    
    def update(self, link: VideoPlaybackLink) -> VideoPlaybackLink:
        """更新链接"""
        self.session.add(link)
        self.session.commit()
        self.session.refresh(link)
        return link
    
    def increment_view_count(self, link_id: int) -> None:
        """增加观看次数"""
        link = self.get_by_id(link_id)
        if link:
            link.view_count += 1
            self.session.add(link)
            self.session.commit()
    
    def delete(self, link_id: int) -> bool:
        """删除链接"""
        link = self.get_by_id(link_id)
        if link:
            self.session.delete(link)
            self.session.commit()
            return True
        return False


class VideoPlaybackStatRepository:
    """视频观看统计仓库"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def create(self, stat: VideoPlaybackStat) -> VideoPlaybackStat:
        """创建统计记录"""
        self.session.add(stat)
        self.session.commit()
        self.session.refresh(stat)
        return stat
    
    def list_by_video(self, video_id: int, limit: Optional[int] = None) -> List[VideoPlaybackStat]:
        """获取视频的统计记录"""
        statement = select(VideoPlaybackStat).where(
            VideoPlaybackStat.video_id == video_id
        ).order_by(VideoPlaybackStat.watched_at.desc())
        if limit:
            statement = statement.limit(limit)
        return list(self.session.exec(statement))
    
    def list_by_link(self, link_id: int, limit: Optional[int] = None) -> List[VideoPlaybackStat]:
        """获取链接的统计记录"""
        statement = select(VideoPlaybackStat).where(
            VideoPlaybackStat.link_id == link_id
        ).order_by(VideoPlaybackStat.watched_at.desc())
        if limit:
            statement = statement.limit(limit)
        return list(self.session.exec(statement))
    
    def get_statistics(self, video_id: int) -> dict:
        """获取视频统计汇总"""
        statement = select(VideoPlaybackStat).where(VideoPlaybackStat.video_id == video_id)
        stats = list(self.session.exec(statement))
        
        total_views = len(stats)
        total_duration = sum(s.watch_duration or 0 for s in stats)
        avg_duration = total_duration / total_views if total_views > 0 else 0
        avg_percentage = sum(s.watch_percentage or 0 for s in stats) / total_views if total_views > 0 else 0
        
        return {
            "total_views": total_views,
            "total_duration": total_duration,
            "avg_duration": avg_duration,
            "avg_percentage": avg_percentage,
        }

