<template>
  <div class="projects-page">
    <el-card class="projects-card">
      <template #header>
        <div class="card-header">
          <span class="page-title">项目管理</span>
          <el-button type="primary" @click="showCreateDialog = true" class="add-btn">
            <el-icon><Plus /></el-icon>
            新建项目
          </el-button>
        </div>
      </template>

      <!-- 筛选条件 -->
      <div class="filter-section">
        <el-form :inline="true" class="filter-form">
        <el-form-item label="平台">
          <el-select
            v-model="filters.platform_id"
            placeholder="全部平台"
            clearable
              size="small"
            @change="handleFilterChange"
              style="width: 150px"
          >
            <el-option
              v-for="platform in platforms"
              :key="platform.id"
              :label="platform.name"
              :value="platform.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select
            v-model="filters.status"
            placeholder="全部状态"
            clearable
              size="small"
            @change="handleFilterChange"
              style="width: 120px"
          >
            <el-option label="进行中" value="进行中" />
            <el-option label="已完成" value="已完成" />
            <el-option label="已结账" value="已结账" />
          </el-select>
        </el-form-item>
        <el-form-item label="标签">
          <el-select
            v-model="filters.tag_ids"
            placeholder="选择标签筛选"
            clearable
            multiple
            collapse-tags
            collapse-tags-tooltip
            size="small"
            @change="handleFilterChange"
            style="width: 200px"
          >
            <el-option
              v-for="tag in allTags"
              :key="tag.id"
              :label="tag.name"
              :value="tag.id"
            >
              <span :style="{ color: tag.color }">{{ tag.name }}</span>
            </el-option>
          </el-select>
        </el-form-item>
        <el-form-item>
            <el-button type="primary" size="small" @click="handleFilterChange">查询</el-button>
            <el-button size="small" @click="resetFilters">重置</el-button>
        </el-form-item>
      </el-form>
      </div>

      <!-- 项目列表 -->
      <div class="table-wrapper">
        <el-table 
          :data="projects" 
          style="width: 100%" 
          v-loading="loading" 
          :scroll="{ x: 'max-content' }"
          stripe
          class="projects-table"
          empty-text="暂无项目数据，请点击上方按钮创建新项目"
        >
          <el-table-column prop="title" label="项目名称" min-width="200">
            <template #default="{ row }">
              <div class="project-name-cell">
                <el-icon class="project-icon"><FolderOpened /></el-icon>
                <span>{{ row.title }}</span>
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="platform.name" label="平台" min-width="120">
            <template #default="{ row }">
              {{ row.platform?.name || '未知平台' }}
            </template>
          </el-table-column>
          <el-table-column label="标签" min-width="150">
            <template #default="{ row }">
              <div v-if="row.tags && row.tags.length > 0" class="project-tags-cell">
                <el-tag
                  v-for="tag in row.tags"
                  :key="tag.id"
                  size="small"
                  :style="{
                    backgroundColor: tag.color + '15',
                    borderColor: tag.color,
                    color: tag.color,
                    marginRight: '6px',
                    marginBottom: '4px'
                  }"
                  effect="plain"
                  round
                  @click.stop="handleTagClick(tag)"
                >
                  {{ tag.name }}
                </el-tag>
              </div>
              <span v-else class="no-tags">-</span>
            </template>
          </el-table-column>
          <el-table-column prop="price" label="金额" min-width="100" align="right">
            <template #default="{ row }">
              <span class="money-text">¥{{ (row.price || 0).toFixed(2) }}</span>
            </template>
          </el-table-column>
          <el-table-column label="当前状态" min-width="120">
            <template #default="{ row }">
              <el-tag :type="getCurrentStatusType(row)" size="small">
                {{ getCurrentStatus(row) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="is_paid" label="结账" min-width="80" align="center">
            <template #default="{ row }">
              <el-tag :type="row.is_paid ? 'success' : 'info'" size="small">
                {{ row.is_paid ? '已结' : '未结' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="进度" min-width="120">
            <template #default="{ row }">
              <el-progress
                :percentage="getProgress(row)"
                :color="getProgressColor(getProgress(row))"
                :stroke-width="6"
                :show-text="false"
              />
              <span class="progress-text">{{ getProgress(row) }}%</span>
            </template>
          </el-table-column>
          <el-table-column label="操作" min-width="150" fixed="right" align="center">
            <template #default="{ row }">
              <div class="action-buttons">
              <el-button
                type="primary"
                size="small"
                  :icon="View"
                @click="goToDetail(row.id)"
              >
                查看
              </el-button>
              <el-button
                type="danger"
                size="small"
                  :icon="Delete"
                @click="handleDelete(row)"
              >
                删除
              </el-button>
              </div>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </el-card>

    <!-- 创建项目对话框 -->
    <el-dialog
      v-model="showCreateDialog"
      title=""
      width="800px"
      class="create-project-dialog"
      :close-on-click-modal="false"
      @close="resetForm"
      :fullscreen="isMobile"
    >
      <template #header>
        <div class="dialog-header">
          <div class="header-icon-wrapper">
            <el-icon class="header-icon"><Plus /></el-icon>
          </div>
          <div class="header-content">
            <h3 class="dialog-title">创建新项目</h3>
            <p class="dialog-subtitle">填写项目信息，开始管理您的项目</p>
          </div>
        </div>
      </template>
      
      <div class="dialog-body">
        <el-form
          ref="formRef"
          :model="form"
          :rules="rules"
          label-width="120px"
          class="project-form"
        >
          <!-- 基本信息 -->
          <div class="form-section">
            <div class="section-header">
              <el-icon class="section-icon"><InfoFilled /></el-icon>
              <span class="section-title">基本信息</span>
            </div>
            <div class="form-row">
              <el-form-item label="项目名称" prop="title" class="form-item-half">
                <el-input 
                  v-model="form.title" 
                  placeholder="请输入项目名称"
                  size="large"
                  clearable
                >
                  <template #prefix>
                    <el-icon><Document /></el-icon>
                  </template>
                </el-input>
              </el-form-item>
              <el-form-item label="学生姓名" prop="student_name" class="form-item-half">
                <el-input 
                  v-model="form.student_name" 
                  placeholder="请输入学生姓名"
                  size="large"
                  clearable
                >
                  <template #prefix>
                    <el-icon><User /></el-icon>
                  </template>
                </el-input>
              </el-form-item>
            </div>
            <div class="form-row">
              <el-form-item label="接单平台" prop="platform_id" class="form-item-half">
                <el-select
                  v-model="form.platform_id"
                  placeholder="请选择平台"
                  size="large"
                  style="width: 100%"
                  popper-class="project-dialog-platform-select"
                >
                  <el-option
                    v-for="platform in platforms"
                    :key="platform.id"
                    :label="platform.name"
                    :value="platform.id"
                  />
                </el-select>
              </el-form-item>
              <el-form-item label="步骤模板" class="form-item-half">
                <el-select 
                  v-model="form.template_id" 
                  placeholder="选择步骤模板（默认使用默认模板）" 
                  clearable 
                  size="large"
                  style="width: 100%"
                >
                  <el-option
                    v-for="template in stepTemplates"
                    :key="template.id"
                    :label="template.name + (template.is_default ? '（默认）' : '')"
                    :value="template.id"
                  />
                </el-select>
              </el-form-item>
            </div>
          </div>

          <!-- 财务信息 -->
          <div class="form-section">
            <div class="section-header">
              <el-icon class="section-icon"><Money /></el-icon>
              <span class="section-title">财务信息</span>
            </div>
            <div class="form-row">
              <el-form-item label="订单金额" prop="price" class="form-item-half">
                <el-input-number
                  v-model="form.price"
                  :precision="2"
                  :min="0"
                  size="large"
                  style="width: 100%"
                  placeholder="请输入订单金额"
                  controls-position="right"
                />
              </el-form-item>
              <el-form-item label="实际金额" prop="actual_income" class="form-item-half">
                <el-input-number
                  v-model="form.actual_income"
                  :precision="2"
                  :min="0"
                  size="large"
                  style="width: 100%"
                  placeholder="请输入实际收入金额（可选）"
                  controls-position="right"
                />
              </el-form-item>
            </div>
            <div class="form-item-tip">
              <el-icon><InfoFilled /></el-icon>
              <span>实际收入用于财务统计，如不填写则默认为订单金额</span>
            </div>
          </div>

          <!-- 项目详情 -->
          <div class="form-section">
            <div class="section-header">
              <el-icon class="section-icon"><Edit /></el-icon>
              <span class="section-title">项目详情</span>
            </div>
            <el-form-item 
              v-if="selectedPlugins.includes('github')"
              label="GitHub地址" 
              prop="github_url"
            >
              <el-input 
                v-model="form.github_url" 
                placeholder="请输入GitHub仓库地址"
                size="large"
                clearable
              >
                <template #prefix>
                  <el-icon><Link /></el-icon>
                </template>
              </el-input>
              <div class="form-item-tip">
                <el-icon><InfoFilled /></el-icon>
                <span>启用GitHub插件后需要填写GitHub仓库地址</span>
              </div>
            </el-form-item>
            <el-form-item label="需求描述" prop="requirements">
              <el-input
                v-model="form.requirements"
                type="textarea"
                :rows="4"
                placeholder="请输入项目需求描述（可选）"
                show-word-limit
                maxlength="1000"
              />
            </el-form-item>
          </div>
          <!-- 需求文件 -->
          <div class="form-section">
            <div class="section-header">
              <el-icon class="section-icon"><FolderOpened /></el-icon>
              <span class="section-title">需求文件</span>
            </div>
            <el-form-item>
              <div class="upload-area-wrapper">
                <el-upload
                  ref="fileUploadRef"
                  :auto-upload="false"
                  :limit="10"
                  :on-change="handleFileChange"
                  :on-remove="handleFileRemove"
                  :file-list="requirementFiles"
                  multiple
                  drag
                  class="requirement-upload-area"
                >
                  <div class="upload-content">
                    <div class="upload-icon-wrapper">
                      <el-icon class="upload-icon"><Upload /></el-icon>
                    </div>
                    <div class="upload-text">
                      <p class="upload-main-text">点击或拖拽文件到此处上传</p>
                      <p class="upload-tip-text">支持所有文件类型，最多10个文件，将上传到"项目需求"文件夹</p>
                    </div>
                  </div>
                </el-upload>
                <!-- 文件预览列表 -->
                <div v-if="requirementFiles.length > 0" class="file-preview-list">
                  <div class="file-list-header">
                    <span class="file-count">已选择 {{ requirementFiles.length }} 个文件</span>
                    <el-button
                      type="text"
                      size="small"
                      @click="requirementFiles = []; fileUploadRef?.clearFiles()"
                    >
                      清空
                    </el-button>
                  </div>
                  <div class="file-list-content">
                    <div
                      v-for="(file, index) in requirementFiles"
                      :key="index"
                      class="file-preview-item"
                    >
                      <div class="file-icon">
                        <el-icon><Document /></el-icon>
                      </div>
                      <div class="file-info">
                        <div class="file-name" :title="file.name">{{ file.name }}</div>
                        <div class="file-size">{{ formatFileSize(file.size || 0) }}</div>
                      </div>
                      <el-button
                        type="danger"
                        :icon="Delete"
                        circle
                        size="small"
                        @click="handleFileRemove(file, requirementFiles)"
                      />
                    </div>
                  </div>
                </div>
              </div>
            </el-form-item>
          </div>

          <!-- 项目标签 -->
          <div class="form-section">
            <div class="section-header">
              <el-icon class="section-icon"><PriceTag /></el-icon>
              <span class="section-title">项目标签</span>
            </div>
            <el-form-item label="标签">
              <TagSelector v-model="form.tag_ids" />
            </el-form-item>
          </div>

          <!-- 插件选择 -->
          <div class="form-section">
            <div class="section-header">
              <el-icon class="section-icon"><Setting /></el-icon>
              <span class="section-title">启用插件</span>
              <el-button
                type="text"
                size="small"
                class="toggle-all-btn"
                @click="toggleAllPlugins"
              >
                {{ allPluginsSelected ? '全不选' : '全选' }}
              </el-button>
            </div>
            <el-form-item>
              <div class="plugins-selection">
            <div class="plugins-list">
              <div
                v-for="plugin in availablePlugins"
                :key="plugin.id"
                class="plugin-card"
                :class="{ 'is-selected': selectedPlugins.includes(plugin.id) }"
                @click="togglePlugin(plugin.id)"
              >
                <el-checkbox
                  :model-value="selectedPlugins.includes(plugin.id)"
                  @click.stop
                  @change="() => togglePlugin(plugin.id)"
                />
                <div class="plugin-icon-wrapper">
                  <el-icon class="plugin-icon"><component :is="plugin.icon" /></el-icon>
                </div>
                <div class="plugin-info">
                  <div class="plugin-name">{{ plugin.name }}</div>
                  <div class="plugin-description">{{ plugin.description }}</div>
                </div>
              </div>
              </div>
              <div class="plugins-tip">
                <el-icon><InfoFilled /></el-icon>
                <span>选择的插件将在项目创建后自动启用</span>
              </div>
            </div>
            </el-form-item>
          </div>
        </el-form>
      </div>
      
      <template #footer>
        <div class="dialog-footer">
          <el-button size="large" @click="showCreateDialog = false">取消</el-button>
          <el-button 
            type="primary" 
            size="large" 
            :loading="submitting" 
            @click="handleSubmit"
            class="submit-btn"
          >
            <el-icon v-if="!submitting"><Check /></el-icon>
            <span>{{ submitting ? '创建中...' : '创建项目' }}</span>
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessageBox, ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { Plus, Upload, Document, Delete, View, FolderOpened, InfoFilled, Link, User, Money, Edit, Setting, Check, Box, VideoPlay, PriceTag } from '@element-plus/icons-vue'
import { useProject } from '@/composables/useProject'
import { useUserStore } from '@/stores/user'
import type { Project, ProjectCreate } from '@/api/project'
import type { UploadFile, UploadFiles, UploadInstance } from 'element-plus'
import { attachmentApi } from '@/api/attachment'
import { stepTemplateApi, type StepTemplate } from '@/api/stepTemplate'
import { usePluginSettings } from '@/composables/usePluginSettings'
import { tagApi, type Tag } from '@/api/tag'
import TagSelector from '@/components/TagSelector.vue'

const userStore = useUserStore()
const formRef = ref<FormInstance>()
const submitting = ref(false)
const showCreateDialog = ref(false)
const fileUploadRef = ref<UploadInstance>()
const requirementFiles = ref<UploadFile[]>([])
const stepTemplates = ref<StepTemplate[]>([])

// 插件选择
const { enableProject } = usePluginSettings()
const selectedPlugins = ref<string[]>([])

// 可用插件列表
const availablePlugins = [
  {
    id: 'graduation',
    name: '毕设插件',
    description: '提供项目核心文件的标记和管理功能',
    icon: Document,
  },
  {
    id: 'github',
    name: 'GitHub插件',
    description: '显示GitHub仓库的提交记录和分支信息',
    icon: Link,
  },
  {
    id: 'parts',
    name: '元器件清单插件',
    description: '管理项目所需的元器件清单和成本统计',
    icon: Box,
  },
  {
    id: 'video-playback',
    name: '视频回放插件',
    description: '上传视频并生成安全观看链接',
    icon: VideoPlay,
  },
]

// 全选/全不选插件
const allPluginsSelected = computed(() => {
  return availablePlugins.every(plugin => selectedPlugins.value.includes(plugin.id))
})

const toggleAllPlugins = () => {
  if (allPluginsSelected.value) {
    selectedPlugins.value = []
  } else {
    selectedPlugins.value = availablePlugins.map(p => p.id)
  }
}

const togglePlugin = (pluginId: string) => {
  const index = selectedPlugins.value.indexOf(pluginId)
  if (index > -1) {
    selectedPlugins.value.splice(index, 1)
  } else {
    selectedPlugins.value.push(pluginId)
  }
}

// 使用Composable
const {
  loading,
  projects,
  platforms,
  loadPlatforms,
  loadProjects,
  createProject,
  deleteProject,
  goToDetail,
  getProgress,
  getProgressColor,
  getCurrentStatus,
  getCurrentStatusType,
} = useProject()

const filters = reactive({
  platform_id: undefined as number | undefined,
  status: undefined as string | undefined,
  tag_ids: [] as number[],
})

const allTags = ref<Tag[]>([])

const form = reactive<ProjectCreate>({
  title: '',
  student_name: '',
  platform_id: 0,
  user_id: userStore.userInfo?.id || 0,
  price: 0,
  actual_income: undefined,
  github_url: '',
  requirements: '',
  template_id: undefined,
  tag_ids: [],
})

const rules: FormRules = {
  title: [{ required: true, message: '请输入项目名称', trigger: 'blur' }],
  platform_id: [{ required: true, message: '请选择接单平台', trigger: 'change' }],
}

const isMobile = computed(() => {
  return window.innerWidth < 768
})

const handleFilterChange = () => {
  const params: any = {
    platform_id: filters.platform_id,
    status: filters.status,
  }
  
  // 如果有选中的标签，转换为逗号分隔的字符串
  if (filters.tag_ids && filters.tag_ids.length > 0) {
    params.tag_ids = filters.tag_ids.join(',')
  }
  
  loadProjects(params)
}

const resetFilters = () => {
  filters.platform_id = undefined
  filters.status = undefined
  filters.tag_ids = []
  loadProjects()
}

// 点击标签跳转到项目管理页面并筛选
const handleTagClick = (tag: any) => {
  // 如果当前标签已经在筛选列表中，则移除；否则添加
  const tagIndex = filters.tag_ids.indexOf(tag.id)
  if (tagIndex > -1) {
    filters.tag_ids.splice(tagIndex, 1)
  } else {
    filters.tag_ids.push(tag.id)
  }
  handleFilterChange()
}

// 加载标签列表
const loadTags = async () => {
  try {
    allTags.value = await tagApi.list(true)
  } catch (error) {
    console.error('加载标签失败:', error)
    ElMessage.error('加载标签失败')
  }
}

const resetForm = () => {
  formRef.value?.resetFields()
  Object.assign(form, {
    title: '',
    student_name: '',
    platform_id: 0,
    user_id: userStore.userInfo?.id || 0,
    price: 0,
    actual_income: undefined,
    github_url: '',
    requirements: '',
    template_id: undefined,
    tag_ids: [],
  })
  requirementFiles.value = []
  fileUploadRef.value?.clearFiles()
  selectedPlugins.value = []
}

const loadStepTemplates = async () => {
  try {
    await stepTemplateApi.ensureDefault()
    stepTemplates.value = await stepTemplateApi.list()
    // 默认选择默认模板
    const defaultTemplate = stepTemplates.value.find(t => t.is_default)
    if (defaultTemplate && !form.template_id) {
      form.template_id = defaultTemplate.id
    }
  } catch (error) {
    console.error('加载模板列表失败:', error)
  }
}

// 处理文件变化
const handleFileChange = (file: UploadFile, files: UploadFiles) => {
  // 验证文件大小
  if (file.raw) {
    if (file.raw.size > 1 * 1024 * 1024 * 1024) {
      ElMessage.error('单个文件不能超过1GB')
      return
    }
  }
  requirementFiles.value = files
}

// 处理文件移除
const handleFileRemove = (file: UploadFile, files?: UploadFiles) => {
  if (files) {
    requirementFiles.value = files
  } else {
    requirementFiles.value = requirementFiles.value.filter(f => f.uid !== file.uid)
    fileUploadRef.value?.handleRemove(file)
  }
}

// 格式化文件大小
const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
}

const handleSubmit = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (valid) {
      submitting.value = true
      try {
        // 先创建项目
        const newProject = await createProject(form)
        
        // 启用选择的插件（独立控制每个插件）
        if (selectedPlugins.value.includes('graduation')) {
          enableProject(newProject.id, 'graduation')
        }
        if (selectedPlugins.value.includes('github')) {
          enableProject(newProject.id, 'github')
        }
        if (selectedPlugins.value.includes('parts')) {
          enableProject(newProject.id, 'parts')
        }
        if (selectedPlugins.value.includes('video-playback')) {
          enableProject(newProject.id, 'video-playback')
        }
        
        // 如果有需求文件，上传到"项目需求"文件夹
        // 后端会自动更新项目创建日志，添加文件信息
        if (requirementFiles.value.length > 0) {
          try {
            // 获取"项目需求"文件夹
            const { attachmentFolderApi } = await import('@/api/attachmentFolder')
            const folders = await attachmentFolderApi.list(newProject.id)
            const requirementFolder = folders.find(f => f.name === '项目需求')
            
            if (requirementFolder) {
              // 上传所有文件到"项目需求"文件夹
              // 后端会自动检测并更新项目创建日志
              const filesToUpload = requirementFiles.value.map(f => f.raw).filter(Boolean) as File[]
              if (filesToUpload.length > 0) {
                const { batchUploadFiles } = await import('@/utils/uploadHelper')
                await batchUploadFiles(newProject.id, filesToUpload, {
                  fileType: '项目需求',
                  folderId: requirementFolder.id
                })
              }
              ElMessage.success('项目创建成功，需求文件已上传')
            } else {
              ElMessage.warning('项目创建成功，但未找到"项目需求"文件夹，文件上传失败')
            }
          } catch (error) {
            console.error('上传需求文件失败:', error)
            ElMessage.warning('项目创建成功，但需求文件上传失败')
          }
        }
        
        showCreateDialog.value = false
        resetForm()
      } catch (error) {
        // 错误已在Service层处理
      } finally {
        submitting.value = false
      }
    }
  })
}

const handleDelete = async (project: Project) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除项目"${project.title}"吗？`,
      '提示',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )
    
    await deleteProject(project.id)
  } catch (error: any) {
    if (error !== 'cancel') {
      // 错误已在Service层处理
    }
  }
}

onMounted(async () => {
  console.log('Projects page mounted')
  try {
    await Promise.all([
      loadPlatforms(),
      loadStepTemplates(),
      loadTags(),
      loadProjects()
    ])
    console.log('Platforms loaded:', platforms.value)
    console.log('Templates loaded:', stepTemplates.value)
    console.log('Tags loaded:', allTags.value)
    console.log('Projects loaded:', projects.value)
  } catch (error) {
    console.error('Error loading data:', error)
  }
})
</script>

<style scoped>
.projects-page {
  padding: 20px;
  background: #f5f7fa;
  min-height: calc(100vh - 60px);
}

.projects-card {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
  font-weight: 600;
  color: #303133;
}

.page-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.add-btn {
  color: #fff;
}

.filter-section {
  padding: 16px;
  background: #fafafa;
  border-radius: 6px;
  margin-bottom: 16px;
}

.filter-form {
  margin: 0;
}

.table-wrapper {
  overflow-x: auto;
  width: 100%;
}

.projects-table {
  margin-top: 16px;
}

.projects-table :deep(.el-table__row) {
  transition: background-color 0.2s;
}

.projects-table :deep(.el-table__row:hover) {
  background: #f5f7fa;
}

.project-name-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}

.project-icon {
  color: #409eff;
  font-size: 16px;
}

.money-text {
  font-weight: 600;
  color: #303133;
}

.progress-text {
  font-size: 12px;
  color: #909399;
  margin-left: 8px;
}

.action-buttons {
  display: flex;
  gap: 8px;
  justify-content: center;
}

.upload-area-wrapper {
  width: 100%;
}

.requirement-upload-area {
  width: 100%;
}

.requirement-upload-area :deep(.el-upload) {
  width: 100%;
}

.requirement-upload-area :deep(.el-upload-dragger) {
  width: 100%;
  padding: 40px 20px;
  border: 2px dashed #dcdfe6;
  border-radius: 8px;
  background: #fafafa;
  transition: all 0.3s;
}

.requirement-upload-area :deep(.el-upload-dragger:hover) {
  border-color: #409eff;
  background: #f0f7ff;
}

.upload-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}

.upload-icon {
  font-size: 48px;
  color: #409eff;
}

.upload-text {
  text-align: center;
}

.upload-main-text {
  font-size: 14px;
  color: #303133;
  font-weight: 500;
  margin: 0 0 8px 0;
}

.upload-tip-text {
  font-size: 12px;
  color: #909399;
  margin: 0;
}

.form-item-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
  line-height: 1.5;
}

.file-preview-list {
  margin-top: 16px;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  overflow: hidden;
  background: #fff;
}

.file-list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: #f5f7fa;
  border-bottom: 1px solid #e4e7ed;
}

.file-count {
  font-size: 13px;
  color: #606266;
  font-weight: 500;
}

.file-list-content {
  max-height: 240px;
  overflow-y: auto;
  padding: 8px;
}

.file-preview-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 12px;
  background: #fafafa;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  transition: all 0.2s;
  margin-bottom: 8px;
}

.file-preview-item:last-child {
  margin-bottom: 0;
}

.file-preview-item:hover {
  background: #f0f7ff;
  border-color: #b3d8ff;
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
  color: #303133;
  font-weight: 500;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  margin-bottom: 4px;
}

.file-size {
  font-size: 12px;
  color: #909399;
}

/* 移动端样式 */
@media (max-width: 768px) {
  .projects-page {
    padding: 12px;
    min-height: auto;
  }

  .projects-card :deep(.el-card__body) {
    padding: 12px !important;
  }

  .card-header {
    flex-direction: column;
    align-items: stretch;
    gap: 8px;
  }

  .page-title {
    font-size: 15px;
    text-align: center;
  }

  .add-btn {
    width: 100%;
  }

  .filter-section {
    padding: 10px;
    margin-bottom: 12px;
  }

  .filter-form {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }

  .filter-form .el-form-item {
    margin-right: 0;
    margin-bottom: 8px;
    width: 100%;
  }

  .filter-form .el-form-item__label {
    font-size: 12px;
    padding-bottom: 4px;
  }

  .filter-form .el-select,
  .filter-form .el-input {
    width: 100% !important;
  }

  .filter-form .el-form-item:last-child {
    display: flex;
    justify-content: center;
    gap: 8px;
    margin-top: 8px;
  }

  .filter-form .el-form-item:last-child .el-form-item__content {
    display: flex;
    justify-content: center;
    gap: 8px;
  }

  .table-wrapper {
    margin: 0 -12px;
    padding: 0 12px;
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
  }

  .projects-table {
    margin-top: 0;
    min-width: 600px;
  }

  .projects-table :deep(.el-table__cell) {
    padding: 8px 4px !important;
  }

  .project-name-cell {
    font-size: 12px;
  }

  .project-icon {
    font-size: 14px;
  }

  .money-text {
    font-size: 12px;
  }

  .progress-text {
    font-size: 10px;
  }

  .action-buttons {
    flex-wrap: nowrap;
    gap: 4px;
  }

  .action-buttons .el-button {
    padding: 5px 8px !important;
    font-size: 11px !important;
  }

  /* 隐藏标签列在移动端 */
  .projects-table :deep(.el-table__body) .el-table__cell:nth-child(3),
  .projects-table :deep(.el-table__header) .el-table__cell:nth-child(3) {
    display: none;
  }

  /* 对话框样式 */
  .create-project-dialog :deep(.el-dialog) {
    margin-top: 0 !important;
  }

  .create-project-dialog :deep(.el-dialog__header) {
    padding: 16px !important;
  }

  .create-project-dialog :deep(.el-dialog__body) {
    padding: 12px !important;
    max-height: 70vh;
  }

  .dialog-header {
    flex-direction: column;
    text-align: center;
    gap: 12px;
  }

  .header-icon-wrapper {
    width: 48px;
    height: 48px;
  }

  .dialog-title {
    font-size: 16px !important;
  }

  .dialog-subtitle {
    font-size: 12px !important;
  }

  .dialog-body {
    padding: 0;
  }

  .form-section {
    margin-bottom: 16px;
    padding: 12px;
  }

  .section-header {
    margin-bottom: 12px;
  }

  .section-title {
    font-size: 13px;
  }

  .form-row {
    flex-direction: column;
    gap: 0;
  }

  .form-item-half {
    width: 100% !important;
  }

  .project-form :deep(.el-form-item__label) {
    font-size: 12px;
    padding-bottom: 4px;
  }

  .project-form :deep(.el-input__inner) {
    font-size: 14px;
  }

  /* 上传区域 */
  .requirement-upload-area :deep(.el-upload-dragger) {
    padding: 20px 10px !important;
  }

  .upload-icon {
    font-size: 32px;
  }

  .upload-main-text {
    font-size: 13px;
  }

  .upload-tip-text {
    font-size: 11px;
  }

  /* 插件选择 */
  .plugins-list {
    grid-template-columns: 1fr;
  }

  .plugin-card {
    padding: 12px;
  }

  .plugin-icon-wrapper {
    width: 36px;
    height: 36px;
  }

  .plugin-icon {
    font-size: 18px;
  }

  .plugin-name {
    font-size: 13px;
  }

  .plugin-description {
    font-size: 11px;
  }

  .dialog-footer {
    flex-direction: column;
    gap: 8px;
  }

  .dialog-footer .el-button {
    width: 100%;
    margin: 0;
  }

  .submit-btn {
    order: -1;
  }
}

@media (max-width: 480px) {
  .projects-page {
    padding: 8px;
  }

  .page-title {
    font-size: 14px;
  }

  .filter-section {
    padding: 8px;
  }

  .form-section {
    padding: 10px;
  }

  .projects-table {
    min-width: 500px;
  }
}

.tags-cell {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.project-tag {
  font-size: 12px;
  padding: 2px 8px;
  border-radius: 4px;
}

.project-tags-cell {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  align-items: center;
}

.project-tags-cell .el-tag {
  cursor: pointer;
  transition: all 0.3s;
  font-size: 12px;
  padding: 2px 8px;
}

.project-tags-cell .el-tag:hover {
  transform: scale(1.1);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.no-tags {
  color: #909399;
  font-size: 12px;
  font-style: italic;
  color: #909399;
  font-size: 12px;

  .action-buttons .el-button {
    width: 100%;
  }
}

/* 创建项目对话框美化 */
.create-project-dialog :deep(.el-dialog__header) {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px 24px;
  border-radius: 8px 8px 0 0;
}

.create-project-dialog :deep(.el-dialog__title) {
  color: #fff;
  font-size: 18px;
  font-weight: 600;
}

.create-project-dialog :deep(.el-dialog__headerbtn .el-dialog__close) {
  color: #fff;
  font-size: 20px;
}

.create-project-dialog :deep(.el-dialog__headerbtn:hover .el-dialog__close) {
  color: #f0f0f0;
}

.create-project-dialog :deep(.el-dialog__body) {
  padding: 24px;
  background: #fafbfc;
}

.create-project-dialog :deep(.el-form-item__label) {
  font-weight: 500;
  color: #303133;
}

.create-project-dialog :deep(.el-input__wrapper) {
  border-radius: 6px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.create-project-dialog :deep(.el-input__wrapper:hover) {
  box-shadow: 0 2px 6px rgba(64, 158, 255, 0.15);
}

.create-project-dialog :deep(.el-select .el-input__wrapper) {
  border-radius: 6px;
}

.create-project-dialog :deep(.el-textarea__inner) {
  border-radius: 6px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.create-project-dialog :deep(.el-textarea__inner:hover) {
  box-shadow: 0 2px 6px rgba(64, 158, 255, 0.15);
}

.create-project-dialog :deep(.el-dialog__footer) {
  padding: 16px 24px;
  background: #fafbfc;
  border-top: 1px solid #ebeef5;
}

/* 插件选择样式 */
.plugins-selection {
  width: 100%;
}

.plugins-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 12px;
  margin-bottom: 12px;
}

.plugin-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  background: #fff;
  border: 2px solid #e4e7ed;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.04);
}

.plugin-card:hover {
  border-color: #409eff;
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.15);
  transform: translateY(-2px);
}

.plugin-card.is-selected {
  border-color: #409eff;
  background: linear-gradient(135deg, #ecf5ff 0%, #ffffff 100%);
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.2);
}

.plugin-icon-wrapper {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 10px;
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
  flex-shrink: 0;
}

.plugin-card.is-selected .plugin-icon-wrapper {
  background: linear-gradient(135deg, #409eff 0%, #66b1ff 100%);
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.4);
}

.plugin-icon {
  font-size: 22px;
  color: #fff;
}

.plugin-info {
  flex: 1;
  min-width: 0;
}

.plugin-name {
  font-size: 15px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 4px;
}

.plugin-description {
  font-size: 12px;
  color: #909399;
  line-height: 1.4;
}

.plugins-tip {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 10px 12px;
  background: #f0f7ff;
  border: 1px solid #b3d8ff;
  border-radius: 6px;
  font-size: 12px;
  color: #606266;
}

.plugins-tip .el-icon {
  color: #409eff;
  font-size: 14px;
}
</style>
