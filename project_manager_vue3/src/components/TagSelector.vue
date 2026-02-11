<template>
  <div class="tag-selector">
    <!-- 搜索栏 -->
    <div class="search-section">
      <el-input
        v-model="searchKeyword"
        placeholder="搜索标签..."
        clearable
        size="large"
        class="search-input"
      >
        <template #prefix>
          <el-icon><Search /></el-icon>
        </template>
      </el-input>
    </div>

    <!-- 快捷操作 -->
    <div v-if="selectedTagIds.length > 0 || allTags.length > 0" class="quick-actions">
      <el-button 
        v-if="selectedTagIds.length > 0"
        text
        type="danger" 
        size="small"
        @click="clearAll"
        class="action-btn"
      >
        <el-icon><Delete /></el-icon>
        清除全部 ({{ selectedTagIds.length }})
      </el-button>
      <el-button 
        v-if="filteredCommonTags.length > 0 && selectedTagIds.length < filteredCommonTags.length"
        text
        type="primary" 
        size="small"
        @click="selectAllCommon"
        class="action-btn"
      >
        <el-icon><Check /></el-icon>
        全选常用标签
      </el-button>
    </div>

    <!-- 常用标签 -->
    <div v-if="filteredCommonTags.length > 0" class="common-tags-section">
      <div class="section-header">
        <div class="section-title">
          <el-icon class="title-icon"><StarFilled /></el-icon>
          <span>常用标签</span>
          <el-tag size="small" type="info" class="count-badge">{{ filteredCommonTags.length }}</el-tag>
        </div>
      </div>
      <div class="tags-list">
        <el-tag
          v-for="tag in filteredCommonTags"
          :key="tag.id"
          :style="{
            backgroundColor: selectedTagIds.includes(tag.id) ? getTagBackgroundColor(tag.color) : '#f5f7fa',
            borderColor: tag.color || '#409eff',
            color: selectedTagIds.includes(tag.id) ? tag.color || '#409eff' : '#606266',
            fontWeight: selectedTagIds.includes(tag.id) ? '600' : '500'
          }"
          :effect="selectedTagIds.includes(tag.id) ? 'dark' : 'plain'"
          class="tag-item"
          :class="{ 'tag-selected': selectedTagIds.includes(tag.id) }"
          @click="toggleTag(tag.id)"
        >
          <span class="tag-dot" :style="{ backgroundColor: tag.color || '#409eff' }"></span>
          <span class="tag-name">{{ tag.name }}</span>
          <el-icon v-if="selectedTagIds.includes(tag.id)" class="check-icon"><Check /></el-icon>
        </el-tag>
      </div>
    </div>

    <!-- 我的标签 -->
    <div v-if="filteredMyTags.length > 0" class="my-tags-section">
      <div class="section-header">
        <div class="section-title">
          <el-icon class="title-icon"><User /></el-icon>
          <span>我的标签</span>
          <el-tag size="small" type="info" class="count-badge">{{ filteredMyTags.length }}</el-tag>
        </div>
      </div>
      <div class="tags-list">
        <el-tag
          v-for="tag in filteredMyTags"
          :key="tag.id"
          :style="{
            backgroundColor: selectedTagIds.includes(tag.id) ? getTagBackgroundColor(tag.color) : '#f5f7fa',
            borderColor: tag.color || '#409eff',
            color: selectedTagIds.includes(tag.id) ? tag.color || '#409eff' : '#606266',
            fontWeight: selectedTagIds.includes(tag.id) ? '600' : '500'
          }"
          :effect="selectedTagIds.includes(tag.id) ? 'dark' : 'plain'"
          class="tag-item"
          :class="{ 'tag-selected': selectedTagIds.includes(tag.id) }"
          @click="toggleTag(tag.id)"
        >
          <span class="tag-dot" :style="{ backgroundColor: tag.color || '#409eff' }"></span>
          <span class="tag-name">{{ tag.name }}</span>
          <el-icon v-if="selectedTagIds.includes(tag.id)" class="check-icon"><Check /></el-icon>
          <!-- 标签全局共享，所有标签都可以删除（需要管理员权限） -->
          <el-icon class="delete-icon" @click.stop="handleDeleteTag(tag)">
            <Close />
          </el-icon>
        </el-tag>
      </div>
    </div>

    <!-- 无结果提示 -->
    <div v-if="filteredCommonTags.length === 0 && filteredMyTags.length === 0 && searchKeyword" class="no-results">
      <el-empty description="没有找到匹配的标签" :image-size="60" />
    </div>

    <!-- 创建新标签 -->
    <div class="create-tag-section">
      <div class="create-header">
        <el-icon class="create-icon"><Plus /></el-icon>
        <span>创建新标签</span>
      </div>
      <el-input
        v-model="newTagName"
        placeholder="输入标签名称，按回车创建"
        size="large"
        clearable
        @keyup.enter="handleCreateTag"
        class="create-input"
      >
        <template #append>
          <el-button 
            @click="handleCreateTag" 
            :disabled="!newTagName.trim()"
            type="primary"
            :loading="creating"
          >
            <el-icon><Plus /></el-icon>
            创建
          </el-button>
        </template>
      </el-input>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Close, Search, StarFilled, User, Check, Delete, PriceTag } from '@element-plus/icons-vue'
import { tagApi, type Tag } from '@/api/tag'

interface Props {
  modelValue: number[]  // 选中的标签ID列表
  multiple?: boolean    // 是否多选
}

interface Emits {
  (e: 'update:modelValue', value: number[]): void
}

const props = withDefaults(defineProps<Props>(), {
  multiple: true,
})

const emit = defineEmits<Emits>()

const selectedTagIds = computed({
  get: () => props.modelValue || [],
  set: (value) => emit('update:modelValue', value),
})

const commonTags = ref<Tag[]>([])
const myTags = ref<Tag[]>([])
const allTags = computed(() => [...commonTags.value, ...myTags.value])
const newTagName = ref('')
const searchKeyword = ref('')
const loading = ref(false)
const creating = ref(false)

// 过滤标签
const filteredCommonTags = computed(() => {
  if (!searchKeyword.value) return commonTags.value
  const keyword = searchKeyword.value.toLowerCase()
  return commonTags.value.filter(tag => 
    tag.name.toLowerCase().includes(keyword) ||
    (tag.description && tag.description.toLowerCase().includes(keyword))
  )
})

const filteredMyTags = computed(() => {
  if (!searchKeyword.value) return myTags.value
  const keyword = searchKeyword.value.toLowerCase()
  return myTags.value.filter(tag => 
    tag.name.toLowerCase().includes(keyword) ||
    (tag.description && tag.description.toLowerCase().includes(keyword))
  )
})

// 加载标签列表
const loadTags = async () => {
  loading.value = true
  try {
    // 标签全局共享，获取所有标签
    const tags = await tagApi.list(true)
    // 按常用标签和普通标签分类
    commonTags.value = tags.filter(t => t.is_common).sort((a, b) => {
      // 先按使用次数降序，再按名称升序
      if (b.usage_count !== a.usage_count) {
        return b.usage_count - a.usage_count
      }
      return a.name.localeCompare(b.name)
    })
    myTags.value = tags.filter(t => !t.is_common).sort((a, b) => {
      // 先按使用次数降序，再按名称升序
      if (b.usage_count !== a.usage_count) {
        return b.usage_count - a.usage_count
      }
      return a.name.localeCompare(b.name)
    })
    console.log('标签加载成功:', { common: commonTags.value.length, other: myTags.value.length })
  } catch (error) {
    console.error('加载标签失败:', error)
    ElMessage.error('加载标签失败')
  } finally {
    loading.value = false
  }
}

// 清除所有选择
const clearAll = () => {
  selectedTagIds.value = []
  ElMessage.success('已清除所有标签')
}

// 全选常用标签
const selectAllCommon = () => {
  const commonIds = filteredCommonTags.value.map(t => t.id)
  const current = [...selectedTagIds.value]
  // 添加未选中的常用标签
  commonIds.forEach(id => {
    if (!current.includes(id)) {
      current.push(id)
    }
  })
  selectedTagIds.value = current
  ElMessage.success(`已选择 ${commonIds.length} 个常用标签`)
}

// 将十六进制颜色转换为带透明度的颜色
const getTagBackgroundColor = (color: string): string => {
  if (!color) return '#f0f0f015'
  
  if (color.length === 9 && color.startsWith('#')) {
    return color
  }
  
  if (color.length === 7 && color.startsWith('#')) {
    return color + '15'
  }
  
  if (color.length === 4 && color.startsWith('#')) {
    const r = color[1]
    const g = color[2]
    const b = color[3]
    return `#${r}${r}${g}${g}${b}${b}15`
  }
  
  return color + '15'
}

// 切换标签选择
const toggleTag = (tagId: number) => {
  const current = [...selectedTagIds.value]
  const index = current.indexOf(tagId)
  
  if (index > -1) {
    // 取消选择
    current.splice(index, 1)
  } else {
    // 选择标签
    if (props.multiple) {
      current.push(tagId)
    } else {
      current.splice(0, current.length, tagId)  // 单选模式，替换
    }
  }
  
  selectedTagIds.value = current
}

// 检查标签是否存在
const checkTagExists = (tagName: string): Tag | undefined => {
  const normalizedName = tagName.trim().toLowerCase()
  return allTags.value.find(tag => tag.name.toLowerCase() === normalizedName)
}

// 创建新标签
const handleCreateTag = async () => {
  const tagName = newTagName.value.trim()
  if (!tagName) {
    ElMessage.warning('请输入标签名称')
    return
  }

  // 检查标签是否已存在（不区分大小写）
  const existingTag = checkTagExists(tagName)
  if (existingTag) {
    // 如果标签已存在，提示用户选择而不是创建
    ElMessage.warning(`标签"${tagName}"已存在`)
    
    // 如果该标签未被选中，自动选中它
    if (!selectedTagIds.value.includes(existingTag.id)) {
      if (props.multiple) {
        selectedTagIds.value = [...selectedTagIds.value, existingTag.id]
      } else {
        selectedTagIds.value = [existingTag.id]
      }
      ElMessage.info(`已自动选择标签"${tagName}"`)
    } else {
      ElMessage.info(`标签"${tagName}"已被选中`)
    }
    
    // 清空输入框
    newTagName.value = ''
    
    // 设置搜索关键词，高亮显示已存在的标签
    searchKeyword.value = existingTag.name
    
    return
  }

  creating.value = true
  try {
    const newTag = await tagApi.create({
      name: tagName,
      color: getRandomColor(),
      is_common: false,
    })
    
    // 重新加载标签列表（因为标签全局共享，需要获取最新列表）
    await loadTags()
    
    // 从重新加载的列表中获取新创建的标签（确保获取到正确的ID和完整数据）
    const createdTag = allTags.value.find(t => t.name === tagName)
    const tagToSelect = createdTag || newTag
    
    const createdTagName = tagName
    newTagName.value = ''
    ElMessage.success(`标签"${createdTagName}"创建成功`)
    
    // 自动选中新创建的标签
    if (props.multiple) {
      selectedTagIds.value = [...selectedTagIds.value, tagToSelect.id]
    } else {
      selectedTagIds.value = [tagToSelect.id]
    }
    
    // 清空搜索，显示新标签
    searchKeyword.value = ''
  } catch (error: any) {
    console.error('创建标签失败:', error)
    const errorMessage = error.response?.data?.detail || '创建标签失败'
    
    // 如果错误提示标签已存在，尝试查找并选择该标签
    if (errorMessage.includes('已存在')) {
      const existingTag = checkTagExists(tagName)
      if (existingTag && !selectedTagIds.value.includes(existingTag.id)) {
        if (props.multiple) {
          selectedTagIds.value = [...selectedTagIds.value, existingTag.id]
        } else {
          selectedTagIds.value = [existingTag.id]
        }
        ElMessage.info(`标签已存在，已自动选择`)
        searchKeyword.value = existingTag.name
      } else {
        ElMessage.error(errorMessage)
      }
    } else {
      ElMessage.error(errorMessage)
    }
  } finally {
    creating.value = false
  }
}

// 删除标签
const handleDeleteTag = async (tag: Tag) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除标签"${tag.name}"吗？此操作将影响所有使用该标签的项目。`,
      '删除标签',
      {
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )
    
    await tagApi.delete(tag.id)
    
    // 从列表中移除（标签全局共享，需要从两个列表中查找）
    const commonIndex = commonTags.value.findIndex(t => t.id === tag.id)
    if (commonIndex > -1) {
      commonTags.value.splice(commonIndex, 1)
    }
    
    const myIndex = myTags.value.findIndex(t => t.id === tag.id)
    if (myIndex > -1) {
      myTags.value.splice(myIndex, 1)
    }
    
    // 从选中列表中移除
    const selectedIndex = selectedTagIds.value.indexOf(tag.id)
    if (selectedIndex > -1) {
      selectedTagIds.value = selectedTagIds.value.filter(id => id !== tag.id)
    }
    
    ElMessage.success('标签删除成功')
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('删除标签失败:', error)
      ElMessage.error(error.response?.data?.detail || '删除标签失败')
    }
  }
}

// 生成随机颜色
const getRandomColor = (): string => {
  const colors = [
    '#409eff', '#67c23a', '#e6a23c', '#f56c6c', '#909399',
    '#9c27b0', '#00bcd4', '#ff9800', '#4caf50', '#2196f3',
  ]
  return colors[Math.floor(Math.random() * colors.length)]
}

onMounted(() => {
  loadTags()
})
</script>

<style scoped>
.tag-selector {
  padding: 0;
  background: transparent;
}

/* 搜索区域 */
.search-section {
  margin-bottom: 16px;
}

.search-input :deep(.el-input__wrapper) {
  border-radius: 8px;
  transition: all 0.3s;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.06);
}

.search-input :deep(.el-input__wrapper:hover) {
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.15);
}

/* 快捷操作 */
.quick-actions {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
  padding: 12px;
  background: #f5f7fa;
  border-radius: 8px;
  flex-wrap: wrap;
}

.action-btn {
  border-radius: 6px;
  font-size: 12px;
  padding: 6px 12px;
  transition: all 0.3s;
}

.action-btn:hover {
  background-color: rgba(64, 158, 255, 0.1);
}

/* 区域标题 */
.section-header {
  margin-bottom: 12px;
}

.section-title {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 12px;
  background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
  border-radius: 8px;
  border-left: 3px solid #409eff;
}

.title-icon {
  font-size: 16px;
  color: #409eff;
}

.count-badge {
  margin-left: 4px;
  font-size: 11px;
  height: 18px;
  line-height: 18px;
  padding: 0 6px;
}

.common-tags-section,
.my-tags-section {
  margin-bottom: 24px;
}

.tags-list {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  padding: 12px;
  background: #ffffff;
  border-radius: 8px;
  border: 1px solid #e4e7ed;
  min-height: 60px;
  transition: all 0.3s;
}

.tags-list:hover {
  border-color: #c0c4cc;
}

.tag-item {
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  user-select: none;
  position: relative;
  padding: 8px 16px;
  border-radius: 20px;
  font-size: 13px;
  border-width: 2px;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.08);
}

.tag-item:hover {
  transform: translateY(-2px) scale(1.05);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.tag-item:active {
  transform: translateY(0) scale(1.02);
}

.tag-item.tag-selected {
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.25);
  border-width: 2px;
}

.tag-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  display: inline-block;
  box-shadow: 0 0 4px rgba(0, 0, 0, 0.2);
  flex-shrink: 0;
}

.tag-name {
  flex: 1;
  white-space: nowrap;
}

.check-icon {
  font-size: 14px;
  margin-left: 4px;
}

.delete-icon {
  margin-left: 4px;
  font-size: 14px;
  cursor: pointer;
  opacity: 0.6;
  transition: all 0.3s;
  padding: 2px;
  border-radius: 50%;
  background: rgba(0, 0, 0, 0.05);
}

.delete-icon:hover {
  opacity: 1;
  background: rgba(245, 108, 108, 0.2);
  color: #f56c6c;
  transform: scale(1.2);
}

/* 无结果 */
.no-results {
  padding: 40px 20px;
  text-align: center;
}

/* 创建标签区域 */
.create-tag-section {
  margin-top: 24px;
  padding: 16px;
  background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);
  border-radius: 8px;
  border: 2px dashed #d3d4d6;
  transition: all 0.3s;
}

.create-tag-section:hover {
  border-color: #409eff;
  background: linear-gradient(135deg, #f0f9ff 0%, #ffffff 100%);
}

.create-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
  font-size: 13px;
  font-weight: 600;
  color: #606266;
}

.create-icon {
  font-size: 16px;
  color: #409eff;
}

.create-input :deep(.el-input__wrapper) {
  border-radius: 8px 0 0 8px;
  transition: all 0.3s;
}

.create-input :deep(.el-input__wrapper:hover) {
  box-shadow: 0 0 0 1px #409eff inset;
}

.create-input :deep(.el-input-group__append) {
  border-radius: 0 8px 8px 0;
}

.create-input :deep(.el-button) {
  border-radius: 0 8px 8px 0;
  transition: all 0.3s;
  padding: 12px 20px;
}

.create-input :deep(.el-button:hover) {
  background-color: #409eff;
  color: #fff;
}
</style>

