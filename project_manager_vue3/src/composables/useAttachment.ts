/**
 * 附件相关的组合式函数
 */
import { ref } from 'vue'
import { AttachmentService } from '@/services/attachment.service'
import type { Attachment, AttachmentUpdate } from '@/api/attachment'

export function useAttachment(projectId: number) {
  const loading = ref(false)
  const attachments = ref<Attachment[]>([])

  /**
   * 加载附件列表
   */
  const loadAttachments = async () => {
    loading.value = true
    try {
      attachments.value = await AttachmentService.getAttachmentList(projectId)
    } catch (error) {
      // 错误已在Service层处理
    } finally {
      loading.value = false
    }
  }

  /**
   * 上传附件
   */
  const uploadAttachment = async (file: File, fileType: string, description?: string) => {
    const attachment = await AttachmentService.uploadAttachment(projectId, file, fileType, description)
    await loadAttachments()
    return attachment
  }

  /**
   * 下载附件
   */
  const downloadAttachment = async (id: number) => {
    await AttachmentService.downloadAttachment(id)
  }

  /**
   * 删除附件
   */
  const deleteAttachment = async (id: number) => {
    await AttachmentService.deleteAttachment(id)
    await loadAttachments()
  }

  /**
   * 更新附件信息
   */
  const updateAttachment = async (id: number, data: AttachmentUpdate) => {
    const attachment = await AttachmentService.updateAttachment(id, data)
    await loadAttachments()
    return attachment
  }

  return {
    loading,
    attachments,
    loadAttachments,
    uploadAttachment,
    downloadAttachment,
    deleteAttachment,
    updateAttachment,
  }
}

