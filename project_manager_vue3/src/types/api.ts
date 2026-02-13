/**
 * API响应类型定义
 *
 * 定义统一的API响应结构类型。
 * 符合国内互联网企业级规范。
 */

/**
 * 统一API响应结构
 */
export interface ApiResponse<T = unknown> {
  /** 业务状态码 */
  code: number
  /** 响应消息 */
  msg: string
  /** 响应数据 */
  data: T
  /** 附加详情（可选） */
  details?: Record<string, unknown>
}

/**
 * 分页数据结构
 */
export interface PagedData<T> {
  /** 数据列表 */
  items: T[]
  /** 总记录数 */
  total: number
  /** 当前页码 */
  page: number
  /** 每页记录数 */
  page_size: number
  /** 总页数 */
  total_pages: number
}

/**
 * 分页响应
 */
export type PagedResponse<T> = ApiResponse<PagedData<T>>

/**
 * 分页请求参数
 */
export interface PaginationParams {
  /** 页码（从1开始） */
  page?: number
  /** 每页数量 */
  page_size?: number
}

/**
 * 简单响应（只有成功/失败）
 */
export interface SimpleResponse {
  /** 是否成功 */
  success: boolean
  /** 消息 */
  message: string
}

/**
 * ID响应（创建操作返回）
 */
export interface IDResponse {
  /** 新创建的ID */
  id: number
}

/**
 * 计数响应
 */
export interface CountResponse {
  /** 数量 */
  count: number
}

/**
 * API错误
 */
export interface ApiError {
  /** 错误码 */
  code: number
  /** 错误消息 */
  msg: string
  /** 附加详情 */
  details?: Array<{
    field: string
    message: string
    type: string
  }>
}

/**
 * 列表响应（简化版，不带分页信息）
 */
export type ListResponse<T> = ApiResponse<T[]>
