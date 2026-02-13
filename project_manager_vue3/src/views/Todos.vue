<template>
  <div class="todos-page" ref="todosPageRef">
    <el-row :gutter="20" class="todos-layout">
      <!-- 左侧：日期快速选择 -->
      <el-col :xs="24" :sm="8" :md="6" class="date-selector-col">
        <DateSelector
          :selected-date="selectedDate"
          :today="today"
          :calendar-data="calendarData"
          @select="selectDate"
          @scroll="handleDateScroll"
        />
      </el-col>

      <!-- 中间：待办详情 -->
      <el-col :xs="24" :sm="16" :md="12" class="todos-detail-col">
        <TodoList
          :todos="todos"
          :selected-date="selectedDate"
          :loading="loading"
          :show-input="showTodoInput"
          @add-todo="showTodoInput = true"
          @cancel-input="showTodoInput = false"
          @toggle-complete="toggleTodoComplete"
          @view="showTodoDetail"
          @edit="showEditDialog"
          @delete="deleteTodo"
          @add="handleTodoAdd"
        />
      </el-col>

      <!-- 右侧：日历和统计 -->
      <el-col :xs="24" :sm="24" :md="6" class="calendar-col">
        <!-- 待办日历 -->
        <el-card class="calendar-card">
          <template #header>
            <div class="card-header">
              <span>待办日历</span>
              <div class="calendar-nav">
                <el-button
                  type="text"
                  size="small"
                  @click="prevMonth"
                >
                  <el-icon><ArrowLeft /></el-icon>
                </el-button>
                <span class="calendar-month">{{ currentYear }}年{{ currentMonth }}月</span>
                <el-button
                  type="text"
                  size="small"
                  @click="nextMonth"
                >
                  <el-icon><ArrowRight /></el-icon>
                </el-button>
              </div>
            </div>
          </template>
          
          <div class="calendar-wrapper">
            <div class="calendar-weekdays">
              <div v-for="day in weekdays" :key="day" class="weekday">{{ day }}</div>
            </div>
            <div class="calendar-days">
              <div
                v-for="(day, index) in calendarDays"
                :key="index"
                class="calendar-day"
                :class="{
                  'calendar-day-other-month': day.otherMonth,
                  'calendar-day-today': day.isToday,
                  'calendar-day-selected': day.date === selectedDate,
                  'calendar-day-has-todos': day.todoCount > 0,
                  'calendar-day-has-completed': day.completedCount > 0
                }"
                @click="selectDate(day.date)"
              >
                <span class="day-number">{{ day.day }}</span>
                <div class="day-indicators">
                  <div v-if="day.todoCount > 0 || day.completedCount > 0" class="day-stats">
                    <span v-if="day.todoCount > 0" class="indicator-todo" :title="`${day.todoCount}个待办`">
                      {{ day.todoCount }}
                    </span>
                    <span v-if="day.completedCount > 0" class="indicator-completed" :title="`${day.completedCount}个已完成`">
                      {{ day.completedCount }}
                    </span>
                  </div>
                  <div v-if="day.revenue > 0" class="day-revenue" :title="`收入 ¥${day.revenue.toFixed(2)}`">
                    <el-icon><Money /></el-icon>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </el-card>
        
        <!-- 统计信息 -->
        <el-card class="stats-card" style="margin-top: 20px">
          <template #header>
            <div class="card-header">
              <span>统计信息</span>
            </div>
          </template>
          
          <div class="stats-content">
            <div class="stat-item">
              <div class="stat-label">今日待办</div>
              <div class="stat-value">{{ todayTodoCount }}</div>
            </div>
            <div class="stat-item">
              <div class="stat-label">本周待办</div>
              <div class="stat-value">{{ weekTodoCount }}</div>
            </div>
            <div class="stat-item">
              <div class="stat-label">本月待办</div>
              <div class="stat-value">{{ monthTodoCount }}</div>
            </div>
            <div class="stat-item">
              <div class="stat-label">完成率</div>
              <div class="stat-value">{{ completionRate }}%</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 待办详情弹窗 -->
    <el-dialog
      v-model="showDetailDialog"
      title="待办详情"
      width="900px"
      :close-on-click-modal="false"
      class="todo-detail-dialog"
    >
      <div v-if="currentTodoDetail" class="todo-detail-content">
        <!-- 基本信息 -->
        <div class="detail-section">
          <div class="detail-item">
            <span class="detail-label">项目名称：</span>
            <span class="detail-value">{{ currentTodoDetail.project_title }}</span>
          </div>
          <div v-if="currentTodoDetail.step_names && currentTodoDetail.step_names.length > 0" class="detail-item">
            <span class="detail-label">项目步骤：</span>
            <div class="detail-value">
              <el-popover
                placement="top"
                :width="300"
                trigger="hover"
              >
                <template #reference>
                  <el-tag type="info" size="small" class="step-range-tag">
                    {{ formatStepRange(currentTodoDetail.step_names) }}
                  </el-tag>
                </template>
                <div class="step-popover">
                  <div class="step-popover-title">包含步骤：</div>
                  <div class="step-list">
                    <el-tag
                      v-for="(stepName, index) in currentTodoDetail.step_names"
                      :key="index"
                      size="small"
                      class="step-tag"
                    >
                      {{ stepName }}
                    </el-tag>
                  </div>
                </div>
              </el-popover>
            </div>
          </div>
          <div class="detail-item">
            <span class="detail-label">待办内容：</span>
            <div class="detail-value markdown-content" v-html="renderMarkdown(currentTodoDetail.description)"></div>
          </div>
          <div v-if="currentTodoDetail.is_completed && currentTodoDetail.updated_at" class="detail-item">
            <span class="detail-label">完成时间：</span>
            <span class="detail-value">{{ formatDateTime(currentTodoDetail.updated_at) }}</span>
          </div>
        </div>

        <!-- 完成日志（Markdown渲染） -->
        <div v-if="currentTodoDetail.completion_note" class="detail-section">
          <div class="detail-label">完成日志：</div>
          <div class="detail-value markdown-content completion-note" v-html="renderMarkdown(currentTodoDetail.completion_note)"></div>
        </div>

        <!-- 快照（照片九宫格） -->
        <div v-if="todoDetailPhotos.length > 0" class="detail-section">
          <div class="detail-label">快照</div>
          <div class="photo-grid" :class="`photo-grid-${Math.min(todoDetailPhotos.length, 9)}`">
            <div
              v-for="(photo, index) in todoDetailPhotos"
              :key="index"
              class="photo-item"
              @click="viewPhoto(index)"
            >
              <img :src="getPhotoUrl(photo)" :alt="`照片 ${index + 1}`" @error="handleImageError" />
              <div class="photo-overlay">
                <el-icon><ZoomIn /></el-icon>
              </div>
            </div>
          </div>
        </div>

        <!-- 附件（文件列表） -->
        <div v-if="todoDetailFiles.length > 0" class="detail-section">
          <div class="detail-label">附件</div>
          <div class="file-list">
            <div
              v-for="(file, index) in todoDetailFiles"
              :key="index"
              class="file-item"
              @click="handlePreviewFile(file)"
            >
              <el-icon><Document /></el-icon>
              <span>{{ file.name }}</span>
              <div class="file-actions" @click.stop>
                <el-button
                  type="primary"
                  :icon="View"
                  size="small"
                  text
                  circle
                  @click.stop="handlePreviewFile(file)"
                  title="预览"
                />
                <el-button
                  type="primary"
                  :icon="Download"
                  size="small"
                  text
                  circle
                  @click.stop="downloadFile(file)"
                  title="下载"
                />
              </div>
            </div>
          </div>
        </div>
      </div>
    </el-dialog>

    <!-- 编辑待办弹窗 -->
    <el-dialog
      v-model="showEditTodoDialog"
      title="编辑待办"
      width="600px"
      :close-on-click-modal="false"
    >
      <el-form v-if="editingTodo" :model="editTodoForm" label-width="100px">
        <el-form-item label="待办内容">
          <el-input
            v-model="editTodoForm.description"
            type="textarea"
            :rows="4"
            placeholder="请输入待办内容"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showEditTodoDialog = false">取消</el-button>
        <el-button type="primary" @click="saveEditTodo" :loading="savingEdit">保存</el-button>
      </template>
    </el-dialog>

    <!-- 图片查看器 -->
    <el-image-viewer
      v-if="showPhotoViewer"
      :url-list="photoViewerUrls"
      :initial-index="photoViewerIndex"
      @close="showPhotoViewer = false"
    />

    <!-- 完成待办对话框 -->
    <TodoCompleteDialog
      v-model="showCompleteDialog"
      :todo="currentTodo"
      @confirm="handleCompleteConfirm"
    />

    <!-- 文件预览对话框 -->
    <el-dialog
      v-model="showFilePreviewDialog"
      :title="previewFile?.name || '文件预览'"
      width="80%"
      :close-on-click-modal="false"
      class="file-preview-dialog"
    >
      <div v-if="previewFile" class="preview-container">
        <!-- 图片预览 -->
        <div v-if="isImageFile(previewFile.name)" class="preview-image">
          <img
            v-if="getPreviewUrlSync(previewFile.id)"
            :src="getPreviewUrlSync(previewFile.id)"
            :alt="previewFile.name"
            style="max-width: 100%; max-height: 70vh;"
          />
        </div>
        
        <!-- PDF预览 -->
        <div v-else-if="isPdfFile(previewFile.name)" class="preview-pdf">
          <iframe
            :src="getPreviewUrlSync(previewFile.id)"
            style="width: 100%; height: 70vh; border: none;"
          />
        </div>
        
        <!-- 文本预览 -->
        <div v-else-if="isTextFile(previewFile.name)" class="preview-text">
          <pre class="text-preview">{{ textPreviewContent }}</pre>
        </div>
        
        <!-- Office文档预览 -->
        <div v-else-if="isOfficeFile(previewFile.name)" class="preview-office">
          <div
            v-if="officePreviewType === 'word' || officePreviewType === 'excel'"
            class="office-content"
            v-html="officePreviewContent"
          />
          <div v-else-if="officePreviewType === 'ppt'" class="office-content">
            <p style="text-align: center; padding: 60px 20px; color: #909399;">
              PPT文档预览暂不支持，请下载后使用本地软件打开
            </p>
          </div>
        </div>
        
        <!-- 其他文件类型 -->
        <div v-else class="preview-other">
          <p style="text-align: center; padding: 60px 20px; color: #909399;">
            该文件类型不支持在线预览，请下载后查看
          </p>
        </div>
      </div>
      <template #footer>
        <el-button @click="showFilePreviewDialog = false">关闭</el-button>
        <el-button
          type="primary"
          :icon="Download"
          @click="downloadFile(previewFile!)"
          v-if="previewFile"
        >
          下载
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Plus,
  Check,
  View,
  Clock,
  User,
  FolderOpened,
  ArrowLeft,
  ArrowRight,
  Money,
  Edit,
  Delete,
  Document,
  ZoomIn,
  Download,
  Circle
} from '@element-plus/icons-vue'
import { todoApi, type TodoItem, type TodoCalendarItem } from '@/api/todo'
import { projectApi, type ProjectLog } from '@/api/project'
import { attachmentApi, type Attachment } from '@/api/attachment'
import { attachmentFolderApi } from '@/api/attachmentFolder'
import TodoInput from '@/components/TodoInput.vue'
import TodoCompleteDialog from '@/components/TodoCompleteDialog.vue'
import DateSelector from '@/components/todos/DateSelector.vue'
import TodoList from '@/components/todos/TodoList.vue'
import MarkdownIt from 'markdown-it'
import { ElImageViewer } from 'element-plus'
import request from '@/api/request'

const router = useRouter()
const loading = ref(false)
const todos = ref<TodoItem[]>([])
const calendarData = ref<TodoCalendarItem[]>([])

// 本地日期工具（避免 UTC 偏移导致跨天）
const toLocalDateString = (d: Date = new Date()): string => {
  const y = d.getFullYear()
  const m = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${y}-${m}-${day}`
}
const parseLocalDate = (str: string): Date => {
  const [y, m, d] = str.split('-').map(Number)
  return new Date(y, (m || 1) - 1, d || 1)
}

// 响应式的今天日期，会定期更新（基于本地时区）
const today = ref<string>(toLocalDateString())
// 初始化时确保选中今天
const selectedDate = ref<string>(today.value)
const showTodoInput = ref(false)
const currentYear = ref(new Date().getFullYear())
const currentMonth = ref(new Date().getMonth() + 1)
const todosPageRef = ref<HTMLElement>()
const dateSelectorRef = ref<HTMLElement>()

// 定期更新今天的日期（每分钟检查一次，如果跨天了就更新）
let dateUpdateInterval: number | null = null
const updateToday = () => {
  const now = new Date()
  const todayStr = toLocalDateString(now)
  if (todayStr !== today.value) {
    const oldToday = today.value
    today.value = todayStr
    
    // 如果当前选中的是昨天的日期（或更早），自动切换到今天
    const selectedDateObj = parseLocalDate(selectedDate.value)
    const todayDateObj = parseLocalDate(today.value)
    if (selectedDate.value === oldToday || selectedDateObj < todayDateObj) {
      selectedDate.value = today.value
      // 重新加载今天的待办
      loadTodos(today.value)
    }
    
    // 更新年月（如果跨月了）
    const oldYear = currentYear.value
    const oldMonth = currentMonth.value
    currentYear.value = now.getFullYear()
    currentMonth.value = now.getMonth() + 1
    
    // 如果月份变化了，重新加载日历
    if (oldYear !== currentYear.value || oldMonth !== currentMonth.value) {
      loadCalendar()
    }
  }
}

// 待办详情弹窗
const showDetailDialog = ref(false)
const currentTodoDetail = ref<TodoItem | null>(null)
const todoDetailPhotos = ref<Array<string | number>>([])
const todoDetailFiles = ref<Array<{ id: number; name: string; url: string }>>([])

// 编辑待办弹窗
const showEditTodoDialog = ref(false)
const editingTodo = ref<TodoItem | null>(null)
const editTodoForm = ref({ description: '' })
const savingEdit = ref(false)

// 完成待办对话框
const showCompleteDialog = ref(false)
const currentTodo = ref<TodoItem | null>(null)

// 图片查看器
const showPhotoViewer = ref(false)
const photoViewerUrls = ref<string[]>([])
const photoViewerIndex = ref(0)
const photoUrlCache = ref<Map<string | number, string>>(new Map())

const weekdays = ['日', '一', '二', '三', '四', '五', '六']

// markdown 渲染器
const md = new MarkdownIt({
  breaks: true,
  linkify: true,
})

const renderMarkdown = (text?: string) => {
  if (!text) return ''
  return md.render(text)
}

// 日期列表（最近30天）
const dateList = computed(() => {
  const list = []
  const todayDate = parseLocalDate(today.value)
  
  for (let i = -7; i <= 30; i++) {
    const date = new Date(todayDate)
    date.setDate(date.getDate() + i)
    const dateStr = toLocalDateString(date)
    // 动态判断是否是今天
    const isToday = dateStr === today.value
    
    // 从日历数据中获取待办数量
    const calendarItem = calendarData.value.find(item => item.date === dateStr)
    const todoCount = calendarItem ? calendarItem.todo_count : 0
    const completedCount = calendarItem ? calendarItem.completed_count : 0
    const totalCount = todoCount + completedCount
    
    list.push({
      date: dateStr,
      day: date.getDate(),
      month: date.getMonth() + 1,
      weekday: weekdays[date.getDay()],
      isToday,
      todoCount,
      completedCount,
      totalCount
    })
  }
  
  return list
})

// 选中日期的待办统计
const selectedDateTodos = computed(() => {
  return todos.value.filter(t => !t.is_completed)
})

const selectedDateCompleted = computed(() => {
  return todos.value.filter(t => t.is_completed)
})

const selectedDateTotal = computed(() => {
  return todos.value.length
})

// 日历天数
const calendarDays = computed(() => {
  const year = currentYear.value
  const month = currentMonth.value
  const firstDay = new Date(year, month - 1, 1)
  const lastDay = new Date(year, month, 0)
  const daysInMonth = lastDay.getDate()
  const startWeekday = firstDay.getDay()
  
  const days: Array<{
    day: number
    date: string
    otherMonth: boolean
    isToday: boolean
    todoCount: number
    completedCount: number
    revenue: number
  }> = []
  
  // 上个月的日期
  const prevMonthLastDay = new Date(year, month - 1, 0).getDate()
  for (let i = startWeekday - 1; i >= 0; i--) {
    const date = new Date(year, month - 2, prevMonthLastDay - i)
    const dateStr = date.toISOString().split('T')[0]
    const calendarItem = calendarData.value.find(item => item.date === dateStr)
    days.push({
      day: prevMonthLastDay - i,
      date: dateStr,
      otherMonth: true,
      isToday: false,
      todoCount: calendarItem?.todo_count || 0,
      completedCount: calendarItem?.completed_count || 0,
      revenue: calendarItem?.revenue || 0
    })
  }
  
  // 本月的日期
  const todayDateStr = today.value
  for (let day = 1; day <= daysInMonth; day++) {
    const date = new Date(year, month - 1, day)
    const dateStr = toLocalDateString(date)
    // 动态判断是否是今天
    const isToday = dateStr === todayDateStr
    const calendarItem = calendarData.value.find(item => item.date === dateStr)
    days.push({
      day,
      date: dateStr,
      otherMonth: false,
      isToday,
      todoCount: calendarItem?.todo_count || 0,
      completedCount: calendarItem?.completed_count || 0,
      revenue: calendarItem?.revenue || 0
    })
  }
  
  // 下个月的日期（填满6行）
  const remainingDays = 42 - days.length
  for (let day = 1; day <= remainingDays; day++) {
    const date = new Date(year, month, day)
    const dateStr = date.toISOString().split('T')[0]
    const calendarItem = calendarData.value.find(item => item.date === dateStr)
    days.push({
      day,
      date: dateStr,
      otherMonth: true,
      isToday: false,
      todoCount: calendarItem?.todo_count || 0,
      completedCount: calendarItem?.completed_count || 0,
      revenue: calendarItem?.revenue || 0
    })
  }
  
  return days
})

// 统计信息（基于日历数据，使用target_date）
const todayTodoCount = computed(() => {
  const todayItem = calendarData.value.find(item => item.date === today.value)
  return todayItem ? todayItem.todo_count : 0
})

const weekTodoCount = computed(() => {
  const today = new Date()
  const weekAgo = new Date(today)
  weekAgo.setDate(weekAgo.getDate() - 7)
  let count = 0
  for (let i = 0; i <= 7; i++) {
    const date = new Date(weekAgo)
    date.setDate(date.getDate() + i)
    const dateStr = date.toISOString().split('T')[0]
    const item = calendarData.value.find(item => item.date === dateStr)
    if (item) {
      count += item.todo_count
    }
  }
  return count
})

const monthTodoCount = computed(() => {
  const today = new Date()
  const monthAgo = new Date(today)
  monthAgo.setMonth(monthAgo.getMonth() - 1)
  let count = 0
  const currentDate = new Date(monthAgo)
  while (currentDate <= today) {
    const dateStr = currentDate.toISOString().split('T')[0]
    const item = calendarData.value.find(item => item.date === dateStr)
    if (item) {
      count += item.todo_count
    }
    currentDate.setDate(currentDate.getDate() + 1)
  }
  return count
})

const completionRate = computed(() => {
  if (todos.value.length === 0) return 0
  const completed = todos.value.filter(t => t.is_completed).length
  return Math.round((completed / todos.value.length) * 100)
})

// 选择日期
const selectDate = (date: string) => {
  selectedDate.value = date
  loadTodos(date)
}

// 格式化选中的日期
const formatSelectedDate = (dateStr: string) => {
  const date = new Date(dateStr)
  const month = date.getMonth() + 1
  const day = date.getDate()
  const weekday = weekdays[date.getDay()]
  return `${month}月${day}日 星期${weekday}`
}

// 格式化截止时间
const formatDeadline = (deadline: string) => {
  const date = new Date(deadline)
  const now = new Date()
  const diff = date.getTime() - now.getTime()
  const days = Math.ceil(diff / (1000 * 60 * 60 * 24))
  
  if (days < 0) {
    return `已过期 ${Math.abs(days)} 天`
  } else if (days === 0) {
    return '今天截止'
  } else if (days === 1) {
    return '明天截止'
  } else if (days <= 7) {
    return `${days} 天后截止`
  } else {
    return date.toLocaleString('zh-CN', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }
}

// 判断是否紧急
const isUrgent = (targetDate?: string) => {
  if (!targetDate) return false
  const date = new Date(targetDate)
  const now = new Date()
  const diff = date.getTime() - now.getTime()
  const days = Math.ceil(diff / (1000 * 60 * 60 * 24))
  return days >= 0 && days <= 3
}

// 加载待办列表
const loadTodos = async (date?: string) => {
  loading.value = true
  try {
    const data = await todoApi.getTodos(date || selectedDate.value)
    todos.value = data
  } catch (error) {
    ElMessage.error('加载待办列表失败')
  } finally {
    loading.value = false
  }
}

// 加载日历数据
const loadCalendar = async () => {
  try {
    const data = await todoApi.getCalendar(currentYear.value, currentMonth.value)
    calendarData.value = data
  } catch (error) {
    console.error('加载日历数据失败:', error)
  }
}

// 切换待办完成状态
const toggleTodoComplete = async (todo: TodoItem) => {
  if (todo.is_completed) {
    // 如果已完成，取消完成状态
    try {
      await todoApi.updateTodo(todo.id, {
        is_completed: false
      })
      ElMessage.success('待办已取消完成')
      await loadTodos()
      await loadCalendar()
    } catch (error) {
      ElMessage.error('取消完成失败')
    }
  } else {
    // 如果未完成，显示完成对话框（与Dashboard页面一致）
    currentTodo.value = todo
    showCompleteDialog.value = true
  }
}

// 处理完成确认（与Dashboard页面保持一致）
const handleCompleteConfirm = async (data: { completionNote: string; files: File[]; photos: File[]; fileFolderId?: number; photoFolderId?: number }) => {
  if (!currentTodo.value) return
  
  try {
    // 上传文件（如果有）
    const attachmentIds: number[] = []
    if (data.files.length > 0) {
      const { batchUploadFiles } = await import('@/utils/uploadHelper')
      const fileIds = await batchUploadFiles(currentTodo.value.project_id, data.files, {
        fileType: '其他',
        description: data.completionNote || undefined,
        folderId: data.fileFolderId
      })
      attachmentIds.push(...fileIds)
    }
    
    // 上传照片（如果有，默认上传到快照文件夹）
    if (data.photos && data.photos.length > 0) {
      // 如果没有指定文件夹，尝试获取快照文件夹
      let photoFolderId = data.photoFolderId
      if (!photoFolderId) {
        try {
          const folders = await attachmentFolderApi.list(currentTodo.value.project_id)
          const snapshotFolder = folders.find(f => f.name === '快照')
          if (snapshotFolder) {
            photoFolderId = snapshotFolder.id
          }
        } catch (error) {
          console.error('获取快照文件夹失败:', error)
        }
      }
      
      const { batchUploadFiles } = await import('@/utils/uploadHelper')
      const photoIds = await batchUploadFiles(currentTodo.value.project_id, data.photos, {
        fileType: '其他',
        description: data.completionNote || undefined,
        folderId: photoFolderId
      })
      attachmentIds.push(...photoIds)
    }
    
    // 更新待办状态，所有附件ID（包括文件和照片）都传给后端，后端会自动区分
    await todoApi.updateTodo(currentTodo.value.id, {
      is_completed: true,
      completion_note: data.completionNote || undefined,
      attachment_ids: attachmentIds.length > 0 ? attachmentIds : undefined
    })
    
    ElMessage.success('待办已完成')
    showCompleteDialog.value = false
    currentTodo.value = null
    await loadTodos()
    await loadCalendar()
  } catch (error) {
      ElMessage.error('完成待办失败')
  }
}

// 删除待办
const deleteTodo = async (todo: TodoItem) => {
  try {
    await ElMessageBox.confirm(
      '确定要删除这个待办吗？',
      '确认删除',
      {
        confirmButtonText: '删除',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )
    
    await todoApi.deleteTodo(todo.id)
    ElMessage.success('待办已删除')
    await loadTodos()
    await loadCalendar()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error('删除待办失败')
    }
  }
}

// 格式化步骤范围（与dashboard页面保持一致）
const formatStepRange = (stepNames: string[]): string => {
  if (!stepNames || stepNames.length === 0) return ''
  if (stepNames.length === 1) return stepNames[0]
  return `${stepNames[0]} ~ ${stepNames[stepNames.length - 1]}`
}

// 格式化时间（刚刚、几分钟前等）
const formatTimeAgo = (dateStr: string): string => {
  const date = new Date(dateStr)
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  const seconds = Math.floor(diff / 1000)
  const minutes = Math.floor(seconds / 60)
  const hours = Math.floor(minutes / 60)
  const days = Math.floor(hours / 24)
  
  if (seconds < 60) {
    return '刚刚'
  } else if (minutes < 60) {
    return `${minutes}分钟前`
  } else if (hours < 24) {
    return `${hours}小时前`
  } else if (days < 7) {
    return `${days}天前`
  } else {
    return date.toLocaleDateString('zh-CN', {
      month: 'short',
      day: 'numeric'
    })
  }
}

// 处理待办添加
const handleTodoAdd = async (data: { projectId: number; projectTitle: string; stepIds: number[]; stepNames: string[]; description: string }) => {
  try {
    await todoApi.createTodo({
      project_id: data.projectId,
      description: data.description,
      step_ids: data.stepIds
    })
    ElMessage.success('待办添加成功')
    showTodoInput.value = false
    await loadTodos()
    await loadCalendar()
  } catch (error) {
    ElMessage.error('添加待办失败')
  }
}

// 跳转到项目
const goToProject = (projectId: number) => {
  router.push(`/projects/${projectId}`)
}

// 显示待办详情
const showTodoDetail = async (todo: TodoItem) => {
  currentTodoDetail.value = todo
  todoDetailPhotos.value = []
  todoDetailFiles.value = []
  showDetailDialog.value = true
  
  // 如果待办已完成，从项目日志中获取附件信息
  if (todo.is_completed) {
    try {
      const logs = await projectApi.getLogs(todo.project_id, 100)
      // 查找该待办完成时的日志
      const completionLog = logs.find(log => 
        log.action === 'todo_completed' && 
        log.description.includes(todo.description)
      )
      
      if (completionLog && completionLog.details) {
        const details = typeof completionLog.details === 'string' 
          ? JSON.parse(completionLog.details) 
          : completionLog.details
        
        // 获取照片ID（可能是字符串或数字）
        const photoIds: (string | number)[] = details.photos || []
        const attachmentIds: number[] = details.attachment_ids || []
        
        // 处理照片ID，统一转换为数字或字符串
        const normalizedPhotoIds = photoIds.map((id: string | number) => {
          if (typeof id === 'string') {
            const numId = parseInt(id)
            return numId > 0 ? numId : id
          }
          return id
        }).filter((id: string | number) => {
          if (typeof id === 'number') return id > 0
          return id !== ''
        })
        
        // 照片ID直接存储，不需要先获取附件对象
        todoDetailPhotos.value = normalizedPhotoIds
        
        // 获取文件附件（排除照片ID）
        const fileAttachmentIds = attachmentIds.filter((id: number) => {
          return !normalizedPhotoIds.some((photoId: string | number) => {
            if (typeof photoId === 'number') {
              return photoId === id
            }
            return parseInt(photoId.toString()) === id
              })
        })
        
        // 获取文件附件信息
        if (fileAttachmentIds.length > 0) {
          const fileAttachments = await attachmentApi.batch(fileAttachmentIds)
          todoDetailFiles.value = fileAttachments.map(att => ({
                id: att.id,
                name: att.file_name,
                url: `/api/attachments/${att.id}/download`
          }))
        }
      }
    } catch (error) {
      console.error('加载待办详情失败:', error)
    }
  }
}

// 获取附件ID
const getAttachmentId = (photoPath: string | number): number | null => {
  if (typeof photoPath === 'number') {
    return photoPath
  }
  if (typeof photoPath === 'string') {
    if (photoPath.startsWith('http://') || photoPath.startsWith('https://')) {
      return null // 完整URL，不需要转换
    }
    const id = parseInt(photoPath.split('/').pop()?.replace(/\.[^.]+$/, '') || photoPath) || 0
    return id > 0 ? id : null
  }
  return null
}

// 加载照片URL（异步）
const loadPhotoUrl = async (photoPath: string | number): Promise<string> => {
  // 如果已缓存，直接返回
  if (photoUrlCache.value.has(photoPath)) {
    return photoUrlCache.value.get(photoPath)!
  }
  
  // 如果是完整URL，直接返回
  if (typeof photoPath === 'string' && (photoPath.startsWith('http://') || photoPath.startsWith('https://'))) {
    photoUrlCache.value.set(photoPath, photoPath)
    return photoPath
  }
  
  const attachmentId = getAttachmentId(photoPath)
  if (!attachmentId) return ''
  
  try {
    const blob = await attachmentApi.download(attachmentId)
    const blobUrl = URL.createObjectURL(blob)
    photoUrlCache.value.set(photoPath, blobUrl)
    return blobUrl
  } catch (error) {
    console.error('Failed to load photo:', error)
    return ''
  }
}

// 获取照片URL（同步版本，用于模板）
const getPhotoUrl = (photoPath: string | number): string => {
  // 如果已缓存，直接返回
  if (photoUrlCache.value.has(photoPath)) {
    return photoUrlCache.value.get(photoPath)!
  }
  
  // 如果是完整URL，直接返回
  if (typeof photoPath === 'string' && (photoPath.startsWith('http://') || photoPath.startsWith('https://'))) {
    return photoPath
  }
  
  // 如果未缓存，触发异步加载
  loadPhotoUrl(photoPath).then(url => {
    if (url) {
      // URL加载成功后，触发响应式更新
      photoUrlCache.value.set(photoPath, url)
    }
  })
  
  // 返回空字符串，等待异步加载
  return ''
}

// 查看照片
const viewPhoto = (index: number) => {
  photoViewerUrls.value = todoDetailPhotos.value.map(p => getPhotoUrl(p))
  photoViewerIndex.value = index
  showPhotoViewer.value = true
}

// 预览相关
const showFilePreviewDialog = ref(false)
const previewFile = ref<{ id: number; name: string; url: string } | null>(null)
const previewUrlCache = ref<Record<number, string>>({})
const textPreviewContent = ref('')
const officePreviewContent = ref('')
const officePreviewType = ref<'word' | 'excel' | 'ppt' | null>(null)

// 文件类型判断
const isImageFile = (filename: string): boolean => {
  const ext = filename.toLowerCase().split('.').pop()
  return ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp', 'svg', 'ico'].includes(ext || '')
}

const isPdfFile = (filename: string): boolean => {
  return filename.toLowerCase().endsWith('.pdf')
}

const isTextFile = (filename: string): boolean => {
  const ext = filename.toLowerCase().split('.').pop()
  return ['txt', 'md', 'json', 'xml', 'csv', 'log'].includes(ext || '')
}

const isOfficeFile = (filename: string): boolean => {
  return isWordFile(filename) || isExcelFile(filename) || isPptFile(filename)
}

const isWordFile = (filename: string): boolean => {
  const ext = filename.toLowerCase().split('.').pop()
  return ['doc', 'docx'].includes(ext || '')
}

const isExcelFile = (filename: string): boolean => {
  const ext = filename.toLowerCase().split('.').pop()
  return ['xls', 'xlsx'].includes(ext || '')
}

const isPptFile = (filename: string): boolean => {
  const ext = filename.toLowerCase().split('.').pop()
  return ['ppt', 'pptx'].includes(ext || '')
}

// 获取预览URL
const getPreviewUrl = async (fileId: number): Promise<string> => {
  if (previewUrlCache.value[fileId]) {
    return previewUrlCache.value[fileId]
  }
  
  try {
    const blob = await attachmentApi.preview(fileId)
    const url = URL.createObjectURL(blob)
    previewUrlCache.value[fileId] = url
    return url
  } catch (error) {
    ElMessage.error('加载预览失败')
    return ''
  }
}

const getPreviewUrlSync = (fileId: number): string => {
  return previewUrlCache.value[fileId] || ''
}

// 预览文件
const handlePreviewFile = async (file: { id: number; name: string; url: string }) => {
  previewFile.value = file
  textPreviewContent.value = ''
  officePreviewContent.value = ''
  officePreviewType.value = null
  showFilePreviewDialog.value = true
  
  // 预加载预览URL
  await getPreviewUrl(file.id)
  
  // 如果是文本文件，加载内容
  if (isTextFile(file.name)) {
    try {
      const blob = await attachmentApi.preview(file.id)
      const text = await blob.text()
      textPreviewContent.value = text
    } catch (error) {
      ElMessage.error('加载文件内容失败')
      textPreviewContent.value = '无法加载文件内容'
    }
  } else if (isWordFile(file.name)) {
    try {
      officePreviewType.value = 'word'
      const blob = await attachmentApi.preview(file.id)
      const arrayBuffer = await blob.arrayBuffer()
      const mammoth = (await import('mammoth')).default
      const result = await mammoth.convertToHtml({ arrayBuffer })
      officePreviewContent.value = result.value
    } catch (error) {
      console.error('Word预览错误:', error)
      ElMessage.error('加载Word文档失败')
      officePreviewContent.value = '<p style="color: red; padding: 20px;">无法加载Word文档</p>'
    }
  } else if (isExcelFile(file.name)) {
    try {
      officePreviewType.value = 'excel'
      const blob = await attachmentApi.preview(file.id)
      const arrayBuffer = await blob.arrayBuffer()
      const XLSX = (await import('xlsx')).default
      const workbook = XLSX.read(arrayBuffer, { type: 'array' })
      
      let html = '<div class="excel-preview">'
      workbook.SheetNames.forEach((sheetName, index) => {
        const worksheet = workbook.Sheets[sheetName]
        const htmlTable = XLSX.utils.sheet_to_html(worksheet)
        html += `<div class="excel-sheet"><h3>工作表 ${index + 1}: ${sheetName}</h3>${htmlTable}</div>`
      })
      html += '</div>'
      officePreviewContent.value = html
    } catch (error) {
      console.error('Excel预览错误:', error)
      ElMessage.error('加载Excel文档失败')
      officePreviewContent.value = '<p style="color: red; padding: 20px;">无法加载Excel文档</p>'
    }
  } else if (isPptFile(file.name)) {
    officePreviewType.value = 'ppt'
  }
}

// 下载文件
const downloadFile = async (file: { id: number; name: string; url: string }) => {
  try {
    const blob = await attachmentApi.download(file.id)
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = file.name
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
    ElMessage.success('下载成功')
  } catch (error) {
    ElMessage.error('下载文件失败')
  }
}

// 处理图片加载错误
const handleImageError = (e: Event) => {
  const img = e.target as HTMLImageElement
  img.src = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCIgZmlsbD0iI2Y1ZjdmYSIvPjx0ZXh0IHg9IjUwJSIgeT0iNTAlIiBmb250LWZhbWlseT0iQXJpYWwiIGZvbnQtc2l6ZT0iMTQiIGZpbGw9IiM5MDkzOTkiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGR5PSIuM2VtIj7lm77niYfliqDovb3lpLHotKU8L3RleHQ+PC9zdmc+'
}

// 格式化日期时间
const formatDateTime = (dateStr: string): string => {
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 显示编辑对话框
const showEditDialog = (todo: TodoItem) => {
  editingTodo.value = todo
  editTodoForm.value = { description: todo.description }
  showEditTodoDialog.value = true
}

// 保存编辑
const saveEditTodo = async () => {
  if (!editingTodo.value) return
  
  savingEdit.value = true
  try {
    await todoApi.updateTodo(editingTodo.value.id, {
      description: editTodoForm.value.description
    })
    ElMessage.success('待办已更新')
    showEditTodoDialog.value = false
    await loadTodos()
    await loadCalendar()
  } catch (error) {
    ElMessage.error('更新待办失败')
  } finally {
    savingEdit.value = false
  }
}

// 上一个月
const prevMonth = () => {
  if (currentMonth.value === 1) {
    currentMonth.value = 12
    currentYear.value--
  } else {
    currentMonth.value--
  }
  loadCalendar()
}

// 下一个月
const nextMonth = () => {
  if (currentMonth.value === 12) {
    currentMonth.value = 1
    currentYear.value++
  } else {
    currentMonth.value++
  }
  loadCalendar()
}

// 处理日期选择器滚动
const handleDateScroll = () => {
  // 滚动联动逻辑可以在这里实现
}

// 监听月份变化
watch([currentYear, currentMonth], () => {
  loadCalendar()
})

// 监听选中日期变化，自动滚动到选中项
watch(selectedDate, (newDate) => {
  nextTick(() => {
    if (dateSelectorRef.value) {
      const selectedItem = dateSelectorRef.value.querySelector(`[data-date="${newDate}"]`)
      if (selectedItem) {
        selectedItem.scrollIntoView({ block: 'center', behavior: 'smooth' })
      }
    }
  })
})

onMounted(async () => {
  // 确保选中日期是今天
  selectedDate.value = today.value
  
  // 加载今天的待办和日历数据
  await loadTodos(today.value)
  await loadCalendar()
  
  // 初始滚动到今日
  nextTick(() => {
    if (dateSelectorRef.value) {
      const todayItem = dateSelectorRef.value.querySelector('.date-item-today')
      if (todayItem) {
        todayItem.scrollIntoView({ block: 'center', behavior: 'smooth' })
      }
    }
  })
  
  // 启动日期更新定时器（每分钟检查一次）
  updateToday()
  dateUpdateInterval = setInterval(updateToday, 60000) as unknown as number
})

// 组件卸载时清理定时器
onUnmounted(() => {
  if (dateUpdateInterval) {
    clearInterval(dateUpdateInterval)
  }
})
</script>

<style scoped>
.todos-page {
  padding: 20px;
  height: calc(100vh - 60px);
  max-height: calc(100vh - 60px);
  overflow: hidden;
  display: flex;
  flex-direction: column;
  box-sizing: border-box;
}

.todos-layout {
  flex: 1;
  height: 100%;
  overflow: hidden;
  display: flex;
}

.todos-layout .el-row {
  width: 100%;
  height: 100%;
  max-height: 100%;
  margin: 0 !important;
  flex: 1;
  overflow: hidden;
}

.todos-layout .el-col {
  height: 100%;
  max-height: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  box-sizing: border-box;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
  font-size: 16px;
  color: #111827;
}

.card-header span {
  color: #111827;
}

/* Element Plus 组件样式覆盖 */
.todos-page :deep(.el-card__header) {
  color: #111827;
}

.todos-page :deep(.el-card__header span) {
  color: #111827;
}

.todos-page :deep(.el-button) {
  color: #111827;
}

.todos-page :deep(.el-button.is-plain) {
  color: #111827;
  border-color: #d1d5db;
}

.todos-page :deep(.el-button.is-plain:hover) {
  color: #111827;
  background-color: #f9fafb;
  border-color: #111827;
}

/* 添加待办按钮特殊样式 - 深色背景白色文字 */
.todos-page :deep(.add-todo-btn) {
  color: #ffffff !important;
  background-color: #111827 !important;
  border-color: #111827 !important;
}

.todos-page :deep(.add-todo-btn:hover) {
  color: #ffffff !important;
  background-color: #374151 !important;
  border-color: #374151 !important;
}

.todos-page :deep(.add-todo-btn .el-icon) {
  color: #ffffff !important;
}

.todos-page :deep(.el-button--text) {
  color: #6b7280;
}

.todos-page :deep(.el-button--text:hover) {
  color: #111827;
}

.todos-page :deep(.el-tag) {
  color: #374151;
  background-color: #f3f4f6;
  border-color: #e5e7eb;
}

.todos-page :deep(.el-tag.el-tag--info) {
  color: #374151;
  background-color: #f3f4f6;
  border-color: #e5e7eb;
}

.todos-page :deep(.el-empty__description) {
  color: #6b7280;
}

.header-left {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.header-stats {
  display: flex;
  gap: 8px;
  align-items: center;
}

.stat-badge {
  display: inline-flex;
  align-items: center;
  padding: 2px 8px;
  background: #f3f4f6;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  font-size: 11px;
  color: #1f2937 !important;
  font-weight: 600;
}

/* 日期选择器 */
.date-selector-col {
  height: 100%;
  padding-right: 10px;
}

.date-selector-card {
  height: 100%;
  max-height: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  box-sizing: border-box;
}

.date-selector-card :deep(.el-card__body) {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  padding: 20px;
}

.date-selector {
  overflow-y: auto;
  flex: 1;
  padding: 10px 0;
}

.date-item {
  position: relative;
  padding: 10px 12px;
  margin-bottom: 6px;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
  background: #ffffff;
  border: 1px solid #e5e7eb;
}

.date-item:hover {
  background: #f9fafb;
  border-color: #111827;
}

.date-item-today {
  background: #111827;
  color: #ffffff;
  font-weight: 600;
  border-color: #111827;
}

/* 如果今天被选中，需要特殊处理 - 优先级高于 .date-item-today */
.date-item-today.date-item-selected {
  background: #f9fafb !important;
  border-color: #111827;
  border-width: 2px;
  color: #111827 !important;
}

.date-item-today.date-item-selected .date-weekday {
  color: #6b7280 !important;
}

.date-item-today.date-item-selected .date-day {
  color: #111827 !important;
}

.date-item-today.date-item-selected .date-month {
  color: #6b7280 !important;
  font-weight: 500;
}

.date-item-today.date-item-selected .date-stats {
  border-top-color: #e5e7eb !important;
}

.date-item-today.date-item-selected .stat-label {
  color: #6b7280 !important;
  font-weight: 500;
}

.date-item-today.date-item-selected .stat-value {
  color: #111827 !important;
}

.date-item-selected {
  border-color: #111827;
  background: #f9fafb;
  border-width: 2px;
  color: #111827 !important;
}

.date-item-selected .date-weekday {
  color: #6b7280 !important;
}

.date-item-selected .date-day {
  color: #111827 !important;
}

.date-item-selected .date-month {
  color: #6b7280 !important;
  font-weight: 500;
}

.date-item-selected .stat-label {
  color: #6b7280 !important;
  font-weight: 500;
}

.date-item-selected .stat-value {
  color: #111827 !important;
}

.date-item-has-todos {
  border-left: 2px solid #111827;
}

.date-weekday {
  font-size: 11px;
  color: #6b7280;
  margin-bottom: 4px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.date-item-today .date-weekday {
  color: rgba(255, 255, 255, 0.9);
}

.date-day {
  font-size: 20px;
  font-weight: 600;
  line-height: 1;
  margin-bottom: 2px;
  color: #111827;
}

.date-item-today .date-day {
  color: #ffffff;
}

.date-month {
  font-size: 11px;
  color: #6b7280;
  font-weight: 500;
}

.date-item-today .date-month {
  color: rgba(255, 255, 255, 0.8);
}

.date-stats {
  display: flex;
  flex-direction: column;
  gap: 3px;
  margin-top: 6px;
  padding-top: 6px;
  border-top: 1px solid #e5e7eb;
}

.date-item-today .date-stats {
  border-top-color: rgba(255, 255, 255, 0.2);
}

.date-stat-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 10px;
}

.date-stat-item .stat-label {
  color: #6b7280;
  font-size: 9px;
  text-transform: uppercase;
  letter-spacing: 0.3px;
  font-weight: 500;
}

.date-item-today .date-stat-item .stat-label {
  color: rgba(255, 255, 255, 0.8);
}

.date-stat-item .stat-value {
  font-weight: 600;
  font-size: 11px;
  color: #111827;
}

.date-item-today .date-stat-item .stat-value {
  color: #ffffff;
}

/* 待办详情 */
.todos-detail-col {
  height: 100%;
  display: flex;
  flex-direction: column;
  padding: 0 10px;
}

.todos-detail-card {
  height: 100%;
  max-height: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  box-sizing: border-box;
}

.todos-detail-card :deep(.el-card__body) {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  padding: 16px;
}

.todo-input-wrapper {
  margin-bottom: 16px;
  padding-bottom: 16px;
  border-bottom: 1px solid #ebeef5;
}

.todos-list {
  flex: 1;
  overflow-y: auto;
  padding-right: 8px;
}

.empty-todos {
  padding: 40px 0;
}

.todo-items {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.todo-item {
  position: relative;
  display: flex;
  background: #ffffff;
  border-radius: 4px;
  overflow: hidden;
  transition: all 0.2s;
  border: 1px solid #e5e7eb;
}

.todo-item:hover {
  border-color: #111827;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}

.todo-item-completed {
  opacity: 0.9;
  background: #f3f4f6;
  border-color: #d1d5db;
}

.todo-item-completed .project-name,
.todo-item-completed .todo-description,
.todo-item-completed .todo-time {
  color: #4b5563;
}

.todo-item-completed .todo-status-indicator {
  background: #111827;
}

.todo-item-completed .todo-status-dot {
  background: #111827;
}

/* 完成按钮（圆圈） */
.todo-checkbox {
  flex-shrink: 0;
  padding: 0 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  z-index: 10;
  position: relative;
}

.checkbox-circle {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  border: 2px solid #d1d5db;
  background: #ffffff;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
  position: relative;
  pointer-events: auto;
  flex-shrink: 0;
}

.checkbox-circle:hover {
  border-color: #111827;
  transform: scale(1.1);
  background: #f9fafb;
}

.checkbox-circle.checked {
  background: #111827;
  border-color: #111827;
}

.checkbox-circle.checked:hover {
  background: #374151;
  border-color: #374151;
}

.check-icon {
  color: #ffffff;
  font-size: 12px;
  font-weight: bold;
  pointer-events: none;
}

/* 左侧状态指示器 */
.todo-status-indicator {
  width: 2px;
  background: #e5e7eb;
  flex-shrink: 0;
  transition: background 0.2s;
}

.todo-status-indicator.completed {
  background: #111827;
}

/* 主要内容区域 */
.todo-content {
  flex: 1;
  padding: 10px 12px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.todo-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.todo-header-left {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
  flex: 1;
  min-width: 0;
}

.todo-meta {
  display: flex;
  align-items: center;
  gap: 6px;
  flex: 1;
  min-width: 0;
}

.project-name {
  font-weight: 600;
  font-size: 14px;
  color: #111827;
  letter-spacing: -0.01em;
  line-height: 1.4;
}

.separator {
  color: #9ca3af;
  font-size: 11px;
  flex-shrink: 0;
}

.step-badge {
  display: inline-flex;
  align-items: center;
  padding: 1px 6px;
  background: #f9fafb;
  border: 1px solid #e5e7eb;
  border-radius: 3px;
  font-size: 10px;
  color: #6b7280;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
}

.step-badge:hover {
  background: #f3f4f6;
  border-color: #111827;
  color: #111827;
}

.todo-header-right {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
}

.todo-time {
  font-size: 12px;
  color: #6b7280;
  font-weight: 500;
  white-space: nowrap;
}

.todo-status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #e5e7eb;
  flex-shrink: 0;
  transition: background 0.2s;
}

.todo-status-dot.completed {
  background: #111827;
}

.todo-description-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin: 6px 0;
}

.todo-description {
  font-size: 13px;
  line-height: 1.6;
  color: #111827;
  word-break: break-word;
  font-weight: 400;
  flex: 1;
  min-width: 0;
  transition: all 0.3s ease;
}

.todo-description.completed {
  text-decoration: line-through;
  text-decoration-color: #6b7280;
  text-decoration-thickness: 2px;
  color: #6b7280;
  opacity: 0.8;
}

.todo-description :deep(p),
.note-content :deep(p) {
  margin: 0 0 4px 0;
  line-height: 1.5;
  color: #374151;
}

.todo-description :deep(p:last-child),
.note-content :deep(p:last-child) {
  margin-bottom: 0;
}

.todo-note {
  padding: 6px 10px;
  background: #f9fafb;
  border-left: 2px solid #111827;
  border-radius: 3px;
  margin-top: 2px;
}

.note-content {
  font-size: 11px;
  line-height: 1.4;
  color: #4b5563;
  white-space: pre-wrap;
}

.todo-actions {
  display: flex;
  gap: 4px;
  flex-shrink: 0;
  opacity: 0.7;
  transition: opacity 0.2s;
}

.todo-item:hover .todo-actions {
  opacity: 1;
}

.action-btn {
  padding: 4px 8px;
  color: #4b5563 !important;
  transition: all 0.2s;
  font-size: 12px;
  font-weight: 500;
}

.action-btn:hover {
  color: #111827 !important;
  background: #e5e7eb;
}

.action-btn .el-icon {
  font-size: 14px;
  margin-right: 4px;
  color: inherit;
}

/* 步骤标签样式 */
.step-range-tag {
  cursor: help;
  font-size: 11px;
  padding: 2px 8px;
  color: #1f2937 !important;
  background-color: #e5e7eb !important;
  border-color: #d1d5db !important;
  font-weight: 500;
}

.step-popover {
  padding: 8px 0;
}

.step-popover-title {
  font-size: 12px;
  color: #6b7280;
  margin-bottom: 8px;
  font-weight: 500;
}

.step-list {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.step-tag {
  font-weight: 500;
}

.step-tag {
  font-weight: 500;
}

.step-popover {
  padding: 8px 0;
}

.step-popover-title {
  font-size: 12px;
  color: #6b7280;
  margin-bottom: 8px;
  font-weight: 500;
}

.step-list {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

/* 日历 */
.calendar-col {
  height: 100%;
  padding-left: 10px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.calendar-card {
  flex-shrink: 0;
  height: auto;
  display: flex;
  flex-direction: column;
  overflow: visible;
  box-sizing: border-box;
}

.calendar-card :deep(.el-card__body) {
  display: flex;
  flex-direction: column;
  overflow: visible;
  padding: 20px;
  height: auto;
}

.calendar-nav {
  display: flex;
  align-items: center;
  gap: 8px;
}

.calendar-month {
  font-size: 14px;
  font-weight: 600;
  min-width: 80px;
  text-align: center;
}

.calendar-wrapper {
  overflow: visible;
  padding: 10px 0;
  height: auto;
}

.calendar-weekdays {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 4px;
  margin-bottom: 8px;
}

.weekday {
  text-align: center;
  font-size: 11px;
  font-weight: 600;
  color: #6b7280;
  padding: 4px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.calendar-days {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 4px;
}

.calendar-day {
  aspect-ratio: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
  position: relative;
  padding: 4px;
}

.calendar-day:hover {
  background: #f9fafb;
  border: 1px solid #e5e7eb;
}

.calendar-day-other-month {
  opacity: 0.3;
}

.calendar-day-today {
  background: #111827;
  color: #ffffff;
  font-weight: 600;
}

/* 如果今天被选中，需要特殊处理 - 优先级高于 .calendar-day-today */
.calendar-day-today.calendar-day-selected {
  background: #f9fafb !important;
  border: 2px solid #111827;
  color: #111827 !important;
}

.calendar-day-today.calendar-day-selected .day-number {
  color: #111827 !important;
}

.calendar-day-selected {
  background: #f9fafb;
  border: 2px solid #111827;
  color: #111827 !important;
}

.calendar-day-selected .day-number {
  color: #111827 !important;
}

.calendar-day-has-todos {
  border-left: 2px solid #111827;
}

.calendar-day-has-completed {
  border-right: 2px solid #111827;
}

.day-number {
  font-size: 14px;
  line-height: 1;
  color: #111827;
}

.calendar-day-today .day-number {
  color: #ffffff !important;
}

.day-indicators {
  position: absolute;
  bottom: 2px;
  left: 0;
  right: 0;
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: center;
  gap: 4px;
  font-size: 9px;
}

.day-stats {
  display: flex;
  flex-direction: row;
  gap: 2px;
  align-items: center;
}

.day-revenue {
  color: #111827;
  font-size: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-top: 2px;
}

.day-revenue .el-icon {
  font-size: 12px;
}

.indicator-todo {
  background: #111827;
  color: #ffffff;
  border-radius: 2px;
  padding: 0 2px;
  min-width: 12px;
  text-align: center;
  font-size: 9px;
}

.indicator-completed {
  background: #6b7280;
  color: #ffffff;
  border-radius: 2px;
  padding: 0 2px;
  min-width: 12px;
  text-align: center;
  font-size: 9px;
}

/* 统计信息 */
.stats-card {
  flex-shrink: 0;
  box-sizing: border-box;
  overflow: visible;
}

.stats-card :deep(.el-card__body) {
  padding: 20px;
  overflow: visible;
  height: auto;
}

.stats-content {
  display: grid;
  grid-template-columns: 1fr 1fr;
  grid-template-rows: 1fr 1fr;
  gap: 12px;
}

.stat-item {
  padding: 10px;
  background: #ffffff;
  border: 1px solid #e5e7eb;
  border-radius: 4px;
  text-align: center;
}

.stat-label {
  font-size: 11px;
  color: #6b7280;
  margin-bottom: 6px;
  text-transform: uppercase;
  letter-spacing: 0.3px;
}

.stat-value {
  font-size: 20px;
  font-weight: 600;
  color: #111827;
}

/* 移动端适配 */
@media (max-width: 768px) {
  .todos-page {
    padding: 12px;
    height: auto;
    min-height: calc(100vh - 60px);
    max-height: none;
    overflow-y: auto;
    overflow-x: hidden;
  }

  .todos-layout {
    flex-direction: column;
    height: auto;
    max-height: none;
    overflow: visible;
  }

  .todos-layout .el-row {
    height: auto;
    max-height: none;
    overflow: visible;
    flex-direction: column;
  }

  .todos-layout .el-col {
    height: auto;
    max-height: none;
    width: 100% !important;
    flex: 0 0 auto !important;
    padding: 0 !important;
    margin-bottom: 12px;
    overflow: visible;
  }

  .date-selector-col,
  .todos-detail-col,
  .calendar-col {
    padding: 0 !important;
  }

  .date-selector-card,
  .calendar-card,
  .stats-card {
    position: static;
    height: auto;
    margin-bottom: 12px;
  }

  .date-selector-card :deep(.el-card__body),
  .todos-detail-card :deep(.el-card__body) {
    padding: 12px !important;
  }

  .date-selector {
    display: flex;
    overflow-x: auto;
    gap: 8px;
    padding: 8px 0;
    -webkit-overflow-scrolling: touch;
  }

  .date-item {
    min-width: 70px;
    margin-bottom: 0;
    flex-shrink: 0;
  }

  .date-day {
    font-size: 16px;
  }

  .calendar-card {
    order: 3;
  }

  .calendar-wrapper {
    padding: 8px 0;
  }

  .calendar-weekdays {
    gap: 2px;
  }

  .weekday {
    font-size: 10px;
    padding: 2px;
  }

  .calendar-days {
    gap: 2px;
  }

  .calendar-day {
    padding: 2px;
    min-height: 32px;
  }

  .day-number {
    font-size: 11px;
  }

  .day-indicators {
    font-size: 8px;
  }

  .indicator-todo,
  .indicator-completed {
    font-size: 8px;
    min-width: 10px;
    padding: 0 1px;
  }

  .stats-card {
    order: 4;
  }

  .stats-content {
    grid-template-columns: repeat(2, 1fr);
    gap: 8px;
  }

  .stat-item {
    padding: 8px;
  }

  .stat-label {
    font-size: 10px;
  }

  .stat-value {
    font-size: 16px;
  }

  .todos-detail-col {
    order: 1;
  }

  .todos-detail-card {
    min-height: 300px;
  }

  .todo-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 6px;
  }

  .todo-header-left {
    width: 100%;
  }

  .todo-meta {
    flex-wrap: wrap;
  }

  .project-name {
    font-size: 13px;
  }

  .step-badge {
    font-size: 9px;
  }

  .todo-description-row {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }

  .todo-description {
    font-size: 12px;
  }

  .todo-actions {
    opacity: 1;
    width: 100%;
    justify-content: flex-end;
    margin-top: 8px;
    padding-top: 8px;
    border-top: 1px solid #e5e7eb;
  }

  .action-btn {
    padding: 6px 12px;
  }

  /* 对话框样式 */
  .todo-detail-dialog :deep(.el-dialog) {
    width: 96% !important;
    margin-top: 2vh !important;
  }

  .todo-detail-dialog :deep(.el-dialog__body) {
    padding: 12px !important;
    max-height: 70vh;
  }

  .detail-item {
    flex-direction: column;
    gap: 4px;
  }

  .detail-label {
    min-width: auto;
    font-size: 12px;
  }

  .detail-value {
    font-size: 13px;
  }

  .photo-grid-3,
  .photo-grid-4,
  .photo-grid-5,
  .photo-grid-6,
  .photo-grid-7,
  .photo-grid-8,
  .photo-grid-9 {
    grid-template-columns: repeat(3, 1fr);
    max-width: 100%;
  }

  .file-item {
    padding: 10px 12px;
  }

  .file-item span {
    font-size: 12px;
  }
}

@media (max-width: 480px) {
  .todos-page {
    padding: 8px;
  }

  .date-item {
    min-width: 60px;
    padding: 8px 10px;
  }

  .date-day {
    font-size: 14px;
  }

  .calendar-day {
    min-height: 28px;
  }

  .day-number {
    font-size: 10px;
  }

  .stat-item {
    padding: 6px;
  }

  .stat-value {
    font-size: 14px;
  }

  .project-name {
    font-size: 12px;
  }

  .todo-description {
    font-size: 11px;
  }
}

/* 待办详情弹窗样式 */
.todo-detail-dialog :deep(.el-dialog__body) {
  padding: 24px;
  max-height: 70vh;
  overflow-y: auto;
}

.todo-detail-content {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.detail-section {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.detail-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
}

.detail-label {
  font-size: 14px;
  font-weight: 600;
  color: #111827 !important;
  min-width: 100px;
  flex-shrink: 0;
}

.detail-value {
  font-size: 14px;
  color: #374151 !important;
  flex: 1;
  word-break: break-word;
}

/* Markdown 内容样式 */
.markdown-content {
  font-size: 14px;
  line-height: 1.7;
  color: #111827 !important;
}

.markdown-content :deep(h1) {
  font-size: 24px;
  font-weight: 700;
  margin: 20px 0 12px 0;
  color: #111827;
  border-bottom: 2px solid #e5e7eb;
  padding-bottom: 8px;
}

.markdown-content :deep(h2) {
  font-size: 20px;
  font-weight: 600;
  margin: 18px 0 10px 0;
  color: #111827;
}

.markdown-content :deep(h3) {
  font-size: 18px;
  font-weight: 600;
  margin: 16px 0 8px 0;
  color: #111827;
}

.markdown-content :deep(h4) {
  font-size: 16px;
  font-weight: 600;
  margin: 14px 0 6px 0;
  color: #111827;
}

.markdown-content :deep(p) {
  margin: 8px 0;
  line-height: 1.7;
  color: #374151;
}

.markdown-content :deep(strong) {
  font-weight: 600;
  color: #111827;
}

.markdown-content :deep(em) {
  font-style: italic;
  color: #374151;
}

.markdown-content :deep(code) {
  background: #f3f4f6;
  padding: 2px 6px;
  border-radius: 4px;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', 'Consolas', 'source-code-pro', monospace;
  font-size: 13px;
  color: #111827;
  border: 1px solid #e5e7eb;
}

.markdown-content :deep(pre) {
  background: #f9fafb;
  padding: 16px;
  border-radius: 6px;
  overflow-x: auto;
  margin: 12px 0;
  border: 1px solid #e5e7eb;
}

.markdown-content :deep(pre code) {
  background: transparent;
  padding: 0;
  border: none;
  font-size: 13px;
}

.markdown-content :deep(ul),
.markdown-content :deep(ol) {
  margin: 12px 0;
  padding-left: 24px;
}

.markdown-content :deep(li) {
  margin: 6px 0;
  line-height: 1.7;
  color: #374151;
}

.markdown-content :deep(a) {
  color: #111827;
  text-decoration: underline;
  transition: color 0.2s;
}

.markdown-content :deep(a:hover) {
  color: #6b7280;
}

.markdown-content :deep(blockquote) {
  border-left: 4px solid #e5e7eb;
  padding-left: 16px;
  margin: 12px 0;
  color: #6b7280;
  font-style: italic;
}

.markdown-content :deep(hr) {
  border: none;
  border-top: 1px solid #e5e7eb;
  margin: 20px 0;
}

.markdown-content :deep(table) {
  width: 100%;
  border-collapse: collapse;
  margin: 12px 0;
}

.markdown-content :deep(th),
.markdown-content :deep(td) {
  border: 1px solid #e5e7eb;
  padding: 8px 12px;
  text-align: left;
}

.markdown-content :deep(th) {
  background: #f9fafb;
  font-weight: 600;
  color: #111827;
}

.completion-note {
  padding: 16px;
  background: #f9fafb;
  border-radius: 8px;
  border-left: 4px solid #111827;
}

/* 照片九宫格样式（与项目详情页面保持一致） */
.photo-grid {
  display: grid;
  gap: 6px;
  margin-top: 8px;
  margin-bottom: 8px;
  max-width: 100%;
}

.photo-grid-1 {
  grid-template-columns: 1fr;
  max-width: 200px;
}

.photo-grid-2 {
  grid-template-columns: repeat(2, 1fr);
  max-width: 400px;
}

.photo-grid-3,
.photo-grid-4,
.photo-grid-5,
.photo-grid-6,
.photo-grid-7,
.photo-grid-8,
.photo-grid-9 {
  grid-template-columns: repeat(3, 1fr);
  max-width: 600px;
}

.photo-item {
  position: relative;
  width: 100%;
  aspect-ratio: 1;
  background: #f5f7fa;
  border-radius: 4px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s;
  border: 1px solid #e5e7eb;
}

.photo-item:hover {
  transform: scale(1.02);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.photo-item img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.photo-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s;
  opacity: 0;
}

.photo-item:hover .photo-overlay {
  background: rgba(0, 0, 0, 0.4);
  opacity: 1;
}

.photo-overlay .el-icon {
  color: #fff;
  font-size: 24px;
}

/* 文件列表 */
.file-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-top: 8px;
}

.file-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  background: #f9fafb;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.file-item:hover {
  background: #f3f4f6;
  border-color: #111827;
}

.file-item .el-icon {
  font-size: 20px;
  color: #6b7280;
  flex-shrink: 0;
}

.file-item span {
  flex: 1;
  font-size: 14px;
  color: #111827;
  word-break: break-all;
}

.download-icon {
  font-size: 16px;
  color: #9ca3af;
  transition: color 0.2s;
}

.file-item:hover .download-icon {
  color: #111827;
}

.file-actions {
  display: flex;
  gap: 4px;
  opacity: 0;
  transition: opacity 0.2s;
}

.file-item:hover .file-actions {
  opacity: 1;
}

.preview-container {
  max-height: 70vh;
  overflow: auto;
}

.preview-image {
  text-align: center;
  padding: 20px;
}

.preview-pdf {
  width: 100%;
  height: 70vh;
}

.preview-text {
  padding: 20px;
}

.text-preview {
  padding: 16px;
  background: #f5f7fa;
  border-radius: 4px;
  white-space: pre-wrap;
  word-wrap: break-word;
  font-family: 'Courier New', monospace;
  font-size: 14px;
  line-height: 1.6;
  max-height: 60vh;
  overflow: auto;
}

.preview-office {
  padding: 20px;
}

.office-content {
  padding: 20px;
  background: #fff;
  border-radius: 4px;
}

.excel-preview {
  overflow-x: auto;
}

.excel-sheet {
  margin-bottom: 30px;
}

.excel-sheet h3 {
  margin-bottom: 12px;
  color: #303133;
}
</style>


