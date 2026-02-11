/**
 * 项目相关的组合式函数
 */
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ProjectService } from '@/services/project.service'
import { PlatformService } from '@/services/platform.service'
import type { Project, ProjectCreate, ProjectUpdate, ProjectStep, ProjectStepCreate, ProjectStepUpdate } from '@/api/project'
import type { Platform } from '@/api/platform'
import { useUserStore } from '@/stores/user'

export function useProject() {
  const router = useRouter()
  const userStore = useUserStore()
  
  const loading = ref(false)
  const projects = ref<Project[]>([])
  const platforms = ref<Platform[]>([])
  const currentProject = ref<Project | null>(null)

  /**
   * 加载平台列表
   */
  const loadPlatforms = async () => {
    try {
      platforms.value = await PlatformService.getPlatformList()
    } catch (error) {
      // 错误已在Service层处理
    }
  }

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
      const params: any = {}
      if (filters?.platform_id) params.platform_id = filters.platform_id
      if (filters?.status) params.status = filters.status
      if (filters?.tag_ids) params.tag_ids = filters.tag_ids
      
      console.log('Loading projects with params:', params)
      const data = await ProjectService.getProjectList(params)
      console.log('Projects loaded:', data)
      projects.value = data || []
    } catch (error) {
      console.error('Error loading projects:', error)
      projects.value = []
      // 错误已在Service层处理
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
      const project = await ProjectService.getProjectById(id)
      // 调试：检查接收到的项目数据
      console.log('useProject.loadProject - received project:', project)
      console.log('useProject.loadProject - tags:', project.tags)
      console.log('useProject.loadProject - tags type:', typeof project.tags)
      console.log('useProject.loadProject - tags is array:', Array.isArray(project.tags))
      currentProject.value = project
      return currentProject.value
    } catch (error) {
      router.back()
      throw error
    } finally {
      loading.value = false
    }
  }

  /**
   * 创建项目
   */
  const createProject = async (data: ProjectCreate) => {
    // 设置用户ID
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
    // 调试：检查更新后的项目数据
    console.log('useProject.updateProject - updated project:', project)
    console.log('useProject.updateProject - tags:', project.tags)
    if (currentProject.value?.id === id) {
      currentProject.value = project
      console.log('useProject.updateProject - currentProject updated:', currentProject.value)
      console.log('useProject.updateProject - currentProject.tags:', currentProject.value.tags)
    }
    await loadProjects()
    return project
  }

  /**
   * 删除项目
   */
  const deleteProject = async (id: number) => {
    await ProjectService.deleteProject(id)
    await loadProjects()
  }

  /**
   * 创建步骤
   */
  const createStep = async (projectId: number, data: ProjectStepCreate) => {
    const step = await ProjectService.createStep(projectId, data)
    await loadProject(projectId)
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
   * 跳转到项目详情
   */
  const goToDetail = (id: number) => {
    router.push(`/projects/${id}`)
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

  return {
    // 状态
    loading,
    projects,
    platforms,
    currentProject,
    
    // 方法
    loadPlatforms,
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
    goToDetail,
    getProgress,
    getProgressColor,
    getCurrentStatus,
    getCurrentStatusType,
  }
}

