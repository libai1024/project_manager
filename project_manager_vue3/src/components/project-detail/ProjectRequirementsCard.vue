<template>
  <el-card v-if="requirements" class="requirements-card">
    <template #header>
      <div class="card-header">
        <span>项目需求</span>
      </div>
    </template>
    <div class="requirements-content-wrapper">
      <div 
        ref="requirementsContentRef"
        class="requirements-content"
        :class="{ 'requirements-collapsed': !requirementsExpanded && shouldShowExpandButton }"
        v-html="renderedRequirements"
      ></div>
      <div 
        v-if="shouldShowExpandButton"
        class="requirements-expand-overlay"
        :class="{ 'is-expanded': requirementsExpanded }"
      >
        <el-button
          type="text"
          class="expand-button"
          @click="requirementsExpanded = !requirementsExpanded"
        >
          <el-icon>
            <ArrowDown v-if="!requirementsExpanded" />
            <ArrowUp v-else />
          </el-icon>
          <span>{{ requirementsExpanded ? '收起' : '展开' }}</span>
        </el-button>
      </div>
    </div>
  </el-card>
</template>

<script setup lang="ts">
import { ref, computed, nextTick, watch } from 'vue'
import { ArrowDown, ArrowUp } from '@element-plus/icons-vue'
import MarkdownIt from 'markdown-it'

const props = defineProps<{
  requirements: string | null | undefined
}>()

const md = new MarkdownIt()
const requirementsExpanded = ref(false)
const requirementsContentRef = ref<HTMLElement | null>(null)
const shouldShowExpandButton = ref(false)

const renderedRequirements = computed(() => {
  if (!props.requirements) return ''
  return md.render(props.requirements)
})

const checkRequirementsHeight = () => {
  nextTick(() => {
    if (requirementsContentRef.value && props.requirements) {
      shouldShowExpandButton.value = requirementsContentRef.value.scrollHeight > 300
    } else {
      shouldShowExpandButton.value = false
    }
  })
}

watch(() => props.requirements, checkRequirementsHeight, { immediate: true })
</script>

<style scoped>
.requirements-card {
  margin-bottom: 20px;
}

.requirements-content-wrapper {
  position: relative;
}

.requirements-content {
  max-height: 300px;
  overflow: hidden;
  transition: max-height 0.3s ease;
}

.requirements-content.requirements-collapsed {
  max-height: 300px;
}

.requirements-content:not(.requirements-collapsed) {
  max-height: none;
  overflow: visible;
}

.requirements-expand-overlay {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 80px;
  background: linear-gradient(to bottom, transparent, rgba(255, 255, 255, 0.95));
  display: flex;
  align-items: flex-end;
  justify-content: center;
  padding-bottom: 10px;
  pointer-events: none;
  transition: opacity 0.3s;
}

.requirements-expand-overlay.is-expanded {
  opacity: 0;
  pointer-events: none;
}

.expand-button {
  pointer-events: auto;
  color: #409eff;
}

/* 移动端样式 */
@media (max-width: 768px) {
  .requirements-card {
    margin-bottom: 12px;
  }

  .requirements-card :deep(.el-card__header) {
    padding: 12px;
  }

  .requirements-card :deep(.el-card__body) {
    padding: 12px;
  }

  .requirements-content {
    max-height: 200px;
    font-size: 13px;
  }

  .requirements-content.requirements-collapsed {
    max-height: 200px;
  }

  .requirements-expand-overlay {
    height: 60px;
  }

  .expand-button {
    font-size: 12px;
  }
}

@media (max-width: 480px) {
  .requirements-content {
    font-size: 12px;
    max-height: 150px;
  }

  .requirements-content.requirements-collapsed {
    max-height: 150px;
  }
}
</style>

