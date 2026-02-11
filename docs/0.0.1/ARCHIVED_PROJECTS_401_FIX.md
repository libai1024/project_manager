# 归档项目 401 错误修复指南

## 问题描述
访问归档项目 API 时出现 401 Unauthorized 错误：
```
GET http://localhost:8000/api/archived-projects/?skip=0&limit=12 401 (Unauthorized)
```

## 问题分析

### 1. 后端测试（成功）
使用 curl 测试后端 API，确认后端工作正常：
```bash
curl -X GET "http://localhost:8000/api/archived-projects/?skip=0&limit=12" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTc2NzUxOTg4MH0.XZkpt0TMHnVv1dAyLSyDPJS-BPaBKF7WuUDi3ehyVwg"
```
返回：`200 OK` 和空数组 `[]`

### 2. Token 状态
- Token 未过期（有效期至 2026-01-04）
- Token 格式正确

### 3. 可能的原因
1. **Token 未存储在 LocalStorage**：前端请求拦截器从 `localStorage.getItem('token')` 读取 token，如果不存在则不会发送 Authorization header
2. **请求拦截器问题**：虽然代码中有多层设置 header 的逻辑，但可能存在边缘情况
3. **CORS 问题**：虽然已配置允许所有 headers，但需要确认

## 解决方案

### 方案 1：使用测试工具设置 Token（推荐）

1. **打开测试页面**：
   - 在浏览器中打开：`file:///Users/wangwei/Money/project_manager/set_token_and_test.html`
   - 或者通过本地服务器访问

2. **设置 Token**：
   - 在页面中输入你的 Bearer Token
   - 点击"设置 Token 到 LocalStorage"按钮
   - 点击"测试 API"验证 token 是否有效

3. **刷新前端应用**：
   - 设置 token 后，刷新你的 Vue 应用页面
   - 再次访问归档项目页面

### 方案 2：在浏览器控制台手动设置

1. 打开浏览器开发者工具 (F12)
2. 切换到 Console 标签
3. 运行以下命令：
```javascript
localStorage.setItem('token', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTc2NzUxOTg4MH0.XZkpt0TMHnVv1dAyLSyDPJS-BPaBKF7WuUDi3ehyVwg');
console.log('Token 已设置:', localStorage.getItem('token'));
```

4. 刷新页面并重新访问归档项目

### 方案 3：检查登录流程

如果 token 应该通过登录自动设置，检查：
1. 登录是否成功
2. 登录后 token 是否正确保存到 localStorage
3. 检查 `userStore.login()` 方法是否正确调用 `setToken()`

## 调试步骤

### 1. 检查 Token 是否存在
在浏览器控制台运行：
```javascript
console.log('Token:', localStorage.getItem('token'));
console.log('Token 长度:', localStorage.getItem('token')?.length || 0);
```

### 2. 检查请求拦截器
打开浏览器 Network 标签：
1. 访问归档项目页面
2. 查看 `/api/archived-projects/` 请求
3. 检查 Request Headers 中是否包含 `Authorization: Bearer ...`
4. 如果没有，说明请求拦截器没有正确设置 header

### 3. 查看控制台日志
前端代码在开发环境下会输出详细的请求拦截器日志：
- 查找 `[Request Interceptor]` 开头的日志
- 检查 token 是否被正确读取和设置

### 4. 使用测试页面
打开 `test_archived_projects_api.html` 进行详细测试：
- 测试 Fetch API
- 测试 Axios
- 测试 XMLHttpRequest
- 查看详细的请求和响应信息

## 测试工具

### 1. `set_token_and_test.html`
- 设置 token 到 localStorage
- 测试 API 调用
- 检查当前状态

### 2. `test_archived_projects_api.html`
- 详细的 API 测试工具
- 支持多种请求方式
- 显示完整的请求和响应信息

### 3. `test_api_console.js`
- 可在浏览器控制台运行的测试脚本
- 快速诊断问题

## 代码检查点

### 前端请求拦截器 (`src/api/request.ts`)
- 第 31 行：`const token = getToken()` - 从 localStorage 读取 token
- 第 43 行：设置 Authorization header
- 第 94-104 行：开发环境下的调试日志

### Token 工具 (`src/utils/auth.ts`)
- `getToken()`: 从 localStorage 读取 token
- `setToken()`: 设置 token 到 localStorage

### 用户 Store (`src/stores/user.ts`)
- `login()`: 登录时应该调用 `setToken()` 保存 token
- `token`: 响应式 token 状态

## 验证修复

修复后，验证以下内容：
1. ✅ LocalStorage 中存在 token
2. ✅ Network 标签中请求包含 Authorization header
3. ✅ API 返回 200 状态码
4. ✅ 归档项目列表正常显示

## 如果问题仍然存在

1. **检查后端日志**：
   ```bash
   tail -f logs/backend.log
   ```
   查看是否有请求到达后端，以及 Authorization header 是否存在

2. **检查 CORS 配置**：
   确认 `fastapi_back/main.py` 中的 CORS 配置允许 Authorization header

3. **检查浏览器控制台**：
   查看是否有 JavaScript 错误或网络错误

4. **使用 curl 对比**：
   使用相同的 token 通过 curl 测试，确认后端正常

## 预防措施

1. **登录时确保 token 保存**：
   检查登录流程是否正确保存 token 到 localStorage

2. **添加 token 检查**：
   在访问需要认证的页面时，先检查 token 是否存在

3. **改进错误处理**：
   当收到 401 错误时，自动跳转到登录页面

