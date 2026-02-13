<template>
  <el-dialog
    :model-value="visible"
    title="移入文件夹"
    width="400px"
    @update:model-value="$emit('update:visible', $event)"
    @close="handleClose"
  >
    <el-form @submit.prevent="handleConfirm">
      <el-form-item label="选择文件夹">
        <el-select v-model="selectedFolderId" clearable placeholder="选择目标文件夹" style="width: 100%">
          <el-option
            v-for="folder in folders"
            :key="folder.id"
            :label="folder.name"
            :value="folder.id"
          />
        </el-select>
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="$emit('update:visible', false)">取消</el-button>
      <el-button type="primary" @click="handleConfirm">确定</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import type { AttachmentFolder } from '@/api/attachmentFolder'

const props = defineProps<{
  visible: boolean
  folders: AttachmentFolder[]
}>()

const emit = defineEmits<{
  (e: 'update:visible', value: boolean): void
  (e: 'confirm', folderId: number | null): void
}>()

const selectedFolderId = ref<number | null>(null)

const handleClose = () => {
  selectedFolderId.value = null
}

const handleConfirm = () => {
  emit('confirm', selectedFolderId.value)
  emit('update:visible', false)
  selectedFolderId.value = null
}

watch(() => props.visible, (val) => {
  if (!val) {
    selectedFolderId.value = null
  }
})
</script>
