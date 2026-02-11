import { ref, computed } from 'vue'
import { systemSettingsApi } from '@/api/historicalProject'
import { ElMessage } from 'element-plus'

// 插件类型
export type PluginType = 'graduation' | 'github' | 'parts' | 'video-playback'

// 插件设置键名（用于API）
const PLUGIN_KEYS: Record<PluginType, string> = {
  graduation: 'graduation',
  github: 'github',
  parts: 'parts',
  'video-playback': 'video-playback'
}

export function usePluginSettings() {
  // 从数据库加载插件设置（全局共享）
  const graduationEnabledProjectIds = ref<number[]>([])
  const githubEnabledProjectIds = ref<number[]>([])
  const partsEnabledProjectIds = ref<number[]>([])
  const videoPlaybackEnabledProjectIds = ref<number[]>([])
  const loading = ref(false)

  // 加载插件设置
  const loadPluginSettings = async () => {
    loading.value = true
    try {
      const settings = await systemSettingsApi.getPluginSettings()
      graduationEnabledProjectIds.value = settings.graduation || []
      githubEnabledProjectIds.value = settings.github || []
      partsEnabledProjectIds.value = settings.parts || []
      videoPlaybackEnabledProjectIds.value = settings['video-playback'] || []
      console.log('插件设置加载成功:', settings)
    } catch (error) {
      console.error('加载插件设置失败:', error)
      // 如果加载失败，使用空数组作为默认值
      graduationEnabledProjectIds.value = []
      githubEnabledProjectIds.value = []
      partsEnabledProjectIds.value = []
      videoPlaybackEnabledProjectIds.value = []
    } finally {
      loading.value = false
    }
  }

  // 保存插件设置到数据库
  const savePluginSettings = async () => {
    try {
      const settings: Record<string, number[]> = {
        graduation: graduationEnabledProjectIds.value,
        github: githubEnabledProjectIds.value,
        parts: partsEnabledProjectIds.value,
        'video-playback': videoPlaybackEnabledProjectIds.value
      }
      await systemSettingsApi.updatePluginSettings(settings)
      console.log('插件设置保存成功')
    } catch (error) {
      console.error('保存插件设置失败:', error)
      ElMessage.error('保存插件设置失败')
      throw error
    }
  }

  // 检查指定项目是否启用指定插件
  const isProjectEnabled = (projectId: number, pluginType: PluginType = 'graduation'): boolean => {
    if (pluginType === 'github') {
      return githubEnabledProjectIds.value.includes(projectId)
    }
    if (pluginType === 'parts') {
      return partsEnabledProjectIds.value.includes(projectId)
    }
    if (pluginType === 'video-playback') {
      return videoPlaybackEnabledProjectIds.value.includes(projectId)
    }
    return graduationEnabledProjectIds.value.includes(projectId)
  }

  // 启用指定项目的指定插件
  const enableProject = async (projectId: number, pluginType: PluginType = 'graduation') => {
    if (pluginType === 'github') {
      if (!githubEnabledProjectIds.value.includes(projectId)) {
        githubEnabledProjectIds.value.push(projectId)
        await savePluginSettings()
      }
    } else if (pluginType === 'parts') {
      if (!partsEnabledProjectIds.value.includes(projectId)) {
        partsEnabledProjectIds.value.push(projectId)
        await savePluginSettings()
      }
    } else if (pluginType === 'video-playback') {
      if (!videoPlaybackEnabledProjectIds.value.includes(projectId)) {
        videoPlaybackEnabledProjectIds.value.push(projectId)
        await savePluginSettings()
      }
    } else {
      if (!graduationEnabledProjectIds.value.includes(projectId)) {
        graduationEnabledProjectIds.value.push(projectId)
        await savePluginSettings()
      }
    }
  }

  // 禁用指定项目的指定插件
  const disableProject = async (projectId: number, pluginType: PluginType = 'graduation') => {
    if (pluginType === 'github') {
      const index = githubEnabledProjectIds.value.indexOf(projectId)
      if (index > -1) {
        githubEnabledProjectIds.value.splice(index, 1)
        await savePluginSettings()
      }
    } else if (pluginType === 'parts') {
      const index = partsEnabledProjectIds.value.indexOf(projectId)
      if (index > -1) {
        partsEnabledProjectIds.value.splice(index, 1)
        await savePluginSettings()
      }
    } else if (pluginType === 'video-playback') {
      const index = videoPlaybackEnabledProjectIds.value.indexOf(projectId)
      if (index > -1) {
        videoPlaybackEnabledProjectIds.value.splice(index, 1)
        await savePluginSettings()
      }
    } else {
      const index = graduationEnabledProjectIds.value.indexOf(projectId)
      if (index > -1) {
        graduationEnabledProjectIds.value.splice(index, 1)
        await savePluginSettings()
      }
    }
  }

  // 切换指定项目的指定插件状态
  const toggleProject = async (projectId: number, pluginType: PluginType = 'graduation') => {
    if (isProjectEnabled(projectId, pluginType)) {
      await disableProject(projectId, pluginType)
    } else {
      await enableProject(projectId, pluginType)
    }
  }

  // 批量启用项目
  const enableProjects = async (projectIds: number[], pluginType: PluginType = 'graduation') => {
    if (pluginType === 'github') {
      projectIds.forEach(id => {
        if (!githubEnabledProjectIds.value.includes(id)) {
          githubEnabledProjectIds.value.push(id)
        }
      })
      await savePluginSettings()
    } else if (pluginType === 'parts') {
      projectIds.forEach(id => {
        if (!partsEnabledProjectIds.value.includes(id)) {
          partsEnabledProjectIds.value.push(id)
        }
      })
      await savePluginSettings()
    } else if (pluginType === 'video-playback') {
      projectIds.forEach(id => {
        if (!videoPlaybackEnabledProjectIds.value.includes(id)) {
          videoPlaybackEnabledProjectIds.value.push(id)
        }
      })
      await savePluginSettings()
    } else {
      projectIds.forEach(id => {
        if (!graduationEnabledProjectIds.value.includes(id)) {
          graduationEnabledProjectIds.value.push(id)
        }
      })
      await savePluginSettings()
    }
  }

  // 批量禁用项目
  const disableProjects = async (projectIds: number[], pluginType: PluginType = 'graduation') => {
    if (pluginType === 'github') {
      githubEnabledProjectIds.value = githubEnabledProjectIds.value.filter(id => !projectIds.includes(id))
      await savePluginSettings()
    } else if (pluginType === 'parts') {
      partsEnabledProjectIds.value = partsEnabledProjectIds.value.filter(id => !projectIds.includes(id))
      await savePluginSettings()
    } else if (pluginType === 'video-playback') {
      videoPlaybackEnabledProjectIds.value = videoPlaybackEnabledProjectIds.value.filter(id => !projectIds.includes(id))
      await savePluginSettings()
    } else {
      graduationEnabledProjectIds.value = graduationEnabledProjectIds.value.filter(id => !projectIds.includes(id))
      await savePluginSettings()
    }
  }

  // 启用所有项目
  const enableAllProjects = async (allProjectIds: number[], pluginType: PluginType = 'graduation') => {
    if (pluginType === 'github') {
      githubEnabledProjectIds.value = [...allProjectIds]
      await savePluginSettings()
    } else if (pluginType === 'parts') {
      partsEnabledProjectIds.value = [...allProjectIds]
      await savePluginSettings()
    } else if (pluginType === 'video-playback') {
      videoPlaybackEnabledProjectIds.value = [...allProjectIds]
      await savePluginSettings()
    } else {
      graduationEnabledProjectIds.value = [...allProjectIds]
      await savePluginSettings()
    }
  }

  // 禁用所有项目
  const disableAllProjects = async (pluginType: PluginType = 'graduation') => {
    if (pluginType === 'github') {
      githubEnabledProjectIds.value = []
      await savePluginSettings()
    } else if (pluginType === 'parts') {
      partsEnabledProjectIds.value = []
      await savePluginSettings()
    } else if (pluginType === 'video-playback') {
      videoPlaybackEnabledProjectIds.value = []
      await savePluginSettings()
    } else {
      graduationEnabledProjectIds.value = []
      await savePluginSettings()
    }
  }

  // 获取启用的项目数量
  const getEnabledCount = (pluginType: PluginType = 'graduation'): number => {
    if (pluginType === 'github') {
      return githubEnabledProjectIds.value.length
    }
    if (pluginType === 'parts') {
      return partsEnabledProjectIds.value.length
    }
    if (pluginType === 'video-playback') {
      return videoPlaybackEnabledProjectIds.value.length
    }
    return graduationEnabledProjectIds.value.length
  }

  return {
    graduationEnabledProjectIds,
    githubEnabledProjectIds,
    partsEnabledProjectIds,
    videoPlaybackEnabledProjectIds,
    loading,
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

