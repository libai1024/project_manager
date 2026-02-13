# 外包项目管理系统 1.0.0 领域模型与表结构建议

本文档给出面向企业级演进的领域划分与推荐数据模型（以 PostgreSQL 为目标库）。重点在于：

- 领域边界清晰（便于模块化与团队协作）
- 数据一致性可控（约束、索引、外键、审计字段）
- 可扩展（未来引入多租户、插件、对象存储等）

> 说明：当前代码已包含 `users/projects/platforms/todos/attachments/tags` 等模型。本文以 1.0.0 目标形态做“规范化整理 + 建议补齐”。

## 1. 领域划分（Domain Boundaries）

- **Identity & Access（身份与权限）**
  - 用户、角色、权限、会话、登录日志
- **CRM（客户与渠道）**
  - 客户（Client）、联系人、渠道/平台（Platform）
- **Project Delivery（项目交付）**
  - 项目（Project）、阶段/步骤（Step）、任务（Task）、项目日志
- **Knowledge & Files（文档与附件）**
  - 附件、文件夹、标签、对象存储
- **Finance（财务与回款）**
  - 报价/合同、回款计划、收支流水（后续扩展）
- **System（系统设置与审计）**
  - 系统配置、操作审计日志

## 2. 通用建模约定（强烈建议）

### 2.1 通用字段

建议所有核心表包含：

- `id`：UUID 或 BIGINT（开源/分布式建议 UUID）
- `created_at`、`updated_at`：`timestamptz`，统一 UTC
- `created_by`、`updated_by`：可选，审计用途
- `is_deleted` 或 `deleted_at`：软删除（避免业务误删）

### 2.2 索引与约束

- 所有外键列建立索引（Postgres 不会自动为 FK 建索引）
- 明确唯一约束：
  - 用户名、邮箱（如启用）
  - 同一项目下步骤序号唯一等
- 对常用查询字段建立组合索引：
  - `project(status, updated_at)`
  - `todo(project_id, status, due_date)`

### 2.3 命名规则

- 表名：小写复数（`projects`、`users`）
- 列名：`snake_case`
- 关联表：`project_tags`（中间表）

## 3. 核心实体与关系（建议版）

### 3.1 用户与权限

#### `users`

- `id`
- `username`（unique）
- `password_hash`
- `display_name`
- `email`（可选 unique）
- `role`（过渡期可用 enum/string；长期建议 RBAC）
- `is_active`
- `last_login_at`

#### RBAC（建议引入）

- `roles`：`id, name, description`
- `permissions`：`id, code, description`
- `role_permissions`：`role_id, permission_id`
- `user_roles`：`user_id, role_id`

> 过渡策略：先保留当前 `role` 字段，后续平滑迁移到 RBAC。

#### `login_logs`

- `id`
- `user_id`
- `ip`
- `user_agent`
- `created_at`

#### Token 相关（如果继续采用 refresh token / blacklist）

- `refresh_tokens`：建议存 hash 而非明文
- `token_blacklist`：如采用可撤销 access token

### 3.2 客户与平台

#### `platforms`

- `id`
- `name`
- `description`

#### `clients`（建议新增）

- `id`
- `name`
- `type`（company/person）
- `notes`

#### `client_contacts`（建议新增）

- `id`
- `client_id`
- `name`
- `phone`
- `wechat`
- `email`
- `is_primary`

### 3.3 项目交付

#### `projects`

- `id`
- `name`
- `platform_id`（nullable：直客项目可为空）
- `client_id`（建议新增后关联）
- `status`（enum：planned/active/paused/done/archived）
- `price`（合同金额）
- `actual_income`（实收，可选）
- `start_date`、`due_date`、`delivered_at`
- `description`

#### `project_steps`

- `id`
- `project_id`
- `title`
- `order_index`（同一 project 内唯一）
- `status`
- `is_todo`
- `started_at`、`completed_at`

> 建议：将“步骤模板”与“实例步骤”分离，模板只用于生成。

#### `step_templates` / `step_template_items`

- `step_templates`：`id, name, description`
- `step_template_items`：`id, template_id, title, order_index`

#### `todos`

- `id`
- `project_id`（nullable：也支持个人 todo）
- `title`
- `status`（open/doing/done）
- `due_date`
- `assigned_to`（user_id，可选）

#### `project_logs`

- `id`
- `project_id`
- `type`（status_change/comment/system）
- `content`
- `created_by`
- `created_at`

### 3.4 文档与附件

#### `attachment_folders`

- `id`
- `project_id`
- `name`
- `parent_id`（支持树形目录）

#### `attachments`

- `id`
- `project_id`
- `folder_id`
- `filename`
- `content_type`
- `size_bytes`
- `storage_provider`（local/s3）
- `storage_path`（或 `object_key`）
- `uploaded_by`
- `created_at`

### 3.5 标签体系

- `tags`：`id, name, color`
- `project_tags`：`project_id, tag_id`
- `attachment_tags`（可选）：`attachment_id, tag_id`

## 4. 财务（建议扩展模块）

> 当前项目已有 `actual_income` 等字段。若要更企业化，建议引入更规范的财务子域。

### 4.1 合同与回款

- `contracts`：`id, project_id, amount, signed_at, file_attachment_id`
- `payment_plans`：`id, project_id, amount, due_date, status`
- `payments`：`id, project_id, amount, paid_at, method, note`

## 5. 多租户（未来可选）

若后续要做 SaaS 化：

- 新增 `tenants` 表
- 核心业务表增加 `tenant_id`
- 鉴权中注入 tenant 上下文
- 所有查询强制 tenant 过滤（可用 SQLAlchemy 的 query hook/拦截器）

## 6. 与现有代码的落地建议（迁移路径）

- 第 1 步：引入 Alembic，生成 baseline 迁移（基于当前模型）
- 第 2 步：将 SQLite 作为开发可选项，默认 Postgres
- 第 3 步：逐个引入：`clients`、RBAC 表、财务表
- 第 4 步：为所有关键表补齐：索引、唯一约束、软删除、审计字段


