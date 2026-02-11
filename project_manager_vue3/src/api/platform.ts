import request from './request'

export interface Platform {
  id: number
  name: string
  description?: string
  created_at: string
}

export interface PlatformCreate {
  name: string
  description?: string
}

export interface PlatformUpdate {
  name?: string
  description?: string
}

export const platformApi = {
  list: () => {
    return request.get<Platform[]>('/platforms/')
  },
  
  create: (data: PlatformCreate) => {
    return request.post<Platform>('/platforms/', data)
  },
  
  get: (id: number) => {
    return request.get<Platform>(`/platforms/${id}`)
  },
  
  update: (id: number, data: PlatformUpdate) => {
    return request.put<Platform>(`/platforms/${id}`, data)
  },
  
  delete: (id: number) => {
    return request.delete(`/platforms/${id}`)
  },
}

