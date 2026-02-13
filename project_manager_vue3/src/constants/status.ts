/**
 * 状态常量定义
 *
 * 集中管理所有业务状态常量，避免硬编码。
 * 符合国内互联网企业级规范。
 */

/**
 * 项目状态
 */
export const ProjectStatus = {
  /** 进行中 */
  IN_PROGRESS: 'in_progress',
  /** 已完成 */
  COMPLETED: 'completed',
  /** 已结账 */
  SETTLED: 'settled'
} as const

/**
 * 项目状态显示名称映射
 */
export const ProjectStatusLabel: Record<string, string> = {
  [ProjectStatus.IN_PROGRESS]: '进行中',
  [ProjectStatus.COMPLETED]: '已完成',
  [ProjectStatus.SETTLED]: '已结账',
  // 兼容旧数据
  '进行中': '进行中',
  '已完成': '已完成',
  '已结账': '已结账'
}

/**
 * 项目状态颜色映射（用于Element Plus Tag）
 */
export const ProjectStatusColor: Record<string, string> = {
  [ProjectStatus.IN_PROGRESS]: 'primary',
  [ProjectStatus.COMPLETED]: 'success',
  [ProjectStatus.SETTLED]: 'info'
}

/**
 * 步骤状态
 */
export const StepStatus = {
  /** 待开始 */
  PENDING: 'pending',
  /** 进行中 */
  IN_PROGRESS: 'in_progress',
  /** 已完成 */
  DONE: 'done'
} as const

/**
 * 步骤状态显示名称映射
 */
export const StepStatusLabel: Record<string, string> = {
  [StepStatus.PENDING]: '待开始',
  [StepStatus.IN_PROGRESS]: '进行中',
  [StepStatus.DONE]: '已完成',
  // 兼容旧数据
  '待开始': '待开始',
  '进行中': '进行中',
  '已完成': '已完成'
}

/**
 * 步骤状态颜色映射
 */
export const StepStatusColor: Record<string, string> = {
  [StepStatus.PENDING]: 'info',
  [StepStatus.IN_PROGRESS]: 'warning',
  [StepStatus.DONE]: 'success'
}

/**
 * 待办状态
 */
export const TodoStatus = {
  /** 待处理 */
  OPEN: 'open',
  /** 进行中 */
  DOING: 'doing',
  /** 已完成 */
  DONE: 'done'
} as const

/**
 * 待办状态显示名称映射
 */
export const TodoStatusLabel: Record<string, string> = {
  [TodoStatus.OPEN]: '待处理',
  [TodoStatus.DOING]: '进行中',
  [TodoStatus.DONE]: '已完成'
}

/**
 * 待办状态颜色映射
 */
export const TodoStatusColor: Record<string, string> = {
  [TodoStatus.OPEN]: 'danger',
  [TodoStatus.DOING]: 'warning',
  [TodoStatus.DONE]: 'success'
}

/**
 * 用户角色
 */
export const UserRole = {
  /** 管理员 */
  ADMIN: 'admin',
  /** 普通用户 */
  USER: 'user'
} as const

/**
 * 用户角色显示名称映射
 */
export const UserRoleLabel: Record<string, string> = {
  [UserRole.ADMIN]: '管理员',
  [UserRole.USER]: '普通用户'
}

/**
 * 插件类型
 */
export const PluginType = {
  /** 毕设插件 */
  GRADUATION: 'graduation',
  /** GitHub插件 */
  GITHUB: 'github',
  /** 配件清单插件 */
  PARTS: 'parts',
  /** 视频回放插件 */
  VIDEO_PLAYBACK: 'video-playback'
} as const

/**
 * 插件类型显示名称映射
 */
export const PluginTypeLabel: Record<string, string> = {
  [PluginType.GRADUATION]: '毕设插件',
  [PluginType.GITHUB]: 'GitHub插件',
  [PluginType.PARTS]: '配件清单',
  [PluginType.VIDEO_PLAYBACK]: '视频回放'
}

/**
 * 附件类型
 */
export const AttachmentType = {
  /** 需求文档 */
  REQUIREMENT: 'requirement',
  /** 交付物 */
  DELIVERABLE: 'deliverable',
  /** 其他 */
  OTHER: 'other'
} as const

/**
 * 附件类型显示名称映射
 */
export const AttachmentTypeLabel: Record<string, string> = {
  [AttachmentType.REQUIREMENT]: '需求文档',
  [AttachmentType.DELIVERABLE]: '交付物',
  [AttachmentType.OTHER]: '其他'
}

/**
 * 获取状态显示名称
 */
export function getStatusLabel(status: string, type: 'project' | 'step' | 'todo' = 'project'): string {
  const maps: Record<string, Record<string, string>> = {
    project: ProjectStatusLabel,
    step: StepStatusLabel,
    todo: TodoStatusLabel
  }
  return maps[type]?.[status] || status
}

/**
 * 获取状态颜色
 */
export function getStatusColor(status: string, type: 'project' | 'step' | 'todo' = 'project'): string {
  const maps: Record<string, Record<string, string>> = {
    project: ProjectStatusColor,
    step: StepStatusColor,
    todo: TodoStatusColor
  }
  return maps[type]?.[status] || 'info'
}
