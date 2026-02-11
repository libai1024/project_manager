import request from './request'

export interface UserInfo {
  id: number
  username: string
  role: string
  created_at: string
}

export interface UserUpdate {
  username?: string
  password?: string
  role?: string
}

export const userApi = {
  list: () => {
    return request.get<UserInfo[]>('/users/')
  },
  
  get: (id: number) => {
    return request.get<UserInfo>(`/users/${id}`)
  },
  
  update: (id: number, data: UserUpdate) => {
    return request.put<UserInfo>(`/users/${id}`, data)
  },
  
  delete: (id: number) => {
    return request.delete(`/users/${id}`)
  },
}

