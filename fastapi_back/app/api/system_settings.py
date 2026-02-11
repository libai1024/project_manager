"""
系统设置API路由层
用于管理系统级配置，包括历史项目功能开关等
"""
import logging
from typing import Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from app.core.database import get_session
from app.core.dependencies import get_current_active_user, get_current_admin_user
from app.repositories.system_settings_repository import SystemSettingsRepository
from app.models.user import User
from app.models.system_settings import SystemSettingsRead, SystemSettingsUpdate, SystemSettingsIntRead, SystemSettingsIntUpdate

logger = logging.getLogger(__name__)
router = APIRouter(tags=["系统设置"])


@router.get("/historical-project", response_model=Dict[str, bool])
async def get_historical_project_settings(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_admin_user)
):
    """获取历史项目功能设置（仅管理员）"""
    settings_repo = SystemSettingsRepository(session)
    try:
        return settings_repo.get_historical_project_settings()
    except Exception as e:
        logger.error(f"Error in get_historical_project_settings API: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.put("/historical-project", response_model=Dict[str, bool])
async def update_historical_project_settings(
    settings: Dict[str, bool],
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_admin_user)
):
    """更新历史项目功能设置（仅管理员）"""
    settings_repo = SystemSettingsRepository(session)
    try:
        settings_repo.update_historical_project_settings(settings)
        return settings_repo.get_historical_project_settings()
    except Exception as e:
        logger.error(f"Error in update_historical_project_settings API: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/token-duration", response_model=Dict[str, int])
async def get_token_duration_settings(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """获取 Token 持续时间设置（所有用户可读）"""
    settings_repo = SystemSettingsRepository(session)
    from app.core.config import settings as config_settings
    
    access_token_minutes = settings_repo.get_int_value("access_token_expire_minutes", config_settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_token_days = settings_repo.get_int_value("refresh_token_expire_days", config_settings.REFRESH_TOKEN_EXPIRE_DAYS)
    
    return {
        "access_token_expire_minutes": access_token_minutes,
        "refresh_token_expire_days": refresh_token_days
    }


@router.put("/token-duration", response_model=Dict[str, int])
async def update_token_duration_settings(
    settings: Dict[str, int],
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_admin_user)
):
    """更新 Token 持续时间设置（仅管理员）"""
    settings_repo = SystemSettingsRepository(session)
    
    # 验证输入值
    access_token_minutes = settings.get("access_token_expire_minutes")
    refresh_token_days = settings.get("refresh_token_expire_days")
    
    if access_token_minutes is not None:
        if access_token_minutes < 1 or access_token_minutes > 1440:  # 1分钟到24小时
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Access token expire minutes must be between 1 and 1440 (24 hours)"
            )
        settings_repo.update_int(
            "access_token_expire_minutes",
            access_token_minutes,
            description="Access Token 过期时间（分钟）",
            category="token"
        )
    
    if refresh_token_days is not None:
        if refresh_token_days < 1 or refresh_token_days > 365:  # 1天到1年
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Refresh token expire days must be between 1 and 365"
            )
        settings_repo.update_int(
            "refresh_token_expire_days",
            refresh_token_days,
            description="Refresh Token 过期时间（天）",
            category="token"
        )
    
    # 返回更新后的值
    from app.core.config import settings as config_settings
    access_token_minutes = settings_repo.get_int_value("access_token_expire_minutes", config_settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_token_days = settings_repo.get_int_value("refresh_token_expire_days", config_settings.REFRESH_TOKEN_EXPIRE_DAYS)
    
    return {
        "access_token_expire_minutes": access_token_minutes,
        "refresh_token_expire_days": refresh_token_days
    }


@router.get("/plugin-settings", response_model=Dict[str, List[int]])
async def get_plugin_settings(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """获取插件设置（所有用户可读，全局共享）"""
    settings_repo = SystemSettingsRepository(session)
    
    # 插件设置键名
    plugin_keys = {
        "graduation": "graduationPluginEnabledProjects",
        "github": "githubPluginEnabledProjects",
        "parts": "partsPluginEnabledProjects",
        "video-playback": "videoPlaybackPluginEnabledProjects"
    }
    
    result = {}
    for plugin_type, key in plugin_keys.items():
        project_ids = settings_repo.get_value(key, [])
        if isinstance(project_ids, list):
            result[plugin_type] = project_ids
        else:
            result[plugin_type] = []
    
    return result


@router.put("/plugin-settings", response_model=Dict[str, List[int]])
async def update_plugin_settings(
    settings: Dict[str, List[int]],
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """更新插件设置（所有用户可写，全局共享）"""
    settings_repo = SystemSettingsRepository(session)
    
    # 插件设置键名和描述
    plugin_configs = {
        "graduation": ("graduationPluginEnabledProjects", "毕业设计插件启用的项目ID列表"),
        "github": ("githubPluginEnabledProjects", "GitHub插件启用的项目ID列表"),
        "parts": ("partsPluginEnabledProjects", "元器件清单插件启用的项目ID列表"),
        "video-playback": ("videoPlaybackPluginEnabledProjects", "视频回放插件启用的项目ID列表")
    }
    
    # 更新每个插件的设置
    for plugin_type, project_ids in settings.items():
        if plugin_type in plugin_configs:
            key, description = plugin_configs[plugin_type]
            # 确保 project_ids 是整数列表
            if isinstance(project_ids, list):
                validated_ids = [int(pid) for pid in project_ids if isinstance(pid, (int, str)) and str(pid).isdigit()]
                settings_repo.set_value(
                    key,
                    validated_ids,
                    description=description,
                    category="plugin"
                )
    
    # 返回更新后的所有设置
    result = {}
    for plugin_type, (key, _) in plugin_configs.items():
        project_ids = settings_repo.get_value(key, [])
        if isinstance(project_ids, list):
            result[plugin_type] = project_ids
        else:
            result[plugin_type] = []
    
    return result


@router.put("/{key}", response_model=SystemSettingsRead)
async def update_setting(
    key: str,
    data: SystemSettingsUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_admin_user)
):
    """更新系统设置（仅管理员）"""
    settings_repo = SystemSettingsRepository(session)
    try:
        setting = settings_repo.update(key, data.value)
        return SystemSettingsRead(
            id=setting.id,
            key=setting.key,
            value=data.value,  # 直接使用传入的布尔值
            description=setting.description,
            category=setting.category,
            created_at=setting.created_at,
            updated_at=setting.updated_at
        )
    except Exception as e:
        logger.error(f"Error in update_setting API: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/{key}", response_model=SystemSettingsRead)
async def get_setting(
    key: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """获取系统设置（所有用户可读）"""
    settings_repo = SystemSettingsRepository(session)
    setting = settings_repo.get_by_key(key)
    if not setting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="设置不存在"
        )
    # 解析 value 为布尔值
    import json
    try:
        value = json.loads(setting.value)
        if isinstance(value, bool):
            bool_value = value
        else:
            bool_value = str(value).lower() in ('true', '1', 'yes')
    except (json.JSONDecodeError, TypeError):
        bool_value = str(setting.value).lower() in ('true', '1', 'yes')
    
    return SystemSettingsRead(
        id=setting.id,
        key=setting.key,
        value=bool_value,
        description=setting.description,
        category=setting.category,
        created_at=setting.created_at,
        updated_at=setting.updated_at
    )


@router.get("/", response_model=List[SystemSettingsRead])
async def get_all_settings(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """获取所有系统设置（所有用户可读）"""
    settings_repo = SystemSettingsRepository(session)
    try:
        settings = settings_repo.list_all()
        import json
        result = []
        for s in settings:
            try:
                value = json.loads(s.value)
                if isinstance(value, bool):
                    bool_value = value
                else:
                    bool_value = str(value).lower() in ('true', '1', 'yes')
            except (json.JSONDecodeError, TypeError):
                bool_value = str(s.value).lower() in ('true', '1', 'yes')
            
            result.append(SystemSettingsRead(
                id=s.id,
                key=s.key,
                value=bool_value,
                description=s.description,
                category=s.category,
                created_at=s.created_at,
                updated_at=s.updated_at
            ))
        return result
    except Exception as e:
        logger.error(f"Error in get_all_settings API: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

