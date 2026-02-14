<template>
  <el-dialog
    :model-value="visible"
    :title="attachment?.file_name || '文件预览'"
    width="90%"
    :close-on-click-modal="false"
    class="file-preview-dialog"
    destroy-on-close
    @update:model-value="$emit('update:visible', $event)"
  >
    <div v-if="attachment" class="preview-container">
      <!-- 图片预览 -->
      <div v-if="isImage" class="preview-image">
        <img v-if="previewUrl" :src="previewUrl" :alt="attachment.file_name" />
        <div v-else class="loading-text">加载中...</div>
      </div>

      <!-- PDF预览 -->
      <div v-else-if="isPdf" class="preview-pdf">
        <iframe v-if="previewUrl" :src="previewUrl" frameborder="0"></iframe>
        <div v-else class="loading-text">加载中...</div>
      </div>

      <!-- 文本文件预览 -->
      <div v-else-if="isText" class="preview-text">
        <pre v-if="textContent" class="text-content">{{ textContent }}</pre>
        <div v-else class="loading-text">加载中...</div>
      </div>

      <!-- 视频预览 -->
      <div v-else-if="isVideo" class="preview-video">
        <video v-if="previewUrl" :src="previewUrl" controls style="width: 100%; max-height: 70vh;"></video>
        <div v-else class="loading-text">加载中...</div>
      </div>

      <!-- 音频预览 -->
      <div v-else-if="isAudio" class="preview-audio">
        <audio v-if="previewUrl" :src="previewUrl" controls style="width: 100%;"></audio>
        <div v-else class="loading-text">加载中...</div>
      </div>

      <!-- Office文档预览 -->
      <div v-else-if="isOffice" class="preview-office">
        <div v-if="officeContent" class="office-content" v-html="officeContent"></div>
        <div v-else class="loading-text">
          <el-icon class="is-loading" style="font-size: 24px; margin-right: 8px;"><Loading /></el-icon>
          正在加载文档...
        </div>
      </div>

      <!-- 其他文件 - 提示下载 -->
      <div v-else class="preview-other">
        <div class="unsupported-preview">
          <el-empty description="该文件类型暂不支持在线预览">
            <template #image>
              <el-icon style="font-size: 80px; color: #909399;"><Document /></el-icon>
            </template>
            <el-button type="primary" @click="handleDownload">
              <el-icon><Download /></el-icon>
              下载文件
            </el-button>
          </el-empty>
        </div>
      </div>
    </div>

    <template #footer>
      <div class="preview-footer">
        <el-button @click="$emit('update:visible', false)">关闭</el-button>
        <el-button v-if="attachment" type="primary" @click="handleDownload">
          <el-icon><Download /></el-icon>
          下载
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { Document, Download, Loading } from '@element-plus/icons-vue'
import type { Attachment } from '@/api/attachment'

const props = defineProps<{
  visible: boolean
  attachment: Attachment | null
  previewUrl: string | null
  textContent: string
  officeContent: string
}>()

const emit = defineEmits<{
  (e: 'update:visible', value: boolean): void
  (e: 'download', attachment: Attachment): void
}>()

// 文件类型检测
const getFileExtension = (filename: string): string => {
  const parts = filename.split('.')
  return parts.length > 1 ? parts[parts.length - 1].toLowerCase() : ''
}

const isImage = computed(() => {
  if (!props.attachment) return false
  const ext = getFileExtension(props.attachment.file_name)
  return ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp', 'svg', 'heic', 'heif', 'tiff', 'tif', 'ico'].includes(ext)
})

const isPdf = computed(() => {
  if (!props.attachment) return false
  return getFileExtension(props.attachment.file_name) === 'pdf'
})

const isText = computed(() => {
  if (!props.attachment) return false
  const ext = getFileExtension(props.attachment.file_name)
  return ['txt', 'md', 'json', 'xml', 'html', 'css', 'js', 'vue', 'py', 'java', 'c', 'cpp', 'h', 'go', 'rs', 'php', 'rb', 'sh', 'jsx', 'tsx', 'swift', 'kt', 'sql', 'yaml', 'yml', 'ini', 'conf', 'log'].includes(ext)
})

const isVideo = computed(() => {
  if (!props.attachment) return false
  const ext = getFileExtension(props.attachment.file_name)
  return ['mp4', 'webm', 'mov', 'avi', 'mkv', 'flv', 'wmv', 'm4v', 'mpeg', 'mpg', '3gp', 'ogv', 'ts', 'mts', 'm2ts'].includes(ext)
})

const isAudio = computed(() => {
  if (!props.attachment) return false
  const ext = getFileExtension(props.attachment.file_name)
  return ['mp3', 'wav', 'ogg', 'flac', 'aac', 'm4a', 'wma', 'aiff', 'aif', 'au', 'opus'].includes(ext)
})

const isOffice = computed(() => {
  if (!props.attachment) return false
  const ext = getFileExtension(props.attachment.file_name)
  return ['doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'wps', 'et', 'dps', 'odt', 'ods', 'odp', 'rtf'].includes(ext)
})

const handleDownload = () => {
  if (props.attachment) {
    emit('download', props.attachment)
  }
}
</script>

<style scoped>
.preview-container {
  min-height: 300px;
}

.preview-image img {
  max-width: 100%;
  max-height: 70vh;
  display: block;
  margin: 0 auto;
}

.preview-pdf iframe,
.preview-video video {
  width: 100%;
  height: 70vh;
}

.preview-text .text-content {
  background: #f5f7fa;
  padding: 16px;
  border-radius: 4px;
  max-height: 70vh;
  overflow: auto;
  white-space: pre-wrap;
  word-break: break-all;
}

.preview-audio {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 200px;
}

.preview-office .office-content {
  max-height: 70vh;
  overflow: auto;
  padding: 16px;
  background: #f5f7fa;
  border-radius: 4px;
}

.loading-text {
  text-align: center;
  padding: 40px;
  color: #909399;
}

.preview-other {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 300px;
}
</style>
