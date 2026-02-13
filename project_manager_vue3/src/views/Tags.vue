<template>
  <div class="tags-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>标签管理</span>
          <el-button type="primary" :icon="Plus" @click="showCreateDialog = true">创建标签</el-button>
        </div>
      </template>

      <!-- 筛选区域 -->
      <div class="filter-section">
        <el-input
          v-model="searchKeyword"
          placeholder="搜索标签名称"
          :prefix-icon="Search"
          clearable
          style="width: 300px"
          @input="handleSearch"
        />
        <el-checkbox v-model="showCommonOnly" @change="loadTags">仅显示常用标签</el-checkbox>
      </div>

      <!-- 标签列表 -->
      <el-table :data="filteredTags" v-loading="loading" style="margin-top: 20px">
        <el-table-column prop="name" label="标签名称" min-width="150">
          <template #default="{ row }">
            <el-tag
              :style="{ backgroundColor: row.color, borderColor: row.color, color: '#fff' }"
              effect="dark"
              round
            >
              {{ row.name }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="color" label="颜色" width="100">
          <template #default="{ row }">
            <div class="color-preview" :style="{ backgroundColor: row.color }"></div>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip />
        <el-table-column prop="is_common" label="常用标签" width="100" align="center">
          <template #default="{ row }">
            <el-tag v-if="row.is_common" type="success" size="small">是</el-tag>
            <el-tag v-else type="info" size="small">否</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="usage_count" label="使用次数" width="100" align="center" sortable />
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button
              type="primary"
              size="small"
              :icon="Edit"
              @click="handleEdit(row)"
              :disabled="!canEdit(row)"
            >
              编辑
            </el-button>
            <el-button
              type="danger"
              size="small"
              :icon="Delete"
              @click="handleDelete(row)"
              :disabled="!canDelete(row)"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 创建/编辑对话框 -->
    <el-dialog
      v-model="showEditDialog"
      :title="editingTag ? '编辑标签' : '创建标签'"
      width="500px"
      @close="resetForm"
    >
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="100px"
      >
        <el-form-item label="标签名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入标签名称" />
        </el-form-item>
        <el-form-item label="标签颜色" prop="color">
          <el-color-picker v-model="form.color" show-alpha />
        </el-form-item>
        <el-form-item label="描述">
          <el-input
            v-model="form.description"
            type="textarea"
            :rows="3"
            placeholder="请输入标签描述（可选）"
          />
        </el-form-item>
        <el-form-item label="常用标签">
          <el-switch v-model="form.is_common" />
          <span style="margin-left: 10px; color: #909399; font-size: 12px;">
            常用标签会显示在标签选择器的顶部
          </span>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showEditDialog = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Edit, Delete, Search } from '@element-plus/icons-vue'
import { tagApi, type Tag, type TagCreate, type TagUpdate } from '@/api/tag'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()

const loading = ref(false)
const submitting = ref(false)
const tags = ref<Tag[]>([])
const searchKeyword = ref('')
const showCommonOnly = ref(false)
const showCreateDialog = ref(false)
const showEditDialog = ref(false)
const editingTag = ref<Tag | null>(null)
const formRef = ref()

const form = ref<TagCreate | TagUpdate>({
  name: '',
  color: '#409eff',
  description: '',
  is_common: false,
})

const rules = {
  name: [{ required: true, message: '请输入标签名称', trigger: 'blur' }],
  color: [{ required: true, message: '请选择标签颜色', trigger: 'change' }],
}

const filteredTags = computed(() => {
  let result = tags.value

  // 搜索过滤
  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    result = result.filter(tag =>
      tag.name.toLowerCase().includes(keyword) ||
      (tag.description && tag.description.toLowerCase().includes(keyword))
    )
  }

  // 常用标签过滤
  if (showCommonOnly.value) {
    result = result.filter(tag => tag.is_common)
  }

  return result
})

const canEdit = (tag: Tag) => {
  // 用户可以编辑自己创建的标签，管理员可以编辑所有标签
  return userStore.isAdmin || tag.user_id === userStore.userInfo?.id
}

const canDelete = (tag: Tag) => {
  // 用户可以删除自己创建的标签，管理员可以删除所有标签
  // 但使用次数大于0的标签需要谨慎删除
  return (userStore.isAdmin || tag.user_id === userStore.userInfo?.id) && tag.usage_count === 0
}

const loadTags = async () => {
  loading.value = true
  try {
    tags.value = await tagApi.list(true)
  } catch (error: any) {
    console.error('加载标签失败:', error)
    ElMessage.error(error.response?.data?.detail || '加载标签列表失败')
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  // 搜索由 computed 属性自动处理
}

const handleEdit = (tag: Tag) => {
  editingTag.value = tag
  form.value = {
    name: tag.name,
    color: tag.color,
    description: tag.description || '',
    is_common: tag.is_common,
  }
  showEditDialog.value = true
}

const handleDelete = async (tag: Tag) => {
  if (tag.usage_count > 0) {
    ElMessage.warning('该标签正在使用中，无法删除')
    return
  }

  try {
    await ElMessageBox.confirm(
      `确定要删除标签"${tag.name}"吗？`,
      '提示',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )
    await tagApi.delete(tag.id)
    ElMessage.success('删除成功')
    await loadTags()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.response?.data?.detail || '删除失败')
    }
  }
}

const handleSubmit = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid: boolean) => {
    if (!valid) return
    submitting.value = true
    try {
      if (editingTag.value) {
        // 更新标签
        await tagApi.update(editingTag.value.id, form.value as TagUpdate)
        ElMessage.success('更新成功')
      } else {
        // 创建标签
        await tagApi.create(form.value as TagCreate)
        ElMessage.success('创建成功')
      }
      showEditDialog.value = false
      showCreateDialog.value = false
      await loadTags()
    } catch (error: any) {
      ElMessage.error(error.response?.data?.detail || (editingTag.value ? '更新失败' : '创建失败'))
    } finally {
      submitting.value = false
    }
  })
}

const resetForm = () => {
  editingTag.value = null
  form.value = {
    name: '',
    color: '#409eff',
    description: '',
    is_common: false,
  }
  formRef.value?.clearValidate()
}

const formatDate = (dateStr: string) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN')
}

// 监听创建对话框
watch(showCreateDialog, (newVal) => {
  if (newVal) {
    resetForm()
    showEditDialog.value = true
  }
})

onMounted(() => {
  loadTags()
})
</script>

<style scoped>
.tags-page {
  padding: 20px;
}

.tags-page :deep(.el-card__body) {
  padding: 16px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.filter-section {
  display: flex;
  align-items: center;
  gap: 20px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.color-preview {
  width: 30px;
  height: 30px;
  border-radius: 4px;
  border: 1px solid #dcdfe6;
}

/* 移动端样式 */
@media (max-width: 768px) {
  .tags-page {
    padding: 12px;
  }

  .tags-page :deep(.el-card__body) {
    padding: 12px !important;
  }

  .card-header {
    flex-direction: column;
    align-items: stretch;
    gap: 8px;
  }

  .card-header span {
    font-size: 15px;
    text-align: center;
  }

  .card-header .el-button {
    width: 100%;
  }

  .filter-section {
    flex-direction: column;
    align-items: stretch;
    gap: 8px;
    margin-bottom: 12px;
  }

  .filter-section .el-input {
    width: 100% !important;
  }

  .filter-section .el-checkbox {
    margin-top: 4px;
  }

  /* 表格优化 */
  .tags-page :deep(.el-table) {
    font-size: 12px !important;
    display: block;
    overflow-x: auto;
    white-space: nowrap;
    -webkit-overflow-scrolling: touch;
  }

  .tags-page :deep(.el-table__cell) {
    padding: 8px 4px !important;
  }

  .tags-page :deep(.el-tag) {
    font-size: 11px !important;
  }

  .color-preview {
    width: 24px;
    height: 24px;
  }

  /* 隐藏不重要的列 */
  .tags-page :deep(.el-table__body) .el-table__cell:nth-child(5),
  .tags-page :deep(.el-table__header) .el-table__cell:nth-child(5) {
    display: none;
  }

  /* 操作按钮 */
  .tags-page :deep(.el-table) .el-button {
    padding: 4px 8px !important;
    font-size: 11px !important;
  }

  /* 对话框样式 */
  .tags-page :deep(.el-dialog) {
    width: 94% !important;
    margin-top: 5vh !important;
  }

  .tags-page :deep(.el-dialog__header) {
    padding: 12px !important;
  }

  .tags-page :deep(.el-dialog__body) {
    padding: 12px !important;
  }

  .tags-page :deep(.el-dialog__footer) {
    padding: 12px !important;
    display: flex;
    flex-direction: column;
    gap: 8px;
  }

  .tags-page :deep(.el-dialog__footer .el-button) {
    width: 100%;
    margin: 0;
  }

  .tags-page :deep(.el-form-item__label) {
    font-size: 12px;
    float: none;
    text-align: left;
    padding-bottom: 4px;
    width: 100% !important;
  }

  .tags-page :deep(.el-form-item__content) {
    margin-left: 0 !important;
  }
}

@media (max-width: 480px) {
  .tags-page {
    padding: 8px;
  }

  .tags-page :deep(.el-table__cell) {
    padding: 6px 2px !important;
  }

  .tags-page :deep(.el-tag) {
    font-size: 10px !important;
    padding: 0 4px !important;
  }

  .color-preview {
    width: 20px;
    height: 20px;
  }
}
</style>

