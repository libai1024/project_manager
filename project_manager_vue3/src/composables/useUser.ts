/**
 * 用户相关的组合式函数
 */
import { ref, computed } from 'vue'
import { UserService } from '@/services/user.service'
import type { UserInfo, UserUpdate } from '@/api/user'
import type { RegisterForm } from '@/api/auth'
import { useUserStore } from '@/stores/user'

export function useUser() {
  const userStore = useUserStore()
  const loading = ref(false)
  const users = ref<UserInfo[]>([])

  /**
   * 加载用户列表
   */
  const loadUsers = async () => {
    loading.value = true
    try {
      users.value = await UserService.getUserList()
    } catch (error) {
      // 错误已在Service层处理
    } finally {
      loading.value = false
    }
  }

  /**
   * 创建用户
   */
  const createUser = async (data: RegisterForm) => {
    const user = await UserService.createUser(data)
    await loadUsers()
    return user
  }

  /**
   * 更新用户
   */
  const updateUser = async (id: number, data: UserUpdate) => {
    const user = await UserService.updateUser(id, data)
    await loadUsers()
    return user
  }

  /**
   * 删除用户
   */
  const deleteUser = async (id: number) => {
    await UserService.deleteUser(id)
    await loadUsers()
  }

  return {
    loading,
    users,
    loadUsers,
    createUser,
    updateUser,
    deleteUser,
    currentUserId: computed(() => userStore.userInfo?.id),
  }
}

