"""
Schemas模块

包含所有Pydantic Schema定义，与ORM模型分离。
符合国内互联网企业级规范。
"""

# 基础Schema
from app.schemas.base import (
    BaseSchema,
    BaseEntity,
    PaginationParams,
    PagedResult,
    SimpleResponse,
    IDResponse,
    CountResponse,
    DateRangeParams,
    SearchParams,
    OrderParams,
    QueryParams,
    DateQueryParams,
)

# 用户相关
from app.schemas.user import (
    UserBase,
    UserCreate,
    UserUpdate,
    UserRead,
    Token,
    TokenData,
    LoginRequest,
    RefreshTokenRequest,
)

# 平台相关
from app.schemas.platform import (
    PlatformBase,
    PlatformCreate,
    PlatformUpdate,
    PlatformRead,
    PlatformList,
)

# 标签相关
from app.schemas.tag import (
    TagBase,
    TagCreate,
    TagUpdate,
    TagRead,
    TagList,
    ProjectTagCreate,
    HistoricalProjectTagCreate,
)

# 项目相关
from app.schemas.project import (
    ProjectBase,
    ProjectCreate,
    ProjectUpdate,
    ProjectRead,
    ProjectReadWithRelations,
    ProjectList,
    ProjectStepBase,
    ProjectStepCreate,
    ProjectStepUpdate,
    ProjectStepRead,
    StepReorderItem,
    StepReorderRequest,
)

# 待办相关
from app.schemas.todo import (
    TodoBase,
    TodoCreate,
    TodoUpdate,
    TodoRead,
    TodoReadWithRelations,
    TodoList,
)

# 附件相关
from app.schemas.attachment import (
    AttachmentType,
    AttachmentBase,
    AttachmentCreate,
    AttachmentUpdate,
    AttachmentRead,
    AttachmentList,
    AttachmentFolderBase,
    AttachmentFolderCreate,
    AttachmentFolderUpdate,
    AttachmentFolderRead,
)

# 日志相关
from app.schemas.project_log import (
    LogAction,
    ProjectLogBase,
    ProjectLogCreate,
    ProjectLogRead,
    ProjectLogReadWithRelations,
    ProjectLogList,
)

__all__ = [
    # 基础
    "BaseSchema",
    "BaseEntity",
    "PaginationParams",
    "PagedResult",
    "SimpleResponse",
    "IDResponse",
    "CountResponse",
    "DateRangeParams",
    "SearchParams",
    "OrderParams",
    "QueryParams",
    "DateQueryParams",
    # 用户
    "UserBase",
    "UserCreate",
    "UserUpdate",
    "UserRead",
    "Token",
    "TokenData",
    "LoginRequest",
    "RefreshTokenRequest",
    # 平台
    "PlatformBase",
    "PlatformCreate",
    "PlatformUpdate",
    "PlatformRead",
    "PlatformList",
    # 标签
    "TagBase",
    "TagCreate",
    "TagUpdate",
    "TagRead",
    "TagList",
    "ProjectTagCreate",
    "HistoricalProjectTagCreate",
    # 项目
    "ProjectBase",
    "ProjectCreate",
    "ProjectUpdate",
    "ProjectRead",
    "ProjectReadWithRelations",
    "ProjectList",
    "ProjectStepBase",
    "ProjectStepCreate",
    "ProjectStepUpdate",
    "ProjectStepRead",
    "StepReorderItem",
    "StepReorderRequest",
    # 待办
    "TodoBase",
    "TodoCreate",
    "TodoUpdate",
    "TodoRead",
    "TodoReadWithRelations",
    "TodoList",
    # 附件
    "AttachmentType",
    "AttachmentBase",
    "AttachmentCreate",
    "AttachmentUpdate",
    "AttachmentRead",
    "AttachmentList",
    "AttachmentFolderBase",
    "AttachmentFolderCreate",
    "AttachmentFolderUpdate",
    "AttachmentFolderRead",
    # 日志
    "LogAction",
    "ProjectLogBase",
    "ProjectLogCreate",
    "ProjectLogRead",
    "ProjectLogReadWithRelations",
    "ProjectLogList",
]
