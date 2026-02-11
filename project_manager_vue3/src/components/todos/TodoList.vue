<template>
  <el-card class="todos-detail-card">
    <template #header>
      <div class="card-header">
        <div class="header-left">
          <span>{{ formattedDate }} 的待办</span>
          <div class="header-stats">
            <span class="stat-badge">待办: {{ todoCount }}</span>
            <span class="stat-badge">完成: {{ completedCount }}</span>
            <span class="stat-badge">总计: {{ totalCount }}</span>
          </div>
        </div>
        <el-button
          plain
          size="small"
          class="add-todo-btn"
          @click="$emit('add-todo')"
        >
          <el-icon><Plus /></el-icon>
          添加待办
        </el-button>
      </div>
    </template>
    
    <!-- 待办输入组件 -->
    <div v-if="showInput" class="todo-input-wrapper">
      <TodoInput @add="handleAdd" />
      <el-button
        type="text"
        size="small"
        @click="$emit('cancel-input')"
        style="margin-top: 8px"
      >
        取消
      </el-button>
    </div>
    
    <div v-loading="loading" class="todos-list">
      <div v-if="todos.length === 0" class="empty-todos">
        <el-empty description="该日期暂无待办事项" :image-size="100">
          <el-button type="primary" @click="$emit('add-todo')">
            添加待办
          </el-button>
        </el-empty>
      </div>
      
      <div v-else class="todo-items">
        <div
          v-for="todo in todos"
          :key="todo.id"
          class="todo-item"
          :class="{
            'todo-item-completed': todo.is_completed
          }"
        >
          <!-- 完成按钮（圆圈） -->
          <div class="todo-checkbox" @click.stop="$emit('toggle-complete', todo)">
            <div class="checkbox-circle" :class="{ 'checked': todo.is_completed }">
              <el-icon v-if="todo.is_completed" class="check-icon"><Check /></el-icon>
            </div>
          </div>
          
          <!-- 左侧状态指示器 -->
          <div class="todo-status-indicator" :class="{ 'completed': todo.is_completed }"></div>
          
          <!-- 主要内容区域 -->
          <div class="todo-content">
            <!-- 第一行：项目名称和完成时间 -->
            <div class="todo-header">
              <div class="todo-header-left">
                <span class="project-name">{{ todo.project_title }}</span>
                <!-- 步骤标签 -->
                <el-popover
                  v-if="todo.step_names && todo.step_names.length > 0"
                  placement="top"
                  :width="300"
                  trigger="hover"
                >
                  <template #reference>
                    <el-tag type="info" size="small" class="step-range-tag">
                      {{ formatStepRange(todo.step_names) }}
                    </el-tag>
                  </template>
                  <div class="step-popover">
                    <div class="step-popover-title">包含步骤：</div>
                    <div class="step-list">
                      <el-tag
                        v-for="(stepName, index) in todo.step_names"
                        :key="index"
                        size="small"
                        class="step-tag"
                      >
                        {{ stepName }}
                      </el-tag>
                    </div>
                  </div>
                </el-popover>
              </div>
              <span v-if="todo.is_completed && todo.updated_at" class="todo-time">
                {{ formatTimeAgo(todo.updated_at) }}完成
              </span>
            </div>
            
            <!-- 待办内容和操作按钮 -->
            <div class="todo-description-row">
              <div class="todo-description" :class="{ 'completed': todo.is_completed }">
                {{ todo.description }}
              </div>
              <div class="todo-actions">
                <el-button
                  text
                  size="small"
                  class="action-btn"
                  @click.stop="$emit('view', todo)"
                >
                  <el-icon><View /></el-icon>
                  查看
                </el-button>
                <el-button
                  v-if="!todo.is_completed"
                  text
                  size="small"
                  class="action-btn"
                  @click.stop="$emit('edit', todo)"
                >
                  <el-icon><Edit /></el-icon>
                  编辑
                </el-button>
                <el-button
                  text
                  size="small"
                  class="action-btn"
                  @click.stop="$emit('delete', todo)"
                >
                  <el-icon><Delete /></el-icon>
                  删除
                </el-button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </el-card>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { Check, Plus, View, Edit, Delete } from '@element-plus/icons-vue'
import TodoInput from '@/components/TodoInput.vue'
import type { TodoItem } from '@/api/todo'

interface Props {
  todos: TodoItem[]
  selectedDate: string
  loading?: boolean
  showInput?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  loading: false,
  showInput: false
})

const emit = defineEmits<{
  'add-todo': []
  'cancel-input': []
  'toggle-complete': [todo: TodoItem]
  'view': [todo: TodoItem]
  'edit': [todo: TodoItem]
  'delete': [todo: TodoItem]
  'add': [description: string]
}>()

const weekdays = ['日', '一', '二', '三', '四', '五', '六']

// 格式化选中的日期
const formattedDate = computed(() => {
  const date = new Date(props.selectedDate)
  const month = date.getMonth() + 1
  const day = date.getDate()
  const weekday = weekdays[date.getDay()]
  return `${month}月${day}日 星期${weekday}`
})

// 统计
const todoCount = computed(() => {
  return props.todos.filter(t => !t.is_completed).length
})

const completedCount = computed(() => {
  return props.todos.filter(t => t.is_completed).length
})

const totalCount = computed(() => {
  return props.todos.length
})

// 格式化步骤范围
const formatStepRange = (stepNames: string[]): string => {
  if (!stepNames || stepNames.length === 0) return ''
  if (stepNames.length === 1) return stepNames[0]
  return `${stepNames[0]} ~ ${stepNames[stepNames.length - 1]}`
}

// 格式化时间差
const formatTimeAgo = (dateString: string): string => {
  const date = new Date(dateString)
  const now = new Date()
  const diffMs = now.getTime() - date.getTime()
  const diffMins = Math.floor(diffMs / (1000 * 60))
  const diffHours = Math.floor(diffMs / (1000 * 60 * 60))
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24))
  
  if (diffMins < 1) return '刚刚'
  if (diffMins < 60) return `${diffMins}分钟前`
  if (diffHours < 24) return `${diffHours}小时前`
  if (diffDays < 7) return `${diffDays}天前`
  
  return date.toLocaleDateString('zh-CN', {
    month: 'short',
    day: 'numeric'
  })
}

const handleAdd = (description: string) => {
  emit('add', description)
}
</script>

<style scoped>
.todos-detail-card {
  height: 100%;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
}

.header-left {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.header-stats {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.stat-badge {
  padding: 4px 8px;
  background: #f5f7fa;
  border-radius: 4px;
  font-size: 12px;
  color: #606266;
}

.add-todo-btn {
  flex-shrink: 0;
}

.todo-input-wrapper {
  margin-bottom: 16px;
  padding: 16px;
  background: #f5f7fa;
  border-radius: 8px;
}

.todos-list {
  min-height: 200px;
}

.empty-todos {
  padding: 60px 0;
  text-align: center;
}

.todo-items {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.todo-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 16px;
  background: #fff;
  border: 1px solid #ebeef5;
  border-radius: 8px;
  transition: all 0.3s;
  position: relative;
}

.todo-item:hover {
  border-color: #409eff;
  box-shadow: 0 2px 12px rgba(64, 158, 255, 0.1);
  transform: translateY(-2px);
}

.todo-item-completed {
  opacity: 0.7;
  background: #f5f7fa;
}

.todo-checkbox {
  flex-shrink: 0;
  cursor: pointer;
}

.checkbox-circle {
  width: 24px;
  height: 24px;
  border: 2px solid #dcdfe6;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s;
  background: #fff;
}

.checkbox-circle.checked {
  background: #67c23a;
  border-color: #67c23a;
}

.check-icon {
  color: #fff;
  font-size: 14px;
}

.todo-status-indicator {
  width: 4px;
  background: #e6a23c;
  border-radius: 2px;
  flex-shrink: 0;
  transition: all 0.3s;
}

.todo-status-indicator.completed {
  background: #67c23a;
}

.todo-content {
  flex: 1;
  min-width: 0;
}

.todo-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
  flex-wrap: wrap;
  gap: 8px;
}

.todo-header-left {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.project-name {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
}

.step-range-tag {
  font-size: 11px;
}

.todo-time {
  font-size: 12px;
  color: #909399;
}

.todo-description-row {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
}

.todo-description {
  flex: 1;
  font-size: 14px;
  color: #606266;
  line-height: 1.6;
  word-break: break-word;
}

.todo-description.completed {
  text-decoration: line-through;
  color: #909399;
}

.todo-actions {
  display: flex;
  gap: 4px;
  flex-shrink: 0;
  opacity: 0;
  transition: opacity 0.2s;
}

.todo-item:hover .todo-actions {
  opacity: 1;
}

.action-btn {
  padding: 4px 8px;
}

.step-popover {
  padding: 8px;
}

.step-popover-title {
  font-size: 12px;
  color: #909399;
  margin-bottom: 8px;
}

.step-list {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.step-tag {
  font-size: 11px;
}

@media (max-width: 768px) {
  .todo-item {
    flex-direction: column;
  }

  .todo-description-row {
    flex-direction: column;
  }

  .todo-actions {
    width: 100%;
    justify-content: flex-end;
    opacity: 1;
  }
}
</style>

