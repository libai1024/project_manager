/**
 * usePluginSettings Composable 单元测试
 */
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { usePluginSettings } from '@/composables/usePluginSettings'

// Mock system settings API
vi.mock('@/api/historicalProject', () => ({
  systemSettingsApi: {
    getPluginSettings: vi.fn().mockResolvedValue({
      graduation: [1, 2],
      github: [1],
      parts: [],
      'video-playback': [3]
    }),
    updatePluginSettings: vi.fn().mockResolvedValue(undefined)
  }
}))

// Mock Element Plus
vi.mock('element-plus', () => ({
  ElMessage: {
    error: vi.fn()
  }
}))

describe('usePluginSettings', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('初始化时所有插件 ID 列表为空', () => {
    const {
      graduationEnabledProjectIds,
      githubEnabledProjectIds,
      partsEnabledProjectIds,
      videoPlaybackEnabledProjectIds
    } = usePluginSettings()

    expect(graduationEnabledProjectIds.value).toEqual([])
    expect(githubEnabledProjectIds.value).toEqual([])
    expect(partsEnabledProjectIds.value).toEqual([])
    expect(videoPlaybackEnabledProjectIds.value).toEqual([])
  })

  it('loadPluginSettings 加载设置', async () => {
    const { loadPluginSettings, graduationEnabledProjectIds, githubEnabledProjectIds } = usePluginSettings()

    await loadPluginSettings()

    expect(graduationEnabledProjectIds.value).toEqual([1, 2])
    expect(githubEnabledProjectIds.value).toEqual([1])
  })

  it('isProjectEnabled 检查项目是否启用插件', async () => {
    const { loadPluginSettings, isProjectEnabled } = usePluginSettings()

    await loadPluginSettings()

    expect(isProjectEnabled(1, 'graduation')).toBe(true)
    expect(isProjectEnabled(3, 'graduation')).toBe(false)
    expect(isProjectEnabled(1, 'github')).toBe(true)
    expect(isProjectEnabled(2, 'github')).toBe(false)
  })

  it('getEnabledCount 返回正确的数量', async () => {
    const { loadPluginSettings, getEnabledCount } = usePluginSettings()

    await loadPluginSettings()

    expect(getEnabledCount('graduation')).toBe(2)
    expect(getEnabledCount('github')).toBe(1)
    expect(getEnabledCount('parts')).toBe(0)
    expect(getEnabledCount('video-playback')).toBe(1)
  })

  it('enableProject 启用项目插件', async () => {
    const { loadPluginSettings, enableProject, isProjectEnabled } = usePluginSettings()

    await loadPluginSettings()
    await enableProject(3, 'graduation')

    expect(isProjectEnabled(3, 'graduation')).toBe(true)
  })

  it('disableProject 禁用项目插件', async () => {
    const { loadPluginSettings, disableProject, isProjectEnabled } = usePluginSettings()

    await loadPluginSettings()
    await disableProject(1, 'graduation')

    expect(isProjectEnabled(1, 'graduation')).toBe(false)
  })

  it('toggleProject 切换项目插件状态', async () => {
    const { loadPluginSettings, toggleProject, isProjectEnabled } = usePluginSettings()

    await loadPluginSettings()

    // 切换关闭
    await toggleProject(1, 'graduation')
    expect(isProjectEnabled(1, 'graduation')).toBe(false)

    // 切换开启
    await toggleProject(1, 'graduation')
    expect(isProjectEnabled(1, 'graduation')).toBe(true)
  })

  it('enableAllProjects 启用所有项目', async () => {
    const { loadPluginSettings, enableAllProjects, getEnabledCount } = usePluginSettings()

    await loadPluginSettings()
    await enableAllProjects([1, 2, 3, 4, 5], 'parts')

    expect(getEnabledCount('parts')).toBe(5)
  })

  it('disableAllProjects 禁用所有项目', async () => {
    const { loadPluginSettings, disableAllProjects, getEnabledCount } = usePluginSettings()

    await loadPluginSettings()
    await disableAllProjects('graduation')

    expect(getEnabledCount('graduation')).toBe(0)
  })
})
