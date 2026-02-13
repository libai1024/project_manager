"""
工具模块

包含常量定义、权限检查等工具函数。
"""
from app.utils.constants import (
    ProjectStatus,
    StepStatus,
    UserRole,
    AttachmentType,
    TodoStatus,
    PluginType,
    DEFAULT_STEPS,
    MAX_FILE_SIZE,
    UPLOAD_DIR,
    ALLOWED_FILE_TYPES,
    DEFAULT_PAGE,
    DEFAULT_PAGE_SIZE,
    MAX_PAGE_SIZE,
    ErrorMessages,
)

from app.utils.permissions import (
    is_admin,
    is_user_active,
    is_user_locked,
    check_project_access,
    check_project_read_access,
    check_project_write_access,
    can_access_user_resources,
    check_user_resource_access,
    assert_admin,
    assert_active,
    assert_not_locked,
    assert_owner,
)

__all__ = [
    # 常量
    "ProjectStatus",
    "StepStatus",
    "UserRole",
    "AttachmentType",
    "TodoStatus",
    "PluginType",
    "DEFAULT_STEPS",
    "MAX_FILE_SIZE",
    "UPLOAD_DIR",
    "ALLOWED_FILE_TYPES",
    "DEFAULT_PAGE",
    "DEFAULT_PAGE_SIZE",
    "MAX_PAGE_SIZE",
    "ErrorMessages",
    # 权限
    "is_admin",
    "is_user_active",
    "is_user_locked",
    "check_project_access",
    "check_project_read_access",
    "check_project_write_access",
    "can_access_user_resources",
    "check_user_resource_access",
    "assert_admin",
    "assert_active",
    "assert_not_locked",
    "assert_owner",
]
