"""
视频回放插件数据模型
"""
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING
from datetime import datetime, timedelta
from enum import Enum

if TYPE_CHECKING:
    from app.models.project import Project
    from app.models.historical_project import HistoricalProject


class VideoStatus(str, Enum):
    """视频状态"""
    UPLOADING = "上传中"
    PROCESSING = "处理中"
    READY = "就绪"
    ERROR = "错误"


class VideoPlaybackBase(SQLModel):
    """视频回放基础模型"""
    project_id: Optional[int] = Field(default=None, foreign_key="project.id", description="所属项目ID")
    historical_project_id: Optional[int] = Field(default=None, foreign_key="historicalproject.id", description="所属历史项目ID")
    title: str = Field(description="视频标题")
    description: Optional[str] = Field(default=None, description="视频描述")
    file_path: str = Field(description="视频文件路径")
    file_name: str = Field(description="原始文件名")
    file_size: int = Field(description="文件大小（字节）")
    duration: Optional[int] = Field(default=None, description="视频时长（秒）")
    thumbnail_path: Optional[str] = Field(default=None, description="缩略图路径")
    status: str = Field(default=VideoStatus.UPLOADING, description="视频状态")


class VideoPlayback(VideoPlaybackBase, table=True):
    """视频回放表"""
    __tablename__ = "videoplayback"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow, sa_column_kwargs={"onupdate": datetime.utcnow})
    
    # 关系
    project: Optional["Project"] = Relationship(back_populates="video_playbacks")
    historical_project: Optional["HistoricalProject"] = Relationship(back_populates="video_playbacks")
    links: list["VideoPlaybackLink"] = Relationship(back_populates="video")
    stats: list["VideoPlaybackStat"] = Relationship(back_populates="video")


class VideoPlaybackLinkBase(SQLModel):
    """视频观看链接基础模型"""
    video_id: int = Field(foreign_key="videoplayback.id", description="视频ID")
    password: str = Field(description="访问密码（加密存储）")
    expires_at: Optional[datetime] = Field(default=None, description="过期时间")
    max_views: Optional[int] = Field(default=None, description="最大观看次数")
    is_active: bool = Field(default=True, description="是否激活")
    description: Optional[str] = Field(default=None, description="链接描述")
    last_watch_position: Optional[float] = Field(default=0.0, description="上次观看位置（秒）")


class VideoPlaybackLink(VideoPlaybackLinkBase, table=True):
    """视频观看链接表"""
    __tablename__ = "videoplaybacklink"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    token: str = Field(unique=True, index=True, description="访问令牌（唯一标识）")
    view_count: int = Field(default=0, description="已观看次数")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: int = Field(description="创建者用户ID")
    
    # 关系
    video: VideoPlayback = Relationship(back_populates="links")
    stats: list["VideoPlaybackStat"] = Relationship(back_populates="link")


class VideoPlaybackStatBase(SQLModel):
    """视频观看统计基础模型"""
    video_id: int = Field(foreign_key="videoplayback.id", description="视频ID")
    link_id: int = Field(foreign_key="videoplaybacklink.id", description="链接ID")
    ip_address: Optional[str] = Field(default=None, description="IP地址")
    user_agent: Optional[str] = Field(default=None, description="用户代理")
    watch_duration: Optional[int] = Field(default=None, description="观看时长（秒）")
    watch_percentage: Optional[float] = Field(default=None, description="观看百分比")
    referer: Optional[str] = Field(default=None, description="来源页面")


class VideoPlaybackStat(VideoPlaybackStatBase, table=True):
    """视频观看统计表"""
    __tablename__ = "videoplaybackstat"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    watched_at: datetime = Field(default_factory=datetime.utcnow)
    
    # 关系
    video: VideoPlayback = Relationship(back_populates="stats")
    link: VideoPlaybackLink = Relationship(back_populates="stats")


# API 模型
class VideoPlaybackCreate(SQLModel):
    """创建视频"""
    title: str
    description: Optional[str] = None


class VideoPlaybackRead(VideoPlaybackBase):
    """读取视频"""
    id: int
    created_at: datetime
    updated_at: datetime
    link_count: int = 0  # 链接数量
    total_views: int = 0  # 总观看次数


class VideoPlaybackUpdate(SQLModel):
    """更新视频"""
    title: Optional[str] = None
    description: Optional[str] = None


class VideoPlaybackLinkCreate(SQLModel):
    """创建观看链接"""
    password: str
    expires_in_days: Optional[int] = Field(default=None, description="有效期（天数），None表示永久")
    max_views: Optional[int] = Field(default=None, description="最大观看次数，None表示无限制")
    description: Optional[str] = None


class VideoPlaybackLinkRead(SQLModel):
    """读取观看链接"""
    id: int
    video_id: int
    token: str
    view_count: int
    max_views: Optional[int]
    expires_at: Optional[datetime]
    is_active: bool
    description: Optional[str]
    created_at: datetime
    watch_url: str  # 完整观看URL
    last_watch_position: Optional[float] = 0.0  # 上次观看位置（秒）


class VideoPlaybackStatRead(SQLModel):
    """读取观看统计"""
    id: int
    video_id: int
    link_id: int
    watched_at: datetime
    ip_address: Optional[str]
    watch_duration: Optional[int]
    watch_percentage: Optional[float]


class VideoPasswordVerify(SQLModel):
    """密码验证"""
    password: str

