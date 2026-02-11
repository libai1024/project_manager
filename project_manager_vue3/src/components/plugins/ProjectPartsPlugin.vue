<template>
  <BasePluginCard
    :project-id="project.id"
    plugin-type="parts"
    title="元器件清单"
    subtitle="管理项目所需元器件及成本"
    :icon="Box"
    :icon-gradient="['#f56c6c', '#f78989']"
    card-class="parts-plugin-card"
  >
    <template #header-actions>
      <el-button
        type="primary"
        size="small"
        :icon="Plus"
        @click="handleAdd"
      >
        新增/编辑
      </el-button>
      <el-button
        size="small"
        :icon="Document"
        @click="handleExport"
        :disabled="parts.length === 0"
      >
        导出 Excel
      </el-button>
    </template>

    <ProjectPartsCard
      :project="project"
      :parts="parts"
      @add="handleAdd"
      @edit="handleEdit"
      @delete="handleDelete"
      @export="handleExport"
    />

    <!-- 编辑对话框 -->
    <ProjectPartsEditDialog
      v-model="showEditDialog"
      :project-id="project.id"
      :editing-part="editingPart"
      :editing-index="editingIndex"
      @save="handleSave"
      @cancel="handleCancel"
    />
  </BasePluginCard>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus, Document, Box } from '@element-plus/icons-vue'
import BasePluginCard from './BasePluginCard.vue'
import ProjectPartsCard from '@/components/project-detail/ProjectPartsCard.vue'
import ProjectPartsEditDialog from '@/components/project-detail/ProjectPartsEditDialog.vue'
import { projectPartApi, type ProjectPart } from '@/api/projectPart'
import type { Project } from '@/api/project'

interface Props {
  project: Project
}

const props = defineProps<Props>()

const emit = defineEmits<{
  refresh: []
}>()

const parts = ref<ProjectPart[]>([])
const showEditDialog = ref(false)
const editingPart = ref<ProjectPart | null>(null)
const editingIndex = ref(-1)

// 加载元器件清单
const loadParts = async () => {
  if (!props.project?.id) return
  try {
    const data = await projectPartApi.list(props.project.id)
    parts.value = data.map(p => ({
      ...p,
      unit_price: p.unit_price ?? 0,
      quantity: p.quantity ?? 1,
    }))
    console.log('元器件清单加载成功:', parts.value.length, '条')
  } catch (error: any) {
    console.error('加载元器件清单失败:', error)
    ElMessage.error(error.response?.data?.detail || '加载元器件清单失败')
  }
}

// 新增
const handleAdd = () => {
  console.log('新增元器件')
  editingPart.value = null
  editingIndex.value = -1
  showEditDialog.value = true
}

// 编辑
const handleEdit = (index: number, row: ProjectPart) => {
  console.log('编辑元器件:', { index, row })
  editingPart.value = { ...row }
  editingIndex.value = index
  showEditDialog.value = true
}

// 删除
const handleDelete = async (index: number, row: ProjectPart) => {
  console.log('删除元器件:', { index, row })
  
  // 如果是临时数据（未保存的），直接删除
  if (row.id < 0) {
    parts.value.splice(index, 1)
    ElMessage.success('元器件已删除')
    return
  }
  
  try {
    await projectPartApi.delete(row.id)
    parts.value.splice(index, 1)
    ElMessage.success('元器件已删除')
    // 删除后刷新列表
    await loadParts()
  } catch (error: any) {
    console.error('删除元器件失败:', error)
    ElMessage.error(error.response?.data?.detail || '删除失败')
  }
}

// 导出
const handleExport = async () => {
  if (parts.value.length === 0) {
    ElMessage.warning('没有可导出的数据')
    return
  }

  try {
    // 这里可以调用导出API或使用前端导出
    // 暂时使用简单的CSV导出
    const headers = ['功能模块名称', '核心元器件', '主要功能', '单价', '数量', '小计', '购买链接']
    const rows = parts.value.map(p => [
      p.module_name || '',
      p.core_component || '',
      p.remark || '',
      p.unit_price || 0,
      p.quantity || 0,
      (Number(p.unit_price || 0) * Number(p.quantity || 0)).toFixed(2),
      p.purchase_link || ''
    ])

    const csvContent = [
      headers.join(','),
      ...rows.map(row => row.map(cell => `"${cell}"`).join(','))
    ].join('\n')

    const blob = new Blob(['\ufeff' + csvContent], { type: 'text/csv;charset=utf-8;' })
    const link = document.createElement('a')
    const url = URL.createObjectURL(blob)
    link.href = url
    link.download = `${props.project.title || '项目'}_元器件清单_${new Date().toISOString().split('T')[0]}.csv`
    link.click()
    URL.revokeObjectURL(url)
    
    ElMessage.success('导出成功')
  } catch (error) {
    console.error('导出失败:', error)
    ElMessage.error('导出失败')
  }
}

// 保存
const handleSave = async () => {
  console.log('保存元器件清单，刷新列表')
  await loadParts()
  emit('refresh')
}

// 取消
const handleCancel = () => {
  editingPart.value = null
  editingIndex.value = -1
}

onMounted(() => {
  loadParts()
})
</script>

<style scoped>
.parts-plugin-card {
  /* 可以添加特定样式 */
}
</style>

