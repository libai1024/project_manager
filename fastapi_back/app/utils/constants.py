"""
常量与枚举定义模块

集中管理所有业务常量和枚举，避免硬编码。
符合国内互联网企业级规范。

使用示例:
    from app.utils.constants import ProjectStatus, StepStatus, DEFAULT_STEPS

    if project.status == ProjectStatus.SETTLED:
        # 处理已结账逻辑
        pass
"""
from enum import Enum
from typing import List


class ProjectStatus(str, Enum):
    """
    项目状态枚举

    使用英文编码，通过display_name属性获取中文显示名
    """
    IN_PROGRESS = "in_progress"  # 进行中
    COMPLETED = "completed"      # 已完成
    SETTLED = "settled"          # 已结账

    @property
    def display_name(self) -> str:
        """获取中文显示名"""
        names = {
            ProjectStatus.IN_PROGRESS: "进行中",
            ProjectStatus.COMPLETED: "已完成",
            ProjectStatus.SETTLED: "已结账"
        }
        return names.get(self, self.value)

    @classmethod
    def from_chinese(cls, chinese: str) -> "ProjectStatus":
        """
        从中文名称转换（用于兼容旧数据）

        Args:
            chinese: 中文名称

        Returns:
            对应的枚举值

        Example:
            status = ProjectStatus.from_chinese("已结账")  # 返回 ProjectStatus.SETTLED
        """
        mapping = {
            "进行中": cls.IN_PROGRESS,
            "已完成": cls.COMPLETED,
            "已结账": cls.SETTLED
        }
        return mapping.get(chinese, cls.IN_PROGRESS)


class StepStatus(str, Enum):
    """
    步骤状态枚举
    """
    PENDING = "pending"         # 待开始
    IN_PROGRESS = "in_progress" # 进行中
    DONE = "done"               # 已完成

    @property
    def display_name(self) -> str:
        """获取中文显示名"""
        names = {
            StepStatus.PENDING: "待开始",
            StepStatus.IN_PROGRESS: "进行中",
            StepStatus.DONE: "已完成"
        }
        return names.get(self, self.value)

    @classmethod
    def from_chinese(cls, chinese: str) -> "StepStatus":
        """从中文名称转换（用于兼容旧数据）"""
        mapping = {
            "待开始": cls.PENDING,
            "进行中": cls.IN_PROGRESS,
            "已完成": cls.DONE
        }
        return mapping.get(chinese, cls.PENDING)


class UserRole(str, Enum):
    """
    用户角色枚举
    """
    ADMIN = "admin"  # 管理员
    USER = "user"    # 普通用户

    @property
    def display_name(self) -> str:
        """获取中文显示名"""
        names = {
            UserRole.ADMIN: "管理员",
            UserRole.USER: "普通用户"
        }
        return names.get(self, self.value)


class AttachmentType(str, Enum):
    """
    附件类型枚举
    """
    REQUIREMENT = "requirement"     # 需求文档
    DELIVERABLE = "deliverable"     # 交付物
    OTHER = "other"                 # 其他

    @property
    def display_name(self) -> str:
        """获取中文显示名"""
        names = {
            AttachmentType.REQUIREMENT: "需求文档",
            AttachmentType.DELIVERABLE: "交付物",
            AttachmentType.OTHER: "其他"
        }
        return names.get(self, self.value)


class TodoStatus(str, Enum):
    """
    待办状态枚举
    """
    OPEN = "open"       # 待处理
    DOING = "doing"     # 进行中
    DONE = "done"       # 已完成

    @property
    def display_name(self) -> str:
        """获取中文显示名"""
        names = {
            TodoStatus.OPEN: "待处理",
            TodoStatus.DOING: "进行中",
            TodoStatus.DONE: "已完成"
        }
        return names.get(self, self.value)


class PluginType(str, Enum):
    """
    插件类型枚举
    """
    GRADUATION = "graduation"           # 毕设插件
    GITHUB = "github"                   # GitHub插件
    PARTS = "parts"                     # 配件清单插件
    VIDEO_PLAYBACK = "video-playback"   # 视频回放插件

    @property
    def display_name(self) -> str:
        """获取中文显示名"""
        names = {
            PluginType.GRADUATION: "毕设插件",
            PluginType.GITHUB: "GitHub插件",
            PluginType.PARTS: "配件清单",
            PluginType.VIDEO_PLAYBACK: "视频回放"
        }
        return names.get(self, self.value)


# ==================== 默认值常量 ====================

DEFAULT_STEPS: List[str] = [
    "已接单",
    "已规划",
    "硬件完成",
    "软件完成",
    "软硬调试",
    "实物验收",
    "实物邮寄",
    "论文框架",
    "论文初稿",
    "论文终稿",
    "答辩辅导",
    "毕设通过",
    "已结账"
]

# 文件上传相关常量
MAX_FILE_SIZE = 1 * 1024 * 1024 * 1024  # 1GB
UPLOAD_DIR = "uploads"

# 允许的文件类型白名单
ALLOWED_FILE_TYPES = {
    # 文档
    ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx",
    ".txt", ".md", ".rtf",
    # 代码
    ".py", ".js", ".ts", ".java", ".cpp", ".c", ".h", ".cs",
    ".go", ".rs", ".rb", ".php", ".swift", ".kt",
    # 压缩包
    ".zip", ".rar", ".7z", ".tar", ".gz",
    # 图片
    ".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp",
    # 视频
    ".mp4", ".avi", ".mov", ".wmv", ".flv", ".mkv",
    # 音频
    ".mp3", ".wav", ".flac", ".aac",
    # 其他
    ".json", ".xml", ".yaml", ".yml", ".sql", ".db"
}

# 分页默认值
DEFAULT_PAGE = 1
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 1000


# ==================== 错误消息常量 ====================

class ErrorMessages:
    """错误消息常量"""

    # 通用错误
    INTERNAL_ERROR = "服务器内部错误"
    VALIDATION_ERROR = "数据验证失败"
    NOT_FOUND = "资源不存在"
    FORBIDDEN = "权限不足"
    UNAUTHORIZED = "未授权访问"

    # 用户相关
    USER_NOT_FOUND = "用户不存在"
    USER_DISABLED = "用户已被禁用"
    USER_LOCKED = "用户已被锁定"
    PASSWORD_ERROR = "密码错误"
    USERNAME_EXISTS = "用户名已存在"

    # 项目相关
    PROJECT_NOT_FOUND = "项目不存在"
    PROJECT_ACCESS_DENIED = "无权访问该项目"
    PROJECT_STATUS_ERROR = "项目状态错误"

    # 文件相关
    FILE_NOT_FOUND = "文件不存在"
    FILE_TYPE_NOT_ALLOWED = "文件类型不支持"
    FILE_SIZE_EXCEEDED = "文件大小超过限制"
    FILE_UPLOAD_FAILED = "文件上传失败"
