<template>
  <el-card class="project-info-card">
    <template #header>
      <div class="card-header">
        <span>项目详情</span>
        <div>
          <el-button @click="$emit('go-back')">返回</el-button>
          <el-button v-if="canEdit" type="primary" @click="$emit('edit')">编辑</el-button>
          <el-button 
            v-if="canSettle" 
            type="success" 
            @click="$emit('settle')"
            :loading="settling"
          >
            <el-icon><Money /></el-icon>
            结账
          </el-button>
        </div>
      </div>
    </template>

    <el-descriptions :column="isMobile ? 1 : 2" border v-if="project">
      <!-- 调试信息 -->
      <!-- <div style="padding: 10px; background: #f0f0f0; margin-bottom: 10px;">
        <p>Tags Debug: {{ JSON.stringify(project.tags) }}</p>
        <p>Tags Length: {{ project.tags?.length || 0 }}</p>
        <p>Has Tags: {{ project.tags && project.tags.length > 0 }}</p>
      </div> -->
      <el-descriptions-item label="项目名称">{{ project.title }}</el-descriptions-item>
      <el-descriptions-item label="学生姓名">{{ project.student_name || '-' }}</el-descriptions-item>
      <el-descriptions-item label="接单平台">{{ project.platform?.name }}</el-descriptions-item>
      <el-descriptions-item label="订单金额">¥{{ project.price.toFixed(2) }}</el-descriptions-item>
      <el-descriptions-item label="实际收入">¥{{ project.actual_income.toFixed(2) }}</el-descriptions-item>
      <el-descriptions-item label="项目状态">
        <el-tag :type="getStatusType(project.status)">{{ project.status }}</el-tag>
      </el-descriptions-item>
      <el-descriptions-item label="结账状态">
        <el-tag :type="project.is_paid ? 'success' : 'info'" :class="{ 'settled-tag': project.is_paid }">
          {{ project.is_paid ? '已结账' : '未结账' }}
        </el-tag>
      </el-descriptions-item>
      <el-descriptions-item label="项目标签" :span="isMobile ? 1 : 2">
        <div class="tags-display">
          <template v-if="projectTags.length > 0">
            <el-tag
              v-for="tag in projectTags"
              :key="tag.id"
              :style="{
                backgroundColor: getTagBackgroundColor(tag.color),
                borderColor: tag.color || '#409eff',
                color: tag.color || '#409eff',
                fontWeight: '600'
              }"
              size="default"
              class="project-tag"
              effect="plain"
              round
              @click.stop="handleTagClick(tag)"
            >
              <span class="tag-dot" :style="{ backgroundColor: tag.color || '#409eff' }"></span>
              <span class="tag-name">{{ tag.name }}</span>
              <el-icon class="tag-icon"><PriceTag /></el-icon>
            </el-tag>
          </template>
          <div v-else class="no-tag-wrapper">
            <el-empty 
              :image-size="80" 
              description="暂无标签"
              class="no-tag-empty"
            >
              <template #image>
                <el-icon class="empty-icon"><PriceTag /></el-icon>
              </template>
              <el-button 
                v-if="canEdit"
                type="primary" 
                size="small" 
                @click="$emit('edit')"
                class="add-tag-btn"
              >
                <el-icon><Plus /></el-icon>
                添加标签
              </el-button>
            </el-empty>
          </div>
        </div>
      </el-descriptions-item>
    </el-descriptions>
  </el-card>
</template>

<script setup lang="ts">
import { ref, watch, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { Money, PriceTag, Plus } from '@element-plus/icons-vue'
import type { Project } from '@/api/project'
import type { Tag } from '@/api/tag'
import { tagApi } from '@/api/tag'

interface Props {
  project: Project | null
  canEdit: boolean
  canSettle: boolean
  settling: boolean
  isMobile: boolean
}

const props = defineProps<Props>()
const router = useRouter()

defineEmits<{
  'go-back': []
  'edit': []
  'settle': []
}>()

// 所有标签列表
const allTags = ref<Tag[]>([])
// 项目标签（从标签API获取后过滤）
const projectTags = ref<Tag[]>([])

// 加载所有标签
const loadAllTags = async () => {
  try {
    console.log('ProjectInfoCard - loading all tags...')
    allTags.value = await tagApi.list(true)
    console.log('ProjectInfoCard - loaded tags:', allTags.value.length)
    updateProjectTags()
  } catch (error) {
    console.error('Failed to load tags:', error)
  }
}

// 根据项目的标签数据更新项目标签
const updateProjectTags = () => {
  if (!props.project) {
    projectTags.value = []
    console.log('ProjectInfoCard - updateProjectTags: no project')
    return
  }
  
  // 如果还没有加载所有标签，先等待
  if (allTags.value.length === 0) {
    console.log('ProjectInfoCard - updateProjectTags: tags not loaded yet')
    return
  }
  
  console.log('ProjectInfoCard - updateProjectTags:', {
    project: props.project,
    projectTags: props.project.tags,
    allTagsCount: allTags.value.length
  })
  
  // 如果项目有 tags 数组
  if (props.project.tags && Array.isArray(props.project.tags) && props.project.tags.length > 0) {
    // 提取标签ID（支持完整标签对象或只有ID的情况）
    const tagIds: number[] = []
    for (const tag of props.project.tags) {
      if (typeof tag === 'number') {
        tagIds.push(tag)
      } else if (tag && typeof tag === 'object' && 'id' in tag) {
        tagIds.push(tag.id as number)
      }
    }
    
    console.log('ProjectInfoCard - extracted tagIds:', tagIds)
    
    // 从所有标签中查找对应的标签（使用标签API的完整数据）
    if (tagIds.length > 0) {
      projectTags.value = allTags.value.filter(tag => tagIds.includes(tag.id))
      console.log('ProjectInfoCard - matched tags:', projectTags.value)
      return
    }
  }
  
  console.log('ProjectInfoCard - no tags found')
  projectTags.value = []
}

// 监听项目变化
watch(() => props.project, () => {
  updateProjectTags()
}, { immediate: true, deep: true })

// 监听所有标签变化，当标签加载完成后也要更新项目标签
watch(() => allTags.value, () => {
  if (allTags.value.length > 0) {
    updateProjectTags()
  }
}, { deep: true })

// 组件挂载时加载标签
onMounted(() => {
  loadAllTags()
})

const getStatusType = (status: string) => {
  const statusMap: Record<string, string> = {
    '进行中': 'warning',
    '已完成': 'success',
    '已暂停': 'info',
    '已取消': 'danger'
  }
  return statusMap[status] || 'info'
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

// 点击标签跳转到项目管理页面并筛选
const handleTagClick = (tag: any) => {
  router.push({
    path: '/projects',
    query: { tag_ids: tag.id.toString() }
  })
}
</script>

<style scoped>
.project-info-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.settled-tag {
  font-weight: 600;
}

.tags-display {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  align-items: center;
}

.project-tag {
  font-size: 13px;
  padding: 8px 16px;
  border-radius: 20px;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  display: inline-flex;
  align-items: center;
  gap: 8px;
  border-width: 2px;
  position: relative;
  overflow: hidden;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.08);
}

.project-tag::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
  transition: left 0.5s;
}

.project-tag:hover::before {
  left: 100%;
}

.project-tag:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  border-width: 2px;
}

.project-tag:active {
  transform: translateY(0);
}

.tag-name {
  font-weight: 500;
  letter-spacing: 0.3px;
}

.tag-icon {
  font-size: 12px;
  opacity: 0.8;
}

.tag-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  display: inline-block;
  margin-right: 6px;
  box-shadow: 0 0 4px rgba(0, 0, 0, 0.2);
}

.no-tag-wrapper {
  padding: 20px;
  text-align: center;
}

.no-tag-empty {
  padding: 0;
}

.empty-icon {
  font-size: 48px;
  color: #c0c4cc;
  margin-bottom: 8px;
}

.add-tag-btn {
  margin-top: 12px;
  border-radius: 16px;
  padding: 8px 20px;
  font-weight: 500;
}

/* 移动端样式 */
@media (max-width: 768px) {
  .project-info-card {
    margin-bottom: 12px;
  }

  .project-info-card :deep(.el-card__header) {
    padding: 12px;
  }

  .project-info-card :deep(.el-card__body) {
    padding: 12px;
  }

  .card-header {
    flex-direction: column;
    align-items: stretch;
    gap: 10px;
  }

  .card-header > div {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
  }

  .card-header .el-button {
    flex: 1;
    min-width: 80px;
    font-size: 13px;
    padding: 8px 12px;
  }

  .project-info-card :deep(.el-descriptions) {
    font-size: 13px;
  }

  .project-info-card :deep(.el-descriptions__label) {
    font-size: 12px;
    padding: 10px 8px;
    min-width: 70px;
  }

  .project-info-card :deep(.el-descriptions__content) {
    font-size: 13px;
    padding: 10px 8px;
  }

  .tags-display {
    gap: 6px;
  }

  .project-tag {
    font-size: 11px;
    padding: 5px 10px;
    border-radius: 14px;
    gap: 4px;
  }

  .tag-dot {
    width: 6px;
    height: 6px;
  }

  .tag-icon {
    font-size: 10px;
  }

  .no-tag-wrapper {
    padding: 12px;
  }

  .empty-icon {
    font-size: 36px;
  }

  .add-tag-btn {
    font-size: 12px;
    padding: 6px 16px;
  }
}

@media (max-width: 480px) {
  .project-info-card :deep(.el-descriptions__label) {
    min-width: 60px;
    font-size: 11px;
  }

  .project-info-card :deep(.el-descriptions__content) {
    font-size: 12px;
  }

  .card-header .el-button {
    font-size: 12px;
    padding: 6px 10px;
  }

  .project-tag {
    font-size: 10px;
    padding: 4px 8px;
  }
}
</style>

