import request from './request'
import type { TodoItem } from './todo'

export interface DashboardStats {
  today_todos: TodoItem[]
  total_revenue: number
  platform_revenue: Record<string, number>
  pending_projects_count: number
  in_progress_steps_count: number
}

export const dashboardApi = {
  getStats: () => {
    return request.get<DashboardStats>('/dashboard/stats')
  },
}

