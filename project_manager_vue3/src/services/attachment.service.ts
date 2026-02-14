/**
 * 附件服务层
 * 处理附件相关的业务逻辑
 */
import { attachmentApi, type Attachment, type AttachmentUpdate } from '@/api/attachment'
import { ElMessage } from 'element-plus'

export class AttachmentService {
  /**
   * 获取项目附件列表
   */
  static async getAttachmentList(projectId: number): Promise<Attachment[]> {
    try {
      return await attachmentApi.list(projectId)
    } catch (error: any) {
      const message = error?.response?.data?.detail || '获取附件列表失败'
      ElMessage.error(message)
      throw error
    }
  }

  /**
   * 上传附件
   */
  static async uploadAttachment(
    projectId: number,
    file: File,
    fileType: string,
    description?: string,
    folderId?: number,
    onUploadProgress?: (progressEvent: any) => void
  ): Promise<Attachment> {
    try {
      const attachment = await attachmentApi.upload(projectId, file, fileType, description, folderId, onUploadProgress)
      ElMessage.success('文件上传成功')
      return attachment
    } catch (error: any) {
      const message = error?.response?.data?.detail || '文件上传失败'
      ElMessage.error(message)
      throw error
    }
  }

  /**
   * 下载附件
   */
  static async downloadAttachment(id: number): Promise<void> {
    try {
      // download 方法返回的已经是 Blob 对象
      const blob = await attachmentApi.download(id)
      // 直接使用 blob 创建 URL
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      // 获取文件信息以获取原始文件名
      const attachment = await attachmentApi.get(id)
      link.setAttribute('download', attachment.file_name)
      document.body.appendChild(link)
      link.click()
      link.remove()
      window.URL.revokeObjectURL(url)
    } catch (error: any) {
      const message = error?.response?.data?.detail || '文件下载失败'
      ElMessage.error(message)
      throw error
    }
  }

  /**
   * 删除附件
   */
  static async deleteAttachment(id: number): Promise<void> {
    try {
      await attachmentApi.delete(id)
      ElMessage.success('附件删除成功')
    } catch (error: any) {
      const message = error?.response?.data?.detail || '删除附件失败'
      ElMessage.error(message)
      throw error
    }
  }

  /**
   * 更新附件信息
   */
  static async updateAttachment(id: number, data: AttachmentUpdate): Promise<Attachment> {
    try {
      const attachment = await attachmentApi.update(id, data)
      ElMessage.success('附件信息更新成功')
      return attachment
    } catch (error: any) {
      const message = error?.response?.data?.detail || '更新附件信息失败'
      ElMessage.error(message)
      throw error
    }
  }
}

