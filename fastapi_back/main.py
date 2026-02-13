from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import engine
from app.exceptions.handlers import setup_exception_handlers
from sqlmodel import SQLModel
import logging

# 首先导入所有模型以确保关系正确建立
from app.models.user import User
from app.models.platform import Platform
from app.models.project import Project, ProjectStep
from app.models.attachment import Attachment
from app.models.attachment_folder import AttachmentFolder
from app.models.todo import Todo
from app.models.project_log import ProjectLog
from app.models.step_template import StepTemplate, StepTemplateItem
from app.models.project_part import ProjectPart
from app.models.github_commit import GitHubCommit
from app.models.video_playback import VideoPlayback, VideoPlaybackLink, VideoPlaybackStat
from app.models.refresh_token import RefreshToken
from app.models.token_blacklist import TokenBlacklist
from app.models.login_log import LoginLog
from app.models.tag import Tag, ProjectTag, HistoricalProjectTag
from app.models.historical_project import HistoricalProjectReadWithRelations

# 导入 Schema（DTO）
from app.schemas.project import ProjectReadWithRelations, ProjectStepRead
from app.schemas.platform import PlatformRead
from app.schemas.tag import TagRead

# 重建模型以解析前向引用（Pydantic 2.x 要求）
ProjectReadWithRelations.model_rebuild()
HistoricalProjectReadWithRelations.model_rebuild()

# 然后导入API路由
from app.api import auth, platforms, projects, dashboard, users, attachments, attachment_folders, todos, project_logs, step_templates, project_parts, github_commits, video_playbacks, historical_projects, system_settings, tags

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def run_migrations():
    """Run database migrations on application startup.

    Uses Alembic for database migrations. Falls back to SQLModel.metadata.create_all
    if Alembic is not configured or migrations fail (useful for development).
    """
    try:
        from alembic.config import Config
        from alembic import command
        import os

        # Check if alembic.ini exists
        alembic_ini_path = os.path.join(os.path.dirname(__file__), "alembic.ini")
        if os.path.exists(alembic_ini_path):
            alembic_cfg = Config(alembic_ini_path)
            command.upgrade(alembic_cfg, "head")
            logger.info("Database migrations completed successfully via Alembic")
        else:
            logger.warning("alembic.ini not found, falling back to create_all()")
            SQLModel.metadata.create_all(engine)
    except Exception as e:
        logger.warning(f"Could not run Alembic migrations: {e}")
        logger.info("Falling back to SQLModel.metadata.create_all()")
        SQLModel.metadata.create_all(engine)


# Run database migrations on startup
run_migrations()

app = FastAPI(
    title="外包项目管理系统",
    description="外包项目管理系统 API",
    version="1.0.0"
)

# 添加请求日志中间件（必须在 CORS 中间件之后，但会在路由处理之前执行）
@app.middleware("http")
async def log_requests(request, call_next):
    import logging
    logger = logging.getLogger(__name__)
    
    # 跳过 OPTIONS 预检请求的详细日志（CORS 预检请求不包含 Authorization header）
    if request.method == "OPTIONS":
        response = await call_next(request)
        return response
    
    # 记录请求信息（不包括敏感信息）
    # 尝试多种方式获取 header（不区分大小写）
    auth_header = (
        request.headers.get("authorization") or 
        request.headers.get("Authorization") or
        request.headers.get("AUTHORIZATION")
    )
    
    # 详细记录特定 API 的请求（用于调试）
    is_historical_project_request = "/historical-projects" in str(request.url.path)
    is_auth_api_request = "/auth/login-logs" in str(request.url.path) or "/auth/refresh-tokens" in str(request.url.path)
    
    if auth_header:
        auth_preview = auth_header[7:37] if len(auth_header) > 7 else 'invalid'
        logger.info(f"[请求中间件] {request.method} {request.url.path} - Auth: Bearer {auth_preview}... (长度: {len(auth_header)})")
        if is_historical_project_request:
            logger.info(f"[历史项目请求] 找到 Authorization header，长度: {len(auth_header)}")
        if is_auth_api_request:
            logger.info(f"[Token管理API] {request.method} {request.url.path} - 找到 Authorization header，长度: {len(auth_header)}")
    else:
        logger.warning(f"[请求中间件] {request.method} {request.url.path} - Auth: None (missing Authorization header)")
        if is_historical_project_request:
            logger.error(f"[历史项目请求] ⚠️ 未找到 Authorization header！")
            # 列出所有请求头以便调试
            logger.error(f"[历史项目请求] 请求头列表: {list(request.headers.keys())}")
            # 列出所有 header 的值（用于调试）
            for key in request.headers.keys():
                value = request.headers.get(key)
                logger.error(f"[历史项目请求]   {key}: {str(value)[:50] if value else None}...")
        elif is_auth_api_request:
            logger.error(f"[Token管理API] ⚠️ {request.method} {request.url.path} - 未找到 Authorization header！")
            # 列出所有请求头以便调试
            logger.error(f"[Token管理API] 请求头列表: {list(request.headers.keys())}")
            # 列出所有 header 的值（用于调试）
            for key in request.headers.keys():
                value = request.headers.get(key)
                logger.error(f"[Token管理API]   {key}: {str(value)[:50] if value else None}...")
        else:
            # 非特殊请求，只记录基本信息
            logger.warning(f"Request headers: {list(request.headers.keys())}")
            for key in request.headers.keys():
                logger.warning(f"  {key}: {request.headers.get(key)[:50] if request.headers.get(key) else None}...")
    
    response = await call_next(request)
    return response

# 配置CORS
# 开发环境：允许所有来源（包括局域网）
# 生产环境：请设置 CORS_ALLOW_ALL=False 并配置具体的 CORS_ORIGINS
if settings.CORS_ALLOW_ALL:
    # 开发环境：允许所有来源
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # 允许所有来源
        allow_credentials=False,  # 当 allow_origins=["*"] 时，allow_credentials 必须为 False
        allow_methods=["*"],
        allow_headers=["*"],  # 允许所有 headers，包括 Authorization
        expose_headers=["*"],  # 暴露所有响应头
    )
else:
    # 生产环境：只允许配置的来源
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],  # 允许所有 headers，包括 Authorization
        expose_headers=["*"],  # 暴露所有响应头
    )

# 注册异常处理器
setup_exception_handlers(app)

# 注册路由
app.include_router(auth.router, prefix="/api/auth", tags=["认证"])
app.include_router(platforms.router, prefix="/api/platforms", tags=["平台管理"])
app.include_router(projects.router, prefix="/api/projects", tags=["项目管理"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["Dashboard"])
app.include_router(users.router, prefix="/api/users", tags=["用户管理"])
app.include_router(attachments.router, prefix="/api/attachments", tags=["附件管理"])
app.include_router(attachment_folders.router, prefix="/api/attachment-folders", tags=["附件文件夹管理"])
app.include_router(todos.router, prefix="/api/todos", tags=["待办管理"])
app.include_router(project_logs.router, prefix="/api/project-logs", tags=["项目日志"])
app.include_router(step_templates.router, prefix="/api/step-templates", tags=["步骤模板管理"])
app.include_router(project_parts.router, prefix="/api/project-parts", tags=["配件清单"])
app.include_router(github_commits.router, prefix="/api", tags=["GitHub Commits"])
app.include_router(video_playbacks.router, prefix="/api", tags=["视频回放"])
app.include_router(historical_projects.router, prefix="/api/historical-projects", tags=["历史项目管理"])
app.include_router(system_settings.router, prefix="/api/system-settings", tags=["系统设置"])
app.include_router(tags.router, prefix="/api/tags", tags=["标签管理"])


@app.get("/")
async def root():
    return {"message": "外包项目管理系统 API", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    return {"status": "ok"}

