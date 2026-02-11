<template>
  <div class="finance-page">
    <!-- 总览统计卡片 -->
    <el-row :gutter="20" class="stats-row">
      <el-col :xs="24" :sm="12" :md="6">
        <div class="stat-card total-revenue">
          <div class="stat-icon">
            <el-icon :size="32"><Money /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-label">总收入</div>
            <div class="stat-value">¥{{ formatMoney(totalRevenue) }}</div>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <div class="stat-card paid-projects">
          <div class="stat-icon">
            <el-icon :size="32"><Check /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-label">已结账项目</div>
            <div class="stat-value">{{ paidProjectsCount }}</div>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <div class="stat-card pending-revenue">
          <div class="stat-icon">
            <el-icon :size="32"><Clock /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-label">待结账金额</div>
            <div class="stat-value">¥{{ formatMoney(pendingRevenue) }}</div>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <div class="stat-card avg-revenue">
          <div class="stat-icon">
            <el-icon :size="32"><TrendCharts /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-label">平均项目收入</div>
            <div class="stat-value">¥{{ formatMoney(avgRevenue) }}</div>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- 时间筛选和视图切换 -->
    <div class="filter-section">
      <div class="filter-left">
        <el-radio-group v-model="timeRange" size="small" @change="handleTimeRangeChange">
          <el-radio-button label="all">全部</el-radio-button>
          <el-radio-button label="year">本年</el-radio-button>
          <el-radio-button label="month">本月</el-radio-button>
          <el-radio-button label="week">本周</el-radio-button>
        </el-radio-group>
        
        <el-date-picker
          v-model="customDateRange"
          type="daterange"
          range-separator="至"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
          size="small"
          style="margin-left: 12px;"
          @change="handleCustomDateChange"
        />
      </div>
      
      <div class="filter-right">
        <el-select
          v-model="selectedPlatform"
          placeholder="全部平台"
          clearable
          size="small"
          style="width: 150px; margin-right: 12px;"
          @change="handleFilterChange"
        >
          <el-option
            v-for="platform in platforms"
            :key="platform.id"
            :label="platform.name"
            :value="platform.id"
          />
        </el-select>
        
        <el-select
          v-model="selectedStatus"
          placeholder="全部状态"
          clearable
          size="small"
          style="width: 120px;"
          @change="handleFilterChange"
        >
          <el-option label="已结账" value="已结账" />
          <el-option label="已完成" value="已完成" />
          <el-option label="进行中" value="进行中" />
        </el-select>
      </div>
    </div>

    <!-- 图表区域 -->
    <el-row :gutter="20" class="charts-row">
      <!-- 平台收入分布 -->
      <el-col :xs="24" :md="12">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <span>平台收入分布</span>
            </div>
          </template>
          <div class="platform-revenue-list">
            <div
              v-for="(revenue, platformName) in platformRevenue"
              :key="platformName"
              class="platform-item"
            >
              <div class="platform-info">
                <div class="platform-name">{{ platformName }}</div>
                <div class="platform-revenue">¥{{ formatMoney(revenue) }}</div>
              </div>
              <el-progress
                :percentage="getPlatformPercentage(revenue)"
                :stroke-width="8"
                :color="getPlatformColor(platformName)"
                :show-text="false"
              />
            </div>
            <el-empty
              v-if="Object.keys(platformRevenue).length === 0"
              description="暂无数据"
              :image-size="80"
            />
          </div>
        </el-card>
      </el-col>

      <!-- 时间收入趋势 -->
      <el-col :xs="24" :md="12">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <span>收入趋势</span>
            </div>
          </template>
          <div class="revenue-trend">
            <div
              v-for="(item, index) in revenueTrend"
              :key="index"
              class="trend-item"
            >
              <div class="trend-label">{{ item.label }}</div>
              <div class="trend-bar-container">
                <div
                  class="trend-bar"
                  :style="{ width: item.percentage + '%', backgroundColor: item.color }"
                ></div>
                <span class="trend-value">¥{{ formatMoney(item.value) }}</span>
              </div>
            </div>
            <el-empty
              v-if="revenueTrend.length === 0"
              description="暂无数据"
              :image-size="80"
            />
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 项目收入列表 -->
    <el-card class="projects-card">
      <template #header>
        <div class="card-header">
          <span>项目收入明细</span>
          <div class="header-actions">
            <el-input
              v-model="searchKeyword"
              placeholder="搜索项目名称或学生姓名..."
              clearable
              size="small"
              style="width: 250px; margin-right: 12px;"
              @input="handleSearch"
            >
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
            </el-input>
            <el-button
              size="small"
              :icon="Refresh"
              @click="loadData"
              :loading="loading"
            >
              刷新
            </el-button>
          </div>
        </div>
      </template>

      <el-table
        :data="paginatedProjects"
        v-loading="loading"
        stripe
        style="width: 100%"
        @row-click="handleRowClick"
        class="finance-table"
      >
        <el-table-column prop="title" label="项目名称" min-width="200">
          <template #default="{ row }">
            <div class="project-name-cell">
              <el-icon class="project-icon"><FolderOpened /></el-icon>
              <span>{{ row.title }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="student_name" label="学生姓名" min-width="120" />
        <el-table-column prop="platform.name" label="平台" min-width="120">
          <template #default="{ row }">
            {{ row.platform?.name || '未知平台' }}
          </template>
        </el-table-column>
        <el-table-column prop="price" label="订单金额" min-width="120" align="right">
          <template #default="{ row }">
            <span class="money-text">¥{{ formatMoney(row.price) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="actual_income" label="实际收入" min-width="120" align="right">
          <template #default="{ row }">
            <span class="money-text income-text">¥{{ formatMoney(row.actual_income) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" min-width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" size="small">
              {{ row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="is_paid" label="结账状态" min-width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="row.is_paid ? 'success' : 'info'" size="small">
              {{ row.is_paid ? '已结账' : '未结账' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="项目周期" min-width="150">
          <template #default="{ row }">
            <div class="project-duration">
              <el-icon :size="14"><Timer /></el-icon>
              <span>{{ getProjectDuration(row) }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" min-width="160">
          <template #default="{ row }">
            {{ formatDateTime(row.created_at) }}
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-wrapper" v-if="totalProjects > pageSize">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :total="totalProjects"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handlePageChange"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  Money,
  Check,
  Clock,
  TrendCharts,
  Search,
  Refresh,
  FolderOpened,
  Timer,
} from '@element-plus/icons-vue'
import { projectApi, type Project } from '@/api/project'
import { platformApi, type Platform } from '@/api/platform'

const router = useRouter()

// 数据
const loading = ref(false)
const projects = ref<Project[]>([])
const platforms = ref<Platform[]>([])

// 筛选条件
const timeRange = ref<'all' | 'year' | 'month' | 'week'>('all')
const customDateRange = ref<[Date, Date] | null>(null)
const selectedPlatform = ref<number | null>(null)
const selectedStatus = ref<string | null>(null)
const searchKeyword = ref('')

// 分页
const currentPage = ref(1)
const pageSize = ref(20)

// 计算属性
const totalRevenue = computed(() => {
  return filteredProjects.value
    .filter(p => p.is_paid && p.actual_income > 0)
    .reduce((sum, p) => sum + p.actual_income, 0)
})

const paidProjectsCount = computed(() => {
  return filteredProjects.value.filter(p => p.is_paid).length
})

const pendingRevenue = computed(() => {
  return filteredProjects.value
    .filter(p => !p.is_paid && p.price > 0)
    .reduce((sum, p) => sum + p.price, 0)
})

const avgRevenue = computed(() => {
  const paidProjects = filteredProjects.value.filter(p => p.is_paid && p.actual_income > 0)
  if (paidProjects.length === 0) return 0
  return totalRevenue.value / paidProjects.length
})

const platformRevenue = computed(() => {
  const revenue: Record<string, number> = {}
  filteredProjects.value.forEach(project => {
    if (project.is_paid && project.actual_income > 0) {
      const platformName = project.platform?.name || '未知平台'
      revenue[platformName] = (revenue[platformName] || 0) + project.actual_income
    }
  })
  return revenue
})

const revenueTrend = computed(() => {
  // 根据时间范围生成趋势数据
  const trend: Array<{ label: string; value: number; percentage: number; color: string }> = []
  
  if (timeRange.value === 'month') {
    // 本月按周统计
    const weeks = getWeeksInMonth(new Date())
    weeks.forEach(week => {
      const weekRevenue = filteredProjects.value
        .filter(p => {
          if (!p.is_paid || p.actual_income <= 0) return false
          const paidDate = new Date(p.updated_at)
          return paidDate >= week.start && paidDate <= week.end
        })
        .reduce((sum, p) => sum + p.actual_income, 0)
      
      trend.push({
        label: week.label,
        value: weekRevenue,
        percentage: 0,
        color: '#409eff'
      })
    })
  } else if (timeRange.value === 'year') {
    // 本年按月统计
    const months = getMonthsInYear(new Date().getFullYear())
    months.forEach(month => {
      const monthRevenue = filteredProjects.value
        .filter(p => {
          if (!p.is_paid || p.actual_income <= 0) return false
          const paidDate = new Date(p.updated_at)
          return paidDate.getMonth() === month.index && paidDate.getFullYear() === new Date().getFullYear()
        })
        .reduce((sum, p) => sum + p.actual_income, 0)
      
      trend.push({
        label: month.label,
        value: monthRevenue,
        percentage: 0,
        color: '#409eff'
      })
    })
  }
  
  // 计算百分比
  const maxValue = Math.max(...trend.map(t => t.value), 1)
  trend.forEach(item => {
    item.percentage = (item.value / maxValue) * 100
  })
  
  return trend
})

const filteredProjects = computed(() => {
  let result = [...projects.value]
  
  // 时间筛选
  if (timeRange.value !== 'all' || customDateRange.value) {
    const now = new Date()
    let startDate: Date | null = null
    let endDate: Date | null = null
    
    if (customDateRange.value) {
      [startDate, endDate] = customDateRange.value
    } else {
      switch (timeRange.value) {
        case 'year':
          startDate = new Date(now.getFullYear(), 0, 1)
          endDate = new Date(now.getFullYear(), 11, 31, 23, 59, 59)
          break
        case 'month':
          startDate = new Date(now.getFullYear(), now.getMonth(), 1)
          endDate = new Date(now.getFullYear(), now.getMonth() + 1, 0, 23, 59, 59)
          break
        case 'week':
          const day = now.getDay()
          startDate = new Date(now)
          startDate.setDate(now.getDate() - day)
          startDate.setHours(0, 0, 0, 0)
          endDate = new Date(startDate)
          endDate.setDate(startDate.getDate() + 6)
          endDate.setHours(23, 59, 59, 999)
          break
      }
    }
    
    if (startDate && endDate) {
      result = result.filter(p => {
        const projectDate = new Date(p.created_at)
        return projectDate >= startDate! && projectDate <= endDate!
      })
    }
  }
  
  // 平台筛选
  if (selectedPlatform.value) {
    result = result.filter(p => p.platform_id === selectedPlatform.value)
  }
  
  // 状态筛选
  if (selectedStatus.value) {
    result = result.filter(p => p.status === selectedStatus.value)
  }
  
  // 搜索
  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    result = result.filter(p =>
      p.title.toLowerCase().includes(keyword) ||
      (p.student_name && p.student_name.toLowerCase().includes(keyword))
    )
  }
  
  return result
})

const totalProjects = computed(() => filteredProjects.value.length)

const paginatedProjects = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredProjects.value.slice(start, end)
})

// 方法
const loadData = async () => {
  loading.value = true
  try {
    const [projectsData, platformsData] = await Promise.all([
      projectApi.list(),
      platformApi.list()
    ])
    projects.value = projectsData
    platforms.value = platformsData
  } catch (error) {
    ElMessage.error('加载数据失败')
  } finally {
    loading.value = false
  }
}

const formatMoney = (amount: number): string => {
  return amount.toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ',')
}

const formatDateTime = (dateString: string): string => {
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const getStatusType = (status: string): string => {
  const statusMap: Record<string, string> = {
    '进行中': 'primary',
    '已完成': 'success',
    '已结账': 'success',
    '已暂停': 'warning',
    '已取消': 'danger',
  }
  return statusMap[status] || 'info'
}

const getProjectDuration = (project: Project): string => {
  const start = new Date(project.created_at)
  const end = project.updated_at ? new Date(project.updated_at) : new Date()
  const diff = end.getTime() - start.getTime()
  const days = Math.floor(diff / (1000 * 60 * 60 * 24))
  
  if (days < 1) return '1天以内'
  if (days < 30) return `${days}天`
  if (days < 365) {
    const months = Math.floor(days / 30)
    return `${months}个月`
  }
  const years = Math.floor(days / 365)
  const remainingMonths = Math.floor((days % 365) / 30)
  return remainingMonths > 0 ? `${years}年${remainingMonths}个月` : `${years}年`
}

const getPlatformPercentage = (revenue: number): number => {
  if (totalRevenue.value === 0) return 0
  return Math.round((revenue / totalRevenue.value) * 100)
}

const getPlatformColor = (platformName: string): string => {
  const colors = ['#409eff', '#67c23a', '#e6a23c', '#f56c6c', '#909399', '#606266']
  const index = platformName.charCodeAt(0) % colors.length
  return colors[index]
}

const getWeeksInMonth = (date: Date) => {
  const year = date.getFullYear()
  const month = date.getMonth()
  const firstDay = new Date(year, month, 1)
  const lastDay = new Date(year, month + 1, 0)
  const weeks: Array<{ label: string; start: Date; end: Date }> = []
  
  let currentWeekStart = new Date(firstDay)
  while (currentWeekStart <= lastDay) {
    const currentWeekEnd = new Date(currentWeekStart)
    currentWeekEnd.setDate(currentWeekStart.getDate() + 6)
    if (currentWeekEnd > lastDay) currentWeekEnd.setTime(lastDay.getTime())
    
    weeks.push({
      label: `${currentWeekStart.getDate()}日-${currentWeekEnd.getDate()}日`,
      start: new Date(currentWeekStart),
      end: new Date(currentWeekEnd)
    })
    
    currentWeekStart.setDate(currentWeekStart.getDate() + 7)
  }
  
  return weeks
}

const getMonthsInYear = (year: number) => {
  const months = []
  for (let i = 0; i < 12; i++) {
    months.push({
      label: `${i + 1}月`,
      index: i
    })
  }
  return months
}

const handleTimeRangeChange = () => {
  customDateRange.value = null
  handleFilterChange()
}

const handleCustomDateChange = () => {
  if (customDateRange.value) {
    timeRange.value = 'all'
  }
  handleFilterChange()
}

const handleFilterChange = () => {
  currentPage.value = 1
}

const handleSearch = () => {
  currentPage.value = 1
}

const handleRowClick = (row: Project) => {
  router.push(`/projects/${row.id}`)
}

const handleSizeChange = (size: number) => {
  pageSize.value = size
  currentPage.value = 1
}

const handlePageChange = (page: number) => {
  currentPage.value = page
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.finance-page {
  padding: 20px;
  background: #f5f7fa;
  min-height: calc(100vh - 60px);
}

.stats-row {
  margin-bottom: 20px;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  transition: all 0.3s;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12);
}

.stat-icon {
  width: 56px;
  height: 56px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 12px;
  flex-shrink: 0;
}

.total-revenue .stat-icon {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
}

.paid-projects .stat-icon {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  color: #fff;
}

.pending-revenue .stat-icon {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
  color: #fff;
}

.avg-revenue .stat-icon {
  background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
  color: #fff;
}

.stat-content {
  flex: 1;
  min-width: 0;
}

.stat-label {
  font-size: 13px;
  color: #909399;
  margin-bottom: 8px;
}

.stat-value {
  font-size: 24px;
  font-weight: 600;
  color: #303133;
  line-height: 1.2;
}

.filter-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding: 16px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.filter-left,
.filter-right {
  display: flex;
  align-items: center;
}

.charts-row {
  margin-bottom: 20px;
}

.chart-card {
  height: 100%;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
  color: #303133;
}

.header-actions {
  display: flex;
  align-items: center;
}

.platform-revenue-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.platform-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.platform-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.platform-name {
  font-size: 14px;
  color: #303133;
  font-weight: 500;
}

.platform-revenue {
  font-size: 14px;
  color: #409eff;
  font-weight: 600;
}

.revenue-trend {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.trend-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.trend-label {
  font-size: 13px;
  color: #606266;
}

.trend-bar-container {
  display: flex;
  align-items: center;
  gap: 12px;
}

.trend-bar {
  flex: 1;
  height: 24px;
  border-radius: 4px;
  transition: width 0.3s ease;
  min-width: 4px;
}

.trend-value {
  font-size: 13px;
  color: #303133;
  font-weight: 600;
  min-width: 80px;
  text-align: right;
}

.projects-card {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.finance-table {
  margin-top: 16px;
}

.finance-table :deep(.el-table__row) {
  cursor: pointer;
}

.finance-table :deep(.el-table__row:hover) {
  background: #f5f7fa;
}

.project-name-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}

.project-icon {
  color: #409eff;
}

.money-text {
  font-weight: 600;
  color: #303133;
}

.income-text {
  color: #67c23a;
}

.project-duration {
  display: flex;
  align-items: center;
  gap: 4px;
  color: #909399;
  font-size: 13px;
}

.pagination-wrapper {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .filter-section {
    flex-direction: column;
    gap: 12px;
    align-items: stretch;
  }

  .filter-left,
  .filter-right {
    flex-direction: column;
    width: 100%;
  }

  .filter-right .el-select {
    width: 100% !important;
    margin-right: 0 !important;
    margin-bottom: 8px;
  }
}
</style>

