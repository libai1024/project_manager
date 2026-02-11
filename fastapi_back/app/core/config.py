from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # 数据库配置
    DATABASE_URL: str = "sqlite:///./project_manager.db"
    
    # JWT配置
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15  # 15分钟（企业级：短期访问令牌）
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30  # 30天（刷新令牌）
    
    # 安全配置
    MAX_LOGIN_ATTEMPTS: int = 5  # 最大登录尝试次数
    LOCKOUT_DURATION_MINUTES: int = 30  # 账户锁定时长（分钟）
    PASSWORD_MIN_LENGTH: int = 8  # 密码最小长度
    PASSWORD_REQUIRE_UPPERCASE: bool = True  # 要求大写字母
    PASSWORD_REQUIRE_LOWERCASE: bool = True  # 要求小写字母
    PASSWORD_REQUIRE_NUMBER: bool = True  # 要求数字
    PASSWORD_REQUIRE_SPECIAL: bool = False  # 要求特殊字符
    PASSWORD_EXPIRE_DAYS: Optional[int] = None  # 密码过期天数（None表示不过期）
    
    # CORS配置
    # 允许 localhost 和局域网访问（开发环境）
    # 生产环境请修改为具体的域名
    # 注意：当 allow_credentials=True 时，不能使用 "*"，需要列出具体域名
    # 开发环境可以使用正则表达式匹配局域网IP
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        # 允许所有 localhost 端口
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
        # 允许局域网访问（使用正则表达式匹配 192.168.x.x, 10.x.x.x, 172.16-31.x.x）
        # 注意：FastAPI CORS 不支持正则，需要在 main.py 中动态处理
    ]
    
    # 开发模式：是否允许所有来源（仅开发环境使用）
    CORS_ALLOW_ALL: bool = True  # 开发环境设为 True，生产环境设为 False
    
    # 前端URL配置（用于生成外部链接）
    FRONTEND_URL: str = "http://localhost:5173"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False
    )


settings = Settings()

