<template>
  <el-dialog
    :model-value="visible"
    title="新建文件夹"
    width="400px"
    @update:model-value="$emit('update:visible', $event)"
    @close="handleClose"
  >
    <el-form @submit.prevent="handleSubmit">
      <el-form-item label="文件夹名称">
        <el-input
          v-model="folderName"
          placeholder="请输入文件夹名称"
          @keyup.enter="handleSubmit"
        />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="$emit('update:visible', false)">取消</el-button>
      <el-button type="primary" @click="handleSubmit">确定</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'

const props = defineProps<{
  visible: boolean
}>()

const emit = defineEmits<{
  (e: 'update:visible', value: boolean): void
  (e: 'submit', name: string): void
}>()

const folderName = ref('')

const handleClose = () => {
  folderName.value = ''
}

const handleSubmit = () => {
  if (folderName.value.trim()) {
    emit('submit', folderName.value.trim())
    emit('update:visible', false)
    folderName.value = ''
  }
}

watch(() => props.visible, (val) => {
  if (!val) {
    folderName.value = ''
  }
})
</script>
