<template>
  <el-dialog
    v-model="dialogVisible"
    :title="isProjectSteps ? '编辑项目步骤时间线' : (isEdit ? '编辑模板' : '新建模板')"
    width="800px"
    @close="handleClose"
    class="template-editor-dialog"
  >
    <el-form
      ref="formRef"
      :model="form"
      :rules="rules"
      label-width="100px"
    >
      <el-form-item v-if="!isProjectSteps" label="模板名称" prop="name">
        <el-input
          v-model="form.name"
          placeholder="请输入模板名称"
          :disabled="isEdit && template && 'is_default' in template && (template as any).is_default === true"
          clearable
        />
        <div class="form-tip" v-if="!isEdit">模板名称用于在创建项目时识别和选择模板</div>
      </el-form-item>
      <el-form-item v-if="!isProjectSteps" label="模板描述">
        <el-input
          v-model="form.description"
          type="textarea"
          :rows="2"
          placeholder="请输入模板描述（可选）"
          :disabled="isEdit && template && 'is_default' in template && (template as any).is_default === true"
        />
      </el-form-item>
      <el-alert
        v-if="isEdit && template && 'is_default' in template && (template as any).is_default === true"
        type="warning"
        :closable="false"
        show-icon
        style="margin-bottom: 20px;"
      >
        <template #title>
          <span>默认模板不可修改，如需修改请复制模板后编辑</span>
        </template>
      </el-alert>
      <el-form-item label="步骤列表" prop="steps">
        <div class="steps-editor">
          <div class="steps-header">
            <span class="steps-count">共 {{ form.steps.filter(s => s.trim()).length }} 个步骤</span>
            <el-button
              type="primary"
              :icon="Plus"
              size="small"
            @click="addStep"
            class="add-step-btn-header"
            :disabled="isEdit && template && 'is_default' in template && (template as any).is_default === true"
          >
            添加步骤
          </el-button>
          </div>
          <div class="steps-list" ref="stepsListRef">
            <transition-group name="step-list" tag="div">
              <div
                v-for="(step, index) in form.steps"
                :key="`step-${index}`"
                class="step-item"
                :class="{ 
                  'is-dragging': draggedIndex === index,
                  'is-over': draggedOverIndex === index && draggedIndex !== null && draggedIndex !== index
                }"
                :draggable="!isStepProtected(index) && !(isEdit && template && 'is_default' in template && (template as any).is_default === true)"
                @dragstart="handleDragStart(index, $event)"
                @dragend="handleDragEnd"
                @dragover.prevent="handleDragOver(index, $event)"
                @drop="handleDrop(index, $event)"
              >
                <div class="step-number" :class="{ 'protected-number': isStepProtected(index) }">
                  {{ index + 1 }}
                  <el-icon v-if="isStepProtected(index)" class="lock-icon"><Lock /></el-icon>
                </div>
                <div class="step-handle" :class="{ 'protected-handle': isStepProtected(index) }">
                  <el-icon class="drag-icon" :class="{ 'disabled': isStepProtected(index) }"><Rank /></el-icon>
                </div>
                <div class="step-content">
                  <el-input
                    v-model="form.steps[index]"
                    placeholder="请输入步骤名称"
                    @input="handleStepChange(index)"
                    @keyup.enter="addStep"
                    @focus="handleStepFocus(index)"
                    :disabled="isStepProtected(index) || (isEdit && template && 'is_default' in template && (template as any).is_default === true)"
                    :class="{ 'protected-step': isStepProtected(index) || (isEdit && template && 'is_default' in template && (template as any).is_default === true) }"
                  />
                </div>
                <div class="step-actions">
                  <el-tooltip
                    v-if="isStepProtected(index)"
                    content="首尾步骤不可删除"
                    placement="top"
                  >
                    <el-button
                      type="danger"
                      :icon="Delete"
                      circle
                      size="small"
                      disabled
                    />
                  </el-tooltip>
                  <el-button
                    v-else
                    type="danger"
                    :icon="Delete"
                    circle
                    size="small"
                    @click="removeStep(index)"
                    :disabled="form.steps.length <= 1 || (isEdit && template && 'is_default' in template && (template as any).is_default === true)"
                  />
                </div>
              </div>
            </transition-group>
            <div v-if="form.steps.length === 0" class="empty-steps">
              <el-empty description="暂无步骤，点击上方按钮添加" :image-size="80" />
            </div>
          </div>
        </div>
      </el-form-item>
    </el-form>

    <template #footer>
      <el-button @click="handleClose">取消</el-button>
      <el-button type="primary" :loading="submitting" @click="handleSubmit">
        确定
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, reactive, computed, watch, nextTick } from 'vue'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { Plus, Delete, Rank, Lock } from '@element-plus/icons-vue'
import { stepTemplateApi, type StepTemplate, type StepTemplateCreate, type StepTemplateUpdate } from '@/api/stepTemplate'

interface TemplateLike {
  id?: number
  name: string
  description?: string
  steps: string[]
  is_default?: boolean
}

interface Props {
  modelValue: boolean
  template?: StepTemplate | TemplateLike | null
}

const props = withDefaults(defineProps<Props>(), {
  template: null,
})

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  'success': [data?: { steps: string[] }]
  'close': []
}>()

const dialogVisible = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

const formRef = ref<FormInstance>()
const stepsListRef = ref<HTMLElement | null>(null)
const submitting = ref(false)
const draggedIndex = ref<number | null>(null)
const draggedOverIndex = ref<number | null>(null)
const focusedStepIndex = ref<number | null>(null)

const isEdit = computed(() => !!props.template)

// 检查是否是项目步骤（临时模板）
const isProjectSteps = computed(() => {
  if (!props.template) return false
  return !('id' in props.template) || (props.template && 'id' in props.template && props.template.id === 0)
})

const form = reactive<{
  name: string
  description: string
  steps: string[]
}>({
  name: '',
  description: '',
  steps: [''],
})

// 动态创建 rules，因为 isProjectSteps 是 computed
const rules = computed<FormRules>(() => ({
  name: [
    {
      required: !isProjectSteps.value,
      message: '请输入模板名称',
      trigger: 'blur'
    }
  ],
  steps: [
    {
      validator: (rule, value, callback) => {
        if (!value || value.length === 0) {
          callback(new Error('至少需要一个步骤'))
        } else if (value.some((step: string) => !step.trim())) {
          callback(new Error('步骤名称不能为空'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ],
}))

// 默认的首尾步骤（不可删除）
const DEFAULT_FIRST_STEP = '已接单'
const DEFAULT_LAST_STEP = '已结账'

// 判断步骤是否不可删除（首尾步骤）
const isStepProtected = (index: number): boolean => {
  if (!isEdit.value && !isProjectSteps.value) {
    // 新建模板时，首尾位置（index 0 和最后一个）的步骤不可删除
    // 确保"已接单"在第一位，"已结账"在最后一位
    const firstIndex = 0
    const lastIndex = form.steps.length - 1
    const isFirstStep = index === firstIndex && form.steps[firstIndex]?.trim() === DEFAULT_FIRST_STEP
    const isLastStep = index === lastIndex && form.steps[lastIndex]?.trim() === DEFAULT_LAST_STEP
    return isFirstStep || isLastStep
  }
  return false
}

// 判断位置是否受保护（首尾位置）
const isPositionProtected = (index: number): boolean => {
  if (!isEdit.value && !isProjectSteps.value) {
    // 首尾位置（index 0 和最后一个）受保护，不能将其他步骤拖拽到这里
    const firstIndex = 0
    const lastIndex = form.steps.length - 1
    return index === firstIndex || index === lastIndex
  }
  return false
}

// 初始化表单
watch(() => props.template, (template) => {
  if (template) {
    form.name = template.name
    form.description = template.description || ''
    form.steps = template.steps.length > 0 ? [...template.steps] : ['']
  } else {
    // 新建模板时，默认包含"已接单"和"已结账"
    form.name = ''
    form.description = ''
    form.steps = [DEFAULT_FIRST_STEP, DEFAULT_LAST_STEP]
  }
}, { immediate: true })

// 确保首尾步骤正确
const ensureFirstAndLastSteps = () => {
  if (isEdit.value || isProjectSteps.value) return
  
  // 确保"已接单"在第一位
  if (form.steps.length === 0 || form.steps[0]?.trim() !== DEFAULT_FIRST_STEP) {
    // 如果第一位不是"已接单"，检查是否存在，如果存在则移到第一位，否则添加
    const firstIndex = form.steps.findIndex(step => step.trim() === DEFAULT_FIRST_STEP)
    if (firstIndex > 0) {
      form.steps.splice(firstIndex, 1)
      form.steps.unshift(DEFAULT_FIRST_STEP)
    } else if (firstIndex === -1) {
      form.steps.unshift(DEFAULT_FIRST_STEP)
    }
  }
  
  // 确保"已结账"在最后一位
  const lastIndex = form.steps.length - 1
  if (lastIndex < 0 || form.steps[lastIndex]?.trim() !== DEFAULT_LAST_STEP) {
    // 如果最后一位不是"已结账"，检查是否存在，如果存在则移到最后，否则添加
    const lastStepIndex = form.steps.findIndex(step => step.trim() === DEFAULT_LAST_STEP)
    if (lastStepIndex >= 0 && lastStepIndex < lastIndex) {
      form.steps.splice(lastStepIndex, 1)
      form.steps.push(DEFAULT_LAST_STEP)
    } else if (lastStepIndex === -1) {
      form.steps.push(DEFAULT_LAST_STEP)
    }
  }
}

// 监听步骤变化，确保首尾步骤正确
watch(() => form.steps, () => {
  if (!isEdit.value && !isProjectSteps.value) {
    ensureFirstAndLastSteps()
  }
}, { deep: true })

const addStep = () => {
  // 如果已经有"已结账"在最后，则在它之前插入新步骤
  const lastIndex = form.steps.length - 1
  if (form.steps[lastIndex]?.trim() === DEFAULT_LAST_STEP) {
    form.steps.splice(lastIndex, 0, '')
  } else {
    form.steps.push('')
  }
  nextTick(() => {
    // 滚动到底部
    if (stepsListRef.value) {
      stepsListRef.value.scrollTop = stepsListRef.value.scrollHeight
    }
    // 聚焦到新添加的输入框
    const newIndex = form.steps.length - 2 // 因为"已结账"在最后
    const input = stepsListRef.value?.querySelector(`.step-item:nth-child(${newIndex + 1}) .el-input__inner`) as HTMLInputElement
    if (input) {
      input.focus()
    }
  })
}

const removeStep = (index: number) => {
  if (form.steps.length <= 1) {
    ElMessage.warning('至少需要保留一个步骤')
    return
  }
  
  // 检查是否是受保护的步骤
  if (isStepProtected(index)) {
    ElMessage.warning('首尾步骤（已接单、已结账）不可删除')
    return
  }
  
  form.steps.splice(index, 1)
  
  // 确保首尾步骤正确
  ensureFirstAndLastSteps()
}

const handleStepChange = (index: number) => {
  // 可以在这里添加实时验证逻辑
}

const handleStepFocus = (index: number) => {
  focusedStepIndex.value = index
}

// 拖拽相关
const handleDragStart = (index: number, event: DragEvent) => {
  // 受保护的步骤不能拖拽
  if (isStepProtected(index)) {
    event.preventDefault()
    return
  }
  draggedIndex.value = index
  if (event.dataTransfer) {
    event.dataTransfer.effectAllowed = 'move'
    event.dataTransfer.setData('text/html', '')
  }
}

const handleDragEnd = () => {
  draggedIndex.value = null
  draggedOverIndex.value = null
  // 拖拽结束后，移除所有拖拽样式
  nextTick(() => {
    if (stepsListRef.value) {
      const items = stepsListRef.value.querySelectorAll('.step-item')
      items.forEach(item => item.classList.remove('is-over'))
    }
  })
}

const handleDragOver = (index: number, event: DragEvent) => {
  event.preventDefault()
  if (event.dataTransfer) {
    // 如果目标位置受保护，不允许拖拽
    if (isPositionProtected(index)) {
      event.dataTransfer.dropEffect = 'none'
      return
    }
    event.dataTransfer.dropEffect = 'move'
  }
  draggedOverIndex.value = index
}

const handleDrop = (targetIndex: number, event: DragEvent) => {
  event.preventDefault()
  if (draggedIndex.value === null || draggedIndex.value === targetIndex) {
    return
  }
  
  // 不能将步骤拖拽到受保护的位置（首尾位置）
  if (isPositionProtected(targetIndex)) {
    ElMessage.warning('不能将步骤移动到首尾位置（已接单必须在第一位，已结账必须在最后一位）')
    draggedIndex.value = null
    draggedOverIndex.value = null
    return
  }
  
  // 不能拖拽受保护的步骤（已接单和已结账）
  if (isStepProtected(draggedIndex.value)) {
    ElMessage.warning('不能移动首尾步骤（已接单和已结账）')
    draggedIndex.value = null
    draggedOverIndex.value = null
    return
  }
  
  const draggedStep = form.steps[draggedIndex.value]
  form.steps.splice(draggedIndex.value, 1)
  
  // 如果拖拽的目标位置在受保护步骤之后，需要调整索引
  let adjustedTargetIndex = targetIndex
  if (draggedIndex.value < targetIndex) {
    adjustedTargetIndex = targetIndex - 1
  }
  
  form.steps.splice(adjustedTargetIndex, 0, draggedStep)
  
  // 确保首尾步骤正确
  ensureFirstAndLastSteps()
  
  draggedIndex.value = null
  draggedOverIndex.value = null
}

const handleSubmit = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (valid) {
      submitting.value = true
      try {
        const steps = form.steps.filter(step => step.trim())
        
        // 如果是项目步骤（临时模板），直接触发success事件，由父组件处理
        if (isProjectSteps.value) {
          emit('success', { steps })
          submitting.value = false
          return
        }
        
        if (isEdit.value && props.template && 'id' in props.template && props.template.id) {
          // 检查是否是默认模板
          if (props.template && 'is_default' in props.template && (props.template as any).is_default === true) {
            ElMessage.warning('默认模板不可修改，请复制后编辑')
            submitting.value = false
            return
          }
          
          const updateData: StepTemplateUpdate = {
            name: form.name,
            description: form.description || undefined,
            steps: steps,
          }
          await stepTemplateApi.update(props.template.id, updateData)
          ElMessage.success('模板更新成功')
        } else {
          const createData: StepTemplateCreate = {
            name: form.name,
            description: form.description || undefined,
            steps: steps,
          }
          await stepTemplateApi.create(createData)
          ElMessage.success('模板创建成功')
        }
        
        emit('success')
      } catch (error: any) {
        ElMessage.error(error.response?.data?.detail || '操作失败')
      } finally {
        submitting.value = false
      }
    }
  })
}

const handleClose = () => {
  emit('close')
  // 重置表单
  form.name = ''
  form.description = ''
  form.steps = ['']
  draggedIndex.value = null
  draggedOverIndex.value = null
  focusedStepIndex.value = null
  if (formRef.value) {
    formRef.value.resetFields()
  }
}
</script>

<style scoped>
.template-editor-dialog :deep(.el-dialog__body) {
  padding: 20px;
}

.steps-editor {
  width: 100%;
}

.steps-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  padding: 8px 12px;
  background: #f5f7fa;
  border-radius: 6px;
}

.steps-count {
  font-size: 14px;
  color: #606266;
  font-weight: 500;
}

.add-step-btn-header {
  height: 32px;
}

.steps-list {
  max-height: 450px;
  overflow-y: auto;
  padding: 12px;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  background: #fafafa;
  min-height: 100px;
}

.empty-steps {
  padding: 40px 0;
}

.step-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px;
  margin-bottom: 10px;
  background: #fff;
  border: 2px solid #e4e7ed;
  border-radius: 8px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  cursor: move;
  position: relative;
}

.step-item:last-child {
  margin-bottom: 0;
}

.step-item:hover {
  border-color: #409eff;
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.15);
  transform: translateY(-1px);
}

.step-item.is-dragging {
  opacity: 0.6;
  transform: scale(0.98) rotate(2deg);
  z-index: 1000;
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
}

.step-item.is-over {
  border-color: #67c23a;
  background: #f0f9ff;
  border-style: dashed;
}

.step-number {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
  border-radius: 50%;
  font-size: 13px;
  font-weight: 600;
  flex-shrink: 0;
  position: relative;
}

.step-number.protected-number {
  background: linear-gradient(135deg, #67c23a 0%, #85ce61 100%);
}

.step-number .lock-icon {
  position: absolute;
  top: -4px;
  right: -4px;
  font-size: 10px;
  background: #f56c6c;
  color: #fff;
  border-radius: 50%;
  padding: 2px;
  border: 1px solid #fff;
}

.step-handle {
  display: flex;
  align-items: center;
  cursor: grab;
  color: #909399;
  padding: 4px;
  border-radius: 4px;
  transition: all 0.2s;
}

.step-handle:hover:not(.protected-handle) {
  background: #f5f7fa;
  color: #409eff;
}

.step-handle.protected-handle {
  cursor: not-allowed;
  opacity: 0.5;
}

.step-handle:active:not(.protected-handle) {
  cursor: grabbing;
}

.drag-icon {
  font-size: 20px;
}

.drag-icon.disabled {
  opacity: 0.3;
  cursor: not-allowed;
}

.step-content {
  flex: 1;
}

.step-content :deep(.el-input__wrapper) {
  transition: all 0.3s;
}

.step-content :deep(.el-input__wrapper:hover) {
  box-shadow: 0 0 0 1px #409eff inset;
}

.step-content :deep(.el-input.protected-step .el-input__wrapper) {
  background-color: #f0f9ff;
  border-color: #67c23a;
}

.step-content :deep(.el-input.is-disabled .el-input__wrapper) {
  background-color: #f5f7fa;
  cursor: not-allowed;
}

.step-actions {
  display: flex;
  gap: 8px;
  flex-shrink: 0;
}

.step-actions .el-button {
  transition: all 0.2s;
}

.step-actions .el-button:hover {
  transform: scale(1.1);
}

/* 拖拽动画优化 */
.step-list-enter-active {
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.step-list-leave-active {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: absolute;
  width: calc(100% - 24px);
}

.step-list-enter-from {
  opacity: 0;
  transform: translateY(-20px) scale(0.9);
}

.step-list-leave-to {
  opacity: 0;
  transform: translateX(100px) scale(0.8);
}

.step-list-move {
  transition: transform 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

/* 拖拽动画 */
.step-list-enter-active,
.step-list-leave-active {
  transition: all 0.3s ease;
}

.step-list-enter-from {
  opacity: 0;
  transform: translateY(-10px);
}

.step-list-leave-to {
  opacity: 0;
  transform: translateX(30px);
}

.step-list-move {
  transition: transform 0.3s ease;
}

.form-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
  line-height: 1.5;
}
</style>

