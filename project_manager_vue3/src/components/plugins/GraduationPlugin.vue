<template>
  <BasePluginCard
    :project-id="projectId"
    plugin-type="graduation"
    title="毕设核心文件"
    subtitle="管理毕设项目核心文档"
    :icon="Document"
    :icon-gradient="['#667eea', '#764ba2']"
    card-class="graduation-plugin-card"
  >
    <template #header-actions>
          <el-button
            type="success"
            size="small"
            :icon="Download"
            @click="handleExportZip"
            :loading="exporting"
            :disabled="totalFilesCount === 0"
          >
            导出ZIP
          </el-button>
          <el-button
            type="primary"
            size="small"
            :icon="Upload"
            @click="showUploadDialog = true"
          >
            上传文件
          </el-button>
    </template>

    <div class="graduation-files">
      <div class="files-container">
        <div
          v-for="(config, fileType) in graduationFileTypes"
          :key="fileType"
          class="file-type-section"
          :class="{ 'has-files': getFilesByType(fileType as GraduationFileType).length > 0 }"
        >
          <div class="file-type-header">
            <div class="file-type-icon-wrapper">
              <el-icon class="file-type-icon"><component :is="getIconComponent(config.icon)" /></el-icon>
            </div>
            <div class="file-type-info">
              <span class="file-type-label">{{ config.label }}</span>
              <el-tag v-if="getFilesByType(fileType as GraduationFileType).length > 0" size="small" type="success" class="file-count-tag">
                {{ getFilesByType(fileType as GraduationFileType).length }}
              </el-tag>
            </div>
          </div>
          <div class="file-list">
            <div
              v-for="file in getFilesByType(fileType as GraduationFileType)"
              :key="file.id"
              class="file-item"
              @click="handleFileClick(file)"
              @contextmenu.prevent="handleFileContextMenu($event, file)"
            >
              <el-icon class="file-icon"><Document /></el-icon>
              <span class="file-name" :title="file.file_name">{{ file.file_name }}</span>
              <div class="file-actions" @click.stop>
                <el-button
                  type="primary"
                  :icon="View"
                  size="small"
                  text
                  circle
                  @click.stop="handleFileClick(file)"
                  class="preview-btn action-btn"
                  title="预览"
                />
                <el-button
                  type="primary"
                  :icon="Download"
                  size="small"
                  text
                  circle
                  @click.stop="handleDownloadFile(file)"
                  class="download-btn action-btn"
                  title="下载"
                />
              <el-button
                type="danger"
                :icon="Delete"
                size="small"
                text
                circle
                @click.stop="handleUntagFile(file)"
                  class="untag-btn action-btn"
                  title="取消标记"
              />
              </div>
            </div>
            <div
              v-if="getFilesByType(fileType as GraduationFileType).length === 0"
              class="file-empty"
            >
              <span class="empty-text">暂无</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 上传文件对话框 -->
    <el-dialog
      v-model="showUploadDialog"
      title="上传毕设文件"
      width="500px"
    >
      <el-form label-width="100px">
        <el-form-item label="文件类型" required>
          <el-select
            v-model="uploadFileType"
            placeholder="请选择文件类型"
            style="width: 100%"
          >
            <el-option
              v-for="(config, type) in graduationFileTypes"
              :key="type"
              :label="config.label"
              :value="type"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="选择文件" required>
          <el-upload
            ref="uploadRef"
            :auto-upload="false"
            :on-change="handleFileChange"
            :limit="1"
            :accept="getAcceptTypes(uploadFileType)"
            drag
            class="upload-dragger"
          >
            <el-icon class="el-icon--upload"><Upload /></el-icon>
            <div class="el-upload__text">
              将文件拖到此处，或<em>点击上传</em>
            </div>
            <template #tip>
              <div class="el-upload__tip">支持 {{ getAcceptTypes(uploadFileType) || '所有文件类型' }}，单个文件不超过1GB</div>
            </template>
          </el-upload>
          <div v-if="selectedFile" class="selected-file">
            <el-icon><Document /></el-icon>
            <span>{{ selectedFile.name }}</span>
          </div>
          <div v-if="uploading" class="upload-progress" style="margin-top: 15px;">
            <el-progress :percentage="uploadProgress" :status="uploadProgress === 100 ? 'success' : undefined" />
            <div style="text-align: center; margin-top: 8px; color: #909399; font-size: 12px;">
              {{ uploadProgress }}% - 正在上传...
            </div>
          </div>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showUploadDialog = false" :disabled="uploading">取消</el-button>
        <el-button
          type="primary"
          @click="handleUpload"
          :loading="uploading"
          :disabled="!uploadFileType || !selectedFile || uploading"
        >
          {{ uploading ? `上传中 ${uploadProgress}%` : '上传' }}
        </el-button>
      </template>
    </el-dialog>

    <!-- 右键菜单 -->
    <div
      v-if="showGraduationContextMenu"
      class="context-menu"
      :style="{ left: graduationContextMenuPos.x + 'px', top: graduationContextMenuPos.y + 'px' }"
      @click.stop
    >
      <div class="menu-title">标记为：</div>
      <div
        v-for="(config, type) in graduationFileTypes"
        :key="type"
        class="menu-item"
        @click="handleTagFile(type as GraduationFileType)"
      >
        <el-icon><component :is="getIconComponent(config.icon)" /></el-icon>
        <span>{{ config.label }}</span>
      </div>
      <div class="menu-divider"></div>
      <div class="menu-item danger" @click="handleUntagFile(graduationContextMenuFile!)">
        <el-icon><Delete /></el-icon>
        <span>取消标记</span>
      </div>
    </div>

    <!-- 文件预览对话框 -->
    <el-dialog
      v-model="showPreviewDialog"
      :title="previewAttachment?.file_name || '文件预览'"
      width="80%"
      :close-on-click-modal="false"
      class="file-preview-dialog"
    >
      <div v-if="previewAttachment" class="preview-container">
        <!-- 图片预览 -->
        <div v-if="isImageFile(previewAttachment.file_name)" class="preview-image">
          <img
            v-if="getPreviewUrlSync(previewAttachment.id)"
            :src="getPreviewUrlSync(previewAttachment.id)"
            :alt="previewAttachment.file_name"
            style="max-width: 100%; max-height: 70vh;"
          />
        </div>
        
        <!-- PDF预览 -->
        <div v-else-if="isPdfFile(previewAttachment.file_name)" class="preview-pdf">
          <iframe
            :src="getPreviewUrlSync(previewAttachment.id)"
            style="width: 100%; height: 70vh; border: none;"
          />
        </div>
        
        <!-- 文本预览 -->
        <div v-else-if="isTextFile(previewAttachment.file_name)" class="preview-text">
          <pre class="text-preview">{{ textPreviewContent }}</pre>
        </div>
        
        <!-- Office文档预览 -->
        <div v-else-if="isOfficeFile(previewAttachment.file_name)" class="preview-office">
          <div
            v-if="officePreviewType === 'word' || officePreviewType === 'excel'"
            class="office-content"
            v-html="officePreviewContent"
          />
          <div v-else-if="officePreviewType === 'ppt'" class="office-content">
            <p style="text-align: center; padding: 60px 20px; color: #909399;">
              PPT文档预览暂不支持，请下载后使用本地软件打开
            </p>
          </div>
        </div>
        
        <!-- 其他文件类型 -->
        <div v-else class="preview-other">
          <p style="text-align: center; padding: 60px 20px; color: #909399;">
            该文件类型不支持在线预览，请下载后查看
          </p>
        </div>
      </div>
      <template #footer>
        <el-button @click="showPreviewDialog = false">关闭</el-button>
        <el-button
          type="primary"
          :icon="Download"
          @click="handleDownloadFile(previewAttachment!)"
          v-if="previewAttachment"
        >
          下载
        </el-button>
      </template>
    </el-dialog>
  </BasePluginCard>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import {
  Document,
  Upload,
  Delete,
  VideoPlay,
  Download,
  View,
} from '@element-plus/icons-vue'
import JSZip from 'jszip'
import { saveAs } from 'file-saver'
import type { UploadFile, UploadFiles, UploadInstance } from 'element-plus'
import { useGraduationPlugin } from '@/composables/useGraduationPlugin'
import { graduationFileTypes, type GraduationFileType } from '@/types/plugin'
import type { Attachment } from '@/api/attachment'
import { attachmentApi } from '@/api/attachment'
import { attachmentFolderApi, type AttachmentFolder } from '@/api/attachmentFolder'
import BasePluginCard from './BasePluginCard.vue'

interface Props {
  projectId: number
  attachments: Attachment[]
  projectTitle?: string
}

const props = defineProps<Props>()

const emit = defineEmits<{
  refresh: []
}>()

const { tagAttachment, untagAttachment, getAttachmentTag, getTaggedAttachments, uploadAndTag } = useGraduationPlugin()

const showUploadDialog = ref(false)
const uploadFileType = ref<GraduationFileType | ''>('')
const selectedFile = ref<File | null>(null)
const uploading = ref(false)
const uploadProgress = ref(0)
const uploadRef = ref<UploadInstance>()
const exporting = ref(false)

// 右键菜单
const showGraduationContextMenu = ref(false)
const graduationContextMenuPos = ref({ x: 0, y: 0 })
const graduationContextMenuFile = ref<Attachment | null>(null)

// 获取文件类型对应的文件列表
const getFilesByType = (fileType: GraduationFileType): Attachment[] => {
  const tagged = getTaggedAttachments(props.attachments)
  return tagged[fileType] || []
}

// 计算总文件数
const totalFilesCount = computed(() => {
  return props.attachments.filter(att => {
    const tag = getAttachmentTag(att.id)
    return tag !== null
  }).length
})

// 导出ZIP文件
const handleExportZip = async () => {
  if (totalFilesCount.value === 0) {
    ElMessage.warning('没有可导出的文件')
    return
  }

  exporting.value = true
  try {
    const zip = new JSZip()
    const tagged = getTaggedAttachments(props.attachments)

    // 按文件类型组织文件
    for (const [fileType, files] of Object.entries(tagged)) {
      if (files.length === 0) continue

      const config = graduationFileTypes[fileType as GraduationFileType]
      const folderName = config.label

      // 为每个文件类型创建文件夹
      const folder = zip.folder(folderName)
      if (!folder) continue

      // 下载并添加文件到ZIP
      for (const file of files) {
        try {
          const blob = await attachmentApi.download(file.id)
          folder.file(file.file_name, blob)
        } catch (error) {
          console.error(`下载文件 ${file.file_name} 失败:`, error)
          ElMessage.warning(`文件 ${file.file_name} 下载失败，已跳过`)
        }
      }
    }

    // 生成ZIP文件并下载
    const zipBlob = await zip.generateAsync({ type: 'blob' })
    const projectName = props.projectTitle || `项目${props.projectId}`
    const dateStr = new Date().toISOString().split('T')[0]
    const fileName = `${projectName}_毕设核心文件_${dateStr}.zip`
    saveAs(zipBlob, fileName)
    
    ElMessage.success('导出成功')
  } catch (error) {
    console.error('导出ZIP失败:', error)
    ElMessage.error('导出失败，请重试')
  } finally {
    exporting.value = false
  }
}

// 获取图标组件
const getIconComponent = (iconName: string) => {
  const iconMap: Record<string, any> = {
    Document,
    VideoPlay,
  }
  return iconMap[iconName] || Document
}

// 获取文件类型限制
const getAcceptTypes = (fileType: GraduationFileType | ''): string => {
  if (!fileType) return ''
  return graduationFileTypes[fileType].accept || ''
}

// 文件选择变化
const handleFileChange = (file: UploadFile) => {
  // 验证文件大小（最大1GB）
  if (file.raw && file.raw.size > 1 * 1024 * 1024 * 1024) {
    ElMessage.error('单个文件不能超过1GB')
    uploadRef.value?.clearFiles()
    selectedFile.value = null
    return
  }
  selectedFile.value = file.raw || null
}

// 上传文件
const handleUpload = async () => {
  if (!uploadFileType.value || !selectedFile.value) return

  uploading.value = true
  uploadProgress.value = 0
  try {
    // 获取默认文件夹（快照文件夹或"其他"文件夹）
    let folderId: number | undefined
    try {
      const folders = await attachmentFolderApi.list(props.projectId)
      const snapshotFolder = folders.find(f => f.name === '快照')
      const otherFolder = folders.find(f => f.name === '其他')
      folderId = snapshotFolder?.id || otherFolder?.id
    } catch (error) {
      console.error('获取文件夹失败:', error)
    }

    await uploadAndTag(
      props.projectId,
      uploadFileType.value,
      selectedFile.value,
      folderId,
      (progressEvent) => {
        if (progressEvent.total) {
          uploadProgress.value = Math.round((progressEvent.loaded * 100) / progressEvent.total)
        }
      }
    )

    ElMessage.success('上传成功')
    showUploadDialog.value = false
    uploadFileType.value = ''
    selectedFile.value = null
    uploadProgress.value = 0
    uploadRef.value?.clearFiles()
    emit('refresh')
  } catch (error: any) {
    console.error('上传失败:', error)
    uploadProgress.value = 0
  } finally {
    uploading.value = false
  }
}

// 预览相关
const showPreviewDialog = ref(false)
const previewAttachment = ref<Attachment | null>(null)
const previewUrlCache = ref<Record<number, string>>({})
const textPreviewContent = ref('')
const officePreviewContent = ref('')
const officePreviewType = ref<'word' | 'excel' | 'ppt' | null>(null)

// 文件类型判断
const isImageFile = (filename: string): boolean => {
  const ext = filename.toLowerCase().split('.').pop()
  return ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp', 'svg', 'ico'].includes(ext || '')
}

const isPdfFile = (filename: string): boolean => {
  return filename.toLowerCase().endsWith('.pdf')
}

const isTextFile = (filename: string): boolean => {
  const ext = filename.toLowerCase().split('.').pop()
  return ['txt', 'md', 'json', 'xml', 'csv', 'log'].includes(ext || '')
}

const isOfficeFile = (filename: string): boolean => {
  return isWordFile(filename) || isExcelFile(filename) || isPptFile(filename)
}

const isWordFile = (filename: string): boolean => {
  const ext = filename.toLowerCase().split('.').pop()
  return ['doc', 'docx'].includes(ext || '')
}

const isExcelFile = (filename: string): boolean => {
  const ext = filename.toLowerCase().split('.').pop()
  return ['xls', 'xlsx'].includes(ext || '')
}

const isPptFile = (filename: string): boolean => {
  const ext = filename.toLowerCase().split('.').pop()
  return ['ppt', 'pptx'].includes(ext || '')
}

// 获取预览URL
const getPreviewUrl = async (attachmentId: number): Promise<string> => {
  if (previewUrlCache.value[attachmentId]) {
    return previewUrlCache.value[attachmentId]
  }
  
  try {
    const blob = await attachmentApi.preview(attachmentId)
    const url = URL.createObjectURL(blob)
    previewUrlCache.value[attachmentId] = url
    return url
  } catch (error) {
    ElMessage.error('加载预览失败')
    return ''
  }
}

const getPreviewUrlSync = (attachmentId: number): string => {
  return previewUrlCache.value[attachmentId] || ''
}

// 文件点击 - 预览
const handleFileClick = async (file: Attachment) => {
  previewAttachment.value = file
  textPreviewContent.value = ''
  officePreviewContent.value = ''
  officePreviewType.value = null
  showPreviewDialog.value = true
  
  // 预加载预览URL
  await getPreviewUrl(file.id)
  
  // 如果是文本文件，加载内容
  if (isTextFile(file.file_name)) {
    try {
      const blob = await attachmentApi.preview(file.id)
      const text = await blob.text()
      textPreviewContent.value = text
    } catch (error) {
      ElMessage.error('加载文件内容失败')
      textPreviewContent.value = '无法加载文件内容'
    }
  } else if (isWordFile(file.file_name)) {
    try {
      officePreviewType.value = 'word'
      const blob = await attachmentApi.preview(file.id)
      const arrayBuffer = await blob.arrayBuffer()
      const mammoth = (await import('mammoth')).default
      const result = await mammoth.convertToHtml({ arrayBuffer })
      officePreviewContent.value = result.value
    } catch (error) {
      console.error('Word预览错误:', error)
      ElMessage.error('加载Word文档失败')
      officePreviewContent.value = '<p style="color: red; padding: 20px;">无法加载Word文档</p>'
    }
  } else if (isExcelFile(file.file_name)) {
    try {
      officePreviewType.value = 'excel'
      const blob = await attachmentApi.preview(file.id)
      const arrayBuffer = await blob.arrayBuffer()
      const XLSX = (await import('xlsx')).default
      const workbook = XLSX.read(arrayBuffer, { type: 'array' })
      
      let html = '<div class="excel-preview">'
      workbook.SheetNames.forEach((sheetName, index) => {
        const worksheet = workbook.Sheets[sheetName]
        const htmlTable = XLSX.utils.sheet_to_html(worksheet)
        html += `<div class="excel-sheet"><h3>工作表 ${index + 1}: ${sheetName}</h3>${htmlTable}</div>`
      })
      html += '</div>'
      officePreviewContent.value = html
    } catch (error) {
      console.error('Excel预览错误:', error)
      ElMessage.error('加载Excel文档失败')
      officePreviewContent.value = '<p style="color: red; padding: 20px;">无法加载Excel文档</p>'
    }
  } else if (isPptFile(file.file_name)) {
    officePreviewType.value = 'ppt'
  }
}

// 下载文件
const handleDownloadFile = async (file: Attachment) => {
  try {
    const blob = await attachmentApi.download(file.id)
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = file.file_name
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
    ElMessage.success('下载成功')
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '下载失败')
  }
}

// 文件右键菜单
const handleFileContextMenu = (event: MouseEvent, file: Attachment) => {
  graduationContextMenuFile.value = file
  graduationContextMenuPos.value = { x: event.clientX, y: event.clientY }
  showGraduationContextMenu.value = true
}

// 标记文件
const handleTagFile = async (fileType: GraduationFileType) => {
  if (!graduationContextMenuFile.value) return

  await tagAttachment(graduationContextMenuFile.value.id, fileType, props.projectId)
  showGraduationContextMenu.value = false
  emit('refresh')
}

// 取消标记
const handleUntagFile = async (file: Attachment) => {
  untagAttachment(file.id)
  ElMessage.success('已取消标记')
  emit('refresh')
}

// 点击外部关闭右键菜单
const handleClickOutside = () => {
  showGraduationContextMenu.value = false
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<style scoped>
.graduation-plugin-card {
  margin-top: 20px;
}

.graduation-files {
  width: 100%;
}

.files-container {
  display: flex;
  gap: 12px;
  overflow-x: auto;
  padding: 4px 0;
  scrollbar-width: thin;
  scrollbar-color: #c0c4cc #f5f7fa;
}

.files-container::-webkit-scrollbar {
  height: 6px;
}

.files-container::-webkit-scrollbar-track {
  background: #f5f7fa;
  border-radius: 3px;
}

.files-container::-webkit-scrollbar-thumb {
  background: #c0c4cc;
  border-radius: 3px;
}

.files-container::-webkit-scrollbar-thumb:hover {
  background: #909399;
}

.file-type-section {
  flex: 0 0 auto;
  width: 240px;
  min-width: 220px;
  border: 2px solid #ebeef5;
  border-radius: 10px;
  padding: 12px;
  background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
  display: flex;
  flex-direction: column;
  transition: all 0.3s ease;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.04);
}

.file-type-section:hover {
  border-color: #c0c4cc;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.file-type-section.has-files {
  border-color: #409eff;
  background: linear-gradient(135deg, #ecf5ff 0%, #ffffff 100%);
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.15);
}

.file-type-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 10px;
  padding-bottom: 8px;
  border-bottom: 1.5px solid #ebeef5;
}

.file-type-icon-wrapper {
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #409eff 0%, #66b1ff 100%);
  border-radius: 6px;
  box-shadow: 0 2px 6px rgba(64, 158, 255, 0.3);
  flex-shrink: 0;
}

.file-type-icon {
  font-size: 16px;
  color: #fff;
}

.file-type-info {
  flex: 1;
  min-width: 0;
  display: flex;
  align-items: center;
  gap: 6px;
}

.file-type-label {
  font-size: 12px;
  font-weight: 600;
  color: #303133;
  line-height: 1.2;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.file-count-tag {
  flex-shrink: 0;
  font-weight: 500;
  font-size: 10px;
  padding: 1px 5px;
  height: 16px;
  line-height: 14px;
}

.file-list {
  display: flex;
  flex-direction: column;
  gap: 5px;
  flex: 1;
  min-height: 60px;
  max-height: 320px;
  overflow-y: auto;
  overflow-x: hidden;
}

.file-item {
  display: flex;
  align-items: flex-start;
  gap: 6px;
  padding: 6px 8px;
  background: #fff;
  border: 1px solid #e4e7ed;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04);
  min-height: 40px;
}

.file-item:hover {
  border-color: #409eff;
  background: linear-gradient(135deg, #ecf5ff 0%, #ffffff 100%);
  box-shadow: 0 2px 6px rgba(64, 158, 255, 0.2);
  transform: translateX(2px);
}

.file-icon {
  color: #409eff;
  font-size: 14px;
  flex-shrink: 0;
  margin-top: 2px;
}

.file-name {
  flex: 1;
  font-size: 11px;
  color: #606266;
  overflow: hidden;
  word-break: break-word;
  white-space: normal;
  line-height: 1.4;
  min-width: 0;
  display: -webkit-box;
  -webkit-line-clamp: 4;
  -webkit-box-orient: vertical;
  max-height: 5.6em;
}

.file-actions {
  display: flex;
  flex-direction: column;
  gap: 2px;
  opacity: 0;
  transition: opacity 0.2s;
  flex-shrink: 0;
  margin-top: 2px;
}

.file-item:hover .file-actions {
  opacity: 1;
}

.preview-btn,
.download-btn,
.untag-btn {
  opacity: 0;
  transition: opacity 0.2s;
}

.file-item:hover .preview-btn,
.file-item:hover .download-btn,
.file-item:hover .untag-btn {
  opacity: 1;
}

.action-btn {
  width: 20px !important;
  height: 20px !important;
  padding: 0 !important;
}

.action-btn :deep(.el-icon) {
  font-size: 12px !important;
}

.preview-container {
  max-height: 70vh;
  overflow: auto;
}

.preview-image {
  text-align: center;
  padding: 20px;
}

.preview-pdf {
  width: 100%;
  height: 70vh;
}

.preview-text {
  padding: 20px;
}

.text-preview {
  padding: 16px;
  background: #f5f7fa;
  border-radius: 4px;
  white-space: pre-wrap;
  word-wrap: break-word;
  font-family: 'Courier New', monospace;
  font-size: 14px;
  line-height: 1.6;
  max-height: 60vh;
  overflow: auto;
}

.preview-office {
  padding: 20px;
}

.office-content {
  padding: 20px;
  background: #fff;
  border-radius: 4px;
}

.excel-preview {
  overflow-x: auto;
}

.excel-sheet {
  margin-bottom: 30px;
}

.excel-sheet h3 {
  margin-bottom: 12px;
  color: #303133;
}

.file-empty {
  padding: 16px 8px;
  text-align: center;
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

.empty-text {
  font-size: 11px;
  color: #c0c4cc;
  font-style: italic;
}

.selected-file {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 8px;
  padding: 8px;
  background: #f5f7fa;
  border-radius: 4px;
  font-size: 14px;
  color: #606266;
}

.context-menu {
  position: fixed;
  background: #fff;
  border: 1px solid #e4e7ed;
  border-radius: 6px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  z-index: 9999;
  min-width: 180px;
  padding: 4px 0;
}

.menu-title {
  padding: 8px 16px;
  font-size: 12px;
  color: #909399;
  border-bottom: 1px solid #ebeef5;
  margin-bottom: 4px;
}

.menu-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  cursor: pointer;
  font-size: 14px;
  color: #606266;
  transition: background 0.2s;
}

.menu-item:hover {
  background: #f5f7fa;
}

.menu-item.danger {
  color: #f56c6c;
}

.menu-item.danger:hover {
  background: #fef0f0;
}

.menu-divider {
  height: 1px;
  background: #ebeef5;
  margin: 4px 0;
}

/* 上传拖拽区域样式 */
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
</style>

