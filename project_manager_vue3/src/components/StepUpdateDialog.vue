<template>
  <el-dialog
    v-model="visible"
    title="更新步骤进度"
    width="700px"
    :close-on-click-modal="false"
    class="step-update-dialog"
  >
    <div class="dialog-content">
      <!-- 步骤信息 -->
      <div class="step-info">
        <div class="step-info-item">
          <span class="info-label">步骤名称：</span>
          <span class="info-value">{{ step?.name }}</span>
        </div>
        <div class="step-info-item">
          <span class="info-label">当前状态：</span>
          <span class="info-value">{{ step?.status }}</span>
        </div>
        <div class="step-info-item">
          <span class="info-label">更新为：</span>
          <span class="info-value">{{ newStatus }}</span>
        </div>
      </div>

      <!-- 更新说明 -->
      <div class="update-form">
        <div class="form-header">
          <span class="form-title">更新说明</span>
          <span class="form-hint">（可选）支持Markdown语法</span>
        </div>
        <div class="markdown-editor-wrapper">
          <div class="editor-tabs">
            <button 
              :class="['tab-button', { active: editorMode === 'edit' }]"
              @click="editorMode = 'edit'"
            >
              编辑
            </button>
            <button 
              :class="['tab-button', { active: editorMode === 'preview' }]"
              @click="editorMode = 'preview'"
            >
              预览
            </button>
          </div>
          <div v-show="editorMode === 'edit'" class="input-wrapper">
            <el-input
              v-model="updateNote"
              type="textarea"
              :rows="8"
              placeholder="输入更新说明，支持Markdown语法..."
              class="update-textarea"
              maxlength="2000"
              show-word-limit
            />
          </div>
          <div v-show="editorMode === 'preview'" class="preview-wrapper">
            <div class="markdown-preview" v-html="renderMarkdown(updateNote)"></div>
            <div v-if="!updateNote.trim()" class="preview-empty">
              暂无内容
            </div>
          </div>
        </div>
        <div class="markdown-hint">
          <span>支持Markdown语法：**粗体**、*斜体*、`代码`、[链接](url)、# 标题、- 列表</span>
        </div>
      </div>

      <!-- 上传区域：附件上传和快照上传并排 -->
      <div class="upload-sections">
        <!-- 左侧：附件上传 -->
        <div class="file-upload-section">
          <div class="form-header">
            <span class="form-title">上传附件</span>
            <span class="form-hint">（可选）最多5个</span>
          </div>
          <!-- 文件夹选择 -->
          <div class="folder-select-section">
            <el-select
              v-model="selectedFolderId"
              clearable
              placeholder="选择文件夹（可选）"
              style="width: 100%;"
              size="small"
              @change="handleFolderChange"
            >
              <el-option
                v-for="folder in folders"
                :key="folder.id"
                :label="folder.name"
                :value="folder.id"
              />
              <el-option
                value="__create__"
                label="+ 新建文件夹"
                class="create-folder-option"
              >
                <span style="display: flex; align-items: center; gap: 4px;">
                  <el-icon><Plus /></el-icon>
                  <span>新建文件夹</span>
                </span>
              </el-option>
            </el-select>
          </div>
          <el-upload
            ref="fileUploadRef"
            :auto-upload="false"
            :limit="5"
            :on-change="handleFileChange"
            :on-remove="handleFileRemove"
            :file-list="fileList"
            :drag="true"
            multiple
            class="upload-dragger"
          >
            <el-icon class="el-icon--upload"><upload-filled /></el-icon>
            <div class="el-upload__text">
              将文件拖到此处，或<em>点击上传</em>
            </div>
            <template #tip>
              <div class="el-upload__tip">支持所有文件类型，单个文件不超过1GB</div>
            </template>
          </el-upload>
          <!-- 文件预览列表 -->
          <div v-if="fileList.length > 0" class="file-preview-list">
            <div
              v-for="(file, index) in fileList"
              :key="index"
              class="file-preview-item"
            >
              <div class="file-icon">
                <el-icon><Document /></el-icon>
              </div>
              <div class="file-info">
                <div class="file-name">{{ file.name }}</div>
                <div class="file-size">{{ formatFileSize(file.size || 0) }}</div>
              </div>
              <el-button
                type="danger"
                :icon="Delete"
                circle
                size="small"
                @click="handleFileRemove(file, fileList)"
              />
            </div>
          </div>
        </div>

        <!-- 右侧：快照上传 -->
        <div class="photo-upload-section">
          <div class="form-header">
            <span class="form-title">上传快照</span>
            <span class="form-hint">最多9张照片</span>
          </div>
          <!-- 快照文件夹选择（默认快照文件夹） -->
          <div class="folder-select-section">
            <el-select
              v-model="selectedSnapshotFolderId"
              clearable
              placeholder="选择文件夹（默认：快照）"
              style="width: 100%;"
              size="small"
              @change="handleSnapshotFolderChange"
            >
              <el-option
                v-for="folder in folders"
                :key="folder.id"
                :label="folder.name"
                :value="folder.id"
              />
              <el-option
                value="__create__"
                label="+ 新建文件夹"
                class="create-folder-option"
              >
                <span style="display: flex; align-items: center; gap: 4px;">
                  <el-icon><Plus /></el-icon>
                  <span>新建文件夹</span>
                </span>
              </el-option>
            </el-select>
          </div>
          <el-upload
            ref="photoUploadRef"
            :auto-upload="false"
            :limit="9"
            :on-change="handlePhotoChange"
            :on-remove="handlePhotoRemove"
            :file-list="photoList"
            :accept="'image/*'"
            :drag="true"
            multiple
            class="photo-upload-dragger"
          >
            <el-icon class="el-icon--upload"><upload-filled /></el-icon>
            <div class="el-upload__text">
              将照片拖到此处，或<em>点击上传</em>
            </div>
            <template #tip>
              <div class="el-upload__tip">支持JPG、PNG、GIF格式，单张不超过10MB</div>
            </template>
          </el-upload>
          <!-- 照片预览网格 -->
          <div v-if="photoList.length > 0" class="photo-preview-grid">
            <div
              v-for="(photo, index) in photoList"
              :key="index"
              class="photo-preview-item"
            >
              <img
                :src="getPhotoPreviewUrl(photo)"
                :alt="photo.name"
                class="photo-preview-image"
              />
              <div class="photo-preview-overlay">
                <el-button
                  type="danger"
                  :icon="Delete"
                  circle
                  size="small"
                  @click="handlePhotoRemove(photo, photoList)"
                />
              </div>
              <div class="photo-preview-name">{{ photo.name }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleCancel">取消</el-button>
        <el-button type="primary" @click="handleConfirm" :loading="loading">
          确认更新
        </el-button>
      </div>
    </template>
    
    <!-- 新建文件夹对话框 -->
    <el-dialog
      v-model="showCreateFolderDialog"
      title="新建文件夹"
      width="400px"
      @close="newFolderName = ''"
    >
      <el-form>
        <el-form-item label="文件夹名称">
          <el-input
            v-model="newFolderName"
            placeholder="请输入文件夹名称"
            @keyup.enter="handleCreateFolder"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateFolderDialog = false">取消</el-button>
        <el-button type="primary" @click="handleCreateFolder">确定</el-button>
      </template>
    </el-dialog>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { UploadFilled, Document, Delete, Plus } from '@element-plus/icons-vue'
import type { ProjectStep } from '@/api/project'
import type { UploadFile, UploadFiles, UploadInstance } from 'element-plus'
import { attachmentFolderApi, type AttachmentFolder } from '@/api/attachmentFolder'

interface Props {
  modelValue: boolean
  step: ProjectStep | null
  newStatus: string
  projectId: number
}

const props = defineProps<Props>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  confirm: [data: { note: string; files: File[]; photos: File[]; fileFolderId?: number; photoFolderId?: number }]
}>()

const visible = ref(false)
const updateNote = ref('')
const loading = ref(false)
const editorMode = ref<'edit' | 'preview'>('edit')
const fileUploadRef = ref<UploadInstance>()
const photoUploadRef = ref<UploadInstance>()
const fileList = ref<UploadFile[]>([])
const photoList = ref<UploadFile[]>([])

// 文件夹相关
const folders = ref<AttachmentFolder[]>([])
const selectedFolderId = ref<number | null>(null)
const selectedSnapshotFolderId = ref<number | null>(null)
const showCreateFolderDialog = ref(false)
const newFolderName = ref('')

// 加载文件夹列表
const loadFolders = async () => {
  if (!props.projectId) return
  try {
    folders.value = await attachmentFolderApi.list(props.projectId)
    // 默认选择快照文件夹
    const snapshotFolder = folders.value.find(f => f.name === '快照')
    if (snapshotFolder) {
      selectedSnapshotFolderId.value = snapshotFolder.id
    }
  } catch (error) {
    console.error('加载文件夹失败:', error)
  }
}

// 创建文件夹
const handleCreateFolder = async () => {
  if (!props.projectId) return
  if (!newFolderName.value.trim()) {
    ElMessage.warning('请输入文件夹名称')
    return
  }
  
  // 检查是否为默认文件夹名称
  if (['项目需求', '项目交付', '其他'].includes(newFolderName.value.trim())) {
    ElMessage.warning('不能使用默认文件夹名称')
    return
  }
  
  try {
    const newFolder = await attachmentFolderApi.create(props.projectId, { name: newFolderName.value.trim() })
    await loadFolders()
    showCreateFolderDialog.value = false
    // 自动选择新创建的文件夹
    selectedFolderId.value = newFolder.id
    selectedSnapshotFolderId.value = newFolder.id
    newFolderName.value = ''
    ElMessage.success('文件夹创建成功')
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '创建文件夹失败')
  }
}

// 处理文件夹选择变化
const handleFolderChange = (value: number | string | null) => {
  if (value === '__create__') {
    selectedFolderId.value = null
    showCreateFolderDialog.value = true
  }
}

// 处理快照文件夹选择变化
const handleSnapshotFolderChange = (value: number | string | null) => {
  if (value === '__create__') {
    selectedSnapshotFolderId.value = null
    showCreateFolderDialog.value = true
  }
}

watch(() => props.modelValue, (val) => {
  visible.value = val
  if (val) {
    updateNote.value = ''
    editorMode.value = 'edit'
    fileList.value = []
    photoList.value = []
    selectedFolderId.value = null
    selectedSnapshotFolderId.value = null
    loadFolders()
  }
})

watch(() => props.projectId, () => {
  if (props.projectId) {
    loadFolders()
  }
}, { immediate: true })

watch(visible, (val) => {
  emit('update:modelValue', val)
})

const handleFileChange = (file: UploadFile, files: UploadFiles) => {
  // 验证文件大小
  if (file.raw) {
    if (file.raw.size > 1 * 1024 * 1024 * 1024) {
      ElMessage.error('单个文件不能超过1GB')
      return
    }
  }
  fileList.value = files
}

const handleFileRemove = (file: UploadFile, files?: UploadFiles) => {
  if (files) {
    fileList.value = files
  } else {
    fileList.value = fileList.value.filter(f => f.uid !== file.uid)
    fileUploadRef.value?.handleRemove(file)
  }
}

const handlePhotoChange = (file: UploadFile, files: UploadFiles) => {
  // 验证文件类型和大小
  if (file.raw) {
    if (!file.raw.type.startsWith('image/')) {
      ElMessage.error('只能上传图片文件')
      return
    }
    if (file.raw.size > 10 * 1024 * 1024) {
      ElMessage.error('单张图片不能超过10MB')
      return
    }
  }
  photoList.value = files
}

const handlePhotoRemove = (file: UploadFile, files?: UploadFiles) => {
  if (files) {
    photoList.value = files
  } else {
    photoList.value = photoList.value.filter(f => f.uid !== file.uid)
    photoUploadRef.value?.handleRemove(file)
  }
}

const getPhotoPreviewUrl = (file: UploadFile): string => {
  if (file.url) return file.url
  if (file.raw) {
    return URL.createObjectURL(file.raw)
  }
  return ''
}

const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
}

const handleCancel = () => {
  visible.value = false
  updateNote.value = ''
  fileList.value = []
  photoList.value = []
  editorMode.value = 'edit'
}

const handleConfirm = () => {
  const files = fileList.value.map(f => f.raw as File).filter(Boolean)
  const photos = photoList.value.map(f => f.raw as File).filter(Boolean)
  
  // 确保folder_id是数字类型，排除字符串'__create__'
  const fileFolderId = typeof selectedFolderId.value === 'number' ? selectedFolderId.value : undefined
  const photoFolderId = typeof selectedSnapshotFolderId.value === 'number' ? selectedSnapshotFolderId.value : undefined
  
  emit('confirm', {
    note: updateNote.value.trim(),
    files,
    photos,
    fileFolderId,
    photoFolderId
  })
  loading.value = true
  setTimeout(() => {
    loading.value = false
  }, 100)
}

// Markdown渲染函数
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
</script>

<style scoped>
.step-update-dialog :deep(.el-dialog__body) {
  padding: 24px;
}

.dialog-content {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.step-info {
  padding: 16px;
  background: #f9fafb;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
}

.step-info-item {
  display: flex;
  align-items: flex-start;
  margin-bottom: 12px;
}

.step-info-item:last-child {
  margin-bottom: 0;
}

.info-label {
  font-size: 13px;
  color: #6b7280;
  font-weight: 500;
  min-width: 80px;
  flex-shrink: 0;
}

.info-value {
  font-size: 13px;
  color: #111827;
  flex: 1;
  word-break: break-word;
}

.update-form,
.file-upload-section {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.folder-select-section {
  margin-bottom: 12px;
}

:deep(.create-folder-option) {
  background-color: #f0f9ff !important;
  color: #409eff !important;
  font-weight: 500;
}

:deep(.create-folder-option:hover) {
  background-color: #e0f2fe !important;
}

.form-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.form-title {
  font-size: 14px;
  font-weight: 600;
  color: #111827;
}

.form-hint {
  font-size: 12px;
  color: #9ca3af;
}

.markdown-editor-wrapper {
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  overflow: hidden;
  transition: all 0.2s;
}

.markdown-editor-wrapper:focus-within {
  border-color: #111827;
  box-shadow: 0 0 0 3px rgba(17, 24, 39, 0.1);
}

.editor-tabs {
  display: flex;
  border-bottom: 1px solid #e5e7eb;
  background: #f9fafb;
}

.tab-button {
  flex: 1;
  padding: 8px 16px;
  border: none;
  background: transparent;
  cursor: pointer;
  font-size: 13px;
  color: #6b7280;
  transition: all 0.2s;
  border-bottom: 2px solid transparent;
}

.tab-button:hover {
  color: #111827;
  background: #f3f4f6;
}

.tab-button.active {
  color: #111827;
  border-bottom-color: #111827;
  font-weight: 500;
}

.input-wrapper {
  border: none;
  border-radius: 0;
}

.update-textarea {
  width: 100%;
}

.update-textarea :deep(.el-textarea__inner) {
  border: none;
  box-shadow: none;
  padding: 12px 16px;
  font-size: 13px;
  line-height: 1.6;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', 'Consolas', monospace;
  resize: vertical;
}

.preview-wrapper {
  min-height: 150px;
  padding: 16px;
  background: #fff;
  max-height: 300px;
  overflow-y: auto;
}

.markdown-preview {
  font-size: 13px;
  line-height: 1.7;
  color: #111827;
}

.markdown-preview :deep(h1) { font-size: 20px; font-weight: 600; margin: 16px 0 8px 0; }
.markdown-preview :deep(h2) { font-size: 18px; font-weight: 600; margin: 14px 0 6px 0; }
.markdown-preview :deep(h3) { font-size: 16px; font-weight: 600; margin: 12px 0 4px 0; }
.markdown-preview :deep(strong) { font-weight: 600; }
.markdown-preview :deep(em) { font-style: italic; }
.markdown-preview :deep(code) { background: #f3f4f6; padding: 2px 6px; border-radius: 3px; font-size: 12px; }
.markdown-preview :deep(pre) { background: #f3f4f6; padding: 12px; border-radius: 4px; overflow-x: auto; margin: 8px 0; }
.markdown-preview :deep(pre code) { background: transparent; padding: 0; }
.markdown-preview :deep(ul) { margin: 8px 0; padding-left: 24px; }
.markdown-preview :deep(li) { margin: 4px 0; }
.markdown-preview :deep(a) { color: #111827; text-decoration: underline; }

.preview-empty {
  color: #9ca3af;
  font-size: 13px;
  text-align: center;
  padding: 40px 0;
}

.markdown-hint {
  margin-top: 8px;
  font-size: 11px;
  color: #9ca3af;
  padding: 8px 12px;
  background: #f9fafb;
  border-radius: 4px;
}

.upload-sections {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
}

.file-upload-section,
.photo-upload-section {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.upload-dragger {
  width: 100%;
}

.upload-dragger :deep(.el-upload-dragger) {
  width: 100%;
  height: 180px;
  border: 2px dashed #d9d9d9;
  border-radius: 8px;
  background: #fafafa;
  transition: all 0.3s;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  cursor: pointer;
}

.upload-dragger :deep(.el-upload-dragger:hover) {
  border-color: #409eff;
  background: #f0f9ff;
}

.upload-dragger :deep(.el-icon--upload) {
  font-size: 48px;
  color: #8c939d;
  margin-bottom: 16px;
}

.upload-dragger :deep(.el-upload__text) {
  color: #606266;
  font-size: 14px;
}

.upload-dragger :deep(.el-upload__text em) {
  color: #409eff;
  font-style: normal;
}

.file-preview-list {
  margin-top: 16px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.file-preview-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: #f9fafb;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  transition: all 0.2s;
}

.file-preview-item:hover {
  background: #f3f4f6;
  border-color: #d1d5db;
}

.file-icon {
  font-size: 24px;
  color: #409eff;
  flex-shrink: 0;
}

.file-info {
  flex: 1;
  min-width: 0;
}

.file-name {
  font-size: 13px;
  color: #111827;
  font-weight: 500;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  margin-bottom: 4px;
}

.file-size {
  font-size: 12px;
  color: #6b7280;
}

.photo-upload-dragger {
  width: 100%;
}

.photo-upload-dragger :deep(.el-upload-dragger) {
  width: 100%;
  height: 180px;
  border: 2px dashed #d9d9d9;
  border-radius: 8px;
  background: #fafafa;
  transition: all 0.3s;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  cursor: pointer;
}

.photo-upload-dragger :deep(.el-upload-dragger:hover) {
  border-color: #409eff;
  background: #f0f9ff;
}

.photo-upload-dragger :deep(.el-icon--upload) {
  font-size: 48px;
  color: #8c939d;
  margin-bottom: 16px;
}

.photo-upload-dragger :deep(.el-upload__text) {
  color: #606266;
  font-size: 14px;
}

.photo-upload-dragger :deep(.el-upload__text em) {
  color: #409eff;
  font-style: normal;
}

.photo-preview-grid {
  margin-top: 12px;
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8px;
  max-height: 300px;
  overflow-y: auto;
}

.photo-preview-item {
  position: relative;
  aspect-ratio: 1;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  overflow: hidden;
  background: #f9fafb;
  transition: all 0.2s;
  cursor: pointer;
}

.photo-preview-item:hover {
  border-color: #409eff;
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.2);
}

.photo-preview-item:hover .photo-preview-overlay {
  opacity: 1;
}

.photo-preview-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.photo-preview-overlay {
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
  transition: opacity 0.2s;
}

.photo-preview-name {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 6px 8px;
  background: rgba(0, 0, 0, 0.6);
  color: #fff;
  font-size: 11px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}
</style>

