<template>
  <div class="video-watch-page">
    <!-- Token无效提示 -->
    <div v-if="!token" class="password-verify-container">
      <div class="verify-card">
        <div class="verify-header">
          <el-icon class="verify-icon"><WarningFilled /></el-icon>
          <h2>链接无效</h2>
          <p class="verify-subtitle">您访问的链接无效或已过期</p>
        </div>
        <div class="error-message" style="margin-top: 24px;">
          <el-icon><WarningFilled /></el-icon>
          <span>请检查链接是否正确，或联系视频提供者获取新的观看链接</span>
        </div>
      </div>
    </div>

    <!-- 密码验证界面 -->
    <div v-else-if="!verified" class="password-verify-container">
      <div class="verify-card">
        <div class="verify-header">
          <el-icon class="verify-icon"><Lock /></el-icon>
          <h2>视频访问验证</h2>
          <p class="verify-subtitle">请输入访问密码以观看视频</p>
        </div>
        <el-form
          ref="passwordFormRef"
          :model="passwordForm"
          :rules="passwordRules"
          @submit.prevent="handleVerify"
        >
          <el-form-item prop="password">
            <el-input
              v-model="passwordForm.password"
              type="password"
              placeholder="请输入访问密码"
              size="large"
              show-password
              clearable
              @keyup.enter="handleVerify"
            >
              <template #prefix>
                <el-icon><Lock /></el-icon>
              </template>
            </el-input>
          </el-form-item>
          <el-form-item>
            <el-button
              type="primary"
              size="large"
              :loading="verifying"
              @click="handleVerify"
              style="width: 100%"
            >
              验证并观看
            </el-button>
          </el-form-item>
        </el-form>
        <el-alert
          v-if="errorMessage"
          :title="errorMessage"
          type="error"
          :closable="false"
          show-icon
          class="error-alert"
        >
          <template #default>
            <div class="error-content">
              <div class="error-text">{{ getFriendlyErrorMessage(errorMessage) }}</div>
              <div class="error-tips">
                <p>💡 提示：</p>
                <ul>
                  <li>请检查密码是否正确，注意大小写</li>
                  <li>如果忘记密码，请联系视频提供者</li>
                </ul>
              </div>
            </div>
          </template>
        </el-alert>
      </div>
    </div>

    <!-- 视频播放界面 -->
    <div v-else class="video-player-container">
      <div class="video-header">
        <h1 class="video-title">{{ videoInfo?.title || '视频播放' }}</h1>
        <div v-if="videoInfo?.description" class="video-description">
          {{ videoInfo.description }}
        </div>
      </div>

      <div class="video-wrapper">
        <video
          ref="videoPlayerRef"
          :src="videoUrl"
          controls
          class="video-player"
          @loadedmetadata="handleVideoLoaded"
          @timeupdate="handleTimeUpdate"
          @ended="handleVideoEnded"
        >
          您的浏览器不支持视频播放
        </video>
      </div>

      <div class="video-info">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="文件大小">
            {{ formatFileSize(videoInfo?.file_size || 0) }}
          </el-descriptions-item>
          <el-descriptions-item label="观看次数">
            {{ linkInfo?.view_count || 0 }}
          </el-descriptions-item>
          <el-descriptions-item label="最大观看次数">
            {{ linkInfo?.max_views || '无限制' }}
          </el-descriptions-item>
          <el-descriptions-item label="过期时间">
            {{ linkInfo?.expires_at ? formatDate(linkInfo.expires_at) : '永久有效' }}
          </el-descriptions-item>
        </el-descriptions>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { Lock, WarningFilled } from '@element-plus/icons-vue'
import { videoPlaybackApi, type VideoPlayback, type VideoPlaybackLink } from '@/api/videoPlayback'

const route = useRoute()

const token = route.params.token as string

const verified = ref(false)
const verifying = ref(false)
const errorMessage = ref('')
const videoInfo = ref<VideoPlayback | null>(null)
const linkInfo = ref<VideoPlaybackLink | null>(null)
const videoUrl = ref('')
const videoPlayerRef = ref<HTMLVideoElement>()

const passwordFormRef = ref<FormInstance>()
const passwordForm = ref({
  password: '',
})

const passwordRules: FormRules = {
  password: [{ required: true, message: '请输入访问密码', trigger: 'blur' }],
}

// 观看统计
let watchStartTime = 0
let watchTimer: number | null = null
let lastRecordTime = 0
const RECORD_INTERVAL = 10000 // 每10秒记录一次

// 验证密码
const handleVerify = async () => {
  if (!passwordFormRef.value) return

  try {
    await passwordFormRef.value.validate()
    verifying.value = true
    errorMessage.value = ''

    const result = await videoPlaybackApi.verifyPassword(token, passwordForm.value.password)
    
    // 从验证结果中获取视频和链接信息
    if (result.video) {
      videoInfo.value = result.video
    }
    if (result.link) {
      linkInfo.value = result.link
    }

    // 构建视频URL
    videoUrl.value = `/api/video-playbacks/watch/${token}/video`

    verified.value = true
    
    // 等待视频元素加载后，恢复观看进度
    await nextTick()
    if (videoPlayerRef.value && result.link?.last_watch_position && result.link.last_watch_position > 0) {
      // 从上次观看位置继续播放
      videoPlayerRef.value.addEventListener('loadedmetadata', () => {
        if (videoPlayerRef.value && result.link?.last_watch_position) {
          videoPlayerRef.value.currentTime = result.link.last_watch_position
        }
      }, { once: true })
    }
    
    // 记录观看开始
    watchStartTime = Date.now()
    startWatchTracking()
  } catch (error: any) {
    console.error('验证失败:', error)
    // 验证失败时，只显示错误信息，不跳转
    let errorDetail = ''
    
    if (error.response) {
      // 从响应中获取错误信息
      errorDetail = error.response.data?.detail || error.response.data?.message || ''
    } else if (error.message) {
      errorDetail = error.message
    }
    
    // 将技术性错误信息转换为友好提示
    if (errorDetail.includes('401') || errorDetail.includes('Unauthorized')) {
      errorDetail = '密码验证失败'
    } else if (errorDetail.includes('403') || errorDetail.includes('Forbidden')) {
      errorDetail = '访问被拒绝'
    } else if (errorDetail.includes('404') || errorDetail.includes('Not Found')) {
      errorDetail = '链接不存在或已失效'
    } else if (errorDetail.includes('Request failed')) {
      errorDetail = '网络请求失败，请稍后重试'
    } else if (!errorDetail || errorDetail.trim() === '') {
      errorDetail = '密码错误，请重试'
    }
    
    errorMessage.value = errorDetail
    
    // 清空密码输入框，方便用户重新输入
    passwordForm.value.password = ''
    passwordFormRef.value?.clearValidate()
    
    // 不显示ElMessage，只显示页面内的错误提示
  } finally {
    verifying.value = false
  }
}

// 开始观看追踪
const startWatchTracking = () => {
  // 立即记录一次
  recordWatchProgress()

  // 定期记录
  watchTimer = window.setInterval(() => {
    recordWatchProgress()
  }, RECORD_INTERVAL)
}

// 记录观看进度
const recordWatchProgress = async () => {
  if (!videoPlayerRef.value || !videoInfo.value) return

  try {
    const currentTime = videoPlayerRef.value.currentTime
    const duration = videoPlayerRef.value.duration
    const watchDuration = Math.floor(Date.now() / 1000 - watchStartTime / 1000)
    const watchPercentage = duration > 0 ? (currentTime / duration) * 100 : 0

    // 只在有显著变化时记录统计
    if (Math.abs(currentTime - lastRecordTime) > 5) {
      await videoPlaybackApi.recordView(
        token,
        watchDuration,
        watchPercentage
      )
      lastRecordTime = currentTime
    }
    
    // 保存观看位置（每5秒保存一次）
    if (currentTime > 0 && Math.abs(currentTime - lastRecordTime) > 5) {
      await videoPlaybackApi.saveProgress(token, currentTime)
    }
  } catch (error) {
    console.error('记录观看进度失败:', error)
  }
}

// 视频加载完成
const handleVideoLoaded = () => {
  if (videoPlayerRef.value) {
    recordWatchProgress()
  }
}

// 时间更新 - 定期保存观看进度
let lastSaveTime = 0
const SAVE_PROGRESS_INTERVAL = 5000 // 每5秒保存一次进度

const handleTimeUpdate = async () => {
  if (!videoPlayerRef.value || !verified.value) return
  
  const currentTime = videoPlayerRef.value.currentTime
  const now = Date.now()
  
  // 每5秒保存一次观看进度
  if (now - lastSaveTime >= SAVE_PROGRESS_INTERVAL && currentTime > 0) {
    try {
      await videoPlaybackApi.saveProgress(token, currentTime)
      lastSaveTime = now
    } catch (error) {
      console.error('保存观看进度失败:', error)
    }
  }
}

// 视频播放结束
const handleVideoEnded = async () => {
  if (!videoInfo.value) return

  try {
    const duration = videoPlayerRef.value?.duration || 0
    const watchDuration = Math.floor(Date.now() / 1000 - watchStartTime / 1000)
    
    await videoPlaybackApi.recordView(
      token,
      watchDuration,
      100 // 观看百分比100%
    )
    
    // 播放结束时，将进度重置为0（表示已看完）
    if (videoPlayerRef.value) {
      await videoPlaybackApi.saveProgress(token, 0)
    }
  } catch (error) {
    console.error('记录观看结束失败:', error)
  }

  // 停止追踪
  stopWatchTracking()
}

// 停止观看追踪
const stopWatchTracking = () => {
  if (watchTimer !== null) {
    clearInterval(watchTimer)
    watchTimer = null
  }
}

// 获取友好的错误信息
const getFriendlyErrorMessage = (error: string): string => {
  if (error.includes('密码') || error.includes('验证失败')) {
    return '密码验证失败，请检查密码是否正确'
  } else if (error.includes('链接') || error.includes('不存在') || error.includes('失效')) {
    return '观看链接无效或已过期'
  } else if (error.includes('网络') || error.includes('请求失败')) {
    return '网络连接异常，请检查网络后重试'
  } else if (error.includes('访问被拒绝') || error.includes('权限')) {
    return '您没有权限访问此视频'
  } else {
    return error || '验证失败，请重试'
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

onMounted(() => {
  if (!token) {
    errorMessage.value = '无效的观看链接，请检查链接是否正确'
    ElMessage.error('无效的观看链接')
  }
})

onUnmounted(() => {
  stopWatchTracking()
  // 保存最终观看进度
  if (verified.value && videoPlayerRef.value && videoPlayerRef.value.currentTime > 0) {
    videoPlaybackApi.saveProgress(token, videoPlayerRef.value.currentTime).catch(err => {
      console.error('保存最终观看进度失败:', err)
    })
  }
})
</script>

<style scoped>
.video-watch-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.password-verify-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: calc(100vh - 40px);
}

.verify-card {
  background: #fff;
  border-radius: 16px;
  padding: 40px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
  width: 100%;
  max-width: 400px;
}

.verify-header {
  text-align: center;
  margin-bottom: 32px;
}

.verify-icon {
  font-size: 48px;
  color: #409eff;
  margin-bottom: 16px;
}

.verify-header h2 {
  margin: 0 0 8px 0;
  font-size: 24px;
  color: #303133;
}

.verify-subtitle {
  margin: 0;
  font-size: 14px;
  color: #909399;
}

.error-alert {
  margin-top: 16px;
}

.error-content {
  padding: 8px 0;
}

.error-text {
  font-size: 14px;
  color: #f56c6c;
  margin-bottom: 12px;
}

.error-tips {
  font-size: 12px;
  color: #606266;
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid #ebeef5;
}

.error-tips p {
  margin: 0 0 8px 0;
  font-weight: 600;
}

.error-tips ul {
  margin: 0;
  padding-left: 20px;
}

.error-tips li {
  margin: 4px 0;
  line-height: 1.6;
}

.video-player-container {
  max-width: 1200px;
  margin: 0 auto;
  background: #fff;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
}

.video-header {
  margin-bottom: 24px;
}

.video-title {
  margin: 0 0 8px 0;
  font-size: 24px;
  color: #303133;
}

.video-description {
  font-size: 14px;
  color: #606266;
  margin-top: 8px;
}

.video-wrapper {
  position: relative;
  width: 100%;
  padding-bottom: 56.25%; /* 16:9 aspect ratio */
  background: #000;
  border-radius: 8px;
  overflow: hidden;
  margin-bottom: 24px;
}

.video-player {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
}

.video-info {
  margin-top: 24px;
}

/* 移动端样式 */
@media (max-width: 768px) {
  .video-watch-page {
    padding: 12px;
  }

  .video-player-container {
    padding: 12px;
    border-radius: 8px;
  }

  .video-header {
    margin-bottom: 12px;
  }

  .video-title {
    font-size: 18px;
  }

  .video-description {
    font-size: 13px;
  }

  .video-wrapper {
    margin-bottom: 12px;
    border-radius: 4px;
  }

  .video-info {
    margin-top: 12px;
  }

  .video-info :deep(.el-descriptions__label) {
    font-size: 12px;
  }

  .video-info :deep(.el-descriptions__content) {
    font-size: 12px;
  }

  .error-container {
    padding: 20px;
  }

  .error-icon {
    font-size: 48px;
  }

  .error-title {
    font-size: 16px;
  }

  .error-message {
    font-size: 13px;
  }

  .back-button {
    padding: 8px 16px;
    font-size: 13px;
  }
}

@media (max-width: 480px) {
  .video-watch-page {
    padding: 8px;
  }

  .video-player-container {
    padding: 8px;
    border-radius: 4px;
  }

  .video-title {
    font-size: 16px;
  }

  .video-description {
    font-size: 12px;
  }

  .error-container {
    padding: 16px;
  }

  .error-icon {
    font-size: 36px;
  }

  .error-title {
    font-size: 14px;
  }
}
</style>
