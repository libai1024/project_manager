import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { ElMessage } from 'element-plus'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/login',
      name: 'Login',
      component: () => import('@/views/Login.vue'),
      meta: { requiresAuth: false },
    },
    {
      path: '/',
      component: () => import('@/layouts/MainLayout.vue'),
      redirect: '/dashboard',
      meta: { requiresAuth: true },
      children: [
        {
          path: 'dashboard',
          name: 'Dashboard',
          component: () => import('@/views/Dashboard.vue'),
        },
        {
          path: 'projects',
          name: 'Projects',
          component: () => import('@/views/Projects.vue'),
        },
        {
          path: 'projects/:id',
          name: 'ProjectDetail',
          component: () => import('@/views/ProjectDetail.vue'),
        },
        {
          path: 'platforms',
          name: 'Platforms',
          component: () => import('@/views/Platforms.vue'),
        },
        {
          path: 'users',
          name: 'Users',
          component: () => import('@/views/Users.vue'),
          meta: { requiresAdmin: true },
        },
        {
          path: 'todos',
          name: 'Todos',
          component: () => import('@/views/Todos.vue'),
        },
        {
          path: 'resources',
          name: 'ResourceManager',
          component: () => import('@/views/ResourceManager.vue'),
        },
        {
          path: 'finance',
          name: 'Finance',
          component: () => import('@/views/Finance.vue'),
        },
        {
          path: 'settings',
          name: 'Settings',
          component: () => import('@/views/Settings.vue'),
        },
        {
          path: 'historical-projects',
          name: 'HistoricalProjects',
          component: () => import('@/views/HistoricalProjects.vue'),
        },
        {
          path: 'historical-projects/:id',
          name: 'HistoricalProjectDetail',
          component: () => import('@/views/HistoricalProjectDetail.vue'),
        },
        {
          path: 'historical-projects/import',
          name: 'HistoricalProjectImport',
          component: () => import('@/views/HistoricalProjectImport.vue'),
        },
        {
          path: 'tags',
          name: 'Tags',
          component: () => import('@/views/Tags.vue'),
        },
      ],
    },
    {
      path: '/video/watch/:token',
      name: 'VideoWatch',
      component: () => import('@/views/VideoWatch.vue'),
      meta: { requiresAuth: false },
    },
  ],
})

/**
 * 路由守卫
 * 
 * 职责：
 * - 检查路由是否需要认证
 * - 检查管理员权限
 * - 统一使用 Pinia store 进行认证状态管理
 */
router.beforeEach(async (to, from, next) => {
  const userStore = useUserStore()
  
  // 同步 token（确保 store 和 localStorage 一致）
  userStore.syncToken()
  
  // 使用 store 的 isAuthenticated 计算属性
  const isAuthenticated = userStore.isAuthenticated

  // 检查是否需要认证（包括父路由的 meta）
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth)
  
  if (requiresAuth && !isAuthenticated) {
    // 清除可能存在的无效 token
    if (userStore.token) {
      userStore.logout()
    }
    next('/login')
    return
  }
  
  // 如果已登录，访问登录页时重定向到首页
  if (to.path === '/login' && isAuthenticated) {
    next('/')
    return
  }
  
  // 如果路由需要认证，确保用户信息已加载
  if (requiresAuth && isAuthenticated && !userStore.userInfo) {
    try {
      await userStore.fetchUserInfo()
      // 如果获取用户信息失败（token 过期），fetchUserInfo 会调用 logout
      // 此时 isAuthenticated 会变为 false，需要重新检查
      if (!userStore.isAuthenticated) {
        next('/login')
        return
      }
    } catch (error) {
      // fetchUserInfo 失败，跳转到登录页
      next('/login')
      return
    }
  }
  
  // 检查管理员权限
  if (to.meta.requiresAdmin) {
    // 确保用户信息已加载
    if (!userStore.userInfo && isAuthenticated) {
      await userStore.fetchUserInfo()
    }
    // 使用计算属性检查管理员权限
    if (!userStore.isAdmin) {
      ElMessage.warning('您没有权限访问此页面')
      next('/dashboard')
      return
    }
  }
  
  next()
})

export default router

