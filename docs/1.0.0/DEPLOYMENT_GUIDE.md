# 外包项目管理系统 1.0.0 部署指南（Docker / Compose / 生产建议）

本文档描述「外包项目管理系统」的推荐部署方式，重点面向开源用户的 **Docker / Docker Compose 一键部署**，并给出生产环境的关键注意事项。

## 1. 部署目标与约定

- **目标**：`docker compose up -d` 后即可获得可用系统（前端 + 后端 + 数据库）。
- **推荐主数据库**：PostgreSQL。
- **配置方式**：使用环境变量（`.env` 文件）。
- **文件存储**：默认本地持久化卷（后续可扩展 S3/MinIO）。

> 说明：当前仓库尚未完全落地 Compose/Alembic/PostgreSQL，本指南作为 1.0.0 的目标形态与实施说明；实现落地时以本指南为准逐项补齐。

## 2. Docker 镜像设计

### 2.1 后端（FastAPI）镜像

推荐使用多层缓存友好的构建：

- 基础镜像：`python:3.12-slim`（或你实际支持的 Python 版本）
- 安装系统依赖：`build-essential`（如需编译依赖）、`libpq-dev`（Postgres 驱动）等
- 安装 Python 依赖：`pip install -r requirements.txt`
- 复制代码并启动：
  - 生产模式：`uvicorn main:app --host 0.0.0.0 --port 8000`

建议在容器启动前执行：
- `alembic upgrade head`

### 2.2 前端（Vue3）镜像

推荐：**构建阶段 Node + 运行阶段 Nginx**。

- build stage：`node:20-alpine` 执行 `npm ci && npm run build`
- runtime stage：`nginx:stable-alpine` 托管 `dist/`
- Nginx 反代：将 `/api` 代理到后端服务 `backend:8000`

这样可获得：
- 静态资源高性能
- SPA 刷新路由正确
- 单容器即可对外提供前端

## 3. Docker Compose（推荐）

### 3.1 服务组成

- `db`：PostgreSQL
- `backend`：FastAPI API 服务
- `frontend`：Nginx 托管 Vue build 产物 + 反向代理

可选：
- `redis`：用于缓存、限流、任务队列（若后续引入 Celery/RQ 等）

### 3.2 环境变量（.env）建议

提供 `.env.example`，并在文档中说明每个变量。

后端常见变量：

- `ENV=dev|prod`
- `DATABASE_URL=postgresql+psycopg://user:pass@db:5432/outsource_manager`
- `SECRET_KEY=...`（生产必须更换）
- `CORS_ALLOW_ALL=false`
- `CORS_ORIGINS=["https://your.domain"]`
- `UPLOAD_DIR=/data/uploads`（本地卷挂载路径）

数据库常见变量：

- `POSTGRES_DB=outsource_manager`
- `POSTGRES_USER=outsource`
- `POSTGRES_PASSWORD=...`

### 3.3 数据持久化

- Postgres：挂载到 `db_data` volume
- 上传文件：挂载到 `uploads_data` volume

## 4. 生产环境关键建议

### 4.1 反向代理与 HTTPS

建议使用：
- Nginx / Caddy / Traefik 作为入口网关
- 配置 HTTPS（Let’s Encrypt）

### 4.2 数据库备份

- 使用 `pg_dump` 定期备份
- 建议设置：
  - 每日全量
  - 保留 7/14/30 天策略
  - 异地存储（对象存储）

### 4.3 安全配置

- 必须更换：
  - `SECRET_KEY`
  - 默认管理员密码（如存在）
- 限制 CORS：
  - 生产环境禁止 `CORS_ALLOW_ALL=true`
- 日志：
  - 避免打印敏感 header/token
  - 统一输出到 stdout，交给容器平台收集

### 4.4 资源与性能

- 后端：
  - 使用多 worker（例如 `gunicorn -k uvicorn.workers.UvicornWorker`）
  - 配置 DB 连接池与超时
- 前端：
  - 开启 gzip/brotli（由 Nginx/网关处理）

## 5. CI/CD（推荐形态）

- PR 检查：
  - 后端：lint（ruff/flake8）、类型检查（mypy 可选）、单元测试（pytest）
  - 前端：eslint、typecheck、build
- 发布：
  - Git tag（语义化版本）触发镜像构建并推送到 GHCR/DockerHub

## 6. 常见问题排查（建议）

- **容器启动但接口 502**：检查前端 Nginx 反代目标是否为 `backend:8000`
- **数据库连不上**：检查 `DATABASE_URL` host 是否为 `db`
- **迁移失败**：检查 `alembic` 配置与容器启动顺序（`depends_on` + 重试）


