/**
 * 常量模块统一导出
 */

export * from './status'
export * from './steps'

/**
 * 分页默认值
 */
export const PaginationDefaults = {
  /** 默认页码 */
  PAGE: 1,
  /** 默认每页数量 */
  PAGE_SIZE: 20,
  /** 最大每页数量 */
  MAX_PAGE_SIZE: 1000
} as const

/**
 * 文件上传常量
 */
export const FileUploadConstants = {
  /** 最大文件大小（1GB） */
  MAX_FILE_SIZE: 1 * 1024 * 1024 * 1024,
  /** 允许的文件类型 */
  ALLOWED_TYPES: [
    // 文档
    '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
    '.txt', '.md', '.rtf',
    // 代码
    '.py', '.js', '.ts', '.java', '.cpp', '.c', '.h', '.cs',
    '.go', '.rs', '.rb', '.php', '.swift', '.kt',
    // 压缩包
    '.zip', '.rar', '.7z', '.tar', '.gz',
    // 图片
    '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp',
    // 视频
    '.mp4', '.avi', '.mov', '.wmv', '.flv', '.mkv',
    // 音频
    '.mp3', '.wav', '.flac', '.aac',
    // 其他
    '.json', '.xml', '.yaml', '.yml', '.sql', '.db'
  ]
} as const

/**
 * 本地存储键名
 */
export const StorageKeys = {
  /** Token键名 */
  TOKEN: import.meta.env.VITE_TOKEN_KEY || 'pm_token',
  /** 刷新Token键名 */
  REFRESH_TOKEN: import.meta.env.VITE_REFRESH_TOKEN_KEY || 'pm_refresh_token',
  /** 用户信息键名 */
  USER_INFO: 'pm_user_info',
  /** 主题键名 */
  THEME: 'pm_theme',
  /** 语言键名 */
  LANGUAGE: 'pm_language'
} as const

/**
 * 错误消息
 */
export const ErrorMessages = {
  /** 网络错误 */
  NETWORK_ERROR: '网络错误，请检查网络连接',
  /** 请求超时 */
  TIMEOUT: '请求超时，请稍后重试',
  /** 服务器错误 */
  SERVER_ERROR: '服务器错误，请稍后重试',
  /** 未授权 */
  UNAUTHORIZED: '登录已过期，请重新登录',
  /** 权限不足 */
  FORBIDDEN: '权限不足，无法执行此操作',
  /** 资源不存在 */
  NOT_FOUND: '请求的资源不存在',
  /** 验证失败 */
  VALIDATION_ERROR: '数据验证失败',
  /** 文件过大 */
  FILE_TOO_LARGE: '文件大小超过限制',
  /** 文件类型不支持 */
  FILE_TYPE_NOT_ALLOWED: '文件类型不支持'
} as const
