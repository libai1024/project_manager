/**
 * 用户 Store 单元测试
 */
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useUserStore } from '@/stores/user'

// Mock auth API
vi.mock('@/api/auth', () => ({
  authApi: {
    login: vi.fn().mockResolvedValue({ access_token: 'test-token' }),
    getCurrentUser: vi.fn().mockResolvedValue({
      id: 1,
      username: 'testuser',
      role: 'user'
    })
  }
}))

// Mock router
vi.mock('@/router', () => ({
  default: {
    push: vi.fn()
  }
}))

// Mock auth utils
vi.mock('@/utils/auth', () => ({
  getToken: vi.fn().mockReturnValue(null),
  setToken: vi.fn(),
  removeToken: vi.fn()
}))

describe('User Store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('初始化时 token 为 null', () => {
    const store = useUserStore()

    expect(store.token).toBeNull()
    expect(store.userInfo).toBeNull()
    expect(store.isAuthenticated).toBe(false)
  })

  it('isAdmin 正确判断管理员角色', async () => {
    const store = useUserStore()

    // 模拟普通用户
    store.userInfo = { id: 1, username: 'user', role: 'user', created_at: '' }
    expect(store.isAdmin).toBe(false)

    // 模拟管理员
    store.userInfo = { id: 2, username: 'admin', role: 'admin', created_at: '' }
    expect(store.isAdmin).toBe(true)
  })

  it('logout 清空状态', () => {
    const store = useUserStore()

    // 设置一些状态
    store.token = 'test-token'
    store.userInfo = { id: 1, username: 'user', role: 'user', created_at: '' }

    // 登出
    store.logout()

    expect(store.token).toBeNull()
    expect(store.userInfo).toBeNull()
    expect(store.isAuthenticated).toBe(false)
  })
})
