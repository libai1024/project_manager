/**
 * 插件设置组合式函数
 *
 * 重构后使用 Map 模式消除重复的 if-else 语句
 */
import { ref, computed } from 'vue'
import { systemSettingsApi } from '@/api/historicalProject'
import { ElMessage } from 'element-plus'

// 插件类型
export type PluginType = 'graduation' | 'github' | 'parts' | 'video-playback'

// 插件键名映射（API 使用）
const PLUGIN_KEYS: Record<PluginType, string> = {
  graduation: 'graduation',
  github: 'github',
  parts: 'parts',
  'video-playback': 'video-playback'
}

export function usePluginSettings() {
  // 使用 Map 存储各插件的启用项目 ID
  const pluginEnabledIds = ref<Map<PluginType, number[]>>(new Map([
    ['graduation', []],
    ['github', []],
    ['parts', []],
    ['video-playback', []]
  ]))

  const loading = ref(false)

  /**
   * 获取指定插件的启用项目 ID 数组
   */
  const getEnabledIds = (pluginType: PluginType): number[] => {
    return pluginEnabledIds.value.get(pluginType) || []
  }

  /**
   * 加载插件设置
   */
  const loadPluginSettings = async () => {
    loading.value = true
    try {
      const settings = await systemSettingsApi.getPluginSettings()
      // 使用 Map 批量更新
      const newMap = new Map<PluginType, number[]>()
      ;(Object.keys(PLUGIN_KEYS) as PluginType[]).forEach(key => {
        newMap.set(key, settings[PLUGIN_KEYS[key]] || [])
      })
      pluginEnabledIds.value = newMap
    } catch (error) {
      console.error('加载插件设置失败:', error)
      // 加载失败时使用空数组
      pluginEnabledIds.value = new Map([
        ['graduation', []],
        ['github', []],
        ['parts', []],
        ['video-playback', []]
      ])
    } finally {
      loading.value = false
    }
  }

  /**
   * 保存插件设置到数据库
   */
  const savePluginSettings = async () => {
    try {
      const settings: Record<string, number[]> = {}
      pluginEnabledIds.value.forEach((ids, key) => {
        settings[PLUGIN_KEYS[key]] = ids
      })
      await systemSettingsApi.updatePluginSettings(settings)
    } catch (error) {
      console.error('保存插件设置失败:', error)
      ElMessage.error('保存插件设置失败')
      throw error
    }
  }

  /**
   * 检查指定项目是否启用指定插件
   */
  const isProjectEnabled = (projectId: number, pluginType: PluginType = 'graduation'): boolean => {
    return getEnabledIds(pluginType).includes(projectId)
  }

  /**
   * 更新插件启用状态（内部方法）
   */
  const updatePluginIds = async (
    pluginType: PluginType,
    updater: (ids: number[]) => number[]
  ) => {
    const currentIds = getEnabledIds(pluginType)
    const newIds = updater([...currentIds])

    // 只有在值真正改变时才更新和保存
    if (JSON.stringify(currentIds) !== JSON.stringify(newIds)) {
      pluginEnabledIds.value.set(pluginType, newIds)
      await savePluginSettings()
    }
  }

  /**
   * 启用指定项目的指定插件
   */
  const enableProject = async (projectId: number, pluginType: PluginType = 'graduation') => {
    await updatePluginIds(pluginType, ids => {
      if (!ids.includes(projectId)) {
        ids.push(projectId)
      }
      return ids
    })
  }

  /**
   * 禁用指定项目的指定插件
   */
  const disableProject = async (projectId: number, pluginType: PluginType = 'graduation') => {
    await updatePluginIds(pluginType, ids => {
      return ids.filter(id => id !== projectId)
    })
  }

  /**
   * 切换指定项目的指定插件状态
   */
  const toggleProject = async (projectId: number, pluginType: PluginType = 'graduation') => {
    if (isProjectEnabled(projectId, pluginType)) {
      await disableProject(projectId, pluginType)
    } else {
      await enableProject(projectId, pluginType)
    }
  }

  /**
   * 批量启用项目
   */
  const enableProjects = async (projectIds: number[], pluginType: PluginType = 'graduation') => {
    await updatePluginIds(pluginType, ids => {
      const newIds = [...ids]
      projectIds.forEach(id => {
        if (!newIds.includes(id)) {
          newIds.push(id)
        }
      })
      return newIds
    })
  }

  /**
   * 批量禁用项目
   */
  const disableProjects = async (projectIds: number[], pluginType: PluginType = 'graduation') => {
    await updatePluginIds(pluginType, ids => {
      return ids.filter(id => !projectIds.includes(id))
    })
  }

  /**
   * 启用所有项目
   */
  const enableAllProjects = async (allProjectIds: number[], pluginType: PluginType = 'graduation') => {
    await updatePluginIds(pluginType, () => [...allProjectIds])
  }

  /**
   * 禁用所有项目
   */
  const disableAllProjects = async (pluginType: PluginType = 'graduation') => {
    await updatePluginIds(pluginType, () => [])
  }

  /**
   * 获取启用的项目数量
   */
  const getEnabledCount = (pluginType: PluginType = 'graduation'): number => {
    return getEnabledIds(pluginType).length
  }

  // 为保持向后兼容，提供独立的响应式引用
  const graduationEnabledProjectIds = computed(() => getEnabledIds('graduation'))
  const githubEnabledProjectIds = computed(() => getEnabledIds('github'))
  const partsEnabledProjectIds = computed(() => getEnabledIds('parts'))
  const videoPlaybackEnabledProjectIds = computed(() => getEnabledIds('video-playback'))

  return {
    // 响应式引用（保持向后兼容）
    graduationEnabledProjectIds,
    githubEnabledProjectIds,
    partsEnabledProjectIds,
    videoPlaybackEnabledProjectIds,
    loading,

    // 方法
    isProjectEnabled,
    enableProject,
    disableProject,
    toggleProject,
    enableProjects,
    disableProjects,
    enableAllProjects,
    disableAllProjects,
    getEnabledCount,
    loadPluginSettings,
    savePluginSettings,
  }
}
