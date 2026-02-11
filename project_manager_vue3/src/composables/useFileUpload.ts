/**
 * 通用文件上传 Composable
 * 提供统一的上传状态管理和进度追踪
 */
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { attachmentApi, type Attachment } from '@/api/attachment'

export interface UploadOptions {
  fileType?: string
  description?: string
  folderId?: number
  onProgress?: (progress: number, fileIndex: number, totalFiles: number) => void
}

export function useFileUpload() {
  const uploading = ref(false)
  const uploadProgress = ref(0)
  const currentFileIndex = ref(0)
  const totalFiles = ref(0)

  /**
   * 上传单个文件
   */
  const uploadFile = async (
    projectId: number,
    file: File,
    options: UploadOptions = {}
  ): Promise<Attachment> => {
    const { fileType = '其他', description, folderId, onProgress } = options

    return attachmentApi.upload(
      projectId,
      file,
      fileType,
      description,
      folderId,
      (progressEvent) => {
        if (progressEvent.total) {
          const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total)
          uploadProgress.value = progress
          if (onProgress) {
            onProgress(progress, 0, 1)
          }
        }
      }
    )
  }

  /**
   * 批量上传文件（使用统一配置）
   */
  const uploadMultipleFiles = async (
    projectId: number,
    files: File[],
    options: UploadOptions = {}
  ): Promise<Attachment[]> => {
    if (files.length === 0) {
      return []
    }

    uploading.value = true
    uploadProgress.value = 0
    totalFiles.value = files.length
    currentFileIndex.value = 0

    const results: Attachment[] = []
    const { fileType = '其他', description, folderId, onProgress } = options

    try {
      for (let i = 0; i < files.length; i++) {
        currentFileIndex.value = i + 1
        const file = files[i]

        try {
          const attachment = await attachmentApi.upload(
            projectId,
            file,
            fileType,
            description,
            folderId,
            (progressEvent) => {
              if (progressEvent.total) {
                // 计算总体进度：已完成文件的进度 + 当前文件的进度
                const fileProgress = Math.round((progressEvent.loaded * 100) / progressEvent.total)
                const overallProgress = Math.round(
                  (i * 100 + fileProgress) / files.length
                )
                uploadProgress.value = overallProgress
                if (onProgress) {
                  onProgress(overallProgress, i + 1, files.length)
                }
              }
            }
          )
          results.push(attachment)
        } catch (error: any) {
          console.error(`上传文件 ${file.name} 失败:`, error)
          ElMessage.error(`上传文件 ${file.name} 失败: ${error.response?.data?.detail || '上传失败'}`)
          // 继续上传其他文件，不中断
        }
      }

      return results
    } finally {
      uploading.value = false
      uploadProgress.value = 0
      currentFileIndex.value = 0
      totalFiles.value = 0
    }
  }

  /**
   * 批量上传文件（每个文件可以有不同的配置）
   */
  const uploadMultipleFilesWithOptions = async (
    projectId: number,
    files: Array<{ file: File; options?: UploadOptions }>
  ): Promise<Attachment[]> => {
    if (files.length === 0) {
      return []
    }

    uploading.value = true
    uploadProgress.value = 0
    totalFiles.value = files.length
    currentFileIndex.value = 0

    const results: Attachment[] = []

    try {
      for (let i = 0; i < files.length; i++) {
        currentFileIndex.value = i + 1
        const { file, options = {} } = files[i]
        const { fileType = '其他', description, folderId, onProgress } = options

        try {
          const attachment = await attachmentApi.upload(
            projectId,
            file,
            fileType,
            description,
            folderId,
            (progressEvent) => {
              if (progressEvent.total) {
                const fileProgress = Math.round((progressEvent.loaded * 100) / progressEvent.total)
                const overallProgress = Math.round(
                  (i * 100 + fileProgress) / files.length
                )
                uploadProgress.value = overallProgress
                if (onProgress) {
                  onProgress(overallProgress, i + 1, files.length)
                }
              }
            }
          )
          results.push(attachment)
        } catch (error: any) {
          console.error(`上传文件 ${file.name} 失败:`, error)
          ElMessage.error(`上传文件 ${file.name} 失败: ${error.response?.data?.detail || '上传失败'}`)
        }
      }

      return results
    } finally {
      uploading.value = false
      uploadProgress.value = 0
      currentFileIndex.value = 0
      totalFiles.value = 0
    }
  }

  /**
   * 重置上传状态
   */
  const resetUploadState = () => {
    uploading.value = false
    uploadProgress.value = 0
    currentFileIndex.value = 0
    totalFiles.value = 0
  }

  return {
    uploading,
    uploadProgress,
    currentFileIndex,
    totalFiles,
    uploadFile,
    uploadMultipleFiles,
    uploadMultipleFilesWithOptions,
    resetUploadState,
  }
}

