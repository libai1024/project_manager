<template>
  <div class="templates-section">
    <div class="section-header">
      <div class="section-title">
        <h3>项目步骤模板管理</h3>
        <p class="section-desc">管理项目步骤时间线模板，创建项目时可选择使用</p>
      </div>
      <el-button type="primary" @click="$emit('create')">
        <el-icon><Plus /></el-icon>
        新建模板
      </el-button>
    </div>

    <div class="templates-list">
      <div
        v-for="template in templates"
        :key="template.id"
        class="template-item"
        :class="{ 'is-default': template.is_default }"
      >
        <div class="template-info">
          <div class="template-header">
            <span class="template-name">{{ template.name }}</span>
            <el-tag v-if="template.is_default" type="success" size="small">默认</el-tag>
          </div>
          <div v-if="template.description" class="template-description">
            {{ template.description }}
          </div>
          <div class="template-steps-preview">
            <span class="steps-label">步骤列表：</span>
            <div class="steps-tags">
              <el-tag
                v-for="(step, index) in template.steps.slice(0, 5)"
                :key="index"
                size="small"
                class="step-tag"
              >
                {{ step }}
              </el-tag>
              <el-tag v-if="template.steps.length > 5" size="small" type="info">
                +{{ template.steps.length - 5 }} 更多
              </el-tag>
            </div>
          </div>
          <div class="template-meta">
            <span class="template-steps-count">共 {{ template.steps.length }} 个步骤</span>
            <span class="template-time">创建于 {{ formatTime(template.created_at) }}</span>
          </div>
        </div>
        <div class="template-actions">
          <el-dropdown trigger="click" @command="(cmd) => $emit('action', cmd, template)">
            <el-button type="primary" size="small" :icon="More">
              更多操作
            </el-button>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="view" :icon="View">
                  查看详情
                </el-dropdown-item>
                <el-dropdown-item command="copy" :icon="CopyDocument">
                  复制模板
                </el-dropdown-item>
                <el-dropdown-item
                  v-if="!template.is_default"
                  command="edit"
                  :icon="Edit"
                >
                  编辑模板
                </el-dropdown-item>
                <el-dropdown-item
                  v-if="!template.is_default"
                  command="rename"
                  :icon="EditPen"
                >
                  重命名
                </el-dropdown-item>
                <el-dropdown-item
                  v-if="template.is_default"
                  command="edit"
                  :icon="Edit"
                  disabled
                >
                  默认模板不可编辑
                </el-dropdown-item>
                <el-dropdown-item
                  v-if="!template.is_default"
                  command="delete"
                  :icon="Delete"
                  divided
                >
                  删除模板
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </div>
      <el-empty v-if="templates.length === 0" description="暂无模板，点击上方按钮创建" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { Plus, More, View, CopyDocument, Edit, EditPen, Delete } from '@element-plus/icons-vue'
import type { StepTemplate } from '@/api/stepTemplate'

interface Props {
  templates: StepTemplate[]
}

defineProps<Props>()

defineEmits<{
  'create': []
  'action': [command: string, template: StepTemplate]
}>()

const formatTime = (timeString: string): string => {
  const date = new Date(timeString)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}
</script>

<style scoped>
.templates-section {
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

.templates-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 20px;
}

.template-item {
  padding: 20px;
  border: 1px solid #ebeef5;
  border-radius: 8px;
  background: #fff;
  transition: all 0.3s;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 16px;
}

.template-item:hover {
  border-color: #409eff;
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.15);
  transform: translateY(-2px);
}

.template-item.is-default {
  border-color: #67c23a;
  background: linear-gradient(135deg, #f0f9ff 0%, #ffffff 100%);
}

.template-info {
  flex: 1;
  min-width: 0;
}

.template-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
}

.template-name {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.template-description {
  font-size: 13px;
  color: #606266;
  line-height: 1.6;
  margin-bottom: 12px;
}

.template-steps-preview {
  margin-bottom: 12px;
}

.steps-label {
  font-size: 12px;
  color: #909399;
  margin-right: 8px;
}

.steps-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 6px;
}

.step-tag {
  font-size: 11px;
}

.template-meta {
  display: flex;
  gap: 16px;
  font-size: 12px;
  color: #909399;
}

.template-steps-count {
  font-weight: 500;
}

.template-actions {
  flex-shrink: 0;
}

@media (max-width: 768px) {
  .templates-list {
    grid-template-columns: 1fr;
  }

  .template-item {
    flex-direction: column;
  }
}
</style>

