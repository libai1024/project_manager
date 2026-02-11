<template>
  <el-container class="layout-container">
    <!-- 移动端抽屉菜单 -->
    <el-drawer
      v-model="drawerVisible"
      :with-header="false"
      direction="ltr"
      size="200px"
      class="mobile-drawer"
    >
      <div class="logo">
        <h2>接单项目管理系统</h2>
      </div>
      <el-menu
        :default-active="activeMenu"
        class="sidebar-menu"
        background-color="#304156"
        text-color="#bfcbd9"
        active-text-color="#409EFF"
        router
        @select="handleMenuSelect"
      >
        <el-menu-item index="/dashboard">
          <el-icon><DataBoard /></el-icon>
          <span>工作台</span>
        </el-menu-item>
        <el-menu-item index="/projects">
          <el-icon><FolderOpened /></el-icon>
          <span>项目管理</span>
        </el-menu-item>
        <el-menu-item index="/platforms">
          <el-icon><Platform /></el-icon>
          <span>平台管理</span>
        </el-menu-item>
        <el-menu-item index="/todos">
          <el-icon><List /></el-icon>
          <span>待办管理</span>
        </el-menu-item>
        <el-menu-item index="/resources">
          <el-icon><Folder /></el-icon>
          <span>资源管理</span>
        </el-menu-item>
        <el-menu-item index="/finance">
          <el-icon><Money /></el-icon>
          <span>财务管理</span>
        </el-menu-item>
        <el-menu-item index="/historical-projects">
          <el-icon><Clock /></el-icon>
          <span>历史项目</span>
        </el-menu-item>
        <el-menu-item index="/tags">
          <el-icon><PriceTag /></el-icon>
          <span>标签管理</span>
        </el-menu-item>
        <el-menu-item v-if="userStore.isAdmin" index="/users">
          <el-icon><User /></el-icon>
          <span>用户管理</span>
        </el-menu-item>
        <el-menu-item index="/settings">
          <el-icon><Setting /></el-icon>
          <span>系统设置</span>
        </el-menu-item>
      </el-menu>
    </el-drawer>

    <!-- 桌面端侧边栏 -->
    <el-aside :width="isMobile ? '0' : '200px'" class="sidebar desktop-sidebar">
      <div class="logo">
        <h2>接单项目管理系统</h2>
      </div>
      <el-menu
        :default-active="activeMenu"
        class="sidebar-menu"
        background-color="#304156"
        text-color="#bfcbd9"
        active-text-color="#409EFF"
        router
        @select="handleMenuSelect"
      >
        <el-menu-item index="/dashboard">
          <el-icon><DataBoard /></el-icon>
          <span>工作台</span>
        </el-menu-item>
        <el-menu-item index="/projects">
          <el-icon><FolderOpened /></el-icon>
          <span>项目管理</span>
        </el-menu-item>
        <el-menu-item index="/platforms">
          <el-icon><Platform /></el-icon>
          <span>平台管理</span>
        </el-menu-item>
        <el-menu-item index="/todos">
          <el-icon><List /></el-icon>
          <span>待办管理</span>
        </el-menu-item>
        <el-menu-item index="/resources">
          <el-icon><Folder /></el-icon>
          <span>资源管理</span>
        </el-menu-item>
        <el-menu-item index="/finance">
          <el-icon><Money /></el-icon>
          <span>财务管理</span>
        </el-menu-item>
        <el-menu-item index="/historical-projects">
          <el-icon><Clock /></el-icon>
          <span>历史项目</span>
        </el-menu-item>
        <el-menu-item index="/tags">
          <el-icon><PriceTag /></el-icon>
          <span>标签管理</span>
        </el-menu-item>
        <el-menu-item v-if="userStore.isAdmin" index="/users">
          <el-icon><User /></el-icon>
          <span>用户管理</span>
        </el-menu-item>
        <el-menu-item index="/settings">
          <el-icon><Setting /></el-icon>
          <span>系统设置</span>
        </el-menu-item>
      </el-menu>
    </el-aside>
    
    <el-container>
      <el-header class="header">
        <div class="header-left">
          <el-button
            v-if="isMobile"
            :icon="Menu"
            circle
            @click="drawerVisible = true"
            class="menu-toggle"
          />
          <span class="welcome-text">欢迎，{{ userStore.userInfo?.username }}</span>
        </div>
        <div class="header-right">
          <el-dropdown @command="handleCommand">
            <span class="user-dropdown">
              <el-icon><User /></el-icon>
              <span class="username-text">{{ userStore.userInfo?.username }}</span>
              <el-icon class="el-icon--right"><arrow-down /></el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="logout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>
      
      <el-main class="main-content">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { computed, ref, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { DataBoard, FolderOpened, Platform, User, ArrowDown, Menu, List, Folder, Money, Setting, Clock, PriceTag } from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const drawerVisible = ref(false)
const isMobile = ref(false)

const activeMenu = computed(() => {
  // 确保路径匹配正确
  const path = route.path
  console.log('Active menu computed, current path:', path)
  if (path.startsWith('/projects/') && path !== '/projects') {
    return '/projects' // 项目详情页也高亮项目管理菜单
  }
  return path
})

const checkMobile = () => {
  isMobile.value = window.innerWidth < 768
}

const handleMenuSelect = (index: string) => {
  // 确保路由跳转（即使router属性已设置，也手动处理以确保跳转）
  if (index && index !== route.path) {
    console.log('Menu selected:', index, 'Current path:', route.path)
    router.push(index).then(() => {
      console.log('Navigation successful to:', index)
    }).catch((err) => {
      console.error('Navigation error:', err)
      // 如果router属性没有工作，手动跳转
      if (err.name !== 'NavigationDuplicated') {
        window.location.href = index
      }
    })
  }
  if (isMobile.value) {
    drawerVisible.value = false
  }
}

const handleCommand = (command: string) => {
  if (command === 'logout') {
    userStore.logout()
  }
}

onMounted(() => {
  checkMobile()
  window.addEventListener('resize', checkMobile)
})

onUnmounted(() => {
  window.removeEventListener('resize', checkMobile)
})
</script>

<style scoped>
.layout-container {
  height: 100vh;
  background-color: var(--bg-primary);
}

.sidebar {
  background-color: var(--bg-primary);
  border-right: var(--border-width-thin) solid var(--border-color);
  overflow: hidden;
  transition: width var(--transition-base);
}

.desktop-sidebar {
  display: block;
}

.logo {
  height: 60px;
  line-height: 60px;
  text-align: center;
  background-color: var(--bg-primary);
  border-bottom: var(--border-width-thin) solid var(--border-color);
  color: var(--text-primary);
  font-weight: var(--font-weight-semibold);
  letter-spacing: 0.05em;
}

.logo h2 {
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-semibold);
  margin: 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  text-transform: uppercase;
  letter-spacing: 0.1em;
}

.sidebar-menu {
  border-right: none;
  height: calc(100vh - 60px);
  overflow-y: auto;
  background-color: var(--bg-primary);
}

.header {
  background-color: var(--bg-primary);
  border-bottom: var(--border-width-thin) solid var(--border-color);
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 var(--spacing-md);
  height: 60px;
  position: sticky;
  top: 0;
  z-index: var(--z-index-sticky);
  box-shadow: var(--shadow-xs);
}

.header-left {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  font-size: var(--font-size-base);
  color: var(--text-primary);
  font-weight: var(--font-weight-medium);
}

.menu-toggle {
  display: none;
  border: var(--border-width-thin) solid var(--border-color);
  background-color: var(--bg-primary);
}

.menu-toggle:hover {
  border-color: var(--color-black);
  background-color: var(--bg-secondary);
}

.welcome-text {
  display: inline-block;
}

.header-right {
  display: flex;
  align-items: center;
}

.user-dropdown {
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: var(--spacing-xs);
  color: var(--text-primary);
  padding: var(--spacing-xs) var(--spacing-sm);
  border-radius: var(--radius-sm);
  transition: background-color var(--transition-fast);
  font-weight: var(--font-weight-medium);
}

.user-dropdown:hover {
  background-color: var(--bg-secondary);
}

.username-text {
  display: inline-block;
}

.main-content {
  background-color: var(--bg-secondary);
  padding: var(--spacing-lg);
  overflow-x: hidden;
  min-height: calc(100vh - 60px);
}

/* 移动端样式 */
@media (max-width: 768px) {
  .desktop-sidebar {
    display: none !important;
    width: 0 !important;
  }

  .menu-toggle {
    display: inline-flex !important;
  }

  .header {
    padding: 0 var(--spacing-sm);
  }

  .header-left {
    font-size: var(--font-size-sm);
  }

  .welcome-text {
    display: none;
  }

  .username-text {
    display: none;
  }

  .main-content {
    padding: var(--spacing-md);
  }

  .logo h2 {
    font-size: var(--font-size-base);
  }
}

/* 平板样式 */
@media (min-width: 769px) and (max-width: 1024px) {
  .sidebar {
    width: 180px !important;
  }

  .main-content {
    padding: var(--spacing-md);
  }
}

/* 移动端抽屉样式 */
:deep(.mobile-drawer .el-drawer__body) {
  padding: 0;
  background-color: var(--bg-primary);
}

:deep(.mobile-drawer .logo) {
  height: 60px;
  line-height: 60px;
  text-align: center;
  background-color: var(--bg-primary);
  border-bottom: var(--border-width-thin) solid var(--border-color);
  color: var(--text-primary);
  margin-bottom: 0;
}

:deep(.mobile-drawer .sidebar-menu) {
  background-color: var(--bg-primary);
}
</style>

