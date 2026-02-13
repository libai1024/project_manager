<template>
  <div class="historical-project-detail-page">
    <el-card v-loading="loading">
      <template #header>
        <div class="card-header">
          <div class="header-left">
            <el-button :icon="ArrowLeft" @click="$router.back()">返回</el-button>
            <span class="page-title">{{ project?.title || '历史项目详情' }}</span>
          </div>
          <div class="header-actions">
            <el-button type="primary" :icon="Edit" @click="showEditDialog = true">编辑</el-button>
            <el-button type="danger" :icon="Delete" @click="handleDelete">删除</el-button>
          </div>
        </div>
      </template>

      <div v-if="project" class="project-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="项目名称">{{ project.title }}</el-descriptions-item>
          <el-descriptions-item label="学生姓名">{{ project.student_name || '-' }}</el-descriptions-item>
          <el-descriptions-item label="接单平台">{{ project.platform?.name || '-' }}</el-descriptions-item>
          <el-descriptions-item label="项目金额">¥{{ (project.price || 0).toFixed(2) }}</el-descriptions-item>
          <el-descriptions-item label="实际收入">¥{{ (project.actual_income || 0).toFixed(2) }}</el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="getStatusType(project.status)">{{ project.status || '已完成' }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="完成时间">{{ formatDate(project.completed_at) }}</el-descriptions-item>
          <el-descriptions-item label="创建时间">{{ formatDate(project.created_at) }}</el-descriptions-item>
          <el-descriptions-item label="项目描述" :span="2">{{ project.description || '-' }}</el-descriptions-item>
          <el-descriptions-item label="GitHub地址" :span="2">
            <a v-if="project.github_url" :href="project.github_url" target="_blank">{{ project.github_url }}</a>
            <span v-else>-</span>
          </el-descriptions-item>
          <el-descriptions-item label="项目标签" :span="2">
            <div v-if="project.tags && project.tags.length > 0" class="project-tags">
              <el-tag
                v-for="tag in project.tags"
                :key="tag.id"
                :style="{ backgroundColor: tag.color, borderColor: tag.color, color: '#fff' }"
                size="small"
                effect="dark"
                round
              >
                {{ tag.name }}
              </el-tag>
            </div>
            <span v-else>-</span>
          </el-descriptions-item>
        </el-descriptions>
      </div>
    </el-card>

    <!-- 编辑对话框 -->
    <el-dialog
      v-model="showEditDialog"
      title="编辑历史项目"
      width="600px"
      @close="resetForm"
    >
      <el-form
        ref="formRef"
        :model="editForm"
        :rules="rules"
        label-width="100px"
      >
        <el-form-item label="项目名称" prop="title">
          <el-input v-model="editForm.title" placeholder="请输入项目名称" />
        </el-form-item>
        <el-form-item label="学生姓名">
          <el-input v-model="editForm.student_name" placeholder="请输入学生姓名" />
        </el-form-item>
        <el-form-item label="接单平台" prop="platform_id">
          <el-select v-model="editForm.platform_id" placeholder="请选择平台" style="width: 100%">
            <el-option
              v-for="platform in platforms"
              :key="platform.id"
              :label="platform.name"
              :value="platform.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="项目金额">
          <el-input-number v-model="editForm.price" :min="0" :precision="2" style="width: 100%" />
        </el-form-item>
        <el-form-item label="实际收入">
          <el-input-number v-model="editForm.actual_income" :min="0" :precision="2" style="width: 100%" />
        </el-form-item>
        <el-form-item label="完成时间">
          <el-date-picker
            v-model="editForm.completed_at"
            type="datetime"
            placeholder="选择完成时间"
            style="width: 100%"
            format="YYYY-MM-DD HH:mm:ss"
            value-format="YYYY-MM-DDTHH:mm:ss"
          />
        </el-form-item>
        <el-form-item label="项目描述">
          <el-input
            v-model="editForm.description"
            type="textarea"
            :rows="4"
            placeholder="请输入项目描述"
          />
        </el-form-item>
        <el-form-item label="项目标签">
          <TagSelector v-model="editForm.tag_ids" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showEditDialog = false">取消</el-button>
        <el-button type="primary" @click="handleUpdate" :loading="updating">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ArrowLeft, Edit, Delete } from '@element-plus/icons-vue'
import { historicalProjectApi, type HistoricalProject } from '@/api/historicalProject'
import { platformApi, type Platform } from '@/api/platform'
import TagSelector from '@/components/TagSelector.vue'
import { tagApi } from '@/api/tag'

const route = useRoute()
const router = useRouter()

const project = ref<HistoricalProject | null>(null)
const platforms = ref<Platform[]>([])
const loading = ref(false)
const updating = ref(false)
const showEditDialog = ref(false)
const formRef = ref()

const editForm = ref({
  title: '',
  student_name: '',
  platform_id: undefined as number | undefined,
  price: 0,
  actual_income: 0,
  description: '',
  completed_at: '',
  tag_ids: [] as number[],
})

const rules = {
  title: [{ required: true, message: '请输入项目名称', trigger: 'blur' }],
  platform_id: [{ required: true, message: '请选择接单平台', trigger: 'change' }],
}

const loadProject = async () => {
  const id = Number(route.params.id)
  if (!id) {
    ElMessage.error('项目ID无效')
    router.back()
    return
  }
  loading.value = true
  try {
    project.value = await historicalProjectApi.get(id)
    editForm.value = {
      title: project.value.title,
      student_name: project.value.student_name || '',
      platform_id: project.value.platform_id,
      price: project.value.price || 0,
      actual_income: project.value.actual_income || 0,
      description: project.value.description || '',
      completed_at: project.value.completed_at || '',
      tag_ids: project.value.tags ? project.value.tags.map(tag => tag.id) : [],
    }
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '加载项目详情失败')
    router.back()
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

const resetForm = () => {
  if (project.value) {
    editForm.value = {
      title: project.value.title,
      student_name: project.value.student_name || '',
      platform_id: project.value.platform_id,
      price: project.value.price || 0,
      actual_income: project.value.actual_income || 0,
      description: project.value.description || '',
      completed_at: project.value.completed_at || '',
      tag_ids: project.value.tags ? project.value.tags.map(tag => tag.id) : [],
    }
  }
  formRef.value?.clearValidate()
}

const handleUpdate = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid: boolean) => {
    if (!valid) return
    if (!project.value) return
    updating.value = true
    try {
      // 更新项目基本信息
      project.value = await historicalProjectApi.update(project.value.id, editForm.value)
      
      // 更新标签
      const currentTagIds = project.value.tags ? project.value.tags.map(t => t.id) : []
      const tagsToAdd = editForm.value.tag_ids.filter(id => !currentTagIds.includes(id))
      const tagsToRemove = currentTagIds.filter(id => !editForm.value.tag_ids.includes(id))
      
      // 添加新标签
      for (const tagId of tagsToAdd) {
        try {
          await tagApi.addHistoricalProjectTag(project.value.id, tagId)
        } catch (error) {
          console.error(`添加标签 ${tagId} 失败:`, error)
        }
      }
      
      // 删除旧标签
      for (const tagId of tagsToRemove) {
        try {
          await tagApi.removeHistoricalProjectTag(project.value.id, tagId)
        } catch (error) {
          console.error(`删除标签 ${tagId} 失败:`, error)
        }
      }
      
      // 重新加载项目以获取最新标签
      await loadProject()
      ElMessage.success('更新成功')
      showEditDialog.value = false
    } catch (error: any) {
      ElMessage.error(error.response?.data?.detail || '更新失败')
    } finally {
      updating.value = false
    }
  })
}

const handleDelete = async () => {
  if (!project.value) return
  try {
    await ElMessageBox.confirm(
      `确定要删除历史项目"${project.value.title}"吗？`,
      '提示',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )
    await historicalProjectApi.delete(project.value.id)
    ElMessage.success('删除成功')
    router.push('/historical-projects')
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.response?.data?.detail || '删除失败')
    }
  }
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

onMounted(() => {
  loadPlatforms()
  loadProject()
})
</script>

<style scoped>
.historical-project-detail-page {
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

.header-actions {
  display: flex;
  gap: 12px;
}

.project-detail {
  margin-top: 20px;
}

.project-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

/* 移动端样式 */
@media (max-width: 768px) {
  .historical-project-detail-page {
    padding: 12px;
  }

  .historical-project-detail-page :deep(.el-card__header) {
    padding: 12px;
  }

  .historical-project-detail-page :deep(.el-card__body) {
    padding: 12px;
  }

  .card-header {
    flex-direction: column;
    align-items: stretch;
    gap: 10px;
  }

  .header-left {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }

  .page-title {
    font-size: 16px;
    text-align: center;
  }

  .header-actions {
    width: 100%;
    justify-content: center;
    gap: 8px;
  }

  .header-actions .el-button {
    flex: 1;
    font-size: 12px;
  }

  .project-detail {
    margin-top: 12px;
  }

  .project-detail :deep(.el-descriptions__label) {
    font-size: 12px;
    min-width: 70px;
  }

  .project-detail :deep(.el-descriptions__content) {
    font-size: 13px;
  }

  .project-tags {
    gap: 6px;
  }

  .project-tags :deep(.el-tag) {
    font-size: 11px;
  }
}

@media (max-width: 480px) {
  .historical-project-detail-page {
    padding: 8px;
  }

  .header-actions .el-button {
    font-size: 11px;
    padding: 6px 10px;
  }

  .project-detail :deep(.el-descriptions__label) {
    font-size: 11px;
    min-width: 60px;
  }

  .project-detail :deep(.el-descriptions__content) {
    font-size: 12px;
  }
}
</style>

