# 前端认证架构文档

## 概述

本文档描述了前端项目中 token 认证的统一管理架构。经过重构，所有 token 相关的操作都通过统一的接口进行，确保整个项目的认证逻辑一致。

## 架构设计

### 1. 核心模块

#### `utils/auth.ts` - Token 工具函数
**职责：**
- 提供同步的 token 读写接口
- 封装 localStorage 操作
- 用于非响应式环境（如 axios 拦截器）

**API：**
- `getToken(): string | null` - 获取 token
- `setToken(token: string): void` - 设置 token
- `removeToken(): void` - 移除 token
- `hasToken(): boolean` - 检查是否存在 token

**使用场景：**
- Axios 请求拦截器中获取 token
- 其他非 Vue 组件环境

#### `stores/user.ts` - 用户状态管理（Pinia Store）
**职责：**
- 作为整个应用中**唯一的 token 管理源**
- 管理用户认证状态
- 管理用户信息
- 提供登录/登出功能

**状态：**
- `token: Ref<string | null>` - 当前 token
- `userInfo: Ref<UserInfo | null>` - 用户信息
- `isAuthenticated: ComputedRef<boolean>` - 是否已认证
- `isAdmin: ComputedRef<boolean>` - 是否为管理员

**方法：**
- `login(username, password)` - 用户登录
- `logout()` - 用户登出
- `fetchUserInfo()` - 获取用户信息
- `syncToken()` - 同步 token（从 localStorage 到 store）

**使用场景：**
- Vue 组件中获取认证状态
- 路由守卫中检查认证
- 应用初始化时恢复会话

#### `api/request.ts` - Axios 请求配置
**职责：**
- 配置 axios 实例
- 统一处理请求拦截（自动添加 token）
- 统一处理响应拦截（错误处理、token 过期处理）

**关键逻辑：**
- 请求拦截器：从 `utils/auth.ts` 获取 token，自动添加到请求头
- 响应拦截器：处理 401 错误，自动清除 token 并跳转登录页

**注意：**
- 不能直接使用 Pinia store，避免循环依赖
- 使用 `utils/auth.ts` 同步获取 token

### 2. 文件层级结构

```
src/
├── utils/
│   └── auth.ts              # Token 工具函数（同步操作）
├── stores/
│   └── user.ts              # 用户状态管理（响应式，唯一 token 管理源）
├── api/
│   ├── request.ts           # Axios 配置（使用 utils/auth.ts）
│   ├── auth.ts              # 认证 API
│   └── ...                  # 其他 API
├── router/
│   └── index.ts             # 路由守卫（使用 stores/user.ts）
├── main.ts                   # 应用初始化（使用 stores/user.ts）
└── views/
    └── ...                   # 视图组件（使用 stores/user.ts）
```

### 3. 数据流

```
┌─────────────────┐
│  localStorage   │  ←→  stores/user.ts  ←→  Vue Components
└─────────────────┘         ↓
                      utils/auth.ts
                            ↓
                      api/request.ts (Axios Interceptor)
                            ↓
                      Backend API
```

**说明：**
1. `localStorage` 作为持久化存储
2. `stores/user.ts` 作为响应式状态管理，与 `localStorage` 双向同步
3. `utils/auth.ts` 提供同步访问接口，供非响应式环境使用
4. `api/request.ts` 使用 `utils/auth.ts` 获取 token，自动添加到请求头
5. Vue 组件通过 `stores/user.ts` 访问认证状态

## 使用指南

### 在 Vue 组件中使用

```typescript
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()

// 检查是否已认证
if (userStore.isAuthenticated) {
  // 已登录
}

// 获取 token（通常不需要直接访问）
const token = userStore.token

// 检查是否为管理员
if (userStore.isAdmin) {
  // 管理员操作
}

// 登出
userStore.logout()
```

### 在非 Vue 环境中使用（如 axios 拦截器）

```typescript
import { getToken } from '@/utils/auth'

// 获取 token
const token = getToken()
if (token) {
  // 使用 token
}
```

### 路由守卫

路由守卫已经统一使用 `stores/user.ts`，无需额外处理。

## 重构清单

✅ 已完成的重构：
1. 创建 `utils/auth.ts` - 统一的 token 工具函数
2. 重构 `stores/user.ts` - 作为唯一的 token 管理源
3. 重构 `api/request.ts` - 使用统一的 token 获取方法
4. 重构 `router/index.ts` - 统一使用 store
5. 重构 `main.ts` - 简化初始化逻辑
6. 重构所有视图组件 - 移除直接使用 localStorage 的代码
7. 重构 `api/attachment.ts` - 使用统一的 token 管理

## 最佳实践

1. **不要在组件中直接使用 `localStorage.getItem('token')`**
   - 使用 `useUserStore().token` 或 `useUserStore().isAuthenticated`

2. **在非响应式环境中使用 `utils/auth.ts`**
   - 如 axios 拦截器、工具函数等

3. **所有 token 的写入操作都通过 `stores/user.ts`**
   - 登录：`userStore.login()`
   - 登出：`userStore.logout()`

4. **使用计算属性检查认证状态**
   - `userStore.isAuthenticated` - 是否已认证
   - `userStore.isAdmin` - 是否为管理员

## 注意事项

1. **循环依赖问题**
   - `api/request.ts` 不能直接导入 `stores/user.ts`，因为可能导致循环依赖
   - 解决方案：使用 `utils/auth.ts` 作为中间层

2. **多标签页同步**
   - `stores/user.ts` 已监听 `storage` 事件，实现多标签页 token 同步

3. **Token 过期处理**
   - 在 `api/request.ts` 的响应拦截器中统一处理 401 错误
   - 自动清除 token 并跳转登录页

4. **文件预览 URL**
   - `api/attachment.ts` 的 `getPreviewUrl` 函数用于生成预览 URL
   - 由于 iframe/img 标签无法使用 Authorization header，需要后端支持 cookie 认证或 URL 参数传递 token

## 未来改进

1. **Token 刷新机制**
   - 实现 refresh token 机制
   - 自动刷新过期的 access token

2. **Cookie 认证支持**
   - 后端支持从 cookie 读取 token
   - 解决文件预览 URL 的认证问题

3. **更细粒度的权限控制**
   - 基于角色的访问控制（RBAC）
   - 权限中间件


