import { ref, computed } from 'vue'
import {
  Plus,
  Check,
  Delete,
  Edit,
  Camera,
  InfoFilled,
  Document,
  Clock,
  Star,
  StarFilled,
  Warning,
  Refresh,
  User,
  Upload,
  Link,
  TopRight,
  Rank,
  ArrowDown,
  Loading,
} from '@element-plus/icons-vue'

// 日志操作类型
export type LogActionType = 
  | 'project_created'
  | 'todo_created'
  | 'todo_completed'
  | 'todo_deleted'
  | 'step_updated'
  | 'project_updated'
  | 'project_snapshot'

// 日志操作类型的中文名称
export const logActionNames: Record<LogActionType, string> = {
  project_created: '创建项目',
  todo_created: '创建待办',
  todo_completed: '完成待办',
  todo_deleted: '删除待办',
  step_updated: '更新步骤',
  project_updated: '更新项目',
  project_snapshot: '项目快照',
}

// 所有可用的图标
export const availableIcons = {
  Plus,
  Check,
  Delete,
  Edit,
  Camera,
  InfoFilled,
  Document,
  Clock,
  Star,
  StarFilled,
  Warning,
  Refresh,
  User,
  Upload,
  Link,
  TopRight,
  Rank,
  ArrowDown,
  Loading,
}

// 图标名称列表（用于选择器）
export const iconNames = Object.keys(availableIcons) as Array<keyof typeof availableIcons>

// 默认图标配置
const defaultIconConfig: Record<LogActionType, keyof typeof availableIcons> = {
  project_created: 'Plus',
  todo_created: 'Plus',
  todo_completed: 'Check',
  todo_deleted: 'Delete',
  step_updated: 'Edit',
  project_updated: 'Edit',
  project_snapshot: 'Camera',
}

// 从 localStorage 加载配置
const loadIconConfig = (): Record<LogActionType, keyof typeof availableIcons> => {
  try {
    const stored = localStorage.getItem('logIconConfig')
    if (stored) {
      const parsed = JSON.parse(stored)
      // 合并默认配置，确保所有类型都有图标
      return { ...defaultIconConfig, ...parsed }
    }
  } catch (error) {
    console.error('加载日志图标配置失败:', error)
  }
  return { ...defaultIconConfig }
}

// 保存配置到 localStorage
const saveIconConfig = (config: Record<LogActionType, keyof typeof availableIcons>) => {
  try {
    localStorage.setItem('logIconConfig', JSON.stringify(config))
  } catch (error) {
    console.error('保存日志图标配置失败:', error)
  }
}

// 组合式函数
export function useLogIconConfig() {
  const iconConfig = ref<Record<LogActionType, keyof typeof availableIcons>>(loadIconConfig())

  // 获取指定操作类型的图标组件
  const getIcon = (action: LogActionType) => {
    const iconName = iconConfig.value[action] || defaultIconConfig[action]
    return availableIcons[iconName] || InfoFilled
  }

  // 更新图标配置
  const updateIcon = (action: LogActionType, iconName: keyof typeof availableIcons) => {
    iconConfig.value[action] = iconName
    saveIconConfig(iconConfig.value)
  }

  // 重置为默认配置
  const resetToDefault = () => {
    iconConfig.value = { ...defaultIconConfig }
    saveIconConfig(iconConfig.value)
  }

  // 获取当前配置
  const getConfig = () => ({ ...iconConfig.value })

  return {
    iconConfig,
    getIcon,
    updateIcon,
    resetToDefault,
    getConfig,
  }
}

