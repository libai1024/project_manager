<template>
  <div class="plugin-card-header">
    <div class="header-left">
      <div class="icon-wrapper" :style="iconStyle">
        <el-icon class="plugin-icon">
          <component :is="icon" />
        </el-icon>
      </div>
      <div class="title-wrapper">
        <span class="plugin-title">{{ title }}</span>
        <span v-if="subtitle" class="plugin-subtitle">{{ subtitle }}</span>
      </div>
    </div>
    <div class="header-actions">
      <slot name="actions">
        <!-- 默认操作按钮插槽 -->
      </slot>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { Component } from 'vue'

interface Props {
  title: string
  subtitle?: string
  icon: Component | string
  iconGradient?: [string, string] // [startColor, endColor]
}

const props = withDefaults(defineProps<Props>(), {
  subtitle: '',
  iconGradient: () => ['#409eff', '#66b1ff']
})

const iconStyle = computed(() => {
  return {
    background: `linear-gradient(135deg, ${props.iconGradient[0]} 0%, ${props.iconGradient[1]} 100%)`
  }
})
</script>

<style scoped>
.plugin-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 4px 0;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.icon-wrapper {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 10px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
  flex-shrink: 0;
}

.plugin-icon {
  font-size: 22px;
  color: #fff;
}

.title-wrapper {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.plugin-title {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
  line-height: 1.2;
}

.plugin-subtitle {
  font-size: 12px;
  color: #909399;
  line-height: 1.2;
}

.header-actions {
  display: flex;
  gap: 8px;
  align-items: center;
}
</style>

