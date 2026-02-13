<template>
  <el-dialog
    :model-value="visible"
    title="上传文件"
    width="500px"
    @update:model-value="$emit('update:visible', $event)"
    @close="handleClose"
  >
    <el-form
      ref="formRef"
      :model="form"
      :rules="rules"
      label-width="100px"
    >
      <el-form-item label="选择文件" prop="file">
        <el-upload
          ref="uploadRef"
          :auto-upload="false"
          :limit="1"
          :on-change="handleFileChange"
          :on-remove="handleFileRemove"
          drag
          class="upload-dragger"
        >
          <el-icon class="el-icon--upload"><Upload /></el-icon>
          <div class="el-upload__text">
            将文件拖到此处，或<em>点击上传</em>
          </div>
          <template #tip>
            <div class="el-upload__tip">支持所有文件类型，单个文件不超过1GB</div>
          </template>
        </el-upload>
      </el-form-item>
      <el-form-item label="文件类型">
        <el-select v-model="form.file_type" style="width: 100%">
          <el-option label="需求" value="需求" />
          <el-option label="开题报告" value="开题报告" />
          <el-option label="初稿" value="初稿" />
          <el-option label="终稿" value="终稿" />
          <el-option label="其他" value="其他" />
        </el-select>
      </el-form-item>
      <el-form-item label="描述">
        <el-input
          v-model="form.description"
          type="textarea"
          :rows="3"
          placeholder="文件描述（可选）"
        />
      </el-form-item>
      <el-form-item label="文件夹">
        <el-select
          v-model="form.folder_id"
          clearable
          placeholder="选择文件夹（可选）"
          style="width: 100%;"
          @change="handleFolderChange"
        >
          <el-option
            v-for="folder in folders"
            :key="folder.id"
            :label="folder.name"
            :value="folder.id"
          />
          <el-option
            value="__create__"
            label="+ 新建文件夹"
            class="create-folder-option"
          >
            <span style="display: flex; align-items: center; gap: 4px;">
              <el-icon><Plus /></el-icon>
              <span>新建文件夹</span>
            </span>
          </el-option>
        </el-select>
      </el-form-item>
      <el-form-item v-if="uploading">
        <el-progress :percentage="uploadProgress" :status="uploadProgress === 100 ? 'success' : undefined" />
        <div style="text-align: center; margin-top: 8px; color: #909399; font-size: 12px;">
          {{ uploadProgress }}% - 正在上传文件...
        </div>
      </el-form-item>
    </el-form>

    <template #footer>
      <el-button @click="$emit('update:visible', false)" :disabled="uploading">取消</el-button>
      <el-button type="primary" :loading="uploading" :disabled="uploading" @click="handleSubmit">
        {{ uploading ? `上传中 ${uploadProgress}%` : '上传' }}
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, reactive, watch } from 'vue'
import { Upload, Plus } from '@element-plus/icons-vue'
import type { FormInstance, FormRules, UploadFile } from 'element-plus'
import type { AttachmentFolder } from '@/api/attachmentFolder'

interface UploadForm {
  file: File | null
  file_type: string
  description: string
  folder_id: number | undefined
}

const props = defineProps<{
  visible: boolean
  folders: AttachmentFolder[]
  uploading: boolean
  uploadProgress: number
}>()

const emit = defineEmits<{
  (e: 'update:visible', value: boolean): void
  (e: 'submit', data: UploadForm): void
  (e: 'create-folder'): void
}>()

const formRef = ref<FormInstance>()

const form = reactive<UploadForm>({
  file: null,
  file_type: '其他',
  description: '',
  folder_id: undefined,
})

const rules: FormRules = {
  file: [{ required: true, message: '请选择文件', trigger: 'change' }],
}

const handleFileChange = (file: UploadFile) => {
  if (file.raw) {
    form.file = file.raw
  }
}

const handleFileRemove = () => {
  form.file = null
}

const handleFolderChange = (value: number | string | null) => {
  if (value === '__create__') {
    form.folder_id = undefined
    emit('create-folder')
  } else {
    form.folder_id = typeof value === 'number' ? value : undefined
  }
}

const handleClose = () => {
  form.file = null
  form.file_type = '其他'
  form.description = ''
  form.folder_id = undefined
  formRef.value?.resetFields()
}

const handleSubmit = async () => {
  if (!form.file) {
    formRef.value?.validateField('file')
    return
  }
  emit('submit', { ...form })
}

watch(() => props.visible, (val) => {
  if (!val) {
    handleClose()
  }
})
</script>

<style scoped>
.upload-dragger {
  width: 100%;
}

:deep(.el-upload-dragger) {
  width: 100%;
}
</style>
