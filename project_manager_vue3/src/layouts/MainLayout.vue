<template>
  <el-container class="layout-container">
    <!-- 移动端抽屉菜单 -->
    <el-drawer
      v-model="drawerVisible"
      :with-header="false"
      direction="ltr"
      size="260px"
      class="mobile-drawer"
    >
      <div class="sidebar-container">
        <div class="logo">
          <div class="logo-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M12 2L2 7l10 5 10-5-10-5z" />
              <path d="M2 17l10 5 10-5" />
              <path d="M2 12l10 5 10-5" />
            </svg>
          </div>
          <h2>项目管理系统</h2>
        </div>
        <el-menu
          :default-active="activeMenu"
          class="sidebar-menu"
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
      </div>
    </el-drawer>

    <!-- 桌面端侧边栏 -->
    <el-aside :width="isMobile ? '0' : '240px'" class="sidebar desktop-sidebar">
      <div class="sidebar-container">
        <div class="logo">
          <div class="logo-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M12 2L2 7l10 5 10-5-10-5z" />
              <path d="M2 17l10 5 10-5" />
              <path d="M2 12l10 5 10-5" />
            </svg>
          </div>
          <h2>项目管理系统</h2>
        </div>
        <el-menu
          :default-active="activeMenu"
          class="sidebar-menu"
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
      </div>
    </el-aside>

    <el-container class="main-container">
      <el-header class="header">
        <div class="header-left">
          <button
            v-if="isMobile"
            class="menu-toggle"
            @click="drawerVisible = true"
            aria-label="打开菜单"
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M3 12h18M3 6h18M3 18h18" />
            </svg>
          </button>
          <span class="welcome-text">
            <span class="welcome-greeting">欢迎回来，</span>
            <span class="welcome-name">{{ userStore.userInfo?.username }}</span>
          </span>
        </div>
        <div class="header-right">
          <el-dropdown @command="handleCommand" trigger="click">
            <div class="user-dropdown">
              <div class="user-avatar">
                {{ userStore.userInfo?.username?.charAt(0)?.toUpperCase() || 'U' }}
              </div>
              <span class="username-text">{{ userStore.userInfo?.username }}</span>
              <el-icon class="dropdown-icon"><ArrowDown /></el-icon>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">
                  <el-icon><User /></el-icon>
                  个人信息
                </el-dropdown-item>
                <el-dropdown-item command="logout" divided>
                  <el-icon><SwitchButton /></el-icon>
                  退出登录
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>

      <el-main class="main-content">
        <router-view v-slot="{ Component }">
          <transition name="fade-slide" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { computed, ref, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import {
  DataBoard,
  FolderOpened,
  Platform,
  User,
  ArrowDown,
  List,
  Folder,
  Money,
  Setting,
  Clock,
  PriceTag,
  SwitchButton
} from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const drawerVisible = ref(false)
const isMobile = ref(false)

const activeMenu = computed(() => {
  const path = route.path
  if (path.startsWith('/projects/') && path !== '/projects') {
    return '/projects'
  }
  return path
})

const checkMobile = () => {
  isMobile.value = window.innerWidth < 768
}

const handleMenuSelect = (index: string) => {
  if (index && index !== route.path) {
    router.push(index).catch((err) => {
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
  background-color: var(--bg-secondary);
}

/* ===== 侧边栏 ===== */
.sidebar {
  background: var(--bg-sidebar);
  overflow: hidden;
  transition: width var(--transition-base);
}

.desktop-sidebar {
  display: block;
}

.sidebar-container {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.logo {
  height: var(--header-height);
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  padding: 0 var(--spacing-lg);
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.logo-icon {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-primary-dark) 100%);
  border-radius: var(--radius-md);
  color: white;
}

.logo-icon svg {
  width: 18px;
  height: 18px;
}

.logo h2 {
  font-size: var(--font-size-md);
  font-weight: var(--font-weight-semibold);
  color: white;
  margin: 0;
  white-space: nowrap;
  letter-spacing: var(--letter-spacing-tight);
}

.sidebar-menu {
  flex: 1;
  padding: var(--spacing-md) 0;
  border-right: none;
  background-color: transparent;
  overflow-y: auto;
  overflow-x: hidden;
}

.sidebar-menu::-webkit-scrollbar {
  width: 4px;
}

.sidebar-menu::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.1);
  border-radius: var(--radius-full);
}

/* ===== 头部 ===== */
.header {
  background-color: var(--bg-card);
  border-bottom: 1px solid var(--border-color);
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 var(--spacing-lg);
  height: var(--header-height);
  position: sticky;
  top: 0;
  z-index: var(--z-index-sticky);
  box-shadow: var(--shadow-xs);
}

.header-left {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
}

.menu-toggle {
  display: none;
  width: 40px;
  height: 40px;
  border: none;
  border-radius: var(--radius-md);
  background-color: var(--bg-secondary);
  cursor: pointer;
  align-items: center;
  justify-content: center;
  transition: all var(--transition-fast);
}

.menu-toggle:hover {
  background-color: var(--bg-tertiary);
}

.menu-toggle svg {
  width: 20px;
  height: 20px;
  color: var(--text-primary);
}

.welcome-text {
  font-size: var(--font-size-sm);
  color: var(--text-secondary);
}

.welcome-greeting {
  color: var(--text-tertiary);
}

.welcome-name {
  color: var(--text-primary);
  font-weight: var(--font-weight-medium);
}

.header-right {
  display: flex;
  align-items: center;
}

.user-dropdown {
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  padding: var(--spacing-xs) var(--spacing-sm);
  border-radius: var(--radius-lg);
  transition: all var(--transition-fast);
}

.user-dropdown:hover {
  background-color: var(--bg-secondary);
}

.user-avatar {
  width: 36px;
  height: 36px;
  border-radius: var(--radius-md);
  background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-primary-dark) 100%);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-semibold);
}

.username-text {
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  color: var(--text-primary);
}

.dropdown-icon {
  color: var(--text-tertiary);
  font-size: 12px;
  transition: transform var(--transition-fast);
}

.user-dropdown:hover .dropdown-icon {
  transform: rotate(180deg);
}

/* ===== 主内容区 ===== */
.main-content {
  background-color: var(--bg-secondary);
  padding: var(--spacing-lg);
  overflow-x: hidden;
  min-height: calc(100vh - var(--header-height));
}

/* ===== 页面切换动画 ===== */
.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: all 0.2s ease;
}

.fade-slide-enter-from {
  opacity: 0;
  transform: translateY(10px);
}

.fade-slide-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

/* ===== 移动端样式 ===== */
@media (max-width: 768px) {
  .desktop-sidebar {
    display: none !important;
    width: 0 !important;
  }

  .menu-toggle {
    display: flex !important;
  }

  .header {
    padding: 0 var(--spacing-md);
  }

  .welcome-text {
    font-size: var(--font-size-xs);
  }

  .welcome-greeting {
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

  .user-avatar {
    width: 32px;
    height: 32px;
  }
}

/* ===== 平板样式 ===== */
@media (min-width: 769px) and (max-width: 1024px) {
  .sidebar {
    width: 200px !important;
  }

  .main-content {
    padding: var(--spacing-md);
  }

  .logo {
    padding: 0 var(--spacing-md);
  }

  .logo h2 {
    font-size: var(--font-size-sm);
  }
}

/* ===== 移动端抽屉样式 ===== */
:deep(.mobile-drawer) {
  .el-drawer__body {
    padding: 0;
    background: var(--bg-sidebar);
  }

  .sidebar-container {
    height: 100%;
  }

  .logo {
    border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  }

  .sidebar-menu {
    background-color: transparent;
  }
}
</style>
