import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { attachmentApi, type Attachment } from '@/api/attachment'
import request from '@/api/request'
import type { GraduationFileType } from '@/types/plugin'
import { graduationFileTypes } from '@/types/plugin'

// 存储附件标记的映射：attachment_id -> file_type
const attachmentTags = ref<Record<number, GraduationFileType>>({})

// 从 localStorage 加载标记
const loadTags = () => {
  try {
    const stored = localStorage.getItem('graduationAttachmentTags')
    if (stored) {
      attachmentTags.value = JSON.parse(stored)
    }
  } catch (error) {
    console.error('加载毕设附件标记失败:', error)
  }
}

// 保存标记到 localStorage
const saveTags = () => {
  try {
    localStorage.setItem('graduationAttachmentTags', JSON.stringify(attachmentTags.value))
  } catch (error) {
    console.error('保存毕设附件标记失败:', error)
  }
}

// 初始化加载
loadTags()

export function useGraduationPlugin() {
  // 标记附件为毕设文件类型
  const tagAttachment = async (
    attachmentId: number,
    fileType: GraduationFileType,
    projectId: number
  ) => {
    attachmentTags.value[attachmentId] = fileType
    saveTags()
    
    // 创建日志记录
    try {
      const fileTypeConfig = graduationFileTypes[fileType]
      await request.post('/project-logs/', {
        project_id: projectId,
        action: 'project_updated',
        description: `标记文件为：${fileTypeConfig.label}`,
        details: JSON.stringify({
          attachment_id: attachmentId,
          graduation_file_type: fileType
        })
      })
      ElMessage.success(`已标记为${fileTypeConfig.label}`)
    } catch (error) {
      console.error('创建日志记录失败:', error)
    }
  }

  // 取消标记
  const untagAttachment = (attachmentId: number) => {
    delete attachmentTags.value[attachmentId]
    saveTags()
  }

  // 获取附件的标记类型
  const getAttachmentTag = (attachmentId: number): GraduationFileType | null => {
    return attachmentTags.value[attachmentId] || null
  }

  // 获取项目下所有标记的附件
  const getTaggedAttachments = (attachments: Attachment[]): Record<GraduationFileType, Attachment[]> => {
    const result: Record<string, Attachment[]> = {}
    
    // 初始化所有类型
    Object.keys(graduationFileTypes).forEach(type => {
      result[type] = []
    })

    attachments.forEach(attachment => {
      const tag = attachmentTags.value[attachment.id]
      if (tag) {
        if (!result[tag]) {
          result[tag] = []
        }
        result[tag].push(attachment)
      }
    })

    return result as Record<GraduationFileType, Attachment[]>
  }

  // 上传文件并标记
  const uploadAndTag = async (
    projectId: number,
    fileType: GraduationFileType,
    file: File,
    folderId?: number,
    onUploadProgress?: (progressEvent: any) => void
  ) => {
    try {
      // 上传文件（使用 fileType 作为 file_type）
      const attachment = await attachmentApi.upload(
        projectId, 
        file, 
        '其他', // file_type，标记会在后续处理
        undefined, // description
        folderId,
        onUploadProgress
      )
      
      // 标记文件
      await tagAttachment(attachment.id, fileType, projectId)
      
      return attachment
    } catch (error: any) {
      console.error('上传并标记文件失败:', error)
      ElMessage.error(error.response?.data?.detail || '上传文件失败')
      throw error
    }
  }

  return {
    tagAttachment,
    untagAttachment,
    getAttachmentTag,
    getTaggedAttachments,
    uploadAndTag,
  }
}

