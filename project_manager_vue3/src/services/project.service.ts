/**
 * 项目服务层
 * 处理项目相关的业务逻辑
 */
import { projectApi, type Project, type ProjectCreate, type ProjectUpdate, type ProjectStep, type ProjectStepCreate, type ProjectStepUpdate } from '@/api/project'
import { ElMessage } from 'element-plus'

export class ProjectService {
  /**
   * 获取项目列表
   */
  static async getProjectList(params?: {
    skip?: number
    limit?: number
    user_id?: number
    platform_id?: number
    status?: string
    tag_ids?: string
  }): Promise<Project[]> {
    try {
      return await projectApi.list(params)
    } catch (error: any) {
      const message = error?.response?.data?.detail || '获取项目列表失败'
      ElMessage.error(message)
      throw error
    }
  }

  /**
   * 获取项目详情
   */
  static async getProjectById(id: number): Promise<Project> {
    try {
      const project = await projectApi.get(id)
      // 调试：检查标签数据
      console.log('ProjectService.getProjectById - received project:', project)
      console.log('ProjectService.getProjectById - tags:', project.tags)
      console.log('ProjectService.getProjectById - tags length:', project.tags?.length || 0)
      return project
    } catch (error: any) {
      const message = error?.response?.data?.detail || '获取项目详情失败'
      ElMessage.error(message)
      throw error
    }
  }

  /**
   * 创建项目
   */
  static async createProject(data: ProjectCreate): Promise<Project> {
    try {
      const project = await projectApi.create(data)
      ElMessage.success('项目创建成功')
      return project
    } catch (error: any) {
      const message = error?.response?.data?.detail || '创建项目失败'
      ElMessage.error(message)
      throw error
    }
  }

  /**
   * 更新项目
   */
  static async updateProject(id: number, data: ProjectUpdate): Promise<Project> {
    try {
      const project = await projectApi.update(id, data)
      ElMessage.success('项目更新成功')
      return project
    } catch (error: any) {
      const message = error?.response?.data?.detail || '更新项目失败'
      ElMessage.error(message)
      throw error
    }
  }

  /**
   * 删除项目
   */
  static async deleteProject(id: number): Promise<void> {
    try {
      await projectApi.delete(id)
      ElMessage.success('项目删除成功')
    } catch (error: any) {
      const message = error?.response?.data?.detail || '删除项目失败'
      ElMessage.error(message)
      throw error
    }
  }

  /**
   * 创建步骤
   */
  static async createStep(projectId: number, data: ProjectStepCreate): Promise<ProjectStep> {
    try {
      const step = await projectApi.createStep(projectId, data)
      ElMessage.success('步骤创建成功')
      return step
    } catch (error: any) {
      const message = error?.response?.data?.detail || '创建步骤失败'
      ElMessage.error(message)
      throw error
    }
  }

  /**
   * 更新步骤
   */
  static async updateStep(stepId: number, data: ProjectStepUpdate): Promise<ProjectStep> {
    try {
      const step = await projectApi.updateStep(stepId, data)
      ElMessage.success('步骤更新成功')
      return step
    } catch (error: any) {
      const message = error?.response?.data?.detail || '更新步骤失败'
      ElMessage.error(message)
      throw error
    }
  }

  /**
   * 删除步骤
   */
  static async deleteStep(stepId: number): Promise<void> {
    try {
      await projectApi.deleteStep(stepId)
      ElMessage.success('步骤删除成功')
    } catch (error: any) {
      const message = error?.response?.data?.detail || '删除步骤失败'
      ElMessage.error(message)
      throw error
    }
  }

  /**
   * 切换步骤待办状态
   */
  static async toggleStepTodo(stepId: number): Promise<ProjectStep> {
    try {
      return await projectApi.toggleStepTodo(stepId)
    } catch (error: any) {
      const message = error?.response?.data?.detail || '操作失败'
      ElMessage.error(message)
      throw error
    }
  }

  /**
   * 重新排序步骤
   */
  static async reorderSteps(stepOrders: Array<{ step_id: number; order_index: number }>): Promise<void> {
    try {
      await projectApi.reorderSteps(stepOrders)
      ElMessage.success('步骤顺序已更新')
    } catch (error: any) {
      const message = error?.response?.data?.detail || '更新步骤顺序失败'
      ElMessage.error(message)
      throw error
    }
  }

  /**
   * 计算项目进度
   */
  static calculateProgress(steps: ProjectStep[]): number {
    if (!steps || steps.length === 0) {
      return 0
    }
    const completedSteps = steps.filter(step => step.status === '已完成').length
    return Math.round((completedSteps / steps.length) * 100)
  }

  /**
   * 获取进度条颜色
   */
  static getProgressColor(percentage: number): string {
    if (percentage === 100) {
      return '#67c23a' // 绿色 - 完成
    } else if (percentage >= 50) {
      return '#409eff' // 蓝色 - 进行中
    } else if (percentage > 0) {
      return '#e6a23c' // 橙色 - 刚开始
    } else {
      return '#909399' // 灰色 - 未开始
    }
  }

  /**
   * 获取当前状态
   */
  static getCurrentStatus(project: Project): string {
    if (!project.steps || project.steps.length === 0) {
      return '未开始'
    }
    
    const sortedSteps = [...project.steps].sort((a, b) => a.order_index - b.order_index)
    
    // 找到最后一个状态为"已完成"的步骤
    let lastDoneStep = null
    for (let i = sortedSteps.length - 1; i >= 0; i--) {
      if (sortedSteps[i].status === '已完成') {
        lastDoneStep = sortedSteps[i]
        break
      }
    }
    
    // 如果所有步骤都完成
    const allDone = sortedSteps.every(step => step.status === '已完成')
    if (allDone) {
      return '已完成'
    }
    
    // 如果有完成的步骤，返回最后一个完成步骤的名称
    if (lastDoneStep) {
      return lastDoneStep.name
    }
    
    // 如果没有完成的步骤，返回第一个步骤的名称
    return sortedSteps[0]?.name || '未开始'
  }

  /**
   * 获取当前状态的标签类型
   */
  static getCurrentStatusType(project: Project): string {
    const status = this.getCurrentStatus(project)
    
    if (status === '已完成') {
      return 'success'
    }
    
    if (status === '未开始') {
      return 'info'
    }
    
    // 检查是否有进行中的步骤
    const hasInProgress = project.steps?.some(step => step.status === '进行中')
    if (hasInProgress) {
      return 'warning'
    }
    
    return 'info'
  }
}

