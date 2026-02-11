from sqlmodel import SQLModel
from app.models.user import User
from app.models.platform import Platform
from app.models.project import Project, ProjectStep
from app.models.attachment import Attachment
from app.models.todo import Todo
from app.models.project_log import ProjectLog
from app.models.project_part import ProjectPart
from app.models.github_commit import GitHubCommit
from app.models.video_playback import VideoPlayback, VideoPlaybackLink, VideoPlaybackStat
from app.models.refresh_token import RefreshToken
from app.models.token_blacklist import TokenBlacklist
from app.models.login_log import LoginLog
from app.models.historical_project import HistoricalProject
from app.models.system_settings import SystemSettings
# SQLModel的Base
Base = SQLModel.metadata

__all__ = [
    "Base",
    "User",
    "Platform",
    "Project",
    "ProjectStep",
    "Attachment",
    "Todo",
    "ProjectLog",
    "ProjectPart",
    "GitHubCommit",
    "VideoPlayback",
    "VideoPlaybackLink",
    "VideoPlaybackStat",
    "RefreshToken",
    "TokenBlacklist",
    "LoginLog",
    "HistoricalProject",
    "SystemSettings",
]

