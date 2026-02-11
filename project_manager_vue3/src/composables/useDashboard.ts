/**
 * Dashboard相关的组合式函数
 */
import { ref } from 'vue'
import { DashboardService } from '@/services/dashboard.service'
import type { DashboardStats } from '@/api/dashboard'

export function useDashboard() {
  const loading = ref(false)
  const stats = ref<DashboardStats>({
    today_todos: [],
    total_revenue: 0,
    platform_revenue: {},
    pending_projects_count: 0,
    in_progress_steps_count: 0,
  })

  /**
   * 加载统计数据
   */
  const loadStats = async () => {
    loading.value = true
    try {
      stats.value = await DashboardService.getStats()
    } catch (error) {
      // 错误已在Service层处理
    } finally {
      loading.value = false
    }
  }

  return {
    loading,
    stats,
    loadStats,
  }
}

