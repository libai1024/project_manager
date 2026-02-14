<template>
  <div class="project-detail" v-loading="loading">
    <!-- 项目基本信息 -->
    <ProjectInfoCard
      :project="project"
      :can-edit="canEdit"
      :can-settle="canSettle"
      :settling="settling"
      :is-mobile="isMobile"
      @go-back="goBack"
      @edit="showEditDialog = true"
      @settle="handleSettle"
    />

    <!-- 项目需求卡片 -->
    <ProjectRequirementsCard
      v-if="project?.requirements"
      :requirements="project.requirements"
    />

    <!-- 主要内容区域：步骤时间线和项目日志 -->
    <el-row :gutter="20" class="main-content-row">
    <!-- 项目步骤时间线 -->
      <el-col :xs="24" :lg="14">
        <ProjectStepsTimeline
          :steps="sortedSteps"
          :expanded-step-id="expandedStepId"
          :editing-step-id="editingStepId"
          :editing-step-name="editingStepName"
          :project-created-at="project?.created_at"
          :is-step-operable="isStepOperable"
          :check-previous-steps-completed="checkPreviousStepsCompleted"
          :get-step-hint="getStepOperationHint"
          @select-template="showTemplateSelectorDialog = true"
          @edit-timeline="showTemplateEditorDialog = true"
          @toggle-expand="toggleStepExpand"
          @edit-name="startEditStepName"
          @update-editing-name="editingStepName.value = $event"
          @save-name="saveStepName"
          @cancel-edit-name="cancelEditStepName"
          @cycle-status="cycleStepStatus"
          @update-status="updateStepStatusDirect"
          @update-deadline="updateStepDeadline"
          @toggle-todo="handleToggleTodo"
          @insert-before="insertStepBefore"
          @delete-step="handleDeleteStep"
        />
      </el-col>

      <!-- 项目日志卡片 -->
      <el-col :xs="24" :lg="10">
        <ProjectLogsTimeline
          :logs="projectLogs"
          :log-attachments="logAttachments"
          :loading="loadingLogs"
          :project-title="project?.title || ''"
          @add-snapshot="showSnapshotDialog = true"
          @refresh="loadProjectLogs"
          @delete-log="handleDeleteLogById"
          @export="handleExportLogs"
          @view-photo="openPhotoViewer"
          @download-file="downloadAttachmentById"
        />
      </el-col>
    </el-row>

    <!-- 元器件清单插件 -->
    <ProjectPartsPlugin
      v-if="project"
      :project="project"
      @refresh="refreshProject"
    />

    <!-- 毕设插件 -->
    <GraduationPlugin
      v-if="project && isGraduationPluginEnabled"
      :project-id="project.id"
      :attachments="attachments"
      :project-title="project.title"
      @refresh="loadAttachments"
    />

    <!-- GitHub插件 -->
    <GitHubPlugin
      v-if="project && isGithubPluginEnabled"
      :project="project"
      @refresh="refreshProject"
    />

    <!-- 视频回放插件 -->
    <VideoPlaybackPlugin
      v-if="project && isVideoPlaybackPluginEnabled"
      :project="project"
      @refresh="refreshProject"
    />

    <!-- Files & Repo 部分 -->
    <ProjectFilesManager
      :attachments="attachments"
      :folders="folders"
      :view-mode="viewMode"
      :search-keyword="searchKeyword"
      :sort-by="sortBy"
      :filter-type="filterType"
      :selected-folder-id="selectedFolderId"
      :file-extensions="getAllFileExtensions"
      @update:view-mode="viewMode = $event"
      @update:search-keyword="searchKeyword = $event"
      @update:sort-by="sortBy = $event"
      @update:filter-type="filterType = $event"
      @select-folder="selectedFolderId = $event"
      @delete-folder="handleDeleteFolder"
      @upload="showUploadDialog = true"
      @create-folder="showCreateFolderDialog = true"
      @preview="handlePreviewAttachment"
      @download="handleDownloadAttachment"
      @delete="handleDeleteAttachment"
      @right-click="handleRightClick"
    />

    <!-- 编辑项目对话框 -->
    <ProjectEditDialog
      v-model:visible="showEditDialog"
      :project="project"
      :platforms="platforms"
      :all-tags="allTags"
      :submitting="submitting"
      @submit="handleUpdateSubmit"
      @manage-tags="router.push('/tags')"
    />

    <!-- 添加步骤对话框（添加到末尾） -->
    <el-dialog
      v-model="showAddStepDialog"
      title="添加步骤"
      width="500px"
      @close="resetStepForm"
    >
      <el-form
        ref="stepFormRef"
        :model="stepForm"
        :rules="stepRules"
        label-width="100px"
      >
        <el-form-item label="步骤名称" prop="name">
          <el-input v-model="stepForm.name" placeholder="请输入步骤名称" />
        </el-form-item>
        <el-form-item label="截止时间">
          <el-date-picker
            v-model="stepForm.deadline"
            type="datetime"
            placeholder="选择截止时间"
            style="width: 100%"
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showAddStepDialog = false">取消</el-button>
        <el-button type="primary" @click="handleAddStep">确定</el-button>
      </template>
    </el-dialog>

    <!-- 插入步骤对话框（插入到指定位置） -->
    <el-dialog
      v-model="showInsertStepDialog"
      title="插入步骤"
      width="500px"
      @close="resetInsertStepForm"
    >
      <el-form
        ref="insertStepFormRef"
        :model="insertStepForm"
        :rules="stepRules"
        label-width="100px"
      >
        <el-form-item label="插入位置" prop="position">
          <el-select v-model="insertStepForm.position" placeholder="选择插入位置" style="width: 100%">
            <el-option
              v-for="(step, index) in sortedSteps"
              :key="step.id"
              :label="`在${step.name}之后`"
              :value="step.id"
            />
            <el-option label="在最后" :value="null" />
          </el-select>
        </el-form-item>
        <el-form-item label="步骤名称" prop="name">
          <el-input v-model="insertStepForm.name" placeholder="请输入步骤名称" />
        </el-form-item>
        <el-form-item label="截止时间">
          <el-date-picker
            v-model="insertStepForm.deadline"
            type="datetime"
            placeholder="选择截止时间"
            style="width: 100%"
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showInsertStepDialog = false">取消</el-button>
        <el-button type="primary" @click="handleInsertStep">确定</el-button>
      </template>
    </el-dialog>

    <!-- 上传文件对话框 -->
    <el-dialog
      v-model="showUploadDialog"
      title="上传文件"
      width="500px"
      @close="resetUploadForm"
    >
      <el-form
        ref="uploadFormRef"
        :model="uploadForm"
        :rules="uploadRules"
        label-width="100px"
      >
        <el-form-item label="选择文件" prop="file">
          <el-upload
            ref="uploadRef"
            :auto-upload="false"
            :limit="1"
            :on-change="handleFileChange"
            :on-remove="handleFileRemove"
            drag
            class="upload-dragger"
          >
            <el-icon class="el-icon--upload"><Upload /></el-icon>
            <div class="el-upload__text">
              将文件拖到此处，或<em>点击上传</em>
            </div>
            <template #tip>
              <div class="el-upload__tip">支持所有文件类型，单个文件不超过1GB</div>
            </template>
          </el-upload>
        </el-form-item>
        <el-form-item label="文件类型">
          <el-select v-model="uploadForm.file_type" style="width: 100%">
            <el-option label="需求" value="需求" />
            <el-option label="开题报告" value="开题报告" />
            <el-option label="初稿" value="初稿" />
            <el-option label="终稿" value="终稿" />
            <el-option label="其他" value="其他" />
          </el-select>
        </el-form-item>
        <el-form-item label="描述">
          <el-input
            v-model="uploadForm.description"
            type="textarea"
            :rows="3"
            placeholder="文件描述（可选）"
          />
        </el-form-item>
        <el-form-item label="文件夹">
          <el-select 
            v-model="uploadForm.folder_id" 
            clearable 
            placeholder="选择文件夹（可选）" 
            style="width: 100%;"
            @change="handleUploadFolderChange"
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
        </el-form-item>
        <el-form-item v-if="uploading">
          <el-progress :percentage="uploadProgress" :status="uploadProgress === 100 ? 'success' : undefined" />
          <div style="text-align: center; margin-top: 8px; color: #909399; font-size: 12px;">
            {{ uploadProgress }}% - 正在上传文件...
          </div>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showUploadDialog = false" :disabled="uploading">取消</el-button>
        <el-button type="primary" :loading="uploading" :disabled="uploading" @click="handleUpload">
          {{ uploading ? `上传中 ${uploadProgress}%` : '上传' }}
        </el-button>
      </template>
    </el-dialog>

    <!-- 创建文件夹对话框 -->
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

    <!-- 右键菜单 -->
    <div
      v-if="showContextMenu"
      class="context-menu"
      :style="{ left: contextMenuPosition.x + 'px', top: contextMenuPosition.y + 'px' }"
      @click.stop
      @mouseleave="closeContextMenu"
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
      <div class="context-menu-item" @click="handleRenameFile">
        <el-icon><Edit /></el-icon>
        <span>重命名</span>
      </div>
      <div class="context-menu-item" @click="handleMoveToFolder">
        <el-icon><Folder /></el-icon>
        <span>移入文件夹</span>
      </div>
      <div class="context-menu-item" @click="handleMoveToOtherFolder">
        <el-icon><FolderAdd /></el-icon>
        <span>移入其他文件夹</span>
      </div>
      <template v-if="isGraduationPluginEnabled">
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
      :style="getSubmenuStyle()"
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

    <!-- 移入文件夹对话框 -->
    <el-dialog
      v-model="showMoveToFolderDialog"
      title="移入文件夹"
      width="400px"
      @close="() => { moveToFolderId = null; moveToFolderAttachment = null }"
    >
      <el-form>
        <el-form-item label="选择文件夹">
          <el-select v-model="moveToFolderId" clearable placeholder="选择目标文件夹" style="width: 100%">
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
        <el-button @click="showMoveToFolderDialog = false">取消</el-button>
        <el-button type="primary" @click="confirmMoveToFolder">确定</el-button>
      </template>
    </el-dialog>

    <!-- 步骤更新对话框 -->
    <StepUpdateDialog
      v-model="showStepUpdateDialog"
      :step="currentStep"
      :new-status="stepNewStatus"
      :project-id="projectId"
      @confirm="handleStepUpdateConfirm"
    />

    <!-- 项目快照对话框 -->
    <ProjectSnapshotDialog
      v-model="showSnapshotDialog"
      :project-id="projectId"
      @confirm="handleSnapshotConfirm"
    />

    <!-- 照片查看器 -->
    <PhotoViewer
      v-if="showPhotoViewer"
      :images="photoViewerImages"
      :initial-index="photoViewerIndex"
      @close="showPhotoViewer = false"
    />

    <!-- 模板选择对话框 -->
    <el-dialog
      v-model="showTemplateSelectorDialog"
      title="选择步骤模板"
      width="600px"
      @close="selectedTemplateId = null"
    >
      <div class="template-selector">
        <el-alert
          type="info"
          :closable="false"
          show-icon
          style="margin-bottom: 20px;"
        >
          <template #title>
            <span>选择模板后，将替换当前项目的所有步骤。此操作不可撤销，请谨慎操作。</span>
          </template>
        </el-alert>
        
        <el-select
          v-model="selectedTemplateId"
          placeholder="请选择步骤模板"
          style="width: 100%"
          filterable
        >
          <el-option
            v-for="template in stepTemplates"
            :key="template.id"
            :label="template.name + (template.is_default ? '（默认）' : '')"
            :value="template.id"
          >
            <div class="template-option">
              <div class="template-option-name">
                <span>{{ template.name }}</span>
                <el-tag v-if="template.is_default" type="success" size="small" style="margin-left: 8px;">默认</el-tag>
  </div>
              <div class="template-option-desc" v-if="template.description">
                {{ template.description }}
              </div>
              <div class="template-option-steps">
                共 {{ template.steps.length }} 个步骤
              </div>
            </div>
          </el-option>
        </el-select>
        
        <div v-if="selectedTemplateId" class="template-preview">
          <div class="preview-title">模板预览：</div>
          <div class="preview-steps">
            <el-tag
              v-for="(step, index) in stepTemplates.find(t => t.id === selectedTemplateId)?.steps || []"
              :key="index"
              size="small"
              style="margin: 4px;"
            >
              {{ index + 1 }}. {{ step }}
            </el-tag>
          </div>
        </div>
      </div>
      
      <template #footer>
        <el-button @click="showTemplateSelectorDialog = false">取消</el-button>
        <el-button
          type="primary"
          @click="applyTemplateToProject"
          :disabled="!selectedTemplateId"
        >
          应用模板
        </el-button>
      </template>
    </el-dialog>

    <!-- 项目步骤模板编辑器对话框 -->
    <StepTemplateEditor
      v-model="showTemplateEditorDialog"
      :template="projectTemplate"
      :is-project-steps="true"
      @success="(data: any) => handleProjectTemplateUpdate(data)"
      @close="showTemplateEditorDialog = false"
    />

    <!-- 文件预览对话框 -->
    <el-dialog
      v-model="showPreviewDialog"
      :title="previewAttachment?.file_name || '文件预览'"
      width="90%"
      :close-on-click-modal="false"
      class="file-preview-dialog"
      destroy-on-close
    >
      <div v-if="previewAttachment" class="preview-container">
        <!-- 图片预览 -->
        <div v-if="isImageFile(previewAttachment.file_name)" class="preview-image">
          <img v-if="getPreviewUrlSync(previewAttachment.id)" :src="getPreviewUrlSync(previewAttachment.id)" :alt="previewAttachment.file_name" />
          <div v-else class="loading-text">加载中...</div>
  </div>
        
        <!-- PDF预览 -->
        <div v-else-if="isPdfFile(previewAttachment.file_name)" class="preview-pdf">
          <iframe v-if="getPreviewUrlSync(previewAttachment.id)" :src="getPreviewUrlSync(previewAttachment.id)" frameborder="0"></iframe>
          <div v-else class="loading-text">加载中...</div>
        </div>
        
        <!-- 文本文件预览 -->
        <div v-else-if="isTextFile(previewAttachment.file_name)" class="preview-text">
          <pre v-if="textPreviewContent" class="text-content">{{ textPreviewContent }}</pre>
          <div v-else class="loading-text">加载中...</div>
        </div>
        
        <!-- 视频预览 -->
        <div v-else-if="isVideoFile(previewAttachment.file_name)" class="preview-video">
          <video v-if="getPreviewUrlSync(previewAttachment.id)" :src="getPreviewUrlSync(previewAttachment.id)" controls style="width: 100%; max-height: 70vh;"></video>
          <div v-else class="loading-text">加载中...</div>
        </div>
        
        <!-- 音频预览 -->
        <div v-else-if="isAudioFile(previewAttachment.file_name)" class="preview-audio">
          <audio v-if="getPreviewUrlSync(previewAttachment.id)" :src="getPreviewUrlSync(previewAttachment.id)" controls style="width: 100%;"></audio>
          <div v-else class="loading-text">加载中...</div>
        </div>
        
        <!-- Office文档预览 -->
        <div v-else-if="isOfficeFile(previewAttachment.file_name)" class="preview-office">
          <div v-if="officePreviewContent" class="office-content" v-html="officePreviewContent"></div>
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
              <el-button type="primary" @click="handleDownloadAttachment(previewAttachment)">
                <el-icon><Download /></el-icon>
                下载文件
              </el-button>
            </el-empty>
          </div>
        </div>
      </div>
      
      <template #footer>
        <div class="preview-footer">
          <el-button @click="showPreviewDialog = false">关闭</el-button>
          <el-button type="primary" @click="handleDownloadAttachment(previewAttachment!)" v-if="previewAttachment">
            <el-icon><Download /></el-icon>
            下载
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import {
  Plus,
  Delete,
  Clock,
  Upload,
  Link,
  TopRight,
  Document,
  Rank,
  Star,
  StarFilled,
  Check,
  Loading,
  ArrowDown,
  ArrowUp,
  Warning,
  Refresh,
  User,
  Money,
  Edit,
  Setting,
  InfoFilled,
  Download,
  Camera,
  ZoomIn,
  View,
  FolderAdd,
  Folder,
  List,
  Search,
  ArrowLeft,
  Lock,
  Picture,
  Timer,
  PriceTag,
  ArrowRight,
} from '@element-plus/icons-vue'

// 图标组件映射
const iconComponents: Record<string, any> = {
  Plus,
  Delete,
  Clock,
  Upload,
  Link,
  TopRight,
  Document,
  Rank,
  Star,
  StarFilled,
  Check,
  Loading,
  ArrowDown,
  Warning,
  Refresh,
  User,
  Edit,
  InfoFilled,
  Document,
  Delete
}
import { useProject } from '@/composables/useProject'
import { useAttachment } from '@/composables/useAttachment'
import { projectApi, type Project, ProjectStep, ProjectUpdate, ProjectStepCreate, ProjectLog } from '@/api/project'
import { useUserStore } from '@/stores/user'
import { attachmentApi, type Attachment } from '@/api/attachment'
import { attachmentFolderApi, type AttachmentFolder } from '@/api/attachmentFolder'
// 元器件清单功能已移至 ProjectPartsPlugin 插件
// import { projectPartApi, type ProjectPart, ProjectPartCreate, ProjectPartUpdate } from '@/api/projectPart'
import StepUpdateDialog from '@/components/StepUpdateDialog.vue'
import ProjectSnapshotDialog from '@/components/ProjectSnapshotDialog.vue'
import PhotoViewer from '@/components/PhotoViewer.vue'
import StepTemplateEditor from '@/components/StepTemplateEditor.vue'
import { stepTemplateApi, type StepTemplate } from '@/api/stepTemplate'
import ProjectInfoCard from '@/components/project-detail/ProjectInfoCard.vue'
import ProjectRequirementsCard from '@/components/project-detail/ProjectRequirementsCard.vue'
import ProjectLogsTimeline from '@/components/project-detail/ProjectLogsTimeline.vue'
import ProjectEditDialog from '@/components/project-detail/ProjectEditDialog.vue'
import ProjectStepsTimeline from '@/components/project-detail/ProjectStepsTimeline.vue'
import ProjectFilesManager from '@/components/project-detail/ProjectFilesManager.vue'
import GraduationPlugin from '@/components/plugins/GraduationPlugin.vue'
import GitHubPlugin from '@/components/plugins/GitHubPlugin.vue'
import ProjectPartsPlugin from '@/components/plugins/ProjectPartsPlugin.vue'
import VideoPlaybackPlugin from '@/components/plugins/VideoPlaybackPlugin.vue'
import { useLogIconConfig } from '@/composables/useLogIconConfig'
import { useGraduationPlugin } from '@/composables/useGraduationPlugin'
import { usePluginSettings } from '@/composables/usePluginSettings'
import { graduationFileTypes, type GraduationFileType } from '@/types/plugin'
import { useFileUpload } from '@/composables/useFileUpload'
import { batchUploadFiles } from '@/utils/uploadHelper'
import mammoth from 'mammoth'
import * as XLSX from 'xlsx'
import MarkdownIt from 'markdown-it'
import FileTypeIcon from '@/components/FileTypeIcon.vue'
import TagSelector from '@/components/TagSelector.vue'
import { tagApi, type Tag } from '@/api/tag'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
// 安全地解析项目ID，如果无效则使用0（会在onMounted中检查并跳转）
const projectId = route.params.id ? parseInt(route.params.id as string) : 0

// Markdown 渲染器
const md = new MarkdownIt({
  breaks: true,
  linkify: true,
  html: true,
})

const submitting = ref(false)
const showEditDialog = ref(false)
// 使用通用的文件上传composable
const { uploading, uploadProgress, uploadFile } = useFileUpload()
const showAddStepDialog = ref(false)
const showInsertStepDialog = ref(false)
const showUploadDialog = ref(false)
const editingStepId = ref<number | null>(null)
const editingStepName = ref('')
const stepNameInputRef = ref<FormInstance>()
const expandedStepId = ref<number | null>(null)

// 项目标签
const selectedTagIds = ref<number[]>([])
const allTags = ref<Tag[]>([])

// 项目日志
const projectLogs = ref<ProjectLog[]>([])
const loadingLogs = ref(false)
const logAttachments = ref<Record<number, Attachment[]>>({}) // 存储日志的附件信息

// 元器件清单功能已移至 ProjectPartsPlugin 插件
// 以下代码保留用于兼容，但实际功能由插件管理
const parts = ref<any[]>([]) // 保留类型为 any 以避免类型错误
const partsTableRef = ref()
const partsDefaultExpand = ref(false)
const showPartsEditDialog = ref(false)
const editingPart = ref<any>(null)
const editingPartIndex = ref(-1)

// 步骤更新对话框
const showStepUpdateDialog = ref(false)
const currentStep = ref<ProjectStep | null>(null)
const stepNewStatus = ref('')

// 项目快照对话框
const showSnapshotDialog = ref(false)

// 模板编辑器对话框（用于编辑项目步骤）
const showTemplateEditorDialog = ref(false)
const showTemplateSelectorDialog = ref(false)
const stepTemplates = ref<StepTemplate[]>([])
const selectedTemplateId = ref<number | null>(null)

const projectTemplate = computed(() => {
  if (!project.value?.steps) return null
  const sortedSteps = [...project.value.steps].sort((a, b) => a.order_index - b.order_index)
  return {
    name: `${project.value.title} - 步骤模板`,
    description: `项目"${project.value.title}"的步骤时间线`,
    steps: sortedSteps.map(s => s.name),
    id: 0, // 临时ID，用于标识这是项目步骤
    is_default: false,
  }
})

// 加载模板列表
const loadStepTemplates = async () => {
  try {
    await stepTemplateApi.ensureDefault()
    stepTemplates.value = await stepTemplateApi.list()
  } catch (error) {
    console.error('加载模板列表失败:', error)
  }
}

// 应用模板到项目
const applyTemplateToProject = async () => {
  if (!selectedTemplateId.value || !project.value) return
  
  try {
    const template = stepTemplates.value.find(t => t.id === selectedTemplateId.value)
    if (!template) {
      ElMessage.error('模板不存在')
      return
    }
    
    // 获取当前步骤（保存副本，因为删除后sortedSteps会变化）
    const currentSteps = [...sortedSteps.value]
    
    // 先创建新步骤（使用模板的步骤），使用较大的order_index避免冲突
    const maxOrderIndex = currentSteps.length > 0 
      ? Math.max(...currentSteps.map(s => s.order_index)) 
      : -1
    
    for (let index = 0; index < template.steps.length; index++) {
      const stepName = template.steps[index]
      if (stepName.trim()) {
        await createStep(projectId, {
          name: stepName.trim(),
          order_index: maxOrderIndex + index + 1, // 使用较大的order_index
        })
      }
    }
    
    // 等待新步骤创建完成
    await refreshProject()
    
    // 现在删除所有旧步骤（此时新步骤已经存在，所以可以删除"已结账"）
    // 从后往前删除，避免删除最后一个"已结账"时的错误
    for (let i = currentSteps.length - 1; i >= 0; i--) {
      const step = currentSteps[i]
      try {
        await deleteStep(step.id)
      } catch (error: any) {
        // 如果删除失败，继续删除其他步骤
        console.warn(`删除步骤 ${step.id} 失败:`, error)
      }
    }
    
    // 刷新项目以获取最新步骤
    await refreshProject()
    
    // 重新排序步骤，确保order_index正确
    const updatedSteps = sortedSteps.value
    for (let index = 0; index < updatedSteps.length; index++) {
      const step = updatedSteps[index]
      if (step.order_index !== index) {
        await updateStep(step.id, { order_index: index })
      }
    }
    
    // 最后刷新项目
    await refreshProject()
    ElMessage.success(`已应用模板"${template.name}"`)
    showTemplateSelectorDialog.value = false
    selectedTemplateId.value = null
  } catch (error) {
    ElMessage.error('应用模板失败')
    console.error('Failed to apply template:', error)
  }
}

// 处理项目模板更新
const handleProjectTemplateUpdate = async (templateData: { steps: string[] }) => {
  if (!project.value) return
  
  try {
    // 获取当前步骤（保存副本）
    const currentSteps = [...sortedSteps.value]
    
    // 先创建新步骤，使用较大的order_index避免冲突
    const maxOrderIndex = currentSteps.length > 0 
      ? Math.max(...currentSteps.map(s => s.order_index)) 
      : -1
    
    for (let index = 0; index < templateData.steps.length; index++) {
      const stepName = templateData.steps[index]
      if (stepName.trim()) {
        await createStep(projectId, {
          name: stepName.trim(),
          order_index: maxOrderIndex + index + 1,
        })
      }
    }
    
    // 等待新步骤创建完成
    await refreshProject()
    
    // 现在删除所有旧步骤（从后往前删除）
    for (let i = currentSteps.length - 1; i >= 0; i--) {
      const step = currentSteps[i]
      try {
        await deleteStep(step.id)
      } catch (error: any) {
        console.warn(`删除步骤 ${step.id} 失败:`, error)
      }
    }
    
    // 刷新项目
    await refreshProject()
    
    // 重新排序步骤
    const updatedSteps = sortedSteps.value
    for (let index = 0; index < updatedSteps.length; index++) {
      const step = updatedSteps[index]
      if (step.order_index !== index) {
        await updateStep(step.id, { order_index: index })
      }
    }
    
    // 最后刷新项目
    await refreshProject()
    ElMessage.success('步骤时间线更新成功')
    showTemplateEditorDialog.value = false
  } catch (error) {
    ElMessage.error('更新步骤时间线失败')
    console.error('Failed to update project steps:', error)
  }
}

// 照片查看器
const showPhotoViewer = ref(false)
const photoViewerImages = ref<string[]>([])
const photoViewerIndex = ref(0)

// 文件预览
const showPreviewDialog = ref(false)
const previewAttachment = ref<Attachment | null>(null)
const textPreviewContent = ref<string>('')
const officePreviewContent = ref<string>('') // Office文档预览内容（HTML）
const officePreviewType = ref<'word' | 'excel' | 'ppt' | null>(null) // Office文档类型

// 结账相关
const settling = ref(false)

// 使用Composables
const {
  loading,
  currentProject,
  platforms,
  loadPlatforms,
  loadProject,
  updateProject,
  createStep,
  updateStep,
  deleteStep,
  toggleStepTodo,
  reorderSteps,
} = useProject()

const project = computed(() => currentProject.value)

// 项目需求展开/收起
const requirementsExpanded = ref(false)
const requirementsContentRef = ref<HTMLElement | null>(null)
const shouldShowExpandButton = ref(false)

// 检查是否需要显示展开按钮
const checkRequirementsHeight = () => {
  nextTick(() => {
    if (requirementsContentRef.value && project.value?.requirements) {
      shouldShowExpandButton.value = requirementsContentRef.value.scrollHeight > 300
    } else {
      shouldShowExpandButton.value = false
    }
  })
}

// 监听项目变化，检查高度
watch(() => project.value?.requirements, () => {
  checkRequirementsHeight()
}, { immediate: true })

// 监听模板选择对话框打开，加载模板列表
watch(() => showTemplateSelectorDialog.value, (visible) => {
  if (visible) {
    loadStepTemplates()
  }
})

const {
  loading: attachmentLoading,
  attachments,
  loadAttachments,
  uploadAttachment,
  downloadAttachment,
  deleteAttachment,
} = useAttachment(projectId)

// 文件夹相关
const folders = ref<AttachmentFolder[]>([])
const loadingFolders = ref(false)
const loadFolders = async () => {
  loadingFolders.value = true
  try {
    folders.value = await attachmentFolderApi.list(projectId)
  } catch (error) {
    console.error('加载文件夹失败:', error)
  } finally {
    loadingFolders.value = false
  }
}

// 文件管理器相关
const viewMode = ref<'folder' | 'list'>('folder')
const selectedFolderId = ref<number | null>(null)
const searchKeyword = ref('')
const sortBy = ref<'name' | 'type' | 'time'>('name')
const filterType = ref<string>('')
const showCreateFolderDialog = ref(false)
const newFolderName = ref('')

// 获取文件扩展名
const getFileExtension = (filename: string): string => {
  const parts = filename.split('.')
  return parts.length > 1 ? '.' + parts[parts.length - 1].toLowerCase() : ''
}

// 获取所有文件扩展名（用于筛选选项）
const getAllFileExtensions = computed(() => {
  if (!attachments.value || !Array.isArray(attachments.value)) return []
  const extensions = new Set<string>()
  attachments.value.forEach(att => {
    const ext = getFileExtension(att.file_name)
    if (ext) {
      extensions.add(ext)
    }
  })
  return Array.from(extensions).sort()
})

// 创建文件夹
const handleCreateFolder = async () => {
  if (!newFolderName.value.trim()) {
    ElMessage.warning('请输入文件夹名称')
    return
  }
  
  // 检查是否为默认文件夹名称
  if (isDefaultFolder(newFolderName.value.trim())) {
    ElMessage.warning('不能使用默认文件夹名称')
    return
  }
  
  try {
    const newFolder = await attachmentFolderApi.create(projectId, { name: newFolderName.value.trim() })
    await loadFolders()
    showCreateFolderDialog.value = false
    // 自动选择新创建的文件夹
    uploadForm.folder_id = newFolder.id
    newFolderName.value = ''
    ElMessage.success('文件夹创建成功')
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '创建文件夹失败')
  }
}

// 处理上传文件夹选择变化
const handleUploadFolderChange = (value: number | string | null) => {
  if (value === '__create__') {
    uploadForm.folder_id = null
    showCreateFolderDialog.value = true
  } else {
    // 确保只接受数字类型
    uploadForm.folder_id = typeof value === 'number' ? value : null
  }
}

// 删除文件夹
const handleDeleteFolder = async (folder: AttachmentFolder) => {
  // 检查是否为默认文件夹
  if (isDefaultFolder(folder.name) || folder.is_default) {
    ElMessage.warning('默认文件夹不能删除')
    return
  }
  
  try {
    await ElMessageBox.confirm(
      `确定要删除文件夹"${folder.name}"吗？文件夹内的文件将移入"其他"文件夹。`,
      '提示',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )
    
    // 找到"其他"文件夹
    const otherFolder = folders.value.find(f => f.name === '其他')
    if (otherFolder) {
      // 将该文件夹内的所有文件移入"其他"文件夹
      const folderFiles = attachments.value.filter(a => a.folder_id === folder.id)
      for (const file of folderFiles) {
        try {
          await attachmentApi.update(file.id, { folder_id: otherFolder.id })
        } catch (error) {
          console.error(`移动文件 ${file.file_name} 失败:`, error)
        }
      }
    }
    
    await attachmentFolderApi.delete(folder.id)
    await loadFolders()
    await loadAttachments()
    
    // 如果删除的是当前选中的文件夹，清空选中
    if (selectedFolderId.value === folder.id) {
      selectedFolderId.value = null
    }
    
    ElMessage.success('文件夹删除成功')
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.response?.data?.detail || '删除文件夹失败')
    }
  }
}

const stepFormRef = ref<FormInstance>()
const insertStepFormRef = ref<FormInstance>()
const uploadFormRef = ref<FormInstance>()
const uploadRef = ref()

const stepForm = reactive<ProjectStepCreate>({
  name: '',
  deadline: undefined,
})

const insertStepForm = reactive<{
  position: number | null
  name: string
  deadline?: string
}>({
  position: null,
  name: '',
  deadline: undefined,
})

const uploadForm = reactive<{
  file: File | null
  file_type: string
  description: string
  folder_id: number | undefined
}>({
  file: null,
  file_type: '其他',
  description: '',
  folder_id: undefined,
})



const stepRules: FormRules = {
  name: [{ required: true, message: '请输入步骤名称', trigger: 'blur' }],
}

const uploadRules: FormRules = {
  file: [{ required: true, message: '请选择文件', trigger: 'change' }],
}


const sortedSteps = computed(() => {
  if (!project.value?.steps) return []
  return [...project.value.steps].sort((a, b) => a.order_index - b.order_index)
})

// 检查是否可以编辑项目（只有项目所有者或管理员可以编辑）
const canEdit = computed(() => {
  if (!project.value) return false
  const isAdmin = userStore.isAdmin
  const isOwner = project.value.user_id === userStore.userInfo?.id
  return isAdmin || isOwner
})

// 检查是否可以结账（最后一个步骤已完成且项目未结账，且用户有权限）
const canSettle = computed(() => {
  if (!project.value || project.value.is_paid) return false
  if (!sortedSteps.value.length) return false
  
  // 权限检查：只有项目所有者或管理员可以结账
  const isAdmin = userStore.isAdmin
  const isOwner = project.value.user_id === userStore.userInfo?.id
  if (!isAdmin && !isOwner) return false
  
  const lastStep = sortedSteps.value[sortedSteps.value.length - 1]
  return lastStep.status === '已完成'
})

// 检查前置步骤是否完成
const checkPreviousStepsCompleted = (step: ProjectStep): boolean => {
  const currentIndex = sortedSteps.value.findIndex(s => s.id === step.id)
  if (currentIndex <= 0) return true // 第一步或未找到，允许操作
  
  // 检查所有前置步骤是否都已完成
  for (let i = 0; i < currentIndex; i++) {
    if (sortedSteps.value[i].status !== '已完成') {
      return false
    }
  }
  return true
}

// 检查步骤是否可操作
const isStepOperable = (step: ProjectStep): boolean => {
  // 如果步骤已完成，可以操作（允许修改）
  if (step.status === '已完成') return true
  // 检查前置步骤是否完成
  return checkPreviousStepsCompleted(step)
}

// 获取步骤操作提示信息
const getStepOperationHint = (step: ProjectStep): string | null => {
  if (isStepOperable(step)) return null
  
  const currentIndex = sortedSteps.value.findIndex(s => s.id === step.id)
  if (currentIndex > 0) {
    const incompleteStep = sortedSteps.value.find((s, idx) => idx < currentIndex && s.status !== '已完成')
    if (incompleteStep) {
      return `请先完成前置步骤"${incompleteStep.name}"`
    }
  }
  return '请先完成前置步骤'
}

const isMobile = computed(() => {
  return window.innerWidth < 768
})

// 获取当前激活的步骤索引（最后一个未完成的步骤）
const getActiveStepIndex = () => {
  if (!sortedSteps.value.length) return -1
  for (let i = sortedSteps.value.length - 1; i >= 0; i--) {
    if (sortedSteps.value[i].status !== '已完成') {
      return i
    }
  }
  return sortedSteps.value.length - 1
}

// 获取步骤在时间线中的状态
const getStepStatusForTimeline = (step: ProjectStep) => {
  if (step.status === '已完成') return 'success'
  if (step.status === '进行中') return 'process'
  return 'wait'
}

// 格式化日期时间
const formatDateTime = (dateString: string): string => {
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

// 计算项目开始时长
const getProjectDuration = (createdAt: string): string => {
  const startDate = new Date(createdAt)
  const now = new Date()
  const diffMs = now.getTime() - startDate.getTime()
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24))
  const diffMonths = Math.floor(diffDays / 30)
  const diffYears = Math.floor(diffDays / 365)
  
  if (diffYears > 0) {
    return `${diffYears}年${Math.floor((diffDays % 365) / 30)}个月`
  } else if (diffMonths > 0) {
    return `${diffMonths}个月${diffDays % 30}天`
  } else if (diffDays > 0) {
    return `${diffDays}天`
  } else {
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60))
    if (diffHours > 0) {
      return `${diffHours}小时`
    } else {
      const diffMinutes = Math.floor(diffMs / (1000 * 60))
      return diffMinutes > 0 ? `${diffMinutes}分钟` : '刚刚开始'
    }
  }
}

// 加载数据函数已由Composables提供
const refreshProject = async () => {
  // 检查 projectId 是否有效
  if (!projectId || isNaN(projectId)) {
    console.error('Invalid project ID:', projectId)
    return
  }
  
  try {
    await loadProject(projectId)
    // 编辑表单数据由 ProjectEditDialog 组件内部管理，不需要在这里更新
  } catch (error) {
    console.error('Failed to refresh project:', error)
    // 不抛出错误，避免触发 router.back()
  }
}


const resetStepForm = () => {
  stepFormRef.value?.resetFields()
  Object.assign(stepForm, {
    name: '',
    deadline: undefined,
  })
}

const resetInsertStepForm = () => {
  insertStepFormRef.value?.resetFields()
  Object.assign(insertStepForm, {
    position: null,
    name: '',
    deadline: undefined,
  })
}

const resetUploadForm = () => {
  uploadFormRef.value?.resetFields()
  uploadRef.value?.clearFiles()
  Object.assign(uploadForm, {
    file: null,
    file_type: '其他',
    description: '',
    folder_id: undefined,
  })
}

// 处理编辑对话框提交
const handleUpdateSubmit = async (updateData: ProjectUpdate & { tag_ids?: number[] }) => {
  submitting.value = true
  try {
    const updatedProject = await updateProject(projectId, updateData)
    
    if (updatedProject) {
      await refreshProject()
    }
    showEditDialog.value = false
    await loadProjectLogs()
  } catch (error) {
    // 错误已在Service层处理
  } finally {
    submitting.value = false
  }
}

const handleAddStep = async () => {
  if (!stepFormRef.value) return
  
  await stepFormRef.value.validate(async (valid) => {
    if (valid) {
      try {
        const maxOrder = sortedSteps.value.length > 0
          ? Math.max(...sortedSteps.value.map(s => s.order_index))
          : -1
        
        await createStep(projectId, {
          ...stepForm,
          order_index: maxOrder + 1,
        })
        showAddStepDialog.value = false
        await refreshProject()
        await loadProjectLogs()
      } catch (error) {
        // 错误已在Service层处理
      }
    }
  })
}

const handleInsertStep = async () => {
  if (!insertStepFormRef.value) return
  
  await insertStepFormRef.value.validate(async (valid) => {
    if (valid) {
      try {
        let targetOrderIndex = sortedSteps.value.length
        
        if (insertStepForm.position !== null) {
          const targetStep = sortedSteps.value.find(s => s.id === insertStepForm.position)
          if (targetStep) {
            targetOrderIndex = targetStep.order_index + 1
            // 更新后续步骤的order_index
            const stepOrders = sortedSteps.value
              .filter(s => s.order_index >= targetOrderIndex)
              .map(s => ({
                step_id: s.id,
                order_index: s.order_index + 1
              }))
            
            if (stepOrders.length > 0) {
              await reorderSteps(stepOrders)
            }
          }
        }
        
        await createStep(projectId, {
          name: insertStepForm.name,
          order_index: targetOrderIndex,
          deadline: insertStepForm.deadline,
        })
        showInsertStepDialog.value = false
        await refreshProject()
        await loadProjectLogs()
      } catch (error) {
        // 错误已在Service层处理
      }
    }
  })
}

const insertStepBefore = async (step: ProjectStep) => {
  insertStepForm.position = step.id
  showInsertStepDialog.value = true
}

const updateStepStatus = async (step: ProjectStep) => {
  // 检查前置步骤是否完成（允许从已完成状态修改，但不允许跳过前置步骤）
  if (step.status !== '已完成' && !checkPreviousStepsCompleted(step)) {
    const hint = getStepOperationHint(step)
    ElMessage.warning(hint || '请先完成前置步骤')
    // 恢复原状态
    await refreshProject()
    return
  }
  
  try {
    await updateStep(step.id, { status: step.status })
    await refreshProject()
  } catch (error) {
    // 错误已在Service层处理
  }
}

const updateStepStatusDirect = async (step: ProjectStep, status: string) => {
  // 如果要设置为"进行中"或"已完成"，检查前置步骤
  if (status !== '待开始' && !checkPreviousStepsCompleted(step)) {
    const hint = getStepOperationHint(step)
    ElMessage.warning(hint || '请先完成前置步骤')
    return
  }
  
  // 如果状态发生变化，弹出更新对话框
  if (step.status !== status) {
    currentStep.value = step
    stepNewStatus.value = status
    showStepUpdateDialog.value = true
  } else {
  await updateStepStatus(step)
  }
}

const cycleStepStatus = async (step: ProjectStep) => {
  const statuses = ['待开始', '进行中', '已完成']
  const currentIndex = statuses.indexOf(step.status)
  const nextIndex = (currentIndex + 1) % statuses.length
  const nextStatus = statuses[nextIndex]
  
  // 如果要切换到"进行中"或"已完成"，检查前置步骤
  if (nextStatus !== '待开始' && !checkPreviousStepsCompleted(step)) {
    const hint = getStepOperationHint(step)
    ElMessage.warning(hint || '请先完成前置步骤')
    return
  }
  
  // 如果状态发生变化，弹出更新对话框
  if (step.status !== nextStatus) {
    currentStep.value = step
    stepNewStatus.value = nextStatus
    showStepUpdateDialog.value = true
  } else {
  await updateStepStatus(step)
  }
}

// 处理步骤更新确认
const handleStepUpdateConfirm = async (data: { note: string; files: File[]; photos: File[]; fileFolderId?: number; photoFolderId?: number }) => {
  if (!currentStep.value) return
  
  try {
    const oldStatus = currentStep.value.status
    
    // 更新步骤状态
    await updateStep(currentStep.value.id, { status: stepNewStatus.value })
    
    // 上传文件
    const attachmentIds: number[] = []
    if (data.files && data.files.length > 0) {
      const fileIds = await batchUploadFiles(projectId, data.files, {
        fileType: '其他',
        description: data.note || undefined,
        folderId: data.fileFolderId
      })
      attachmentIds.push(...fileIds)
    }
    
    // 上传照片（默认上传到快照文件夹）
    if (data.photos && data.photos.length > 0) {
      // 如果没有指定文件夹，尝试获取快照文件夹
      let photoFolderId = data.photoFolderId
      if (!photoFolderId) {
        const snapshotFolder = folders.value.find(f => f.name === '快照')
        if (snapshotFolder) {
          photoFolderId = snapshotFolder.id
        }
      }
      
      const photoIds = await batchUploadFiles(projectId, data.photos, {
        fileType: '其他',
        description: data.note || undefined,
        folderId: photoFolderId
      })
      attachmentIds.push(...photoIds)
    }
    
    // 记录项目日志
    try {
      await projectApi.logStepUpdate({
        project_id: projectId,
        step_id: currentStep.value.id,
        old_status: oldStatus,
        new_status: stepNewStatus.value,
        update_note: data.note || undefined,
        attachment_ids: attachmentIds.length > 0 ? attachmentIds : undefined
      })
    } catch (error) {
      console.error('记录日志失败:', error)
    }
    
    await refreshProject()
    await loadAttachments()
    await loadProjectLogs()
    
    showStepUpdateDialog.value = false
    currentStep.value = null
    ElMessage.success('步骤更新成功')
  } catch (error) {
    ElMessage.error('更新步骤失败')
  }
}

// 处理项目快照确认
const handleSnapshotConfirm = async (data: { note: string; photos: File[]; files: File[]; fileFolderId?: number; photoFolderId?: number }) => {
  try {
    // 如果没有指定快照文件夹，尝试获取快照文件夹
    let photoFolderId = data.photoFolderId
    if (!photoFolderId) {
      const snapshotFolder = folders.value.find(f => f.name === '快照')
      if (snapshotFolder) {
        photoFolderId = snapshotFolder.id
      }
    }
    
    // 上传照片（默认上传到快照文件夹）
    const photoUrls: string[] = []
    const photoAttachmentIds = await batchUploadFiles(projectId, data.photos, {
      fileType: '项目快照',
      description: data.note || undefined,
      folderId: photoFolderId
    })
    photoAttachmentIds.forEach(id => photoUrls.push(`${id}`))
    
    // 上传文件
    const fileAttachmentIds = await batchUploadFiles(projectId, data.files, {
      fileType: '项目快照',
      description: data.note || undefined,
      folderId: data.fileFolderId
    })
    
    // 合并所有附件ID（照片和文件）
    const allAttachmentIds = [...photoAttachmentIds, ...fileAttachmentIds]
    
    // 记录项目日志
    try {
      await projectApi.createSnapshot({
        project_id: projectId,
        snapshot_note: data.note || undefined,
        photo_urls: photoUrls,
        attachment_ids: allAttachmentIds.length > 0 ? allAttachmentIds : undefined
      })
    } catch (error) {
      console.error('记录日志失败:', error)
    }
    
    await refreshProject()
    await loadAttachments()
    await loadProjectLogs()
    
    showSnapshotDialog.value = false
    ElMessage.success('项目快照保存成功')
  } catch (error) {
    ElMessage.error('保存项目快照失败')
  }
}

const toggleStepExpand = (stepId: number) => {
  expandedStepId.value = expandedStepId.value === stepId ? null : stepId
}

// 处理结账
const handleSettle = async () => {
  if (!project.value) return
  
  try {
    await ElMessageBox.confirm(
      `确定要结账项目"${project.value.title}"吗？\n结账后项目状态将变为"已结账"，实际收入将同步更新。`,
      '确认结账',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )
    
    settling.value = true
    try {
      await projectApi.settleProject(projectId)
      ElMessage.success('项目结账成功')
      await refreshProject()
      await loadProjectLogs()
    } catch (error: any) {
      ElMessage.error(error.response?.data?.detail || '结账失败')
    } finally {
      settling.value = false
    }
  } catch (error: any) {
    if (error !== 'cancel') {
      // 用户取消操作，不需要处理
    }
  }
}

const updateStepDeadline = async (step: ProjectStep, deadline: string | null) => {
  try {
    await updateStep(step.id, { deadline: deadline || undefined })
    await refreshProject()
  } catch (error) {
    // 错误已在Service层处理
  }
}

const startEditStepName = (step: ProjectStep) => {
  editingStepId.value = step.id
  editingStepName.value = step.name
  nextTick(() => {
    if (stepNameInputRef.value) {
      const input = (stepNameInputRef.value as any).$el?.querySelector('input')
      if (input) {
        input.focus()
        input.select()
      }
    }
  })
}

const saveStepName = async (step: ProjectStep, name: string) => {
  if (name.trim() === '') {
    ElMessage.warning('步骤名称不能为空')
    return
  }
  
  if (name === step.name) {
    editingStepId.value = null
    return
  }
  
  try {
    await updateStep(step.id, { name: name.trim() })
    editingStepId.value = null
    await refreshProject()
  } catch (error) {
    // 错误已在Service层处理
  }
}

const cancelEditStepName = () => {
  editingStepId.value = null
  editingStepName.value = ''
}

const handleToggleTodo = async (step: ProjectStep) => {
  try {
    await toggleStepTodo(step.id)
    await refreshProject()
  } catch (error) {
    // 错误已在Service层处理
  }
}

const handleDeleteStep = async (step: ProjectStep) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除步骤"${step.name}"吗？`,
      '提示',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )
    
    await deleteStep(step.id)
    await refreshProject()
    await loadProjectLogs()
  } catch (error: any) {
    if (error !== 'cancel') {
      // 错误已在Service层处理
    }
  }
}

const handleFileChange = (file: any) => {
  // 验证文件大小（最大1GB）
  if (file.raw && file.raw.size > 1 * 1024 * 1024 * 1024) {
    ElMessage.error('单个文件不能超过1GB')
    uploadRef.value?.clearFiles()
    return
  }
  uploadForm.file = file.raw
}

const handleFileRemove = () => {
  uploadForm.file = null
}

const handleUpload = async () => {
  if (!uploadFormRef.value || !uploadForm.file) return
  
  await uploadFormRef.value.validate(async (valid) => {
    if (valid) {
      try {
        // 确保folder_id是数字类型，排除字符串'__create__'
        const folderId = typeof uploadForm.folder_id === 'number' ? uploadForm.folder_id : undefined
        await uploadFile(projectId, uploadForm.file!, {
          fileType: uploadForm.file_type,
          description: uploadForm.description,
          folderId
        })
        await loadAttachments()
        showUploadDialog.value = false
        resetUploadForm()
      } catch (error) {
        // 错误已在Service层处理
      }
    }
  })
}

const handleDownloadAttachment = async (attachment: Attachment) => {
  try {
    await downloadAttachment(attachment.id)
  } catch (error) {
    // 错误已在Service层处理
  }
}

// 文件类型判断函数
const isImageFile = (filename: string): boolean => {
  const ext = filename.toLowerCase().split('.').pop()
  return ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp', 'svg', 'ico'].includes(ext || '')
}

const isPdfFile = (filename: string): boolean => {
  return filename.toLowerCase().endsWith('.pdf')
}

const isTextFile = (filename: string): boolean => {
  const ext = filename.toLowerCase().split('.').pop()
  return ['txt', 'md', 'json', 'xml', 'csv', 'js', 'html', 'css', 'py', 'java', 'cpp', 'c', 'h', 'go', 'rs', 'php', 'rb', 'sh', 'yaml', 'yml', 'log', 'vue', 'jsx', 'tsx', 'swift', 'kt', 'sql', 'conf', 'ini'].includes(ext || '')
}

const isVideoFile = (filename: string): boolean => {
  const ext = filename.toLowerCase().split('.').pop()
  return ['mp4', 'webm', 'avi', 'mov', 'mkv', 'flv', 'wmv', 'm4v', 'mpeg', 'mpg', '3gp', 'ogv', 'ts', 'mts', 'm2ts'].includes(ext || '')
}

const isAudioFile = (filename: string): boolean => {
  const ext = filename.toLowerCase().split('.').pop()
  return ['mp3', 'wav', 'ogg', 'flac', 'aac', 'm4a', 'wma', 'aiff', 'aif', 'au', 'opus'].includes(ext || '')
}

const isOfficeFile = (filename: string): boolean => {
  const ext = filename.toLowerCase().split('.').pop()
  return ['doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'wps', 'et', 'dps', 'odt', 'ods', 'odp', 'rtf'].includes(ext || '')
}

const isWordFile = (filename: string): boolean => {
  const ext = filename.toLowerCase().split('.').pop()
  return ['doc', 'docx', 'wps', 'odt', 'rtf'].includes(ext || '')
}

const isExcelFile = (filename: string): boolean => {
  const ext = filename.toLowerCase().split('.').pop()
  return ['xls', 'xlsx', 'et', 'ods'].includes(ext || '')
}

const isPptFile = (filename: string): boolean => {
  const ext = filename.toLowerCase().split('.').pop()
  return ['ppt', 'pptx', 'dps', 'odp'].includes(ext || '')
}

// 预览URL缓存
const previewUrlCache = ref<Record<number, string>>({})

// 获取预览URL（使用Blob URL）
const getPreviewUrl = async (attachmentId: number): Promise<string> => {
  // 如果已缓存，直接返回
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

// 同步获取预览URL（用于模板）
const getPreviewUrlSync = (attachmentId: number): string => {
  return previewUrlCache.value[attachmentId] || ''
}

// 预览附件
const handlePreviewAttachment = async (attachment: Attachment) => {
  if (!attachment) {
    ElMessage.error('预览附件失败: 附件信息无效')
    return
  }
  
  previewAttachment.value = attachment
  textPreviewContent.value = ''
  officePreviewContent.value = ''
  officePreviewType.value = null
  showPreviewDialog.value = true
  
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
    // Word文档预览
    try {
      officePreviewType.value = 'word'
      const blob = await attachmentApi.preview(attachment.id)
      const arrayBuffer = await blob.arrayBuffer()
      const result = await mammoth.convertToHtml({ arrayBuffer })
      officePreviewContent.value = result.value
      if (result.messages.length > 0) {
        console.warn('Word转换警告:', result.messages)
      }
    } catch (error) {
      console.error('Word预览错误:', error)
      ElMessage.error('加载Word文档失败')
      officePreviewContent.value = '<p style="color: red; padding: 20px;">无法加载Word文档，请下载后使用本地软件打开</p>'
    }
  } else if (isExcelFile(attachment.file_name)) {
    // Excel文档预览
    try {
      officePreviewType.value = 'excel'
      const blob = await attachmentApi.preview(attachment.id)
      const arrayBuffer = await blob.arrayBuffer()
      const workbook = XLSX.read(arrayBuffer, { type: 'array' })
      
      // 将Excel转换为HTML表格
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
      officePreviewContent.value = '<p style="color: red; padding: 20px;">无法加载Excel文档，请下载后使用本地软件打开</p>'
    }
  } else if (isPptFile(attachment.file_name)) {
    // PPT文档预览（暂不支持，提示下载）
    officePreviewType.value = 'ppt'
    officePreviewContent.value = `
      <div style="text-align: center; padding: 60px 20px;">
        <el-icon style="font-size: 80px; color: #909399; margin-bottom: 20px;">
          <Document />
        </el-icon>
        <h3 style="color: #303133; margin: 20px 0 10px 0;">PPT文档预览暂不支持</h3>
        <p style="color: #606266; margin-bottom: 30px;">PowerPoint文档需要下载后使用Microsoft PowerPoint或其他软件打开</p>
        <p style="color: #909399; font-size: 14px;">支持的格式：.ppt, .pptx</p>
      </div>
    `
  } else {
    // 对于其他文件类型，预加载Blob URL
    try {
      await getPreviewUrl(attachment.id)
    } catch (error) {
      ElMessage.error('加载预览失败')
    }
  }
}

// 清理预览URL缓存
const cleanupPreviewUrls = () => {
  Object.values(previewUrlCache.value).forEach(url => {
    if (url) {
      URL.revokeObjectURL(url)
    }
  })
  previewUrlCache.value = {}
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
    
    await deleteAttachment(attachment.id)
    await loadAttachments()
    await loadFolders() // 刷新文件夹列表以更新文件数量
    closeContextMenu()
  } catch (error: any) {
    if (error !== 'cancel') {
      // 错误已在Service层处理
    }
  }
}

// 右键菜单相关
const showContextMenu = ref(false)
const contextMenuPosition = ref({ x: 0, y: 0 })
const contextMenuAttachment = ref<Attachment | null>(null)
const showGraduationTagMenu = ref(false)

// 毕设插件
const { tagAttachment, untagAttachment, getAttachmentTag } = useGraduationPlugin()
const { isProjectEnabled, loadPluginSettings } = usePluginSettings()
const isGraduationPluginEnabled = computed(() => {
  return project.value ? isProjectEnabled(project.value.id, 'graduation') : false
})
const isGithubPluginEnabled = computed(() => {
  return project.value ? isProjectEnabled(project.value.id, 'github') : false
})
const isVideoPlaybackPluginEnabled = computed(() => {
  return project.value ? isProjectEnabled(project.value.id, 'video-playback') : false
})

// 处理右键点击
const handleRightClick = (event: MouseEvent, attachment: Attachment) => {
  event.preventDefault()
  event.stopPropagation()
  
  // 计算菜单位置，避免被遮挡
  const menuWidth = 180 // 菜单宽度
  const menuHeight = 350 // 预估菜单高度（包含所有选项）
  const padding = 10 // 边距
  
  let x = event.clientX
  let y = event.clientY
  
  // 检查右边界
  if (x + menuWidth + padding > window.innerWidth) {
    x = window.innerWidth - menuWidth - padding
  }
  
  // 检查下边界，如果太靠下则向上调整
  if (y + menuHeight + padding > window.innerHeight) {
    y = window.innerHeight - menuHeight - padding
    // 如果向上调整后位置太靠上，则从点击位置向上显示
    if (y < padding) {
      y = event.clientY - menuHeight
      // 如果还是太靠上，则从顶部开始显示
      if (y < padding) {
        y = padding
      }
    }
  }
  
  // 检查左边界
  if (x < padding) {
    x = padding
  }
  
  // 检查上边界
  if (y < padding) {
    y = padding
  }
  
  contextMenuPosition.value = { x, y }
  contextMenuAttachment.value = attachment
  showContextMenu.value = true
}

// 关闭右键菜单
const closeContextMenu = () => {
  showContextMenu.value = false
  showGraduationTagMenu.value = false
  contextMenuAttachment.value = null
}

// 移入文件夹
const showMoveToFolderDialog = ref(false)
const moveToFolderId = ref<number | null>(null)
const moveToFolderAttachment = ref<Attachment | null>(null)

const handleMoveToFolder = () => {
  if (!contextMenuAttachment.value) return
  moveToFolderAttachment.value = contextMenuAttachment.value
  moveToFolderId.value = contextMenuAttachment.value.folder_id || null
  showMoveToFolderDialog.value = true
  closeContextMenu()
}

const confirmMoveToFolder = async () => {
  if (!moveToFolderAttachment.value) {
    ElMessage.error('未找到要移动的文件')
    showMoveToFolderDialog.value = false
    return
  }
  
  // 如果选择的文件夹和当前文件夹相同，不需要移动
  if (moveToFolderId.value === moveToFolderAttachment.value.folder_id) {
    ElMessage.info('文件已在目标文件夹中')
    showMoveToFolderDialog.value = false
    moveToFolderId.value = null
    moveToFolderAttachment.value = null
    return
  }
  
  try {
    await attachmentApi.update(moveToFolderAttachment.value.id, {
      folder_id: moveToFolderId.value || undefined
    })
    await loadAttachments()
    await loadFolders() // 刷新文件夹列表以更新文件数量
    ElMessage.success('文件已移入文件夹')
    showMoveToFolderDialog.value = false
    moveToFolderId.value = null
    moveToFolderAttachment.value = null
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '移动文件失败')
  }
}

// 重命名文件
const handleRenameFile = async () => {
  if (!contextMenuAttachment.value) return
  
  const currentName = contextMenuAttachment.value.file_name
  
  try {
    const { value: fileName } = await ElMessageBox.prompt(
      '请输入新文件名',
      '重命名文件',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        inputValue: currentName,
        inputValidator: (value) => {
          if (!value || !value.trim()) {
            return '文件名不能为空'
          }
          return true
        },
      }
    )
    
    if (fileName && fileName.trim() !== currentName) {
      await attachmentApi.update(contextMenuAttachment.value.id, {
        file_name: fileName.trim()
      })
      await loadAttachments()
      ElMessage.success('文件重命名成功')
      closeContextMenu()
    }
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.response?.data?.detail || '重命名文件失败')
    }
    closeContextMenu()
  }
}

// 移入其他文件夹
const handleMoveToOtherFolder = async () => {
  if (!contextMenuAttachment.value) return
  
  // 找到"其他"文件夹
  const otherFolder = folders.value.find(f => f.name === '其他')
  if (!otherFolder) {
    ElMessage.error('未找到"其他"文件夹')
    closeContextMenu()
    return
  }
  
  try {
    await attachmentApi.update(contextMenuAttachment.value.id, {
      folder_id: otherFolder.id
    })
    await loadAttachments()
    await loadFolders() // 刷新文件夹列表以更新文件数量
    ElMessage.success('文件已移入"其他"文件夹')
    closeContextMenu()
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '移动文件失败')
    closeContextMenu()
  }
}

// 判断是否为默认文件夹
const isDefaultFolder = (folderName: string): boolean => {
  return ['项目需求', '项目交付', '其他'].includes(folderName)
}

// 右键菜单操作函数
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

const handleContextMenuDelete = async () => {
  if (contextMenuAttachment.value) {
    await handleDeleteAttachment(contextMenuAttachment.value)
  }
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
  if (!contextMenuAttachment.value || !project.value) return
  
  // 检查项目是否启用插件
  if (!isProjectEnabled(project.value.id, 'graduation')) {
    ElMessage.warning('当前项目未启用毕设插件')
    showGraduationTagMenu.value = false
    closeContextMenu()
    return
  }
  
  await tagAttachment(contextMenuAttachment.value.id, fileType, project.value.id)
  showGraduationTagMenu.value = false
  closeContextMenu()
  await loadAttachments()
}

const handleUntagGraduationFile = async () => {
  if (!contextMenuAttachment.value) return
  
  untagAttachment(contextMenuAttachment.value.id)
  ElMessage.success('已取消标记')
  showGraduationTagMenu.value = false
  closeContextMenu()
  await loadAttachments()
}

const editGithubUrl = () => {
  githubForm.github_url = project.value?.github_url || ''
  showGithubDialog.value = true
}

const saveGithubUrl = async () => {
  if (!githubFormRef.value) return
  
  await githubFormRef.value.validate(async (valid) => {
    if (valid) {
      try {
        await updateProject(projectId, {
          github_url: githubForm.github_url || undefined,
        })
        showGithubDialog.value = false
        await refreshProject()
      } catch (error) {
        // 错误已在Service层处理
      }
    }
  })
}

const getStatusType = (status: string) => {
  const statusMap: Record<string, string> = {
    '进行中': 'warning',
    '已完成': 'success',
    '已结账': 'info',
  }
  return statusMap[status] || 'info'
}

const getStepStatusType = (status: string) => {
  const statusMap: Record<string, string> = {
    '待开始': 'info',
    '进行中': 'warning',
    '已完成': 'success',
  }
  return statusMap[status] || 'info'
}

// 加载所有标签（用于显示标签名称）
const loadAllTags = async () => {
  try {
    allTags.value = await tagApi.list(true)
  } catch (error) {
    console.error('加载标签列表失败:', error)
  }
}

// 根据标签ID获取标签名称
const getTagName = (tagId: number): string => {
  const tag = allTags.value.find(t => t.id === tagId)
  return tag ? tag.name : `标签 ${tagId}`
}

// 点击标签跳转到项目管理页面并筛选

const goBack = () => {
  router.back()
}

// 删除项目日志（通过ID）
const handleDeleteLogById = async (logId: number) => {
  try {
    await projectApi.deleteLog(logId)
    ElMessage.success('日志删除成功')
    await loadProjectLogs()
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '删除日志失败')
    console.error('Failed to delete log:', error)
  }
}

// 加载项目日志
const loadProjectLogs = async () => {
  loadingLogs.value = true
  try {
    projectLogs.value = await projectApi.getLogs(projectId)
    
    // 批量获取所有日志的附件信息
    const allAttachmentIds: number[] = []
    projectLogs.value.forEach(log => {
      const details = parseLogDetails(log.details)
      if (details?.attachment_ids) {
        allAttachmentIds.push(...details.attachment_ids)
      }
    })
    
    // 去重
    const uniqueIds = [...new Set(allAttachmentIds)]
    
    if (uniqueIds.length > 0) {
      try {
        const attachments = await attachmentApi.batch(uniqueIds)
        // 按日志分组附件
        const attachmentsMap: Record<number, Attachment[]> = {}
        projectLogs.value.forEach(log => {
          const details = parseLogDetails(log.details)
          if (details?.attachment_ids) {
            attachmentsMap[log.id] = attachments.filter(a => 
              details.attachment_ids.includes(a.id)
            )
          }
        })
        logAttachments.value = attachmentsMap
      } catch (error) {
        console.error('获取附件信息失败:', error)
      }
    }
    
    // 预加载所有照片URL
    projectLogs.value.forEach(log => {
      const details = parseLogDetails(log.details)
      if (details?.photos && details.photos.length > 0) {
        details.photos.forEach((photo: string | number) => {
          loadPhotoUrl(photo).catch(error => {
            console.error(`Failed to preload photo ${photo}:`, error)
          })
        })
      }
    })
  } catch (error) {
    ElMessage.error('加载项目日志失败')
  } finally {
    loadingLogs.value = false
  }
}

// 加载元器件清单 - 功能已移至 ProjectPartsPlugin 插件
// 保留此函数以防其他地方调用，但实际功能由插件管理
const loadProjectParts = async () => {
  // 功能已移至 ProjectPartsPlugin 插件
  // 此函数保留用于兼容性
}

// 打开配件编辑对话框
const openPartsEditDialog = () => {
  if (!project.value) return
  editingPart.value = null
  editingPartIndex.value = -1
  showPartsEditDialog.value = true
}

// 编辑单个配件
const editPartRow = (index: number, row: ProjectPart) => {
  editingPart.value = row
  editingPartIndex.value = index
  showPartsEditDialog.value = true
}

// 处理保存成功
const handlePartsSave = async () => {
  await loadProjectParts()
}

// 处理取消
const handlePartsCancel = () => {
  editingPart.value = null
  editingPartIndex.value = -1
}


const removePartRow = async (index: number, row: ProjectPart) => {
  if (!project.value) return
  // 负ID表示仅前端存在，尚未保存
  if (row.id < 0) {
    parts.value.splice(index, 1)
    return
  }
  try {
    await projectPartApi.delete(row.id)
    parts.value.splice(index, 1)
    ElMessage.success('元器件已删除')
  } catch (error: any) {
    console.error('删除元器件失败:', error)
    ElMessage.error(error.response?.data?.detail || '删除元器件失败')
  }
}

const partsTotalPrice = computed(() => {
  return parts.value.reduce((sum, p) => {
    const price = Number(p.unit_price || 0)
    const qty = Number(p.quantity || 0)
    return sum + price * qty
  }, 0)
})

const exportPartsToExcel = () => {
  if (!project.value || parts.value.length === 0) return
  const title = `${project.value.title} - 元器件清单`

  const header = ['功能模块名称', '核心元器件', '主要功能描述', '单价', '数量', '小计', '购买链接', '图片链接']
  const dataRows = parts.value.map(p => [
    p.module_name,
    p.core_component,
    p.remark || '',
    Number(p.unit_price || 0),
    Number(p.quantity || 0),
    Number(p.unit_price || 0) * Number(p.quantity || 0),
    p.purchase_link || '',
    p.image_url || '',
  ])

  const aoa = [
    [title],
    [],
    header,
    ...dataRows,
  ]

  const ws = XLSX.utils.aoa_to_sheet(aoa)
  const wb = XLSX.utils.book_new()
  XLSX.utils.book_append_sheet(wb, ws, '元器件清单')

  const fileName = `${project.value.title}_元器件清单_${new Date().toISOString().split('T')[0]}.xlsx`
  XLSX.writeFile(wb, fileName)
}

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

// 获取日志操作图标组件（使用配置的图标）
const { getIcon: getLogIcon } = useLogIconConfig()

const getLogActionIcon = (action: string) => {
  return getLogIcon(action as any) || iconComponents.InfoFilled
}

// 获取日志操作颜色 - 黑白极简风格，统一使用黑色
const getLogActionColor = (action: string): string => {
  return '#000'
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

// 获取文件附件ID列表（排除照片ID）
const getFileAttachmentIds = (details?: string): number[] => {
  const parsed = parseLogDetails(details)
  if (!parsed) return []
  
  // 如果是快照日志，需要从attachment_ids中排除photos中的ID
  if (parsed.photos && parsed.attachment_ids) {
    const photoIds = parsed.photos.map((p: string | number) => {
      // photos可能是ID字符串或数字
      if (typeof p === 'string') {
        return parseInt(p) || 0
      }
      return p
    }).filter((id: number) => id > 0)
    
    // 从attachment_ids中排除照片ID
    return parsed.attachment_ids.filter((id: number) => !photoIds.includes(id))
  }
  
  // 其他情况直接返回attachment_ids
  return parsed.attachment_ids || []
}

// 获取日志的文件附件（排除照片）
const getFileAttachments = (logId: number): Attachment[] => {
  const attachments = logAttachments.value[logId] || []
  const log = projectLogs.value.find(l => l.id === logId)
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

// 获取日志的所有附件
const getLogAttachments = (logId: number): Attachment[] => {
  return logAttachments.value[logId] || []
}

// 项目需求 Markdown 渲染函数
const renderRequirementsMarkdown = (text: string): string => {
  if (!text) return ''
  return md.render(text)
}

// 简单的Markdown渲染函数（用于日志）
const renderMarkdown = (text: string): string => {
  if (!text) return ''
  
  // 转义HTML，防止XSS
  const escapeHtml = (str: string) => {
    const div = document.createElement('div')
    div.textContent = str
    return div.innerHTML
  }
  
  let html = escapeHtml(text)
  
  // 标题
  html = html.replace(/^### (.*$)/gim, '<h3>$1</h3>')
  html = html.replace(/^## (.*$)/gim, '<h2>$1</h2>')
  html = html.replace(/^# (.*$)/gim, '<h1>$1</h1>')
  
  // 粗体
  html = html.replace(/\*\*(.*?)\*\*/gim, '<strong>$1</strong>')
  html = html.replace(/__(.*?)__/gim, '<strong>$1</strong>')
  
  // 斜体
  html = html.replace(/\*(.*?)\*/gim, '<em>$1</em>')
  html = html.replace(/_(.*?)_/gim, '<em>$1</em>')
  
  // 代码块
  html = html.replace(/```([\s\S]*?)```/gim, '<pre><code>$1</code></pre>')
  
  // 行内代码
  html = html.replace(/`([^`]+)`/gim, '<code>$1</code>')
  
  // 链接
  html = html.replace(/\[([^\]]+)\]\(([^)]+)\)/gim, '<a href="$2" target="_blank" rel="noopener noreferrer">$1</a>')
  
  // 列表
  html = html.replace(/^\* (.*$)/gim, '<li>$1</li>')
  html = html.replace(/^- (.*$)/gim, '<li>$1</li>')
  html = html.replace(/^\+ (.*$)/gim, '<li>$1</li>')
  
  // 换行
  html = html.replace(/\n/gim, '<br>')
  
  // 包装列表项
  html = html.replace(/(<li>.*<\/li>)/gim, '<ul>$1</ul>')
  
  return html
}

// 照片URL缓存（响应式）
const photoUrlCache = ref<Map<string | number, string>>(new Map())

// 获取附件ID
const getAttachmentId = (photoPath: string | number): number | null => {
  if (typeof photoPath === 'number') {
    return photoPath
  }
  if (typeof photoPath === 'string') {
    if (photoPath.startsWith('http://') || photoPath.startsWith('https://')) {
      return null // 完整URL，不需要转换
    }
    const id = parseInt(photoPath.split('/').pop()?.replace(/\.[^.]+$/, '') || photoPath) || 0
    return id > 0 ? id : null
  }
  return null
}

// 加载照片URL（异步）
const loadPhotoUrl = async (photoPath: string | number): Promise<string> => {
  // 如果已缓存，直接返回
  if (photoUrlCache.value.has(photoPath)) {
    return photoUrlCache.value.get(photoPath)!
  }
  
  // 如果是完整URL，直接返回
  if (typeof photoPath === 'string' && (photoPath.startsWith('http://') || photoPath.startsWith('https://'))) {
    photoUrlCache.value.set(photoPath, photoPath)
    return photoPath
  }
  
  const attachmentId = getAttachmentId(photoPath)
  if (!attachmentId) return ''
  
  try {
    // 通过axios获取图片（会自动添加认证头）
    const response = await attachmentApi.download(attachmentId)
    // response已经是Blob类型
    let blob: Blob
    if (response instanceof Blob) {
      blob = response
    } else if (response && typeof response === 'object' && 'data' in response) {
      // 如果response有data属性，使用data
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

// 获取照片URL（同步版本，用于模板）
const getPhotoUrl = (photoPath: string | number): string => {
  // 如果已缓存，直接返回
  if (photoUrlCache.value.has(photoPath)) {
    return photoUrlCache.value.get(photoPath)!
  }
  
  // 如果是完整URL，直接返回
  if (typeof photoPath === 'string' && (photoPath.startsWith('http://') || photoPath.startsWith('https://'))) {
    return photoPath
  }
  
  // 如果未缓存，触发异步加载
  loadPhotoUrl(photoPath).then(url => {
    if (url) {
      // URL加载成功后，触发响应式更新
      photoUrlCache.value.set(photoPath, url)
    }
  })
  
  // 返回空字符串，等待异步加载
  return ''
}

// 打开照片查看器
const openPhotoViewer = (photos: (string | number)[], index: number) => {
  photoViewerImages.value = photos.map(p => getPhotoUrl(p))
  photoViewerIndex.value = index
  showPhotoViewer.value = true
}

// 处理图片加载错误
const handleImageError = (e: Event) => {
  const img = e.target as HTMLImageElement
  img.src = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCIgZmlsbD0iI2Y1ZjdmYSIvPjx0ZXh0IHg9IjUwJSIgeT0iNTAlIiBmb250LWZhbWlseT0iQXJpYWwiIGZvbnQtc2l6ZT0iMTQiIGZpbGw9IiM5MDkzOTkiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGR5PSIuM2VtIj7lm77niYfliqDovb3lpLHotKU8L3RleHQ+PC9zdmc+'
}

// 下载附件
const downloadAttachmentById = async (attachmentId: number) => {
  try {
    await downloadAttachment(attachmentId)
  } catch (error) {
    ElMessage.error('下载附件失败')
  }
}

// 导出项目日志
const handleExportLogs = async (format: 'markdown' | 'pdf') => {
  if (projectLogs.value.length === 0) {
    ElMessage.warning('没有日志可导出')
    return
  }
  
  if (format === 'markdown') {
    exportAsMarkdown()
  } else {
    exportAsPDF()
  }
}

// 将图片转换为base64
const imageToBase64 = async (url: string): Promise<string> => {
  try {
    // 如果是相对路径，转换为完整URL
    const fullUrl = url.startsWith('/') ? `${window.location.origin}${url}` : url
    
    // 使用fetch获取图片
    const response = await fetch(fullUrl, {
      credentials: 'include' // 包含cookie以支持认证
    })
    
    if (!response.ok) {
      throw new Error('图片加载失败')
    }
    
    const blob = await response.blob()
    
    // 将blob转换为base64
    return new Promise((resolve, reject) => {
      const reader = new FileReader()
      reader.onloadend = () => {
        const base64 = reader.result as string
        resolve(base64)
      }
      reader.onerror = () => reject(new Error('图片转换失败'))
      reader.readAsDataURL(blob)
    })
  } catch (error) {
    // 如果fetch失败，尝试使用Image方式
    return new Promise((resolve, reject) => {
      const img = new Image()
      img.crossOrigin = 'anonymous'
      img.onload = () => {
        const canvas = document.createElement('canvas')
        canvas.width = img.width
        canvas.height = img.height
        const ctx = canvas.getContext('2d')
        if (ctx) {
          ctx.drawImage(img, 0, 0)
          try {
            const base64 = canvas.toDataURL('image/png')
            resolve(base64)
          } catch (error) {
            reject(error)
          }
        } else {
          reject(new Error('无法创建canvas上下文'))
        }
      }
      img.onerror = () => reject(new Error('图片加载失败'))
      const fullUrl = url.startsWith('/') ? `${window.location.origin}${url}` : url
      img.src = fullUrl
    })
  }
}

// 导出为Markdown格式
const exportAsMarkdown = async () => {
  ElMessage.info('正在导出，请稍候...')
  
  let content = `# 项目日志\n\n`
  content += `**项目名称**：${project.value?.title || '未知项目'}\n\n`
  content += `**导出时间**：${new Date().toLocaleString('zh-CN')}\n\n`
  content += `**日志总数**：${projectLogs.value.length} 条\n\n`
  content += '---\n\n'
  
  for (const log of projectLogs.value) {
    const index = projectLogs.value.indexOf(log)
    content += `## ${index + 1}. ${formatLogAction(log.action)}\n\n`
    content += `**时间**：${new Date(log.created_at).toLocaleString('zh-CN')}\n\n`
    if (log.user_name) {
      content += `**操作人**：${log.user_name}\n\n`
    }
    content += `**描述**：${log.description}\n\n`
    
    const details = parseLogDetails(log.details)
    if (details) {
      if (details.step_names && details.step_names.length > 0) {
        content += `**涉及步骤**：${details.step_names.join('、')}\n\n`
      }
      if (details.completion_note) {
        content += `**完成说明**：\n\n${details.completion_note}\n\n`
      }
      if (details.update_note) {
        content += `**更新说明**：\n\n${details.update_note}\n\n`
      }
      if (details.snapshot_note) {
        content += `**快照说明**：\n\n${details.snapshot_note}\n\n`
      }
      if (details.photos && details.photos.length > 0) {
        content += `**照片**：\n\n`
        for (const photo of details.photos) {
          try {
            // 获取附件ID
            let attachmentId: number | null = null
            if (typeof photo === 'number') {
              attachmentId = photo
            } else if (typeof photo === 'string') {
              attachmentId = parseInt(photo.split('/').pop()?.replace(/\.[^.]+$/, '') || photo) || 0
            }
            
            if (attachmentId) {
              try {
                // 通过axios获取图片并转换为base64
                const response = await attachmentApi.download(attachmentId)
                const blob = response instanceof Blob ? response : new Blob([response], { type: 'image/jpeg' })
                const base64 = await new Promise<string>((resolve, reject) => {
                  const reader = new FileReader()
                  reader.onloadend = () => resolve(reader.result as string)
                  reader.onerror = () => reject(new Error('图片转换失败'))
                  reader.readAsDataURL(blob)
                })
                content += `![照片](${base64})\n\n`
              } catch (error) {
                console.error('Failed to load photo for markdown export:', error)
                content += `![照片](图片加载失败)\n\n`
              }
            }
          } catch (error) {
            content += `![照片](图片加载失败)\n\n`
          }
        }
      }
      if (details.attachment_ids && details.attachment_ids.length > 0) {
        const fileIds = getFileAttachmentIds(log.details)
        if (fileIds.length > 0) {
          content += `**文件**：\n\n`
          const fileAttachments = getFileAttachments(log.id)
          fileAttachments.forEach((attachment) => {
            content += `- ${attachment.file_name}\n`
          })
          content += '\n'
        }
      }
    }
    
    content += '---\n\n'
  }
  
  // 创建Blob并下载
  const blob = new Blob([content], { type: 'text/markdown;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `项目日志_${project.value?.title || '未知项目'}_${new Date().toISOString().split('T')[0]}.md`
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
  
  ElMessage.success('日志导出成功')
}

// 导出为PDF格式（使用浏览器打印功能）
const exportAsPDF = async () => {
  ElMessage.info('正在导出，请稍候...')
  // 创建打印内容
  let htmlContent = `
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="UTF-8">
      <title>项目日志 - ${project.value?.title || '未知项目'}</title>
      <style>
        body {
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
          padding: 40px;
          line-height: 1.6;
          color: #333;
        }
        h1 {
          font-size: 24px;
          margin-bottom: 10px;
          color: #000;
        }
        h2 {
          font-size: 18px;
          margin-top: 30px;
          margin-bottom: 10px;
          color: #000;
          border-bottom: 2px solid #000;
          padding-bottom: 5px;
        }
        .meta {
          margin-bottom: 30px;
          color: #666;
          font-size: 14px;
        }
        .log-item {
          margin-bottom: 30px;
          page-break-inside: avoid;
        }
        .log-header {
          margin-bottom: 10px;
        }
        .log-time {
          color: #666;
          font-size: 12px;
        }
        .log-description {
          margin: 10px 0;
        }
        .log-details {
          margin-top: 10px;
          padding-left: 20px;
        }
        .photo-grid {
          display: grid;
          grid-template-columns: repeat(3, 1fr);
          gap: 6px;
          max-width: 600px;
          margin: 8px 0;
        }
        .photo-item {
          aspect-ratio: 1;
          overflow: hidden;
          border-radius: 4px;
        }
        .photo-item img {
          width: 100%;
          height: 100%;
          object-fit: cover;
        }
        .markdown-content {
          margin-top: 8px;
        }
        .markdown-content h1 { font-size: 18px; font-weight: 600; margin: 12px 0 6px 0; }
        .markdown-content h2 { font-size: 16px; font-weight: 600; margin: 10px 0 4px 0; }
        .markdown-content h3 { font-size: 14px; font-weight: 600; margin: 8px 0 2px 0; }
        .markdown-content strong { font-weight: 600; }
        .markdown-content em { font-style: italic; }
        .markdown-content code { background: #f3f4f6; padding: 2px 4px; border-radius: 2px; font-size: 12px; }
        .markdown-content pre { background: #f3f4f6; padding: 8px; border-radius: 3px; overflow-x: auto; margin: 6px 0; }
        .markdown-content pre code { background: transparent; padding: 0; }
        .markdown-content ul { margin: 6px 0; padding-left: 20px; }
        .markdown-content li { margin: 2px 0; }
        @media print {
          body { padding: 20px; }
          .log-item { page-break-inside: avoid; }
        }
      </style>
    </head>
    <body>
      <h1>项目日志</h1>
      <div class="meta">
        <p><strong>项目名称</strong>：${project.value?.title || '未知项目'}</p>
        <p><strong>导出时间</strong>：${new Date().toLocaleString('zh-CN')}</p>
        <p><strong>日志总数</strong>：${projectLogs.value.length} 条</p>
      </div>
      <hr style="margin: 30px 0; border: 1px solid #ddd;">
  `
  
  // 使用async函数处理图片
  const processLogs = async () => {
    for (const log of projectLogs.value) {
      const index = projectLogs.value.indexOf(log)
      htmlContent += `
        <div class="log-item">
          <h2>${index + 1}. ${formatLogAction(log.action)}</h2>
          <div class="log-header">
            <div class="log-time">时间：${new Date(log.created_at).toLocaleString('zh-CN')}</div>
            ${log.user_name ? `<div class="log-time">操作人：${log.user_name}</div>` : ''}
          </div>
          <div class="log-description">${log.description}</div>
      `
      
      const details = parseLogDetails(log.details)
      if (details) {
        if (details.step_names && details.step_names.length > 0) {
          htmlContent += `<div class="log-details"><strong>涉及步骤</strong>：${details.step_names.join('、')}</div>`
        }
        if (details.completion_note) {
          const renderedNote = renderMarkdown(details.completion_note)
          htmlContent += `<div class="log-details"><strong>完成说明</strong>：<div class="markdown-content">${renderedNote}</div></div>`
        }
        if (details.update_note) {
          const renderedNote = renderMarkdown(details.update_note)
          htmlContent += `<div class="log-details"><strong>更新说明</strong>：<div class="markdown-content">${renderedNote}</div></div>`
        }
        if (details.snapshot_note) {
          const renderedNote = renderMarkdown(details.snapshot_note)
          htmlContent += `<div class="log-details"><strong>快照说明</strong>：<div class="markdown-content">${renderedNote}</div></div>`
        }
        if (details.photos && details.photos.length > 0) {
          htmlContent += `<div class="log-details"><strong>照片</strong>：</div><div class="photo-grid" style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 6px; max-width: 600px; margin: 8px 0;">`
          for (const photo of details.photos) {
            try {
              // 获取附件ID
              let attachmentId: number | null = null
              if (typeof photo === 'number') {
                attachmentId = photo
              } else if (typeof photo === 'string') {
                attachmentId = parseInt(photo.split('/').pop()?.replace(/\.[^.]+$/, '') || photo) || 0
              }
              
              if (attachmentId) {
                try {
                  // 通过axios获取图片并转换为base64
                  const response = await attachmentApi.download(attachmentId)
                  const blob = response instanceof Blob ? response : new Blob([response], { type: 'image/jpeg' })
                  const base64 = await new Promise<string>((resolve, reject) => {
                    const reader = new FileReader()
                    reader.onloadend = () => resolve(reader.result as string)
                    reader.onerror = () => reject(new Error('图片转换失败'))
                    reader.readAsDataURL(blob)
                  })
                  htmlContent += `<div class="photo-item" style="aspect-ratio: 1; overflow: hidden; border-radius: 4px;"><img src="${base64}" alt="照片" style="width: 100%; height: 100%; object-fit: cover;" /></div>`
                } catch (error) {
                  console.error('Failed to load photo for export:', error)
                  htmlContent += `<div class="photo-item" style="aspect-ratio: 1; background: #f5f7fa; border-radius: 4px; display: flex; align-items: center; justify-content: center; color: #999; font-size: 12px;">图片加载失败</div>`
                }
              }
            } catch (error) {
              htmlContent += `<div class="photo-item" style="aspect-ratio: 1; background: #f5f7fa; border-radius: 4px; display: flex; align-items: center; justify-content: center; color: #999; font-size: 12px;">图片加载失败</div>`
            }
          }
          htmlContent += `</div>`
        }
        // 显示文件列表
        const fileIds = getFileAttachmentIds(log.details)
        if (fileIds.length > 0) {
          const fileAttachments = getFileAttachments(log.id)
          if (fileAttachments.length > 0) {
            htmlContent += `<div class="log-details"><strong>文件</strong>：</div><div class="file-list">`
            fileAttachments.forEach((attachment) => {
              htmlContent += `<div class="file-item">${attachment.file_name}</div>`
            })
            htmlContent += `</div>`
          }
        }
      }
      
      htmlContent += `</div><hr style="margin: 20px 0; border: 1px solid #eee;">`
    }
    
    htmlContent += `
        </body>
      </html>
    `
    
    // 打开新窗口并打印
    const printWindow = window.open('', '_blank')
    if (printWindow) {
      printWindow.document.write(htmlContent)
      printWindow.document.close()
      // 等待图片加载完成后再打印
      printWindow.onload = async () => {
        // 等待所有图片加载
        await new Promise(resolve => setTimeout(resolve, 1000))
        printWindow.print()
      }
    } else {
      ElMessage.warning('无法打开打印窗口，请检查浏览器弹窗设置')
    }
  }
  
  await processLogs()
}

// 组件卸载时清理预览URL
onUnmounted(() => {
  cleanupPreviewUrls()
  // 移除全局点击事件监听
  document.removeEventListener('click', handleClickOutside)
})

// 点击外部关闭右键菜单（合并处理所有右键菜单）
const handleClickOutside = (event: MouseEvent) => {
  // 关闭附件右键菜单
  if (showContextMenu.value) {
    closeContextMenu()
  }
}

onMounted(async () => {
  // 加载插件设置（全局共享）
  loadPluginSettings()
  await Promise.all([
    loadPlatforms(),
    loadAllTags(),
    refreshProject(),
    loadAttachments(),
    loadFolders(),
    loadProjectLogs()
  ])
  // loadProjectParts() - 功能已移至 ProjectPartsPlugin 插件
  
  // 调试：检查项目标签数据
  if (project.value) {
    console.log('Project tags after load:', project.value.tags)
    console.log('Project tags length:', project.value.tags?.length || 0)
  }
  
  // 添加全局点击事件监听，用于关闭右键菜单
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  // 移除全局点击事件监听
  document.removeEventListener('click', handleClickOutside)
})
</script>

<style scoped>
/* 结账标识青蓝渐变色 */
.settled-tag {
  background: linear-gradient(135deg, #409eff 0%, #66b1ff 100%) !important;
  border: none !important;
  color: #fff !important;
}

.project-detail {
  padding: 0;
  max-width: 1400px;
  margin: 0 auto;
}

.project-info-card {
  margin-bottom: 20px;
}

.requirements-card {
  margin-bottom: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.requirements-content-wrapper {
  position: relative;
}

.requirements-content {
  line-height: 1.8;
  color: #303133;
  transition: max-height 0.3s ease;
  overflow: hidden;
}

.requirements-content.requirements-collapsed {
  max-height: 300px;
  position: relative;
}

.requirements-content.requirements-collapsed::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 80px;
  background: linear-gradient(to bottom, transparent, #fff);
  pointer-events: none;
}

.requirements-expand-overlay {
  display: flex;
  justify-content: center;
  padding-top: 12px;
  border-top: 1px solid #e4e7ed;
  margin-top: 16px;
}

.requirements-expand-overlay.is-expanded {
  border-top: none;
  padding-top: 0;
}

.expand-button {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #409eff;
  font-size: 14px;
  padding: 8px 16px;
  transition: all 0.3s;
}

.expand-button:hover {
  color: #66b1ff;
  background: #ecf5ff;
}

.requirements-content :deep(h1) {
  font-size: 24px;
  font-weight: 600;
  margin: 20px 0 12px 0;
  color: #303133;
  border-bottom: 2px solid #e4e7ed;
  padding-bottom: 8px;
}

.requirements-content :deep(h2) {
  font-size: 20px;
  font-weight: 600;
  margin: 18px 0 10px 0;
  color: #303133;
}

.requirements-content :deep(h3) {
  font-size: 16px;
  font-weight: 600;
  margin: 16px 0 8px 0;
  color: #303133;
}

.requirements-content :deep(h4) {
  font-size: 14px;
  font-weight: 600;
  margin: 14px 0 6px 0;
  color: #303133;
}

.requirements-content :deep(p) {
  margin: 12px 0;
  line-height: 1.8;
  color: #606266;
}

.requirements-content :deep(strong) {
  font-weight: 600;
  color: #303133;
}

.requirements-content :deep(em) {
  font-style: italic;
  color: #606266;
}

.requirements-content :deep(code) {
  background: #f3f4f6;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 13px;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  color: #e83e8c;
}

.requirements-content :deep(pre) {
  background: #f5f7fa;
  padding: 16px;
  border-radius: 8px;
  overflow-x: auto;
  margin: 16px 0;
  border: 1px solid #e4e7ed;
}

.requirements-content :deep(pre code) {
  background: transparent;
  padding: 0;
  color: #303133;
  font-size: 13px;
}

.requirements-content :deep(ul),
.requirements-content :deep(ol) {
  margin: 12px 0;
  padding-left: 24px;
}

.requirements-content :deep(li) {
  margin: 6px 0;
  line-height: 1.8;
  color: #606266;
}

.requirements-content :deep(a) {
  color: #409eff;
  text-decoration: none;
  border-bottom: 1px solid transparent;
  transition: all 0.3s;
}

.requirements-content :deep(a:hover) {
  color: #66b1ff;
  border-bottom-color: #66b1ff;
}

.requirements-content :deep(blockquote) {
  border-left: 4px solid #409eff;
  padding-left: 16px;
  margin: 16px 0;
  color: #909399;
  font-style: italic;
  background: #f5f7fa;
  padding: 12px 16px;
  border-radius: 4px;
}

.requirements-content :deep(hr) {
  border: none;
  border-top: 1px solid #e4e7ed;
  margin: 24px 0;
}

.requirements-content :deep(table) {
  width: 100%;
  border-collapse: collapse;
  margin: 16px 0;
}

.requirements-content :deep(th),
.requirements-content :deep(td) {
  border: 1px solid #e4e7ed;
  padding: 10px 12px;
  text-align: left;
}

.requirements-content :deep(th) {
  background: #f5f7fa;
  font-weight: 600;
  color: #303133;
}

.requirements-content :deep(img) {
  max-width: 100%;
  height: auto;
  border-radius: 8px;
  margin: 16px 0;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.main-content-row {
  margin-bottom: 20px;
}

.steps-card,

.files-card {
  margin-top: 0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
}

/* 优化的步骤时间线样式 */
.steps-timeline-container {
  padding: 20px 0;
}

.timeline-wrapper {
  position: relative;
  padding-left: 40px;
}

.timeline-item {
  position: relative;
  margin-bottom: 24px;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.timeline-item:hover {
  transform: translateX(4px);
}

.timeline-item-active {
  background: linear-gradient(90deg, rgba(64, 158, 255, 0.05) 0%, transparent 100%);
  border-left: 3px solid #409eff;
  padding-left: 12px;
  margin-left: -12px;
  border-radius: 4px;
}

.timeline-item-completed .timeline-node {
  background: linear-gradient(135deg, #67c23a 0%, #85ce61 100%);
  box-shadow: 0 2px 8px rgba(103, 194, 58, 0.3);
}

.timeline-item-todo {
  background: linear-gradient(90deg, rgba(255, 193, 7, 0.08) 0%, transparent 100%);
  border-left: 3px solid #ffc107;
  padding-left: 12px;
  margin-left: -12px;
  border-radius: 4px;
  animation: todoPulse 2s ease-in-out infinite;
}

@keyframes todoPulse {
  0%, 100% {
    box-shadow: 0 0 0 0 rgba(255, 193, 7, 0.4);
  }
  50% {
    box-shadow: 0 0 0 8px rgba(255, 193, 7, 0);
  }
}

.timeline-line {
  position: absolute;
  left: -32px;
  top: 40px;
  width: 2px;
  height: calc(100% + 24px);
  background: linear-gradient(to bottom, #e4e7ed 0%, #e4e7ed 50%, transparent 100%);
  transition: background 0.3s;
}

.timeline-item-completed + .timeline-item .timeline-line {
  background: linear-gradient(to bottom, #67c23a 0%, #e4e7ed 50%, transparent 100%);
}

.timeline-node {
  position: absolute;
  left: -40px;
  top: 0;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: #e4e7ed;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  z-index: 2;
}

.timeline-item:hover .timeline-node {
  transform: scale(1.1);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.node-icon {
  color: #fff;
  font-size: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.node-number {
  font-size: 14px;
  font-weight: 600;
  color: #909399;
}

.node-success {
  background: linear-gradient(135deg, #67c23a 0%, #85ce61 100%);
}

.node-process {
  background: linear-gradient(135deg, #409eff 0%, #66b1ff 100%);
  animation: nodePulse 2s ease-in-out infinite;
}

@keyframes nodePulse {
  0%, 100% {
    box-shadow: 0 0 0 0 rgba(64, 158, 255, 0.6);
  }
  50% {
    box-shadow: 0 0 0 8px rgba(64, 158, 255, 0);
  }
}

.node-wait {
  background: #e4e7ed;
}

.node-wait .node-number {
  color: #909399;
}

.timeline-content {
  background: #fff;
  border-radius: 8px;
  padding: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  border: 1px solid #ebeef5;
}

.timeline-item:hover .timeline-content {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
  border-color: #c0c4cc;
}

.timeline-item-expanded .timeline-content {
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  border-color: #409eff;
}

.step-disabled {
  opacity: 0.7;
  position: relative;
}

.step-disabled::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.5);
  border-radius: 8px;
  z-index: 1;
  pointer-events: none;
}

.step-name-disabled {
  color: #c0c4cc;
  cursor: not-allowed;
}

.status-badge-disabled {
  opacity: 0.5;
  cursor: not-allowed;
  pointer-events: none;
}

.warning-icon {
  color: #e6a23c;
  font-size: 16px;
  cursor: help;
  animation: warningPulse 2s ease-in-out infinite;
}

@keyframes warningPulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.6;
  }
}

.status-option.disabled {
  opacity: 0.5;
  cursor: not-allowed;
  background: #f5f7fa;
  color: #c0c4cc;
  pointer-events: none;
}

.step-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
}

.step-title-row {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
  flex-wrap: wrap;
}

.step-name {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 4px;
  transition: all 0.2s;
  flex: 1;
  min-width: 120px;
}

.step-name:hover {
  background-color: #f5f7fa;
  color: #409eff;
}

.step-name-input {
  flex: 1;
  min-width: 200px;
}

.step-badges {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.step-time-info {
  margin-top: 8px;
  padding-top: 8px;
  border-top: 1px solid #ebeef5;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.step-time-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: #909399;
}

.time-icon {
  font-size: 14px;
  color: #909399;
}

.time-label {
  color: #909399;
  font-weight: 500;
}

.time-value {
  color: #606266;
  font-weight: 500;
}

.status-badge {
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  user-select: none;
}

.status-badge:hover {
  transform: scale(1.05);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.status-success {
  background: linear-gradient(135deg, #67c23a 0%, #85ce61 100%);
  color: #fff;
}

.status-process {
  background: linear-gradient(135deg, #409eff 0%, #66b1ff 100%);
  color: #fff;
}

.status-wait {
  background: #f5f7fa;
  color: #909399;
}

.todo-badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
  background: linear-gradient(135deg, #ffc107 0%, #ffd54f 100%);
  color: #fff;
  cursor: pointer;
  transition: all 0.2s;
  animation: todoBadgePulse 2s ease-in-out infinite;
}

.todo-badge:hover {
  transform: scale(1.05);
  box-shadow: 0 2px 8px rgba(255, 193, 7, 0.4);
}

@keyframes todoBadgePulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.8;
  }
}

.expand-indicator {
  color: #909399;
  transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  flex-shrink: 0;
}

.expand-indicator .rotated {
  transform: rotate(180deg);
}

/* 展开详情区域 */
.step-details {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #ebeef5;
}

.slide-down-enter-active,
.slide-down-leave-active {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  overflow: hidden;
}

.slide-down-enter-from {
  opacity: 0;
  max-height: 0;
  transform: translateY(-10px);
}

.slide-down-enter-to {
  opacity: 1;
  max-height: 500px;
  transform: translateY(0);
}

.slide-down-leave-from {
  opacity: 1;
  max-height: 500px;
  transform: translateY(0);
}

.slide-down-leave-to {
  opacity: 0;
  max-height: 0;
  transform: translateY(-10px);
}

.details-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  margin-bottom: 16px;
}

.detail-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.detail-item label {
  font-size: 12px;
  color: #909399;
  font-weight: 500;
}

.status-selector {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.status-option {
  padding: 6px 16px;
  border-radius: 16px;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
  background: #f5f7fa;
  color: #606266;
  border: 1px solid #e4e7ed;
}

.status-option:hover {
  background: #ebeef5;
  transform: translateY(-2px);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.status-option.active {
  background: linear-gradient(135deg, #409eff 0%, #66b1ff 100%);
  color: #fff;
  border-color: #409eff;
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.3);
}

.step-actions {
  display: flex;
  gap: 12px;
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #ebeef5;
}

.action-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  border-radius: 6px;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
  user-select: none;
}

.insert-btn {
  background: #f0f9ff;
  color: #409eff;
  border: 1px solid #b3d8ff;
}

.insert-btn:hover {
  background: #409eff;
  color: #fff;
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(64, 158, 255, 0.3);
}

.delete-btn {
  background: #fef0f0;
  color: #f56c6c;
  border: 1px solid #fbc4c4;
}

.delete-btn:hover {
  background: #f56c6c;
  color: #fff;
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(245, 108, 108, 0.3);
}

.deadline-display {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-top: 12px;
  padding: 8px 12px;
  background: #f5f7fa;
  border-radius: 6px;
  font-size: 13px;
  color: #606266;
}

/* Files & Repo 样式 */
.repo-section,
.attachments-section {
  padding: 10px 0;
}

.attachments-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.attachments-toolbar {
  display: flex;
  gap: 10px;
}

.file-manager-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding: 12px;
  background: #f5f7fa;
  border-radius: 4px;
}

.toolbar-right {
  display: flex;
  align-items: center;
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
  margin-bottom: 20px;
}

.folder-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 24px 20px;
  border: 2px solid #e4e7ed;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
  position: relative;
  overflow: hidden;
}

.folder-item::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: transparent;
  transition: background 0.3s;
}

.folder-item:hover {
  border-color: #409eff;
  background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
  transform: translateY(-3px);
  box-shadow: 0 6px 20px rgba(64, 158, 255, 0.2);
}

.folder-item:hover::before {
  background: linear-gradient(90deg, #409eff 0%, #66b1ff 100%);
}

.folder-item.active {
  border-color: #409eff;
  background: linear-gradient(135deg, #ecf5ff 0%, #d9ecff 100%);
  box-shadow: 0 4px 16px rgba(64, 158, 255, 0.25);
}

.folder-item.active::before {
  background: linear-gradient(90deg, #409eff 0%, #66b1ff 100%);
}

.folder-item.default-folder {
  border-color: #67c23a;
  background: linear-gradient(135deg, #f0f9ff 0%, #e8f5e9 100%);
}

.folder-item.default-folder:hover {
  border-color: #67c23a;
  background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%);
}

.folder-item.default-folder.active {
  border-color: #67c23a;
  background: linear-gradient(135deg, #c8e6c9 0%, #a5d6a7 100%);
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

.folder-delete-btn {
  position: absolute;
  top: 8px;
  right: 8px;
  opacity: 0;
  transition: opacity 0.2s;
}

.folder-item:hover .folder-delete-btn {
  opacity: 1;
}

.folder-icon {
  font-size: 52px;
  color: #409eff;
  margin-bottom: 12px;
  transition: transform 0.3s;
}

.folder-item:hover .folder-icon {
  transform: scale(1.1);
  color: #66b1ff;
}

.folder-name {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 6px;
  text-align: center;
  word-break: break-word;
  line-height: 1.4;
}

.folder-count {
  font-size: 12px;
  color: #909399;
}

/* 右键菜单样式 */
.context-menu {
  position: fixed;
  background: #fff;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  z-index: 9999;
  min-width: 160px;
  padding: 4px 0;
}

.context-menu-item {
  display: flex;
  align-items: center;
  padding: 8px 16px;
  cursor: pointer;
  font-size: 14px;
  color: #606266;
  transition: background-color 0.2s;
}

.context-menu-item:hover {
  background-color: #f5f7fa;
}

.context-menu-item.danger {
  color: #f56c6c;
}

.context-menu-item.danger:hover {
  background-color: #fef0f0;
}

.context-menu-item .el-icon {
  margin-right: 8px;
  font-size: 16px;
}

.context-menu-divider {
  height: 1px;
  background-color: #e4e7ed;
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
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  z-index: 10000;
  min-width: 180px;
  padding: 6px 0;
  backdrop-filter: blur(10px);
}

.files-in-folder {
  margin-top: 20px;
}

.folder-files-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid #e4e7ed;
}

.folder-files-header span {
  font-size: 16px;
  font-weight: 500;
  color: #303133;
}

.repo-section h4 {
  margin: 0 0 15px 0;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  display: flex;
  align-items: center;
  gap: 8px;
}

.github-url {
  display: flex;
  align-items: center;
  padding: 15px;
  background-color: #f5f7fa;
  border-radius: 4px;
}

.no-github,
.no-attachments {
  padding: 20px 0;
}

.attachments-list {
  max-height: 500px;
  overflow-y: auto;
  padding: 4px;
  margin-top: 12px;
}

.attachments-list::-webkit-scrollbar {
  width: 6px;
}

.attachments-list::-webkit-scrollbar-track {
  background: #f5f7fa;
  border-radius: 3px;
}

.attachments-list::-webkit-scrollbar-thumb {
  background: #c0c4cc;
  border-radius: 3px;
}

.attachments-list::-webkit-scrollbar-thumb:hover {
  background: #909399;
}

.attachment-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px 16px;
  margin-bottom: 8px;
  background-color: #ffffff;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  cursor: pointer;
  position: relative;
  overflow: hidden;
}

.attachment-item::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 3px;
  background: transparent;
  transition: background 0.3s;
}

.attachment-item:hover {
  background-color: #f0f9ff;
  border-color: #409eff;
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.15);
  transform: translateX(4px);
}

.attachment-item:hover::before {
  background: #409eff;
}

.attachment-info {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
  min-width: 0;
}

.file-icon {
  font-size: 28px;
  color: #409eff;
  flex-shrink: 0;
  transition: transform 0.3s;
}

.attachment-item:hover .file-icon {
  transform: scale(1.1);
  color: #66b1ff;
}

.file-details {
  flex: 1;
  min-width: 0;
}

.file-name {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 6px;
  word-break: break-word;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.file-meta {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 12px;
  color: #909399;
}

.file-date {
  white-space: nowrap;
}

.attachment-actions {
  display: flex;
  gap: 6px;
  flex-shrink: 0;
  z-index: 10;
  position: relative;
  opacity: 0.7;
  transition: opacity 0.3s;
}

.attachment-item:hover .attachment-actions {
  opacity: 1;
}

/* 文件预览对话框样式 */
.file-preview-dialog {
  max-width: 95vw;
}

.file-preview-dialog :deep(.el-dialog__body) {
  padding: 20px;
}

.preview-container {
  min-height: 400px;
  max-height: 75vh;
  overflow: auto;
}

.preview-image {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 400px;
}

.preview-image img {
  max-width: 100%;
  max-height: 75vh;
  object-fit: contain;
}

.preview-pdf {
  width: 100%;
  height: 75vh;
}

.preview-pdf iframe {
  width: 100%;
  height: 100%;
  border: none;
}

.preview-text {
  width: 100%;
  max-height: 75vh;
  overflow: auto;
  background: #f5f7fa;
  padding: 20px;
  border-radius: 4px;
}

.text-content {
  margin: 0;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', 'Consolas', 'source-code-pro', monospace;
  font-size: 14px;
  line-height: 1.6;
  color: #303133;
  white-space: pre-wrap;
  word-wrap: break-word;
}

.loading-text {
  text-align: center;
  color: #909399;
  padding: 40px;
}

.preview-video {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 400px;
}

.preview-audio {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 40px;
}

.preview-other {
  width: 100%;
  min-height: 400px;
}

.preview-office {
  width: 100%;
  max-height: 75vh;
  overflow: auto;
  background: #ffffff;
  padding: 20px;
  border-radius: 4px;
}

.office-content {
  width: 100%;
}

/* Word文档预览样式 */
.office-content :deep(p) {
  margin: 8px 0;
  line-height: 1.6;
}

.office-content :deep(h1) {
  font-size: 24px;
  font-weight: 600;
  margin: 16px 0 8px 0;
}

.office-content :deep(h2) {
  font-size: 20px;
  font-weight: 600;
  margin: 14px 0 6px 0;
}

.office-content :deep(h3) {
  font-size: 18px;
  font-weight: 600;
  margin: 12px 0 4px 0;
}

.office-content :deep(table) {
  border-collapse: collapse;
  width: 100%;
  margin: 12px 0;
}

.office-content :deep(table td),
.office-content :deep(table th) {
  border: 1px solid #ddd;
  padding: 8px;
  text-align: left;
}

.office-content :deep(table th) {
  background-color: #f5f7fa;
  font-weight: 600;
}

/* Excel预览样式 */
.excel-preview {
  width: 100%;
  overflow-x: auto;
}

.excel-sheet {
  margin-bottom: 30px;
}

.excel-sheet h3 {
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 12px;
  color: #303133;
  padding-bottom: 8px;
  border-bottom: 2px solid #409eff;
}

.excel-sheet :deep(table) {
  border-collapse: collapse;
  width: 100%;
  font-size: 13px;
}

.excel-sheet :deep(table td),
.excel-sheet :deep(table th) {
  border: 1px solid #e4e7ed;
  padding: 6px 10px;
  text-align: left;
  background-color: #ffffff;
}

.excel-sheet :deep(table th) {
  background-color: #f5f7fa;
  font-weight: 600;
  color: #303133;
}

.excel-sheet :deep(table tr:nth-child(even) td) {
  background-color: #fafafa;
}

.excel-sheet :deep(table tr:hover td) {
  background-color: #f0f9ff;
}

.loading-text {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  color: #909399;
  font-size: 14px;
}

.unsupported-preview {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 400px;
}

.preview-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

/* 移动端样式 */
@media (max-width: 768px) {
  .card-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .main-content-row {
    margin-bottom: 0;
  }

  .steps-card,
  .logs-card {
    margin-bottom: 20px;
  }

  .logs-card {
    position: static;
    max-height: none;
  }

  .project-logs-timeline {
    max-height: none;
  }

  .timeline-wrapper {
    padding-left: 20px;
  }

  .timeline-node {
    left: -20px;
    width: 24px;
    height: 24px;
  }

  .timeline-line {
    left: -12px;
  }

  .step-title-row {
    flex-direction: column;
    align-items: flex-start;
  }

  .details-grid {
    grid-template-columns: 1fr;
  }

  .step-actions {
    flex-direction: column;
  }

  .action-btn {
    width: 100%;
    justify-content: center;
  }

  .attachment-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }

  .attachment-actions {
    width: 100%;
    justify-content: flex-end;
  }

  .log-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .log-detail-item {
    flex-direction: column;
    align-items: flex-start;
  }
}

/* 项目日志时间线样式 - 黑白极简风格 */
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
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell', sans-serif;
}

.log-time {
  font-size: 11px;
  color: #666;
  font-weight: 400;
  letter-spacing: 0.01em;
}

.log-user {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 11px;
  color: #666;
  font-weight: 400;
}

.log-user .el-icon {
  font-size: 12px;
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
  font-weight: 400;
  letter-spacing: 0.01em;
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

.log-detail-item:last-child {
  margin-bottom: 0;
}

.detail-label {
  font-size: 11px;
  color: #666;
  font-weight: 500;
  flex-shrink: 0;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.completion-note {
  flex: 1;
  font-size: 12px;
  color: #333;
  line-height: 1.7;
  padding: 10px 0;
  background: transparent;
  border-radius: 0;
  white-space: pre-wrap;
  word-break: break-word;
  border-left: 2px solid #000;
  padding-left: 12px;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell', sans-serif;
}

.markdown-content {
  white-space: normal;
}

.markdown-content :deep(h1),
.markdown-content :deep(h2),
.markdown-content :deep(h3) {
  font-weight: 600;
  margin: 8px 0 4px 0;
  color: #000;
}

.markdown-content :deep(strong) {
  font-weight: 600;
  color: #000;
}

.markdown-content :deep(em) {
  font-style: italic;
}

.markdown-content :deep(code) {
  background: #f3f4f6;
  padding: 2px 4px;
  border-radius: 2px;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', 'Consolas', monospace;
  font-size: 11px;
}

.markdown-content :deep(pre) {
  background: #f3f4f6;
  padding: 8px;
  border-radius: 4px;
  overflow-x: auto;
  margin: 8px 0;
}

.markdown-content :deep(pre code) {
  background: transparent;
  padding: 0;
}

.markdown-content :deep(ul) {
  margin: 6px 0;
  padding-left: 20px;
}

.markdown-content :deep(li) {
  margin: 2px 0;
}

.markdown-content :deep(a) {
  color: #000;
  text-decoration: underline;
}

/* 照片九宫格样式 */
.photo-grid {
  display: grid;
  gap: 6px;
  margin-top: 8px;
  margin-bottom: 8px;
  max-width: 100%;
}

.photo-grid-1 {
  grid-template-columns: 1fr;
  max-width: 200px;
}

.photo-grid-2 {
  grid-template-columns: repeat(2, 1fr);
  max-width: 400px;
}

.photo-grid-3,
.photo-grid-4,
.photo-grid-5,
.photo-grid-6,
.photo-grid-7,
.photo-grid-8,
.photo-grid-9 {
  grid-template-columns: repeat(3, 1fr);
  max-width: 600px;
}

.photo-item {
  position: relative;
  width: 100%;
  aspect-ratio: 1;
  background: #f5f7fa;
  border-radius: 4px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s;
  border: 1px solid #e5e7eb;
}

.photo-item:hover {
  transform: scale(1.02);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.photo-item img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.photo-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s;
  opacity: 0;
}

.photo-item:hover .photo-overlay {
  background: rgba(0, 0, 0, 0.4);
  opacity: 1;
}

.photo-overlay .el-icon {
  color: #fff;
  font-size: 24px;
}

/* 文件列表样式 */
.file-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.file-list-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  background: #f9fafb;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
}

.file-list-item:hover {
  background: #f3f4f6;
  border-color: #d1d5db;
}

.file-list-item .file-icon {
  font-size: 18px;
  color: #409eff;
  flex-shrink: 0;
}

.file-list-item .file-name {
  flex: 1;
  font-size: 13px;
  color: #111827;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.empty-logs {
  padding: 60px 0;
  text-align: center;
}

.empty-logs :deep(.el-empty__description) {
  color: #666;
  font-size: 13px;
}

/* 新建文件夹选项样式 */
:deep(.create-folder-option) {
  background-color: #f0f9ff !important;
  color: #409eff !important;
  font-weight: 500;
}

:deep(.create-folder-option:hover) {
  background-color: #e0f2fe !important;
}

.template-selector {
  padding: 10px 0;
}

.template-option {
  padding: 8px 0;
}

.template-option-name {
  display: flex;
  align-items: center;
  font-weight: 600;
  color: #303133;
  margin-bottom: 4px;
}

.template-option-desc {
  font-size: 12px;
  color: #909399;
  margin-bottom: 4px;
  line-height: 1.5;
}

.template-option-steps {
  font-size: 12px;
  color: #606266;
}

.template-preview {
  margin-top: 20px;
  padding: 16px;
  background: #f5f7fa;
  border-radius: 6px;
}

.preview-title {
  font-weight: 600;
  color: #303133;
  margin-bottom: 12px;
}

.preview-steps {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

/* 移动端样式 */
@media (max-width: 768px) {
  .project-logs-timeline {
    padding-left: 20px;
  }

  .log-node {
    left: -20px;
    width: 24px;
    height: 24px;
    font-size: 14px;
  }

  .log-line {
    left: -12px;
  }

  .log-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .log-detail-item {
    flex-direction: column;
    align-items: flex-start;
  }
}

/* 元器件清单样式 */
.parts-card {
  margin-top: 20px;
  
  .el-card__header {
    background: linear-gradient(135deg, #f5f7fa 0%, #e9ecef 100%);
    border-bottom: 2px solid #e4e7ed;
    
    .card-header {
      font-weight: 600;
      color: #303133;
    }
  }
}

.parts-table {
  margin-top: 16px;
  
  :deep(.el-table) {
    border-radius: 8px;
    overflow: hidden;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
    
    .el-table__header-wrapper {
      .el-table__header {
        th {
          background: linear-gradient(135deg, #f5f7fa 0%, #e9ecef 100%);
          color: #303133;
          font-weight: 600;
          padding: 14px 12px;
          border-bottom: 2px solid #dcdfe6;
        }
      }
    }
    
    .el-table__body-wrapper {
      .el-table__body {
        tr {
          transition: all 0.2s;
          
          &:hover {
            background-color: #f5f9ff;
            transform: scale(1.001);
          }
          
          td {
            padding: 16px 12px;
            border-bottom: 1px solid #f0f0f0;
          }
        }
      }
    }
  }
  
  :deep(.subtotal-text) {
    font-weight: 600;
    color: #409eff;
    font-size: 15px;
  }
}

.part-image-cell {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 8px;
  height: 100%;
}

.part-image {
  width: 80px !important;
  height: 80px !important;
  min-width: 80px;
  min-height: 80px;
  max-width: 80px;
  max-height: 80px;
  border-radius: 8px;
  cursor: pointer;
  object-fit: cover;
  border: 2px solid #e4e7ed;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.08);
  display: block;
}

.part-image:hover {
  border-color: #409eff;
  transform: scale(1.08);
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.3);
}

.parts-table :deep(.el-image) {
  width: 80px !important;
  height: 80px !important;
  
  .el-image__inner {
    width: 80px !important;
    height: 80px !important;
    object-fit: cover;
  }
}

.part-image-placeholder {
  width: 80px !important;
  height: 80px !important;
  min-width: 80px;
  min-height: 80px;
  max-width: 80px;
  max-height: 80px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  background: linear-gradient(135deg, #f5f7fa 0%, #e9ecef 100%);
  border: 2px dashed #c0c4cc;
  border-radius: 8px;
  color: #909399;
  font-size: 12px;
  gap: 4px;
  transition: all 0.3s;
  
  .el-icon {
    font-size: 24px;
  }
  
  .placeholder-text {
    font-size: 11px;
    line-height: 1;
  }
  
  &:hover {
    border-color: #409eff;
    color: #409eff;
    background: linear-gradient(135deg, #ecf5ff 0%, #d9ecff 100%);
  }
}

/* 操作按钮样式 */
.parts-action-buttons {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  
  .action-btn-edit {
    width: 32px;
    height: 32px;
    padding: 0;
    background: linear-gradient(135deg, #409eff 0%, #66b1ff 100%);
    border: none;
    box-shadow: 0 2px 6px rgba(64, 158, 255, 0.3);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    
    &:hover {
      background: linear-gradient(135deg, #66b1ff 0%, #85c1ff 100%);
      transform: translateY(-2px) scale(1.1);
      box-shadow: 0 4px 12px rgba(64, 158, 255, 0.4);
    }
    
    &:active {
      transform: translateY(0) scale(1.05);
    }
    
    .el-icon {
      font-size: 16px;
      color: #fff;
    }
  }
  
  .action-btn-delete {
    width: 32px;
    height: 32px;
    padding: 0;
    background: linear-gradient(135deg, #f56c6c 0%, #f78989 100%);
    border: none;
    box-shadow: 0 2px 6px rgba(245, 108, 108, 0.3);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    
    &:hover {
      background: linear-gradient(135deg, #f78989 0%, #f9a5a5 100%);
      transform: translateY(-2px) scale(1.1);
      box-shadow: 0 4px 12px rgba(245, 108, 108, 0.4);
    }
    
    &:active {
      transform: translateY(0) scale(1.05);
    }
    
    .el-icon {
      font-size: 16px;
      color: #fff;
    }
  }
}

.part-image-placeholder .placeholder-text {
  font-size: 10px;
  color: #909399;
}

.part-expand {
  padding: 16px;
  background-color: #fafafa;
}

.part-expand-row {
  display: flex;
  margin-bottom: 12px;
  align-items: flex-start;
}

.part-expand-row:last-child {
  margin-bottom: 0;
}

.part-expand-row .label {
  font-weight: 600;
  color: #606266;
  min-width: 100px;
  margin-right: 12px;
}

.part-expand-row .value {
  flex: 1;
  color: #303133;
  word-break: break-all;
}

.part-expand-row .value a {
  color: #409eff;
  text-decoration: none;
}

.part-expand-row .value a:hover {
  text-decoration: underline;
}

.subtotal-text {
  font-weight: 600;
  color: #409eff;
}

.parts-summary {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 20px;
  padding: 20px 24px;
  background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%);
  border-radius: 8px;
  border: 1px solid #e4e7ed;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  
  .summary-item {
    display: flex;
    align-items: center;
    gap: 8px;
    
    .summary-label {
      font-size: 14px;
      color: #606266;
      font-weight: 500;
    }
    
    .summary-value {
      font-size: 16px;
      color: #303133;
      font-weight: 600;
    }
    
    .total-price {
      font-weight: 700;
      font-size: 20px;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      background-clip: text;
    }
  }
}

/* 元器件编辑对话框样式 */
.parts-edit-dialog {
  .el-dialog {
    max-width: 95vw;
    margin: 3vh auto;
    border-radius: 8px;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12);
  }
  
  .el-dialog__header {
    padding: 20px 24px;
    border-bottom: 1px solid #ebeef5;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 8px 8px 0 0;
    
    .el-dialog__title {
      color: #fff;
      font-weight: 600;
      font-size: 18px;
    }
    
    .el-dialog__headerbtn {
      .el-dialog__close {
        color: #fff;
        font-size: 20px;
        
        &:hover {
          color: #f0f0f0;
        }
      }
    }
  }
  
  .el-dialog__body {
    padding: 24px;
    max-height: calc(90vh - 140px);
    overflow: hidden;
    display: flex;
    flex-direction: column;
    background: #fafbfc;
  }
  
  .el-dialog__footer {
    padding: 16px 24px;
    border-top: 1px solid #ebeef5;
    background: #fff;
    border-radius: 0 0 8px 8px;
  }
}

.parts-edit-content {
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow: hidden;
  gap: 16px;
}

.parts-edit-tips {
  flex-shrink: 0;
  
  .modern-alert {
    border-radius: 6px;
    border: none;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
    
    .alert-content {
      display: flex;
      align-items: center;
      gap: 8px;
      
      .alert-icon {
        font-size: 18px;
        color: #409eff;
      }
      
      .required-hint {
        color: #f56c6c;
        font-weight: 600;
      }
    }
  }
}

.validation-errors {
  flex-shrink: 0;
  
  .el-alert {
    border-radius: 6px;
    border: 1px solid #fde2e2;
    background: #fef0f0;
  }
}

.parts-table-wrapper {
  flex: 1;
  overflow: hidden;
  min-height: 0;
  display: flex;
  flex-direction: column;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  padding: 8px;
}

/* 可编辑表格样式 */
.editing-parts-table {
  flex: 1;
  overflow: auto;
  border-radius: 6px;
  
  :deep(.el-table__header-wrapper) {
    .el-table__header {
      th {
        background: linear-gradient(135deg, #f5f7fa 0%, #e9ecef 100%);
        color: #303133;
        font-weight: 600;
        padding: 12px 8px;
        border-bottom: 2px solid #dcdfe6;
        
        .required-header {
          display: flex;
          align-items: center;
          gap: 4px;
          
          .required-star {
            color: #f56c6c;
            font-weight: 700;
            font-size: 14px;
          }
        }
      }
    }
  }
  
  :deep(.el-table__body-wrapper) {
    overflow-x: auto;
    overflow-y: auto;
    
    .el-table__body {
      tr {
        transition: background-color 0.2s;
        
        &:hover {
          background-color: #f5f9ff;
        }
        
        td {
          padding: 12px 8px;
          
          .cell {
            padding: 0;
          }
        }
      }
    }
  }
  
  :deep(.cell-error-column) {
    background-color: #fef0f0;
  }
  
  :deep(.cell-error .el-input__wrapper),
  :deep(.cell-error .el-input-number) {
    border-color: #f56c6c;
    box-shadow: 0 0 0 1px #f56c6c inset;
    background-color: #fff5f5;
  }
  
  :deep(.el-input),
  :deep(.el-input-number) {
    .el-input__wrapper {
      border-radius: 4px;
      transition: all 0.2s;
      
      &:hover {
        box-shadow: 0 0 0 1px #c0c4cc inset;
      }
      
      &.is-focus {
        box-shadow: 0 0 0 1px #409eff inset;
      }
    }
  }
  
  :deep(.el-textarea) {
    .el-textarea__inner {
      border-radius: 4px;
      transition: all 0.2s;
      
      &:hover {
        border-color: #c0c4cc;
      }
      
      &:focus {
        border-color: #409eff;
      }
    }
  }
}

.cell-with-error {
  display: flex;
  align-items: center;
  gap: 6px;
  width: 100%;
  padding: 4px 0;
}

.cell-with-error .el-input,
.cell-with-error .el-input-number {
  flex: 1;
}

.cell-error-icon {
  color: #f56c6c;
  font-size: 16px;
  flex-shrink: 0;
  line-height: 1;
  animation: shake 0.3s;
}

@keyframes shake {
  0%, 100% { transform: translateX(0); }
  25% { transform: translateX(-4px); }
  75% { transform: translateX(4px); }
}

/* 编辑项目对话框样式 */
.edit-project-dialog {
  animation: dialogFadeIn 0.3s ease-out;
}

.edit-project-dialog :deep(.el-dialog__header) {
  padding: 0;
  background: transparent;
}

.edit-project-dialog :deep(.el-dialog__body) {
  padding: 0;
  background: #fafbfc;
}

.edit-project-dialog .dialog-header {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 24px 24px 20px;
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  border-radius: 8px 8px 0 0;
  animation: headerSlideIn 0.4s ease-out;
}

.edit-project-dialog .header-icon-wrapper {
  width: 56px;
  height: 56px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  backdrop-filter: blur(10px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  animation: iconBounce 0.6s ease-out 0.2s both;
}

.edit-project-dialog .header-icon {
  font-size: 28px;
  color: #fff;
}

.edit-project-dialog .dialog-body {
  padding: 24px;
  max-height: calc(90vh - 200px);
  overflow-y: auto;
}

.edit-project-dialog .project-form {
  animation: formFadeIn 0.5s ease-out 0.2s both;
}

.edit-project-dialog .form-section {
  background: #fff;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 20px;
  border: 1px solid #e4e7ed;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  transition: all 0.3s ease;
  animation: sectionSlideIn 0.4s ease-out both;
}

.edit-project-dialog .form-section:nth-child(1) { animation-delay: 0.1s; }
.edit-project-dialog .form-section:nth-child(2) { animation-delay: 0.2s; }
.edit-project-dialog .form-section:nth-child(3) { animation-delay: 0.3s; }
.edit-project-dialog .form-section:nth-child(4) { animation-delay: 0.4s; }

.edit-project-dialog .form-section:hover {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
  transform: translateY(-2px);
}

.edit-project-dialog .section-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 20px;
  padding-bottom: 12px;
  border-bottom: 2px solid #f0f2f5;
}

.edit-project-dialog .section-icon {
  font-size: 20px;
  color: #f5576c;
}

.edit-project-dialog .section-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  flex: 1;
}

.edit-project-dialog .form-row {
  display: flex;
  gap: 16px;
}

.edit-project-dialog .form-item-half {
  flex: 1;
}

.edit-project-dialog :deep(.el-form-item__label) {
  font-weight: 500;
  color: #303133;
  font-size: 14px;
}

.edit-project-dialog :deep(.el-input__wrapper) {
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
}

.edit-project-dialog :deep(.el-input__wrapper:hover) {
  box-shadow: 0 2px 8px rgba(245, 87, 108, 0.2);
  transform: translateY(-1px);
}

.edit-project-dialog :deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 2px rgba(245, 87, 108, 0.2);
}

.edit-project-dialog :deep(.el-textarea__inner) {
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
}

.edit-project-dialog :deep(.el-textarea__inner:hover) {
  box-shadow: 0 2px 8px rgba(245, 87, 108, 0.2);
}

.edit-project-dialog :deep(.el-textarea__inner:focus) {
  box-shadow: 0 0 0 2px rgba(245, 87, 108, 0.2);
}

.edit-project-dialog .dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 20px 24px;
  background: #fff;
  border-top: 1px solid #ebeef5;
  border-radius: 0 0 8px 8px;
}

.edit-project-dialog .submit-btn {
  min-width: 120px;
  font-weight: 500;
  box-shadow: 0 2px 8px rgba(245, 87, 108, 0.3);
  transition: all 0.3s ease;
}

.edit-project-dialog .submit-btn:hover {
  box-shadow: 0 4px 12px rgba(245, 87, 108, 0.4);
  transform: translateY(-2px);
}

.edit-project-dialog .submit-btn:active {
  transform: translateY(0);
}

@keyframes dialogFadeIn {
  from {
    opacity: 0;
    transform: scale(0.95) translateY(-10px);
  }
  to {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
}

@keyframes headerSlideIn {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes iconBounce {
  0%, 100% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.1);
  }
}

@keyframes formFadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes sectionSlideIn {
  from {
    opacity: 0;
    transform: translateX(-20px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

.parts-empty {
  padding: 60px 40px;
  text-align: center;
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: #fafbfc;
  border-radius: 6px;
}

.parts-edit-actions {
  display: flex;
  gap: 12px;
  padding: 16px;
  background: linear-gradient(135deg, #f5f7fa 0%, #e9ecef 100%);
  border-radius: 8px;
  flex-wrap: wrap;
  flex-shrink: 0;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  
  .el-button {
    flex: 1;
    min-width: 140px;
    height: 40px;
    font-weight: 500;
    border-radius: 6px;
    transition: all 0.3s;
    
    &:hover {
      transform: translateY(-2px);
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    }
    
    &.el-button--primary {
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      border: none;
      
      &:hover {
        background: linear-gradient(135deg, #5568d3 0%, #6a3f8f 100%);
      }
    }
  }
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  
  .el-button {
    min-width: 100px;
    height: 36px;
    border-radius: 6px;
    font-weight: 500;
    transition: all 0.3s;
    
    &:hover {
      transform: translateY(-1px);
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.12);
    }
  }
}

.error-list {
  margin: 8px 0 0 0;
  padding-left: 24px;
  color: #f56c6c;
  max-height: 150px;
  overflow-y: auto;
  list-style: none;
  
  &::-webkit-scrollbar {
    width: 6px;
  }
  
  &::-webkit-scrollbar-track {
    background: #f5f5f5;
    border-radius: 3px;
  }
  
  &::-webkit-scrollbar-thumb {
    background: #dcdfe6;
    border-radius: 3px;
    
    &:hover {
      background: #c0c4cc;
    }
  }
  
  li {
    margin: 6px 0;
    font-size: 13px;
    line-height: 1.6;
    position: relative;
    
    &::before {
      content: '•';
      position: absolute;
      left: -16px;
      color: #f56c6c;
      font-weight: bold;
    }
  }
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

/* 项目标签卡片样式 */
/* 编辑对话框中的标签部分样式 */
.tags-form-section {
  background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);
  border: 1px solid #e9ecef;
  border-radius: 10px;
  padding: 20px;
  margin-bottom: 20px;
}

.tags-form-section .section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 2px solid #e9ecef;
}

.tags-form-section .manage-tags-btn {
  color: #409eff;
  font-size: 12px;
  padding: 4px 8px;
  border-radius: 4px;
  transition: all 0.3s;
}

.tags-form-section .manage-tags-btn:hover {
  background-color: #ecf5ff;
  color: #66b1ff;
}

.tag-selector-wrapper {
  background: #fff;
  border-radius: 8px;
  padding: 16px;
  border: 1px solid #e4e7ed;
  transition: all 0.3s;
}

.tag-selector-wrapper:hover {
  border-color: #409eff;
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.1);
}

.selected-tags-preview {
  margin-top: 16px;
  padding: 12px;
  background: #f5f7fa;
  border-radius: 8px;
  border: 1px dashed #d3d4d6;
}

.preview-label {
  font-size: 12px;
  color: #606266;
  margin-bottom: 8px;
  font-weight: 500;
}

.preview-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.preview-tag {
  font-size: 12px;
  padding: 4px 10px;
  border-radius: 12px;
  transition: all 0.3s;
}

.preview-tag:hover {
  transform: scale(1.05);
}

/* 移动端适配 */
@media (max-width: 768px) {
  .tags-form-section .section-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
}
</style>

