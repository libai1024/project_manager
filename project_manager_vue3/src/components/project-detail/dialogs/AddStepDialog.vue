<template>
  <el-dialog
    :model-value="visible"
    title="添加步骤"
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
      <el-form-item label="步骤名称" prop="name">
        <el-input v-model="form.name" placeholder="请输入步骤名称" />
      </el-form-item>
      <el-form-item label="截止时间">
        <el-date-picker
          v-model="form.deadline"
          type="datetime"
          placeholder="选择截止时间"
          style="width: 100%"
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
import { ref, reactive, watch } from 'vue'
import type { FormInstance, FormRules } from 'element-plus'

interface StepForm {
  name: string
  deadline?: Date
}

const props = defineProps<{
  visible: boolean
}>()

const emit = defineEmits<{
  (e: 'update:visible', value: boolean): void
  (e: 'submit', data: StepForm): void
}>()

const formRef = ref<FormInstance>()

const form = reactive<StepForm>({
  name: '',
  deadline: undefined,
})

const rules: FormRules = {
  name: [{ required: true, message: '请输入步骤名称', trigger: 'blur' }],
}

const resetForm = () => {
  form.name = ''
  form.deadline = undefined
  formRef.value?.resetFields()
}

const handleClose = () => {
  resetForm()
}

const handleSubmit = async () => {
  const valid = await formRef.value?.validate()
  if (valid) {
    emit('submit', { ...form })
    emit('update:visible', false)
    resetForm()
  }
}

// Reset form when dialog opens
watch(() => props.visible, (val) => {
  if (!val) {
    resetForm()
  }
})
</script>
