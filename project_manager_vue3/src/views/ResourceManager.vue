<template>
  <div class="resource-manager">
    <el-row :gutter="0" class="manager-container">
      <!-- 左侧项目选择栏 -->
      <el-col :span="6" class="project-sidebar">
        <div class="sidebar-header">
          <h3>项目列表</h3>
        </div>
        
        <!-- 搜索和排序工具栏 -->
        <div class="toolbar">
          <el-input
            v-model="projectSearchKeyword"
            placeholder="搜索项目..."
            clearable
            size="small"
            class="search-input"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
          
          <!-- 排序切换按钮组 -->
          <div class="sort-tabs">
            <div
              class="sort-tab"
              :class="{ active: projectSortBy === 'name' }"
              @click="projectSortBy = 'name'"
            >
              <el-icon :size="14"><Sort /></el-icon>
              <span>名称</span>
            </div>
            <div
              class="sort-tab"
              :class="{ active: projectSortBy === 'time' }"
              @click="projectSortBy = 'time'"
            >
              <el-icon :size="14"><Timer /></el-icon>
              <span>时间</span>
            </div>
            <div
              class="sort-tab"
              :class="{ active: projectSortBy === 'progress' }"
              @click="projectSortBy = 'progress'"
            >
              <el-icon :size="14"><TrendCharts /></el-icon>
              <span>进度</span>
            </div>
          </div>
        </div>
        
        <!-- 项目列表 -->
        <div class="project-list" v-loading="loadingProjects">
          <div
            v-for="project in filteredAndSortedProjects"
            :key="project.id"
            class="project-item"
            :class="{ active: selectedProjectId === project.id }"
            @click="selectProject(project.id)"
          >
            <!-- 项目图标 -->
            <div class="project-icon">
              <el-icon :size="24">
                <FolderOpened v-if="selectedProjectId === project.id" />
                <Folder v-else />
              </el-icon>
            </div>
            
            <!-- 项目信息 -->
            <div class="project-info">
              <div class="project-title-row">
                <span class="project-title">{{ project.title }}</span>
                <el-tag 
                  :type="getStatusType(project.status)" 
                  size="small"
                  class="status-tag"
                >
                  {{ project.status }}
                </el-tag>
              </div>
              
              <div class="project-meta-row">
                <div class="meta-item">
                  <el-icon :size="14"><TrendCharts /></el-icon>
                  <span class="meta-text">{{ getProjectProgress(project) }}%</span>
                </div>
                <div class="meta-item">
                  <el-icon :size="14"><Timer /></el-icon>
                  <span class="meta-text">{{ formatDate(project.updated_at) }}</span>
                </div>
              </div>
              
              <!-- 进度条 -->
              <div class="progress-bar-container">
                <el-progress
                  :percentage="getProjectProgress(project)"
                  :stroke-width="4"
                  :show-text="false"
                  :color="getProgressColor(getProjectProgress(project))"
                  class="progress-bar"
                />
              </div>
            </div>
          </div>
          
          <el-empty
            v-if="!loadingProjects && filteredAndSortedProjects.length === 0"
            description="暂无项目"
            :image-size="80"
          />
        </div>
      </el-col>
      
      <!-- 右侧文件资源管理器 -->
      <el-col :span="18" class="file-manager">
        <div v-if="!selectedProjectId" class="empty-state">
          <el-empty description="请从左侧选择一个项目" :image-size="120" />
        </div>
        
        <div v-else class="file-manager-content">
          <!-- 工具栏 -->
          <div class="file-manager-toolbar">
            <div class="toolbar-left">
              <h3>{{ currentProject?.title || '文件管理' }}</h3>
              <el-breadcrumb separator="/" class="breadcrumb">
                <el-breadcrumb-item>
                  <span @click="currentFolderId = null">全部文件</span>
                </el-breadcrumb-item>
                <el-breadcrumb-item
                  v-for="folder in folderPath"
                  :key="folder.id"
                >
                  <span @click="navigateToFolder(folder.id)">{{ folder.name }}</span>
                </el-breadcrumb-item>
              </el-breadcrumb>
            </div>
            
            <div class="toolbar-center">
              <el-button-group>
                <el-button
                  size="small"
                  :disabled="selectedFiles.length === 0"
                  @click="handleRenameSelected"
                >
                  <el-icon><Edit /></el-icon>
                  重命名
                </el-button>
                <el-button
                  size="small"
                  :disabled="selectedFiles.length === 0"
                  @click="handleCopySelected"
                >
                  <el-icon><CopyDocument /></el-icon>
                  复制
                </el-button>
                <el-button
                  size="small"
                  :disabled="clipboardItems.length === 0"
                  @click="handlePaste"
                >
                  <el-icon><DocumentCopy /></el-icon>
                  粘贴
                </el-button>
                <el-button
                  size="small"
                  :disabled="selectedFiles.length === 0"
                  @click="handleMoveSelected"
                >
                  <el-icon><FolderOpened /></el-icon>
                  移动
                </el-button>
                <el-button
                  size="small"
                  type="danger"
                  :disabled="selectedFiles.length === 0"
                  @click="handleDeleteSelected"
                >
                  <el-icon><Delete /></el-icon>
                  删除
                </el-button>
              </el-button-group>
              <span v-if="selectedFiles.length > 0" class="selection-info">
                已选择 {{ selectedFiles.length }} 项
              </span>
            </div>
            
            <div class="toolbar-right">
            <el-button
              size="small"
              type="primary"
              style="margin-right: 10px;"
              @click="openCreateFolderDialog"
            >
              <el-icon><Folder /></el-icon>
              新建文件夹
            </el-button>
              <el-input
                v-model="searchKeyword"
                placeholder="搜索文件..."
                size="small"
                clearable
                style="width: 200px; margin-right: 10px;"
              >
                <template #prefix>
                  <el-icon><Search /></el-icon>
                </template>
              </el-input>
              
              <el-select
                v-model="sortBy"
                size="small"
                style="width: 120px; margin-right: 10px;"
              >
                <el-option label="名称" value="name" />
                <el-option label="类型" value="type" />
                <el-option label="时间" value="time" />
              </el-select>
              
              <el-select
                v-model="filterType"
                size="small"
                clearable
                placeholder="文件类型"
                style="width: 150px;"
              >
                <el-option
                  v-for="ext in getAllFileExtensions"
                  :key="ext"
                  :label="ext.toUpperCase()"
                  :value="ext"
                />
              </el-select>
            </div>
          </div>
          
          <!-- 文件夹和文件列表 -->
          <div class="file-content" v-loading="loadingFiles">
            <!-- 文件夹视图 -->
            <div v-if="viewMode === 'folder'" class="folder-view">
              <!-- 文件夹列表 -->
              <div class="folders-grid">
                <div
                  v-for="folder in folders"
                  :key="folder.id"
                  class="folder-item"
                  @click="navigateToFolder(folder.id)"
                  :class="{ 'default-folder': isDefaultFolder(folder.name) }"
                >
                  <el-icon class="folder-icon"><Folder /></el-icon>
                  <div class="folder-name">{{ folder.name }}</div>
                  <div class="folder-count">{{ folder.attachment_count || 0 }} 个文件</div>
                  <el-icon v-if="isDefaultFolder(folder.name)" class="lock-icon">
                    <Lock />
                  </el-icon>
                </div>
              </div>
              
              <!-- 当前文件夹的文件列表 -->
              <div v-if="currentFolderId" class="files-in-folder">
                <div class="folder-files-header">
                  <h4>文件列表</h4>
                </div>
                <div class="files-grid">
                  <div
                    v-for="file in getCurrentFolderFiles"
                    :key="file.id"
                    class="file-item"
                    :class="{ selected: isFileSelected(file.id) }"
                    @click.stop="toggleFileSelection(file)"
                    @dblclick="handlePreviewAttachment(file)"
                    @contextmenu.prevent="handleRightClick($event, file)"
                  >
                    <el-checkbox
                      :model-value="isFileSelected(file.id)"
                      @click.stop
                      @change="toggleFileSelection(file)"
                      class="file-checkbox"
                    />
                    <el-icon class="file-icon">
                      <Document v-if="!isImageFile(file.file_name)" />
                      <Picture v-else />
                    </el-icon>
                    <div class="file-name">{{ file.file_name }}</div>
                    <div class="file-size">{{ formatFileSize(file) }}</div>
                  </div>
                </div>
              </div>
              
              <!-- 根目录文件列表（当前文件夹为null时显示） -->
              <div v-else class="files-in-folder">
                <div class="folder-files-header">
                  <h4>未分类文件</h4>
                </div>
                <div class="files-grid">
                  <div
                    v-for="file in getUncategorizedFiles"
                    :key="file.id"
                    class="file-item"
                    :class="{ selected: isFileSelected(file.id) }"
                    @click.stop="toggleFileSelection(file)"
                    @dblclick="handlePreviewAttachment(file)"
                    @contextmenu.prevent="handleRightClick($event, file)"
                  >
                    <el-checkbox
                      :model-value="isFileSelected(file.id)"
                      @click.stop
                      @change="toggleFileSelection(file)"
                      class="file-checkbox"
                    />
                    <el-icon class="file-icon">
                      <Document v-if="!isImageFile(file.file_name)" />
                      <Picture v-else />
                    </el-icon>
                    <div class="file-name">{{ file.file_name }}</div>
                    <div class="file-size">{{ formatFileSize(file) }}</div>
                  </div>
                </div>
              </div>
            </div>
            
            <!-- 列表视图 -->
            <div v-else class="list-view">
              <el-table
                :data="filteredFiles"
                style="width: 100%"
                @row-click="handleRowClick"
                @row-contextmenu="handleTableRightClick"
                @selection-change="handleSelectionChange"
              >
                <el-table-column type="selection" width="55" />
                <el-table-column prop="file_name" label="文件名" min-width="200">
                  <template #default="{ row }">
                    <div class="file-name-cell">
                      <el-icon class="file-icon-small">
                        <Document v-if="!isImageFile(row.file_name)" />
                        <Picture v-else />
                      </el-icon>
                      <span>{{ row.file_name }}</span>
                    </div>
                  </template>
                </el-table-column>
                <el-table-column prop="folder_name" label="文件夹" width="150" />
                <el-table-column prop="file_type" label="类型" width="100" />
                <el-table-column label="大小" width="100">
                  <template #default="{ row }">
                    {{ formatFileSize(row) }}
                  </template>
                </el-table-column>
                <el-table-column prop="created_at" label="创建时间" width="180">
                  <template #default="{ row }">
                    {{ formatDate(row.created_at) }}
                  </template>
                </el-table-column>
              </el-table>
            </div>
            
            <el-empty
              v-if="!loadingFiles && filteredFiles.length === 0"
              description="暂无文件"
              :image-size="100"
            />
          </div>
        </div>
      </el-col>
    </el-row>
    
    <!-- 文件预览对话框 -->
    <el-dialog
      v-model="showPreviewDialog"
      title="文件预览"
      width="80%"
      :close-on-click-modal="false"
    >
      <!-- 复用ProjectDetail中的预览逻辑 -->
      <div v-if="previewAttachment">
        <!-- 图片预览 -->
        <div v-if="isImageFile(previewAttachment.file_name)" class="preview-content">
          <el-image
            :src="getPreviewUrlSync(previewAttachment.id)"
            fit="contain"
            style="max-height: 70vh; width: 100%;"
            :preview-src-list="[getPreviewUrlSync(previewAttachment.id)]"
          />
        </div>
        
        <!-- PDF预览 -->
        <div v-else-if="isPdfFile(previewAttachment.file_name)" class="preview-content">
          <iframe
            :src="getPreviewUrlSync(previewAttachment.id)"
            style="width: 100%; height: 70vh; border: none;"
          />
        </div>
        
        <!-- 文本预览 -->
        <div v-else-if="isTextFile(previewAttachment.file_name)" class="preview-content">
          <pre class="text-preview">{{ textPreviewContent }}</pre>
        </div>
        
        <!-- Office文档预览 -->
        <div v-else-if="isOfficeFile(previewAttachment.file_name)" class="preview-content">
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
        <div v-else class="preview-content">
          <p style="text-align: center; padding: 60px 20px; color: #909399;">
            该文件类型不支持在线预览，请下载后查看
          </p>
        </div>
      </div>
    </el-dialog>
    
    <!-- 右键菜单 -->
    <div
      v-if="showContextMenu"
      class="context-menu"
      :style="{ left: contextMenuPosition.x + 'px', top: contextMenuPosition.y + 'px', zIndex: 9999 }"
      @click.stop
      @contextmenu.prevent.stop
    >
      <div class="context-menu-item" @click="handleContextMenuPreview">
        <el-icon><View /></el-icon>
        <span>预览</span>
      </div>
      <div class="context-menu-item" @click="handleContextMenuDownload">
        <el-icon><Download /></el-icon>
        <span>下载</span>
      </div>
      <div class="context-menu-divider"></div>
      <div class="context-menu-item" @click="handleContextMenuRename">
        <el-icon><Edit /></el-icon>
        <span>重命名</span>
      </div>
      <div class="context-menu-item" @click="handleContextMenuCopy">
        <el-icon><CopyDocument /></el-icon>
        <span>复制</span>
      </div>
      <div class="context-menu-item" @click="handleContextMenuMove">
        <el-icon><FolderOpened /></el-icon>
        <span>移动到</span>
      </div>
      <template v-if="selectedProjectId && isGraduationPluginEnabled">
        <div class="context-menu-divider"></div>
        <div class="context-menu-item" @click="showGraduationTagMenu = true">
          <el-icon><Document /></el-icon>
          <span>标记为毕设文件</span>
          <el-icon class="menu-arrow"><ArrowRight /></el-icon>
        </div>
        <div class="context-menu-divider"></div>
      </template>
      <div class="context-menu-item danger" @click="handleContextMenuDelete">
        <el-icon><Delete /></el-icon>
        <span>删除</span>
      </div>
    </div>

    <!-- 毕设标记子菜单 -->
    <div
      v-if="showGraduationTagMenu"
      class="context-submenu"
      :style="{ left: (contextMenuPosition.x + 180) + 'px', top: contextMenuPosition.y + 'px', zIndex: 10000 }"
      @click.stop
      @mouseleave="showGraduationTagMenu = false"
    >
      <div
        v-for="(config, type) in graduationFileTypes"
        :key="type"
        class="context-menu-item"
        @click="handleTagAsGraduationFile(type as GraduationFileType)"
      >
        <el-icon><component :is="getGraduationIcon(config.icon)" /></el-icon>
        <span>{{ config.label }}</span>
      </div>
      <div class="context-menu-divider"></div>
      <div class="context-menu-item" @click="handleUntagGraduationFile">
        <el-icon><Delete /></el-icon>
        <span>取消标记</span>
      </div>
    </div>
    
    <!-- 移动文件对话框 -->
    <el-dialog
      v-model="showMoveDialog"
      title="移动到文件夹"
      width="400px"
      @close="moveTargetFolderId = null"
    >
      <el-form>
        <el-form-item label="选择目标文件夹">
          <el-select v-model="moveTargetFolderId" clearable placeholder="选择目标文件夹" style="width: 100%">
            <el-option label="未分类" :value="null" />
            <el-option
              v-for="folder in folders"
              :key="folder.id"
              :label="folder.name"
              :value="folder.id"
            />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showMoveDialog = false">取消</el-button>
        <el-button type="primary" @click="confirmMove">确定</el-button>
      </template>
    </el-dialog>
    
    <!-- 新建文件夹对话框 -->
    <el-dialog
      v-model="showCreateFolderDialog"
      title="新建文件夹"
      width="400px"
    >
      <el-form @submit.prevent>
        <el-form-item label="文件夹名称">
          <el-input
            v-model="newFolderName"
            placeholder="请输入文件夹名称"
            maxlength="50"
            show-word-limit
            @keyup.enter="handleCreateFolder"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateFolderDialog = false">取消</el-button>
        <el-button type="primary" @click="handleCreateFolder">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Search,
  Folder,
  Document,
  Picture,
  View,
  Download,
  Lock,
  Edit,
  CopyDocument,
  DocumentCopy,
  FolderOpened,
  Delete,
  Sort,
  Timer,
  TrendCharts,
  ArrowRight,
  VideoPlay,
} from '@element-plus/icons-vue'
import { projectApi, type Project } from '@/api/project'
import { attachmentApi, type Attachment } from '@/api/attachment'
import { attachmentFolderApi, type AttachmentFolder } from '@/api/attachmentFolder'
import { useGraduationPlugin } from '@/composables/useGraduationPlugin'
import { usePluginSettings } from '@/composables/usePluginSettings'
import { graduationFileTypes, type GraduationFileType } from '@/types/plugin'
import mammoth from 'mammoth'
import * as XLSX from 'xlsx'

// 项目相关
const loadingProjects = ref(false)
const projects = ref<Project[]>([])
const selectedProjectId = ref<number | null>(null)
const projectSearchKeyword = ref('')
const projectSortBy = ref<'name' | 'time' | 'progress'>('time')

// 文件管理相关
const loadingFiles = ref(false)
const folders = ref<AttachmentFolder[]>([])
const files = ref<Attachment[]>([])
const currentFolderId = ref<number | null>(null)
const viewMode = ref<'folder' | 'list'>('folder')
const searchKeyword = ref('')
const sortBy = ref<'name' | 'type' | 'time'>('name')
const filterType = ref<string>('')

// 预览相关
const showPreviewDialog = ref(false)
const previewAttachment = ref<Attachment | null>(null)
const textPreviewContent = ref('')
const officePreviewContent = ref('')
const officePreviewType = ref<'word' | 'excel' | 'ppt' | null>(null)
const previewUrlCache = ref<Record<number, string>>({})

// 右键菜单相关
const showContextMenu = ref(false)
const contextMenuPosition = ref({ x: 0, y: 0 })
const contextMenuAttachment = ref<Attachment | null>(null)
const showGraduationTagMenu = ref(false)

// 毕设插件
const { tagAttachment, untagAttachment } = useGraduationPlugin()
const { isProjectEnabled } = usePluginSettings()
const isGraduationPluginEnabled = computed(() => {
  return selectedProjectId.value ? isProjectEnabled(selectedProjectId.value, 'graduation') : false
})

// 选择相关
const selectedFiles = ref<number[]>([])

// 剪贴板相关
const clipboardItems = ref<Array<{ type: 'file' | 'folder', id: number, data: Attachment | AttachmentFolder }>>([])

// 移动对话框
const showMoveDialog = ref(false)
const moveTargetFolderId = ref<number | null>(null)

// 新建文件夹对话框
const showCreateFolderDialog = ref(false)
const newFolderName = ref('')

// 计算属性
const currentProject = computed(() => {
  return projects.value.find(p => p.id === selectedProjectId.value) || null
})

const filteredAndSortedProjects = computed(() => {
  let result = [...projects.value]
  
  // 搜索筛选
  if (projectSearchKeyword.value) {
    const keyword = projectSearchKeyword.value.toLowerCase()
    result = result.filter(p => 
      p.title.toLowerCase().includes(keyword) ||
      p.student_name?.toLowerCase().includes(keyword)
    )
  }
  
  // 排序
  result.sort((a, b) => {
    switch (projectSortBy.value) {
      case 'name':
        return a.title.localeCompare(b.title)
      case 'time':
        return new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime()
      case 'progress':
        return getProjectProgress(b) - getProjectProgress(a)
      default:
        return 0
    }
  })
  
  return result
})

const folderPath = computed(() => {
  if (!currentFolderId.value) return []
  const path: AttachmentFolder[] = []
  let current = folders.value.find(f => f.id === currentFolderId.value)
  while (current) {
    path.unshift(current)
    // 这里假设文件夹没有父文件夹关系，如果需要可以扩展
    break
  }
  return path
})

const getAllFileExtensions = computed(() => {
  const extensions = new Set<string>()
  files.value.forEach(file => {
    const ext = getFileExtension(file.file_name)
    if (ext) {
      extensions.add(ext)
    }
  })
  return Array.from(extensions).sort()
})

const getCurrentFolderFiles = computed(() => {
  if (!currentFolderId.value) return []
  return applyFiltersAndSort(
    files.value.filter(f => f.folder_id === currentFolderId.value)
  )
})

const getUncategorizedFiles = computed(() => {
  return applyFiltersAndSort(
    files.value.filter(f => !f.folder_id)
  )
})

const filteredFiles = computed(() => {
  let result = currentFolderId.value
    ? files.value.filter(f => f.folder_id === currentFolderId.value)
    : files.value.filter(f => !f.folder_id)
  
  return applyFiltersAndSort(result)
})

// 方法
const loadProjects = async () => {
  loadingProjects.value = true
  try {
    projects.value = await projectApi.list({ limit: 1000 })
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '加载项目列表失败')
  } finally {
    loadingProjects.value = false
  }
}

const selectProject = async (projectId: number) => {
  selectedProjectId.value = projectId
  currentFolderId.value = null
  await loadFolders()
  await loadFiles()
}

const loadFolders = async () => {
  if (!selectedProjectId.value) return
  try {
    folders.value = await attachmentFolderApi.list(selectedProjectId.value)
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '加载文件夹失败')
  }
}

const loadFiles = async () => {
  if (!selectedProjectId.value) return
  loadingFiles.value = true
  try {
    files.value = await attachmentApi.list(selectedProjectId.value)
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '加载文件失败')
  } finally {
    loadingFiles.value = false
  }
}

const navigateToFolder = (folderId: number) => {
  currentFolderId.value = folderId
}

const openCreateFolderDialog = () => {
  if (!selectedProjectId.value) {
    ElMessage.warning('请先选择一个项目')
    return
  }
  newFolderName.value = ''
  showCreateFolderDialog.value = true
}

const handleCreateFolder = async () => {
  if (!selectedProjectId.value) {
    ElMessage.warning('请先选择一个项目')
    return
  }
  const name = newFolderName.value.trim()
  if (!name) {
    ElMessage.warning('文件夹名称不能为空')
    return
  }
  // 不允许使用默认文件夹名称
  if (isDefaultFolder(name)) {
    ElMessage.warning('该名称为系统默认文件夹名称，请使用其他名称')
    return
  }
  // 简单检查重名
  if (folders.value.some(f => f.name === name)) {
    ElMessage.warning('已存在同名文件夹')
    return
  }
  try {
    await attachmentFolderApi.create(selectedProjectId.value, {
      name,
      description: '',
    })
    await loadFolders()
    ElMessage.success('文件夹创建成功')
    showCreateFolderDialog.value = false
    newFolderName.value = ''
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '创建文件夹失败')
  }
}

const getFileExtension = (filename: string): string => {
  const parts = filename.split('.')
  return parts.length > 1 ? '.' + parts[parts.length - 1].toLowerCase() : ''
}

const applyFiltersAndSort = (fileList: Attachment[]): Attachment[] => {
  let result = [...fileList]
  
  // 搜索筛选
  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    result = result.filter(f => f.file_name.toLowerCase().includes(keyword))
  }
  
  // 文件扩展名筛选
  if (filterType.value) {
    result = result.filter(f => {
      const ext = getFileExtension(f.file_name)
      return ext === filterType.value
    })
  }
  
  // 排序
  result.sort((a, b) => {
    switch (sortBy.value) {
      case 'name':
        return a.file_name.localeCompare(b.file_name)
      case 'type':
        const extA = getFileExtension(a.file_name)
        const extB = getFileExtension(b.file_name)
        return extA.localeCompare(extB)
      case 'time':
        return new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
      default:
        return 0
    }
  })
  
  return result
}

const getProjectProgress = (project: Project): number => {
  if (!project.steps || project.steps.length === 0) return 0
  const completedSteps = project.steps.filter(s => s.status === '已完成').length
  return Math.round((completedSteps / project.steps.length) * 100)
}

const getStatusType = (status: string): string => {
  const statusMap: Record<string, string> = {
    '进行中': 'primary',
    '已完成': 'success',
    '已暂停': 'warning',
    '已取消': 'danger',
  }
  return statusMap[status] || 'info'
}

const formatDate = (dateString: string): string => {
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN')
}

const getProgressColor = (percentage: number): string => {
  if (percentage >= 80) return '#67c23a'
  if (percentage >= 50) return '#e6a23c'
  if (percentage >= 20) return '#409eff'
  return '#909399'
}

const formatFileSize = (file: Attachment): string => {
  // 这里需要从文件信息中获取大小，如果API没有返回，可以显示为未知
  return '未知'
}

const isDefaultFolder = (folderName: string): boolean => {
  return ['项目需求', '项目交付', '其他'].includes(folderName)
}

const isImageFile = (filename: string): boolean => {
  const ext = getFileExtension(filename)
  return ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp'].includes(ext.replace('.', ''))
}

const isPdfFile = (filename: string): boolean => {
  return filename.toLowerCase().endsWith('.pdf')
}

const isTextFile = (filename: string): boolean => {
  const ext = getFileExtension(filename)
  return ['txt', 'md', 'json', 'xml', 'csv', 'log'].includes(ext.replace('.', ''))
}

const isOfficeFile = (filename: string): boolean => {
  return isWordFile(filename) || isExcelFile(filename) || isPptFile(filename)
}

const isWordFile = (filename: string): boolean => {
  const ext = getFileExtension(filename)
  return ['doc', 'docx'].includes(ext.replace('.', ''))
}

const isExcelFile = (filename: string): boolean => {
  const ext = getFileExtension(filename)
  return ['xls', 'xlsx'].includes(ext.replace('.', ''))
}

const isPptFile = (filename: string): boolean => {
  const ext = getFileExtension(filename)
  return ['ppt', 'pptx'].includes(ext.replace('.', ''))
}

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

const handlePreviewAttachment = async (attachment: Attachment) => {
  if (!attachment) return
  
  previewAttachment.value = attachment
  textPreviewContent.value = ''
  officePreviewContent.value = ''
  officePreviewType.value = null
  showPreviewDialog.value = true
  
  // 预加载预览URL
  await getPreviewUrl(attachment.id)
  
  // 如果是文本文件，加载内容
  if (isTextFile(attachment.file_name)) {
    try {
      const blob = await attachmentApi.preview(attachment.id)
      const text = await blob.text()
      textPreviewContent.value = text
    } catch (error) {
      ElMessage.error('加载文件内容失败')
      textPreviewContent.value = '无法加载文件内容'
    }
  } else if (isWordFile(attachment.file_name)) {
    try {
      officePreviewType.value = 'word'
      const blob = await attachmentApi.preview(attachment.id)
      const arrayBuffer = await blob.arrayBuffer()
      const result = await mammoth.convertToHtml({ arrayBuffer })
      officePreviewContent.value = result.value
    } catch (error) {
      console.error('Word预览错误:', error)
      ElMessage.error('加载Word文档失败')
      officePreviewContent.value = '<p style="color: red; padding: 20px;">无法加载Word文档</p>'
    }
  } else if (isExcelFile(attachment.file_name)) {
    try {
      officePreviewType.value = 'excel'
      const blob = await attachmentApi.preview(attachment.id)
      const arrayBuffer = await blob.arrayBuffer()
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
  } else if (isPptFile(attachment.file_name)) {
    officePreviewType.value = 'ppt'
  }
}

const handleDownloadAttachment = async (attachment: Attachment) => {
  try {
    const blob = await attachmentApi.download(attachment.id)
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = attachment.file_name
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
    ElMessage.success('下载成功')
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '下载失败')
  }
}

const handleRightClick = (event: MouseEvent, attachment: Attachment) => {
  event.preventDefault()
  event.stopPropagation()
  
  // 确保右键菜单不会超出视口
  const menuWidth = 150
  const menuHeight = 300
  let x = event.clientX
  let y = event.clientY
  
  if (x + menuWidth > window.innerWidth) {
    x = window.innerWidth - menuWidth - 10
  }
  if (y + menuHeight > window.innerHeight) {
    y = window.innerHeight - menuHeight - 10
  }
  
  contextMenuPosition.value = { x, y }
  contextMenuAttachment.value = attachment
  showContextMenu.value = true
}

const handleTableRightClick = (row: Attachment, column: any, event: MouseEvent) => {
  handleRightClick(event, row)
}

const handleRowClick = (row: Attachment) => {
  handlePreviewAttachment(row)
}

const closeContextMenu = () => {
  showContextMenu.value = false
  showGraduationTagMenu.value = false
  contextMenuAttachment.value = null
}

// 毕设标记相关函数
const getGraduationIcon = (iconName: string) => {
  const iconMap: Record<string, any> = {
    Document: Document,
    VideoPlay: VideoPlay,
  }
  return iconMap[iconName] || Document
}

const handleTagAsGraduationFile = async (fileType: GraduationFileType) => {
  if (!contextMenuAttachment.value || !selectedProjectId.value) return
  
  // 检查项目是否启用插件
  if (!isProjectEnabled(selectedProjectId.value, 'graduation')) {
    ElMessage.warning('当前项目未启用毕设插件')
    showGraduationTagMenu.value = false
    closeContextMenu()
    return
  }
  
  await tagAttachment(contextMenuAttachment.value.id, fileType, selectedProjectId.value)
  showGraduationTagMenu.value = false
  closeContextMenu()
  await loadFiles()
}

const handleUntagGraduationFile = async () => {
  if (!contextMenuAttachment.value) return
  
  untagAttachment(contextMenuAttachment.value.id)
  ElMessage.success('已取消标记')
  showGraduationTagMenu.value = false
  closeContextMenu()
  await loadFiles()
}

const handleContextMenuPreview = () => {
  if (contextMenuAttachment.value) {
    handlePreviewAttachment(contextMenuAttachment.value)
    closeContextMenu()
  }
}

const handleContextMenuDownload = async () => {
  if (contextMenuAttachment.value) {
    await handleDownloadAttachment(contextMenuAttachment.value)
    closeContextMenu()
  }
}

// 选择功能
const isFileSelected = (fileId: number): boolean => {
  return selectedFiles.value.includes(fileId)
}

const toggleFileSelection = (file: Attachment) => {
  const index = selectedFiles.value.indexOf(file.id)
  if (index > -1) {
    selectedFiles.value.splice(index, 1)
  } else {
    selectedFiles.value.push(file.id)
  }
}

const handleSelectionChange = (selection: Attachment[]) => {
  selectedFiles.value = selection.map(f => f.id)
}

// 管理功能
const handleRenameSelected = async () => {
  if (selectedFiles.value.length === 0) return
  if (selectedFiles.value.length > 1) {
    ElMessage.warning('请选择一个文件进行重命名')
    return
  }
  
  const fileId = selectedFiles.value[0]
  const file = files.value.find(f => f.id === fileId)
  if (!file) return
  
  try {
    const { value: fileName } = await ElMessageBox.prompt(
      '请输入新文件名',
      '重命名文件',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        inputValue: file.file_name,
        inputValidator: (value) => {
          if (!value || !value.trim()) {
            return '文件名不能为空'
          }
          return true
        },
      }
    )
    
    if (fileName && fileName.trim() !== file.file_name) {
      await attachmentApi.update(file.id, {
        file_name: fileName.trim()
      })
      await loadFiles()
      await loadFolders()
      selectedFiles.value = []
      ElMessage.success('文件重命名成功')
    }
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.response?.data?.detail || '重命名文件失败')
    }
  }
}

const handleCopySelected = () => {
  if (selectedFiles.value.length === 0) return
  
  clipboardItems.value = selectedFiles.value.map(fileId => {
    const file = files.value.find(f => f.id === fileId)
    return file ? { type: 'file' as const, id: fileId, data: file } : null
  }).filter(item => item !== null) as Array<{ type: 'file', id: number, data: Attachment }>
  
  ElMessage.success(`已复制 ${clipboardItems.value.length} 个文件`)
}

const handlePaste = async () => {
  if (clipboardItems.value.length === 0) {
    ElMessage.warning('剪贴板为空')
    return
  }
  if (!selectedProjectId.value) {
    ElMessage.warning('请先选择一个项目')
    return
  }
  
  try {
    let successCount = 0
    let failCount = 0
    
    for (const item of clipboardItems.value) {
      if (item.type === 'file') {
        try {
          const sourceFile = item.data as Attachment
          
          // 如果复制的文件来自同一个项目，则在同一项目内复制到指定文件夹
          // 如果来自不同项目，则复制到当前项目
          if (sourceFile.project_id === selectedProjectId.value) {
            // 同一项目内复制，不指定target_project_id（传递undefined），后端会使用原项目ID
            await attachmentApi.copy(
              item.id, 
              undefined,  // 同一项目内复制，不指定目标项目
              currentFolderId.value || undefined
            )
          } else {
            // 跨项目复制，指定目标项目
            await attachmentApi.copy(
              item.id, 
              selectedProjectId.value,  // 跨项目复制，指定目标项目
              currentFolderId.value || undefined
            )
          }
          successCount++
        } catch (error: any) {
          console.error(`复制文件 ${item.id} 失败:`, error)
          ElMessage.error(`复制文件失败: ${error.response?.data?.detail || error.message}`)
          failCount++
        }
      }
    }
    
    if (successCount > 0) {
      await loadFiles()
      await loadFolders()
      if (failCount > 0) {
        ElMessage.warning(`成功粘贴 ${successCount} 个文件，${failCount} 个文件失败`)
      } else {
        ElMessage.success(`成功粘贴 ${successCount} 个文件`)
      }
      clipboardItems.value = [] // 粘贴后清空剪贴板
      selectedFiles.value = [] // 清空选择
    } else {
      ElMessage.error('粘贴失败，请检查文件权限')
    }
  } catch (error: any) {
    console.error('粘贴操作失败:', error)
    ElMessage.error(error.response?.data?.detail || '粘贴失败')
  }
}

const handleMoveSelected = () => {
  if (selectedFiles.value.length === 0) return
  showMoveDialog.value = true
}

const confirmMove = async () => {
  if (selectedFiles.value.length === 0) return
  
  try {
    for (const fileId of selectedFiles.value) {
      await attachmentApi.update(fileId, {
        folder_id: moveTargetFolderId.value || undefined
      })
    }
    
    await loadFiles()
    await loadFolders()
    selectedFiles.value = []
    showMoveDialog.value = false
    moveTargetFolderId.value = null
    ElMessage.success('文件移动成功')
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '移动文件失败')
  }
}

const handleDeleteSelected = async () => {
  if (selectedFiles.value.length === 0) return
  
  try {
    await ElMessageBox.confirm(
      `确定要删除选中的 ${selectedFiles.value.length} 个文件吗？`,
      '提示',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )
    
    for (const fileId of selectedFiles.value) {
      try {
        await attachmentApi.delete(fileId)
      } catch (error) {
        console.error(`删除文件 ${fileId} 失败:`, error)
      }
    }
    
    await loadFiles()
    await loadFolders()
    selectedFiles.value = []
    ElMessage.success('文件删除成功')
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.response?.data?.detail || '删除文件失败')
    }
  }
}

const handleDeleteAttachment = async (attachment: Attachment) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除附件"${attachment.file_name}"吗？`,
      '提示',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )
    
    await attachmentApi.delete(attachment.id)
    await loadFiles()
    await loadFolders()
    closeContextMenu()
    ElMessage.success('文件删除成功')
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.response?.data?.detail || '删除文件失败')
    }
    closeContextMenu()
  }
}

// 右键菜单操作
const handleContextMenuRename = async () => {
  if (contextMenuAttachment.value) {
    selectedFiles.value = [contextMenuAttachment.value.id]
    await handleRenameSelected()
    closeContextMenu()
  }
}

const handleContextMenuCopy = () => {
  if (contextMenuAttachment.value) {
    selectedFiles.value = [contextMenuAttachment.value.id]
    handleCopySelected()
    closeContextMenu()
  }
}

const handleContextMenuMove = () => {
  if (contextMenuAttachment.value) {
    selectedFiles.value = [contextMenuAttachment.value.id]
    handleMoveSelected()
    closeContextMenu()
  }
}

const handleContextMenuDelete = async () => {
  if (contextMenuAttachment.value) {
    await handleDeleteAttachment(contextMenuAttachment.value)
  }
}

const cleanupPreviewUrls = () => {
  Object.values(previewUrlCache.value).forEach(url => {
    if (url) {
      URL.revokeObjectURL(url)
    }
  })
  previewUrlCache.value = {}
}

// 点击外部关闭右键菜单
const handleClickOutside = (event: MouseEvent) => {
  if (showContextMenu.value) {
    const target = event.target as HTMLElement
    // 如果点击的不是右键菜单本身，则关闭菜单
    if (!target.closest('.context-menu')) {
      closeContextMenu()
    }
  }
}

// 快捷键支持
const handleKeyDown = (event: KeyboardEvent) => {
  // Ctrl+C 复制
  if (event.ctrlKey && event.key === 'c' && selectedFiles.value.length > 0) {
    event.preventDefault()
    handleCopySelected()
  }
  // Ctrl+V 粘贴
  if (event.ctrlKey && event.key === 'v' && clipboardItems.value.length > 0) {
    event.preventDefault()
    handlePaste()
  }
  // Delete 删除
  if (event.key === 'Delete' && selectedFiles.value.length > 0) {
    event.preventDefault()
    handleDeleteSelected()
  }
  // F2 重命名
  if (event.key === 'F2' && selectedFiles.value.length === 1) {
    event.preventDefault()
    handleRenameSelected()
  }
}

onMounted(async () => {
  await loadProjects()
  document.addEventListener('click', handleClickOutside)
  document.addEventListener('keydown', handleKeyDown)
})

onUnmounted(() => {
  cleanupPreviewUrls()
  document.removeEventListener('click', handleClickOutside)
  document.removeEventListener('keydown', handleKeyDown)
})
</script>

<style scoped>
.resource-manager {
  height: calc(100vh - 60px);
  overflow: hidden;
}

.manager-container {
  height: 100%;
  margin: 0 !important;
}

.project-sidebar {
  height: 100%;
  background: #fff;
  border-right: 1px solid #e4e7ed;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.sidebar-header {
  padding: 18px 16px;
  border-bottom: 1px solid #e4e7ed;
  background: linear-gradient(135deg, #f5f7fa 0%, #ffffff 100%);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.sidebar-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  display: flex;
  align-items: center;
  gap: 8px;
}

.sidebar-header h3::before {
  content: '';
  width: 3px;
  height: 16px;
  background: linear-gradient(135deg, #409eff 0%, #66b1ff 100%);
  border-radius: 2px;
}

.toolbar {
  padding: 14px 12px;
  border-bottom: 1px solid #e4e7ed;
  background: #fff;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.search-input {
  width: 100%;
}

.sort-tabs {
  display: flex;
  gap: 2px;
  background: #f5f7fa;
  border-radius: 6px;
  padding: 2px;
}

.sort-tab {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
  padding: 6px 10px;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  font-size: 12px;
  color: #606266;
  font-weight: 500;
  user-select: none;
}

.sort-tab:hover {
  color: #409eff;
  background: rgba(64, 158, 255, 0.08);
}

.sort-tab.active {
  background: #fff;
  color: #409eff;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  font-weight: 600;
}

.sort-tab .el-icon {
  transition: transform 0.2s;
}

.sort-tab.active .el-icon {
  color: #409eff;
  transform: scale(1.1);
}

.project-list {
  flex: 1;
  overflow-y: auto;
  padding: 12px;
  background: #fafafa;
}

.project-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 14px;
  margin-bottom: 10px;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  background: #fff;
  position: relative;
  overflow: hidden;
}

.project-item::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 3px;
  background: transparent;
  transition: background 0.25s;
}

.project-item:hover {
  border-color: #409eff;
  background: #f0f9ff;
  transform: translateX(2px);
  box-shadow: 0 2px 12px rgba(64, 158, 255, 0.12);
}

.project-item:hover::before {
  background: #409eff;
}

.project-item.active {
  border-color: #409eff;
  background: linear-gradient(135deg, #ecf5ff 0%, #f0f9ff 100%);
  box-shadow: 0 2px 12px rgba(64, 158, 255, 0.2);
}

.project-item.active::before {
  background: #409eff;
}

.project-icon {
  flex-shrink: 0;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
  border-radius: 8px;
  color: #409eff;
  transition: all 0.25s;
}

.project-item.active .project-icon {
  background: linear-gradient(135deg, #409eff 0%, #66b1ff 100%);
  color: #fff;
  transform: scale(1.05);
}

.project-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8px;
  min-width: 0;
}

.project-title-row {
  display: flex;
  align-items: center;
  gap: 8px;
  justify-content: space-between;
}

.project-title {
  font-size: 15px;
  font-weight: 600;
  color: #303133;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  flex: 1;
  min-width: 0;
}

.project-item.active .project-title {
  color: #409eff;
}

.status-tag {
  flex-shrink: 0;
  font-size: 11px;
  padding: 2px 8px;
  height: 20px;
  line-height: 16px;
}

.project-meta-row {
  display: flex;
  align-items: center;
  gap: 16px;
  font-size: 12px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 4px;
  color: #909399;
}

.meta-item .el-icon {
  color: #c0c4cc;
}

.meta-text {
  font-size: 12px;
  color: #909399;
}

.progress-bar-container {
  margin-top: 4px;
}

.progress-bar {
  height: 4px;
  border-radius: 2px;
  overflow: hidden;
}

.progress-bar :deep(.el-progress-bar__outer) {
  background-color: #e4e7ed;
  border-radius: 2px;
}

.progress-bar :deep(.el-progress-bar__inner) {
  border-radius: 2px;
  transition: width 0.3s ease;
}

.file-manager {
  height: 100%;
  background: #f5f7fa;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.empty-state {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.file-manager-content {
  height: 100%;
  display: flex;
  flex-direction: column;
  padding: 16px;
  overflow: hidden;
}

.file-manager-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding-bottom: 16px;
  border-bottom: 1px solid #e4e7ed;
}

.toolbar-left h3 {
  margin: 0 0 8px 0;
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.breadcrumb {
  font-size: 14px;
}

.breadcrumb span {
  cursor: pointer;
  color: #409eff;
}

.breadcrumb span:hover {
  text-decoration: underline;
}

.toolbar-right {
  display: flex;
  align-items: center;
}

.file-content {
  flex: 1;
  overflow-y: auto;
  background: #fff;
  border-radius: 4px;
  padding: 16px;
}

.folder-view {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.folders-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 16px;
}

.folder-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 20px;
  border: 2px solid #e4e7ed;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
  background: #fff;
  position: relative;
}

.folder-item:hover {
  border-color: #409eff;
  background: #f0f9ff;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.15);
}

.folder-item.default-folder {
  border-color: #67c23a;
  background: linear-gradient(135deg, #f0f9ff 0%, #e8f5e9 100%);
}

.folder-icon {
  font-size: 48px;
  color: #409eff;
  margin-bottom: 8px;
}

.folder-item.default-folder .folder-icon {
  color: #67c23a;
}

.folder-name {
  font-size: 14px;
  font-weight: 500;
  color: #303133;
  margin-bottom: 4px;
  text-align: center;
}

.folder-count {
  font-size: 12px;
  color: #909399;
}

.lock-icon {
  position: absolute;
  bottom: 8px;
  right: 8px;
  font-size: 16px;
  color: #67c23a;
  background: rgba(255, 255, 255, 0.9);
  border-radius: 50%;
  padding: 4px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.files-in-folder {
  margin-top: 20px;
}

.folder-files-header {
  margin-bottom: 12px;
}

.folder-files-header h4 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.files-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  gap: 12px;
}

.file-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 12px;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
  background: #fff;
  position: relative;
}

.file-item.selected {
  border-color: #409eff;
  background: #ecf5ff;
}

.file-checkbox {
  position: absolute;
  top: 8px;
  left: 8px;
  z-index: 10;
}

.file-item:hover {
  border-color: #409eff;
  background: #f0f9ff;
  transform: translateY(-2px);
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.15);
}

.file-item.selected {
  border-color: #409eff;
  background: #ecf5ff;
}

.file-checkbox {
  position: absolute;
  top: 8px;
  left: 8px;
  z-index: 10;
}

.file-icon {
  font-size: 36px;
  color: #409eff;
  margin-bottom: 8px;
}

.file-name {
  font-size: 12px;
  color: #303133;
  text-align: center;
  width: 100%;
  margin-bottom: 4px;
  word-break: break-all;
  white-space: normal;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.file-size {
  font-size: 11px;
  color: #909399;
}

.file-name-cell {
  display: flex;
  align-items: center;
  gap: 8px;
  white-space: normal;
  word-break: break-all;
}

.file-icon-small {
  font-size: 18px;
  color: #409eff;
}

.preview-content {
  max-height: 70vh;
  overflow: auto;
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
}

.office-content {
  padding: 20px;
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

.context-menu {
  position: fixed;
  background: #fff;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.15);
  z-index: 9999;
  min-width: 150px;
  padding: 4px 0;
}

.context-menu-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  cursor: pointer;
  transition: background-color 0.2s;
  font-size: 14px;
  color: #303133;
}

.context-menu-item:hover {
  background: #f5f7fa;
}

.context-menu-item.danger {
  color: #f56c6c;
}

.context-menu-item.danger:hover {
  background: #fef0f0;
}

.context-menu-divider {
  height: 1px;
  background: #e4e7ed;
  margin: 4px 0;
}

.context-menu-item .menu-arrow {
  margin-left: auto;
  margin-right: 0;
  font-size: 12px;
  color: #909399;
}

.context-submenu {
  position: fixed;
  background: #fff;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.15);
  z-index: 10000;
  min-width: 180px;
  padding: 4px 0;
}

.list-view {
  width: 100%;
}
</style>

