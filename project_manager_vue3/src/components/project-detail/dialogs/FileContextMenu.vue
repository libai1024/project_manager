<template>
  <div
    v-if="visible"
    class="context-menu"
    :style="{ left: position.x + 'px', top: position.y + 'px' }"
    @click.stop
    @mouseleave="$emit('close')"
  >
    <div class="context-menu-item" @click="handleAction('preview')">
      <el-icon><View /></el-icon>
      <span>预览</span>
    </div>
    <div class="context-menu-item" @click="handleAction('download')">
      <el-icon><Download /></el-icon>
      <span>下载</span>
    </div>
    <div class="context-menu-divider"></div>
    <div class="context-menu-item" @click="handleAction('rename')">
      <el-icon><Edit /></el-icon>
      <span>重命名</span>
    </div>
    <div class="context-menu-item" @click="handleAction('move')">
      <el-icon><Folder /></el-icon>
      <span>移入文件夹</span>
    </div>
    <div class="context-menu-item" @click="handleAction('move-other')">
      <el-icon><FolderAdd /></el-icon>
      <span>移入其他文件夹</span>
    </div>
    <template v-if="showGraduationTags">
      <div class="context-menu-divider"></div>
      <div class="context-menu-item" @click="showSubMenu = true">
        <el-icon><Document /></el-icon>
        <span>标记为毕设文件</span>
        <el-icon class="menu-arrow"><ArrowRight /></el-icon>
      </div>
      <div class="context-menu-divider"></div>
    </template>
    <div class="context-menu-item danger" @click="handleAction('delete')">
      <el-icon><Delete /></el-icon>
      <span>删除</span>
    </div>

    <!-- 毕设标记子菜单 -->
    <div
      v-if="showSubMenu"
      class="context-submenu"
      :style="submenuStyle"
      @click.stop
      @mouseleave="showSubMenu = false"
    >
      <div
        v-for="(config, type) in graduationFileTypes"
        :key="type"
        class="context-menu-item"
        @click="handleGraduationTag(type as GraduationFileType)"
      >
        <el-icon><component :is="getGraduationIcon(config.icon)" /></el-icon>
        <span>{{ config.label }}</span>
      </div>
      <div class="context-menu-divider"></div>
      <div class="context-menu-item" @click="handleAction('untag-graduation')">
        <el-icon><Delete /></el-icon>
        <span>取消标记</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import {
  View,
  Download,
  Edit,
  Folder,
  FolderAdd,
  Document,
  Delete,
  ArrowRight,
  Clock,
  Upload,
  Star,
  Check,
} from '@element-plus/icons-vue'
import { graduationFileTypes, type GraduationFileType } from '@/types/plugin'

const props = defineProps<{
  visible: boolean
  position: { x: number; y: number }
  showGraduationTags: boolean
}>()

const emit = defineEmits<{
  (e: 'close'): void
  (e: 'action', action: string): void
  (e: 'graduation-tag', type: GraduationFileType): void
}>()

const showSubMenu = ref(false)

const submenuStyle = computed(() => ({
  left: '100%',
  top: '0'
}))

const iconMap: Record<string, any> = {
  Clock,
  Upload,
  Star,
  Check,
  Document,
  Delete
}

const getGraduationIcon = (iconName: string) => {
  return iconMap[iconName] || Document
}

const handleAction = (action: string) => {
  emit('action', action)
  emit('close')
}

const handleGraduationTag = (type: GraduationFileType) => {
  emit('graduation-tag', type)
  emit('close')
}
</script>

<style scoped>
.context-menu {
  position: fixed;
  background: #fff;
  border-radius: 4px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.15);
  padding: 4px 0;
  z-index: 3000;
  min-width: 150px;
}

.context-menu-item {
  display: flex;
  align-items: center;
  padding: 8px 16px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.context-menu-item:hover {
  background-color: #f5f7fa;
}

.context-menu-item .el-icon {
  margin-right: 8px;
}

.context-menu-item.danger {
  color: #f56c6c;
}

.context-menu-item.danger:hover {
  background-color: #fef0f0;
}

.context-menu-item .menu-arrow {
  margin-left: auto;
  margin-right: 0;
}

.context-menu-divider {
  height: 1px;
  background-color: #e4e7ed;
  margin: 4px 0;
}

.context-submenu {
  position: absolute;
  background: #fff;
  border-radius: 4px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.15);
  padding: 4px 0;
  min-width: 150px;
}
</style>
