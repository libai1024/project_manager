/**
 * 平台相关的组合式函数
 */
import { ref } from 'vue'
import { PlatformService } from '@/services/platform.service'
import type { Platform, PlatformCreate, PlatformUpdate } from '@/api/platform'

export function usePlatform() {
  const loading = ref(false)
  const platforms = ref<Platform[]>([])

  /**
   * 加载平台列表
   */
  const loadPlatforms = async () => {
    loading.value = true
    try {
      platforms.value = await PlatformService.getPlatformList()
    } catch (error) {
      // 错误已在Service层处理
    } finally {
      loading.value = false
    }
  }

  /**
   * 创建平台
   */
  const createPlatform = async (data: PlatformCreate) => {
    const platform = await PlatformService.createPlatform(data)
    await loadPlatforms()
    return platform
  }

  /**
   * 更新平台
   */
  const updatePlatform = async (id: number, data: PlatformUpdate) => {
    const platform = await PlatformService.updatePlatform(id, data)
    await loadPlatforms()
    return platform
  }

  /**
   * 删除平台
   */
  const deletePlatform = async (id: number) => {
    await PlatformService.deletePlatform(id)
    await loadPlatforms()
  }

  return {
    loading,
    platforms,
    loadPlatforms,
    createPlatform,
    updatePlatform,
    deletePlatform,
  }
}

