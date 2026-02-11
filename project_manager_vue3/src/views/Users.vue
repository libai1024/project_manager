<template>
  <div class="users-page">
    <!-- 统计卡片 -->
    <el-row :gutter="20" class="stats-row">
      <el-col :xs="24" :sm="12" :md="6">
        <div class="stat-card total-users">
          <div class="stat-icon">
            <el-icon :size="32"><User /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-label">总用户数</div>
            <div class="stat-value">{{ totalUsers }}</div>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <div class="stat-card admin-users">
          <div class="stat-icon">
            <el-icon :size="32"><User /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-label">管理员</div>
            <div class="stat-value">{{ adminCount }}</div>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <div class="stat-card normal-users">
          <div class="stat-icon">
            <el-icon :size="32"><User /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-label">普通用户</div>
            <div class="stat-value">{{ normalUserCount }}</div>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <div class="stat-card recent-users">
          <div class="stat-icon">
            <el-icon :size="32"><Clock /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-label">本月新增</div>
            <div class="stat-value">{{ recentUsersCount }}</div>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- 用户列表卡片 -->
    <el-card class="users-card">
      <template #header>
        <div class="card-header">
          <span>用户列表</span>
          <div class="header-actions">
            <el-input
              v-model="searchKeyword"
              placeholder="搜索用户名..."
              clearable
              size="small"
              style="width: 200px; margin-right: 12px;"
              @input="handleSearch"
            >
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
            </el-input>
            <el-select
              v-model="filterRole"
              placeholder="全部角色"
              clearable
              size="small"
              style="width: 120px; margin-right: 12px;"
              @change="handleFilterChange"
            >
              <el-option label="管理员" value="admin" />
              <el-option label="普通用户" value="user" />
            </el-select>
          <el-button type="primary" @click="showCreateDialog = true">
            <el-icon><Plus /></el-icon>
            新建用户
          </el-button>
          </div>
        </div>
      </template>

      <div class="table-wrapper">
        <el-table
          :data="filteredUsers"
          style="width: 100%"
          v-loading="loading"
          :scroll="{ x: 'max-content' }"
          stripe
          class="users-table"
        >
          <el-table-column prop="id" label="ID" min-width="60" align="center" />
          <el-table-column prop="username" label="用户名" min-width="150">
            <template #default="{ row }">
              <div class="username-cell">
                <el-icon class="user-icon"><User /></el-icon>
                <span>{{ row.username }}</span>
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="role" label="角色" min-width="120" align="center">
            <template #default="{ row }">
              <el-tag :type="row.role === 'admin' ? 'danger' : 'info'" size="small">
                {{ row.role === 'admin' ? '管理员' : '普通用户' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="created_at" label="创建时间" min-width="180">
            <template #default="{ row }">
              <div class="time-cell">
                <el-icon :size="14"><Clock /></el-icon>
                <span>{{ formatDateTime(row.created_at) }}</span>
              </div>
            </template>
          </el-table-column>
          <el-table-column label="操作" min-width="180" fixed="right" align="center">
            <template #default="{ row }">
              <el-button
                type="primary"
                size="small"
                :icon="Edit"
                @click="handleEdit(row)"
                :disabled="row.username === 'admin'"
              >
                编辑
              </el-button>
              <el-button
                type="danger"
                size="small"
                :icon="Delete"
                @click="handleDelete(row)"
                :disabled="row.id === currentUserId || row.username === 'admin'"
              >
                删除
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </el-card>

    <!-- 创建/编辑用户对话框 -->
    <el-dialog
      v-model="showCreateDialog"
      :title="editingUser ? '编辑用户' : '新建用户'"
      width="500px"
      @close="resetForm"
    >
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="100px"
      >
        <el-form-item label="用户名" prop="username">
          <el-input
            v-model="form.username"
            placeholder="请输入用户名"
            :disabled="!!editingUser"
          />
        </el-form-item>
        <el-form-item label="密码" prop="password" v-if="!editingUser">
          <el-input
            v-model="form.password"
            type="password"
            placeholder="请输入密码"
            show-password
          />
        </el-form-item>
        <el-form-item label="新密码" prop="newPassword" v-else>
          <el-input
            v-model="form.newPassword"
            type="password"
            placeholder="留空则不修改密码"
            show-password
          />
        </el-form-item>
        <el-form-item label="角色" prop="role">
          <el-select
            v-model="form.role"
            style="width: 100%"
            :disabled="editingUser?.username === 'admin'"
          >
            <el-option label="普通用户" value="user" />
            <el-option label="管理员" value="admin" />
          </el-select>
          <div v-if="editingUser?.username === 'admin'" class="form-tip">
            <el-icon><Lock /></el-icon>
            <span>admin 账户的角色不可修改</span>
          </div>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSubmit">
          确定
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import {
  Plus,
  User,
  Clock,
  Search,
  Edit,
  Delete,
  Lock,
} from '@element-plus/icons-vue'
import { useUser } from '@/composables/useUser'
import type { UserInfo, UserUpdate } from '@/api/user'
import type { RegisterForm } from '@/api/auth'

const formRef = ref<FormInstance>()
const submitting = ref(false)
const showCreateDialog = ref(false)
const editingUser = ref<UserInfo | null>(null)

// 使用Composable
const {
  loading,
  users,
  currentUserId,
  loadUsers,
  createUser,
  updateUser,
  deleteUser,
} = useUser()

const form = reactive<RegisterForm & { newPassword?: string }>({
  username: '',
  password: '',
  role: 'user',
  newPassword: '',
})

// 搜索和筛选
const searchKeyword = ref('')
const filterRole = ref<string | null>(null)

// 计算属性
const totalUsers = computed(() => users.value.length)
const adminCount = computed(() => users.value.filter(u => u.role === 'admin').length)
const normalUserCount = computed(() => users.value.filter(u => u.role === 'user').length)
const recentUsersCount = computed(() => {
  const now = new Date()
  const startOfMonth = new Date(now.getFullYear(), now.getMonth(), 1)
  return users.value.filter(u => {
    const createdAt = new Date(u.created_at)
    return createdAt >= startOfMonth
  }).length
})

const filteredUsers = computed(() => {
  let result = [...users.value]
  
  // 搜索过滤
  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    result = result.filter(u => u.username.toLowerCase().includes(keyword))
  }
  
  // 角色过滤
  if (filterRole.value) {
    result = result.filter(u => u.role === filterRole.value)
  }
  
  return result
})

const rules: FormRules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6位', trigger: 'blur' },
  ],
}

// 格式化时间
const formatDateTime = (dateString: string): string => {
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const handleSearch = () => {
  // 搜索逻辑已在 computed 中处理
}

const handleFilterChange = () => {
  // 筛选逻辑已在 computed 中处理
}

const resetForm = () => {
  formRef.value?.resetFields()
  editingUser.value = null
  Object.assign(form, {
    username: '',
    password: '',
    role: 'user',
    newPassword: '',
  })
}

const handleEdit = (user: UserInfo) => {
  editingUser.value = user
  Object.assign(form, {
    username: user.username,
    role: user.role,
    password: '',
    newPassword: '',
  })
  showCreateDialog.value = true
}

const handleSubmit = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (valid) {
      submitting.value = true
      try {
        if (editingUser.value) {
          // 保护 admin 账户的角色
          if (editingUser.value.username === 'admin' && form.role !== 'admin') {
            ElMessageBox.alert('admin 账户的角色不可修改', '提示', {
              type: 'warning',
            })
            submitting.value = false
            return
          }
          
          const updateData: UserUpdate = {
            role: form.role,
          }
          if (form.newPassword) {
            updateData.password = form.newPassword
          }
          await updateUser(editingUser.value.id, updateData)
        } else {
          await createUser(form)
        }
        showCreateDialog.value = false
        resetForm()
      } catch (error) {
        // 错误已在Service层处理
      } finally {
        submitting.value = false
      }
    }
  })
}

const handleDelete = async (user: UserInfo) => {
  // 保护 admin 账户
  if (user.username === 'admin') {
    ElMessageBox.alert('admin 账户不可删除', '提示', {
      type: 'warning',
    })
    return
  }
  
  try {
    await ElMessageBox.confirm(
      `确定要删除用户"${user.username}"吗？`,
      '提示',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )
    
    await deleteUser(user.id)
  } catch (error: any) {
    if (error !== 'cancel') {
      // 错误已在Service层处理
    }
  }
}

onMounted(() => {
  loadUsers()
})
</script>

<style scoped>
.users-page {
  padding: 20px;
  background: #f5f7fa;
  min-height: calc(100vh - 60px);
}

.stats-row {
  margin-bottom: 20px;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  transition: all 0.3s;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12);
}

.stat-icon {
  width: 56px;
  height: 56px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 12px;
  flex-shrink: 0;
}

.total-users .stat-icon {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
}

.admin-users .stat-icon {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  color: #fff;
}

.normal-users .stat-icon {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
  color: #fff;
}

.recent-users .stat-icon {
  background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
  color: #fff;
}

.stat-content {
  flex: 1;
  min-width: 0;
}

.stat-label {
  font-size: 13px;
  color: #909399;
  margin-bottom: 8px;
}

.stat-value {
  font-size: 24px;
  font-weight: 600;
  color: #303133;
  line-height: 1.2;
}

.users-card {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
  font-weight: 600;
  color: #303133;
}

.header-actions {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
}

.table-wrapper {
  overflow-x: auto;
  width: 100%;
}

.users-table {
  margin-top: 16px;
}

.users-table :deep(.el-table__row) {
  transition: background-color 0.2s;
}

.users-table :deep(.el-table__row:hover) {
  background: #f5f7fa;
}

.username-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}

.user-icon {
  color: #409eff;
}

.time-cell {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #909399;
  font-size: 13px;
}

.form-tip {
  display: flex;
  align-items: center;
  gap: 4px;
  margin-top: 4px;
  font-size: 12px;
  color: #909399;
}

.form-tip .el-icon {
  color: #e6a23c;
}

/* 移动端样式 */
@media (max-width: 768px) {
  .users-page {
    padding: 12px;
  }

  .card-header {
    flex-direction: column;
    align-items: stretch;
  }

  .header-actions {
    flex-direction: column;
    width: 100%;
  }

  .header-actions .el-input,
  .header-actions .el-select {
    width: 100% !important;
    margin-right: 0 !important;
  }

  .header-actions .el-button {
    width: 100%;
  }
}
</style>
