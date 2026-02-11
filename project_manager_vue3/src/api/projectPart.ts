import request from './request'

export interface ProjectPart {
  id: number
  project_id: number
  module_name: string
  core_component: string
  remark?: string
  unit_price: number
  quantity: number
  purchase_link?: string
  image_url?: string
  created_at: string
  updated_at: string
}

export interface ProjectPartCreate {
  module_name: string
  core_component: string
  remark?: string
  unit_price?: number
  quantity?: number
  purchase_link?: string
  image_url?: string
}

export interface ProjectPartUpdate {
  module_name?: string
  core_component?: string
  remark?: string
  unit_price?: number
  quantity?: number
  purchase_link?: string
  image_url?: string
}

export const projectPartApi = {
  list: (projectId: number) => {
    return request.get<ProjectPart[]>(`/project-parts/project/${projectId}`)
  },

  createBatch: (projectId: number, parts: ProjectPartCreate[]) => {
    return request.post<ProjectPart[]>(`/project-parts/project/${projectId}`, parts)
  },

  update: (partId: number, data: ProjectPartUpdate) => {
    return request.put<ProjectPart>(`/project-parts/${partId}`, data)
  },

  delete: (partId: number) => {
    return request.delete(`/project-parts/${partId}`)
  },
}


