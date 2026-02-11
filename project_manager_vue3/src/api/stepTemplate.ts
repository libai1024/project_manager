import request from './request'

export interface StepTemplate {
  id: number
  name: string
  description?: string
  is_default: boolean
  user_id?: number
  created_at: string
  updated_at: string
  steps: string[]
}

export interface StepTemplateCreate {
  name: string
  description?: string
  steps: string[]
}

export interface StepTemplateUpdate {
  name?: string
  description?: string
  steps?: string[]
}

export const stepTemplateApi = {
  list: () => {
    return request.get<StepTemplate[]>('/step-templates/')
  },
  
  create: (data: StepTemplateCreate) => {
    return request.post<StepTemplate>('/step-templates/', data)
  },
  
  get: (id: number) => {
    return request.get<StepTemplate>(`/step-templates/${id}`)
  },
  
  update: (id: number, data: StepTemplateUpdate) => {
    return request.put<StepTemplate>(`/step-templates/${id}`, data)
  },
  
  delete: (id: number) => {
    return request.delete(`/step-templates/${id}`)
  },
  
  ensureDefault: () => {
    return request.post<StepTemplate>('/step-templates/ensure-default')
  },
}

