<template>
  <div class="historical-project-import-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <div class="header-left">
            <el-button :icon="ArrowLeft" @click="$router.back()">返回</el-button>
            <span class="page-title">导入历史项目</span>
          </div>
        </div>
      </template>

      <div class="import-content">
        <el-steps :active="currentStep" finish-status="success" align-center>
          <el-step title="选择项目" />
          <el-step title="选择数据" />
          <el-step title="确认导入" />
        </el-steps>

        <!-- 步骤1: 选择项目 -->
        <div v-if="currentStep === 0" class="step-content">
          <el-form :inline="true" class="filter-form">
            <el-form-item label="平台">
              <el-select
                v-model="filters.platform_id"
                placeholder="全部平台"
                clearable
                size="small"
                @change="loadProjects"
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
            <el-form-item>
              <el-input
                v-model="searchKeyword"
                placeholder="搜索项目..."
                clearable
                size="small"
                style="width: 200px"
                @input="loadProjects"
              >
                <template #prefix>
                  <el-icon><Search /></el-icon>
                </template>
              </el-input>
            </el-form-item>
          </el-form>

          <el-table
            :data="projects"
            v-loading="loadingProjects"
            @selection-change="handleSelectionChange"
            stripe
            style="margin-top: 20px"
          >
            <el-table-column type="selection" width="55" />
            <el-table-column prop="title" label="项目名称" min-width="200" />
            <el-table-column prop="platform.name" label="平台" min-width="120" />
            <el-table-column prop="price" label="金额" min-width="100" align="right">
              <template #default="{ row }">
                ¥{{ (row.price || 0).toFixed(2) }}
              </template>
            </el-table-column>
            <el-table-column prop="status" label="状态" min-width="100">
              <template #default="{ row }">
                <el-tag :type="getStatusType(row.status)" size="small">
                  {{ row.status }}
                </el-tag>
              </template>
            </el-table-column>
          </el-table>
        </div>

        <!-- 步骤2: 选择数据 -->
        <div v-if="currentStep === 1" class="step-content">
          <el-checkbox-group v-model="importOptions">
            <el-checkbox label="include_attachments">导入附件</el-checkbox>
            <el-checkbox label="include_parts">导入配件清单</el-checkbox>
            <el-checkbox label="include_logs">导入项目日志</el-checkbox>
          </el-checkbox-group>
          <p class="tip-text">已选择 {{ selectedProjects.length }} 个项目</p>
        </div>

        <!-- 步骤3: 确认导入 -->
        <div v-if="currentStep === 2" class="step-content">
          <el-alert
            title="确认导入"
            type="info"
            :closable="false"
            style="margin-bottom: 20px"
          >
            <template #default>
              <p>将导入 {{ selectedProjects.length }} 个历史项目</p>
              <p v-if="importOptions.includes('include_attachments')">✓ 包含附件</p>
              <p v-if="importOptions.includes('include_parts')">✓ 包含配件清单</p>
              <p v-if="importOptions.includes('include_logs')">✓ 包含项目日志</p>
            </template>
          </el-alert>
        </div>

        <div class="step-actions">
          <el-button v-if="currentStep > 0" @click="currentStep--">上一步</el-button>
          <el-button
            v-if="currentStep < 2"
            type="primary"
            @click="handleNext"
            :disabled="currentStep === 0 && selectedProjects.length === 0"
          >
            下一步
          </el-button>
          <el-button
            v-if="currentStep === 2"
            type="primary"
            @click="handleImport"
            :loading="importing"
          >
            确认导入
          </el-button>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ArrowLeft, Search } from '@element-plus/icons-vue'
import { historicalProjectApi } from '@/api/historicalProject'
import { projectApi, type Project } from '@/api/project'
import { platformApi, type Platform } from '@/api/platform'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()

const currentStep = ref(0)
const projects = ref<Project[]>([])
const platforms = ref<Platform[]>([])
const selectedProjects = ref<Project[]>([])
const loadingProjects = ref(false)
const importing = ref(false)
const searchKeyword = ref('')
const filters = ref({
  platform_id: undefined as number | undefined,
})

const importOptions = ref<string[]>(['include_attachments'])

const loadProjects = async () => {
  loadingProjects.value = true
  try {
    const params: any = {}
    if (filters.value.platform_id) {
      params.platform_id = filters.value.platform_id
    }
    if (userStore.userInfo?.role !== 'admin') {
      params.user_id = userStore.userInfo?.id
    }
    const allProjects = await projectApi.list(params)
    // 过滤已搜索的关键词
    if (searchKeyword.value) {
      const keyword = searchKeyword.value.toLowerCase()
      projects.value = allProjects.filter(p =>
        p.title.toLowerCase().includes(keyword) ||
        (p.student_name && p.student_name.toLowerCase().includes(keyword))
      )
    } else {
      projects.value = allProjects
    }
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '加载项目列表失败')
  } finally {
    loadingProjects.value = false
  }
}

const loadPlatforms = async () => {
  try {
    platforms.value = await platformApi.list()
  } catch (error) {
    console.error('加载平台列表失败:', error)
  }
}

const handleSelectionChange = (selection: Project[]) => {
  selectedProjects.value = selection
}

const handleNext = () => {
  if (currentStep.value === 0 && selectedProjects.value.length === 0) {
    ElMessage.warning('请至少选择一个项目')
    return
  }
  currentStep.value++
}

const handleImport = async () => {
  if (selectedProjects.value.length === 0) {
    ElMessage.warning('请至少选择一个项目')
    return
  }
  importing.value = true
  try {
    const options: any = {}
    if (importOptions.value.includes('include_attachments')) {
      options.include_attachments = true
    }
    if (importOptions.value.includes('include_parts')) {
      options.include_parts = true
    }
    if (importOptions.value.includes('include_logs')) {
      options.include_logs = true
    }

    let successCount = 0
    let failCount = 0

    for (const project of selectedProjects.value) {
      try {
        await historicalProjectApi.importFromProject(project.id, options)
        successCount++
      } catch (error: any) {
        console.error(`导入项目 ${project.title} 失败:`, error)
        failCount++
      }
    }

    if (successCount > 0) {
      ElMessage.success(`成功导入 ${successCount} 个项目${failCount > 0 ? `，${failCount} 个失败` : ''}`)
      router.push('/historical-projects')
    } else {
      ElMessage.error('导入失败')
    }
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '导入失败')
  } finally {
    importing.value = false
  }
}

const getStatusType = (status: string) => {
  const statusMap: Record<string, string> = {
    '进行中': 'primary',
    '已完成': 'success',
    '已结账': 'success',
  }
  return statusMap[status] || 'info'
}

onMounted(() => {
  loadPlatforms()
  loadProjects()
})
</script>

<style scoped>
.historical-project-import-page {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.page-title {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.import-content {
  margin-top: 40px;
}

.step-content {
  margin: 40px 0;
  min-height: 300px;
}

.filter-form {
  margin-bottom: 20px;
}

.tip-text {
  margin-top: 20px;
  color: #909399;
  font-size: 14px;
}

.step-actions {
  display: flex;
  justify-content: center;
  gap: 12px;
  margin-top: 40px;
}

/* 移动端样式 */
@media (max-width: 768px) {
  .historical-project-import-page {
    padding: 12px;
  }

  .historical-project-import-page :deep(.el-card__header) {
    padding: 12px;
  }

  .historical-project-import-page :deep(.el-card__body) {
    padding: 12px;
  }

  .card-header {
    flex-direction: column;
    align-items: stretch;
    gap: 10px;
  }

  .header-left {
    justify-content: center;
  }

  .page-title {
    font-size: 16px;
    text-align: center;
  }

  .import-content {
    margin-top: 20px;
  }

  .step-content {
    margin: 20px 0;
    min-height: 200px;
  }

  .filter-form :deep(.el-form-item) {
    display: block;
    margin-right: 0;
    margin-bottom: 10px;
  }

  .filter-form :deep(.el-select),
  .filter-form :deep(.el-input) {
    width: 100% !important;
  }

  .tip-text {
    font-size: 12px;
  }

  .step-actions {
    flex-direction: column;
    gap: 8px;
    margin-top: 20px;
  }

  .step-actions .el-button {
    width: 100%;
  }

  /* 表格横向滚动 */
  .historical-project-import-page :deep(.el-table) {
    font-size: 12px;
    display: block;
    overflow-x: auto;
    white-space: nowrap;
    -webkit-overflow-scrolling: touch;
  }

  .historical-project-import-page :deep(.el-table__cell) {
    padding: 8px 4px;
  }
}

@media (max-width: 480px) {
  .historical-project-import-page {
    padding: 8px;
  }

  .page-title {
    font-size: 15px;
  }

  .historical-project-import-page :deep(.el-table__cell) {
    padding: 6px 2px;
  }
}
</style>

