<template>
  <el-dialog
    :model-value="visible"
    title="选择步骤模板"
    width="600px"
    @update:model-value="$emit('update:visible', $event)"
    @close="handleClose"
  >
    <div class="template-selector">
      <el-alert
        type="info"
        :closable="false"
        show-icon
        style="margin-bottom: 20px;"
      >
        <template #title>
          <span>选择模板后，将替换当前项目的所有步骤。此操作不可撤销，请谨慎操作。</span>
        </template>
      </el-alert>

      <el-select
        v-model="selectedTemplateId"
        placeholder="请选择步骤模板"
        style="width: 100%"
        filterable
      >
        <el-option
          v-for="template in templates"
          :key="template.id"
          :label="template.name + (template.is_default ? '（默认）' : '')"
          :value="template.id"
        >
          <div class="template-option">
            <div class="template-option-name">
              <span>{{ template.name }}</span>
              <el-tag v-if="template.is_default" type="success" size="small" style="margin-left: 8px;">
                默认
              </el-tag>
            </div>
            <div v-if="template.description" class="template-option-desc">
              {{ template.description }}
            </div>
            <div class="template-option-steps">
              共 {{ template.steps.length }} 个步骤
            </div>
          </div>
        </el-option>
      </el-select>

      <div v-if="selectedTemplateId" class="template-preview">
        <div class="preview-title">模板预览：</div>
        <div class="preview-steps">
          <el-tag
            v-for="(step, index) in selectedTemplate?.steps || []"
            :key="index"
            size="small"
            style="margin: 4px;"
          >
            {{ index + 1 }}. {{ step }}
          </el-tag>
        </div>
      </div>
    </div>

    <template #footer>
      <el-button @click="$emit('update:visible', false)">取消</el-button>
      <el-button
        type="primary"
        :disabled="!selectedTemplateId"
        @click="handleApply"
      >
        应用模板
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import type { StepTemplate } from '@/api/stepTemplate'

const props = defineProps<{
  visible: boolean
  templates: StepTemplate[]
}>()

const emit = defineEmits<{
  (e: 'update:visible', value: boolean): void
  (e: 'apply', templateId: number): void
}>()

const selectedTemplateId = ref<number | null>(null)

const selectedTemplate = computed(() =>
  props.templates.find(t => t.id === selectedTemplateId.value)
)

const handleClose = () => {
  selectedTemplateId.value = null
}

const handleApply = () => {
  if (selectedTemplateId.value) {
    emit('apply', selectedTemplateId.value)
  }
}

watch(() => props.visible, (val) => {
  if (!val) {
    selectedTemplateId.value = null
  }
})
</script>

<style scoped>
.template-option {
  padding: 4px 0;
}

.template-option-name {
  display: flex;
  align-items: center;
}

.template-option-desc {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

.template-option-steps {
  font-size: 12px;
  color: #606266;
  margin-top: 2px;
}

.template-preview {
  margin-top: 20px;
}

.preview-title {
  font-weight: 500;
  margin-bottom: 10px;
}

.preview-steps {
  display: flex;
  flex-wrap: wrap;
}
</style>
