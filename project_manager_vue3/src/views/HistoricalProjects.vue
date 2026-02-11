<template>
  <div class="historical-projects-page">
    <el-card class="projects-card">
      <template #header>
        <div class="card-header">
          <span class="page-title">历史项目管理</span>
          <div class="header-actions">
            <el-button type="success" @click="$router.push('/historical-projects/import')">
              <el-icon><Upload /></el-icon>
              导入项目
            </el-button>
            <el-button type="primary" @click="showCreateDialog = true">
              <el-icon><Plus /></el-icon>
              新建历史项目
            </el-button>
          </div>
        </div>
      </template>

      <!-- 筛选条件 -->
      <div class="filter-section">
        <el-form :inline="true" class="filter-form">
          <el-form-item label="平台">
            <el-select
              v-model="filters.platform_id"
              placeholder="全部平台"
              clearable
              size="small"
              @change="handleFilterChange"
              style="width: 150px"
            >
              <el-option
                v-for="platform in platforms"
                :key="platform.id"
                :label="platform.name"
                :value="platform.id"
              />
            </el-select>
          </el-form-item>
          <el-form-item label="状态">
            <el-select
              v-model="filters.status"
              placeholder="全部状态"
              clearable
              size="small"
              @change="handleFilterChange"
              style="width: 120px"
            >
              <el-option label="已完成" value="已完成" />
              <el-option label="已结账" value="已结账" />
            </el-select>
          </el-form-item>
          <el-form-item label="标签">
            <el-select
              v-model="filters.tag_ids"
              placeholder="选择标签筛选"
              clearable
              multiple
              collapse-tags
              collapse-tags-tooltip
              size="small"
              @change="handleFilterChange"
              style="width: 200px"
            >
              <el-option
                v-for="tag in allTags"
                :key="tag.id"
                :label="tag.name"
                :value="tag.id"
              >
                <span :style="{ color: tag.color }">{{ tag.name }}</span>
              </el-option>
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" size="small" @click="handleFilterChange">查询</el-button>
            <el-button size="small" @click="resetFilters">重置</el-button>
          </el-form-item>
        </el-form>
      </div>

      <!-- 项目列表 -->
      <div class="table-wrapper">
        <el-table
          :data="projects"
          style="width: 100%"
          v-loading="loading"
          stripe
          class="projects-table"
          empty-text="暂无历史项目数据"
        >
          <el-table-column prop="title" label="项目名称" min-width="200">
            <template #default="{ row }">
              <div class="project-name-cell">
                <el-icon class="project-icon"><Clock /></el-icon>
                <span>{{ row.title }}</span>
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="platform.name" label="平台" min-width="120">
            <template #default="{ row }">
              {{ row.platform?.name || '未知平台' }}
            </template>
          </el-table-column>
          <el-table-column label="标签" min-width="150">
            <template #default="{ row }">
              <div v-if="row.tags && row.tags.length > 0" class="tags-cell">
                <el-tag
                  v-for="tag in row.tags"
                  :key="tag.id"
                  :style="{ backgroundColor: tag.color + '20', borderColor: tag.color, color: tag.color }"
                  size="small"
                  class="project-tag"
                >
                  {{ tag.name }}
                </el-tag>
              </div>
              <span v-else class="no-tags">-</span>
            </template>
          </el-table-column>
          <el-table-column prop="price" label="金额" min-width="100" align="right">
            <template #default="{ row }">
              <span class="money-text">¥{{ (row.price || 0).toFixed(2) }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="actual_income" label="实际收入" min-width="100" align="right">
            <template #default="{ row }">
              <span class="money-text">¥{{ (row.actual_income || 0).toFixed(2) }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="status" label="状态" min-width="100">
            <template #default="{ row }">
              <el-tag :type="getStatusType(row.status)" size="small">
                {{ row.status || '已完成' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="completed_at" label="完成时间" min-width="150">
            <template #default="{ row }">
              {{ formatDate(row.completed_at) }}
            </template>
          </el-table-column>
          <el-table-column label="操作" min-width="150" fixed="right" align="center">
            <template #default="{ row }">
              <div class="action-buttons">
                <el-button
                  type="primary"
                  size="small"
                  :icon="View"
                  @click="goToDetail(row.id)"
                >
                  查看
                </el-button>
                <el-button
                  type="danger"
                  size="small"
                  :icon="Delete"
                  @click="handleDelete(row)"
                >
                  删除
                </el-button>
              </div>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </el-card>

    <!-- 创建历史项目对话框 -->
    <el-dialog
      v-model="showCreateDialog"
      title="新建历史项目"
      width="600px"
      @close="resetForm"
    >
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="100px"
      >
        <el-form-item label="项目名称" prop="title">
          <el-input v-model="form.title" placeholder="请输入项目名称" />
        </el-form-item>
        <el-form-item label="学生姓名" prop="student_name">
          <el-input v-model="form.student_name" placeholder="请输入学生姓名" />
        </el-form-item>
        <el-form-item label="接单平台" prop="platform_id">
          <el-select v-model="form.platform_id" placeholder="请选择平台" style="width: 100%">
            <el-option
              v-for="platform in platforms"
              :key="platform.id"
              :label="platform.name"
              :value="platform.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="项目金额" prop="price">
          <el-input-number v-model="form.price" :min="0" :precision="2" style="width: 100%" />
        </el-form-item>
        <el-form-item label="实际收入" prop="actual_income">
          <el-input-number v-model="form.actual_income" :min="0" :precision="2" style="width: 100%" />
        </el-form-item>
        <el-form-item label="完成时间" prop="completed_at">
          <el-date-picker
            v-model="form.completed_at"
            type="datetime"
            placeholder="选择完成时间"
            style="width: 100%"
            format="YYYY-MM-DD HH:mm:ss"
            value-format="YYYY-MM-DDTHH:mm:ss"
          />
        </el-form-item>
        <el-form-item label="项目描述" prop="description">
          <el-input
            v-model="form.description"
            type="textarea"
            :rows="4"
            placeholder="请输入项目描述"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="handleCreate" :loading="creating">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Upload, View, Delete, Clock } from '@element-plus/icons-vue'
import { historicalProjectApi, type HistoricalProject } from '@/api/historicalProject'
import { platformApi, type Platform } from '@/api/platform'
import { useUserStore } from '@/stores/user'
import { tagApi, type Tag } from '@/api/tag'

const router = useRouter()
const userStore = useUserStore()

const projects = ref<HistoricalProject[]>([])
const platforms = ref<Platform[]>([])
const loading = ref(false)
const creating = ref(false)
const showCreateDialog = ref(false)
const formRef = ref()

const filters = ref({
  platform_id: undefined as number | undefined,
  status: undefined as string | undefined,
  tag_ids: [] as number[],
})

const allTags = ref<Tag[]>([])

const form = ref({
  title: '',
  student_name: '',
  platform_id: undefined as number | undefined,
  price: 0,
  actual_income: 0,
  status: '已完成',
  description: '',
  completed_at: '',
})

const rules = {
  title: [{ required: true, message: '请输入项目名称', trigger: 'blur' }],
  platform_id: [{ required: true, message: '请选择接单平台', trigger: 'change' }],
}

const loadProjects = async () => {
  // 检查是否已登录
  if (!userStore.isAuthenticated) {
    ElMessage.warning('请先登录')
    router.push('/login')
    return
  }
  
  loading.value = true
  try {
    const params: any = {}
    if (filters.value.platform_id) {
      params.platform_id = filters.value.platform_id
    }
    if (filters.value.status) {
      params.status = filters.value.status
    }
    if (filters.value.tag_ids && filters.value.tag_ids.length > 0) {
      params.tag_ids = filters.value.tag_ids.join(',')
    }
    if (userStore.userInfo?.role !== 'admin') {
      params.user_id = userStore.userInfo?.id
    }
    projects.value = await historicalProjectApi.list(params)
  } catch (error: any) {
    // 401 错误会被响应拦截器处理，这里不需要重复处理
    if (error.response?.status !== 401) {
      ElMessage.error(error.response?.data?.detail || '加载历史项目列表失败')
    }
  } finally {
    loading.value = false
  }
}

const loadPlatforms = async () => {
  try {
    platforms.value = await platformApi.list()
  } catch (error) {
    console.error('加载平台列表失败:', error)
  }
}

const handleFilterChange = () => {
  loadProjects()
}

const resetFilters = () => {
  filters.value = {
    platform_id: undefined,
    status: undefined,
    tag_ids: [],
  }
  loadProjects()
}

// 加载标签列表
const loadTags = async () => {
  try {
    allTags.value = await tagApi.list(true)
  } catch (error) {
    console.error('加载标签失败:', error)
  }
}

const goToDetail = (id: number) => {
  router.push(`/historical-projects/${id}`)
}

const handleDelete = async (project: HistoricalProject) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除历史项目"${project.title}"吗？`,
      '提示',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )
    await historicalProjectApi.delete(project.id)
    ElMessage.success('删除成功')
    loadProjects()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.response?.data?.detail || '删除失败')
    }
  }
}

const resetForm = () => {
  form.value = {
    title: '',
    student_name: '',
    platform_id: undefined,
    price: 0,
    actual_income: 0,
    status: '已完成',
    description: '',
    completed_at: '',
  }
  formRef.value?.clearValidate()
}

const handleCreate = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid: boolean) => {
    if (!valid) return
    creating.value = true
    try {
      await historicalProjectApi.create({
        ...form.value,
        user_id: userStore.userInfo!.id,
      })
      ElMessage.success('创建成功')
      showCreateDialog.value = false
      resetForm()
      loadProjects()
    } catch (error: any) {
      ElMessage.error(error.response?.data?.detail || '创建失败')
    } finally {
      creating.value = false
    }
  })
}

const getStatusType = (status?: string) => {
  const statusMap: Record<string, string> = {
    '已完成': 'success',
    '已结账': 'success',
  }
  return statusMap[status || '已完成'] || 'info'
}

const formatDate = (dateStr?: string) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN')
}

onMounted(async () => {
  // 确保用户信息已加载
  if (userStore.isAuthenticated && !userStore.userInfo) {
    await userStore.fetchUserInfo()
  }
  
  // 再次检查认证状态（可能在 fetchUserInfo 时 token 已过期）
  if (!userStore.isAuthenticated) {
    router.push('/login')
    return
  }
  
  await Promise.all([
    loadPlatforms(),
    loadTags(),
    loadProjects()
  ])
})
</script>

<style scoped>
.historical-projects-page {
  padding: 20px;
}

.projects-card {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.page-title {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.filter-section {
  margin-bottom: 20px;
}

.table-wrapper {
  margin-top: 20px;
}

.project-name-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}

.project-icon {
  color: #909399;
}

.money-text {
  font-weight: 500;
  color: #303133;
}

.action-buttons {
  display: flex;
  gap: 8px;
  justify-content: center;
}

.tags-cell {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.project-tag {
  font-size: 12px;
  padding: 2px 8px;
  border-radius: 4px;
}

.no-tags {
  color: #909399;
  font-size: 12px;
}
</style>

