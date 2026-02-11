<!--
  项目管理页面 - 符合阶段三架构要求
  文件：views/ProjectList.vue
  说明：这是按照架构文档要求实现的项目管理页面
-->
<template>
  <div class="project-list-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span class="page-title">项目管理</span>
          <el-button type="primary" @click="showCreateDialog = true">
            <el-icon><Plus /></el-icon>
            新建项目
          </el-button>
        </div>
      </template>

      <!-- 项目列表表格 -->
      <el-table 
        :data="projects" 
        style="width: 100%" 
        v-loading="loading"
        :scroll="{ x: 'max-content' }"
        stripe
      >
        <!-- Title 列 -->
        <el-table-column prop="title" label="项目名称" min-width="200" />
        
        <!-- Platform 列 -->
        <el-table-column prop="platform.name" label="平台" min-width="120" />
        
        <!-- Price 列 -->
        <el-table-column prop="price" label="金额" min-width="100" align="right">
          <template #default="{ row }">
            <span class="price-text">¥{{ row.price.toFixed(2) }}</span>
          </template>
        </el-table-column>
        
        <!-- Current Status 列 - 从最后一个完成的步骤计算 -->
        <el-table-column label="当前状态" min-width="150">
          <template #default="{ row }">
            <el-tag :type="getCurrentStatusType(row)" size="small">
              {{ getCurrentStatus(row) }}
            </el-tag>
          </template>
        </el-table-column>
        
        <!-- Actions 列 -->
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button
              type="primary"
              size="small"
              @click="handleEdit(row)"
            >
              编辑
            </el-button>
            <el-button
              type="danger"
              size="small"
              @click="handleDelete(row)"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 创建项目对话框 -->
    <el-dialog
      v-model="showCreateDialog"
      title="新建项目"
      width="600px"
      @close="resetForm"
    >
      <el-form
        ref="createFormRef"
        :model="createForm"
        :rules="formRules"
        label-width="100px"
      >
        <el-form-item label="项目名称" prop="title">
          <el-input v-model="createForm.title" placeholder="请输入项目名称" />
        </el-form-item>
        <el-form-item label="学生姓名">
          <el-input v-model="createForm.student_name" placeholder="请输入学生姓名" />
        </el-form-item>
        <el-form-item label="接单平台" prop="platform_id">
          <el-select v-model="createForm.platform_id" placeholder="请选择平台" style="width: 100%">
            <el-option
              v-for="platform in platforms"
              :key="platform.id"
              :label="platform.name"
              :value="platform.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="订单金额" prop="price">
          <el-input-number
            v-model="createForm.price"
            :precision="2"
            :min="0"
            style="width: 100%"
            placeholder="请输入订单金额"
          />
        </el-form-item>
        <el-form-item label="GitHub地址">
          <el-input v-model="createForm.github_url" placeholder="请输入GitHub仓库地址" />
        </el-form-item>
        <el-form-item label="需求描述">
          <el-input
            v-model="createForm.requirements"
            type="textarea"
            :rows="4"
            placeholder="请输入项目需求描述"
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleCreate">
          确定
        </el-button>
      </template>
    </el-dialog>

    <!-- 编辑项目对话框 -->
    <el-dialog
      v-model="showEditDialog"
      title="编辑项目"
      width="600px"
      @close="resetEditForm"
    >
      <el-form
        ref="editFormRef"
        :model="editForm"
        :rules="formRules"
        label-width="100px"
      >
        <el-form-item label="项目名称" prop="title">
          <el-input v-model="editForm.title" />
        </el-form-item>
        <el-form-item label="学生姓名">
          <el-input v-model="editForm.student_name" />
        </el-form-item>
        <el-form-item label="接单平台" prop="platform_id">
          <el-select v-model="editForm.platform_id" style="width: 100%">
            <el-option
              v-for="platform in platforms"
              :key="platform.id"
              :label="platform.name"
              :value="platform.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="订单金额" prop="price">
          <el-input-number
            v-model="editForm.price"
            :precision="2"
            :min="0"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="GitHub地址">
          <el-input v-model="editForm.github_url" />
        </el-form-item>
        <el-form-item label="需求描述">
          <el-input
            v-model="editForm.requirements"
            type="textarea"
            :rows="4"
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showEditDialog = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleUpdate">
          确定
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { projectApi, type Project, type ProjectCreate, type ProjectUpdate } from '@/api/project'
import { platformApi, type Platform } from '@/api/platform'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()
const createFormRef = ref<FormInstance>()
const editFormRef = ref<FormInstance>()
const loading = ref(false)
const submitting = ref(false)
const showCreateDialog = ref(false)
const showEditDialog = ref(false)
const editingProjectId = ref<number | null>(null)
const projects = ref<Project[]>([])
const platforms = ref<Platform[]>([])

const createForm = reactive<ProjectCreate>({
  title: '',
  student_name: '',
  platform_id: 0,
  user_id: userStore.userInfo?.id || 0,
  price: 0,
  github_url: '',
  requirements: '',
})

const editForm = reactive<ProjectUpdate>({
  title: '',
  student_name: '',
  platform_id: 0,
  price: 0,
  github_url: '',
  requirements: '',
})

const formRules: FormRules = {
  title: [{ required: true, message: '请输入项目名称', trigger: 'blur' }],
  platform_id: [{ required: true, message: '请选择接单平台', trigger: 'change' }],
  price: [{ required: true, message: '请输入订单金额', trigger: 'blur' }],
}

/**
 * 计算当前状态 - 从最后一个完成的步骤计算
 * 符合架构要求：Current Status (calculated from the last 'done' step)
 */
const getCurrentStatus = (project: Project): string => {
  if (!project.steps || project.steps.length === 0) {
    return '未开始'
  }
  
  // 按 order_index 排序步骤
  const sortedSteps = [...project.steps].sort((a, b) => a.order_index - b.order_index)
  
  // 找到最后一个状态为"已完成"的步骤
  let lastDoneStep = null
  for (let i = sortedSteps.length - 1; i >= 0; i--) {
    if (sortedSteps[i].status === '已完成') {
      lastDoneStep = sortedSteps[i]
      break
    }
  }
  
  // 如果所有步骤都完成
  const allDone = sortedSteps.every(step => step.status === '已完成')
  if (allDone) {
    return '已完成'
  }
  
  // 如果有完成的步骤，返回最后一个完成步骤的名称
  if (lastDoneStep) {
    return lastDoneStep.name
  }
  
  // 如果没有完成的步骤，返回第一个步骤的名称
  return sortedSteps[0]?.name || '未开始'
}

/**
 * 获取当前状态的标签类型
 */
const getCurrentStatusType = (project: Project): string => {
  const status = getCurrentStatus(project)
  
  if (status === '已完成') {
    return 'success'
  }
  
  if (status === '未开始') {
    return 'info'
  }
  
  // 检查是否有进行中的步骤
  const hasInProgress = project.steps?.some(step => step.status === '进行中')
  if (hasInProgress) {
    return 'warning'
  }
  
  return 'info'
}

const loadPlatforms = async () => {
  try {
    const data = await platformApi.list()
    platforms.value = data
  } catch (error) {
    ElMessage.error('加载平台列表失败')
  }
}

const loadProjects = async () => {
  loading.value = true
  try {
    const data = await projectApi.list()
    projects.value = data
  } catch (error) {
    ElMessage.error('加载项目列表失败')
  } finally {
    loading.value = false
  }
}

const resetForm = () => {
  createFormRef.value?.resetFields()
  Object.assign(createForm, {
    title: '',
    student_name: '',
    platform_id: 0,
    user_id: userStore.userInfo?.id || 0,
    price: 0,
    github_url: '',
    requirements: '',
  })
}

const resetEditForm = () => {
  editFormRef.value?.resetFields()
  editingProjectId.value = null
  Object.assign(editForm, {
    title: '',
    student_name: '',
    platform_id: 0,
    price: 0,
    github_url: '',
    requirements: '',
  })
}

const handleCreate = async () => {
  if (!createFormRef.value) return
  
  await createFormRef.value.validate(async (valid) => {
    if (valid) {
      submitting.value = true
      try {
        await projectApi.create(createForm)
        ElMessage.success('创建成功')
        showCreateDialog.value = false
        resetForm()
        loadProjects()
      } catch (error) {
        ElMessage.error('创建失败')
      } finally {
        submitting.value = false
      }
    }
  })
}

const handleEdit = (project: Project) => {
  editingProjectId.value = project.id
  Object.assign(editForm, {
    title: project.title,
    student_name: project.student_name || '',
    platform_id: project.platform_id,
    price: project.price,
    github_url: project.github_url || '',
    requirements: project.requirements || '',
  })
  showEditDialog.value = true
}

const handleUpdate = async () => {
  if (!editFormRef.value || !editingProjectId.value) return
  
  await editFormRef.value.validate(async (valid) => {
    if (valid) {
      submitting.value = true
      try {
        await projectApi.update(editingProjectId.value, editForm)
        ElMessage.success('更新成功')
        showEditDialog.value = false
        resetEditForm()
        loadProjects()
      } catch (error) {
        ElMessage.error('更新失败')
      } finally {
        submitting.value = false
      }
    }
  })
}

const handleDelete = async (project: Project) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除项目"${project.title}"吗？`,
      '提示',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )
    
    await projectApi.delete(project.id)
    ElMessage.success('删除成功')
    loadProjects()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

onMounted(() => {
  loadPlatforms()
  loadProjects()
})
</script>

<style scoped>
.project-list-page {
  padding: 20px;
  background: #f5f7fa;
  min-height: calc(100vh - 60px);
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

.page-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.price-text {
  font-weight: 600;
  color: #303133;
}

.table-wrapper {
  overflow-x: auto;
  width: 100%;
}

:deep(.el-table) {
  margin-top: 16px;
}

:deep(.el-table__row) {
  transition: background-color 0.2s;
}

:deep(.el-table__row:hover) {
  background: #f5f7fa;
}

/* 移动端样式 */
@media (max-width: 768px) {
  .project-list-page {
    padding: 12px;
  }

  .card-header {
    flex-direction: column;
    align-items: stretch;
  }

  .page-title {
    margin-bottom: 12px;
  }
}
</style>

