/**
 * 平台状态管理 Store
 *
 * 职责：
 * - 管理平台列表状态
 * - 提供平台的 CRUD 操作
 * - 缓存平台数据
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { PlatformService } from '@/services/platform.service'
import type { Platform, PlatformCreate, PlatformUpdate } from '@/api/platform'

export const usePlatformStore = defineStore('platform', () => {
  // 状态
  const loading = ref(false)
  const platforms = ref<Platform[]>([])
  const loaded = ref(false)

  // 计算属性
  const platformCount = computed(() => platforms.value.length)

  const platformOptions = computed(() =>
    platforms.value.map(p => ({
      label: p.name,
      value: p.id
    }))
  )

  /**
   * 加载平台列表
   */
  const loadPlatforms = async (force = false) => {
    // 如果已加载且不强制刷新，直接返回
    if (loaded.value && !force) {
      return platforms.value
    }

    loading.value = true
    try {
      platforms.value = await PlatformService.getPlatformList()
      loaded.value = true
      return platforms.value
    } finally {
      loading.value = false
    }
  }

  /**
   * 根据 ID 获取平台
   */
  const getPlatformById = (id: number): Platform | undefined => {
    return platforms.value.find(p => p.id === id)
  }

  /**
   * 根据名称获取平台
   */
  const getPlatformByName = (name: string): Platform | undefined => {
    return platforms.value.find(p => p.name === name)
  }

  /**
   * 创建平台
   */
  const createPlatform = async (data: PlatformCreate) => {
    const platform = await PlatformService.createPlatform(data)
    platforms.value.push(platform)
    return platform
  }

  /**
   * 更新平台
   */
  const updatePlatform = async (id: number, data: PlatformUpdate) => {
    const platform = await PlatformService.updatePlatform(id, data)
    const index = platforms.value.findIndex(p => p.id === id)
    if (index !== -1) {
      platforms.value[index] = platform
    }
    return platform
  }

  /**
   * 删除平台
   */
  const deletePlatform = async (id: number) => {
    await PlatformService.deletePlatform(id)
    platforms.value = platforms.value.filter(p => p.id !== id)
  }

  /**
   * 重置 store
   */
  const reset = () => {
    loading.value = false
    platforms.value = []
    loaded.value = false
  }

  return {
    // 状态
    loading,
    platforms,
    loaded,

    // 计算属性
    platformCount,
    platformOptions,

    // 方法
    loadPlatforms,
    getPlatformById,
    getPlatformByName,
    createPlatform,
    updatePlatform,
    deletePlatform,
    reset,
  }
})
