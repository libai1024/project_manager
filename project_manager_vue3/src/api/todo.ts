import request from './request'

export interface TodoItem {
  id: number
  project_id: number
  project_title: string
  description: string
  step_ids: number[]
  step_names: string[]
  completion_note?: string
  is_completed: boolean
  target_date?: string
  created_at: string
  updated_at: string
  student_name?: string  // 添加学生姓名字段
}

export interface TodoCalendarItem {
  date: string
  todo_count: number
  completed_count: number
  revenue?: number  // 每日收入
}

export interface TodoCreate {
  project_id: number
  description: string
  step_ids: number[]
  target_date?: string
}

export interface TodoUpdate {
  description?: string
  completion_note?: string
  is_completed?: boolean
  target_date?: string
  attachment_ids?: number[]  // 附件ID列表
}

export const todoApi = {
  // 获取指定日期的待办列表
  getTodos: (targetDate?: string) => {
    const params: any = {}
    if (targetDate) {
      params.target_date = targetDate
    }
    return request.get<TodoItem[]>('/todos/', { params })
  },
  
  // 创建待办
  createTodo: (data: TodoCreate) => {
    return request.post<TodoItem>('/todos/', data)
  },
  
  // 更新待办
  updateTodo: (todoId: number, data: TodoUpdate) => {
    return request.put<TodoItem>(`/todos/${todoId}`, data)
  },
  
  // 删除待办
  deleteTodo: (todoId: number) => {
    return request.delete(`/todos/${todoId}`)
  },
  
  // 获取待办日历数据
  getCalendar: (year?: number, month?: number) => {
    const params: any = {}
    if (year) params.year = year
    if (month) params.month = month
    return request.get<TodoCalendarItem[]>('/todos/calendar', { params })
  },
}
