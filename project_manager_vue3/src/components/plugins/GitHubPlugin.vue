<template>
  <BasePluginCard
    v-if="project"
    :project-id="project.id"
    plugin-type="github"
    title="GitHub 仓库"
    subtitle="查看仓库提交记录"
    :icon="Link"
    :icon-gradient="['#24292e', '#586069']"
    card-class="github-plugin-card"
  >
    <template #header-actions>
          <el-button
            type="primary"
            size="small"
            :icon="Edit"
            @click="showEditDialog = true"
          >
            {{ project.github_url ? '编辑' : '添加' }}
          </el-button>
    </template>

    <div v-if="!project.github_url" class="no-github">
      <el-empty description="暂无GitHub地址" :image-size="80">
        <el-button type="primary" @click="showEditDialog = true">添加GitHub地址</el-button>
      </el-empty>
    </div>

    <div v-else class="github-content">
      <!-- GitHub URL 显示 -->
      <div class="github-url-section">
        <el-link :href="project.github_url" target="_blank" type="primary" class="github-link">
          <el-icon><Link /></el-icon>
          <span>{{ project.github_url }}</span>
          <el-icon><TopRight /></el-icon>
        </el-link>
      </div>

      <!-- 分支选择 -->
      <div class="branch-selector">
        <el-form :inline="true" class="branch-form">
          <el-form-item label="分支">
              <el-select
                v-model="selectedBranch"
                placeholder="选择分支"
                style="width: 200px"
                @change="() => loadCommits(false)"
                :loading="loadingBranches"
              >
              <el-option
                v-for="branch in branches"
                :key="branch"
                :label="branch"
                :value="branch"
              />
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-button
              type="primary"
              :icon="Refresh"
              @click="handleSync"
              :loading="syncing"
            >
              {{ syncing ? '同步中...' : '同步' }}
            </el-button>
          </el-form-item>
          <el-form-item>
            <el-dropdown @command="handleExport" trigger="click">
              <el-button type="success" :icon="Download">
                导出
                <el-icon class="el-icon--right"><ArrowDown /></el-icon>
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="pdf">导出为 PDF</el-dropdown-item>
                  <el-dropdown-item command="markdown">导出为 Markdown</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </el-form-item>
        </el-form>
      </div>

      <!-- Commit 列表 -->
      <div class="commits-list" v-loading="loadingCommits">
        <div v-if="commits.length === 0 && !loadingCommits" class="no-commits">
          <el-empty description="暂无提交记录" :image-size="60" />
        </div>
        <div v-else class="commits-timeline">
          <div
            v-for="(commit, index) in displayedCommits"
            :key="commit.sha"
            class="commit-item"
            :style="{ animationDelay: `${index * 0.05}s` }"
          >
            <div class="commit-dot"></div>
            <div class="commit-line" v-if="index < commits.length - 1"></div>
            <div class="commit-content">
              <div class="commit-header">
                <div class="commit-message-wrapper">
                  <el-icon class="commit-icon"><Check /></el-icon>
                  <div class="commit-message">{{ commit.message }}</div>
                </div>
                <el-tag size="small" type="info" class="commit-sha" @click="copySha(commit.sha)">
                  {{ commit.sha.substring(0, 7) }}
                  <el-icon class="copy-icon"><DocumentCopy /></el-icon>
                </el-tag>
              </div>
              <div class="commit-meta">
                <div class="commit-author">
                  <div class="author-avatar">
                    <el-icon><User /></el-icon>
                  </div>
                  <span class="author-name">{{ commit.author }}</span>
                </div>
                <div class="commit-date">
                  <el-icon><Clock /></el-icon>
                  <span>{{ formatDate(commit.date) }}</span>
                </div>
              </div>
              <div class="commit-actions">
                <el-link
                  :href="commit.url"
                  target="_blank"
                  type="primary"
                  class="commit-link"
                >
                  <el-icon><View /></el-icon>
                  查看详情
                  <el-icon><TopRight /></el-icon>
                </el-link>
              </div>
            </div>
          </div>
          <!-- 展开更多按钮 -->
          <div v-if="commits.length > displayLimit" class="load-more-container">
            <el-button
              type="text"
              @click="toggleShowMore"
              class="load-more-btn"
            >
              {{ showAll ? '收起' : `展开更多 (${commits.length - displayLimit} 条)` }}
              <el-icon>
                <ArrowDown v-if="!showAll" />
                <ArrowUp v-else />
              </el-icon>
            </el-button>
          </div>
        </div>
      </div>
    </div>

    <!-- 编辑GitHub地址对话框 -->
    <el-dialog
      v-model="showEditDialog"
      title="编辑GitHub地址"
      width="500px"
    >
      <el-form
        ref="githubFormRef"
        :model="githubForm"
        :rules="githubRules"
        label-width="100px"
      >
        <el-form-item label="GitHub地址" prop="github_url">
          <el-input
            v-model="githubForm.github_url"
            placeholder="请输入GitHub仓库地址，例如：https://github.com/username/repo"
            clearable
            @keyup.enter="handleSaveGithubUrl"
            @blur="() => githubFormRef?.validateField('github_url')"
            @input="(val) => { console.log('输入值变化:', val); githubForm.value.github_url = val }"
          />
          <div class="form-tip">
            <el-icon><InfoFilled /></el-icon>
            <span>请输入完整的GitHub仓库URL，支持 https://github.com/owner/repo 格式</span>
          </div>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showEditDialog = false">取消</el-button>
        <el-button 
          type="primary" 
          @click="handleSaveGithubUrl" 
          :loading="saving"
          :disabled="saving"
        >
          {{ saving ? '保存中...' : '确定' }}
        </el-button>
      </template>
    </el-dialog>
  </BasePluginCard>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import {
  Link,
  TopRight,
  Edit,
  Refresh,
  User,
  Clock,
  InfoFilled,
  Check,
  DocumentCopy,
  View,
  Download,
  ArrowDown,
  ArrowUp,
} from '@element-plus/icons-vue'
import { projectApi, type Project, ProjectUpdate } from '@/api/project'
import { githubCommitApi, type GitHubCommit } from '@/api/githubCommit'
import BasePluginCard from './BasePluginCard.vue'

interface Props {
  project: Project
}

const props = defineProps<Props>()

const emit = defineEmits<{
  refresh: []
}>()

// GitHub URL编辑
const showEditDialog = ref(false)
const githubFormRef = ref<FormInstance>()
const saving = ref(false)
const githubForm = ref({
  github_url: '',
})

const githubRules: FormRules = {
  github_url: [
    {
      validator: (rule, value, callback) => {
        // 允许空值（用于清空URL）
        if (!value || !value.trim()) {
          callback()
          return
        }
        // 更宽松的GitHub URL验证，支持更多格式
        const trimmedValue = value.trim()
        const githubUrlPattern = /^https?:\/\/(www\.)?github\.com\/[\w\-\.]+\/[\w\-\.]+(\/)?$/
        if (!githubUrlPattern.test(trimmedValue)) {
          callback(new Error('请输入有效的GitHub仓库地址，例如：https://github.com/username/repo'))
        } else {
          callback()
        }
      },
      trigger: 'blur',
    },
  ],
}

// Commit相关
const selectedBranch = ref('main')
const branches = ref<string[]>(['main', 'master', 'develop'])
const commits = ref<GitHubCommit[]>([])
const loadingCommits = ref(false)
const loadingBranches = ref(false)
const syncing = ref(false)
let isManualSave = false // 标志，用于避免watch重复加载

// 展开更多功能
const displayLimit = ref(5) // 默认显示5条
const showAll = ref(false)
const displayedCommits = computed(() => {
  if (showAll.value) {
    return commits.value
  }
  return commits.value.slice(0, displayLimit.value)
})

const toggleShowMore = () => {
  showAll.value = !showAll.value
}

// 加载分支列表（暂时使用默认分支，后续可以从后端获取）
const loadBranches = async () => {
  // 分支列表可以从后端API获取，暂时使用默认值
  // 如果需要，可以添加一个获取分支列表的API
  if (!branches.value.includes(selectedBranch.value)) {
    selectedBranch.value = branches.value[0] || 'main'
  }
}

// 加载Commit记录（从后端API获取）
const loadCommits = async (forceSync: boolean = false) => {
  if (!props.project?.id || !selectedBranch.value) return
  
  // 检查是否有GitHub URL，如果没有则提前返回
  if (!props.project.github_url) {
    commits.value = []
    return
  }

  loadingCommits.value = true
  try {
    const data = await githubCommitApi.getCommits(props.project.id, {
      branch: selectedBranch.value,
      limit: 100,
      force_sync: forceSync,
    })
    
    commits.value = data.map(commit => ({
      sha: commit.sha,
      message: commit.message,
      author: commit.author,
      date: commit.commit_date,
      url: commit.url,
    }))
    
    // 重置展开状态
    showAll.value = false
  } catch (error: any) {
    console.error('加载提交记录失败:', error)
    const errorDetail = error.response?.data?.detail || '获取提交记录失败，请检查仓库地址和网络连接'
    ElMessage.error(errorDetail)
    commits.value = []
  } finally {
    loadingCommits.value = false
  }
}

// 手动同步
const handleSync = async () => {
  if (!props.project?.id || !selectedBranch.value) return

  syncing.value = true
  try {
    const data = await githubCommitApi.syncCommits(props.project.id, selectedBranch.value)
    commits.value = data.map(commit => ({
      sha: commit.sha,
      message: commit.message,
      author: commit.author,
      date: commit.commit_date,
      url: commit.url,
    }))
    ElMessage.success('同步成功')
  } catch (error: any) {
    console.error('同步提交记录失败:', error)
    ElMessage.error(error.response?.data?.detail || '同步失败')
  } finally {
    syncing.value = false
  }
}

// 保存GitHub URL
const handleSaveGithubUrl = async (event?: Event) => {
  // 阻止默认行为（如果有）
  if (event) {
    event.preventDefault()
    event.stopPropagation()
  }
  
  console.log('=== 开始保存GitHub URL ===')
  console.log('当前表单对象:', githubForm.value)
  console.log('当前表单值 (githubForm.value.github_url):', githubForm.value.github_url)
  console.log('表单值类型:', typeof githubForm.value.github_url)
  console.log('表单值长度:', githubForm.value.github_url?.length)
  console.log('项目ID:', props.project?.id)
  console.log('表单引用:', githubFormRef.value)
  
  // 尝试从DOM直接读取值（作为备用方案）
  if (githubFormRef.value) {
    const formEl = githubFormRef.value.$el || githubFormRef.value
    const inputEl = formEl?.querySelector?.('input[type="text"]') || formEl?.querySelector?.('input')
    if (inputEl) {
      console.log('从DOM读取的输入值:', inputEl.value)
      // 如果DOM中有值但表单对象中没有，使用DOM的值
      if (inputEl.value && !githubForm.value.github_url) {
        console.log('检测到DOM有值但表单对象为空，使用DOM值')
        githubForm.value.github_url = inputEl.value
      }
    }
  }
  
  if (!githubFormRef.value) {
    console.error('表单引用不存在')
    ElMessage.error('表单初始化失败，请刷新页面重试')
    return
  }
  
  if (!props.project?.id) {
    console.error('项目ID不存在:', props.project)
    ElMessage.error('项目信息不存在，请刷新页面重试')
    return
  }

  try {
    // 先进行表单验证
    console.log('开始表单验证...')
    let valid = false
    try {
      valid = await githubFormRef.value.validate()
    } catch (validationError) {
      console.error('表单验证出错:', validationError)
      valid = false
    }
    
    console.log('表单验证结果:', valid)
    
    if (!valid) {
      console.log('表单验证失败，显示错误信息')
      ElMessage.warning('请检查输入的GitHub地址格式是否正确')
      return
    }

    saving.value = true
    
    // 重新读取表单值（验证后再次确认）
    const formValue = githubForm.value.github_url
    console.log('验证后重新读取的表单值:', formValue)
    
    // 构建更新数据
    const updateData: ProjectUpdate = {}
    // 确保正确处理值：trim后如果为空字符串，则设置为null
    let inputValue = ''
    if (formValue && typeof formValue === 'string') {
      inputValue = formValue.trim()
    }
    
    console.log('处理后的输入值:', inputValue, '长度:', inputValue.length)
    
    // 如果输入为空，设置为null（清空URL）
    // 如果有值，设置为trim后的值
    updateData.github_url = inputValue ? inputValue : null
    
    console.log('准备保存的数据:', {
      projectId: props.project.id,
      githubUrl: updateData.github_url,
      updateData
    })
    
    // 保存URL
    console.log('调用API保存...')
    const updatedProject = await projectApi.update(props.project.id, updateData)
    
    console.log('API返回结果:', updatedProject)
    
    if (updatedProject) {
      console.log('保存成功！')
        ElMessage.success('保存成功')
        showEditDialog.value = false
      
      // 设置标志，避免watch重复加载
      isManualSave = true
      
      // 触发刷新，等待项目数据更新
      console.log('触发刷新事件...')
        emit('refresh')
      
      // 等待Vue响应式更新完成
      await nextTick()
      // 再等待一小段时间，确保loadProject完成
      await new Promise(resolve => setTimeout(resolve, 500))
        
        // 如果有URL，加载分支和提交记录
        if (updateData.github_url) {
        console.log('开始加载分支和提交记录...')
        // loadCommits会从后端读取最新的github_url，所以即使props.project还没更新也能工作
          await loadBranches()
          await loadCommits(true) // 强制同步
        } else {
          // 如果清空了URL，清空相关数据
          branches.value = []
          commits.value = []
      }
      console.log('=== 保存流程完成 ===')
    } else {
      throw new Error('保存失败：未返回更新后的项目数据')
        }
      } catch (error: any) {
    console.error('=== 保存GitHub地址失败 ===')
    console.error('错误详情:', error)
    console.error('错误响应:', error.response)
        const errorDetail = error.response?.data?.detail || error.message || '保存失败'
    ElMessage.error(`保存失败: ${errorDetail}`)
      } finally {
        saving.value = false
      }
}

// 格式化日期
const formatDate = (dateStr: string) => {
  const date = new Date(dateStr)
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  const days = Math.floor(diff / (1000 * 60 * 60 * 24))
  
  if (days === 0) {
    const hours = Math.floor(diff / (1000 * 60 * 60))
    if (hours === 0) {
      const minutes = Math.floor(diff / (1000 * 60))
      return `${minutes}分钟前`
    }
    return `${hours}小时前`
  } else if (days < 7) {
    return `${days}天前`
  } else {
    return date.toLocaleDateString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
    })
  }
}

// 复制SHA
const copySha = async (sha: string) => {
  try {
    await navigator.clipboard.writeText(sha)
    ElMessage.success('已复制SHA')
  } catch (error) {
    console.error('复制失败:', error)
    ElMessage.error('复制失败')
  }
}

// 导出功能
const handleExport = async (format: 'pdf' | 'markdown') => {
  if (!props.project?.github_url || commits.value.length === 0) {
    ElMessage.warning('没有可导出的提交记录')
    return
  }

  try {
    if (format === 'markdown') {
      exportToMarkdown()
    } else if (format === 'pdf') {
      await exportToPDF()
    }
  } catch (error: any) {
    console.error('导出失败:', error)
    ElMessage.error('导出失败: ' + (error.message || '未知错误'))
  }
}

// 导出为 Markdown
const exportToMarkdown = () => {
  const repoName = props.project?.github_url?.split('/').pop() || 'repository'
  const branch = selectedBranch.value
  const date = new Date().toLocaleDateString('zh-CN')
  
  let markdown = `# ${repoName} - 提交记录\n\n`
  markdown += `**分支**: ${branch}\n\n`
  markdown += `**导出时间**: ${date}\n\n`
  markdown += `**总计**: ${commits.value.length} 条提交\n\n`
  markdown += `---\n\n`

  commits.value.forEach((commit, index) => {
    markdown += `## ${index + 1}. ${commit.message}\n\n`
    markdown += `- **SHA**: \`${commit.sha}\`\n`
    markdown += `- **作者**: ${commit.author}\n`
    markdown += `- **时间**: ${formatDate(commit.date)}\n`
    markdown += `- **链接**: [查看详情](${commit.url})\n\n`
    markdown += `---\n\n`
  })

  // 创建下载链接
  const blob = new Blob([markdown], { type: 'text/markdown;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `${repoName}-commits-${branch}-${date.replace(/\//g, '-')}.md`
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
  
  ElMessage.success('Markdown 导出成功')
}

// 导出为 PDF
const exportToPDF = async () => {
  // 动态导入 jsPDF（如果未安装，需要先安装）
  try {
    // 使用 html2pdf.js 或 jsPDF
    // 这里使用简单的方案：先转换为 HTML，然后使用浏览器打印功能
    const repoName = props.project?.github_url?.split('/').pop() || 'repository'
    const branch = selectedBranch.value
    const date = new Date().toLocaleDateString('zh-CN')
    
    let html = `
      <!DOCTYPE html>
      <html>
      <head>
        <meta charset="UTF-8">
        <title>${repoName} - 提交记录</title>
        <style>
          body { font-family: Arial, sans-serif; padding: 20px; }
          h1 { color: #333; border-bottom: 2px solid #409eff; padding-bottom: 10px; }
          h2 { color: #666; margin-top: 20px; }
          .commit-item { margin: 15px 0; padding: 15px; border: 1px solid #e4e7ed; border-radius: 8px; }
          .commit-message { font-weight: bold; color: #303133; margin-bottom: 10px; }
          .commit-meta { color: #909399; font-size: 14px; }
          .commit-sha { font-family: monospace; background: #f5f7fa; padding: 2px 6px; border-radius: 4px; }
          table { width: 100%; border-collapse: collapse; margin-top: 20px; }
          th, td { padding: 10px; text-align: left; border-bottom: 1px solid #e4e7ed; }
          th { background-color: #f5f7fa; font-weight: bold; }
        </style>
      </head>
      <body>
        <h1>${repoName} - 提交记录</h1>
        <p><strong>分支</strong>: ${branch}</p>
        <p><strong>导出时间</strong>: ${date}</p>
        <p><strong>总计</strong>: ${commits.value.length} 条提交</p>
        <hr>
    `

    commits.value.forEach((commit, index) => {
      html += `
        <div class="commit-item">
          <div class="commit-message">${index + 1}. ${escapeHtml(commit.message)}</div>
          <div class="commit-meta">
            <span class="commit-sha">${commit.sha.substring(0, 7)}</span> | 
            <strong>作者</strong>: ${escapeHtml(commit.author)} | 
            <strong>时间</strong>: ${formatDate(commit.date)} | 
            <a href="${commit.url}" target="_blank">查看详情</a>
          </div>
        </div>
      `
    })

    html += `
      </body>
      </html>
    `

    // 打开新窗口并打印
    const printWindow = window.open('', '_blank')
    if (printWindow) {
      printWindow.document.write(html)
      printWindow.document.close()
      printWindow.onload = () => {
        setTimeout(() => {
          printWindow.print()
          ElMessage.success('PDF 导出成功（使用浏览器打印功能）')
        }, 250)
      }
    } else {
      ElMessage.warning('无法打开打印窗口，请允许弹出窗口')
    }
  } catch (error: any) {
    console.error('PDF 导出失败:', error)
    throw error
  }
}

// HTML 转义函数
const escapeHtml = (text: string) => {
  const div = document.createElement('div')
  div.textContent = text
  return div.innerHTML
}

// 监听对话框打开，初始化表单
watch(showEditDialog, (isOpen) => {
  if (isOpen) {
    // 对话框打开时，初始化表单为当前项目的 GitHub URL
    const currentUrl = props.project?.github_url || ''
    // 使用 nextTick 确保在 DOM 更新后设置值
    nextTick(() => {
      githubForm.value.github_url = currentUrl
      console.log('对话框打开，初始化表单URL:', currentUrl)
      console.log('设置后的表单值:', githubForm.value.github_url)
      
      // 清除验证状态
      if (githubFormRef.value) {
        githubFormRef.value.clearValidate()
        console.log('表单验证状态已清除')
      } else {
        console.warn('表单引用不存在，无法清除验证状态')
      }
    })
  } else {
    console.log('对话框关闭')
    console.log('关闭时的表单值:', githubForm.value.github_url)
  }
})

// 监听项目变化
watch(() => props.project.github_url, (newUrl, oldUrl) => {
  // 只有当对话框关闭时才更新表单，避免用户正在编辑时被打断
  if (!showEditDialog.value) {
    githubForm.value.github_url = newUrl || ''
  }
  // 只有当URL从无到有，或者URL发生变化时才加载commits
  // 避免在保存URL后重复加载（因为handleSaveGithubUrl已经会加载）
  if (newUrl && props.project?.id && newUrl !== oldUrl && !isManualSave) {
    // 延迟加载，避免与handleSaveGithubUrl中的加载冲突
    nextTick(() => {
      setTimeout(() => {
        if (props.project?.github_url === newUrl && !isManualSave) {
    loadBranches()
    loadCommits()
        }
      }, 500)
    })
  } else if (!newUrl) {
    commits.value = []
  }
  // 重置标志
  if (isManualSave) {
    setTimeout(() => {
      isManualSave = false
    }, 1000)
  }
}, { immediate: true })

onMounted(() => {
  if (props.project?.github_url && props.project?.id) {
    githubForm.value.github_url = props.project.github_url
    loadBranches()
    loadCommits()
  }
})
</script>

<style scoped>
.github-plugin-card {
  margin-top: 20px;
}

.card-header {
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
  background: linear-gradient(135deg, #24292e 0%, #586069 100%);
  border-radius: 10px;
  box-shadow: 0 2px 8px rgba(36, 41, 46, 0.3);
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
}

.no-github {
  padding: 40px 20px;
  text-align: center;
}

.github-content {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.github-url-section {
  padding: 12px 16px;
  background: #f5f7fa;
  border-radius: 8px;
  border: 1px solid #e4e7ed;
}

.github-link {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 500;
}

.branch-selector {
  padding: 12px 16px;
  background: #fafbfc;
  border-radius: 8px;
  border: 1px solid #e4e7ed;
}

.branch-form {
  margin: 0;
}

.commits-list {
  min-height: 200px;
}

.no-commits {
  padding: 40px 20px;
  text-align: center;
}

.commits-timeline {
  position: relative;
  padding-left: 32px;
}

.commit-item {
  position: relative;
  margin-bottom: 20px;
  animation: commitFadeIn 0.4s ease-out both;
}

@keyframes commitFadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.commit-dot {
  position: absolute;
  left: -28px;
  top: 8px;
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: linear-gradient(135deg, #409eff 0%, #66b1ff 100%);
  border: 3px solid #fff;
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.3);
  z-index: 2;
  transition: all 0.3s ease;
}

.commit-item:hover .commit-dot {
  transform: scale(1.3);
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.5);
}

.commit-line {
  position: absolute;
  left: -22px;
  top: 20px;
  bottom: -20px;
  width: 2px;
  background: linear-gradient(to bottom, #409eff, #e4e7ed);
  z-index: 1;
}

.commit-content {
  background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
  border: 1px solid #e4e7ed;
  border-radius: 12px;
  padding: 16px 18px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  position: relative;
  overflow: hidden;
}

.commit-content::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  width: 4px;
  height: 100%;
  background: linear-gradient(to bottom, #409eff, #66b1ff);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.commit-content:hover {
  border-color: #409eff;
  box-shadow: 0 8px 24px rgba(64, 158, 255, 0.2);
  transform: translateX(6px) translateY(-2px);
}

.commit-content:hover::before {
  opacity: 1;
}

.commit-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 12px;
}

.commit-message-wrapper {
  flex: 1;
  display: flex;
  align-items: flex-start;
  gap: 10px;
}

.commit-icon {
  font-size: 18px;
  color: #67c23a;
  margin-top: 2px;
  flex-shrink: 0;
  animation: iconPulse 2s ease-in-out infinite;
}

@keyframes iconPulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.7;
  }
}

.commit-message {
  flex: 1;
  font-size: 15px;
  font-weight: 600;
  color: #303133;
  line-height: 1.5;
  word-break: break-word;
}

.commit-sha {
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 11px;
  padding: 4px 8px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  gap: 4px;
  flex-shrink: 0;
}

.commit-sha:hover {
  background: #ecf5ff;
  transform: scale(1.05);
}

.copy-icon {
  font-size: 12px;
  opacity: 0.6;
  transition: opacity 0.2s;
}

.commit-sha:hover .copy-icon {
  opacity: 1;
}

.commit-meta {
  display: flex;
  align-items: center;
  gap: 20px;
  margin-bottom: 12px;
  font-size: 13px;
  color: #606266;
}

.commit-author {
  display: flex;
  align-items: center;
  gap: 8px;
}

.author-avatar {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 12px;
  flex-shrink: 0;
  box-shadow: 0 2px 6px rgba(102, 126, 234, 0.3);
}

.author-name {
  font-weight: 500;
  color: #303133;
}

.commit-date {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #909399;
}

.commit-actions {
  display: flex;
  justify-content: flex-end;
  padding-top: 8px;
  border-top: 1px solid #f0f2f5;
}

.commit-link {
  font-size: 13px;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: all 0.2s ease;
}

.commit-link:hover {
  gap: 8px;
}

.form-tip {
  display: flex;
  align-items: center;
  gap: 4px;
  margin-top: 6px;
  font-size: 12px;
  color: #909399;
}

.form-tip .el-icon {
  font-size: 14px;
}

.load-more-container {
  text-align: center;
  padding: 20px 0;
  margin-top: 20px;
}

.load-more-btn {
  color: #409eff;
  font-size: 14px;
  font-weight: 500;
  padding: 8px 16px;
  transition: all 0.3s ease;
}

.load-more-btn:hover {
  color: #66b1ff;
  transform: translateY(-2px);
}

.load-more-btn .el-icon {
  margin-left: 4px;
  transition: transform 0.3s ease;
}

.load-more-btn:hover .el-icon {
  transform: translateY(2px);
}
</style>

