/**
 * 用户服务层
 * 处理用户相关的业务逻辑
 */
import { userApi, type UserInfo, type UserUpdate } from '@/api/user'
import { authApi, type RegisterForm } from '@/api/auth'
import { ElMessage } from 'element-plus'

export class UserService {
  /**
   * 获取用户列表
   */
  static async getUserList(): Promise<UserInfo[]> {
    try {
      return await userApi.list()
    } catch (error: any) {
      const message = error?.response?.data?.detail || '获取用户列表失败'
      ElMessage.error(message)
      throw error
    }
  }

  /**
   * 获取用户详情
   */
  static async getUserById(id: number): Promise<UserInfo> {
    try {
      return await userApi.get(id)
    } catch (error: any) {
      const message = error?.response?.data?.detail || '获取用户详情失败'
      ElMessage.error(message)
      throw error
    }
  }

  /**
   * 创建用户
   */
  static async createUser(data: RegisterForm): Promise<UserInfo> {
    try {
      const user = await authApi.register(data)
      ElMessage.success('用户创建成功')
      return user
    } catch (error: any) {
      const message = error?.response?.data?.detail || '创建用户失败'
      ElMessage.error(message)
      throw error
    }
  }

  /**
   * 更新用户
   */
  static async updateUser(id: number, data: UserUpdate): Promise<UserInfo> {
    try {
      const user = await userApi.update(id, data)
      ElMessage.success('用户更新成功')
      return user
    } catch (error: any) {
      const message = error?.response?.data?.detail || '更新用户失败'
      ElMessage.error(message)
      throw error
    }
  }

  /**
   * 删除用户
   */
  static async deleteUser(id: number): Promise<void> {
    try {
      await userApi.delete(id)
      ElMessage.success('用户删除成功')
    } catch (error: any) {
      const message = error?.response?.data?.detail || '删除用户失败'
      ElMessage.error(message)
      throw error
    }
  }
}

