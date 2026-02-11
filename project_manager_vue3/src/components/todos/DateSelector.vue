<template>
  <el-card class="date-selector-card">
    <template #header>
      <div class="card-header">
        <span>日期选择</span>
      </div>
    </template>
    
    <div class="date-selector" ref="dateSelectorRef" @scroll="handleScroll">
      <div
        v-for="dateItem in dateList"
        :key="dateItem.date"
        class="date-item"
        :class="{
          'date-item-today': dateItem.isToday,
          'date-item-selected': dateItem.date === selectedDate,
          'date-item-has-todos': dateItem.totalCount > 0
        }"
        @click="$emit('select', dateItem.date)"
        :data-date="dateItem.date"
      >
        <div class="date-weekday">{{ dateItem.weekday }}</div>
        <div class="date-day">{{ dateItem.day }}</div>
        <div class="date-month">{{ dateItem.month }}月</div>
        <div v-if="dateItem.totalCount > 0" class="date-stats">
          <div class="date-stat-item">
            <span class="stat-label">待办</span>
            <span class="stat-value todo">{{ dateItem.todoCount }}</span>
          </div>
          <div class="date-stat-item">
            <span class="stat-label">完成</span>
            <span class="stat-value completed">{{ dateItem.completedCount }}</span>
          </div>
        </div>
      </div>
    </div>
  </el-card>
</template>

<script setup lang="ts">
import { ref, computed, watch, nextTick } from 'vue'

interface DateItem {
  date: string
  day: number
  month: number
  weekday: string
  isToday: boolean
  todoCount: number
  completedCount: number
  totalCount: number
}

interface Props {
  selectedDate: string
  today: string
  calendarData: Array<{
    date: string
    todo_count: number
    completed_count: number
  }>
}

const props = defineProps<Props>()

const emit = defineEmits<{
  'select': [date: string]
  'scroll': []
}>()

const dateSelectorRef = ref<HTMLElement>()

const weekdays = ['日', '一', '二', '三', '四', '五', '六']

// 本地日期工具
const toLocalDateString = (d: Date = new Date()): string => {
  const y = d.getFullYear()
  const m = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${y}-${m}-${day}`
}

const parseLocalDate = (str: string): Date => {
  const [y, m, d] = str.split('-').map(Number)
  return new Date(y, (m || 1) - 1, d || 1)
}

// 日期列表（最近30天）
const dateList = computed<DateItem[]>(() => {
  const list: DateItem[] = []
  const todayDate = parseLocalDate(props.today)
  
  for (let i = -7; i <= 30; i++) {
    const date = new Date(todayDate)
    date.setDate(date.getDate() + i)
    const dateStr = toLocalDateString(date)
    const isToday = dateStr === props.today
    
    const calendarItem = props.calendarData.find(item => item.date === dateStr)
    const todoCount = calendarItem ? calendarItem.todo_count : 0
    const completedCount = calendarItem ? calendarItem.completed_count : 0
    const totalCount = todoCount + completedCount
    
    list.push({
      date: dateStr,
      day: date.getDate(),
      month: date.getMonth() + 1,
      weekday: weekdays[date.getDay()],
      isToday,
      todoCount,
      completedCount,
      totalCount
    })
  }
  
  return list
})

const handleScroll = () => {
  emit('scroll')
}

// 监听选中日期变化，自动滚动到选中项
watch(() => props.selectedDate, (newDate) => {
  nextTick(() => {
    if (dateSelectorRef.value) {
      const selectedItem = dateSelectorRef.value.querySelector(`[data-date="${newDate}"]`)
      if (selectedItem) {
        selectedItem.scrollIntoView({ block: 'center', behavior: 'smooth' })
      }
    }
  })
})
</script>

<style scoped>
.date-selector-card {
  height: 100%;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.date-selector {
  max-height: calc(100vh - 200px);
  overflow-y: auto;
  padding: 8px 0;
}

.date-item {
  padding: 12px 16px;
  margin-bottom: 8px;
  border: 2px solid #ebeef5;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
  background: #fff;
  text-align: center;
}

.date-item:hover {
  border-color: #409eff;
  background: #ecf5ff;
  transform: translateX(4px);
}

.date-item-today {
  border-color: #409eff;
  background: linear-gradient(135deg, #ecf5ff 0%, #ffffff 100%);
  font-weight: 600;
}

.date-item-selected {
  border-color: #409eff;
  background: #409eff;
  color: #fff;
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.3);
}

.date-item-selected .date-weekday,
.date-item-selected .date-day,
.date-item-selected .date-month {
  color: #fff;
}

.date-item-has-todos {
  border-left: 4px solid #67c23a;
}

.date-weekday {
  font-size: 12px;
  color: #909399;
  margin-bottom: 4px;
}

.date-day {
  font-size: 24px;
  font-weight: 600;
  color: #303133;
  line-height: 1;
  margin-bottom: 4px;
}

.date-month {
  font-size: 12px;
  color: #909399;
  margin-bottom: 8px;
}

.date-stats {
  display: flex;
  justify-content: center;
  gap: 12px;
  margin-top: 8px;
  padding-top: 8px;
  border-top: 1px solid rgba(0, 0, 0, 0.1);
}

.date-item-selected .date-stats {
  border-top-color: rgba(255, 255, 255, 0.3);
}

.date-stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
}

.stat-label {
  font-size: 10px;
  opacity: 0.8;
}

.date-item-selected .stat-label {
  color: rgba(255, 255, 255, 0.9);
}

.stat-value {
  font-size: 14px;
  font-weight: 600;
}

.stat-value.todo {
  color: #e6a23c;
}

.date-item-selected .stat-value.todo {
  color: #fff;
}

.stat-value.completed {
  color: #67c23a;
}

.date-item-selected .stat-value.completed {
  color: #fff;
}

/* 滚动条样式 */
.date-selector::-webkit-scrollbar {
  width: 6px;
}

.date-selector::-webkit-scrollbar-track {
  background: #f5f7fa;
  border-radius: 3px;
}

.date-selector::-webkit-scrollbar-thumb {
  background: #c0c4cc;
  border-radius: 3px;
}

.date-selector::-webkit-scrollbar-thumb:hover {
  background: #909399;
}
</style>

