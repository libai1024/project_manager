import request from './request'
import type { Platform } from './platform'

export interface ProjectStep {
  id: number
  name: string
  project_id: number
  order_index: number
  status: string
  is_todo: boolean
  deadline?: string
  created_at: string
  updated_at: string
}

import type { Tag } from './tag'

export interface Project {
  id: number
  title: string
  student_name?: string
  platform_id: number
  user_id: number
  price: number
  actual_income: number
  status: string
  github_url?: string
  requirements?: string
  is_paid: boolean
  created_at: string
  updated_at: string
  platform?: Platform
  steps?: ProjectStep[]
  tags?: Tag[]
}

export interface ProjectCreate {
  title: string
  student_name?: string
  platform_id: number
  user_id: number
  price?: number
  actual_income?: number
  status?: string
  github_url?: string
  requirements?: string
  is_paid?: boolean
  template_id?: number
  tag_ids?: number[]
}

export interface ProjectUpdate {
  title?: string
  student_name?: string
  platform_id?: number
  price?: number
  actual_income?: number
  status?: string
  github_url?: string
  requirements?: string
  is_paid?: boolean
  tag_ids?: number[]
}

export interface ProjectStepCreate {
  name: string
  order_index?: number
  deadline?: string
}

export interface ProjectStepUpdate {
  name?: string
  order_index?: number
  status?: string
  is_todo?: boolean
  deadline?: string
}

export interface ProjectLog {
  id: number
  project_id: number
  action: string
  description: string
  details?: string
  user_id?: number
  user_name?: string
  created_at: string
}

export const projectApi = {
  list: (params?: { skip?: number; limit?: number; user_id?: number; platform_id?: number; status?: string; tag_ids?: string }) => {
    return request.get<Project[]>('/projects/', { params })
  },
  
  create: (data: ProjectCreate) => {
    return request.post<Project>('/projects/', data)
  },
  
  get: (id: number) => {
    return request.get<Project>(`/projects/${id}`)
  },
  
  update: (id: number, data: ProjectUpdate) => {
    return request.put<Project>(`/projects/${id}`, data)
  },
  
  delete: (id: number) => {
    return request.delete(`/projects/${id}`)
  },
  
  createStep: (projectId: number, data: ProjectStepCreate) => {
    return request.post<ProjectStep>(`/projects/${projectId}/steps`, data)
  },
  
  updateStep: (stepId: number, data: ProjectStepUpdate) => {
    return request.put<ProjectStep>(`/projects/steps/${stepId}`, data)
  },
  
  deleteStep: (stepId: number) => {
    return request.delete(`/projects/steps/${stepId}`)
  },
  
  toggleStepTodo: (stepId: number) => {
    return request.post<ProjectStep>(`/projects/steps/${stepId}/toggle-todo`)
  },
  
  reorderSteps: (stepOrders: Array<{ step_id: number; order_index: number }>) => {
    return request.post('/projects/steps/reorder', stepOrders)
  },
  
  getLogs: (projectId: number, limit?: number) => {
    const params: any = {}
    if (limit) params.limit = limit
    return request.get<ProjectLog[]>(`/project-logs/project/${projectId}`, { params })
  },
  
  deleteLog: (logId: number) => {
    return request.delete(`/project-logs/${logId}`)
  },
  
  logStepUpdate: (data: {
    project_id: number
    step_id: number
    old_status: string
    new_status: string
    update_note?: string
    attachment_ids?: number[]
  }) => {
    return request.post('/project-logs/step-update', data)
  },
  
  createSnapshot: (data: {
    project_id: number
    snapshot_note?: string
    photo_urls?: string[]
    attachment_ids?: number[]
  }) => {
    return request.post('/project-logs/snapshot', data)
  },
  
  settleProject: (projectId: number) => {
    return request.post<Project>(`/projects/${projectId}/settle`)
  },
}

