/**
 * 平台 Store 单元测试
 */
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { usePlatformStore } from '@/stores/platform'

// Mock platform service
vi.mock('@/services/platform.service', () => ({
  PlatformService: {
    getPlatformList: vi.fn().mockResolvedValue([
      { id: 1, name: '平台A' },
      { id: 2, name: '平台B' }
    ]),
    createPlatform: vi.fn().mockResolvedValue({ id: 3, name: '新平台' }),
    updatePlatform: vi.fn().mockResolvedValue({ id: 1, name: '更新后的平台' }),
    deletePlatform: vi.fn().mockResolvedValue(undefined)
  }
}))

describe('Platform Store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('初始化时平台列表为空', () => {
    const store = usePlatformStore()

    expect(store.platforms).toEqual([])
    expect(store.loaded).toBe(false)
    expect(store.loading).toBe(false)
  })

  it('platformCount 返回正确数量', () => {
    const store = usePlatformStore()
    store.platforms = [{ id: 1, name: '平台A' }, { id: 2, name: '平台B' }]

    expect(store.platformCount).toBe(2)
  })

  it('platformOptions 返回正确的选项格式', () => {
    const store = usePlatformStore()
    store.platforms = [
      { id: 1, name: '平台A' },
      { id: 2, name: '平台B' }
    ]

    expect(store.platformOptions).toEqual([
      { label: '平台A', value: 1 },
      { label: '平台B', value: 2 }
    ])
  })

  it('getPlatformById 返回正确的平台', () => {
    const store = usePlatformStore()
    store.platforms = [
      { id: 1, name: '平台A' },
      { id: 2, name: '平台B' }
    ]

    expect(store.getPlatformById(1)).toEqual({ id: 1, name: '平台A' })
    expect(store.getPlatformById(999)).toBeUndefined()
  })

  it('getPlatformByName 返回正确的平台', () => {
    const store = usePlatformStore()
    store.platforms = [
      { id: 1, name: '平台A' },
      { id: 2, name: '平台B' }
    ]

    expect(store.getPlatformByName('平台A')).toEqual({ id: 1, name: '平台A' })
    expect(store.getPlatformByName('不存在的平台')).toBeUndefined()
  })

  it('reset 清空状态', () => {
    const store = usePlatformStore()
    store.platforms = [{ id: 1, name: '平台A' }]
    store.loaded = true
    store.loading = true

    store.reset()

    expect(store.platforms).toEqual([])
    expect(store.loaded).toBe(false)
    expect(store.loading).toBe(false)
  })
})
