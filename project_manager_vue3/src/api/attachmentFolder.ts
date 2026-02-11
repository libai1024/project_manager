import request from './request'

export interface AttachmentFolder {
  id: number
  project_id: number
  name: string
  is_default: boolean
  description?: string
  created_at: string
  updated_at: string
  attachment_count?: number
}

export interface AttachmentFolderCreate {
  name: string
  description?: string
}

export interface AttachmentFolderUpdate {
  name?: string
  description?: string
}

export const attachmentFolderApi = {
  list: (projectId: number) => {
    return request.get<AttachmentFolder[]>(`/attachment-folders/project/${projectId}`)
  },
  
  create: (projectId: number, data: AttachmentFolderCreate) => {
    return request.post<AttachmentFolder>(`/attachment-folders/project/${projectId}`, data)
  },
  
  update: (folderId: number, data: AttachmentFolderUpdate) => {
    return request.put<AttachmentFolder>(`/attachment-folders/${folderId}`, data)
  },
  
  delete: (folderId: number) => {
    return request.delete(`/attachment-folders/${folderId}`)
  },
}

