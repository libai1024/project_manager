/**
 * 认证工具模块
 * 提供统一的 token 管理接口
 * 
 * 注意：此模块仅作为工具函数，实际的 token 状态管理应在 Pinia store 中
 * 此模块主要用于在非 Vue 组件环境中（如 axios 拦截器）获取 token
 */

const TOKEN_KEY = 'token'

/**
 * 从 localStorage 获取 token
 * 注意：这是同步操作，用于在非响应式环境中获取 token
 * 在 Vue 组件中，应该使用 useUserStore().token
 */
export function getToken(): string | null {
  if (typeof window === 'undefined') {
    return null
  }
  try {
    return localStorage.getItem(TOKEN_KEY)
  } catch (error) {
    console.error('获取 token 失败:', error)
    return null
  }
}

/**
 * 设置 token 到 localStorage
 * 注意：此函数主要用于初始化或同步场景
 * 正常情况下应该通过 Pinia store 的 login 方法设置 token
 */
export function setToken(token: string): void {
  if (typeof window === 'undefined') {
    return
  }
  try {
    localStorage.setItem(TOKEN_KEY, token)
  } catch (error) {
    console.error('设置 token 失败:', error)
  }
}

/**
 * 从 localStorage 移除 token
 * 注意：正常情况下应该通过 Pinia store 的 logout 方法移除 token
 */
export function removeToken(): void {
  if (typeof window === 'undefined') {
    return
  }
  try {
    localStorage.removeItem(TOKEN_KEY)
  } catch (error) {
    console.error('移除 token 失败:', error)
  }
}

/**
 * 检查是否存在 token
 */
export function hasToken(): boolean {
  const token = getToken()
  return !!token && token.trim().length > 0
}


