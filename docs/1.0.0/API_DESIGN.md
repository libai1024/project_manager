# 外包项目管理系统 1.0.0 API 设计规范

本文档定义 API 的版本策略、URL 规范、请求/响应约定、错误码与分页等通用规则，确保前后端协作与开源协作可持续。

## 1. API 版本策略

### 1.1 URL 前缀版本

- **推荐**：采用路径前缀版本：`/api/v1/...`
- 当前代码中存在 `/api/...` 的形式，可作为过渡：
  - v0.x：`/api/...`
  - v1.0+：逐步迁移到 `/api/v1/...`

### 1.2 兼容性原则

- **PATCH/新增字段**：尽量保持向后兼容（客户端忽略未知字段）
- **字段改名/删除**：必须走版本升级或提供兼容期
- **破坏性变更**：提升主版本号（SemVer）

## 2. URL 与资源命名

- 资源使用复数名词：
  - `/projects`、`/users`、`/platforms`
- 子资源：
  - `/projects/{project_id}/steps`
  - `/projects/{project_id}/attachments`

## 3. HTTP 方法语义

- `GET /resources`：列表
- `GET /resources/{id}`：详情
- `POST /resources`：创建
- `PUT /resources/{id}`：整体替换（不推荐频繁使用）
- `PATCH /resources/{id}`：局部更新（推荐）
- `DELETE /resources/{id}`：删除（软删优先）

## 4. 通用请求头

- `Authorization: Bearer <access_token>`
- `Content-Type: application/json`
- `X-Request-Id: <uuid>`（可选，便于链路追踪；服务端可生成并回传）

## 5. 统一响应结构（建议）

为开源与企业化考虑，建议建立统一 envelope：

```json
{
  "success": true,
  "data": {},
  "meta": {
    "request_id": "..."
  }
}
```

错误响应：

```json
{
  "success": false,
  "error": {
    "code": "AUTH_UNAUTHORIZED",
    "message": "Token missing or invalid",
    "details": {
      "reason": "..."
    }
  },
  "meta": {
    "request_id": "..."
  }
}
```

> 说明：当前项目可能是直接返回业务对象。可先不强制 envelope，但至少统一错误结构与错误码。

## 6. 错误码规范

### 6.1 错误码格式

- 使用稳定字符串：`<DOMAIN>_<ERROR>`
  - 例如：`AUTH_UNAUTHORIZED`、`PROJECT_NOT_FOUND`、`VALIDATION_ERROR`

### 6.2 HTTP 状态码映射

- `400 Bad Request`：参数错误/业务校验失败（非权限类）
- `401 Unauthorized`：未登录/Token 无效
- `403 Forbidden`：无权限
- `404 Not Found`：资源不存在
- `409 Conflict`：并发冲突/唯一约束冲突
- `422 Unprocessable Entity`：请求体校验失败（FastAPI 默认）
- `500 Internal Server Error`：未处理异常

### 6.3 建议的错误码集合

- 认证与权限：
  - `AUTH_UNAUTHORIZED`
  - `AUTH_FORBIDDEN`
  - `AUTH_TOKEN_EXPIRED`
  - `AUTH_REFRESH_INVALID`
- 通用：
  - `VALIDATION_ERROR`
  - `RESOURCE_NOT_FOUND`
  - `CONFLICT`
- 项目域：
  - `PROJECT_NOT_FOUND`
  - `PROJECT_STEP_NOT_FOUND`

## 7. 分页、排序与过滤

### 7.1 分页

- 查询参数：
  - `page`（从 1 开始）
  - `page_size`（默认 20，最大 200）

响应：

```json
{
  "items": [],
  "page": 1,
  "page_size": 20,
  "total": 123
}
```

### 7.2 排序

- `sort_by=created_at`
- `sort_order=asc|desc`

### 7.3 过滤

- 简单字段：`status=active`
- 时间范围：`created_from=...&created_to=...`

## 8. 幂等性与并发控制（建议）

- 对创建/支付类接口可引入：`Idempotency-Key`
- 对更新可引入：
  - `updated_at` 乐观锁
  - 或 `ETag / If-Match`

## 9. 鉴权与权限

- 认证：JWT access token + refresh token
- 权限：建议 RBAC
  - `roles`：admin、manager、member、finance（示例）
  - `permissions`：`project.read`、`project.write`、`billing.write` 等

## 10. OpenAPI 与前端契约生成

- 建议前端基于后端 `/openapi.json` 自动生成 TS client：
  - 生成 `types`（DTO 类型）
  - 生成 `api client`（请求函数）
- 约束：
  - 所有 API schema 必须在 OpenAPI 中可见
  - 不要在运行时动态拼 schema


