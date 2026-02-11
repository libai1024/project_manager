import request from './request'
import type { UserInfo } from './user'

export interface LoginForm {
  username: string
  password: string
}

export interface RegisterForm {
  username: string
  password: string
  role?: string
}

export interface TokenResponse {
  access_token: string
  refresh_token?: string
  token_type: string
  expires_in?: number
}

export interface LoginLog {
  id: number
  user_id?: number
  username: string
  status: string
  ip_address?: string
  user_agent?: string
  failure_reason?: string
  created_at: string
}

export interface RefreshTokenInfo {
  id: number
  token: string
  user_id: number
  expires_at: string
  is_revoked: boolean
  device_info?: string
  ip_address?: string
  created_at: string
  revoked_at?: string
}

export const authApi = {
  login: (data: LoginForm) => {
    const formData = new FormData()
    formData.append('username', data.username)
    formData.append('password', data.password)
    return request.post<TokenResponse>('/auth/login', formData)
  },
  
  register: (data: RegisterForm) => {
    return request.post<UserInfo>('/auth/register', data)
  },
  
  getCurrentUser: () => {
    return request.get<UserInfo>('/auth/me')
  },
  
  refreshToken: (refreshToken: string) => {
    return request.post<TokenResponse>('/auth/refresh', { refresh_token: refreshToken })
  },
  
  logout: (refreshToken?: string) => {
    return request.post('/auth/logout', { refresh_token: refreshToken })
  },
  
  logoutAll: () => {
    return request.post('/auth/logout-all')
  },
  
  getLoginLogs: (limit: number = 100) => {
    return request.get<LoginLog[]>('/auth/login-logs', { params: { limit } })
  },
  
  getRefreshTokens: () => {
    return request.get<RefreshTokenInfo[]>('/auth/refresh-tokens')
  },
  
  revokeRefreshToken: (tokenId: number) => {
    return request.delete(`/auth/refresh-tokens/${tokenId}`)
  },
}

