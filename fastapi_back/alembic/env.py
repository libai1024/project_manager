"""
Alembic environment configuration for database migrations.
"""
from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlmodel import SQLModel
from app.core.config import settings

# Import all models to ensure they are registered with SQLModel.metadata
from app.models.user import User
from app.models.platform import Platform
from app.models.project import Project, ProjectStep
from app.models.attachment import Attachment
from app.models.attachment_folder import AttachmentFolder
from app.models.todo import Todo
from app.models.project_log import ProjectLog
from app.models.project_part import ProjectPart
from app.models.github_commit import GitHubCommit
from app.models.video_playback import VideoPlayback, VideoPlaybackLink, VideoPlaybackStat
from app.models.refresh_token import RefreshToken
from app.models.token_blacklist import TokenBlacklist
from app.models.login_log import LoginLog
from app.models.step_template import StepTemplate, StepTemplateItem
from app.models.tag import Tag, ProjectTag, HistoricalProjectTag
from app.models.historical_project import HistoricalProject
from app.models.system_settings import SystemSettings

# Alembic Config object
config = context.config

# Override sqlalchemy.url with settings from app config
# This allows using the same DATABASE_URL as the application
# For local development, use the database in the parent directory's data folder
import os
db_url = settings.DATABASE_URL
# Check if we're running from fastapi_back directory
if db_url.startswith("sqlite:///./data/") and not os.path.exists("./data"):
    # Adjust path for running from fastapi_back directory
    db_url = "sqlite:///../data/project_manager.db"
config.set_main_option("sqlalchemy.url", db_url)

# Setup logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Target metadata for autogenerate support
target_metadata = SQLModel.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.
    """
    # For SQLite, we need special connect_args
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
        connect_args={"check_same_thread": False},  # SQLite specific
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
