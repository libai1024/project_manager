"""
系统设置数据访问层
"""
from typing import Optional, Dict, Any
import json
from sqlmodel import Session, select
from app.models.system_settings import SystemSettings, SystemSettingsCreate, HISTORICAL_PROJECT_DEFAULT_SETTINGS


class SystemSettingsRepository:
    """系统设置数据访问层"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def get_by_key(self, key: str) -> Optional[SystemSettings]:
        """根据键获取设置"""
        return self.session.exec(
            select(SystemSettings).where(SystemSettings.key == key)
        ).first()
    
    def get_value(self, key: str, default: Any = None) -> Any:
        """获取设置值（自动解析JSON）"""
        setting = self.get_by_key(key)
        if not setting:
            return default
        
        try:
            return json.loads(setting.value)
        except (json.JSONDecodeError, TypeError):
            return setting.value
    
    def set_value(self, key: str, value: Any, description: Optional[str] = None, category: str = "general") -> SystemSettings:
        """设置值（自动序列化为JSON）"""
        setting = self.get_by_key(key)
        
        # 序列化值
        if isinstance(value, (dict, list)):
            value_str = json.dumps(value, ensure_ascii=False)
        else:
            value_str = str(value)
        
        if setting:
            # 更新现有设置
            setting.value = value_str
            if description:
                setting.description = description
            self.session.add(setting)
            self.session.commit()
            self.session.refresh(setting)
        else:
            # 创建新设置
            setting = SystemSettings(
                key=key,
                value=value_str,
                description=description,
                category=category
            )
            self.session.add(setting)
            self.session.commit()
            self.session.refresh(setting)
        
        return setting
    
    def get_historical_project_settings(self) -> Dict[str, bool]:
        """获取历史项目功能设置"""
        settings = self.get_value("historical_project_settings", HISTORICAL_PROJECT_DEFAULT_SETTINGS)
        if isinstance(settings, dict):
            return settings
        return HISTORICAL_PROJECT_DEFAULT_SETTINGS.copy()
    
    def update_historical_project_settings(self, settings: Dict[str, bool]) -> SystemSettings:
        """更新历史项目功能设置"""
        return self.set_value(
            "historical_project_settings",
            settings,
            description="历史项目功能开关设置",
            category="historical_project"
        )
    
    def is_feature_enabled(self, feature_key: str) -> bool:
        """检查特定功能是否启用"""
        settings = self.get_historical_project_settings()
        return settings.get(feature_key, False)
    
    def list_all(self) -> list[SystemSettings]:
        """获取所有系统设置"""
        return list(self.session.exec(select(SystemSettings)).all())
    
    def update(self, key: str, value: bool) -> SystemSettings:
        """更新单个设置的值（布尔值）"""
        setting = self.get_by_key(key)
        if not setting:
            # 如果设置不存在，创建它
            setting = SystemSettings(
                key=key,
                value=json.dumps(value),
                description=f"系统设置: {key}",
                category="general"
            )
            self.session.add(setting)
        else:
            setting.value = json.dumps(value)
            self.session.add(setting)
        self.session.commit()
        self.session.refresh(setting)
        return setting
    
    def get_int_value(self, key: str, default: int = 0) -> int:
        """获取整数类型的设置值"""
        setting = self.get_by_key(key)
        if not setting:
            return default
        
        try:
            value = json.loads(setting.value)
            if isinstance(value, int):
                return value
            elif isinstance(value, (float, str)):
                return int(float(value))
            return default
        except (json.JSONDecodeError, TypeError, ValueError):
            try:
                return int(float(setting.value))
            except (ValueError, TypeError):
                return default
    
    def update_int(self, key: str, value: int, description: Optional[str] = None, category: str = "general") -> SystemSettings:
        """更新整数类型的设置值"""
        return self.set_value(key, value, description, category)

