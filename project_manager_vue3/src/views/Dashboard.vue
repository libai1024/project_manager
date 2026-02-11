<template>
  <div class="dashboard">
    <!-- 统计卡片 -->
    <el-row :gutter="16" class="stats-row">
      <el-col :xs="12" :sm="6" :md="6">
        <div class="stat-card revenue-card">
            <div class="stat-icon revenue-icon">
            <el-icon :size="24"><Money /></el-icon>
            </div>
          <div class="stat-content">
            <div class="stat-value">¥{{ formatMoney(stats.total_revenue) }}</div>
            <div class="stat-label">总收益</div>
          </div>
        </div>
      </el-col>
      <el-col :xs="12" :sm="6" :md="6">
        <div class="stat-card project-card">
            <div class="stat-icon project-icon">
            <el-icon :size="24"><FolderOpened /></el-icon>
            </div>
          <div class="stat-content">
            <div class="stat-value">{{ stats.pending_projects_count }}</div>
            <div class="stat-label">待处理项目</div>
          </div>
        </div>
      </el-col>
      <el-col :xs="12" :sm="6" :md="6">
        <div class="stat-card step-card">
            <div class="stat-icon step-icon">
            <el-icon :size="24"><Clock /></el-icon>
            </div>
          <div class="stat-content">
            <div class="stat-value">{{ stats.in_progress_steps_count }}</div>
            <div class="stat-label">进行中步骤</div>
          </div>
        </div>
      </el-col>
      <el-col :xs="12" :sm="6" :md="6">
        <div class="stat-card todo-card">
            <div class="stat-icon todo-icon">
            <el-icon :size="24"><List /></el-icon>
            </div>
          <div class="stat-content">
            <div class="stat-value">{{ stats.today_todos.length }}</div>
            <div class="stat-label">今日待办</div>
          </div>
        </div>
      </el-col>
    </el-row>

    <el-row :gutter="16" class="content-row">
      <!-- 今日待办 -->
      <el-col :xs="24" :md="16">
        <el-card class="todo-card-content">
          <template #header>
            <div class="card-header">
              <span>
                <el-icon><List /></el-icon>
                今日待办
              </span>
              <el-button
                type="text"
                size="small"
                @click="loadStats"
                :loading="loading"
              >
                <el-icon><Refresh /></el-icon>
              </el-button>
            </div>
          </template>
          
          <!-- 待办输入组件 -->
          <div class="todo-input-section">
            <TodoInput @add="handleTodoAdd" />
          </div>
          
          <div v-if="stats.today_todos.length === 0" class="empty-todos">
            <el-empty description="暂无待办" :image-size="60" />
          </div>
          
          <div v-else class="table-wrapper">
            <el-table
              :data="stats.today_todos"
              style="width: 100%"
              :max-height="tableMaxHeight"
              @row-click="handleRowClick"
              class="todo-table"
              size="small"
            >
              <el-table-column label="待办内容" min-width="200">
                <template #default="{ row }">
                  <div class="todo-content-cell">
                    <div class="todo-project-header">
                      <el-icon class="project-icon" :size="14"><FolderOpened /></el-icon>
                      <span class="project-title">{{ row.project_title }}</span>
                      <el-popover
                        placement="top"
                        :width="250"
                        trigger="hover"
                      >
                        <template #reference>
                          <el-tag type="info" size="small" class="step-range-tag">
                            {{ formatStepRange(row.step_names) }}
                          </el-tag>
                        </template>
                        <div class="step-popover">
                          <div class="step-popover-title">包含步骤：</div>
                          <div class="step-list">
                            <el-tag
                              v-for="(stepName, index) in row.step_names"
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
                    <div class="todo-description" :class="{ 'completed': row.is_completed }">
                      {{ row.description }}
                    </div>
                  </div>
                </template>
              </el-table-column>
              <el-table-column prop="student_name" label="学生" min-width="80" />
              <el-table-column label="状态" min-width="70" align="center">
                <template #default="{ row }">
                  <el-tag :type="row.is_completed ? 'success' : 'warning'" size="small">
                    {{ row.is_completed ? '已完成' : '待完成' }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column label="操作" min-width="150" fixed="right" align="center">
                <template #default="{ row }">
                  <div class="action-buttons">
                  <el-button
                    v-if="!row.is_completed"
                    type="success"
                    size="small"
                      :icon="Check"
                      circle
                      @click.stop="openCompleteDialog(row)"
                      title="完成"
                    />
                  <el-button
                    type="primary"
                    size="small"
                      :icon="View"
                      circle
                    @click.stop="goToProject(row.project_id)"
                      title="查看"
                    />
                  <el-button
                    type="danger"
                    size="small"
                      :icon="Delete"
                      circle
                    @click.stop="deleteTodo(row)"
                      title="删除"
                    />
                  </div>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </el-card>
      </el-col>

      <!-- 平台收益统计 -->
      <el-col :xs="24" :md="8">
        <el-card class="revenue-card-content">
          <template #header>
            <div class="card-header">
              <span>
                <el-icon><PieChart /></el-icon>
                平台收益
              </span>
            </div>
          </template>
          
          <div v-if="Object.keys(stats.platform_revenue).length === 0" class="empty-data">
            <el-empty description="暂无数据" :image-size="60" />
          </div>
          
          <div v-else class="revenue-content">
            <!-- ECharts 饼图 -->
            <div ref="chartRef" class="chart-container"></div>
            
            <!-- 收益列表 -->
            <div class="revenue-list">
              <div
                v-for="(revenue, platform) in stats.platform_revenue"
                :key="platform"
                class="revenue-item"
                @click="filterByPlatform(platform)"
              >
                <div class="platform-info">
                  <div class="platform-name">{{ platform }}</div>
                  <div class="platform-revenue">¥{{ formatMoney(revenue) }}</div>
                </div>
                <div class="platform-percentage">
                  {{ getPlatformPercentage(platform) }}%
                </div>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 完成待办对话框 -->
    <TodoCompleteDialog
      v-model="showCompleteDialog"
      :todo="currentTodo"
      @confirm="handleCompleteConfirm"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch, nextTick, computed } from 'vue'
import { useRouter } from 'vue-router'
import {
  Money,
  FolderOpened,
  Clock,
  List,
  Refresh,
  View,
  PieChart,
  Check,
  Delete
} from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import { useDashboard } from '@/composables/useDashboard'
import TodoInput from '@/components/TodoInput.vue'
import TodoCompleteDialog from '@/components/TodoCompleteDialog.vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { todoApi } from '@/api/todo'
import type { TodoItem } from '@/api/todo'

const router = useRouter()
const chartRef = ref<HTMLDivElement>()
let chartInstance: echarts.ECharts | null = null

// 使用Composable
const { loading, stats, loadStats } = useDashboard()

// 完成待办对话框
const showCompleteDialog = ref(false)
const currentTodo = ref<TodoItem | null>(null)

// 计算表格最大高度（确保一屏显示）
const tableMaxHeight = computed(() => {
  // 视口高度 - 头部(60px) - 统计卡片(112px) - 卡片头部(48px) - 输入框(70px) - padding(32px) - 边距(32px)
  const calculated = window.innerHeight - 352
  return calculated > 200 ? calculated : 200
})

// 格式化金额
const formatMoney = (amount: number): string => {
  if (amount >= 10000) {
    return (amount / 10000).toFixed(1) + '万'
  }
  return amount.toFixed(0)
}

// 初始化 ECharts 图表
const initChart = () => {
  if (!chartRef.value) return
  
  chartInstance = echarts.init(chartRef.value)
  window.addEventListener('resize', handleResize)
}

// 更新图表
const updateChart = () => {
  if (!chartInstance || Object.keys(stats.value.platform_revenue).length === 0) {
    return
  }
  
  const platformData = Object.entries(stats.value.platform_revenue).map(([name, value]) => ({
    name,
    value: value.toFixed(2)
  }))
  
  const option = {
    tooltip: {
      trigger: 'item',
      formatter: '{a} <br/>{b}: ¥{c} ({d}%)'
    },
    legend: {
      show: false
    },
    series: [
      {
        name: '平台收益',
        type: 'pie',
        radius: ['50%', '80%'],
        center: ['50%', '50%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 8,
          borderColor: '#fff',
          borderWidth: 2
        },
        label: {
          show: true,
          formatter: '{b}\n{d}%',
          fontSize: 11,
          fontWeight: 'bold'
        },
        labelLine: {
          show: true,
          length: 10,
          length2: 5
        },
        emphasis: {
          label: {
            show: true,
            fontSize: 12,
            fontWeight: 'bold'
          }
        },
        data: platformData,
        color: [
          '#5470c6',
          '#91cc75',
          '#fac858',
          '#ee6666',
          '#73c0de',
          '#3ba272',
          '#fc8452',
          '#9a60b4',
          '#ea7ccc'
        ]
      }
    ]
  }
  
  chartInstance.setOption(option)
}

// 处理窗口大小变化
const handleResize = () => {
  if (chartInstance) {
    chartInstance.resize()
  }
}

// 获取平台收益百分比
const getPlatformPercentage = (platform: string): string => {
  if (stats.value.total_revenue === 0) return '0'
  const revenue = stats.value.platform_revenue[platform] || 0
  return ((revenue / stats.value.total_revenue) * 100).toFixed(1)
}

// 格式化截止时间
const formatDeadline = (deadline: string): string => {
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

// 判断截止时间是否紧急（3天内）
const isDeadlineUrgent = (deadline: string): boolean => {
  const date = new Date(deadline)
  const now = new Date()
  const diff = date.getTime() - now.getTime()
  const days = Math.ceil(diff / (1000 * 60 * 60 * 24))
  return days >= 0 && days <= 3
}

const getStatusType = (status: string) => {
  const statusMap: Record<string, string> = {
    '待开始': 'info',
    '进行中': 'warning',
    '已完成': 'success',
  }
  return statusMap[status] || 'info'
}

const handleRowClick = (row: any) => {
  goToProject(row.project_id)
}

const goToProject = (projectId: number) => {
  router.push(`/projects/${projectId}`)
}

const filterByPlatform = (platform: string) => {
  router.push({
    path: '/projects',
    query: { platform: platform }
  })
}

// 格式化步骤范围
const formatStepRange = (stepNames: string[]): string => {
  if (stepNames.length === 0) return ''
  if (stepNames.length === 1) return stepNames[0]
  return `${stepNames[0]} ~ ${stepNames[stepNames.length - 1]}`
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
    await loadStats()
  } catch (error) {
    ElMessage.error('添加待办失败')
  }
}

// 显示完成对话框
const openCompleteDialog = (todo: TodoItem) => {
  currentTodo.value = todo
  showCompleteDialog.value = true
}

// 处理完成确认
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
        const { attachmentFolderApi } = await import('@/api/attachmentFolder')
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
    
    await todoApi.updateTodo(currentTodo.value.id, {
      is_completed: true,
      completion_note: data.completionNote || undefined,
      attachment_ids: attachmentIds.length > 0 ? attachmentIds : undefined
    })
    
    ElMessage.success('待办已完成')
    showCompleteDialog.value = false
    currentTodo.value = null
    await loadStats()
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
    await loadStats()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error('删除待办失败')
    }
  }
}

// 监听 platform_revenue 变化，更新图表
watch(
  () => stats.value.platform_revenue,
  () => {
    updateChart()
  },
  { deep: true }
)

let refreshInterval: number | null = null

onMounted(async () => {
  await loadStats()
  await nextTick()
  initChart()
  updateChart()
  // 每30秒刷新一次
  refreshInterval = setInterval(loadStats, 30000) as unknown as number
})

onUnmounted(() => {
  if (refreshInterval) {
    clearInterval(refreshInterval)
  }
  window.removeEventListener('resize', handleResize)
  if (chartInstance) {
    chartInstance.dispose()
  }
})
</script>

<style scoped>
.dashboard {
  padding: 16px;
  background: #f5f7fa;
  height: calc(100vh - 60px);
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.stats-row {
  flex-shrink: 0;
  margin-bottom: 16px;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  transition: all 0.3s;
  height: 80px;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12);
}

.stat-icon {
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 10px;
  flex-shrink: 0;
  transition: all 0.3s;
}

.stat-content {
  flex: 1;
  min-width: 0;
}

.stat-value {
  font-size: 20px;
  font-weight: 700;
  color: #303133;
  line-height: 1.2;
  margin-bottom: 4px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.stat-label {
  font-size: 12px;
  color: #909399;
  font-weight: 500;
}

.revenue-card .stat-icon {
  background: linear-gradient(135deg, #67c23a 0%, #85ce61 100%);
  color: #fff;
}

.revenue-card .stat-value {
  color: #67c23a;
}

.project-card .stat-icon {
  background: linear-gradient(135deg, #409eff 0%, #66b1ff 100%);
  color: #fff;
}

.step-card .stat-icon {
  background: linear-gradient(135deg, #e6a23c 0%, #f0c78a 100%);
  color: #fff;
}

.todo-card .stat-icon {
  background: linear-gradient(135deg, #f56c6c 0%, #f78989 100%);
  color: #fff;
}

.content-row {
  flex: 1;
  min-height: 0;
  display: flex;
}

.todo-card-content,
.revenue-card-content {
  height: 100%;
  display: flex;
  flex-direction: column;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.todo-card-content :deep(.el-card__body),
.revenue-card-content :deep(.el-card__body) {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;
  padding: 16px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
  font-size: 14px;
  padding: 0;
}

.card-header span {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #303133;
}

.card-header .el-icon {
  font-size: 16px;
  color: #409eff;
}

.card-header .el-button {
  padding: 4px;
}

.todo-input-section {
  flex-shrink: 0;
  margin-bottom: 12px;
  padding-bottom: 12px;
  border-bottom: 1px solid #ebeef5;
}

.empty-todos {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px 0;
}

.table-wrapper {
  flex: 1;
  min-height: 0;
  overflow: hidden;
}

.todo-table {
  cursor: pointer;
  height: 100%;
}

.todo-content-cell {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.todo-project-header {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-wrap: wrap;
}

.todo-content-cell .project-icon {
  color: #409eff;
  flex-shrink: 0;
}

.project-title {
  font-weight: 600;
  font-size: 13px;
  color: #303133;
  line-height: 1.3;
}

.step-range-tag {
  cursor: help;
  font-size: 11px;
  padding: 2px 6px;
}

.todo-description {
  color: #606266;
  font-size: 12px;
  line-height: 1.5;
  margin-top: 2px;
  padding-left: 20px;
  position: relative;
  transition: all 0.3s ease;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.todo-description::before {
  content: '•';
  position: absolute;
  left: 8px;
  color: #909399;
  font-size: 14px;
}

.todo-description.completed {
  text-decoration: line-through;
  text-decoration-color: #909399;
  text-decoration-thickness: 1px;
  color: #909399;
  opacity: 0.7;
}

.todo-description.completed::before {
  color: #67c23a;
  content: '✓';
  font-weight: bold;
}

.todo-completion-note {
  margin-top: 10px;
  padding: 10px 14px;
  background: #f0f9ff;
  border-left: 3px solid #67c23a;
  border-radius: 6px;
  font-size: 13px;
  color: #606266;
  display: flex;
  align-items: flex-start;
  gap: 8px;
  line-height: 1.6;
}

.todo-completion-note .el-icon {
  color: #67c23a;
  font-size: 16px;
  flex-shrink: 0;
  margin-top: 2px;
}

.step-popover {
  padding: 8px 0;
}

.step-popover-title {
  font-size: 12px;
  color: #909399;
  margin-bottom: 8px;
  font-weight: 600;
}

.step-list {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.todo-table :deep(.el-table__row) {
  transition: background-color 0.2s;
}

.todo-table :deep(.el-table__row:hover) {
  background-color: #f5f7fa;
}

.action-buttons {
  display: flex;
  gap: 4px;
  justify-content: center;
}

.action-buttons .el-button {
  padding: 6px;
}

.project-title-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}

.project-title-cell .project-icon {
  color: #409eff;
  font-size: 18px;
  flex-shrink: 0;
}

.deadline-cell {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 13px;
}

.deadline-urgent {
  color: #f56c6c;
  font-weight: 600;
}

.no-deadline {
  color: #c0c4cc;
}

.revenue-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;
}

.chart-container {
  width: 100%;
  height: 180px;
  flex-shrink: 0;
  margin-bottom: 12px;
  border-radius: 8px;
  overflow: hidden;
}

.empty-data {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #909399;
}

.revenue-list {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  padding: 0;
}

.revenue-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 12px;
  margin-bottom: 6px;
  background-color: #f5f7fa;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
  border: 1px solid transparent;
}

.revenue-item:hover {
  background-color: #fff;
  border-color: #e4e7ed;
  transform: translateX(3px);
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.08);
}

.platform-info {
  flex: 1;
  min-width: 0;
}

.platform-name {
  font-size: 12px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 4px;
  word-break: break-all;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.platform-revenue {
  font-size: 14px;
  font-weight: 700;
  color: #67c23a;
}

.platform-percentage {
  font-size: 16px;
  font-weight: 700;
  color: #409eff;
  margin-left: 8px;
  white-space: nowrap;
  flex-shrink: 0;
}

/* 移动端样式 */
@media (max-width: 768px) {
  .dashboard {
    padding: 12px;
  }

  .stat-card {
    padding: 12px;
    height: 70px;
  }

  .stat-icon {
    width: 40px;
    height: 40px;
  }

  .stat-value {
    font-size: 18px;
  }

  .stat-label {
    font-size: 11px;
  }

  .chart-container {
    height: 150px;
  }

  .revenue-item {
    padding: 8px 10px;
  }

  .platform-name {
    font-size: 11px;
  }

  .platform-revenue {
    font-size: 12px;
  }

  .platform-percentage {
    font-size: 14px;
  }
}
</style>
