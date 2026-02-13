# API 文档

## 概述

本项目采用统一的 API 响应格式，符合国内互联网企业级规范。

## 基础 URL

- 开发环境: `http://localhost:8000`
- 生产环境: 根据部署配置

## 认证

所有需要认证的接口都需要在请求头中携带 JWT Token：

```
Authorization: Bearer <access_token>
```

Token 通过 `/api/auth/login` 接口获取，有效期为 15 分钟。可以使用 `/api/auth/refresh` 刷新 Token。

---

## 统一响应格式

所有 API 响应都遵循以下格式：

### 成功响应

```json
{
  "code": 200,
  "msg": "success",
  "data": { ... }
}
```

### 错误响应

```json
{
  "code": 400,
  "msg": "错误消息",
  "data": null
}
```

### 分页响应

```json
{
  "code": 200,
  "msg": "success",
  "data": {
    "items": [...],
    "total": 100,
    "page": 1,
    "page_size": 20,
    "total_pages": 5
  }
}
```

---

## 响应码定义

### HTTP 标准响应码

| Code | 说明 |
|------|------|
| 200 | 成功 |
| 201 | 创建成功 |
| 400 | 请求参数错误 |
| 401 | 未认证 |
| 403 | 无权限 |
| 404 | 资源不存在 |
| 422 | 参数验证失败 |
| 500 | 服务器内部错误 |

### 业务响应码 (1000+)

| Code | 说明 |
|------|------|
| 1000 | 通用业务错误 |
| 1001 | 资源重复 |
| 1002 | 资源被锁定 |
| 1003 | 操作失败 |

---

## API 模块

### 认证模块 `/api/auth`

#### 登录
```
POST /api/auth/login
Content-Type: application/x-www-form-urlencoded

username=xxx&password=xxx
```

**响应:**
```json
{
  "code": 200,
  "msg": "success",
  "data": {
    "access_token": "eyJ...",
    "refresh_token": "eyJ...",
    "token_type": "bearer"
  }
}
```

#### 刷新 Token
```
POST /api/auth/refresh
Authorization: Bearer <refresh_token>
```

#### 获取当前用户
```
GET /api/auth/me
Authorization: Bearer <access_token>
```

---

### 用户模块 `/api/users`

#### 获取用户列表
```
GET /api/users
Authorization: Bearer <access_token>
```

**响应:**
```json
{
  "code": 200,
  "msg": "success",
  "data": [
    {
      "id": 1,
      "username": "admin",
      "role": "admin",
      "created_at": "2024-01-01T00:00:00"
    }
  ]
}
```

#### 创建用户
```
POST /api/users
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "username": "newuser",
  "password": "password123",
  "role": "user"
}
```

#### 更新用户
```
PUT /api/users/{id}
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "role": "admin"
}
```

#### 删除用户
```
DELETE /api/users/{id}
Authorization: Bearer <access_token>
```

---

### 项目模块 `/api/projects`

#### 获取项目列表
```
GET /api/projects?platform_id=1&status=进行中&tag_ids=1,2
Authorization: Bearer <access_token>
```

**Query Parameters:**
| 参数 | 类型 | 说明 |
|------|------|------|
| platform_id | int | 平台ID（可选） |
| status | string | 项目状态（可选） |
| tag_ids | string | 标签ID，逗号分隔（可选） |

**响应:**
```json
{
  "code": 200,
  "msg": "success",
  "data": [
    {
      "id": 1,
      "title": "项目标题",
      "student_name": "学生姓名",
      "platform_id": 1,
      "platform_name": "平台名称",
      "status": "进行中",
      "is_paid": false,
      "actual_income": 0,
      "steps": [...],
      "tags": [...],
      "user_id": 1,
      "created_at": "2024-01-01T00:00:00"
    }
  ]
}
```

#### 获取项目详情
```
GET /api/projects/{id}
Authorization: Bearer <access_token>
```

#### 创建项目
```
POST /api/projects
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "title": "新项目",
  "student_name": "学生姓名",
  "platform_id": 1,
  "requirements": "项目需求描述",
  "tag_ids": [1, 2]
}
```

#### 更新项目
```
PUT /api/projects/{id}
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "title": "更新后的标题",
  "status": "已完成"
}
```

#### 删除项目
```
DELETE /api/projects/{id}
Authorization: Bearer <access_token>
```

#### 项目结账
```
POST /api/projects/{id}/settle
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "actual_income": 5000.00
}
```

---

### 步骤模块 `/api/projects/{project_id}/steps`

#### 创建步骤
```
POST /api/projects/{project_id}/steps
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "name": "步骤名称",
  "deadline": "2024-12-31T23:59:59"
}
```

#### 更新步骤
```
PUT /api/steps/{step_id}
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "name": "新步骤名称",
  "status": "已完成"
}
```

#### 删除步骤
```
DELETE /api/steps/{step_id}
Authorization: Bearer <access_token>
```

#### 切换步骤待办状态
```
POST /api/steps/{step_id}/toggle-todo
Authorization: Bearer <access_token>
```

#### 重新排序步骤
```
POST /api/steps/reorder
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "orders": [
    { "step_id": 1, "order_index": 0 },
    { "step_id": 2, "order_index": 1 }
  ]
}
```

---

### 平台模块 `/api/platforms`

#### 获取平台列表
```
GET /api/platforms
Authorization: Bearer <access_token>
```

#### 创建平台
```
POST /api/platforms
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "name": "新平台"
}
```

#### 更新平台
```
PUT /api/platforms/{id}
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "name": "更新后的平台名"
}
```

#### 删除平台
```
DELETE /api/platforms/{id}
Authorization: Bearer <access_token>
```

---

### 附件模块 `/api/attachments`

#### 上传附件
```
POST /api/attachments/upload/{project_id}
Authorization: Bearer <access_token>
Content-Type: multipart/form-data

file: <文件>
file_type: 需求
description: 文件描述
folder_id: 1
```

#### 获取项目附件列表
```
GET /api/attachments/project/{project_id}
Authorization: Bearer <access_token>
```

#### 下载附件
```
GET /api/attachments/{id}/download
Authorization: Bearer <access_token>
```

#### 删除附件
```
DELETE /api/attachments/{id}
Authorization: Bearer <access_token>
```

---

### 标签模块 `/api/tags`

#### 获取标签列表
```
GET /api/tags
Authorization: Bearer <access_token>
```

#### 创建标签
```
POST /api/tags
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "name": "标签名称",
  "color": "#409EFF"
}
```

#### 更新标签
```
PUT /api/tags/{id}
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "name": "新标签名",
  "color": "#67C23A"
}
```

#### 删除标签
```
DELETE /api/tags/{id}
Authorization: Bearer <access_token>
```

---

## 错误处理

当发生错误时，API 会返回相应的错误码和错误信息：

```json
{
  "code": 404,
  "msg": "项目不存在",
  "data": null
}
```

常见错误：

| 场景 | Code | Msg |
|------|------|-----|
| Token 无效 | 401 | "未认证" |
| 无权限访问 | 403 | "无权限" |
| 资源不存在 | 404 | "xxx不存在" |
| 参数验证失败 | 422 | "参数验证失败" |
| 用户名已存在 | 1001 | "用户名已存在" |

---

## 数据模型

### Project 项目

| 字段 | 类型 | 说明 |
|------|------|------|
| id | int | 项目ID |
| title | string | 项目标题 |
| student_name | string | 学生姓名 |
| platform_id | int | 平台ID |
| requirements | string | 项目需求 |
| status | string | 项目状态 |
| is_paid | bool | 是否已结账 |
| actual_income | float | 实际收入 |
| user_id | int | 所属用户ID |
| steps | Step[] | 步骤列表 |
| tags | Tag[] | 标签列表 |
| created_at | datetime | 创建时间 |
| updated_at | datetime | 更新时间 |

### ProjectStep 步骤

| 字段 | 类型 | 说明 |
|------|------|------|
| id | int | 步骤ID |
| name | string | 步骤名称 |
| status | string | 步骤状态（未开始/进行中/已完成） |
| deadline | datetime | 截止时间 |
| is_todo | bool | 是否为今日待办 |
| order_index | int | 排序索引 |
| project_id | int | 所属项目ID |

### Platform 平台

| 字段 | 类型 | 说明 |
|------|------|------|
| id | int | 平台ID |
| name | string | 平台名称 |

### User 用户

| 字段 | 类型 | 说明 |
|------|------|------|
| id | int | 用户ID |
| username | string | 用户名 |
| role | string | 角色（admin/user） |
| created_at | datetime | 创建时间 |

### Tag 标签

| 字段 | 类型 | 说明 |
|------|------|------|
| id | int | 标签ID |
| name | string | 标签名称 |
| color | string | 标签颜色 |
