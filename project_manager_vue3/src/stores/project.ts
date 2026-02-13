/**
 * 项目状态管理 Store
 *
 * 职责：
 * - 管理项目列表和当前项目状态
 * - 提供项目的 CRUD 操作
 * - 管理项目步骤
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { ProjectService } from '@/services/project.service'
import type { Project, ProjectCreate, ProjectUpdate, ProjectStep, ProjectStepCreate, ProjectStepUpdate } from '@/api/project'
import { useUserStore } from './user'

export const useProjectStore = defineStore('project', () => {
  // 状态
  const loading = ref(false)
  const projects = ref<Project[]>([])
  const currentProject = ref<Project | null>(null)

  // 计算属性
  const projectCount = computed(() => projects.value.length)

  const activeProjects = computed(() =>
    projects.value.filter(p => p.status !== '已结账')
  )

  const completedProjects = computed(() =>
    projects.value.filter(p => p.status === '已结账')
  )

  /**
   * 加载项目列表
   */
  const loadProjects = async (filters?: {
    platform_id?: number
    status?: string
    tag_ids?: string
  }) => {
    loading.value = true
    try {
      const params: Record<string, unknown> = {}
      if (filters?.platform_id) params.platform_id = filters.platform_id
      if (filters?.status) params.status = filters.status
      if (filters?.tag_ids) params.tag_ids = filters.tag_ids

      projects.value = await ProjectService.getProjectList(params) || []
    } catch {
      projects.value = []
    } finally {
      loading.value = false
    }
  }

  /**
   * 加载项目详情
   */
  const loadProject = async (id: number) => {
    loading.value = true
    try {
      currentProject.value = await ProjectService.getProjectById(id)
      return currentProject.value
    } finally {
      loading.value = false
    }
  }

  /**
   * 创建项目
   */
  const createProject = async (data: ProjectCreate) => {
    const userStore = useUserStore()
    if (!data.user_id) {
      data.user_id = userStore.userInfo?.id || 0
    }

    const project = await ProjectService.createProject(data)
    await loadProjects()
    return project
  }

  /**
   * 更新项目
   */
  const updateProject = async (id: number, data: ProjectUpdate) => {
    const project = await ProjectService.updateProject(id, data)
    if (currentProject.value?.id === id) {
      currentProject.value = project
    }
    // 更新列表中的项目
    const index = projects.value.findIndex(p => p.id === id)
    if (index !== -1) {
      projects.value[index] = project
    }
    return project
  }

  /**
   * 删除项目
   */
  const deleteProject = async (id: number) => {
    await ProjectService.deleteProject(id)
    projects.value = projects.value.filter(p => p.id !== id)
    if (currentProject.value?.id === id) {
      currentProject.value = null
    }
  }

  /**
   * 创建步骤
   */
  const createStep = async (projectId: number, data: ProjectStepCreate) => {
    const step = await ProjectService.createStep(projectId, data)
    if (currentProject.value?.id === projectId) {
      await loadProject(projectId)
    }
    return step
  }

  /**
   * 更新步骤
   */
  const updateStep = async (stepId: number, data: ProjectStepUpdate) => {
    const step = await ProjectService.updateStep(stepId, data)
    if (currentProject.value) {
      await loadProject(currentProject.value.id)
    }
    return step
  }

  /**
   * 删除步骤
   */
  const deleteStep = async (stepId: number) => {
    await ProjectService.deleteStep(stepId)
    if (currentProject.value) {
      await loadProject(currentProject.value.id)
    }
  }

  /**
   * 切换步骤待办状态
   */
  const toggleStepTodo = async (stepId: number) => {
    await ProjectService.toggleStepTodo(stepId)
    if (currentProject.value) {
      await loadProject(currentProject.value.id)
    }
  }

  /**
   * 重新排序步骤
   */
  const reorderSteps = async (stepOrders: Array<{ step_id: number; order_index: number }>) => {
    await ProjectService.reorderSteps(stepOrders)
    if (currentProject.value) {
      await loadProject(currentProject.value.id)
    }
  }

  /**
   * 计算项目进度
   */
  const getProgress = (project: Project) => {
    return ProjectService.calculateProgress(project.steps || [])
  }

  /**
   * 获取进度条颜色
   */
  const getProgressColor = (percentage: number) => {
    return ProjectService.getProgressColor(percentage)
  }

  /**
   * 获取当前状态
   */
  const getCurrentStatus = (project: Project) => {
    return ProjectService.getCurrentStatus(project)
  }

  /**
   * 获取当前状态的标签类型
   */
  const getCurrentStatusType = (project: Project) => {
    return ProjectService.getCurrentStatusType(project)
  }

  /**
   * 清空当前项目
   */
  const clearCurrentProject = () => {
    currentProject.value = null
  }

  /**
   * 重置 store
   */
  const reset = () => {
    loading.value = false
    projects.value = []
    currentProject.value = null
  }

  return {
    // 状态
    loading,
    projects,
    currentProject,

    // 计算属性
    projectCount,
    activeProjects,
    completedProjects,

    // 方法
    loadProjects,
    loadProject,
    createProject,
    updateProject,
    deleteProject,
    createStep,
    updateStep,
    deleteStep,
    toggleStepTodo,
    reorderSteps,
    getProgress,
    getProgressColor,
    getCurrentStatus,
    getCurrentStatusType,
    clearCurrentProject,
    reset,
  }
})
