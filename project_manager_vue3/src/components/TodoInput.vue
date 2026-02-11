<template>
  <div class="todo-input-container">
    <div class="todo-input-card">
      <!-- 第一行：项目选择和步骤范围 -->
      <div class="todo-input-row-first">
        <!-- 项目选择 -->
        <div class="project-select-wrapper">
          <el-select
            v-model="selectedProjectId"
            placeholder="选择项目"
            filterable
            clearable
            class="project-select"
            @change="handleProjectChange"
          >
            <el-option
              v-for="project in projects"
              :key="project.id"
              :label="project.title"
              :value="project.id"
            >
              <span class="project-title">{{ project.title }}</span>
            </el-option>
          </el-select>
        </div>

        <!-- 步骤时间线 -->
        <div v-if="selectedProjectId && availableSteps.length > 0" class="step-timeline-wrapper" ref="timelineWrapperRef">
          <div class="step-timeline" ref="timelineRef">
            <div
              v-for="(step, index) in availableSteps"
              :key="step.id"
              class="step-timeline-item"
              :class="{
                'step-completed': step.status === '已完成',
                'step-todo': isStepInRange(step.id) && step.status !== '已完成',
                'step-selected-start': step.id === startStepId,
                'step-selected-end': step.id === endStepId
              }"
              :style="getStepItemStyle(index)"
              @click="handleStepClick(step.id, index)"
            >
              <div class="step-timeline-line" v-if="index < availableSteps.length - 1" :style="getStepLineStyle(index)"></div>
              <div class="step-timeline-dot"></div>
              <div class="step-timeline-label">{{ step.name }}</div>
            </div>
            <!-- 选中范围指示 -->
            <div
              v-if="startStepId && endStepId"
              class="step-range-indicator"
              :style="getRangeIndicatorStyle()"
            ></div>
          </div>
        </div>
      </div>

      <!-- 第二行：待办内容输入和提交按钮 -->
      <div class="todo-input-row-second">
        <div class="input-group">
          <el-input
            v-model="description"
            placeholder="输入待办内容..."
            class="description-input"
            maxlength="200"
            clearable
            @keyup.enter="handleAdd"
          />
          <el-button
            type="primary"
            :icon="Plus"
            :disabled="!canAdd"
            :loading="adding"
            circle
            class="submit-button"
            @click="handleAdd"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { useProject } from '@/composables/useProject'
import { projectApi, type Project, type ProjectStep } from '@/api/project'

interface Props {
  placeholder?: string
  onAdd?: (data: TodoInputData) => Promise<void>
}

interface TodoInputData {
  projectId: number
  projectTitle: string
  stepIds: number[]
  stepNames: string[]
  description: string
}

const props = withDefaults(defineProps<Props>(), {
  placeholder: '输入待办事项...',
})

const emit = defineEmits<{
  add: [data: TodoInputData]
}>()

const { projects, loadProjects } = useProject()
const selectedProjectId = ref<number | null>(null)
const startStepId = ref<number | null>(null)
const endStepId = ref<number | null>(null)
const description = ref('')
const adding = ref(false)
const projectSteps = ref<ProjectStep[]>([])
const selectingStart = ref(false)
const timelineWrapperRef = ref<HTMLElement | null>(null)
const timelineRef = ref<HTMLElement | null>(null)

// 可用的步骤（显示所有步骤，包括已完成的）
const availableSteps = computed(() => {
  if (projectSteps.value.length === 0) {
    return []
  }
  
  // 返回所有步骤，按顺序排序
  return [...projectSteps.value].sort((a, b) => a.order_index - b.order_index)
})

const startStepName = computed(() => {
  if (!startStepId.value) return ''
  const step = availableSteps.value.find(s => s.id === startStepId.value)
  return step?.name || ''
})

const endStepName = computed(() => {
  if (!endStepId.value) return startStepName.value
  const step = availableSteps.value.find(s => s.id === endStepId.value)
  return step?.name || startStepName.value
})

// 已选择的步骤范围
const selectedSteps = computed(() => {
  if (!startStepId.value) {
    return []
  }
  
  const startIndex = availableSteps.value.findIndex(s => s.id === startStepId.value)
  const endIndex = endStepId.value
    ? availableSteps.value.findIndex(s => s.id === endStepId.value)
    : startIndex
  
  if (startIndex === -1 || endIndex === -1 || startIndex > endIndex) {
    return []
  }
  
  return availableSteps.value.slice(startIndex, endIndex + 1)
})

// 判断步骤是否在选中范围内
const isStepInRange = (stepId: number): boolean => {
  if (!startStepId.value || !endStepId.value) return false
  
  const startIndex = availableSteps.value.findIndex(s => s.id === startStepId.value)
  const endIndex = availableSteps.value.findIndex(s => s.id === endStepId.value)
  const stepIndex = availableSteps.value.findIndex(s => s.id === stepId)
  
  if (startIndex === -1 || endIndex === -1 || stepIndex === -1) return false
  
  const minIndex = Math.min(startIndex, endIndex)
  const maxIndex = Math.max(startIndex, endIndex)
  
  return stepIndex >= minIndex && stepIndex <= maxIndex
}

// 处理步骤点击
const handleStepClick = (stepId: number, index: number) => {
  if (!startStepId.value || !endStepId.value) {
    startStepId.value = stepId
    endStepId.value = stepId
    return
  }
  
  const startIndex = availableSteps.value.findIndex(s => s.id === startStepId.value)
  const endIndex = availableSteps.value.findIndex(s => s.id === endStepId.value)
  const clickedIndex = index
  
  if (startStepId.value === endStepId.value) {
    if (clickedIndex < startIndex) {
      startStepId.value = stepId
    } else if (clickedIndex > startIndex) {
      endStepId.value = stepId
    } else {
      selectingStart.value = !selectingStart.value
    }
    return
  }
  
  if (clickedIndex <= startIndex) {
    startStepId.value = stepId
    if (clickedIndex > endIndex) {
      endStepId.value = startStepId.value
      startStepId.value = stepId
    }
  } else if (clickedIndex >= endIndex) {
    endStepId.value = stepId
    if (clickedIndex < startIndex) {
      startStepId.value = endStepId.value
      endStepId.value = stepId
    }
  } else {
    if (selectingStart.value) {
      startStepId.value = stepId
    } else {
      endStepId.value = stepId
    }
  }
  
  const finalStartIndex = availableSteps.value.findIndex(s => s.id === startStepId.value)
  const finalEndIndex = availableSteps.value.findIndex(s => s.id === endStepId.value)
  
  if (finalStartIndex > finalEndIndex) {
    const temp = startStepId.value
    startStepId.value = endStepId.value
    endStepId.value = temp
  }
}

// 计算每个步骤项的样式（动态计算间隔）
const getStepItemStyle = (index: number) => {
  if (!timelineWrapperRef.value || availableSteps.value.length === 0) {
    return {}
  }
  
  const wrapperWidth = timelineWrapperRef.value.offsetWidth
  const stepCount = availableSteps.value.length
  const minStepWidth = 100 // 最小步骤宽度（包含文字）
  const padding = 20 // 左右内边距
  const availableWidth = wrapperWidth - padding * 2
  
  // 计算每个步骤的宽度，充分利用空间
  const stepWidth = Math.max(minStepWidth, availableWidth / stepCount)
  
  return {
    flex: `0 0 ${stepWidth}px`,
    minWidth: `${stepWidth}px`
  }
}

// 计算连接线样式
const getStepLineStyle = (index: number) => {
  if (!timelineWrapperRef.value || availableSteps.value.length === 0) {
    return {}
  }
  
  const wrapperWidth = timelineWrapperRef.value.offsetWidth
  const stepCount = availableSteps.value.length
  const minStepWidth = 100
  const padding = 20
  const availableWidth = wrapperWidth - padding * 2
  const stepWidth = Math.max(minStepWidth, availableWidth / stepCount)
  
  return {
    width: `${stepWidth}px`
  }
}

// 计算范围指示器样式
const getRangeIndicatorStyle = () => {
  if (!startStepId.value || !endStepId.value || !timelineWrapperRef.value) return {}
  
  const startIndex = availableSteps.value.findIndex(s => s.id === startStepId.value)
  const endIndex = availableSteps.value.findIndex(s => s.id === endStepId.value)
  
  if (startIndex === -1 || endIndex === -1) return {}
  
  const minIndex = Math.min(startIndex, endIndex)
  const maxIndex = Math.max(startIndex, endIndex)
  
  const wrapperWidth = timelineWrapperRef.value.offsetWidth
  const stepCount = availableSteps.value.length
  const minStepWidth = 100
  const padding = 20
  const availableWidth = wrapperWidth - padding * 2
  const stepWidth = Math.max(minStepWidth, availableWidth / stepCount)
  
  const left = padding + minIndex * stepWidth + (stepWidth / 2) - 10 // 圆点中心位置
  const width = (maxIndex - minIndex) * stepWidth + 20
  
  return {
    left: `${left}px`,
    width: `${width}px`
  }
}

// 是否可以添加
const canAdd = computed(() => {
  return !!(
    selectedProjectId.value &&
    startStepId.value &&
    description.value.trim()
  )
})

// 处理项目变化
const handleProjectChange = async (projectId: number | null) => {
  if (!projectId) {
    projectSteps.value = []
    startStepId.value = null
    endStepId.value = null
    return
  }
  
  try {
    const projectData = await projectApi.get(projectId)
    projectSteps.value = (projectData.steps || []).sort((a, b) => a.order_index - b.order_index)
    
    if (availableSteps.value.length > 0) {
      // 找到第一个未完成的步骤
      const firstIncompleteStep = availableSteps.value.find(step => step.status !== '已完成')
      const defaultStepId = firstIncompleteStep ? firstIncompleteStep.id : availableSteps.value[0].id
      
      startStepId.value = defaultStepId
      endStepId.value = defaultStepId
      selectingStart.value = false
    } else {
      startStepId.value = null
      endStepId.value = null
    }
  } catch (error) {
    ElMessage.error('加载项目步骤失败')
    projectSteps.value = []
    startStepId.value = null
    endStepId.value = null
  }
}

// 添加待办
const handleAdd = async () => {
  if (!canAdd.value || !selectedProjectId.value || !startStepId.value) return
  
  const project = projects.value.find(p => p.id === selectedProjectId.value)
  if (!project) return
  
  const stepIds = selectedSteps.value.map(s => s.id)
  const stepNames = selectedSteps.value.map(s => s.name)
  
  const todoData: TodoInputData = {
    projectId: selectedProjectId.value,
    projectTitle: project.title,
    stepIds,
    stepNames,
    description: description.value.trim(),
  }
  
  adding.value = true
  try {
    if (props.onAdd) {
      await props.onAdd(todoData)
    } else {
      emit('add', todoData)
    }
    
    description.value = ''
    if (availableSteps.value.length > 0) {
      // 找到第一个未完成的步骤
      const firstIncompleteStep = availableSteps.value.find(step => step.status !== '已完成')
      const defaultStepId = firstIncompleteStep ? firstIncompleteStep.id : availableSteps.value[0].id
      
      startStepId.value = defaultStepId
      endStepId.value = defaultStepId
      selectingStart.value = false
    }
    
    ElMessage.success('待办添加成功')
  } catch (error) {
    ElMessage.error('添加待办失败')
  } finally {
    adding.value = false
  }
}

// 监听窗口大小变化，重新计算间隔
const handleResize = () => {
  // 触发响应式更新
  if (timelineWrapperRef.value) {
    // 强制重新计算
    const _ = timelineWrapperRef.value.offsetWidth
  }
}

// 滚动到第一个未完成节点并居中
const scrollToFirstIncompleteStep = () => {
  if (!timelineWrapperRef.value || availableSteps.value.length === 0) return
  
  const firstIncompleteIndex = availableSteps.value.findIndex(step => step.status !== '已完成')
  if (firstIncompleteIndex === -1) return
  
  nextTick(() => {
    const timeline = timelineRef.value
    if (!timeline) return
    
    const stepItems = timeline.querySelectorAll('.step-timeline-item')
    if (stepItems.length === 0) return
    
    const targetItem = stepItems[firstIncompleteIndex] as HTMLElement
    if (!targetItem) return
    
    const wrapper = timelineWrapperRef.value
    const wrapperWidth = wrapper.offsetWidth
    const itemLeft = targetItem.offsetLeft
    const itemWidth = targetItem.offsetWidth
    const scrollLeft = itemLeft - (wrapperWidth / 2) + (itemWidth / 2)
    
    wrapper.scrollTo({
      left: Math.max(0, scrollLeft),
      behavior: 'smooth'
    })
    
    // 同时设置选中状态
    const firstIncompleteStep = availableSteps.value[firstIncompleteIndex]
    if (firstIncompleteStep) {
      startStepId.value = firstIncompleteStep.id
      endStepId.value = firstIncompleteStep.id
    }
  })
}

// 监听步骤变化，触发重新计算和居中
watch([availableSteps, selectedProjectId], () => {
  nextTick(() => {
    handleResize()
    // 延迟执行，确保DOM已更新
    setTimeout(() => {
    scrollToFirstIncompleteStep()
    }, 100)
  })
}, { immediate: true })

onMounted(async () => {
  await loadProjects()
  window.addEventListener('resize', handleResize)
  nextTick(() => {
    handleResize()
    // 延迟执行，确保DOM已更新
    setTimeout(() => {
    scrollToFirstIncompleteStep()
    }, 200)
  })
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
})
</script>

<style scoped>
.todo-input-container {
  width: 100%;
}

.todo-input-card {
  background: #ffffff;
  border-radius: 12px;
  border: 1px solid #e5e7eb;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  padding: 16px;
  transition: all 0.3s ease;
}

.todo-input-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

/* 第一行：项目选择和步骤范围 */
.todo-input-row-first {
  display: flex;
  align-items: center;
  gap: 20px;
  margin-bottom: 16px;
}

.project-select-wrapper {
  flex: 0 0 200px;
}

.project-select {
  width: 100%;
}

.project-select :deep(.el-input__wrapper) {
  border-radius: 8px;
  border: 1px solid #e5e7eb;
  box-shadow: none;
  padding: 10px 14px;
  transition: all 0.2s;
}

.project-select :deep(.el-input__wrapper:hover) {
  border-color: #d1d5db;
}

.project-select :deep(.el-input__wrapper.is-focus) {
  border-color: #111827;
  box-shadow: 0 0 0 3px rgba(17, 24, 39, 0.1);
}

.project-title {
  font-weight: 500;
  color: #111827;
}

/* 步骤时间线 */
.step-timeline-wrapper {
  flex: 1;
  min-width: 0;
  overflow-x: auto;
  overflow-y: visible;
  padding: 12px 0 8px 0;
}

.step-timeline {
  position: relative;
  display: flex;
  align-items: flex-start;
  min-width: fit-content;
  padding: 0 20px;
  height: 60px;
}

.step-timeline-item {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  cursor: pointer;
  transition: all 0.3s ease;
  z-index: 2;
  flex-shrink: 0;
  padding-top: 8px;
}

.step-timeline-item:hover {
  transform: translateY(-2px);
}

.step-timeline-item:hover .step-timeline-dot {
  transform: scale(1.2);
}

.step-timeline-item:hover .step-timeline-label {
  color: #111827;
  font-weight: 600;
}

.step-timeline-line {
  position: absolute;
  top: 16px;
  left: 50%;
  height: 2px;
  background: #e5e7eb;
  z-index: 1;
  transform: translateX(0);
}

.step-timeline-item:last-child .step-timeline-line {
  display: none;
}

.step-timeline-dot {
  width: 16px;
  height: 16px;
  border-radius: 50%;
  background: #ffffff;
  border: 2px solid #d1d5db;
  position: relative;
  z-index: 3;
  transition: all 0.3s ease;
  margin-bottom: 8px;
  flex-shrink: 0;
}

.step-timeline-label {
  font-size: 12px;
  color: #6b7280;
  text-align: center;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 100%;
  transition: all 0.3s ease;
  line-height: 1.4;
  padding: 0 4px;
}

/* 已完成步骤 - 绿色 */
.step-timeline-item.step-completed:not(.step-selected-start):not(.step-selected-end) .step-timeline-dot {
  background: #10b981;
  border-color: #10b981;
  box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.1);
}

.step-timeline-item.step-completed:not(:last-child):not(.step-selected-start):not(.step-selected-end) .step-timeline-line {
  background: #10b981;
  height: 2px;
}

.step-timeline-item.step-completed:not(.step-selected-start):not(.step-selected-end) .step-timeline-label {
  color: #10b981;
  font-weight: 500;
}

/* 待办步骤 - 橙色 */
.step-timeline-item.step-todo .step-timeline-dot {
  background: #f97316;
  border-color: #f97316;
  box-shadow: 0 0 0 3px rgba(249, 115, 22, 0.15);
}

.step-timeline-item.step-todo:not(:last-child) .step-timeline-line {
  background: #f97316;
  height: 3px;
  z-index: 2;
}

.step-timeline-item.step-todo .step-timeline-label {
  color: #f97316;
  font-weight: 600;
}

/* 选中起始/结束步骤 */
.step-timeline-item.step-selected-start .step-timeline-dot,
.step-timeline-item.step-selected-end .step-timeline-dot {
  width: 20px;
  height: 20px;
  border: 3px solid #111827;
  background: #111827;
  box-shadow: 0 0 0 4px rgba(17, 24, 39, 0.15);
}

.step-timeline-item.step-selected-start .step-timeline-label,
.step-timeline-item.step-selected-end .step-timeline-label {
  color: #111827;
  font-weight: 700;
}

/* 选中范围指示器 */
.step-range-indicator {
  position: absolute;
  top: 16px;
  height: 3px;
  background: #f97316;
  border-radius: 2px;
  z-index: 2;
  pointer-events: none;
  transition: all 0.3s ease;
  opacity: 0.6;
}

/* 第二行：待办内容输入和提交按钮 */
.todo-input-row-second {
  display: flex;
  align-items: center;
}

.input-group {
  display: flex;
  align-items: center;
  width: 100%;
  border: 1px solid #e5e7eb;
  border-radius: 10px;
  overflow: hidden;
  transition: all 0.3s ease;
  background: #ffffff;
}

.input-group:hover {
  border-color: #d1d5db;
}

.input-group:focus-within {
  border-color: #111827;
  box-shadow: 0 0 0 3px rgba(17, 24, 39, 0.1);
}

.description-input {
  flex: 1;
  border: none;
  border-radius: 0;
}

.description-input :deep(.el-input__wrapper) {
  box-shadow: none;
  border: none;
  padding: 12px 16px;
  background: transparent;
}

.description-input :deep(.el-input__wrapper:hover) {
  box-shadow: none;
}

.description-input :deep(.el-input__wrapper.is-focus) {
  box-shadow: none;
}

.submit-button {
  flex-shrink: 0;
  width: 44px;
  height: 44px;
  border-radius: 0 10px 10px 0;
  border: none;
  border-left: 1px solid #e5e7eb;
  background: #111827;
  color: #ffffff;
  transition: all 0.2s;
  margin: 0;
}

.submit-button:hover:not(:disabled) {
  background: #1f2937;
}

.submit-button:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .todo-input-row-first {
    flex-direction: column;
    align-items: stretch;
    gap: 16px;
  }
  
  .project-select-wrapper {
    flex: 1;
    width: 100%;
  }
  
  .step-timeline {
    height: 70px;
  }
  
  .step-timeline-label {
    font-size: 11px;
  }
}
</style>
