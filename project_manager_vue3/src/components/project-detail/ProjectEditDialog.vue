<template>
  <el-dialog
    :model-value="visible"
    title=""
    width="800px"
    class="edit-project-dialog"
    :close-on-click-modal="false"
    @update:model-value="$emit('update:visible', $event)"
    @close="handleClose"
  >
    <template #header>
      <div class="dialog-header">
        <div class="header-icon-wrapper">
          <el-icon class="header-icon"><Edit /></el-icon>
        </div>
        <div class="header-content">
          <h3 class="dialog-title">编辑项目</h3>
          <p class="dialog-subtitle">修改项目信息，更新项目状态</p>
        </div>
      </div>
    </template>
    
    <div class="dialog-body">
      <el-form
        ref="formRef"
        :model="formData"
        :rules="rules"
        label-width="120px"
        class="project-form"
      >
        <!-- 基本信息 -->
        <div class="form-section">
          <div class="section-header">
            <el-icon class="section-icon"><InfoFilled /></el-icon>
            <span class="section-title">基本信息</span>
          </div>
          <div class="form-row">
            <el-form-item label="项目名称" prop="title" class="form-item-half">
              <el-input 
                v-model="formData.title" 
                size="large"
                clearable
              >
                <template #prefix>
                  <el-icon><Document /></el-icon>
                </template>
              </el-input>
            </el-form-item>
            <el-form-item label="学生姓名" class="form-item-half">
              <el-input 
                v-model="formData.student_name" 
                size="large"
                clearable
              >
                <template #prefix>
                  <el-icon><User /></el-icon>
                </template>
              </el-input>
            </el-form-item>
          </div>
          <el-form-item label="接单平台" prop="platform_id">
            <el-select 
              v-model="formData.platform_id" 
              size="large"
              style="width: 100%"
            >
              <el-option
                v-for="platform in platforms"
                :key="platform.id"
                :label="platform.name"
                :value="platform.id"
              />
            </el-select>
          </el-form-item>
        </div>

        <!-- 财务信息 -->
        <div class="form-section">
          <div class="section-header">
            <el-icon class="section-icon"><Money /></el-icon>
            <span class="section-title">财务信息</span>
          </div>
          <div class="form-row">
            <el-form-item label="订单金额" class="form-item-half">
              <el-input-number
                v-model="formData.price"
                :precision="2"
                :min="0"
                size="large"
                style="width: 100%"
                controls-position="right"
              />
            </el-form-item>
            <el-form-item label="实际收入" class="form-item-half">
              <el-input-number
                v-model="formData.actual_income"
                :precision="2"
                :min="0"
                size="large"
                style="width: 100%"
                controls-position="right"
              />
            </el-form-item>
          </div>
        </div>

        <!-- 项目详情 -->
        <div class="form-section">
          <div class="section-header">
            <el-icon class="section-icon"><Edit /></el-icon>
            <span class="section-title">项目详情</span>
          </div>
          <el-form-item label="GitHub地址">
            <el-input 
              v-model="formData.github_url" 
              size="large"
              clearable
            >
              <template #prefix>
                <el-icon><Link /></el-icon>
              </template>
            </el-input>
          </el-form-item>
          <el-form-item label="需求描述">
            <el-input
              v-model="formData.requirements"
              type="textarea"
              :rows="4"
              show-word-limit
              maxlength="1000"
            />
          </el-form-item>
        </div>

        <!-- 项目状态 -->
        <div class="form-section">
          <div class="section-header">
            <el-icon class="section-icon"><Setting /></el-icon>
            <span class="section-title">项目状态</span>
          </div>
          <div class="form-row">
            <el-form-item label="项目状态" class="form-item-half">
              <el-select v-model="formData.status" size="large" style="width: 100%">
                <el-option label="进行中" value="进行中" />
                <el-option label="已完成" value="已完成" />
                <el-option label="已结账" value="已结账" />
              </el-select>
            </el-form-item>
            <el-form-item label="是否结账" class="form-item-half">
              <el-switch 
                v-model="formData.is_paid" 
                size="large"
                active-text="已结账"
                inactive-text="未结账"
              />
            </el-form-item>
          </div>
        </div>

        <!-- 项目标签 -->
        <div class="form-section tags-form-section">
          <div class="section-header">
            <el-icon class="section-icon"><PriceTag /></el-icon>
            <span class="section-title">项目标签</span>
            <el-button
              type="text"
              size="small"
              @click="$emit('manage-tags')"
              class="manage-tags-btn"
            >
              <el-icon><Setting /></el-icon>
              管理标签
            </el-button>
          </div>
          <el-form-item label="标签">
            <div class="tag-selector-wrapper">
              <TagSelector v-model="selectedTagIds" />
            </div>
            <div v-if="selectedTagIds.length > 0" class="selected-tags-preview">
              <div class="preview-header">
                <div class="preview-label">
                  <el-icon class="label-icon"><Check /></el-icon>
                  <span>已选择 <strong>{{ selectedTagIds.length }}</strong> 个标签</span>
                </div>
                <el-button
                  text
                  type="danger"
                  size="small"
                  @click="selectedTagIds = []"
                  class="clear-btn"
                >
                  <el-icon><Delete /></el-icon>
                  清除全部
                </el-button>
              </div>
              <div class="preview-tags">
                <el-tag
                  v-for="tagId in selectedTagIds"
                  :key="tagId"
                  size="default"
                  class="preview-tag"
                  :style="{
                    backgroundColor: getTagBackgroundColor(getTag(tagId)?.color || ''),
                    borderColor: getTag(tagId)?.color || '#409eff',
                    color: getTag(tagId)?.color || '#409eff',
                    fontWeight: '600'
                  }"
                  effect="plain"
                  round
                  closable
                  @close="selectedTagIds = selectedTagIds.filter(id => id !== tagId)"
                >
                  <span class="tag-dot" :style="{ backgroundColor: getTag(tagId)?.color || '#409eff' }"></span>
                  <span class="tag-name">{{ getTagName(tagId) }}</span>
                </el-tag>
              </div>
            </div>
          </el-form-item>
        </div>
      </el-form>
    </div>
    
    <template #footer>
      <div class="dialog-footer">
        <el-button size="large" @click="$emit('update:visible', false)">取消</el-button>
        <el-button 
          type="primary" 
          size="large" 
          :loading="submitting" 
          @click="handleSubmit"
          class="submit-btn"
        >
          <el-icon v-if="!submitting"><Check /></el-icon>
          <span>{{ submitting ? '保存中...' : '保存更改' }}</span>
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, reactive, watch, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { Edit, InfoFilled, Document, User, Money, Setting, PriceTag, Link, Check, Delete } from '@element-plus/icons-vue'
import type { ProjectUpdate } from '@/api/project'
import type { Platform } from '@/api/platform'
import type { Tag } from '@/api/tag'
import TagSelector from '@/components/TagSelector.vue'

interface Props {
  visible: boolean
  project: {
    title: string
    student_name?: string
    platform_id: number
    price: number
    actual_income: number
    status: string
    github_url?: string
    requirements?: string
    is_paid: boolean
    tags?: Tag[]
  } | null
  platforms: Platform[]
  allTags: Tag[]
  submitting?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  submitting: false
})

const emit = defineEmits<{
  'update:visible': [value: boolean]
  'submit': [data: ProjectUpdate & { tag_ids?: number[] }]
  'manage-tags': []
}>()

const router = useRouter()
const formRef = ref<FormInstance>()
const selectedTagIds = ref<number[]>([])

const formData = reactive<ProjectUpdate>({
  title: '',
  student_name: '',
  platform_id: 0,
  price: 0,
  actual_income: 0,
  status: '进行中',
  github_url: '',
  requirements: '',
  is_paid: false,
})

const rules: FormRules = {
  title: [{ required: true, message: '请输入项目名称', trigger: 'blur' }],
  platform_id: [{ required: true, message: '请选择接单平台', trigger: 'change' }],
}

// 监听项目变化，更新表单数据
watch(() => props.project, (newProject) => {
  if (newProject) {
    Object.assign(formData, {
      title: newProject.title,
      student_name: newProject.student_name || '',
      platform_id: newProject.platform_id,
      price: newProject.price,
      actual_income: newProject.actual_income || 0,
      github_url: newProject.github_url || '',
      requirements: newProject.requirements || '',
      is_paid: newProject.is_paid,
      status: newProject.status || '进行中',
    })
    
    // 更新标签
    if (newProject.tags && newProject.tags.length > 0) {
      selectedTagIds.value = newProject.tags.map(tag => tag.id)
    } else {
      selectedTagIds.value = []
    }
  }
}, { immediate: true, deep: true })

// 获取标签名称
const getTagName = (tagId: number): string => {
  const tag = props.allTags.find(t => t.id === tagId)
  return tag?.name || `标签${tagId}`
}

// 获取标签对象
const getTag = (tagId: number): Tag | undefined => {
  return props.allTags.find(t => t.id === tagId)
}

// 将十六进制颜色转换为带透明度的颜色
const getTagBackgroundColor = (color: string): string => {
  if (!color) return '#f0f0f015'
  
  // 如果已经是完整的8位十六进制颜色（包含透明度），直接返回
  if (color.length === 9 && color.startsWith('#')) {
    return color
  }
  
  // 如果是6位十六进制颜色，添加透明度
  if (color.length === 7 && color.startsWith('#')) {
    return color + '15' // 添加约8%的透明度
  }
  
  // 如果是3位十六进制颜色，扩展为6位并添加透明度
  if (color.length === 4 && color.startsWith('#')) {
    const r = color[1]
    const g = color[2]
    const b = color[3]
    return `#${r}${r}${g}${g}${b}${b}15`
  }
  
  // 默认返回带透明度的颜色
  return color + '15'
}

// 处理关闭
const handleClose = () => {
  formRef.value?.resetFields()
  emit('update:visible', false)
}

// 处理提交
const handleSubmit = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (valid) {
      const updateData: ProjectUpdate & { tag_ids?: number[] } = {
        title: formData.title,
        student_name: formData.student_name || undefined,
        platform_id: formData.platform_id,
        price: formData.price,
        actual_income: formData.actual_income,
        status: formData.status,
        github_url: formData.github_url || undefined,
        requirements: formData.requirements || undefined,
        is_paid: formData.is_paid,
        tag_ids: selectedTagIds.value.length > 0 ? selectedTagIds.value : undefined,
      }
      
      emit('submit', updateData)
    }
  })
}
</script>

<style scoped>
.edit-project-dialog :deep(.el-dialog__header) {
  padding: 0;
  border-bottom: none;
}

.edit-project-dialog :deep(.el-dialog__body) {
  padding: 0;
}

.dialog-header {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 24px 24px 20px 24px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 8px 8px 0 0;
}

.header-icon-wrapper {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
}

.header-icon {
  font-size: 24px;
  color: #fff;
}

.header-content {
  flex: 1;
}

.dialog-title {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  color: #fff;
}

.dialog-subtitle {
  margin: 4px 0 0 0;
  font-size: 14px;
  color: rgba(255, 255, 255, 0.9);
}

.dialog-body {
  padding: 24px;
  max-height: 70vh;
  overflow-y: auto;
}

.project-form {
  padding: 0;
}

.form-section {
  margin-bottom: 32px;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #e9ecef;
}

.form-section:last-child {
  margin-bottom: 0;
}

.section-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 20px;
  padding-bottom: 12px;
  border-bottom: 2px solid #dee2e6;
}

.section-icon {
  font-size: 18px;
  color: #667eea;
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  color: #212529;
  flex: 1;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.form-item-half {
  margin-bottom: 20px;
}

.form-section :deep(.el-form-item) {
  margin-bottom: 20px;
}

.form-section :deep(.el-form-item:last-child) {
  margin-bottom: 0;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 20px 24px;
  border-top: 1px solid #ebeef5;
}

.submit-btn {
  min-width: 120px;
}

/* 标签相关样式 */
.tags-form-section {
  background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);
}

.tags-form-section .section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 2px solid #e9ecef;
}

.manage-tags-btn {
  color: #409eff;
  font-size: 12px;
  padding: 4px 8px;
  border-radius: 4px;
  transition: all 0.3s;
}

.manage-tags-btn:hover {
  background-color: #ecf5ff;
  color: #66b1ff;
}

.tag-selector-wrapper {
  background: #fff;
  border-radius: 8px;
  padding: 16px;
  border: 1px solid #e4e7ed;
  transition: all 0.3s;
}

.tag-selector-wrapper:hover {
  border-color: #409eff;
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.1);
}

.selected-tags-preview {
  margin-top: 16px;
  padding: 16px;
  background: linear-gradient(135deg, #f0f9ff 0%, #ffffff 100%);
  border-radius: 8px;
  border: 2px solid #e1f5ff;
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.08);
}

.preview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  padding-bottom: 12px;
  border-bottom: 1px solid #e1f5ff;
}

.preview-label {
  font-size: 13px;
  color: #409eff;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 6px;
}

.label-icon {
  font-size: 16px;
  color: #67c23a;
}

.preview-label strong {
  color: #303133;
  font-weight: 600;
}

.clear-btn {
  font-size: 12px;
  padding: 4px 8px;
  border-radius: 4px;
  transition: all 0.3s;
}

.clear-btn:hover {
  background-color: rgba(245, 108, 108, 0.1);
}

.preview-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  min-height: 40px;
}

.preview-tag {
  font-size: 13px;
  padding: 8px 14px;
  border-radius: 20px;
  transition: all 0.3s;
  border-width: 2px;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.08);
}

.preview-tag:hover {
  transform: translateY(-2px) scale(1.05);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.preview-tag .tag-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  display: inline-block;
  box-shadow: 0 0 4px rgba(0, 0, 0, 0.2);
  flex-shrink: 0;
}

.preview-tag .tag-name {
  flex: 1;
  white-space: nowrap;
}

@media (max-width: 768px) {
  .form-row {
    grid-template-columns: 1fr;
  }
  
  .tags-form-section .section-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
}
</style>

