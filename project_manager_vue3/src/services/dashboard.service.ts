/**
 * Dashboard服务层
 * 处理Dashboard相关的业务逻辑
 */
import { dashboardApi, type DashboardStats } from '@/api/dashboard'
import { ElMessage } from 'element-plus'

export class DashboardService {
  /**
   * 获取Dashboard统计数据
   */
  static async getStats(): Promise<DashboardStats> {
    try {
      return await dashboardApi.getStats()
    } catch (error: any) {
      const message = error?.response?.data?.detail || '加载数据失败'
      ElMessage.error(message)
      throw error
    }
  }
}

