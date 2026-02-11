<template>
  <el-card class="steps-card">
    <template #header>
      <div class="card-header">
        <span>项目步骤时间线</span>
        <div>
          <el-button type="info" @click="$emit('select-template')">
            <el-icon><Document /></el-icon>
            选择模板
          </el-button>
          <el-button type="info" @click="$emit('edit-timeline')">
            <el-icon><Edit /></el-icon>
            编辑时间线
          </el-button>
        </div>
      </div>
    </template>

    <!-- 优化的步骤时间线 -->
    <div class="steps-timeline-container">
      <div class="timeline-wrapper">
        <div
          v-for="(step, index) in steps"
          :key="step.id"
          class="timeline-item"
          :class="{
            'timeline-item-active': step.status === '进行中',
            'timeline-item-completed': step.status === '已完成',
            'timeline-item-todo': step.is_todo,
            'timeline-item-expanded': expandedStepId === step.id
          }"
          @click="$emit('toggle-expand', step.id)"
        >
          <!-- 时间线连接线 -->
          <div class="timeline-line" v-if="index < steps.length - 1"></div>
          
          <!-- 步骤节点 -->
          <div class="timeline-node" :class="`node-${getStepStatus(step)}`">
            <div class="node-icon">
              <el-icon v-if="step.status === '已完成'"><Check /></el-icon>
              <el-icon v-else-if="step.status === '进行中'"><Loading /></el-icon>
              <span v-else class="node-number">{{ index + 1 }}</span>
            </div>
          </div>
          
          <!-- 步骤内容卡片 -->
          <div class="timeline-content" :class="{ 'step-disabled': !isStepOperable(step) && step.status !== '已完成' }">
            <div class="step-header">
              <div class="step-title-row">
                <!-- 步骤名称（可双击编辑） -->
                <span
                  v-if="editingStepId !== step.id"
                  class="step-name"
                  :class="{ 'step-name-disabled': !isStepOperable(step) && step.status !== '已完成' }"
                  @dblclick.stop="isStepOperable(step) ? $emit('edit-name', step) : null"
                >
                  {{ step.name }}
                </span>
                <el-input
                  v-else
                  :model-value="editingStepName"
                  @update:model-value="(value) => $emit('update-editing-name', value)"
                  ref="stepNameInputRef"
                  size="small"
                  class="step-name-input"
                  @blur="$emit('save-name', step, editingStepName)"
                  @keyup.enter="$emit('save-name', step, editingStepName)"
                  @keyup.esc="$emit('cancel-edit-name')"
                  @click.stop
                />
                
                <!-- 状态标签 -->
                <div class="step-badges">
                  <span
                    class="status-badge"
                    :class="{
                      [`status-${getStepStatus(step)}`]: true,
                      'status-badge-disabled': !isStepOperable(step) && step.status !== '已完成'
                    }"
                    @click.stop="isStepOperable(step) ? $emit('cycle-status', step) : (() => { ElMessage.warning(getStepHint(step) || '请先完成前置步骤') })()"
                    :title="isStepOperable(step) ? '点击切换状态' : (getStepHint(step) || '请先完成前置步骤')"
                  >
                    {{ step.status }}
                  </span>
                  <span
                    v-if="step.is_todo"
                    class="todo-badge"
                    @click.stop="$emit('toggle-todo', step)"
                    title="点击取消待办"
                  >
                    <el-icon><StarFilled /></el-icon>
                    待办
                  </span>
                  <el-tooltip
                    v-if="!isStepOperable(step) && step.status !== '已完成'"
                    :content="getStepHint(step) || '请先完成前置步骤'"
                    placement="top"
                  >
                    <el-icon class="warning-icon"><Warning /></el-icon>
                  </el-tooltip>
                </div>
              </div>
              
              <!-- 步骤完成时间和项目开始时长（仅已完成步骤显示） -->
              <div v-if="step.status === '已完成'" class="step-time-info">
                <div class="step-time-item">
                  <el-icon class="time-icon"><Clock /></el-icon>
                  <span class="time-label">完成时间：</span>
                  <span class="time-value">{{ formatDateTime(step.updated_at) }}</span>
                </div>
                <div class="step-time-item" v-if="projectCreatedAt">
                  <el-icon class="time-icon"><Timer /></el-icon>
                  <span class="time-label">项目开始：</span>
                  <span class="time-value">{{ getProjectDuration(projectCreatedAt) }}</span>
                </div>
              </div>
              
              <!-- 展开/折叠指示器 -->
              <div class="expand-indicator">
                <el-icon :class="{ 'rotated': expandedStepId === step.id }">
                  <ArrowDown />
                </el-icon>
              </div>
            </div>
            
            <!-- 展开后的详细操作区域 -->
            <transition name="slide-down">
              <div v-show="expandedStepId === step.id" class="step-details" @click.stop>
                <div class="details-grid">
                  <!-- 状态选择 -->
                  <div class="detail-item">
                    <label>状态</label>
                    <div class="status-selector">
                      <div
                        v-for="statusOption in ['待开始', '进行中', '已完成']"
                        :key="statusOption"
                        class="status-option"
                        :class="{
                          'active': step.status === statusOption,
                          'disabled': statusOption !== '待开始' && !checkPreviousStepsCompleted(step) && step.status !== '已完成'
                        }"
                        @click="statusOption === '待开始' || checkPreviousStepsCompleted(step) || step.status === '已完成' ? $emit('update-status', step, statusOption) : (() => { ElMessage.warning(getStepHint(step) || '请先完成前置步骤') })()"
                        :title="statusOption !== '待开始' && !checkPreviousStepsCompleted(step) && step.status !== '已完成' ? (getStepHint(step) || '请先完成前置步骤') : ''"
                      >
                        {{ statusOption }}
                      </div>
                    </div>
                  </div>
                  
                  <!-- 截止时间 -->
                  <div class="detail-item">
                    <label>截止时间</label>
                    <el-date-picker
                      :model-value="step.deadline"
                      type="datetime"
                      size="small"
                      placeholder="设置截止时间"
                      @update:model-value="(value) => $emit('update-deadline', step, value)"
                      @click.stop
                    />
                  </div>
                </div>
                
                <!-- 操作按钮组 -->
                <div class="step-actions">
                  <div
                    class="action-btn insert-btn"
                    @click="$emit('insert-before', step)"
                    title="在此步骤之前插入新步骤"
                  >
                    <el-icon><Plus /></el-icon>
                    <span>插入步骤</span>
                  </div>
                  <div
                    class="action-btn delete-btn"
                    @click="$emit('delete-step', step)"
                    title="删除此步骤"
                  >
                    <el-icon><Delete /></el-icon>
                    <span>删除</span>
                  </div>
                </div>
                
                <!-- 截止时间显示 -->
                <div v-if="step.deadline" class="deadline-display">
                  <el-icon><Clock /></el-icon>
                  <span>截止时间：{{ new Date(step.deadline).toLocaleString() }}</span>
                </div>
              </div>
            </transition>
          </div>
        </div>
      </div>
    </div>
  </el-card>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { ElMessage, type FormInstance } from 'element-plus'
import { Document, Edit, Check, Loading, StarFilled, Warning, Clock, Timer, ArrowDown, Plus, Delete } from '@element-plus/icons-vue'
import type { ProjectStep } from '@/api/project'

interface Props {
  steps: ProjectStep[]
  expandedStepId: number | null
  editingStepId: number | null
  editingStepName: string
  projectCreatedAt?: string
  isStepOperable: (step: ProjectStep) => boolean
  checkPreviousStepsCompleted: (step: ProjectStep) => boolean
  getStepHint: (step: ProjectStep) => string | null
}

const props = defineProps<Props>()

defineEmits<{
  'select-template': []
  'edit-timeline': []
  'toggle-expand': [stepId: number]
  'edit-name': [step: ProjectStep]
  'save-name': [step: ProjectStep, name: string]
  'cancel-edit-name': []
  'cycle-status': [step: ProjectStep]
  'update-status': [step: ProjectStep, status: string]
  'update-deadline': [step: ProjectStep, deadline: string | null]
  'toggle-todo': [step: ProjectStep]
  'insert-before': [step: ProjectStep]
  'delete-step': [step: ProjectStep]
}>()

const stepNameInputRef = ref<FormInstance>()

// 获取步骤状态用于样式
const getStepStatus = (step: ProjectStep): string => {
  if (step.status === '已完成') return 'success'
  if (step.status === '进行中') return 'process'
  return 'wait'
}

// 格式化日期时间
const formatDateTime = (dateString: string): string => {
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

// 计算项目开始时长
const getProjectDuration = (createdAt: string): string => {
  const startDate = new Date(createdAt)
  const now = new Date()
  const diffMs = now.getTime() - startDate.getTime()
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24))
  const diffMonths = Math.floor(diffDays / 30)
  const diffYears = Math.floor(diffDays / 365)
  
  if (diffYears > 0) {
    return `${diffYears}年${Math.floor((diffDays % 365) / 30)}个月`
  } else if (diffMonths > 0) {
    return `${diffMonths}个月${diffDays % 30}天`
  } else if (diffDays > 0) {
    return `${diffDays}天`
  } else {
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60))
    if (diffHours > 0) {
      return `${diffHours}小时`
    } else {
      const diffMinutes = Math.floor(diffMs / (1000 * 60))
      return diffMinutes > 0 ? `${diffMinutes}分钟` : '刚刚开始'
    }
  }
}
</script>

<style scoped>
.steps-card {
  height: 100%;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
}

.steps-timeline-container {
  position: relative;
  padding: 20px 0;
}

.timeline-wrapper {
  position: relative;
  padding-left: 50px;
}

.timeline-item {
  position: relative;
  margin-bottom: 24px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.timeline-item:last-child {
  margin-bottom: 0;
}

.timeline-item-active {
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.8;
  }
}

.timeline-item-expanded {
  margin-bottom: 32px;
}

.timeline-line {
  position: absolute;
  left: -37px;
  top: 20px;
  width: 2px;
  height: calc(100% + 4px);
  background: linear-gradient(to bottom, #409eff, #e4e7ed);
  z-index: 1;
}

.timeline-node {
  position: absolute;
  left: -50px;
  top: 0;
  width: 26px;
  height: 26px;
  border-radius: 50%;
  border: 3px solid #fff;
  z-index: 2;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  transition: all 0.3s ease;
}

.timeline-item:hover .timeline-node {
  transform: scale(1.1);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

.node-success {
  background: #67c23a;
  color: #fff;
}

.node-process {
  background: #409eff;
  color: #fff;
  animation: pulse-ring 2s infinite;
}

@keyframes pulse-ring {
  0% {
    box-shadow: 0 0 0 0 rgba(64, 158, 255, 0.7);
  }
  70% {
    box-shadow: 0 0 0 10px rgba(64, 158, 255, 0);
  }
  100% {
    box-shadow: 0 0 0 0 rgba(64, 158, 255, 0);
  }
}

.node-wait {
  background: #e4e7ed;
}

.node-wait .node-number {
  color: #909399;
  font-weight: 600;
  font-size: 12px;
}

.timeline-content {
  background: #fff;
  border-radius: 8px;
  padding: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  border: 1px solid #ebeef5;
}

.timeline-item:hover .timeline-content {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
  border-color: #c0c4cc;
}

.timeline-item-expanded .timeline-content {
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  border-color: #409eff;
}

.step-disabled {
  opacity: 0.7;
  position: relative;
}

.step-disabled::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.5);
  border-radius: 8px;
  z-index: 1;
  pointer-events: none;
}

.step-header {
  position: relative;
}

.step-title-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 8px;
}

.step-name {
  flex: 1;
  font-size: 15px;
  font-weight: 600;
  color: #303133;
  cursor: text;
  padding: 4px 8px;
  border-radius: 4px;
  transition: all 0.2s;
}

.step-name:hover {
  background: #f5f7fa;
}

.step-name-disabled {
  color: #c0c4cc;
  cursor: not-allowed;
}

.step-name-input {
  flex: 1;
}

.step-badges {
  display: flex;
  align-items: center;
  gap: 8px;
}

.status-badge {
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  border: 1px solid transparent;
}

.status-badge:hover {
  transform: scale(1.05);
}

.status-success {
  background: #f0f9ff;
  color: #67c23a;
  border-color: #67c23a;
}

.status-process {
  background: #ecf5ff;
  color: #409eff;
  border-color: #409eff;
}

.status-wait {
  background: #f5f7fa;
  color: #909399;
  border-color: #c0c4cc;
}

.status-badge-disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.todo-badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 4px 8px;
  background: #fff7e6;
  color: #e6a23c;
  border-radius: 12px;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s;
}

.todo-badge:hover {
  background: #ffecc7;
}

.warning-icon {
  color: #e6a23c;
  cursor: help;
}

.step-time-info {
  display: flex;
  gap: 16px;
  margin-top: 8px;
  padding-top: 8px;
  border-top: 1px solid #ebeef5;
  font-size: 12px;
  color: #909399;
}

.step-time-item {
  display: flex;
  align-items: center;
  gap: 4px;
}

.time-icon {
  font-size: 14px;
}

.expand-indicator {
  position: absolute;
  top: 0;
  right: 0;
  transition: transform 0.3s;
}

.expand-indicator .rotated {
  transform: rotate(180deg);
}

.step-details {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #ebeef5;
}

.details-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  margin-bottom: 16px;
}

.detail-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.detail-item label {
  font-size: 12px;
  color: #606266;
  font-weight: 500;
}

.status-selector {
  display: flex;
  gap: 8px;
}

.status-option {
  flex: 1;
  padding: 8px 12px;
  text-align: center;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 13px;
}

.status-option:hover:not(.disabled):not(.active) {
  background: #f5f7fa;
  border-color: #c0c4cc;
}

.status-option.active {
  background: #409eff;
  color: #fff;
  border-color: #409eff;
}

.status-option.disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.step-actions {
  display: flex;
  gap: 12px;
  margin-top: 16px;
}

.action-btn {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 10px;
  border: 1px solid #dcdfe6;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 13px;
}

.action-btn:hover {
  background: #f5f7fa;
  border-color: #c0c4cc;
}

.insert-btn {
  color: #409eff;
  border-color: #409eff;
}

.insert-btn:hover {
  background: #ecf5ff;
}

.delete-btn {
  color: #f56c6c;
  border-color: #f56c6c;
}

.delete-btn:hover {
  background: #fef0f0;
}

.deadline-display {
  margin-top: 12px;
  padding: 8px 12px;
  background: #f5f7fa;
  border-radius: 4px;
  font-size: 12px;
  color: #606266;
  display: flex;
  align-items: center;
  gap: 6px;
}

.slide-down-enter-active,
.slide-down-leave-active {
  transition: all 0.3s ease;
  max-height: 500px;
  opacity: 1;
}

.slide-down-enter-from,
.slide-down-leave-to {
  max-height: 0;
  opacity: 0;
  overflow: hidden;
}

@media (max-width: 768px) {
  .timeline-wrapper {
    padding-left: 30px;
  }

  .timeline-node {
    left: -30px;
    width: 24px;
    height: 24px;
  }

  .timeline-line {
    left: -18px;
  }

  .step-title-row {
    flex-direction: column;
    align-items: flex-start;
  }

  .details-grid {
    grid-template-columns: 1fr;
  }

  .step-actions {
    flex-direction: column;
  }

  .action-btn {
    width: 100%;
    justify-content: center;
  }
}
</style>

