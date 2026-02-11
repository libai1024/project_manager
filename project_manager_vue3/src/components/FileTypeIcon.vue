<template>
  <div class="file-type-icon" :class="[`file-type-${fileType}`, sizeClass]">
    <!-- PDF -->
    <span v-if="fileType === 'pdf'" class="file-icon-text">PDF</span>
    <!-- Word -->
    <span v-else-if="fileType === 'word'" class="file-icon-text">DOC</span>
    <!-- Excel -->
    <span v-else-if="fileType === 'excel'" class="file-icon-text">XLS</span>
    <!-- PowerPoint -->
    <span v-else-if="fileType === 'ppt'" class="file-icon-text">PPT</span>
    <!-- WPS -->
    <span v-else-if="fileType === 'wps'" class="file-icon-text">WPS</span>
    <!-- 压缩包 -->
    <span v-else-if="fileType === 'archive'" class="file-icon-text">ZIP</span>
    <!-- 图片、视频、音频使用图标 -->
    <el-icon v-else-if="fileType === 'image'" :size="iconSize">
      <Picture />
    </el-icon>
    <el-icon v-else-if="fileType === 'video'" :size="iconSize">
      <VideoPlay />
    </el-icon>
    <el-icon v-else-if="fileType === 'audio'" :size="iconSize">
      <Headset />
    </el-icon>
    <!-- 代码文件 -->
    <span v-else-if="fileType === 'code'" class="file-icon-text">CODE</span>
    <!-- 文本文件 -->
    <span v-else-if="fileType === 'text'" class="file-icon-text">TXT</span>
    <!-- 默认文档 -->
    <el-icon v-else :size="iconSize">
      <Document />
    </el-icon>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import {
  Document,
  Picture,
  VideoPlay,
  Headset,
} from '@element-plus/icons-vue'
import { getFileIcon, getFileIconColor, type FileIconType } from '@/utils/fileIcons'

interface Props {
  fileName: string
  size?: 'small' | 'medium' | 'large'
}

const props = withDefaults(defineProps<Props>(), {
  size: 'medium',
})

const fileType = computed<FileIconType>(() => getFileIcon(props.fileName) as FileIconType)
const iconColor = computed(() => getFileIconColor(fileType.value))

const iconSize = computed(() => {
  const sizeMap = {
    small: 16,
    medium: 28,
    large: 40,
  }
  return sizeMap[props.size]
})

const sizeClass = computed(() => `size-${props.size}`)
</script>

<style scoped>
.file-type-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition: transform 0.3s;
  font-weight: 600;
}

.file-type-icon:hover {
  transform: scale(1.1);
}

.file-icon-text {
  font-size: v-bind('iconSize + "px"');
  font-weight: 700;
  letter-spacing: 0.5px;
  user-select: none;
}

/* PDF - 红色 */
.file-type-pdf .file-icon-text {
  color: #dc3545;
}

.file-type-pdf :deep(.el-icon) {
  color: #dc3545 !important;
}

/* Word - 蓝色 */
.file-type-word .file-icon-text {
  color: #2b579a;
}

.file-type-word :deep(.el-icon) {
  color: #2b579a !important;
}

/* Excel - 绿色 */
.file-type-excel .file-icon-text {
  color: #1d6f42;
}

.file-type-excel :deep(.el-icon) {
  color: #1d6f42 !important;
}

/* PowerPoint - 橙色 */
.file-type-ppt .file-icon-text {
  color: #d04423;
}

.file-type-ppt :deep(.el-icon) {
  color: #d04423 !important;
}

/* WPS - 蓝色 */
.file-type-wps .file-icon-text {
  color: #0066cc;
}

.file-type-wps :deep(.el-icon) {
  color: #0066cc !important;
}

/* 压缩包 - 橙色 */
.file-type-archive .file-icon-text {
  color: #ff9800;
}

.file-type-archive :deep(.el-icon) {
  color: #ff9800 !important;
}

/* 图片 - 粉色 */
.file-type-image :deep(.el-icon) {
  color: #e91e63 !important;
}

/* 视频 - 紫色 */
.file-type-video :deep(.el-icon) {
  color: #9c27b0 !important;
}

/* 音频 - 青色 */
.file-type-audio :deep(.el-icon) {
  color: #00bcd4 !important;
}

/* 文本 - 蓝灰色 */
.file-type-text .file-icon-text {
  color: #607d8b;
}

.file-type-text :deep(.el-icon) {
  color: #607d8b !important;
}

/* 代码 - 深紫色 */
.file-type-code .file-icon-text {
  color: #673ab7;
}

.file-type-code :deep(.el-icon) {
  color: #673ab7 !important;
}

/* 默认 - Element Plus 蓝色 */
.file-type-default :deep(.el-icon) {
  color: #409eff !important;
}
</style>

