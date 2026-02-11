<template>
  <el-card v-if="project" class="project-tags-card">
    <template #header>
      <div class="card-header">
        <div class="header-left">
          <el-icon class="header-icon"><PriceTag /></el-icon>
          <span class="card-title">项目标签</span>
          <el-tag v-if="project.tags && project.tags.length > 0" type="info" size="small" class="tag-count">
            {{ project.tags.length }} 个标签
          </el-tag>
        </div>
        <el-button
          v-if="canEdit"
          type="text"
          size="small"
          @click="$emit('edit')"
          class="edit-tags-btn"
        >
          <el-icon><Edit /></el-icon>
          编辑标签
        </el-button>
      </div>
    </template>
    <div v-if="project.tags && project.tags.length > 0" class="tags-container">
      <div
        v-for="tag in project.tags"
        :key="tag.id"
        class="tag-chip"
        :style="{
          backgroundColor: getTagBackgroundColor(tag.color),
          borderColor: tag.color || '#409eff',
          color: tag.color || '#409eff'
        }"
        @click="handleTagClick(tag)"
      >
        <div class="tag-content">
          <div class="tag-dot" :style="{ backgroundColor: tag.color }"></div>
          <span class="tag-text">{{ tag.name }}</span>
          <el-icon class="tag-arrow"><ArrowRight /></el-icon>
        </div>
        <div v-if="tag.description" class="tag-description">{{ tag.description }}</div>
      </div>
    </div>
    <el-empty v-else description="暂无标签，点击编辑按钮添加标签" :image-size="80">
      <el-button v-if="canEdit" type="primary" size="small" @click="$emit('edit')">
        <el-icon><Plus /></el-icon>
        添加标签
      </el-button>
    </el-empty>
  </el-card>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { PriceTag, Edit, Plus, ArrowRight } from '@element-plus/icons-vue'
import type { Project } from '@/api/project'

interface Props {
  project: Project | null
  canEdit: boolean
}

defineProps<Props>()
defineEmits<{
  edit: []
}>()

const router = useRouter()

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

const handleTagClick = (tag: any) => {
  router.push({
    path: '/projects',
    query: { tag_ids: tag.id.toString() }
  })
}
</script>

<style scoped>
.project-tags-card {
  margin-bottom: 20px;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
}

.project-tags-card:hover {
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.12);
}

.project-tags-card .card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);
  border-bottom: 1px solid #ebeef5;
}

.project-tags-card .header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.project-tags-card .header-icon {
  font-size: 20px;
  color: #409eff;
}

.project-tags-card .card-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.project-tags-card .tag-count {
  font-size: 12px;
  padding: 2px 8px;
}

.project-tags-card .edit-tags-btn {
  color: #409eff;
  font-size: 13px;
  padding: 4px 8px;
  border-radius: 4px;
  transition: all 0.3s;
}

.project-tags-card .edit-tags-btn:hover {
  background-color: #ecf5ff;
  color: #66b1ff;
}

.tags-container {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 12px;
  padding: 16px;
}

.tag-chip {
  padding: 14px 16px;
  border-radius: 10px;
  border: 2px solid;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.9) 0%, rgba(255, 255, 255, 0.7) 100%);
  position: relative;
  overflow: hidden;
}

.tag-chip::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.4), transparent);
  transition: left 0.5s;
}

.tag-chip:hover::before {
  left: 100%;
}

.tag-chip:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
  border-width: 2.5px;
}

.tag-chip:active {
  transform: translateY(-2px);
}

.tag-content {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 6px;
}

.tag-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  flex-shrink: 0;
}

.tag-text {
  flex: 1;
  font-weight: 500;
  font-size: 14px;
}

.tag-arrow {
  opacity: 0;
  transition: all 0.3s;
  font-size: 16px;
}

.tag-chip:hover .tag-arrow {
  opacity: 1;
  transform: translateX(4px);
}

.tag-description {
  font-size: 12px;
  color: #909399;
  margin-top: 6px;
  padding-top: 6px;
  border-top: 1px solid rgba(0, 0, 0, 0.05);
  line-height: 1.4;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

@media (max-width: 768px) {
  .tags-container {
    grid-template-columns: 1fr;
  }
  
  .project-tags-card .card-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
}
</style>

