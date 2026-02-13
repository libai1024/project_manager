import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import zhCn from 'element-plus/dist/locale/zh-cn.mjs'
import router from './router'
import App from './App.vue'
import { useUserStore } from './stores/user'
import './styles/theme.css'
import './styles/element-plus-theme.css'
import './styles/components.css'
import './styles/mobile.css'
import './style.css'

const app = createApp(App)
const pinia = createPinia()

// 注册所有图标
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

app.use(pinia)
app.use(router)

/**
 * 应用初始化
 * 
 * 职责：
 * - 同步 token 状态
 * - 恢复用户会话（如果 token 有效）
 */
const userStore = useUserStore()

// 同步 token（从 localStorage 到 store）
userStore.syncToken()

// 如果存在 token，尝试恢复用户会话
if (userStore.isAuthenticated) {
  // 尝试获取用户信息，如果失败会自动清除 token
  userStore.fetchUserInfo().catch(() => {
    // fetchUserInfo 内部已经处理了 401 错误并调用 logout
    // 这里不需要额外处理
  })
}

app.use(ElementPlus, {
  locale: zhCn,
})

app.mount('#app')
