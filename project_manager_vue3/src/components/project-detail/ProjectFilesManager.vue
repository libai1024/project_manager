<template>
  <el-card class="files-card">
    <template #header>
      <div class="card-header">
        <span>文件管理</span>
        <el-button type="primary" @click="$emit('upload')">
          <el-icon><Upload /></el-icon>
          上传文件
        </el-button>
      </div>
    </template>

    <el-row :gutter="20">
      <!-- 附件列表 -->
      <el-col :xs="24" :md="12">
        <div class="attachments-section">
          <div class="attachments-header">
            <h4>
              <el-icon><Document /></el-icon>
              项目附件
            </h4>
            <div class="attachments-toolbar">
              <el-button type="primary" size="small" @click="$emit('upload')">
                <el-icon><Plus /></el-icon>
                上传文件
              </el-button>
              <el-button size="small" @click="$emit('create-folder')">
                <el-icon><FolderAdd /></el-icon>
                新建文件夹
              </el-button>
            </div>
          </div>
          
          <!-- 文件管理器工具栏 -->
          <div class="file-manager-toolbar">
            <el-radio-group :model-value="viewMode" @update:model-value="$emit('update:view-mode', $event)" size="small">
              <el-radio-button value="folder">
                <el-icon><Folder /></el-icon>
                文件夹
              </el-radio-button>
              <el-radio-button value="list">
                <el-icon><List /></el-icon>
                全部文件
              </el-radio-button>
            </el-radio-group>
            
            <div class="toolbar-right">
              <el-input
                :model-value="searchKeyword"
                @update:model-value="$emit('update:search-keyword', $event)"
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
                :model-value="sortBy" 
                @update:model-value="$emit('update:sort-by', $event)"
                size="small" 
                style="width: 120px; margin-right: 10px;"
              >
                <el-option label="名称" value="name" />
                <el-option label="类型" value="type" />
                <el-option label="时间" value="time" />
              </el-select>
              
              <el-select 
                :model-value="filterType" 
                @update:model-value="$emit('update:filter-type', $event)"
                size="small" 
                clearable 
                placeholder="文件类型筛选" 
                style="width: 150px;"
              >
                <el-option
                  v-for="ext in fileExtensions"
                  :key="ext"
                  :label="ext.toUpperCase()"
                  :value="ext"
                />
              </el-select>
            </div>
          </div>
          
          <!-- 文件夹视图 -->
          <div v-if="viewMode === 'folder'" class="folder-view">
            <div class="folders-grid">
              <div
                v-for="folder in folders"
                :key="folder.id"
                class="folder-item"
                @click="$emit('select-folder', folder.id)"
                :class="{ 
                  active: selectedFolderId === folder.id,
                  'default-folder': isDefaultFolder(folder.name)
                }"
              >
                <el-icon class="folder-icon"><Folder /></el-icon>
                <div class="folder-name">{{ folder.name }}</div>
                <div class="folder-count">
                  {{ folder.attachment_count || 0 }} 个文件
                </div>
                <el-icon v-if="isDefaultFolder(folder.name)" class="lock-icon">
                  <Lock />
                </el-icon>
                <el-button
                  v-if="!isDefaultFolder(folder.name) && !folder.is_default"
                  size="small"
                  type="danger"
                  text
                  class="folder-delete-btn"
                  @click.stop="$emit('delete-folder', folder)"
                >
                  <el-icon><Delete /></el-icon>
                </el-button>
              </div>
            </div>
            
            <div class="files-in-folder">
              <div v-if="selectedFolderId" class="folder-files">
                <div class="folder-files-header">
                  <span>{{ getFolderName(selectedFolderId) }} 中的文件</span>
                  <el-button size="small" text @click="$emit('select-folder', null)">
                    <el-icon><ArrowLeft /></el-icon>
                    返回
                  </el-button>
                </div>
                <div v-if="folderFiles.length > 0" class="attachments-list">
                  <div
                    v-for="attachment in folderFiles"
                    :key="attachment.id"
                    class="attachment-item"
                    @click="$emit('preview', attachment)"
                    @contextmenu.prevent="$emit('right-click', $event, attachment)"
                  >
                    <div class="attachment-info">
                      <FileTypeIcon :file-name="attachment.file_name" size="medium" />
                      <div class="file-details">
                        <div class="file-name">{{ attachment.file_name }}</div>
                        <div class="file-meta">
                          <el-tag size="small" type="info">{{ attachment.file_type }}</el-tag>
                          <span class="file-date">{{ new Date(attachment.created_at).toLocaleDateString() }}</span>
                        </div>
                      </div>
                    </div>
                    <div class="attachment-actions" @click.stop>
                      <el-button size="small" type="primary" link @click.stop="$emit('preview', attachment)">
                        <el-icon><View /></el-icon>预览
                      </el-button>
                      <el-button size="small" type="primary" link @click.stop="$emit('download', attachment)">
                        <el-icon><Download /></el-icon>下载
                      </el-button>
                      <el-button size="small" type="danger" link @click.stop="$emit('delete', attachment)">
                        <el-icon><Delete /></el-icon>删除
                      </el-button>
                    </div>
                  </div>
                </div>
                <el-empty v-else description="该文件夹暂无文件" :image-size="60" />
              </div>
              <el-empty v-else description="请选择一个文件夹查看文件" :image-size="80" />
            </div>
          </div>
          
          <!-- 列表视图 -->
          <div v-else class="list-view">
            <div v-if="filteredAttachments.length > 0" class="attachments-list">
              <div
                v-for="attachment in filteredAttachments"
                :key="attachment.id"
                class="attachment-item"
                @click="$emit('preview', attachment)"
                @contextmenu.prevent="$emit('right-click', $event, attachment)"
              >
                <div class="attachment-info">
                  <FileTypeIcon :file-name="attachment.file_name" size="medium" />
                  <div class="file-details">
                    <div class="file-name">{{ attachment.file_name }}</div>
                    <div class="file-meta">
                      <el-tag size="small" type="info">{{ attachment.file_type }}</el-tag>
                      <el-tag v-if="attachment.folder_name" size="small" type="success" style="margin-left: 5px;">
                        {{ attachment.folder_name }}
                      </el-tag>
                      <span class="file-date">{{ new Date(attachment.created_at).toLocaleDateString() }}</span>
                    </div>
                  </div>
                </div>
                <div class="attachment-actions" @click.stop>
                  <el-button size="small" type="primary" link @click.stop="$emit('preview', attachment)">
                    <el-icon><View /></el-icon>预览
                  </el-button>
                  <el-button size="small" type="primary" link @click.stop="$emit('download', attachment)">
                    <el-icon><Download /></el-icon>下载
                  </el-button>
                  <el-button size="small" type="danger" link @click.stop="$emit('delete', attachment)">
                    <el-icon><Delete /></el-icon>删除
                  </el-button>
                </div>
              </div>
            </div>
            <el-empty v-else description="暂无附件" :image-size="80">
              <el-button type="primary" @click="$emit('upload')">上传文件</el-button>
            </el-empty>
          </div>
        </div>
      </el-col>
    </el-row>
  </el-card>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { Upload, Document, Plus, FolderAdd, Folder, List, Search, Lock, Delete, ArrowLeft, View, Download } from '@element-plus/icons-vue'
import type { Attachment } from '@/api/attachment'
import type { Folder as AttachmentFolder } from '@/api/attachment'
import FileTypeIcon from '@/components/FileTypeIcon.vue'

interface Props {
  attachments: Attachment[]
  folders: AttachmentFolder[]
  viewMode: 'folder' | 'list'
  searchKeyword: string
  sortBy: 'name' | 'type' | 'time'
  filterType: string
  selectedFolderId: number | null
  fileExtensions: string[]
}

const props = defineProps<Props>()

defineEmits<{
  'update:view-mode': [value: 'folder' | 'list']
  'update:search-keyword': [value: string]
  'update:sort-by': [value: 'name' | 'type' | 'time']
  'update:filter-type': [value: string]
  'select-folder': [folderId: number | null]
  'delete-folder': [folder: AttachmentFolder]
  'upload': []
  'create-folder': []
  'preview': [attachment: Attachment]
  'download': [attachment: Attachment]
  'delete': [attachment: Attachment]
  'right-click': [event: MouseEvent, attachment: Attachment]
}>()

// 判断是否为默认文件夹
const isDefaultFolder = (folderName: string): boolean => {
  return ['项目需求', '项目交付', '其他'].includes(folderName)
}

// 获取文件夹名称
const getFolderName = (folderId: number | null): string => {
  if (!folderId) return ''
  const folder = props.folders.find(f => f.id === folderId)
  return folder?.name || ''
}

// 获取文件扩展名
const getFileExtension = (filename: string): string => {
  const parts = filename.split('.')
  return parts.length > 1 ? '.' + parts[parts.length - 1].toLowerCase() : ''
}

// 应用筛选和排序
const applyFiltersAndSort = (files: Attachment[]): Attachment[] => {
  let result = [...files]
  
  // 搜索筛选
  if (props.searchKeyword) {
    const keyword = props.searchKeyword.toLowerCase()
    result = result.filter(f => f.file_name.toLowerCase().includes(keyword))
  }
  
  // 文件扩展名筛选
  if (props.filterType) {
    result = result.filter(f => {
      const ext = getFileExtension(f.file_name)
      return ext === props.filterType
    })
  }
  
  // 排序
  result.sort((a, b) => {
    switch (props.sortBy) {
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

// 获取文件夹中的文件（已过滤和排序）
const folderFiles = computed(() => {
  if (!props.selectedFolderId) return []
  if (!props.attachments || !Array.isArray(props.attachments)) return []
  
  let files: Attachment[] = []
  // 如果是"其他"文件夹，显示所有没有 folder_id 或 folder_id 为 null 的文件
  const otherFolder = props.folders.find(f => f.name === '其他' && f.id === props.selectedFolderId)
  if (otherFolder) {
    files = props.attachments.filter(a => !a.folder_id || a.folder_id === props.selectedFolderId)
  } else {
    files = props.attachments.filter(a => a.folder_id === props.selectedFolderId)
  }
  
  return applyFiltersAndSort(files)
})

// 获取过滤后的附件列表（已过滤和排序）
const filteredAttachments = computed(() => {
  if (!props.attachments || !Array.isArray(props.attachments)) return []
  return applyFiltersAndSort(props.attachments)
})
</script>

<style scoped>
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

.attachments-section {
  padding: 10px 0;
}

.attachments-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.attachments-header h4 {
  margin: 0;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 600;
}

.attachments-toolbar {
  display: flex;
  gap: 8px;
}

.file-manager-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding: 12px;
  background: #f5f7fa;
  border-radius: 6px;
  flex-wrap: wrap;
  gap: 12px;
}

.toolbar-right {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.folder-view {
  min-height: 300px;
}

.folders-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 12px;
  margin-bottom: 20px;
}

.folder-item {
  position: relative;
  padding: 16px;
  border: 2px solid #e4e7ed;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
  background: #fff;
  text-align: center;
}

.folder-item:hover {
  border-color: #409eff;
  box-shadow: 0 2px 12px rgba(64, 158, 255, 0.2);
  transform: translateY(-2px);
}

.folder-item.active {
  border-color: #409eff;
  background: #ecf5ff;
}

.folder-item.default-folder {
  background: #f5f7fa;
}

.folder-icon {
  font-size: 32px;
  color: #409eff;
  margin-bottom: 8px;
}

.folder-name {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 4px;
  word-break: break-word;
}

.folder-count {
  font-size: 12px;
  color: #909399;
}

.lock-icon {
  position: absolute;
  top: 8px;
  right: 8px;
  color: #909399;
  font-size: 14px;
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

.files-in-folder {
  margin-top: 20px;
}

.folder-files-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 1px solid #ebeef5;
}

.attachments-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.attachment-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  border: 1px solid #ebeef5;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
  background: #fff;
}

.attachment-item:hover {
  border-color: #409eff;
  background: #f5f7fa;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.attachment-info {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
  min-width: 0;
}

.file-details {
  flex: 1;
  min-width: 0;
}

.file-name {
  font-size: 14px;
  font-weight: 500;
  color: #303133;
  margin-bottom: 4px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.file-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.file-date {
  font-size: 12px;
  color: #909399;
}

.attachment-actions {
  display: flex;
  gap: 4px;
  flex-shrink: 0;
}

.list-view {
  min-height: 300px;
}

@media (max-width: 768px) {
  .file-manager-toolbar {
    flex-direction: column;
    align-items: stretch;
  }

  .toolbar-right {
    width: 100%;
    flex-wrap: wrap;
  }

  .folders-grid {
    grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
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
}
</style>

