/**
 * 视频回放API
 */
import request from './request'

export interface VideoPlayback {
  id: number
  project_id: number
  title: string
  description?: string
  file_path: string
  file_name: string
  file_size: number
  duration?: number
  thumbnail_path?: string
  status: string
  created_at: string
  updated_at: string
  link_count: number
  total_views: number
}

export interface VideoPlaybackLink {
  id: number
  video_id: number
  token: string
  view_count: number
  max_views?: number
  expires_at?: string
  is_active: boolean
  description?: string
  created_at: string
  watch_url: string
  last_watch_position?: number  // 上次观看位置（秒）
}

export interface VideoPlaybackLinkCreate {
  password: string
  expires_in_days?: number
  max_views?: number
  description?: string
}

export interface VideoPlaybackStat {
  id: number
  video_id: number
  link_id: number
  watched_at: string
  ip_address?: string
  watch_duration?: number
  watch_percentage?: number
}

export interface VideoStatistics {
  total_views: number
  total_duration: number
  avg_duration: number
  avg_percentage: number
}

export const videoPlaybackApi = {
  /**
   * 上传视频
   */
  async upload(
    projectId: number,
    file: File,
    title: string,
    description?: string,
    onUploadProgress?: (progressEvent: any) => void
  ): Promise<VideoPlayback> {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('title', title)
    if (description) {
      formData.append('description', description)
    }

    return request.post<VideoPlayback>(
      `/video-playbacks/project/${projectId}/upload`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        timeout: 30 * 60 * 1000, // 30分钟超时
        onUploadProgress: onUploadProgress,
      }
    )
  },

  /**
   * 获取项目的所有视频
   */
  async list(projectId: number): Promise<VideoPlayback[]> {
    return request.get<VideoPlayback[]>(
      `/video-playbacks/project/${projectId}`
    )
  },

  /**
   * 更新视频信息
   */
  async update(
    videoId: number,
    data: { title?: string; description?: string }
  ): Promise<VideoPlayback> {
    return request.put<VideoPlayback>(
      `/video-playbacks/${videoId}`,
      data
    )
  },

  /**
   * 删除视频
   */
  async delete(videoId: number): Promise<void> {
    await request.delete(`/video-playbacks/${videoId}`)
  },

  /**
   * 创建观看链接
   */
  async createLink(
    videoId: number,
    data: VideoPlaybackLinkCreate
  ): Promise<VideoPlaybackLink> {
    return request.post<VideoPlaybackLink>(
      `/video-playbacks/${videoId}/links`,
      data
    )
  },

  /**
   * 获取视频的所有链接
   */
  async listLinks(videoId: number): Promise<VideoPlaybackLink[]> {
    return request.get<VideoPlaybackLink[]>(
      `/video-playbacks/${videoId}/links`
    )
  },

  /**
   * 删除观看链接
   */
  async deleteLink(linkId: number): Promise<void> {
    await request.delete(`/video-playbacks/links/${linkId}`)
  },

  /**
   * 获取视频统计
   */
  async getStatistics(videoId: number): Promise<VideoStatistics> {
    return request.get<VideoStatistics>(
      `/video-playbacks/${videoId}/statistics`
    )
  },

  /**
   * 验证观看链接密码
   */
  async verifyPassword(
    token: string,
    password: string
  ): Promise<{ success: boolean; message: string; video_id: number; link_id: number; video: VideoPlayback; link: VideoPlaybackLink }> {
    return request.post(`/video-playbacks/watch/${token}/verify`, {
      password,
    })
  },

  /**
   * 记录观看统计
   */
  async recordView(
    token: string,
    watchDuration?: number,
    watchPercentage?: number
  ): Promise<void> {
    await request.post(`/video-playbacks/watch/${token}/record`, {
      watch_duration: watchDuration,
      watch_percentage: watchPercentage,
    })
  },

  /**
   * 保存观看进度
   */
  async saveProgress(token: string, position: number): Promise<void> {
    const formData = new FormData()
    formData.append('position', position.toString())
    await request.put(`/video-playbacks/watch/${token}/progress`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
  },

  /**
   * 获取观看进度
   */
  async getProgress(token: string): Promise<{ position: number; has_progress: boolean }> {
    return request.get(`/video-playbacks/watch/${token}/progress`)
  },
}

