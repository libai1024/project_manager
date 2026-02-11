import request from './request'
import type { Platform } from './platform'
import type { Tag } from './tag'

export interface HistoricalProject {
  id: number
  title: string
  student_name?: string
  platform_id: number
  user_id: number
  price?: number
  actual_income?: number
  status?: string
  github_url?: string
  requirements?: string
  description?: string
  completed_at?: string
  created_at: string
  updated_at: string
  platform?: Platform
  tags?: Tag[]
}

export interface HistoricalProjectCreate {
  title: string
  student_name?: string
  platform_id: number
  user_id: number
  price?: number
  actual_income?: number
  status?: string
  github_url?: string
  requirements?: string
  description?: string
  completed_at?: string
}

export interface HistoricalProjectUpdate {
  title?: string
  student_name?: string
  platform_id?: number
  price?: number
  actual_income?: number
  status?: string
  github_url?: string
  requirements?: string
  description?: string
  completed_at?: string
}

export interface SystemSettings {
  id: number
  key: string
  value: boolean
  description?: string
  created_at: string
  updated_at: string
}

export interface SystemSettingsUpdate {
  value: boolean
}

// 历史项目API
export const historicalProjectApi = {
        // 获取历史项目列表
        list: (params?: {
          platform_id?: number
          status?: string
          user_id?: number
          limit?: number
          offset?: number
          tag_ids?: string
        }) => {
          return request.get<HistoricalProject[]>('/historical-projects/', { params })
        },

  // 获取历史项目详情
  get: (id: number) => {
    return request.get<HistoricalProject>(`/historical-projects/${id}`)
  },

  // 创建历史项目
  create: (data: HistoricalProjectCreate) => {
    return request.post<HistoricalProject>('/historical-projects/', data)
  },

  // 更新历史项目
  update: (id: number, data: HistoricalProjectUpdate) => {
    return request.put<HistoricalProject>(`/historical-projects/${id}`, data)
  },

  // 删除历史项目
  delete: (id: number) => {
    return request.delete(`/historical-projects/${id}`)
  },

  // 从现有项目导入
  importFromProject: (projectId: number, data?: {
    include_attachments?: boolean
    include_parts?: boolean
    include_logs?: boolean
  }) => {
    return request.post<HistoricalProject>(`/historical-projects/import-from-project/${projectId}`, data || {})
  },
}

// 系统设置API
export const systemSettingsApi = {
  // 获取所有设置
  list: () => {
    return request.get<SystemSettings[]>('/system-settings/')
  },

  // 获取单个设置
  get: (key: string) => {
    return request.get<SystemSettings>(`/system-settings/${key}`)
  },

  // 更新设置
  update: (key: string, data: SystemSettingsUpdate) => {
    return request.put<SystemSettings>(`/system-settings/${key}`, data)
  },

  // 检查功能是否启用
  isFeatureEnabled: async (key: string): Promise<boolean> => {
    try {
      const response = await request.get<SystemSettings>(`/system-settings/${key}`)
      return response.value
    } catch {
      return false
    }
  },

  // 获取 Token 持续时间设置
  getTokenDuration: () => {
    return request.get<{ access_token_expire_minutes: number; refresh_token_expire_days: number }>('/system-settings/token-duration')
  },

  // 更新 Token 持续时间设置
  updateTokenDuration: (data: { access_token_expire_minutes?: number; refresh_token_expire_days?: number }) => {
    return request.put<{ access_token_expire_minutes: number; refresh_token_expire_days: number }>('/system-settings/token-duration', data)
  },

  // 获取插件设置（全局共享）
  getPluginSettings: () => {
    return request.get<Record<string, number[]>>('/system-settings/plugin-settings')
  },

  // 更新插件设置（全局共享）
  updatePluginSettings: (settings: Record<string, number[]>) => {
    return request.put<Record<string, number[]>>('/system-settings/plugin-settings', settings)
  },
}

