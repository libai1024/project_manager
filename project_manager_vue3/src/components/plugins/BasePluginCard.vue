<template>
  <el-card 
    :class="['base-plugin-card', cardClass]" 
    v-if="isEnabled"
  >
    <template #header>
      <PluginCardHeader
        :title="title"
        :subtitle="subtitle"
        :icon="icon"
        :icon-gradient="iconGradient"
      >
        <template #actions>
          <slot name="header-actions" />
        </template>
      </PluginCardHeader>
    </template>

    <slot />
  </el-card>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import type { Component } from 'vue'
import PluginCardHeader from './PluginCardHeader.vue'
import { usePluginSettings } from '@/composables/usePluginSettings'
import type { PluginType } from '@/composables/usePluginSettings'

interface Props {
  projectId: number
  pluginType: PluginType
  title: string
  subtitle?: string
  icon: Component | string
  iconGradient?: [string, string]
  cardClass?: string
}

const props = withDefaults(defineProps<Props>(), {
  subtitle: '',
  iconGradient: () => ['#409eff', '#66b1ff'],
  cardClass: ''
})

const { isProjectEnabled, loadPluginSettings } = usePluginSettings()
const isEnabled = computed(() => isProjectEnabled(props.projectId, props.pluginType))

// 组件挂载时加载插件设置
onMounted(() => {
  loadPluginSettings()
})
</script>

<style scoped>
.base-plugin-card {
  margin-top: 20px;
}

.base-plugin-card :deep(.el-card__header) {
  padding: 16px 20px;
  border-bottom: 1px solid #ebeef5;
}

.base-plugin-card :deep(.el-card__body) {
  padding: 20px;
}
</style>

