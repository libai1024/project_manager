# 前端架构文档 - 阶段三实现

## 文件结构

```
src/
├── App.vue                    # 根组件
├── main.ts                    # 应用入口
├── api/
│   ├── request.ts            # Axios配置（baseURL + JWT拦截器）
│   ├── auth.ts               # 认证API
│   ├── platform.ts          # 平台管理API
│   ├── project.ts            # 项目管理API
│   ├── dashboard.ts         # Dashboard API
│   ├── user.ts               # 用户管理API
│   └── attachment.ts         # 附件管理API
├── layouts/
│   └── MainLayout.vue        # 主布局（侧边栏 + 头部）
├── views/
│   ├── Login.vue             # 登录页面
│   ├── Dashboard.vue        # 工作台
│   ├── Projects.vue          # 项目管理列表（完整版）
│   ├── ProjectList.vue       # 项目管理列表（符合阶段三要求）
│   ├── ProjectDetail.vue    # 项目详情
│   ├── Platforms.vue         # 平台管理
│   └── Users.vue            # 用户管理
├── router/
│   └── index.ts              # 路由配置
├── stores/
│   └── user.ts               # Pinia状态管理（用户信息）
└── styles/
    ├── theme.css             # 全局主题变量
    ├── element-plus-theme.css # Element Plus主题定制
    ├── components.css        # 自定义组件样式
    └── theme-config.ts      # TypeScript主题配置
```

## 1. 基础布局 (MainLayout.vue)

### 侧边栏导航
- Dashboard（工作台）
- Projects（项目管理）
- Platforms（平台管理）
- Users（用户管理，仅管理员可见）

### 头部导航
- 欢迎信息
- 用户下拉菜单（退出登录）

### 响应式设计
- 桌面端：固定侧边栏
- 移动端：抽屉式侧边栏

## 2. Axios 配置 (api/request.ts)

### Base URL
```typescript
baseURL: '/api'
```

### JWT Token 拦截器
- 请求拦截器：从 localStorage 读取 token，自动添加到 Authorization header
- 响应拦截器：处理 401/403 错误，自动跳转登录

### 错误处理
- 401：登录过期，清除token并跳转登录页
- 403：权限不足提示
- 其他：显示错误消息

## 3. 项目管理页面 (ProjectList.vue)

### 表格列（符合架构要求）

1. **Title（项目名称）**
   - 显示项目标题
   - 最小宽度：200px

2. **Platform（平台）**
   - 显示接单平台名称
   - 最小宽度：120px

3. **Price（金额）**
   - 显示订单金额
   - 格式：¥XX.XX
   - 右对齐
   - 最小宽度：100px

4. **Current Status（当前状态）**
   - **从最后一个完成的步骤计算**
   - 逻辑：
     - 如果所有步骤都完成 → "已完成"
     - 如果有完成的步骤 → 返回最后一个完成步骤的名称
     - 如果没有完成的步骤 → 返回第一个步骤的名称
   - 使用 Tag 组件显示，根据状态显示不同颜色
   - 最小宽度：150px

5. **Actions（操作）**
   - 编辑按钮
   - 删除按钮
   - 固定右侧
   - 宽度：200px

### 创建项目对话框

表单字段：
- 项目名称（必填）
- 学生姓名（可选）
- 接单平台（必填，下拉选择）
- 订单金额（必填，数字输入）
- GitHub地址（可选）
- 需求描述（可选，多行文本）

### 编辑项目对话框

与创建对话框相同的表单字段，用于编辑现有项目。

## 4. 状态管理 (Pinia)

### userStore
- `token`: JWT token（存储在 localStorage）
- `userInfo`: 当前用户信息
- `login()`: 登录方法
- `logout()`: 退出登录
- `fetchUserInfo()`: 获取用户信息
- `isAdmin()`: 判断是否为管理员

## 5. 路由配置

```typescript
/ (MainLayout)
  ├── /dashboard - Dashboard页面
  ├── /projects - 项目管理列表
  ├── /projects/:id - 项目详情
  ├── /platforms - 平台管理
  └── /users - 用户管理（仅管理员）
```

路由守卫：
- 未登录用户自动跳转登录页
- 已登录用户访问登录页自动跳转首页
- 非管理员访问用户管理页自动跳转首页

## 6. 主题系统

### 黑白极简线条风格
- 全局CSS变量系统
- Element Plus组件主题定制
- 响应式设计支持

### 使用主题变量
```vue
<style scoped>
.component {
  color: var(--text-primary);
  background-color: var(--bg-primary);
  border: var(--border-width-thin) solid var(--border-color);
  padding: var(--spacing-md);
}
</style>
```

## 实现要点

### 1. Current Status 计算逻辑

```typescript
const getCurrentStatus = (project: Project): string => {
  // 1. 按 order_index 排序步骤
  const sortedSteps = [...project.steps].sort((a, b) => a.order_index - b.order_index)
  
  // 2. 找到最后一个"已完成"的步骤
  let lastDoneStep = null
  for (let i = sortedSteps.length - 1; i >= 0; i--) {
    if (sortedSteps[i].status === '已完成') {
      lastDoneStep = sortedSteps[i]
      break
    }
  }
  
  // 3. 如果所有步骤都完成 → "已完成"
  if (sortedSteps.every(step => step.status === '已完成')) {
    return '已完成'
  }
  
  // 4. 如果有完成的步骤 → 返回最后一个完成步骤的名称
  if (lastDoneStep) {
    return lastDoneStep.name
  }
  
  // 5. 如果没有完成的步骤 → 返回第一个步骤的名称
  return sortedSteps[0]?.name || '未开始'
}
```

### 2. Axios 配置要点

- Base URL: `/api`（通过 Vite proxy 转发到后端）
- Token 存储：localStorage
- 自动注入：请求拦截器自动添加 Authorization header
- 错误处理：响应拦截器统一处理错误

### 3. 布局响应式

- 桌面端（>768px）：固定侧边栏
- 移动端（≤768px）：抽屉式侧边栏，菜单按钮显示

## 符合架构要求

✅ **基础布局**：侧边栏 + 头部
✅ **Axios配置**：baseURL + JWT拦截器
✅ **项目管理页面**：表格 + 创建对话框
✅ **表格列**：Title, Platform, Price, Current Status, Actions
✅ **Current Status**：从最后一个完成的步骤计算
✅ **Actions**：Edit, Delete

## 使用说明

### 开发新页面

1. 在 `views/` 目录创建 Vue 组件
2. 在 `router/index.ts` 添加路由
3. 在 `api/` 目录创建对应的 API 接口文件
4. 使用主题变量保持样式一致

### 调用 API

```typescript
import { projectApi } from '@/api/project'

// 获取项目列表
const projects = await projectApi.list()

// 创建项目
await projectApi.create(projectData)

// 更新项目
await projectApi.update(id, updateData)

// 删除项目
await projectApi.delete(id)
```

### 使用主题变量

```vue
<style scoped>
.my-component {
  color: var(--text-primary);
  background: var(--bg-primary);
  border: var(--border-width-thin) solid var(--border-color);
  padding: var(--spacing-md);
  border-radius: var(--radius-sm);
}
</style>
```


