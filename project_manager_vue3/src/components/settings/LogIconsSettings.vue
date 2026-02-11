<template>
  <div class="log-icons-settings-section">
    <div class="section-header">
      <div class="section-title">
        <h3>项目日志图标设置</h3>
        <p class="section-desc">
          自定义项目日志中不同操作类型显示的图标，让日志更直观易识别。
        </p>
      </div>
      <el-button type="warning" @click="$emit('reset')">
        <el-icon><Refresh /></el-icon>
        重置为默认
      </el-button>
    </div>
    <div class="log-icons-settings-body">
      <el-card shadow="never" class="setting-card">
        <div class="log-icons-list">
          <div
            v-for="(actionName, action) in logActionNames"
            :key="action"
            class="log-icon-item"
          >
            <div class="icon-item-header">
              <div class="icon-item-label">
                <span class="action-name">{{ actionName }}</span>
                <span class="action-code">({{ action }})</span>
              </div>
              <el-button
                type="primary"
                size="small"
                @click="$emit('select-icon', action as LogActionType)"
              >
                <el-icon><Edit /></el-icon>
                选择图标
              </el-button>
            </div>
            <div class="icon-item-preview">
              <div class="preview-label">当前图标：</div>
              <div class="preview-icon">
                <el-icon :size="24">
                  <component :is="getLogIcon(action as LogActionType)" />
                </el-icon>
                <span class="icon-name">{{ currentIconName(action as LogActionType) }}</span>
              </div>
            </div>
          </div>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { Refresh, Edit } from '@element-plus/icons-vue'
import { useLogIconConfig, type LogActionType, logActionNames } from '@/composables/useLogIconConfig'

const { iconConfig, getIcon } = useLogIconConfig()

defineEmits<{
  'reset': []
  'select-icon': [action: LogActionType]
}>()

const getLogIcon = (action: LogActionType) => {
  return getIcon(action)
}

const currentIconName = (action: LogActionType): string => {
  return iconConfig.value[action] || 'InfoFilled'
}
</script>

<style scoped>
.log-icons-settings-section {
  padding: 20px 0;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px;
  flex-wrap: wrap;
  gap: 16px;
}

.section-title h3 {
  margin: 0 0 8px 0;
  font-size: 20px;
  font-weight: 600;
  color: #303133;
}

.section-desc {
  margin: 0;
  font-size: 14px;
  color: #909399;
  line-height: 1.5;
}

.setting-card {
  border: 1px solid #ebeef5;
  border-radius: 8px;
}

.log-icons-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
  padding: 20px;
}

.log-icon-item {
  padding: 16px;
  border: 1px solid #ebeef5;
  border-radius: 8px;
  background: #fff;
  transition: all 0.3s;
}

.log-icon-item:hover {
  border-color: #409eff;
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.1);
}

.icon-item-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.icon-item-label {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.action-name {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
}

.action-code {
  font-size: 12px;
  color: #909399;
  font-family: monospace;
}

.icon-item-preview {
  display: flex;
  align-items: center;
  gap: 12px;
  padding-top: 12px;
  border-top: 1px solid #ebeef5;
}

.preview-label {
  font-size: 12px;
  color: #909399;
}

.preview-icon {
  display: flex;
  align-items: center;
  gap: 8px;
}

.icon-name {
  font-size: 12px;
  color: #606266;
  font-family: monospace;
}

@media (max-width: 768px) {
  .log-icons-list {
    grid-template-columns: 1fr;
  }
}
</style>

