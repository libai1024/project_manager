/**
 * Axios 请求配置模块
 * 
 * 职责：
 * - 配置 axios 实例
 * - 统一处理请求拦截（添加 token）
 * - 统一处理响应拦截（错误处理、token 过期处理）
 */
import axios, { type InternalAxiosRequestConfig } from 'axios'
import { ElMessage } from 'element-plus'
import router from '@/router'
import { getToken, removeToken } from '@/utils/auth'
import { useUserStore } from '@/stores/user'

const request = axios.create({
  baseURL: '/api',
  timeout: 10000, // 默认10秒，上传请求会在拦截器中单独设置
})

// 请求拦截器 - 统一添加 token 和设置上传请求超时时间
request.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const url = config.url || ''
    
    // 检测是否是文件上传请求（通过URL和Content-Type判断）
    const isUploadApi = url.includes('/attachments/project/') && url.includes('/upload') ||
                       url.includes('/attachments/') && config.method?.toLowerCase() === 'post' ||
                       url.includes('/video-playbacks/') && url.includes('/upload') ||
                       url.includes('/historical-project/') && config.method?.toLowerCase() === 'post' ||
                       config.headers?.['Content-Type']?.includes('multipart/form-data')
    
    // 如果是上传请求，设置更长的超时时间（30分钟）
    if (isUploadApi) {
      config.timeout = 30 * 60 * 1000 // 30分钟
    }
    
    // 排除登录和注册接口，这些接口不需要 token
    const isAuthApi = url.includes('/auth/login') || url.includes('/auth/register')
    
    if (!isAuthApi) {
      // 使用统一的 token 获取方法
      const token = getToken()
      
      if (token) {
        const tokenStr = String(token).trim()
        
        if (tokenStr.length > 0) {
          const authHeaderValue: string = 'Bearer ' + tokenStr
          
          // 确保 headers 对象存在
          if (!config.headers) {
            config.headers = {} as any
          }
          
          // 使用最简单直接的方式设置 header
          // axios 1.x 使用 AxiosHeaders，直接设置即可
          config.headers['Authorization'] = authHeaderValue
          
          // 调试日志（仅在开发环境）
          if (import.meta.env.DEV) {
            console.log(`[Request Interceptor] Token added to request: ${url}`, {
              hasToken: !!token,
              tokenLength: String(token).length,
              headerValue: authHeaderValue.substring(0, 30) + '...',
              headersType: typeof config.headers,
            })
          }
        }
      } else {
        // 开发环境下警告
        if (import.meta.env.DEV) {
          console.warn(`[Request Interceptor] No token found for: ${url}`)
        }
      }
    }
    
    return config
  },
  (error) => {
    console.error('[Request] Interceptor error:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
request.interceptors.response.use(
  (response) => {
    // 对于blob响应，直接返回response，而不是response.data
    if (response.config.responseType === 'blob') {
      return response.data
    }
    // 统一响应格式处理：提取 data 字段
    // 后端返回格式：{ code: number, msg: string, data: any }
    const data = response.data
    if (data && typeof data === 'object' && 'code' in data && 'data' in data) {
      // 如果 code 不是 200，当作错误处理
      if (data.code !== 200) {
        const error: any = new Error(data.msg || '请求失败')
        error.response = { data: { detail: data.msg }, status: data.code }
        return Promise.reject(error)
      }
      return data.data
    }
    return response.data
  },
  (error) => {
    if (error.response) {
      const { status, data, config } = error.response
      const url = config?.url || ''
      
      // 排除不需要自动处理的接口
      const isAuthApi = url.includes('/auth/login') || url.includes('/auth/register')
      const isWatchApi = url.includes('/video-playbacks/watch/')
      // Token 管理相关的 API，401 错误不自动跳转（由调用方处理）
      const isTokenManagementApi = url.includes('/auth/login-logs') || url.includes('/auth/refresh-tokens')
      
      if (status === 401) {
        // 登录和注册接口的401错误不自动跳转，让调用方处理
        if (isAuthApi) {
          // 登录/注册失败，只返回错误，不显示消息（由调用方处理）
          return Promise.reject(error)
        }
        
        // 观看接口的401错误只显示错误信息，不跳转
        if (isWatchApi) {
          ElMessage.error(data.detail || '验证失败，请检查密码')
          return Promise.reject(error)
        }
        
        // Token 管理相关的 API，401 错误不自动跳转，让调用方处理
        if (isTokenManagementApi) {
          // 只返回错误，不显示消息，不跳转（由调用方处理）
          return Promise.reject(error)
        }
        
        // 其他接口的401错误才跳转登录页
        // 避免重复显示消息（如果已经在跳转过程中）
        if (router.currentRoute.value.path !== '/login') {
          ElMessage.error('登录已过期，请重新登录')
        }
        // 清除 token（使用工具函数避免循环依赖）
        removeToken()
        // 清除 user store 的 token
        const userStore = useUserStore()
        userStore.logout()
        // 只有在当前不在登录页时才跳转
        if (router.currentRoute.value.path !== '/login') {
          router.push('/login')
        }
      } else if (status === 403) {
        ElMessage.error(data.detail || '权限不足')
      } else {
        // 登录接口的错误信息由调用方处理，不在这里显示
        if (!isAuthApi) {
        ElMessage.error(data.detail || '请求失败')
        }
      }
    } else {
      ElMessage.error('网络错误，请检查网络连接')
    }
    
    return Promise.reject(error)
  }
)

export default request
