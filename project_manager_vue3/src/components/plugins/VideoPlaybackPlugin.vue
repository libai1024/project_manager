<template>
  <BasePluginCard
    :project-id="project.id"
    plugin-type="video-playback"
    title="视频回放"
    subtitle="上传视频并生成安全观看链接"
    :icon="VideoPlay"
    :icon-gradient="['#f56c6c', '#f78989']"
    card-class="video-playback-plugin-card"
  >
    <template #header-actions>
      <el-button
        size="small"
        :icon="Refresh"
        @click="handleRefresh"
        :loading="refreshing"
      >
        刷新
      </el-button>
      <el-button
        type="primary"
        size="small"
        :icon="Upload"
        @click="showUploadDialog = true"
      >
        上传视频
      </el-button>
    </template>

    <!-- 视频列表 -->
    <div v-if="videos.length > 0" class="videos-list">
      <div
        v-for="video in videos"
        :key="video.id"
        class="video-item"
      >
        <div class="video-header">
          <div class="video-info">
            <div class="video-title-row">
              <el-icon class="video-icon"><VideoPlay /></el-icon>
              <span class="video-title">{{ video.title }}</span>
              <el-tag size="small" type="info">{{ formatFileSize(video.file_size) }}</el-tag>
            </div>
            <div v-if="video.description" class="video-description">
              {{ video.description }}
            </div>
            <div class="video-meta">
              <span>链接数: {{ video.link_count }}</span>
              <span>观看次数: {{ video.total_views }}</span>
              <span>上传时间: {{ formatDate(video.created_at) }}</span>
            </div>
          </div>
          <div class="video-actions">
            <el-button
              size="small"
              :icon="DataAnalysis"
              @click="showStatistics(video)"
            >
              统计
            </el-button>
            <el-button
              size="small"
              :icon="Link"
              @click="toggleVideoExpand(video)"
            >
              {{ expandedVideos.has(video.id) ? '收起链接' : '展开链接' }}
            </el-button>
            <el-button
              size="small"
              :icon="Link"
              @click="showLinkDialogHandler(video)"
            >
              管理链接
            </el-button>
            <el-button
              size="small"
              type="danger"
              :icon="Delete"
              @click="handleDelete(video)"
            >
              删除
            </el-button>
          </div>
        </div>
        
        <!-- 展开的链接列表 -->
        <div v-if="expandedVideos.has(video.id)" class="video-links-expanded">
          <div class="links-header">
            <span class="links-title">观看链接列表</span>
            <el-button
              type="primary"
              size="small"
              :icon="Plus"
              @click="showCreateLinkDialogForVideo(video)"
            >
              创建新链接
            </el-button>
          </div>
          <div v-loading="loadingLinksMap[video.id]" class="links-content">
            <div v-if="videoLinksMap[video.id] && videoLinksMap[video.id].length > 0" class="links-list">
              <div
                v-for="link in videoLinksMap[video.id]"
                :key="link.id"
                class="link-item"
              >
                <div class="link-main">
                  <div class="link-url-section">
                    <div class="link-label">观看链接：</div>
                    <el-input
                      :value="link.watch_url"
                      readonly
                      size="small"
                      class="link-input"
                    >
                      <template #append>
                        <el-button
                          :icon="DocumentCopy"
                          @click="copyLink(link.watch_url)"
                          size="small"
                        />
                      </template>
                    </el-input>
                  </div>
                  <div class="link-info">
                    <el-descriptions :column="4" size="small" border>
                      <el-descriptions-item label="描述">
                        {{ link.description || '无描述' }}
                      </el-descriptions-item>
                      <el-descriptions-item label="观看次数">
                        {{ link.view_count }}
                      </el-descriptions-item>
                      <el-descriptions-item label="最大次数">
                        {{ link.max_views || '无限制' }}
                      </el-descriptions-item>
                      <el-descriptions-item label="过期时间">
                        {{ link.expires_at ? formatDate(link.expires_at) : '永久有效' }}
                      </el-descriptions-item>
                      <el-descriptions-item label="状态">
                        <el-tag :type="link.is_active ? 'success' : 'info'" size="small">
                          {{ link.is_active ? '激活' : '禁用' }}
                        </el-tag>
                      </el-descriptions-item>
                    </el-descriptions>
                  </div>
                </div>
                <div class="link-actions">
                  <el-button
                    type="danger"
                    size="small"
                    :icon="Delete"
                    @click="handleDeleteLink(link)"
                  >
                    删除
                  </el-button>
                </div>
              </div>
            </div>
            <el-empty v-else description="暂无链接" :image-size="60" />
          </div>
        </div>
      </div>
    </div>

    <el-empty v-else description="暂无视频，点击上方按钮上传" :image-size="100" />

    <!-- 上传对话框 -->
    <el-dialog
      v-model="showUploadDialog"
      title="上传视频"
      width="600px"
      @close="resetUploadForm"
    >
      <el-form
        ref="uploadFormRef"
        :model="uploadForm"
        :rules="uploadRules"
        label-width="100px"
      >
        <el-form-item label="视频标题" prop="title">
          <el-input
            v-model="uploadForm.title"
            placeholder="请输入视频标题"
            clearable
          />
        </el-form-item>
        <el-form-item label="视频描述" prop="description">
          <el-input
            v-model="uploadForm.description"
            type="textarea"
            :rows="3"
            placeholder="请输入视频描述（可选）"
            clearable
          />
        </el-form-item>
        <el-form-item label="选择视频" prop="file">
          <el-upload
            ref="uploadRef"
            :auto-upload="false"
            :limit="1"
            :on-change="handleFileChange"
            :on-remove="handleFileRemove"
            accept="video/*"
            drag
          >
            <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
            <div class="el-upload__text">
              将视频拖到此处，或<em>点击上传</em>
            </div>
            <template #tip>
              <div class="el-upload__tip">
                支持 MP4、AVI、MOV、WMV、FLV、WEBM、MKV 格式，最大 1GB
              </div>
            </template>
          </el-upload>
        </el-form-item>
        <el-form-item v-if="uploading">
          <el-progress :percentage="uploadProgress" :status="uploadProgress === 100 ? 'success' : undefined" />
          <div style="text-align: center; margin-top: 8px; color: #909399; font-size: 12px;">
            {{ uploadProgress }}% - 正在上传视频...
          </div>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showUploadDialog = false" :disabled="uploading">取消</el-button>
        <el-button type="primary" @click="handleUpload" :loading="uploading" :disabled="uploading">
          {{ uploading ? `上传中 ${uploadProgress}%` : '上传' }}
        </el-button>
      </template>
    </el-dialog>

    <!-- 链接管理对话框 -->
    <el-dialog
      v-model="showLinkDialog"
      :title="`管理链接 - ${currentVideo?.title || ''}`"
      width="800px"
    >
      <div class="link-management">
        <div class="link-actions">
          <el-button
            type="primary"
            :icon="Plus"
            @click="showCreateLinkDialog = true"
          >
            创建新链接
          </el-button>
        </div>

        <el-table :data="links" style="width: 100%" v-loading="loadingLinks">
          <el-table-column prop="watch_url" label="观看链接" min-width="300">
            <template #default="{ row }">
              <div class="link-url-cell">
                <el-input
                  :value="row.watch_url"
                  readonly
                  size="small"
                >
                  <template #append>
                    <el-button
                      :icon="DocumentCopy"
                      @click="copyLink(row.watch_url)"
                    />
                  </template>
                </el-input>
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="view_count" label="观看次数" width="100" />
          <el-table-column prop="max_views" label="最大次数" width="100">
            <template #default="{ row }">
              {{ row.max_views || '无限制' }}
            </template>
          </el-table-column>
          <el-table-column prop="expires_at" label="过期时间" width="180">
            <template #default="{ row }">
              {{ row.expires_at ? formatDate(row.expires_at) : '永久有效' }}
            </template>
          </el-table-column>
          <el-table-column prop="is_active" label="状态" width="80">
            <template #default="{ row }">
              <el-tag :type="row.is_active ? 'success' : 'info'" size="small">
                {{ row.is_active ? '激活' : '禁用' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="100">
            <template #default="{ row }">
              <el-button
                type="danger"
                size="small"
                :icon="Delete"
                @click="handleDeleteLink(row)"
              />
            </template>
          </el-table-column>
        </el-table>
      </div>
    </el-dialog>

    <!-- 创建链接对话框 -->
    <el-dialog
      v-model="showCreateLinkDialog"
      title="创建观看链接"
      width="500px"
      @close="resetLinkForm"
    >
      <el-form
        ref="linkFormRef"
        :model="linkForm"
        :rules="linkRules"
        label-width="120px"
      >
        <el-form-item label="访问密码" prop="password">
          <el-input
            v-model="linkForm.password"
            type="password"
            placeholder="请输入访问密码"
            show-password
            clearable
          />
        </el-form-item>
        <el-form-item label="有效期（天）" prop="expires_in_days">
          <el-input-number
            v-model="linkForm.expires_in_days"
            :min="1"
            :max="365"
            placeholder="留空表示永久有效"
            style="width: 100%"
          />
          <div class="form-tip">留空表示永久有效</div>
        </el-form-item>
        <el-form-item label="最大观看次数" prop="max_views">
          <el-input-number
            v-model="linkForm.max_views"
            :min="1"
            placeholder="留空表示无限制"
            style="width: 100%"
          />
          <div class="form-tip">留空表示无限制</div>
        </el-form-item>
        <el-form-item label="链接描述" prop="description">
          <el-input
            v-model="linkForm.description"
            type="textarea"
            :rows="2"
            placeholder="请输入链接描述（可选）"
            clearable
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateLinkDialog = false">取消</el-button>
        <el-button type="primary" @click="handleCreateLink" :loading="creatingLink">
          创建
        </el-button>
      </template>
    </el-dialog>

    <!-- 统计对话框 -->
    <el-dialog
      v-model="showStatisticsDialog"
      :title="`观看统计 - ${currentVideo?.title || ''}`"
      width="600px"
    >
      <div v-if="statistics" class="statistics-content">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="总观看次数">
            {{ statistics.total_views }}
          </el-descriptions-item>
          <el-descriptions-item label="平均观看时长">
            {{ formatDuration(statistics.avg_duration) }}
          </el-descriptions-item>
          <el-descriptions-item label="总观看时长">
            {{ formatDuration(statistics.total_duration) }}
          </el-descriptions-item>
          <el-descriptions-item label="平均观看百分比">
            {{ statistics.avg_percentage.toFixed(1) }}%
          </el-descriptions-item>
        </el-descriptions>
      </div>
      <div v-else v-loading="true" style="min-height: 200px" />
    </el-dialog>
  </BasePluginCard>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import {
  VideoPlay,
  Upload,
  Link,
  Delete,
  Plus,
  DocumentCopy,
  DataAnalysis,
  UploadFilled,
  Refresh,
} from '@element-plus/icons-vue'
import BasePluginCard from './BasePluginCard.vue'
import { videoPlaybackApi, type VideoPlayback, type VideoPlaybackLink, type VideoPlaybackLinkCreate, type VideoStatistics } from '@/api/videoPlayback'
import type { Project } from '@/api/project'

interface Props {
  project: Project
}

const props = defineProps<Props>()

const emit = defineEmits<{
  refresh: []
}>()

const videos = ref<VideoPlayback[]>([])
const loadingLinks = ref(false)
const uploading = ref(false)
const creatingLink = ref(false)
const refreshing = ref(false)

// 展开的视频ID集合
const expandedVideos = ref<Set<number>>(new Set())
// 每个视频的链接列表
const videoLinksMap = ref<Record<number, VideoPlaybackLink[]>>({})
// 每个视频的链接加载状态
const loadingLinksMap = ref<Record<number, boolean>>({})

// 上传相关
const showUploadDialog = ref(false)
const uploadProgress = ref(0)
const uploadFormRef = ref<FormInstance>()
const uploadRef = ref()
const uploadForm = ref({
  title: '',
  description: '',
  file: null as File | null,
})

const uploadRules: FormRules = {
  title: [{ required: true, message: '请输入视频标题', trigger: 'blur' }],
  file: [{ required: true, message: '请选择视频文件', trigger: 'change' }],
}

// 链接管理相关
const showLinkDialog = ref(false)
const showCreateLinkDialog = ref(false)
const linkFormRef = ref<FormInstance>()
const currentVideo = ref<VideoPlayback | null>(null)
const links = ref<VideoPlaybackLink[]>([])

const linkForm = ref<VideoPlaybackLinkCreate>({
  password: '',
  expires_in_days: undefined,
  max_views: undefined,
  description: '',
})

const linkRules: FormRules = {
  password: [{ required: true, message: '请输入访问密码', trigger: 'blur' }],
}

// 统计相关
const showStatisticsDialog = ref(false)
const statistics = ref<VideoStatistics | null>(null)

// 加载视频列表
const loadVideos = async () => {
  try {
    videos.value = await videoPlaybackApi.list(props.project.id)
    // 如果视频已展开，刷新其链接列表
    for (const videoId of expandedVideos.value) {
      await loadLinksForVideo(videoId)
    }
  } catch (error: any) {
    console.error('加载视频列表失败:', error)
    ElMessage.error(error.response?.data?.detail || '加载失败')
  }
}

// 刷新数据
const handleRefresh = async () => {
  refreshing.value = true
  try {
    await loadVideos()
    ElMessage.success('刷新成功')
  } catch (error: any) {
    console.error('刷新失败:', error)
    ElMessage.error(error.response?.data?.detail || '刷新失败')
  } finally {
    refreshing.value = false
  }
}

// 文件处理
const handleFileChange = (file: any) => {
  uploadForm.value.file = file.raw
}

const handleFileRemove = () => {
  uploadForm.value.file = null
}

// 上传视频
const handleUpload = async () => {
  if (!uploadFormRef.value) return

  try {
    await uploadFormRef.value.validate()
    
    if (!uploadForm.value.file) {
      ElMessage.warning('请选择视频文件')
      return
    }

    uploading.value = true
    uploadProgress.value = 0
    await videoPlaybackApi.upload(
      props.project.id,
      uploadForm.value.file,
      uploadForm.value.title,
      uploadForm.value.description || undefined,
      (progressEvent) => {
        if (progressEvent.total) {
          uploadProgress.value = Math.round((progressEvent.loaded * 100) / progressEvent.total)
        }
      }
    )
    
    ElMessage.success('上传成功')
    showUploadDialog.value = false
    uploadProgress.value = 0
    resetUploadForm()
    await loadVideos()
    emit('refresh')
  } catch (error: any) {
    console.error('上传失败:', error)
    uploadProgress.value = 0
    ElMessage.error(error.response?.data?.detail || '上传失败')
  } finally {
    uploading.value = false
  }
}

const resetUploadForm = () => {
  uploadForm.value = {
    title: '',
    description: '',
    file: null,
  }
  uploadRef.value?.clearFiles()
  uploadFormRef.value?.clearValidate()
}

// 删除视频
const handleDelete = async (video: VideoPlayback) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除视频"${video.title}"吗？此操作不可恢复。`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )

    await videoPlaybackApi.delete(video.id)
    ElMessage.success('删除成功')
    await loadVideos()
    emit('refresh')
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
      ElMessage.error(error.response?.data?.detail || '删除失败')
    }
  }
}

// 切换视频展开状态
const toggleVideoExpand = async (video: VideoPlayback) => {
  if (expandedVideos.value.has(video.id)) {
    // 收起
    expandedVideos.value.delete(video.id)
  } else {
    // 展开
    expandedVideos.value.add(video.id)
    // 加载链接列表
    await loadLinksForVideo(video.id)
  }
}

// 为指定视频加载链接列表
const loadLinksForVideo = async (videoId: number) => {
  loadingLinksMap.value[videoId] = true
  try {
    videoLinksMap.value[videoId] = await videoPlaybackApi.listLinks(videoId)
  } catch (error: any) {
    console.error('加载链接列表失败:', error)
    ElMessage.error(error.response?.data?.detail || '加载失败')
    videoLinksMap.value[videoId] = []
  } finally {
    loadingLinksMap.value[videoId] = false
  }
}

// 显示链接管理对话框
const showLinkDialogHandler = async (video: VideoPlayback) => {
  currentVideo.value = video
  showLinkDialog.value = true
  await loadLinks(video.id)
}

// 为展开的视频创建链接
const showCreateLinkDialogForVideo = (video: VideoPlayback) => {
  currentVideo.value = video
  showCreateLinkDialog.value = true
}

// 加载链接列表
const loadLinks = async (videoId: number) => {
  loadingLinks.value = true
  try {
    links.value = await videoPlaybackApi.listLinks(videoId)
  } catch (error: any) {
    console.error('加载链接列表失败:', error)
    ElMessage.error(error.response?.data?.detail || '加载失败')
  } finally {
    loadingLinks.value = false
  }
}

// 创建链接
const handleCreateLink = async () => {
  if (!linkFormRef.value || !currentVideo.value) return

  try {
    await linkFormRef.value.validate()
    
    creatingLink.value = true
    const linkData: VideoPlaybackLinkCreate = {
      password: linkForm.value.password,
      expires_in_days: linkForm.value.expires_in_days || undefined,
      max_views: linkForm.value.max_views || undefined,
      description: linkForm.value.description || undefined,
    }
    
    await videoPlaybackApi.createLink(currentVideo.value.id, linkData)
    ElMessage.success('链接创建成功')
    showCreateLinkDialog.value = false
    resetLinkForm()
    
    // 刷新链接列表
    await loadLinks(currentVideo.value.id)
    // 如果视频已展开，刷新展开区域的链接列表
    if (expandedVideos.value.has(currentVideo.value.id)) {
      await loadLinksForVideo(currentVideo.value.id)
    }
    // 刷新视频列表（更新链接数和观看数）
    await loadVideos()
  } catch (error: any) {
    console.error('创建链接失败:', error)
    ElMessage.error(error.response?.data?.detail || '创建失败')
  } finally {
    creatingLink.value = false
  }
}

const resetLinkForm = () => {
  linkForm.value = {
    password: '',
    expires_in_days: undefined,
    max_views: undefined,
    description: '',
  }
  linkFormRef.value?.clearValidate()
}

// 删除链接
const handleDeleteLink = async (link: VideoPlaybackLink) => {
  try {
    await ElMessageBox.confirm(
      '确定要删除此链接吗？',
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )

    await videoPlaybackApi.deleteLink(link.id)
    ElMessage.success('删除成功')
    
    // 刷新链接列表
    if (currentVideo.value) {
      await loadLinks(currentVideo.value.id)
      // 如果视频已展开，刷新展开区域的链接列表
      if (expandedVideos.value.has(currentVideo.value.id)) {
        await loadLinksForVideo(currentVideo.value.id)
      }
    }
    
    // 刷新视频列表（更新链接数和观看数）
    await loadVideos()
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
      ElMessage.error(error.response?.data?.detail || '删除失败')
    }
  }
}

// 复制链接
const copyLink = (url: string) => {
  navigator.clipboard.writeText(url).then(() => {
    ElMessage.success('链接已复制到剪贴板')
  }).catch(() => {
    ElMessage.error('复制失败')
  })
}

// 显示统计
const showStatistics = async (video: VideoPlayback) => {
  currentVideo.value = video
  showStatisticsDialog.value = true
  try {
    statistics.value = await videoPlaybackApi.getStatistics(video.id)
  } catch (error: any) {
    console.error('加载统计失败:', error)
    ElMessage.error(error.response?.data?.detail || '加载失败')
  }
}

// 工具函数
const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
}

const formatDate = (dateStr: string): string => {
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN')
}

const formatDuration = (seconds: number): string => {
  const hours = Math.floor(seconds / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  const secs = Math.floor(seconds % 60)
  
  if (hours > 0) {
    return `${hours}小时${minutes}分钟${secs}秒`
  } else if (minutes > 0) {
    return `${minutes}分钟${secs}秒`
  } else {
    return `${secs}秒`
  }
}

onMounted(() => {
  loadVideos()
})
</script>

<style scoped>
.videos-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.video-item {
  padding: 16px;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  background: #fff;
  transition: all 0.3s;
}

.video-item:hover {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  border-color: #409eff;
}

.video-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 16px;
}

.video-info {
  flex: 1;
  min-width: 0;
}

.video-title-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.video-icon {
  font-size: 20px;
  color: #409eff;
}

.video-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.video-description {
  font-size: 14px;
  color: #606266;
  margin-bottom: 8px;
}

.video-meta {
  display: flex;
  gap: 16px;
  font-size: 12px;
  color: #909399;
}

.video-actions {
  display: flex;
  gap: 8px;
  flex-shrink: 0;
}

.link-management {
  padding: 10px 0;
}

.link-actions {
  margin-bottom: 16px;
}

.link-url-cell {
  display: flex;
  align-items: center;
}

.form-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

.statistics-content {
  padding: 10px 0;
}

/* 展开的链接区域 */
.video-links-expanded {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #e4e7ed;
}

.links-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.links-title {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
}

.links-content {
  min-height: 50px;
}

.links-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.link-item {
  padding: 12px;
  border: 1px solid #e4e7ed;
  border-radius: 6px;
  background: #fafafa;
  transition: all 0.3s;
}

.link-item:hover {
  border-color: #409eff;
  background: #f0f9ff;
}

.link-main {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.link-url-section {
  display: flex;
  align-items: center;
  gap: 8px;
}

.link-label {
  font-size: 13px;
  color: #606266;
  white-space: nowrap;
  min-width: 70px;
}

.link-input {
  flex: 1;
}

.link-info {
  margin-left: 78px;
}

.link-actions {
  margin-top: 8px;
  text-align: right;
}
</style>

