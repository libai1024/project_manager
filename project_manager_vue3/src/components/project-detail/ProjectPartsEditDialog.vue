<template>
  <el-dialog
    :model-value="modelValue"
    @update:model-value="$emit('update:modelValue', $event)"
    :title="editingIndex >= 0 ? '编辑元器件' : '新增元器件'"
    :width="dialogWidth"
    top="3vh"
    :close-on-click-modal="false"
    class="parts-edit-dialog"
    destroy-on-close
    align-center
  >
    <div class="parts-edit-content">
      <div class="parts-edit-tips">
        <el-alert
          type="info"
          :closable="false"
          show-icon
          class="modern-alert"
        >
          <template #title>
            <div class="alert-content">
              <el-icon class="alert-icon"><InfoFilled /></el-icon>
              <span>直接点击单元格即可编辑，<span class="required-hint">必填字段</span>已用红色星号标记</span>
            </div>
          </template>
        </el-alert>
      </div>
      
      <!-- 校验结果提示 -->
      <div v-if="validationErrors.length > 0" class="validation-errors">
        <el-alert
          type="error"
          :closable="false"
          show-icon
        >
          <template #title>
            <div>
              <strong>发现 {{ validationErrors.length }} 个错误：</strong>
              <ul class="error-list">
                <li v-for="(error, index) in validationErrors" :key="index">
                  第 {{ error.row + 1 }} 行：{{ error.message }}
                </li>
              </ul>
            </div>
          </template>
        </el-alert>
      </div>
      
      <!-- 可编辑表格 -->
      <div class="parts-table-wrapper">
        <el-table
          ref="editingTableRef"
          :data="editingParts"
          border
          stripe
          class="editing-parts-table"
          :height="tableHeight"
        >
          <el-table-column type="index" label="#" :width="responsiveColumnWidths.index" align="center" fixed="left" />
          
          <el-table-column label="功能模块名称" :width="responsiveColumnWidths.moduleName" show-overflow-tooltip>
            <template #default="{ row, $index }">
              <el-input
                v-model="row.module_name"
                placeholder="请输入功能模块名称"
                size="small"
                clearable
                @blur="validatePartRow($index)"
              />
            </template>
          </el-table-column>
          
          <el-table-column label="核心元器件" :width="responsiveColumnWidths.coreComponent" show-overflow-tooltip>
            <template #header>
              <span class="required-header">核心元器件 <span class="required-star">*</span></span>
            </template>
            <template #default="{ row, $index }">
              <div class="cell-with-error">
                <el-input
                  v-model="row.core_component"
                  placeholder="请输入核心元器件名称"
                  size="small"
                  clearable
                  :class="{ 'cell-error': getCellError($index, 1) }"
                  @blur="validatePartRow($index)"
                />
                <span v-if="getCellError($index, 1)" class="cell-error-icon" title="元器件名称不能为空">⚠️</span>
              </div>
            </template>
          </el-table-column>
          
          <el-table-column label="主要功能（备注）" :width="responsiveColumnWidths.remark" show-overflow-tooltip>
            <template #default="{ row, $index }">
              <el-input
                v-model="row.remark"
                type="textarea"
                :rows="2"
                placeholder="请输入主要功能描述"
                size="small"
                @blur="validatePartRow($index)"
              />
            </template>
          </el-table-column>
          
          <el-table-column label="单价" :width="responsiveColumnWidths.unitPrice" align="right">
            <template #header>
              <span class="required-header">单价 <span class="required-star">*</span></span>
            </template>
            <template #default="{ row, $index }">
              <div class="cell-with-error">
                <el-input-number
                  v-model="row.unit_price"
                  :min="0"
                  :precision="2"
                  :step="0.01"
                  :controls-position="'right'"
                  :class="{ 'cell-error': getCellError($index, 3) }"
                  @blur="validatePartRow($index)"
                  size="small"
                  style="width: 100%"
                />
                <span v-if="getCellError($index, 3)" class="cell-error-icon" title="单价必须大于0">⚠️</span>
              </div>
            </template>
          </el-table-column>
          
          <el-table-column label="数量" :width="responsiveColumnWidths.quantity" align="right">
            <template #header>
              <span class="required-header">数量 <span class="required-star">*</span></span>
            </template>
            <template #default="{ row, $index }">
              <div class="cell-with-error">
                <el-input-number
                  v-model="row.quantity"
                  :min="1"
                  :controls-position="'right'"
                  :class="{ 'cell-error': getCellError($index, 4) }"
                  @blur="validatePartRow($index)"
                  size="small"
                  style="width: 100%"
                />
                <span v-if="getCellError($index, 4)" class="cell-error-icon" title="数量必须大于0">⚠️</span>
              </div>
            </template>
          </el-table-column>
          
          <el-table-column label="购买链接" :width="responsiveColumnWidths.purchaseLink" show-overflow-tooltip>
            <template #default="{ row, $index }">
              <el-input
                v-model="row.purchase_link"
                placeholder="请输入购买链接"
                size="small"
                clearable
                @blur="validatePartRow($index)"
              />
            </template>
          </el-table-column>
          
          <el-table-column label="图片链接" :width="responsiveColumnWidths.imageUrl" show-overflow-tooltip>
            <template #default="{ row, $index }">
              <el-input
                v-model="row.image_url"
                placeholder="请输入图片链接"
                size="small"
                clearable
                @blur="validatePartRow($index)"
              />
            </template>
          </el-table-column>
          
          <el-table-column label="操作" :width="responsiveColumnWidths.action" align="center" fixed="right">
            <template #default="{ $index }">
              <el-button
                type="danger"
                text
                size="small"
                :icon="Delete"
                @click="removeEditingPartRow($index)"
              >
                删除
              </el-button>
            </template>
          </el-table-column>
        </el-table>
        
        <div v-if="editingParts.length === 0" class="parts-empty">
          <el-empty description="暂无数据，点击下方按钮添加" :image-size="80" />
        </div>
      </div>

      <div class="parts-edit-actions">
        <el-button type="primary" @click="addEditingPartRow" :icon="Plus">
          新增一行
        </el-button>
        <el-button type="warning" @click="validateAllParts" :icon="CircleCheck">
          校验数据
        </el-button>
        <el-button type="danger" plain @click="clearAllRows" :icon="Delete">
          清空所有
        </el-button>
      </div>
    </div>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleCancel" size="default">取消</el-button>
        <el-button type="warning" @click="validateAllParts" :icon="CircleCheck" size="default">
          校验
        </el-button>
        <el-button 
          type="primary" 
          @click="handleSave" 
          :loading="saving"
          :disabled="validationErrors.length > 0"
          :icon="saving ? null : Check"
          size="default"
        >
          {{ saving ? '保存中...' : '保存' }}
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, computed, watch, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Plus,
  Delete,
  CircleCheck,
  Check,
  InfoFilled
} from '@element-plus/icons-vue'
import type { ProjectPart, ProjectPartCreate, ProjectPartUpdate } from '@/api/projectPart'
import { projectPartApi } from '@/api/projectPart'

interface Props {
  modelValue: boolean
  projectId: number
  editingPart?: ProjectPart | null
  editingIndex?: number
}

const props = withDefaults(defineProps<Props>(), {
  editingPart: null,
  editingIndex: -1
})

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  'save': []
  'cancel': []
}>()

// 字段宽度配置
const columnWidths = {
  index: 60,
  moduleName: 160,
  coreComponent: 160,
  remark: 220,
  unitPrice: 130,
  quantity: 100,
  purchaseLink: 220,
  imageUrl: 220,
  action: 100
}

const editingParts = ref<ProjectPart[]>([])
const editingTableRef = ref()
const saving = ref(false)
const validationErrors = ref<Array<{ row: number; col: number; message: string }>>([])

// 计算弹窗宽度
const dialogWidth = computed(() => {
  const totalColumnsWidth = Object.values(columnWidths).reduce((sum, width) => sum + width, 0)
  const minWidth = 1200
  const maxWidth = Math.min(window.innerWidth * 0.95, 1600)
  const calculatedWidth = Math.max(minWidth, Math.min(totalColumnsWidth + 100, maxWidth))
  return `${calculatedWidth}px`
})

// 计算表格高度
const tableHeight = computed(() => {
  return Math.max(350, window.innerHeight * 0.9 - 320)
})

// 响应式列宽
const responsiveColumnWidths = computed(() => {
  const dialogWidthValue = parseInt(dialogWidth.value)
  const scale = Math.min(1, dialogWidthValue / 1400)
  
  return {
    index: columnWidths.index,
    moduleName: Math.floor(columnWidths.moduleName * scale) || 140,
    coreComponent: Math.floor(columnWidths.coreComponent * scale) || 140,
    remark: Math.floor(columnWidths.remark * scale) || 180,
    unitPrice: columnWidths.unitPrice,
    quantity: columnWidths.quantity,
    purchaseLink: Math.floor(columnWidths.purchaseLink * scale) || 180,
    imageUrl: Math.floor(columnWidths.imageUrl * scale) || 180,
    action: columnWidths.action
  }
})

// 加载现有元器件列表
const loadExistingParts = async () => {
  try {
    const data = await projectPartApi.list(props.projectId)
    return data.map(p => ({
      ...p,
      unit_price: p.unit_price ?? 0,
      quantity: p.quantity ?? 1,
    }))
  } catch (error) {
    console.error('加载现有元器件失败:', error)
    return []
  }
}

// 监听编辑模式变化
watch(() => [props.modelValue, props.editingPart, props.editingIndex], async ([visible, part, index]) => {
  if (visible) {
    console.log('编辑对话框打开:', { 
      part, 
      index, 
      editingIndex: props.editingIndex,
      hasPart: !!part,
      partId: part?.id 
    })
    
    // 判断是编辑模式还是新增模式
    // 编辑模式：editingPart 不为 null 且 editingIndex >= 0
    const isEditMode = part !== null && part !== undefined && index !== undefined && index >= 0
    
    if (isEditMode) {
      // 编辑模式：加载要编辑的元器件
      editingParts.value = [{ ...part }]
      console.log('编辑模式，加载元器件:', editingParts.value)
    } else {
      // 新增模式：加载现有元器件列表，方便用户在现有基础上添加
      const existingParts = await loadExistingParts()
      editingParts.value = existingParts.length > 0 ? [...existingParts] : []
      console.log('新增模式，加载现有元器件:', editingParts.value.length, '条')
    }
    validationErrors.value = []
  } else {
    // 对话框关闭时清空数据
    editingParts.value = []
    validationErrors.value = []
  }
}, { immediate: true })

// 添加编辑行
const addEditingPartRow = () => {
  const draft: ProjectPart = {
    id: Date.now() * -1, // 使用负数作为临时ID，表示新创建的
    project_id: props.projectId,
    module_name: '',
    core_component: '',
    remark: '',
    unit_price: 0,
    quantity: 1,
    purchase_link: '',
    image_url: '',
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  }
  editingParts.value.push(draft)
  console.log('添加新行，当前行数:', editingParts.value.length)
}

// 删除编辑行
const removeEditingPartRow = (index: number) => {
  editingParts.value.splice(index, 1)
}

// 验证元器件行
const validatePartRow = (index: number) => {
  const row = editingParts.value[index]
  if (!row) return
  if (row.quantity < 1) {
    row.quantity = 1
  }
  if (row.unit_price < 0) {
    row.unit_price = 0
  }
  validationErrors.value = validationErrors.value.filter(err => err.row !== index)
}

// 获取单元格错误状态
const getCellError = (rowIndex: number, colIndex: number): boolean => {
  return validationErrors.value.some(err => err.row === rowIndex && err.col === colIndex)
}

// 校验所有元器件数据
const validateAllParts = () => {
  validationErrors.value = []
  
  editingParts.value.forEach((row, rowIndex) => {
    if (!row.core_component || row.core_component.trim() === '') {
      validationErrors.value.push({
        row: rowIndex,
        col: 1,
        message: '核心元器件名称不能为空'
      })
    }
    
    if (row.unit_price === null || row.unit_price === undefined || row.unit_price <= 0) {
      validationErrors.value.push({
        row: rowIndex,
        col: 3,
        message: '单价必须大于0'
      })
    }
    
    if (!row.quantity || row.quantity < 1) {
      validationErrors.value.push({
        row: rowIndex,
        col: 4,
        message: '数量必须大于0'
      })
    }
  })
  
  if (validationErrors.value.length === 0) {
    ElMessage.success('校验通过，所有数据格式正确')
  } else {
    ElMessage.warning(`发现 ${validationErrors.value.length} 个错误，请修正后保存`)
    nextTick(() => {
      const firstError = validationErrors.value[0]
      if (firstError && editingTableRef.value) {
        editingTableRef.value.setScrollTop(firstError.row * 50)
      }
    })
  }
}

// 保存元器件
const handleSave = async () => {
  validateAllParts()
  if (validationErrors.value.length > 0) {
    ElMessage.warning('请先修正所有错误后再保存')
    return
  }
  
  const invalidRows = editingParts.value.filter(p => !p.core_component || !p.unit_price || p.unit_price <= 0 || !p.quantity || p.quantity < 1)
  if (invalidRows.length > 0) {
    ElMessage.warning('请填写核心元器件、单价和数量')
    return
  }

  saving.value = true
  try {
    const validParts = editingParts.value.filter(p => 
      p.core_component && 
      p.core_component.trim() !== '' && 
      p.unit_price && 
      p.unit_price > 0 && 
      p.quantity && 
      p.quantity >= 1
    )
    
    if (validParts.length === 0) {
      ElMessage.warning('请至少添加一条有效的元器件记录')
      saving.value = false
      return
    }

    console.log('准备保存元器件:', {
      total: validParts.length,
      toUpdate: validParts.filter(p => p.id > 0).length,
      toCreate: validParts.filter(p => p.id < 0).length,
      allParts: validParts.map(p => ({ id: p.id, component: p.core_component }))
    })

    // 分离需要更新的和需要创建的
    // id > 0: 已存在的元器件，需要更新
    // id < 0: 新创建的元器件（临时ID），需要创建
    const partsToUpdate = validParts.filter(p => p.id > 0)
    const partsToCreate = validParts.filter(p => p.id < 0)

    // 更新已存在的元器件
    for (const part of partsToUpdate) {
      console.log('更新元器件:', part.id, part.core_component)
      const updateData: ProjectPartUpdate = {
        module_name: part.module_name || undefined,
        core_component: part.core_component,
        remark: part.remark || undefined,
        unit_price: part.unit_price,
        quantity: part.quantity,
        purchase_link: part.purchase_link || undefined,
        image_url: part.image_url || undefined,
      }
      await projectPartApi.update(part.id, updateData)
    }

    // 创建新的元器件
    if (partsToCreate.length > 0) {
      console.log('创建新元器件:', partsToCreate.length, '个')
      const createDataList: ProjectPartCreate[] = partsToCreate.map(p => ({
        module_name: p.module_name || '',
        core_component: p.core_component,
        remark: p.remark || undefined,
        unit_price: p.unit_price,
        quantity: p.quantity,
        purchase_link: p.purchase_link || undefined,
        image_url: p.image_url || undefined,
      }))
      await projectPartApi.createBatch(props.projectId, createDataList)
    }

    console.log('元器件清单保存成功')
    ElMessage.success('元器件清单保存成功')
    emit('save')
    emit('update:modelValue', false)
  } catch (error: any) {
    console.error('保存元器件清单失败:', error)
    ElMessage.error(error.response?.data?.detail || '保存元器件清单失败')
  } finally {
    saving.value = false
  }
}

// 取消编辑
const handleCancel = () => {
  emit('cancel')
  emit('update:modelValue', false)
}

// 清空所有行
const clearAllRows = () => {
  ElMessageBox.confirm(
    '确定要清空所有元器件数据吗？此操作不可恢复。',
    '确认清空',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    }
  ).then(() => {
    editingParts.value = []
    ElMessage.success('已清空')
  }).catch(() => {})
}
</script>

<style scoped>
/* 元器件编辑对话框样式 */
.parts-edit-dialog {
  .el-dialog {
    max-width: 95vw;
    margin: 3vh auto;
    border-radius: 8px;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12);
  }
  
  .el-dialog__header {
    padding: 20px 24px;
    border-bottom: 1px solid #ebeef5;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 8px 8px 0 0;
    
    .el-dialog__title {
      color: #fff;
      font-weight: 600;
      font-size: 18px;
    }
    
    .el-dialog__headerbtn {
      .el-dialog__close {
        color: #fff;
        font-size: 20px;
        
        &:hover {
          color: #f0f0f0;
        }
      }
    }
  }
  
  .el-dialog__body {
    padding: 24px;
    max-height: calc(90vh - 140px);
    overflow: hidden;
    display: flex;
    flex-direction: column;
    background: #fafbfc;
  }
  
  .el-dialog__footer {
    padding: 16px 24px;
    border-top: 1px solid #ebeef5;
    background: #fff;
    border-radius: 0 0 8px 8px;
  }
}

.parts-edit-content {
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow: hidden;
  gap: 16px;
}

.parts-edit-tips {
  flex-shrink: 0;
  
  .modern-alert {
    border-radius: 6px;
    border: none;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
    
    .alert-content {
      display: flex;
      align-items: center;
      gap: 8px;
      
      .alert-icon {
        font-size: 18px;
        color: #409eff;
      }
      
      .required-hint {
        color: #f56c6c;
        font-weight: 600;
      }
    }
  }
}

.validation-errors {
  flex-shrink: 0;
  
  .el-alert {
    border-radius: 6px;
    border: 1px solid #fde2e2;
    background: #fef0f0;
  }
}

.parts-table-wrapper {
  flex: 1;
  overflow: hidden;
  min-height: 0;
  display: flex;
  flex-direction: column;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  padding: 8px;
}

.editing-parts-table {
  flex: 1;
  overflow: auto;
  border-radius: 6px;
  
  :deep(.el-table__header-wrapper) {
    .el-table__header {
      th {
        background: linear-gradient(135deg, #f5f7fa 0%, #e9ecef 100%);
        color: #303133;
        font-weight: 600;
        padding: 12px 8px;
        border-bottom: 2px solid #dcdfe6;
        
        .required-header {
          display: flex;
          align-items: center;
          gap: 4px;
          
          .required-star {
            color: #f56c6c;
            font-weight: 700;
            font-size: 14px;
          }
        }
      }
    }
  }
  
  :deep(.el-table__body-wrapper) {
    overflow-x: auto;
    overflow-y: auto;
    
    .el-table__body {
      tr {
        transition: background-color 0.2s;
        
        &:hover {
          background-color: #f5f9ff;
        }
        
        td {
          padding: 12px 8px;
          
          .cell {
            padding: 0;
          }
        }
      }
    }
  }
  
  :deep(.cell-error .el-input__wrapper),
  :deep(.cell-error .el-input-number) {
    border-color: #f56c6c;
    box-shadow: 0 0 0 1px #f56c6c inset;
    background-color: #fff5f5;
  }
  
  :deep(.el-input),
  :deep(.el-input-number) {
    .el-input__wrapper {
      border-radius: 4px;
      transition: all 0.2s;
      
      &:hover {
        box-shadow: 0 0 0 1px #c0c4cc inset;
      }
      
      &.is-focus {
        box-shadow: 0 0 0 1px #409eff inset;
      }
    }
  }
  
  :deep(.el-textarea) {
    .el-textarea__inner {
      border-radius: 4px;
      transition: all 0.2s;
      
      &:hover {
        border-color: #c0c4cc;
      }
      
      &:focus {
        border-color: #409eff;
      }
    }
  }
}

.cell-with-error {
  display: flex;
  align-items: center;
  gap: 6px;
  width: 100%;
  padding: 4px 0;
}

.cell-with-error .el-input,
.cell-with-error .el-input-number {
  flex: 1;
}

.cell-error-icon {
  color: #f56c6c;
  font-size: 16px;
  flex-shrink: 0;
  line-height: 1;
  animation: shake 0.3s;
}

@keyframes shake {
  0%, 100% { transform: translateX(0); }
  25% { transform: translateX(-4px); }
  75% { transform: translateX(4px); }
}

.parts-empty {
  padding: 60px 40px;
  text-align: center;
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: #fafbfc;
  border-radius: 6px;
}

.parts-edit-actions {
  display: flex;
  gap: 12px;
  padding: 16px;
  background: linear-gradient(135deg, #f5f7fa 0%, #e9ecef 100%);
  border-radius: 8px;
  flex-wrap: wrap;
  flex-shrink: 0;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  
  .el-button {
    flex: 1;
    min-width: 140px;
    height: 40px;
    font-weight: 500;
    border-radius: 6px;
    transition: all 0.3s;
    
    &:hover {
      transform: translateY(-2px);
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    }
    
    &.el-button--primary {
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      border: none;
      
      &:hover {
        background: linear-gradient(135deg, #5568d3 0%, #6a3f8f 100%);
      }
    }
  }
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  
  .el-button {
    min-width: 100px;
    height: 36px;
    border-radius: 6px;
    font-weight: 500;
    transition: all 0.3s;
    
    &:hover {
      transform: translateY(-1px);
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.12);
    }
  }
}

.error-list {
  margin: 8px 0 0 0;
  padding-left: 24px;
  color: #f56c6c;
  max-height: 150px;
  overflow-y: auto;
  list-style: none;
  
  &::-webkit-scrollbar {
    width: 6px;
  }
  
  &::-webkit-scrollbar-track {
    background: #f5f5f5;
    border-radius: 3px;
  }
  
  &::-webkit-scrollbar-thumb {
    background: #dcdfe6;
    border-radius: 3px;
    
    &:hover {
      background: #c0c4cc;
    }
  }
  
  li {
    margin: 6px 0;
    font-size: 13px;
    line-height: 1.6;
    position: relative;
    
    &::before {
      content: '•';
      position: absolute;
      left: -16px;
      color: #f56c6c;
      font-weight: bold;
    }
  }
}
</style>

