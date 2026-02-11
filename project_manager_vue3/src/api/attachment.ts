import request from './request'
import { getToken } from '@/utils/auth'

export interface Attachment {
  id: number
  project_id: number
  file_path: string
  file_name: string
  file_type: string
  description?: string
  folder_id?: number
  folder_name?: string
  created_at: string
}

export interface AttachmentCreate {
  file_type: string
  description?: string
}

export interface AttachmentUpdate {
  file_name?: string
  file_type?: string
  description?: string
}

export const attachmentApi = {
  list: (projectId: number) => {
    return request.get<Attachment[]>(`/attachments/project/${projectId}`)
  },
  
  upload: (
    projectId: number, 
    file: File, 
    fileType: string, 
    description?: string, 
    folderId?: number,
    onUploadProgress?: (progressEvent: any) => void
  ) => {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('file_type', fileType)
    if (description) {
      formData.append('description', description)
    }
    if (folderId) {
      formData.append('folder_id', folderId.toString())
    }
    return request.post<Attachment>(`/attachments/project/${projectId}`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      timeout: 30 * 60 * 1000, // 30分钟超时
      onUploadProgress: onUploadProgress,
    })
  },
  
  get: (id: number) => {
    return request.get<Attachment>(`/attachments/${id}`)
  },
  
  update: (id: number, data: AttachmentUpdate) => {
    return request.put<Attachment>(`/attachments/${id}`, data)
  },
  
  delete: (id: number) => {
    return request.delete(`/attachments/${id}`)
  },
  
  copy: (id: number, targetProjectId?: number, targetFolderId?: number) => {
    return request.post<Attachment>(`/attachments/${id}/copy`, {
      target_project_id: targetProjectId,
      target_folder_id: targetFolderId,
    })
  },
  
  download: (id: number) => {
    return request.get(`/attachments/${id}/download`, {
      responseType: 'blob',
    }).then((response: any) => {
      // 如果response已经是Blob，直接返回
      if (response instanceof Blob) {
        return response
      }
      // 否则尝试从response中获取blob
      return response as Blob
    })
  },
  
  batch: (ids: number[]) => {
    return request.post<Attachment[]>(`/attachments/batch`, ids)
  },
  
  preview: (id: number) => {
    return request.get(`/attachments/${id}/preview`, {
      responseType: 'blob',
    }).then((response: any) => {
      if (response instanceof Blob) {
        return response
      }
      return response as Blob
    })
  },
  
  getPreviewUrl: (id: number): string => {
    // 返回预览URL，用于在iframe或img标签中使用
    // 使用统一的 token 获取方法
    const baseURL = import.meta.env.VITE_API_BASE_URL || '/api'
    const token = getToken()
    
    // 注意：对于iframe/img标签，无法直接使用Authorization header
    // 如果后端支持从 cookie 读取 token，则不需要在 URL 中传递
    // 如果后端不支持 cookie，可以通过 URL 参数传递 token（需要后端支持）
    // 目前先返回基础 URL，token 通过 cookie 或后端其他方式处理
    return `${baseURL}/attachments/${id}/preview`
  },
}

