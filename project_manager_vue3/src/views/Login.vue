<template>
  <div class="login-container">
    <!-- 背景装饰 -->
    <div class="bg-decoration">
      <div class="bg-pattern"></div>
      <div class="bg-leaf bg-leaf-1"></div>
      <div class="bg-leaf bg-leaf-2"></div>
    </div>

    <!-- 登录卡片 -->
    <div class="login-wrapper">
      <div class="login-card">
        <!-- Logo 区域 -->
        <div class="login-header">
          <div class="logo-container">
            <div class="logo-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M12 2L2 7l10 5 10-5-10-5z" />
                <path d="M2 17l10 5 10-5" />
                <path d="M2 12l10 5 10-5" />
              </svg>
            </div>
          </div>
          <h1 class="login-title">项目管理系统</h1>
          <p class="login-subtitle">外包项目高效管理平台</p>
        </div>

        <!-- 表单区域 -->
        <el-form
          ref="loginFormRef"
          :model="loginForm"
          :rules="rules"
          class="login-form"
          @submit.prevent="handleLogin"
        >
          <el-form-item prop="username">
            <div class="input-wrapper">
              <label class="input-label">用户名</label>
              <el-input
                v-model="loginForm.username"
                placeholder="请输入用户名"
                size="large"
                :prefix-icon="User"
                @keyup.enter="handleLogin"
              />
            </div>
          </el-form-item>

          <el-form-item prop="password">
            <div class="input-wrapper">
              <label class="input-label">密码</label>
              <el-input
                v-model="loginForm.password"
                type="password"
                placeholder="请输入密码"
                size="large"
                :prefix-icon="Lock"
                show-password
                @keyup.enter="handleLogin"
              />
            </div>
          </el-form-item>

          <el-form-item class="login-button-item">
            <el-button
              type="primary"
              size="large"
              :loading="loading"
              class="login-button"
              @click="handleLogin"
            >
              <span v-if="!loading">登 录</span>
              <span v-else>登录中...</span>
            </el-button>
          </el-form-item>
        </el-form>

        <!-- 提示信息 -->
        <div class="login-footer">
          <div class="login-tip">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="tip-icon">
              <circle cx="12" cy="12" r="10" />
              <path d="M12 16v-4M12 8h.01" />
            </svg>
            <span>默认账号：admin / admin123</span>
          </div>
        </div>
      </div>

      <!-- 版权信息 -->
      <div class="copyright">
        <p>Outsource Project Management System</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { User, Lock } from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()
const loginFormRef = ref<FormInstance>()
const loading = ref(false)

const loginForm = reactive({
  username: '',
  password: '',
})

const rules: FormRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6位', trigger: 'blur' },
  ],
}

const handleLogin = async () => {
  if (!loginFormRef.value) return

  await loginFormRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true
      try {
        await userStore.login(loginForm.username, loginForm.password)
        ElMessage.success('登录成功，欢迎回来！')
        router.push('/dashboard')
      } catch (error: any) {
        ElMessage.error(error.response?.data?.detail || '登录失败，请检查账号密码')
      } finally {
        loading.value = false
      }
    }
  })
}
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 50%, #d1fae5 100%);
  position: relative;
  overflow: hidden;
  padding: var(--spacing-md);
}

/* 背景装饰 */
.bg-decoration {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  pointer-events: none;
  overflow: hidden;
}

.bg-pattern {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-image:
    radial-gradient(circle at 20% 80%, rgba(34, 197, 94, 0.08) 0%, transparent 50%),
    radial-gradient(circle at 80% 20%, rgba(14, 165, 233, 0.08) 0%, transparent 50%),
    radial-gradient(circle at 40% 40%, rgba(34, 197, 94, 0.05) 0%, transparent 30%);
}

.bg-leaf {
  position: absolute;
  border-radius: 50%;
  opacity: 0.6;
}

.bg-leaf-1 {
  width: 300px;
  height: 300px;
  top: -100px;
  right: -50px;
  background: radial-gradient(circle, rgba(134, 239, 172, 0.4) 0%, transparent 70%);
  animation: float 15s ease-in-out infinite;
}

.bg-leaf-2 {
  width: 200px;
  height: 200px;
  bottom: -50px;
  left: -50px;
  background: radial-gradient(circle, rgba(125, 211, 252, 0.3) 0%, transparent 70%);
  animation: float 12s ease-in-out infinite reverse;
}

@keyframes float {
  0%, 100% {
    transform: translateY(0) rotate(0deg);
  }
  50% {
    transform: translateY(-20px) rotate(3deg);
  }
}

/* 登录包装器 */
.login-wrapper {
  position: relative;
  z-index: 1;
  width: 100%;
  max-width: 400px;
}

/* 登录卡片 */
.login-card {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-radius: var(--radius-2xl);
  box-shadow:
    0 4px 24px rgba(34, 197, 94, 0.1),
    0 0 0 1px rgba(34, 197, 94, 0.05);
  padding: var(--spacing-2xl);
  animation: slideUp 0.4s ease-out;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Logo 区域 */
.login-header {
  text-align: center;
  margin-bottom: var(--spacing-xl);
}

.logo-container {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  margin-bottom: var(--spacing-md);
}

.logo-icon {
  width: 60px;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%);
  border-radius: var(--radius-xl);
  box-shadow: 0 8px 20px rgba(34, 197, 94, 0.25);
  color: white;
}

.logo-icon svg {
  width: 30px;
  height: 30px;
}

.login-title {
  font-size: var(--font-size-3xl);
  font-weight: var(--font-weight-bold);
  color: var(--text-primary);
  margin: 0 0 var(--spacing-xs) 0;
  letter-spacing: var(--letter-spacing-tight);
}

.login-subtitle {
  font-size: var(--font-size-sm);
  color: var(--text-tertiary);
  margin: 0;
}

/* 表单样式 */
.login-form {
  margin-bottom: var(--spacing-lg);
}

.input-wrapper {
  width: 100%;
}

.input-label {
  display: block;
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  color: var(--text-secondary);
  margin-bottom: var(--spacing-xs);
}

:deep(.el-form-item) {
  margin-bottom: var(--spacing-lg);
}

:deep(.el-input__wrapper) {
  border-radius: var(--radius-md);
  padding: 4px 14px;
  box-shadow: none;
  border: 1px solid var(--border-color);
  transition: all var(--transition-fast);
}

:deep(.el-input__wrapper:hover) {
  border-color: #86efac;
}

:deep(.el-input__wrapper.is-focus) {
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px var(--color-primary-lightest);
}

:deep(.el-input__inner) {
  font-size: var(--font-size-base);
}

:deep(.el-input__prefix-inner) {
  color: var(--text-tertiary);
}

.login-button-item {
  margin-bottom: 0;
  margin-top: var(--spacing-xl);
}

.login-button {
  width: 100%;
  height: 48px;
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-semibold);
  border-radius: var(--radius-md);
  background: #22c55e;
  border: none;
  box-shadow: 0 4px 12px rgba(34, 197, 94, 0.3);
  transition: all var(--transition-fast);
}

.login-button:hover {
  background: #16a34a;
  box-shadow: 0 6px 16px rgba(34, 197, 94, 0.35);
  transform: translateY(-1px);
}

.login-button:active {
  transform: translateY(0);
}

/* 底部提示 */
.login-footer {
  text-align: center;
  padding-top: var(--spacing-lg);
  border-top: 1px solid var(--border-color-light);
}

.login-tip {
  display: inline-flex;
  align-items: center;
  gap: var(--spacing-xs);
  padding: var(--spacing-sm) var(--spacing-md);
  background: #f0fdf4;
  border-radius: var(--radius-full);
  font-size: var(--font-size-xs);
  color: var(--text-tertiary);
}

.tip-icon {
  width: 16px;
  height: 16px;
  color: var(--color-primary);
}

/* 版权信息 */
.copyright {
  text-align: center;
  margin-top: var(--spacing-xl);
}

.copyright p {
  font-size: var(--font-size-xs);
  color: var(--text-tertiary);
  margin: 0;
}

/* 响应式 */
@media (max-width: 768px) {
  .login-container {
    padding: var(--spacing-md);
  }

  .login-card {
    padding: var(--spacing-xl);
  }

  .login-title {
    font-size: var(--font-size-2xl);
  }

  .logo-icon {
    width: 52px;
    height: 52px;
  }

  .logo-icon svg {
    width: 26px;
    height: 26px;
  }

  .bg-leaf-1 {
    width: 200px;
    height: 200px;
  }

  .bg-leaf-2 {
    width: 150px;
    height: 150px;
  }
}

@media (max-width: 480px) {
  .login-card {
    padding: var(--spacing-lg);
    border-radius: var(--radius-xl);
  }

  .login-title {
    font-size: var(--font-size-xl);
  }
}

/* 减少动画偏好 */
@media (prefers-reduced-motion: reduce) {
  .bg-leaf {
    animation: none;
  }

  .login-card {
    animation: none;
  }
}
</style>
