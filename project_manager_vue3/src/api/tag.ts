import request from './request'

export interface Tag {
  id: number
  name: string
  color: string
  description?: string
  user_id?: number
  is_common: boolean
  usage_count: number
  created_at: string
  updated_at: string
}

export interface TagCreate {
  name: string
  color?: string
  description?: string
  is_common?: boolean
}

export interface TagUpdate {
  name?: string
  color?: string
  description?: string
  is_common?: boolean
}

export const tagApi = {
  // 创建标签
  create: (data: TagCreate) => {
    return request.post<Tag>('/tags/', data)
  },

  // 获取标签列表
  list: (includeCommon: boolean = true) => {
    return request.get<Tag[]>('/tags/', { params: { include_common: includeCommon } })
  },

  // 获取常用标签
  listCommon: () => {
    return request.get<Tag[]>('/tags/common')
  },

  // 获取标签详情
  get: (id: number) => {
    return request.get<Tag>(`/tags/${id}`)
  },

  // 更新标签
  update: (id: number, data: TagUpdate) => {
    return request.put<Tag>(`/tags/${id}`, data)
  },

  // 删除标签
  delete: (id: number) => {
    return request.delete(`/tags/${id}`)
  },

  // 为项目添加标签
  addProjectTag: (projectId: number, tagId: number) => {
    return request.post<Tag>(`/tags/project/${projectId}/tags`, null, { params: { tag_id: tagId } })
  },

  // 移除项目的标签
  removeProjectTag: (projectId: number, tagId: number) => {
    return request.delete(`/tags/project/${projectId}/tags/${tagId}`)
  },

  // 为历史项目添加标签
  addHistoricalProjectTag: (historicalProjectId: number, tagId: number) => {
    return request.post<Tag>(`/tags/historical-project/${historicalProjectId}/tags`, null, { params: { tag_id: tagId } })
  },

  // 移除历史项目的标签
  removeHistoricalProjectTag: (historicalProjectId: number, tagId: number) => {
    return request.delete(`/tags/historical-project/${historicalProjectId}/tags/${tagId}`)
  },
}

