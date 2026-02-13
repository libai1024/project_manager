<template>
  <el-card class="logs-card">
    <template #header>
      <div class="card-header">
        <span>
          <el-icon><Clock /></el-icon>
          项目日志
        </span>
        <div>
          <el-button
            type="primary"
            size="small"
            @click="$emit('add-snapshot')"
          >
            <el-icon><Camera /></el-icon>
            添加快照
          </el-button>
          <el-dropdown @command="handleExport" trigger="click">
            <el-button type="text" size="small">
              <el-icon><Download /></el-icon>
              导出
              <el-icon class="el-icon--right"><ArrowDown /></el-icon>
            </el-button>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="markdown">导出为 Markdown</el-dropdown-item>
                <el-dropdown-item command="pdf">导出为 PDF</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
          <el-button
            type="text"
            size="small"
            @click="$emit('refresh')"
            :loading="loading"
          >
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
        </div>
      </div>
    </template>

    <div v-if="logs.length === 0" class="empty-logs">
      <el-empty description="暂无项目日志" :image-size="80" />
    </div>

    <div v-else class="project-logs-timeline">
      <div
        v-for="(log, index) in logs"
        :key="log.id"
        class="log-item"
      >
        <!-- 时间线连接线 -->
        <div class="log-line" v-if="index < logs.length - 1"></div>
        
        <!-- 日志节点 -->
        <div class="log-node">
          <el-icon>
            <component :is="getLogActionIcon(log.action)" />
          </el-icon>
        </div>
        
        <!-- 日志内容 -->
        <div class="log-content">
          <div class="log-header">
            <div class="log-action">
              <span class="action-text">{{ formatLogAction(log.action) }}</span>
              <span class="log-time">{{ new Date(log.created_at).toLocaleString('zh-CN') }}</span>
            </div>
            <div class="log-header-right">
              <div v-if="log.user_name" class="log-user">
                <el-icon><User /></el-icon>
                <span>{{ log.user_name }}</span>
              </div>
              <el-button
                type="danger"
                :icon="Delete"
                circle
                size="small"
                @click.stop="handleDelete(log)"
                class="log-delete-btn"
              />
            </div>
          </div>
          <div class="log-description">{{ log.description }}</div>
          <div v-if="log.details" class="log-details">
            <div v-if="parseLogDetails(log.details)?.step_names" class="log-detail-item">
              <span class="detail-label">步骤</span>
              <div style="flex: 1; display: flex; flex-wrap: wrap; gap: 6px;">
                <span
                  v-for="(stepName, idx) in parseLogDetails(log.details)?.step_names"
                  :key="idx"
                  style="font-size: 11px; color: #666; padding: 2px 8px; border: 1px solid #000; border-radius: 0; background: transparent;"
                >
                  {{ stepName }}
                </span>
              </div>
            </div>
            <div v-if="parseLogDetails(log.details)?.completion_note" class="log-detail-item" style="flex-direction: column; align-items: stretch;">
              <span class="detail-label" style="margin-bottom: 6px;">完成说明</span>
              <div class="completion-note markdown-content" v-html="renderMarkdown(parseLogDetails(log.details)?.completion_note || '')"></div>
            </div>
            <div v-if="parseLogDetails(log.details)?.update_note" class="log-detail-item" style="flex-direction: column; align-items: stretch;">
              <span class="detail-label" style="margin-bottom: 6px;">更新说明</span>
              <div class="completion-note markdown-content" v-html="renderMarkdown(parseLogDetails(log.details)?.update_note || '')"></div>
            </div>
            <div v-if="parseLogDetails(log.details)?.snapshot_note" class="log-detail-item" style="flex-direction: column; align-items: stretch;">
              <span class="detail-label" style="margin-bottom: 6px;">快照说明</span>
              <div class="completion-note markdown-content" v-html="renderMarkdown(parseLogDetails(log.details)?.snapshot_note || '')"></div>
            </div>
            <!-- 照片九宫格 -->
            <div v-if="parseLogDetails(log.details)?.photos && parseLogDetails(log.details)?.photos.length > 0" class="log-detail-item" style="flex-direction: column; align-items: stretch;">
              <span class="detail-label" style="margin-bottom: 8px;">照片</span>
              <div class="photo-grid" :class="`photo-grid-${Math.min(parseLogDetails(log.details)?.photos.length, 9)}`">
                <div
                  v-for="(photo, photoIdx) in parseLogDetails(log.details)?.photos"
                  :key="photoIdx"
                  class="photo-item"
                  @click="handlePhotoClick(parseLogDetails(log.details)?.photos, photoIdx)"
                >
                  <img :src="getPhotoUrl(photo)" :alt="`照片 ${photoIdx + 1}`" @error="handleImageError" />
                  <div class="photo-overlay">
                    <el-icon><ZoomIn /></el-icon>
                  </div>
                </div>
              </div>
            </div>
            <!-- 文件列表 -->
            <div v-if="getFileAttachments(log.id) && getFileAttachments(log.id).length > 0" class="log-detail-item" style="flex-direction: column; align-items: stretch;">
              <span class="detail-label" style="margin-bottom: 8px;">文件</span>
              <div class="file-list">
                <div
                  v-for="(attachment, idx) in getFileAttachments(log.id)"
                  :key="idx"
                  class="file-list-item"
                  @click="handleFileClick(attachment.id)"
                >
                  <FileTypeIcon :file-name="attachment.file_name" size="small" />
                  <span class="file-name">{{ attachment.file_name }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </el-card>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Clock, Camera, Download, ArrowDown, Refresh, User, Delete, ZoomIn, InfoFilled } from '@element-plus/icons-vue'
import type { ProjectLog } from '@/api/project'
import type { Attachment } from '@/api/attachment'
import { useLogIconConfig } from '@/composables/useLogIconConfig'
import FileTypeIcon from '@/components/FileTypeIcon.vue'
import { attachmentApi } from '@/api/attachment'

interface Props {
  logs: ProjectLog[]
  logAttachments: Record<number, Attachment[]>
  loading?: boolean
  projectTitle?: string
}

const props = withDefaults(defineProps<Props>(), {
  loading: false,
  projectTitle: ''
})

const emit = defineEmits<{
  'add-snapshot': []
  'refresh': []
  'delete-log': [logId: number]
  'export': [format: 'markdown' | 'pdf']
  'view-photo': [photos: (string | number)[], index: number]
  'download-file': [attachmentId: number]
}>()

// 照片URL缓存
const photoUrlCache = ref<Map<string | number, string>>(new Map())

// 日志图标配置
const { getIcon: getLogIcon } = useLogIconConfig()

// 格式化日志操作类型
const formatLogAction = (action: string): string => {
  const actionMap: Record<string, string> = {
    'project_created': '创建项目',
    'todo_created': '创建待办',
    'todo_completed': '完成待办',
    'todo_deleted': '删除待办',
    'step_updated': '更新步骤',
    'project_updated': '更新项目',
    'project_snapshot': '项目快照'
  }
  return actionMap[action] || action
}

// 获取日志操作图标
const getLogActionIcon = (action: string) => {
  return getLogIcon(action as any) || InfoFilled
}

// 解析日志详情
const parseLogDetails = (details?: string): any => {
  if (!details) return null
  try {
    return JSON.parse(details)
  } catch {
    return null
  }
}

// 获取文件附件（排除照片）
const getFileAttachments = (logId: number): Attachment[] => {
  const attachments = props.logAttachments[logId] || []
  const log = props.logs.find(l => l.id === logId)
  if (!log) return []
  
  const details = parseLogDetails(log.details)
  if (!details?.photos) return attachments
  
  // 排除照片ID
  const photoIds = details.photos.map((p: string | number) => {
    if (typeof p === 'string') {
      return parseInt(p) || 0
    }
    return p
  }).filter((id: number) => id > 0)
  
  return attachments.filter(a => !photoIds.includes(a.id))
}

// Markdown渲染
const renderMarkdown = (text: string): string => {
  if (!text) return ''
  
  const escapeHtml = (str: string) => {
    const div = document.createElement('div')
    div.textContent = str
    return div.innerHTML
  }
  
  let html = escapeHtml(text)
  html = html.replace(/^### (.*$)/gim, '<h3>$1</h3>')
  html = html.replace(/^## (.*$)/gim, '<h2>$1</h2>')
  html = html.replace(/^# (.*$)/gim, '<h1>$1</h1>')
  html = html.replace(/\*\*(.*?)\*\*/gim, '<strong>$1</strong>')
  html = html.replace(/__(.*?)__/gim, '<strong>$1</strong>')
  html = html.replace(/\*(.*?)\*/gim, '<em>$1</em>')
  html = html.replace(/_(.*?)_/gim, '<em>$1</em>')
  html = html.replace(/```([\s\S]*?)```/gim, '<pre><code>$1</code></pre>')
  html = html.replace(/`([^`]+)`/gim, '<code>$1</code>')
  html = html.replace(/\[([^\]]+)\]\(([^)]+)\)/gim, '<a href="$2" target="_blank" rel="noopener noreferrer">$1</a>')
  html = html.replace(/^\* (.*$)/gim, '<li>$1</li>')
  html = html.replace(/^- (.*$)/gim, '<li>$1</li>')
  html = html.replace(/^\+ (.*$)/gim, '<li>$1</li>')
  html = html.replace(/\n/gim, '<br>')
  html = html.replace(/(<li>.*<\/li>)/gim, '<ul>$1</ul>')
  
  return html
}

// 获取附件ID
const getAttachmentId = (photoPath: string | number): number | null => {
  if (typeof photoPath === 'number') {
    return photoPath
  }
  if (typeof photoPath === 'string') {
    if (photoPath.startsWith('http://') || photoPath.startsWith('https://')) {
      return null
    }
    const id = parseInt(photoPath.split('/').pop()?.replace(/\.[^.]+$/, '') || photoPath) || 0
    return id > 0 ? id : null
  }
  return null
}

// 加载照片URL
const loadPhotoUrl = async (photoPath: string | number): Promise<string> => {
  if (photoUrlCache.value.has(photoPath)) {
    return photoUrlCache.value.get(photoPath)!
  }
  
  if (typeof photoPath === 'string' && (photoPath.startsWith('http://') || photoPath.startsWith('https://'))) {
    photoUrlCache.value.set(photoPath, photoPath)
    return photoPath
  }
  
  const attachmentId = getAttachmentId(photoPath)
  if (!attachmentId) return ''
  
  try {
    const response = await attachmentApi.download(attachmentId)
    let blob: Blob
    if (response instanceof Blob) {
      blob = response
    } else if (response && typeof response === 'object' && 'data' in response) {
      blob = new Blob([(response as any).data], { type: 'image/jpeg' })
    } else {
      blob = new Blob([response as any], { type: 'image/jpeg' })
    }
    const blobUrl = URL.createObjectURL(blob)
    photoUrlCache.value.set(photoPath, blobUrl)
    return blobUrl
  } catch (error) {
    console.error('Failed to load photo:', error)
    return ''
  }
}

// 获取照片URL（同步版本）
const getPhotoUrl = (photoPath: string | number): string => {
  if (photoUrlCache.value.has(photoPath)) {
    return photoUrlCache.value.get(photoPath)!
  }
  
  if (typeof photoPath === 'string' && (photoPath.startsWith('http://') || photoPath.startsWith('https://'))) {
    return photoPath
  }
  
  loadPhotoUrl(photoPath).then(url => {
    if (url) {
      photoUrlCache.value.set(photoPath, url)
    }
  })
  
  return ''
}

// 处理删除日志
const handleDelete = async (log: ProjectLog) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除这条日志吗？`,
      '提示',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )
    emit('delete-log', log.id)
  } catch (error) {
    // 用户取消
  }
}

// 处理导出
const handleExport = (format: 'markdown' | 'pdf') => {
  emit('export', format)
}

// 处理照片点击
const handlePhotoClick = (photos: (string | number)[], index: number) => {
  emit('view-photo', photos, index)
}

// 处理文件点击
const handleFileClick = (attachmentId: number) => {
  emit('download-file', attachmentId)
}

// 处理图片加载错误
const handleImageError = (e: Event) => {
  const img = e.target as HTMLImageElement
  img.src = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCIgZmlsbD0iI2Y1ZjdmYSIvPjx0ZXh0IHg9IjUwJSIgeT0iNTAlIiBmb250LWZhbWlseT0iQXJpYWwiIGZvbnQtc2l6ZT0iMTQiIGZpbGw9IiM5MDkzOTkiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGR5PSIuM2VtIj7lm77niYfliqDovb3lpLHotKU8L3RleHQ+PC9zdmc+'
}
</script>

<style scoped>
.logs-card {
  height: 100%;
  position: sticky;
  top: 20px;
  max-height: calc(100vh - 100px);
  overflow-y: auto;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
}

.project-logs-timeline {
  position: relative;
  padding-left: 40px;
  max-height: calc(100vh - 200px);
  overflow-y: auto;
  padding-right: 0;
}

.project-logs-timeline::-webkit-scrollbar {
  width: 4px;
}

.project-logs-timeline::-webkit-scrollbar-track {
  background: transparent;
}

.project-logs-timeline::-webkit-scrollbar-thumb {
  background: #000;
  border-radius: 2px;
}

.project-logs-timeline::-webkit-scrollbar-thumb:hover {
  background: #333;
}

.log-item {
  position: relative;
  margin-bottom: 32px;
  display: flex;
  align-items: flex-start;
  gap: 0;
}

.log-item:last-child {
  margin-bottom: 0;
}

.log-line {
  position: absolute;
  left: -30px;
  top: 20px;
  width: 1px;
  height: calc(100% + 12px);
  background: #000;
  opacity: 0.2;
  transform: translateX(50%);
}

.log-item:last-child .log-line {
  display: none;
}

.log-node {
  position: absolute;
  left: -40px;
  top: 0;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: #000;
  border: 2px solid #fff;
  z-index: 2;
  flex-shrink: 0;
  box-shadow: 0 0 0 2px #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 10px;
  transform: translateX(50%);
  margin-left: -10px;
}

.log-content {
  flex: 1;
  background: transparent;
  border-radius: 0;
  padding: 0;
  box-shadow: none;
  border: none;
  border-left: 1px solid transparent;
  padding-left: 0;
  transition: all 0.2s ease;
}

.log-item:hover .log-content {
  border-left-color: #000;
  padding-left: 12px;
}

.log-header {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  margin-bottom: 6px;
  flex-wrap: wrap;
  gap: 12px;
}

.log-action {
  display: flex;
  align-items: baseline;
  gap: 8px;
  flex-wrap: wrap;
}

.action-text {
  font-size: 13px;
  font-weight: 500;
  color: #000;
  letter-spacing: 0.02em;
  text-transform: uppercase;
}

.log-time {
  font-size: 11px;
  color: #666;
  font-weight: 400;
}

.log-user {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: #666;
}

.log-header-right {
  display: flex;
  align-items: center;
  gap: 8px;
}

.log-delete-btn {
  opacity: 0;
  transition: opacity 0.2s;
}

.log-item:hover .log-delete-btn {
  opacity: 1;
}

.log-description {
  font-size: 13px;
  color: #000;
  line-height: 1.7;
  margin-bottom: 0;
}

.log-details {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid #e5e5e5;
}

.log-detail-item {
  margin-bottom: 10px;
  display: flex;
  align-items: flex-start;
  gap: 8px;
  flex-wrap: wrap;
}

.detail-label {
  font-size: 11px;
  color: #666;
  font-weight: 500;
  min-width: 60px;
}

.completion-note {
  font-size: 12px;
  line-height: 1.6;
  color: #333;
}

.photo-grid {
  display: grid;
  gap: 8px;
}

.photo-grid-photo-grid-1 { grid-template-columns: 1fr; }
.photo-grid-photo-grid-2 { grid-template-columns: repeat(2, 1fr); }
.photo-grid-photo-grid-3 { grid-template-columns: repeat(3, 1fr); }
.photo-grid-photo-grid-4 { grid-template-columns: repeat(2, 1fr); }
.photo-grid-photo-grid-5 { grid-template-columns: repeat(3, 1fr); }
.photo-grid-photo-grid-6 { grid-template-columns: repeat(3, 1fr); }
.photo-grid-photo-grid-7 { grid-template-columns: repeat(3, 1fr); }
.photo-grid-photo-grid-8 { grid-template-columns: repeat(3, 1fr); }
.photo-grid-photo-grid-9 { grid-template-columns: repeat(3, 1fr); }

.photo-item {
  position: relative;
  aspect-ratio: 1;
  overflow: hidden;
  border: 1px solid #e5e5e5;
  cursor: pointer;
  border-radius: 4px;
}

.photo-item img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.photo-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.3s;
}

.photo-item:hover .photo-overlay {
  opacity: 1;
}

.file-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.file-list-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px;
  border: 1px solid #e5e5e5;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
}

.file-list-item:hover {
  background: #f5f7fa;
  border-color: #409eff;
}

.file-name {
  font-size: 12px;
  color: #333;
  flex: 1;
}

.empty-logs {
  padding: 40px 0;
}

/* 移动端样式 */
@media (max-width: 768px) {
  .logs-card {
    position: static;
    max-height: none;
    height: auto;
  }

  .logs-card :deep(.el-card__header) {
    padding: 12px;
  }

  .logs-card :deep(.el-card__body) {
    padding: 12px;
  }

  .card-header {
    flex-direction: column;
    align-items: stretch;
    gap: 8px;
  }

  .card-header > span {
    font-size: 14px;
  }

  .card-header > div {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
  }

  .card-header .el-button {
    font-size: 12px;
    padding: 6px 10px;
  }

  .project-logs-timeline {
    padding-left: 24px;
    max-height: none;
  }

  .log-node {
    left: -24px;
    width: 16px;
    height: 16px;
    font-size: 8px;
    margin-left: -8px;
  }

  .log-line {
    left: -18px;
    top: 16px;
  }

  .log-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 6px;
  }

  .log-action {
    flex-direction: column;
    align-items: flex-start;
    gap: 2px;
  }

  .action-text {
    font-size: 12px;
  }

  .log-time {
    font-size: 10px;
  }

  .log-header-right {
    width: 100%;
    justify-content: space-between;
  }

  .log-user {
    font-size: 11px;
  }

  .log-description {
    font-size: 12px;
  }

  .log-details {
    margin-top: 8px;
    padding-top: 8px;
  }

  .log-detail-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 4px;
  }

  .detail-label {
    font-size: 10px;
    min-width: auto;
  }

  .completion-note {
    font-size: 11px;
  }

  .photo-grid {
    gap: 4px;
  }

  .photo-item {
    border-radius: 2px;
  }

  .file-list-item {
    padding: 6px;
  }

  .file-name {
    font-size: 11px;
  }

  .log-delete-btn {
    opacity: 1;
  }

  .empty-logs {
    padding: 20px 0;
  }
}

@media (max-width: 480px) {
  .project-logs-timeline {
    padding-left: 18px;
  }

  .log-node {
    left: -18px;
    width: 14px;
    height: 14px;
    font-size: 7px;
    margin-left: -7px;
  }

  .log-line {
    left: -13px;
  }

  .photo-grid-photo-grid-2,
  .photo-grid-photo-grid-3 {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>

