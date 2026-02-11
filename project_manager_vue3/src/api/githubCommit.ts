import request from './request'

export interface GitHubCommit {
  id: number
  project_id: number
  sha: string
  branch: string
  author: string
  message: string
  commit_date: string
  url: string
  synced_at: string
  created_at: string
  updated_at: string
}

export interface GitHubCommitQuery {
  branch?: string
  limit?: number
  force_sync?: boolean
}

export const githubCommitApi = {
  /**
   * 获取项目的GitHub提交记录
   * @param projectId 项目ID
   * @param params 查询参数
   */
  getCommits(projectId: number, params?: GitHubCommitQuery): Promise<GitHubCommit[]> {
    const queryParams = new URLSearchParams()
    if (params?.branch) {
      queryParams.append('branch', params.branch)
    }
    if (params?.limit) {
      queryParams.append('limit', params.limit.toString())
    }
    if (params?.force_sync !== undefined) {
      queryParams.append('force_sync', params.force_sync.toString())
    }
    
    const queryString = queryParams.toString()
    const url = `/github-commits/projects/${projectId}/commits${queryString ? `?${queryString}` : ''}`
    
    return request.get<GitHubCommit[]>(url)
  },

  /**
   * 手动触发同步GitHub提交记录
   * @param projectId 项目ID
   * @param branch 分支名称
   */
  syncCommits(projectId: number, branch: string = 'main'): Promise<GitHubCommit[]> {
    return request.post<GitHubCommit[]>(`/github-commits/projects/${projectId}/sync?branch=${branch}`)
  },
}

