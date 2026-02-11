"""
系统设置模型
用于存储系统级配置，包括历史项目功能开关等
"""
from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime


class SystemSettingsBase(SQLModel):
    """系统设置基础模型"""
    key: str = Field(unique=True, index=True, description="设置键")
    value: str = Field(description="设置值（JSON字符串）")
    description: Optional[str] = Field(default=None, description="设置描述")
    category: str = Field(default="general", description="设置分类")


class SystemSettings(SystemSettingsBase, table=True):
    """系统设置表"""
    __tablename__ = "systemsettings"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.utcnow, sa_column_kwargs={"onupdate": datetime.utcnow}, description="更新时间")


class SystemSettingsCreate(SQLModel):
    """创建系统设置"""
    key: str
    value: str
    description: Optional[str] = None
    category: str = "general"


class SystemSettingsUpdate(SQLModel):
    """更新系统设置"""
    value: bool | int | str  # 支持布尔值、整数和字符串
    description: Optional[str] = None


class SystemSettingsRead(SQLModel):
    """读取系统设置"""
    id: int
    key: str
    value: bool | int | str  # 返回布尔值、整数或字符串
    description: Optional[str] = None
    category: str = "general"
    created_at: datetime
    updated_at: datetime


class SystemSettingsIntUpdate(SQLModel):
    """更新整数类型系统设置"""
    value: int
    description: Optional[str] = None


class SystemSettingsIntRead(SQLModel):
    """读取整数类型系统设置"""
    id: int
    key: str
    value: int
    description: Optional[str] = None
    category: str = "general"
    created_at: datetime
    updated_at: datetime


# 历史项目功能开关的默认配置
HISTORICAL_PROJECT_DEFAULT_SETTINGS = {
    "enable_project_management": True,  # 是否启用项目管理功能
    "enable_resource_management": True,  # 是否启用资源管理功能
    "enable_todo_management": True,  # 是否启用待办管理功能
    "enable_log_management": True,  # 是否启用日志管理功能
    "enable_part_management": True,  # 是否启用配件管理功能
    "enable_github_integration": True,  # 是否启用GitHub集成
    "enable_video_playback": True,  # 是否启用视频回放功能
}

