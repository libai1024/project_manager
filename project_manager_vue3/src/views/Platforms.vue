<template>
  <div class="platforms-page">
    <el-card class="platforms-card">
      <template #header>
        <div class="card-header">
          <span class="page-title">平台管理</span>
          <el-button type="primary" @click="showCreateDialog = true" class="add-btn">
            <el-icon><Plus /></el-icon>
            新建平台
          </el-button>
        </div>
      </template>

      <div class="table-wrapper">
        <el-table
          :data="platforms"
          style="width: 100%"
          v-loading="loading"
          :scroll="{ x: 'max-content' }"
          stripe
          class="platforms-table"
        >
          <el-table-column prop="id" label="ID" min-width="60" align="center" />
          <el-table-column prop="name" label="平台名称" min-width="150">
            <template #default="{ row }">
              <div class="platform-name-cell">
                <el-icon class="platform-icon"><PlatformIcon /></el-icon>
                <span>{{ row.name }}</span>
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip />
          <el-table-column prop="created_at" label="创建时间" min-width="180">
            <template #default="{ row }">
              <div class="time-cell">
                <el-icon :size="14"><Clock /></el-icon>
                <span>{{ formatDateTime(row.created_at) }}</span>
              </div>
            </template>
          </el-table-column>
          <el-table-column label="操作" min-width="150" fixed="right" align="center">
            <template #default="{ row }">
              <div class="action-buttons">
              <el-button
                type="primary"
                size="small"
                  :icon="Edit"
                @click="handleEdit(row)"
              >
                编辑
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

    <!-- 创建/编辑平台对话框 -->
    <el-dialog
      v-model="showCreateDialog"
      :title="editingPlatform ? '编辑平台' : '新建平台'"
      width="500px"
      @close="resetForm"
    >
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="100px"
      >
        <el-form-item label="平台名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入平台名称" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input
            v-model="form.description"
            type="textarea"
            :rows="3"
            placeholder="请输入平台描述"
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSubmit">
          确定
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import { Plus, Platform as PlatformIcon, Clock, Edit, Delete } from '@element-plus/icons-vue'
import { usePlatform } from '@/composables/usePlatform'
import type { Platform, PlatformCreate, PlatformUpdate } from '@/api/platform'

const formRef = ref<FormInstance>()
const submitting = ref(false)
const showCreateDialog = ref(false)
const editingPlatform = ref<Platform | null>(null)

// 使用Composable
const {
  loading,
  platforms,
  loadPlatforms,
  createPlatform,
  updatePlatform,
  deletePlatform,
} = usePlatform()

const form = reactive<PlatformCreate>({
  name: '',
  description: '',
})

const rules: FormRules = {
  name: [{ required: true, message: '请输入平台名称', trigger: 'blur' }],
}

const resetForm = () => {
  formRef.value?.resetFields()
  editingPlatform.value = null
  Object.assign(form, {
    name: '',
    description: '',
  })
}

const handleEdit = (platform: Platform) => {
  editingPlatform.value = platform
  Object.assign(form, {
    name: platform.name,
    description: platform.description || '',
  })
  showCreateDialog.value = true
}

const handleSubmit = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (valid) {
      submitting.value = true
      try {
        if (editingPlatform.value) {
          await updatePlatform(editingPlatform.value.id, form as PlatformUpdate)
        } else {
          await createPlatform(form)
        }
        showCreateDialog.value = false
        resetForm()
      } catch (error) {
        // 错误已在Service层处理
      } finally {
        submitting.value = false
      }
    }
  })
}

const handleDelete = async (platform: Platform) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除平台"${platform.name}"吗？`,
      '提示',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )
    
    await deletePlatform(platform.id)
  } catch (error: any) {
    if (error !== 'cancel') {
      // 错误已在Service层处理
    }
  }
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

onMounted(() => {
  loadPlatforms()
})
</script>

<style scoped>
.platforms-page {
  padding: 20px;
  background: #f5f7fa;
  min-height: calc(100vh - 60px);
}

.platforms-card {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
  font-weight: 600;
  color: #303133;
}

.page-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.add-btn {
  color: #fff;
}

.table-wrapper {
  overflow-x: auto;
  width: 100%;
}

.platforms-table {
  margin-top: 16px;
}

.platforms-table :deep(.el-table__row) {
  transition: background-color 0.2s;
}

.platforms-table :deep(.el-table__row:hover) {
  background: #f5f7fa;
}

.platform-name-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}

.platform-icon {
  color: #409eff;
  font-size: 16px;
}

.time-cell {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #909399;
  font-size: 13px;
}

.action-buttons {
  display: flex;
  gap: 8px;
  justify-content: center;
}

/* 移动端样式 */
@media (max-width: 768px) {
  .platforms-page {
    padding: 12px;
    min-height: auto;
  }

  .platforms-card :deep(.el-card__body) {
    padding: 12px !important;
  }

  .card-header {
    flex-direction: column;
    align-items: stretch;
    gap: 8px;
  }

  .page-title {
    font-size: 15px;
    text-align: center;
  }

  .add-btn {
    width: 100%;
  }

  .table-wrapper {
    margin: 0 -12px;
    padding: 0 12px;
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
  }

  .platforms-table {
    margin-top: 0;
    min-width: 500px;
  }

  .platforms-table :deep(.el-table__cell) {
    padding: 8px 4px !important;
    font-size: 12px !important;
  }

  .platform-name-cell {
    font-size: 12px;
  }

  .platform-icon {
    font-size: 14px;
  }

  .time-cell {
    font-size: 11px;
  }

  .action-buttons {
    flex-wrap: nowrap;
    gap: 4px;
  }

  .action-buttons .el-button {
    padding: 5px 8px !important;
    font-size: 11px !important;
  }

  /* 对话框样式 */
  .platforms-page :deep(.el-dialog) {
    width: 94% !important;
    margin-top: 5vh !important;
  }

  .platforms-page :deep(.el-dialog__header) {
    padding: 12px !important;
  }

  .platforms-page :deep(.el-dialog__body) {
    padding: 12px !important;
  }

  .platforms-page :deep(.el-dialog__footer) {
    padding: 12px !important;
    display: flex;
    flex-direction: column;
    gap: 8px;
  }

  .platforms-page :deep(.el-dialog__footer .el-button) {
    width: 100%;
    margin: 0;
  }

  .platforms-page :deep(.el-form-item__label) {
    font-size: 12px;
    float: none;
    text-align: left;
    padding-bottom: 4px;
    width: 100% !important;
  }

  .platforms-page :deep(.el-form-item__content) {
    margin-left: 0 !important;
  }
}

@media (max-width: 480px) {
  .platforms-page {
    padding: 8px;
  }

  .platforms-table {
    min-width: 400px;
  }
}
</style>
