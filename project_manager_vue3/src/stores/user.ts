/**
 * 用户状态管理 Store
 * 
 * 职责：
 * - 管理用户认证状态（token）
 * - 管理用户信息
 * - 提供登录/登出功能
 * - 作为整个应用中唯一的 token 管理源
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi } from '@/api/auth'
import type { UserInfo } from '@/api/user'
import router from '@/router'
import { getToken, setToken, removeToken } from '@/utils/auth'

export const useUserStore = defineStore('user', () => {
  // Token 状态 - 从 localStorage 初始化
  const token = ref<string | null>(getToken())
  const userInfo = ref<UserInfo | null>(null)
  
  // 计算属性：是否已认证
  const isAuthenticated = computed(() => {
    return !!token.value && token.value.trim().length > 0
  })
  
  // 监听 localStorage 变化（多标签页同步）
  if (typeof window !== 'undefined') {
    window.addEventListener('storage', (e) => {
      if (e.key === 'token') {
        token.value = e.newValue
      }
    })
  }

  /**
   * 用户登录
   * @param username 用户名
   * @param password 密码
   */
  const login = async (username: string, password: string) => {
    const response = await authApi.login({ username, password })
    
    // 统一设置 token（同时更新 store 和 localStorage）
    token.value = response.access_token
    setToken(response.access_token)
    
    // 获取用户信息
    await fetchUserInfo()
    
    return response
  }

  /**
   * 用户登出
   */
  const logout = () => {
    token.value = null
    userInfo.value = null
    removeToken()
    router.push('/login')
  }

  /**
   * 获取当前用户信息
   */
  const fetchUserInfo = async () => {
    try {
      const info = await authApi.getCurrentUser()
      userInfo.value = info
    } catch (error) {
      console.error('获取用户信息失败:', error)
      // 如果获取用户信息失败，可能是 token 已过期，清除 token
      if (error && typeof error === 'object' && 'response' in error) {
        const axiosError = error as any
        if (axiosError.response?.status === 401) {
          logout()
        }
      }
    }
  }

  /**
   * 检查是否为管理员
   */
  const isAdmin = computed(() => {
    return userInfo.value?.role === 'admin'
  })

  /**
   * 同步 token（从 localStorage 同步到 store）
   * 用于应用初始化时恢复状态
   */
  const syncToken = () => {
    const storedToken = getToken()
    if (storedToken && !token.value) {
      token.value = storedToken
    } else if (!storedToken && token.value) {
      token.value = null
    }
  }

  return {
    // 状态
    token,
    userInfo,
    // 计算属性
    isAuthenticated,
    isAdmin,
    // 方法
    login,
    logout,
    fetchUserInfo,
    syncToken,
  }
})

