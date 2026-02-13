# API测试报告

测试时间: 2026-02-13 17:54:22

---

## 1. 健康检查

### ✅ 根路径
- 方法: GET
- 端点: /
- 状态码: 200

### ✅ 健康检查
- 方法: GET
- 端点: /health
- 状态码: 200

## 2. 用户认证

### ❌ 用户登录
- 方法: POST
- 端点: /api/auth/login
- 状态码: 422
- 响应: `{"code":422,"msg":"数据验证失败","data":null,"details":[{"field":"body -> username","message":"Field required","type":"missing"},{"field":"body -> password","message":"Field required","type":"missing"}]}`

### ✅ 获取当前用户
- 方法: GET
- 端点: /api/auth/me
- 状态码: 200

## 3. 平台管理

### ❌ 获取平台列表
- 方法: GET
- 端点: /api/platforms
- 状态码: 307
- 响应: ``

### ❌ 创建平台
- 方法: POST
- 端点: /api/platforms
- 状态码: 307
- 响应: ``

## 4. 标签管理

### ❌ 获取标签列表
- 方法: GET
- 端点: /api/tags
- 状态码: 307
- 响应: ``

### ❌ 创建标签
- 方法: POST
- 端点: /api/tags
- 状态码: 307
- 响应: ``

## 5. 项目管理

### ❌ 获取项目列表
- 方法: GET
- 端点: /api/projects
- 状态码: 307
- 响应: ``

### ❌ 创建项目
- 方法: POST
- 端点: /api/projects
- 状态码: 307
- 响应: ``

### ✅ 获取项目详情
- 方法: GET
- 端点: /api/projects/
- 状态码: 200

### ❌ 更新项目
- 方法: PUT
- 端点: /api/projects/
- 状态码: 405
- 响应: `{"detail":"Method Not Allowed"}`

## 6. 项目步骤

### ❌ 创建项目步骤
- 方法: POST
- 端点: /api/projects//steps
- 状态码: 404
- 响应: `{"detail":"Not Found"}`

### ❌ 更新步骤状态
- 方法: PUT
- 端点: /api/projects/steps/
- 状态码: 307
- 响应: ``

### ❌ 切换步骤Todo
- 方法: POST
- 端点: /api/projects/steps//toggle-todo
- 状态码: 404
- 响应: `{"detail":"Not Found"}`

## 7. Dashboard

### ✅ Dashboard统计
- 方法: GET
- 端点: /api/dashboard/stats
- 状态码: 200

## 8. Todo管理

### ❌ 获取Todo列表
- 方法: GET
- 端点: /api/todos
- 状态码: 307
- 响应: ``

## 9. 步骤模板

### ❌ 获取步骤模板列表
- 方法: GET
- 端点: /api/step-templates
- 状态码: 307
- 响应: ``

### ❌ 创建步骤模板
- 方法: POST
- 端点: /api/step-templates
- 状态码: 307
- 响应: ``

## 10. 系统设置

### ❌ 获取系统设置
- 方法: GET
- 端点: /api/system-settings
- 状态码: 307
- 响应: ``

## 11. 清理测试数据

### ❌ 删除项目
- 方法: DELETE
- 端点: /api/projects/
- 状态码: 405
- 响应: `{"detail":"Method Not Allowed"}`


---

## 测试汇总

| 指标 | 值 |
|------|-----|
| 总测试数 | 21 |
| 通过数 | 5 |
| 失败数 | 16 |
| 通过率 | 23.8% |
