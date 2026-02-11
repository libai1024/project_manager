/**
 * 上传辅助函数
 * 提供通用的批量上传逻辑，返回attachmentIds数组
 */
import { attachmentApi, type Attachment } from '@/api/attachment'
import { ElMessage } from 'element-plus'

export interface BatchUploadOptions {
  fileType?: string
  description?: string
  folderId?: number
  onProgress?: (progress: number, currentIndex: number, total: number) => void
}

/**
 * 批量上传文件，返回成功上传的attachment IDs
 */
export async function batchUploadFiles(
  projectId: number,
  files: File[],
  options: BatchUploadOptions = {}
): Promise<number[]> {
  if (files.length === 0) {
    return []
  }

  const { fileType = '其他', description, folderId, onProgress } = options
  const attachmentIds: number[] = []

  for (let i = 0; i < files.length; i++) {
    const file = files[i]
    try {
      const attachment = await attachmentApi.upload(
        projectId,
        file,
        fileType,
        description,
        folderId,
        (progressEvent) => {
          if (progressEvent.total && onProgress) {
            const fileProgress = Math.round((progressEvent.loaded * 100) / progressEvent.total)
            const overallProgress = Math.round((i * 100 + fileProgress) / files.length)
            onProgress(overallProgress, i + 1, files.length)
          }
        }
      )
      attachmentIds.push(attachment.id)
    } catch (error: any) {
      console.error(`上传文件 ${file.name} 失败:`, error)
      ElMessage.error(`上传文件 ${file.name} 失败: ${error.response?.data?.detail || '上传失败'}`)
      // 继续上传其他文件
    }
  }

  return attachmentIds
}



