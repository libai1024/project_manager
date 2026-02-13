/**
 * 数据模型类型定义
 *
 * 集中定义所有业务数据模型类型。
 * 符合国内互联网企业级规范。
 */

/**
 * 用户
 */
export interface User {
  id: number
  username: string
  role: UserRole
  is_active: boolean
  is_locked?: boolean
  created_at: string
  updated_at: string
}

/**
 * 用户角色
 */
export type UserRole = 'admin' | 'user'

/**
 * 平台
 */
export interface Platform {
  id: number
  name: string
  description?: string
  created_at: string
}

/**
 * 标签
 */
export interface Tag {
  id: number
  name: string
  color?: string
  is_common?: boolean
  usage_count?: number
  created_at: string
}

/**
 * 项目状态
 */
export type ProjectStatus = 'in_progress' | 'completed' | 'settled'

/**
 * 步骤状态
 */
export type StepStatus = 'pending' | 'in_progress' | 'done'

/**
 * 项目步骤
 */
export interface ProjectStep {
  id: number
  name: string
  project_id: number
  order_index: number
  status: StepStatus
  is_todo: boolean
  deadline?: string
  created_at: string
  updated_at: string
}

/**
 * 项目
 */
export interface Project {
  id: number
  title: string
  student_name?: string
  platform_id: number
  user_id: number
  price: number
  actual_income: number
  status: ProjectStatus
  github_url?: string
  requirements?: string
  is_paid: boolean
  created_at: string
  updated_at: string
  platform?: Platform
  steps?: ProjectStep[]
  tags?: Tag[]
}

/**
 * 带完整关联的项目
 */
export interface ProjectWithRelations extends Project {
  steps: ProjectStep[]
  tags: Tag[]
  platform: Platform
  attachments?: Attachment[]
  folders?: AttachmentFolder[]
  todos?: Todo[]
  logs?: ProjectLog[]
}

/**
 * 待办状态
 */
export type TodoStatus = 'open' | 'doing' | 'done'

/**
 * 待办
 */
export interface Todo {
  id: number
  title: string
  project_id?: number
  historical_project_id?: number
  status: TodoStatus
  target_date?: string
  completion_note?: string
  step_ids?: string
  completed_at?: string
  created_at: string
  updated_at: string
  project?: Project
}

/**
 * 附件类型
 */
export type AttachmentType = 'requirement' | 'deliverable' | 'other'

/**
 * 附件
 */
export interface Attachment {
  id: number
  filename: string
  original_filename: string
  file_path: string
  file_type?: string
  attachment_type?: AttachmentType
  project_id: number
  folder_id?: number
  created_at: string
}

/**
 * 附件文件夹
 */
export interface AttachmentFolder {
  id: number
  name: string
  project_id: number
  parent_id?: number
  created_at: string
}

/**
 * 项目日志类型
 */
export type ProjectLogType = 'status_change' | 'comment' | 'system'

/**
 * 项目日志
 */
export interface ProjectLog {
  id: number
  project_id: number
  type: ProjectLogType
  content: string
  created_by?: number
  created_at: string
  user?: User
  attachments?: Attachment[]
}

/**
 * 历史项目
 */
export interface HistoricalProject {
  id: number
  title: string
  student_name?: string
  platform_id: number
  original_project_id?: number
  import_source?: string
  import_date?: string
  completion_date?: string
  price: number
  actual_income: number
  notes?: string
  created_at: string
  platform?: Platform
  tags?: Tag[]
}

/**
 * 步骤模板
 */
export interface StepTemplate {
  id: number
  name: string
  description?: string
  items: StepTemplateItem[]
  created_at: string
}

/**
 * 步骤模板项
 */
export interface StepTemplateItem {
  id: number
  template_id: number
  title: string
  order_index: number
}

/**
 * 插件类型
 */
export type PluginType = 'graduation' | 'github' | 'parts' | 'video-playback'

/**
 * 系统设置
 */
export interface SystemSettings {
  id: number
  key: string
  value: string
  description?: string
  updated_at: string
}

/**
 * 登录日志
 */
export interface LoginLog {
  id: number
  user_id: number
  ip?: string
  user_agent?: string
  created_at: string
}

/**
 * 刷新令牌
 */
export interface RefreshToken {
  id: number
  token: string
  user_id: number
  expires_at: string
  created_at: string
}

/**
 * Token响应
 */
export interface TokenResponse {
  access_token: string
  refresh_token: string
  token_type: string
}

/**
 * 登录表单
 */
export interface LoginForm {
  username: string
  password: string
}

/**
 * 用户创建表单
 */
export interface UserCreate {
  username: string
  password: string
  role?: UserRole
}

/**
 * 项目创建表单
 */
export interface ProjectCreate {
  title: string
  student_name?: string
  platform_id: number
  user_id?: number
  price: number
  github_url?: string
  requirements?: string
  requirement_files?: number[]
  tag_ids?: number[]
  template_id?: number
}

/**
 * 项目更新表单
 */
export interface ProjectUpdate {
  title?: string
  student_name?: string
  platform_id?: number
  price?: number
  actual_income?: number
  status?: ProjectStatus
  github_url?: string
  requirements?: string
  is_paid?: boolean
  tag_ids?: number[]
}
