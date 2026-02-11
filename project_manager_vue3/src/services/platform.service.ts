/**
 * 平台服务层
 * 处理平台相关的业务逻辑
 */
import { platformApi, type Platform, type PlatformCreate, type PlatformUpdate } from '@/api/platform'
import { ElMessage } from 'element-plus'

export class PlatformService {
  /**
   * 获取平台列表
   */
  static async getPlatformList(): Promise<Platform[]> {
    try {
      return await platformApi.list()
    } catch (error: any) {
      const message = error?.response?.data?.detail || '获取平台列表失败'
      ElMessage.error(message)
      throw error
    }
  }

  /**
   * 获取平台详情
   */
  static async getPlatformById(id: number): Promise<Platform> {
    try {
      return await platformApi.get(id)
    } catch (error: any) {
      const message = error?.response?.data?.detail || '获取平台详情失败'
      ElMessage.error(message)
      throw error
    }
  }

  /**
   * 创建平台
   */
  static async createPlatform(data: PlatformCreate): Promise<Platform> {
    try {
      const platform = await platformApi.create(data)
      ElMessage.success('平台创建成功')
      return platform
    } catch (error: any) {
      const message = error?.response?.data?.detail || '创建平台失败'
      ElMessage.error(message)
      throw error
    }
  }

  /**
   * 更新平台
   */
  static async updatePlatform(id: number, data: PlatformUpdate): Promise<Platform> {
    try {
      const platform = await platformApi.update(id, data)
      ElMessage.success('平台更新成功')
      return platform
    } catch (error: any) {
      const message = error?.response?.data?.detail || '更新平台失败'
      ElMessage.error(message)
      throw error
    }
  }

  /**
   * 删除平台
   */
  static async deletePlatform(id: number): Promise<void> {
    try {
      await platformApi.delete(id)
      ElMessage.success('平台删除成功')
    } catch (error: any) {
      const message = error?.response?.data?.detail || '删除平台失败'
      ElMessage.error(message)
      throw error
    }
  }
}

