# 外包项目管理系统 1.0.0 架构与设计设想

> 本文是对现有「毕设代做管理系统」的升级规划文档，统一名称为 **外包项目管理系统**，并以企业级、敏捷开发、组件复用与开源友好为目标。

## 1. 项目整体定位

- **定位**：面向自由职业者、小团队和中小型外包公司的项目全生命周期管理系统，支持从线索录入、合同与费用管理、执行过程跟踪、交付与售后等完整流程。
- **目标用户**：
  - 外包团队负责人、项目经理
  - 参与开发的工程师、设计师、测试、运维
  - 财务/结算角色
- **核心目标**：
  - 降低单个项目的管理成本与沟通成本
  - 提升交付可视化程度（进度、风险、收益一目了然）
  - 支持多平台/多渠道订单（例如：第三方平台、直客等）
  - 为后续开源生态与插件化扩展（如 CI 集成、GitHub/Jira 集成）打基础

## 2. 目标架构概览

### 2.1 架构风格

- **整体风格**：分层架构 + 领域划分（按业务域拆模块），逐步向 DDD/Hexagonal 架构演进。
- **技术栈**：
  - 后端：FastAPI + SQLModel/SQLAlchemy + PostgreSQL
  - 前端：Vue 3 + TypeScript + Element Plus + Pinia
  - 基础设施：Docker / Docker Compose，支持本地与云环境部署

### 2.2 逻辑分层

后端分层建议：

1. **API 层（Interface Layer）**
   - 目录：`fastapi_back/app/api`
   - 职责：
     - HTTP 接口定义（路由）
     - 请求/响应模型（DTO）绑定
     - 鉴权、权限控制（依赖注入）
     - 调用应用服务层，不包含业务规则

2. **应用服务层（Application Services）**
   - 目录：`fastapi_back/app/services`
   - 职责：
     - 用例级别的业务编排（一个 API 对应一个或多个用例）
     - 事务边界控制
     - 跨聚合/跨模块协作

3. **领域层（Domain Layer）**
   - 目录：`fastapi_back/app/domain`
   - 职责：
     - 核心领域模型（实体、值对象、领域服务）
     - 领域规则与不可变业务约束
   - 说明：可先通过更清晰的 `models + schemas` 拆分过渡，逐步提炼真正的领域模型。

4. **基础设施层（Infrastructure Layer）**
   - 目录：`fastapi_back/app/infrastructure`（或 `repositories`、`adapters` 等）
   - 职责：
     - 数据库访问（Repository / DAO）
     - 第三方服务集成（GitHub、短信、邮件、支付等）
     - 存储实现（本地文件、S3 兼容存储）

前端分层建议：

1. **应用壳（App Shell）**
   - 目录：`project_manager_vue3/src/layouts`、`router`、`stores/root`
   - 职责：整体布局、导航、全局状态（用户会话、主题、国际化）。

2. **特性模块（Feature Modules）**
   - 目录：`src/features/<feature-name>`（推荐新建），过渡期兼容 `views`。
   - 职责：
     - 将每个业务域（项目、平台、结算、报表等）作为独立 feature 来组织
     - 内聚组件、接口调用、状态管理

3. **共享组件与工具（Shared）**
   - 目录：`src/shared/components`、`src/shared/hooks`、`src/shared/utils`
   - 职责：
     - 可复用的 UI 组件、表单、表格、弹窗
     - 通用 hooks（如 `useFetchTable`、`useDialog`）

## 3. 业务域与模块设计

### 3.1 核心业务域

1. **用户与权限（Auth & RBAC）**
   - 用户、角色、权限、访问日志
   - 支持管理员/项目经理/执行成员等角色

2. **平台与客户（Platforms & Clients）**
   - 多接单平台（第三方平台、自有渠道）
   - 客户信息管理（企业/个人、联系人、联系方式）

3. **项目与任务（Projects & Tasks）**
   - 项目基本信息（名称、客户、平台、金额、签订时间、交付时间）
   - 项目阶段与步骤模板（可配置、多模板支持）
   - 子任务/分工（分配到具体成员）

4. **文档与附件（Attachments）**
   - 需求文档、设计稿、代码包、验收材料
   - 文件夹与标签
   - 存储抽象（本地/对象存储）

5. **工时与成本（Time & Cost） [可选扩展]**
   - 工时记录、任务耗时统计
   - 项目毛利/净利

6. **结算与回款（Billing & Payments）**
   - 收入记录（合同金额、实收金额）
   - 回款计划与执行
   - 对账报表

7. **日志与审计（Logs & Audit）**
   - 项目日志、操作记录
   - 系统级审计日志（登录、权限变更等）

### 3.2 模块映射（后端）

- `app/api/auth.py` → 鉴权与用户管理 API
- `app/api/projects.py` → 项目 REST API（后续可分拆为 `projects`, `tasks`, `steps` 等）
- `app/api/platforms.py` → 平台管理
- `app/api/dashboard.py` → 概览与统计
- `app/api/system_settings.py` → 系统设置（含令牌时长、平台配置等）
- 未来新增：
  - `app/api/billing.py` → 结算与回款
  - `app/api/clients.py` → 客户管理
  - `app/api/audit_logs.py` → 审计日志

### 3.3 模块映射（前端）

推荐在 `src/features` 下按域划分：

- `src/features/auth`：登录、注册、权限管理
- `src/features/projects`：项目列表、详情、步骤、任务看板
- `src/features/dashboard`：数据总览与统计图表
- `src/features/clients`：客户列表与维护
- `src/features/billing`：费用、结算、回款
- `src/features/settings`：系统与个人设置


## 4. 数据库与存储设计

### 4.1 数据库技术选型

- **主库**：PostgreSQL（支持生产级事务、约束、扩展能力）
- **迁移工具**：Alembic（作为唯一 schema 迁移入口）

迁移策略：

1. 引入 Alembic，并基于当前 SQLModel 定义生成首个 `baseline` 迁移。
2. 禁止在生产环境中使用 `SQLModel.metadata.create_all(engine)`。
3. 新增表或字段只通过 Alembic 迁移完成。

### 4.2 多环境配置

- 本地开发：
  - 单 docker-compose，包含 Postgres
  - 环境变量示例：`DATABASE_URL=postgresql+psycopg2://user:pass@db:5432/outsource_manager`
- 测试环境：
  - 独立数据库 schema 或独立实例
  - CI 中自动执行 `alembic upgrade head` + 测试
- 生产环境：
  - 扩展连接池、开启慢查询日志
  - 明确备份与恢复策略

### 4.3 附件与文件存储

- 定义统一的 `Storage` 接口：
  - `LocalStorage`（开发环境默认）
  - `S3Storage`（面向云环境）
- 数据库中存路径/URL 与元数据（大小、MIME、上传人、上传时间）。


## 5. 工程化与开源化设计

### 5.1 仓库结构（目标形态）

```text
project_root/
├── fastapi_back/              # 后端
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── domain/            # 可选，逐步演进
│   │   ├── repositories/
│   │   ├── services/
│   │   └── schemas/
│   ├── alembic/
│   ├── requirements.txt
│   └── Dockerfile
│
├── project_manager_vue3/      # 前端
│   ├── src/
│   │   ├── features/
│   │   ├── shared/
│   │   └── ...
│   ├── package.json
│   └── Dockerfile
│
├── docs/
│   ├── 0.0.1/                 # 历史版本文档（当前已有）
│   └── 1.0.0/
│       ├── ARCHITECTURE_VISION.md
│       └── API_DESIGN.md      # 预留
│
├── docker-compose.yml
├── .env.example
└── README.md
```

### 5.2 Docker 与部署

- 后端镜像：
  - 基于官方 Python 镜像
  - 安装依赖 → 复制代码 → 运行 Alembic 迁移 → 启动 uvicorn
- 前端镜像：
  - 构建阶段（node）+ 运行阶段（nginx）
  - 构建产物放入 `/usr/share/nginx/html`，nginx 配反向代理到后端
- docker-compose：
  - `backend`、`frontend`、`db` 服务
  - 默认使用 `.env` 中的变量


## 6. 敏捷迭代与组件复用策略

### 6.1 敏捷迭代

- 按业务价值划分里程碑：
  - v0.1：外包项目基础管理 + Docker 一键启动
  - v0.2：PostgreSQL + Alembic 迁移体系
  - v0.3：领域模块化、前端 feature-first 重构
  - v1.0：权限体系完善、插件扩展点、S3 存储支持

### 6.2 组件复用

- 建立统一 UI 规范：按钮、表格、弹窗、表单布局统一
- 封装通用组件：
  - `DataTable`（分页、排序、筛选）
  - `FormDialog`（弹窗表单）
  - `SearchForm`（查询区）
- 建立通用 hooks：
  - `useFetchTable`、`useFormRequest`、`useConfirm` 等


## 7. 后续文档与设计

在 `docs/1.0.0` 下计划补充的文档：

- `API_DESIGN.md`：主要 API 设计、版本策略、错误码规范
- `DOMAIN_MODEL.md`：核心领域模型与关系图（项目、客户、平台、结算等）
- `DEPLOYMENT_GUIDE.md`：Docker 与生产环境部署指引
- `CONTRIBUTING.md`：开源贡献指南、代码规范、分支策略

---

本文件作为「外包项目管理系统」1.0.0 版本的整体架构与设想蓝图，后续所有重构与新功能设计，建议先在此文档或其子文档中评估与记录，再在代码中实现。
