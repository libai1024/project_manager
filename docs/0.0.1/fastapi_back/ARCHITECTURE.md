# 系统架构文档

## 技术栈

### 前端
- **Vue 3** (Composition API / Script Setup)
- **Vite** (构建工具)
- **Element Plus** (UI框架) - 已定制黑白极简线条风格主题
- **Pinia** (状态管理)
- **Vue Router** (路由管理)
- **Axios** (HTTP客户端)
- **ECharts** (数据可视化，Dashboard图表)

### 后端
- **FastAPI** (Python Web框架)
- **SQLModel** (SQLAlchemy + Pydantic)
- **SQLite** (数据库)
- **python-jose** (JWT Token鉴权)
- **bcrypt** (密码哈希)

### 部署
- 本地运行（SQLite单机部署）
- Docker（可选，生产环境）

## 数据库模型设计 (ER Schema)

### User (用户表)
```python
- id: int (主键)
- username: str (唯一索引)
- password_hash: str
- role: str (admin/user)
- created_at: datetime
```

### Platform (接单平台表)
```python
- id: int (主键)
- name: str (索引)
- description: str (可选)
- created_at: datetime
```

### Project (毕设项目表)
```python
- id: int (主键)
- title: str (索引)
- student_name: str (可选)
- platform_id: int (外键 -> Platform)
- user_id: int (外键 -> User)
- price: float (订单金额)
- status: str (当前整体状态)
- github_url: str (可选)
- requirements: str (需求文本，可选)
- is_paid: bool (是否已结清)
- created_at: datetime
- updated_at: datetime
```

### ProjectStep (项目步骤表 - 核心)
```python
- id: int (主键)
- project_id: int (外键 -> Project)
- name: str (步骤名)
- order_index: int (排序索引)
- status: str (Pending/In Progress/Done)
- is_todo: bool (关键字段，标记是否被@到了今日待办)
- deadline: datetime (可选)
- created_at: datetime
- updated_at: datetime
```

**默认步骤列表**（创建项目时自动生成）：
1. 已接单
2. 已规划
3. 硬件完成
4. 软件完成
5. 软硬调试
6. 实物验收
7. 实物邮寄
8. 论文框架
9. 论文初稿
10. 论文终稿
11. 答辩辅导
12. 毕设通过（待结账）
13. 已结账

### Attachment (附件表)
```python
- id: int (主键)
- project_id: int (外键 -> Project)
- file_path: str (文件存储路径)
- file_name: str (原始文件名)
- file_type: str (需求/开题报告/初稿/终稿/其他)
- description: str (可选)
- created_at: datetime
```

## API 接口规划 (RESTful)

### AUTH (认证)
- `POST /api/auth/login` - 用户登录
- `POST /api/auth/register` - 用户注册（管理员）
- `GET /api/auth/me` - 获取当前用户信息

### PLATFORMS (平台管理)
- `GET /api/platforms/` - 获取所有平台列表
- `POST /api/platforms/` - 创建新平台
- `GET /api/platforms/{id}` - 获取平台详情
- `PUT /api/platforms/{id}` - 更新平台信息
- `DELETE /api/platforms/{id}` - 删除平台

### PROJECTS (项目管理)
- `GET /api/projects/` - 获取项目列表（支持筛选）
- `POST /api/projects/` - 创建新项目（自动生成13个默认步骤）
- `GET /api/projects/{id}` - 获取项目详情（包含步骤列表）
- `PUT /api/projects/{id}` - 更新项目信息
- `DELETE /api/projects/{id}` - 删除项目

### STEPS (步骤管理)
- `POST /api/projects/{project_id}/steps` - 为项目添加新步骤
- `PUT /api/projects/steps/{step_id}` - 更新步骤信息（状态、待办等）
- `DELETE /api/projects/steps/{step_id}` - 删除步骤
- `POST /api/projects/steps/{step_id}/toggle-todo` - 切换步骤的Todo状态
- `POST /api/projects/steps/reorder` - 重新排序步骤

### ATTACHMENTS (附件管理)
- `GET /api/attachments/project/{project_id}` - 获取项目的所有附件
- `POST /api/attachments/project/{project_id}` - 上传附件
- `GET /api/attachments/{id}` - 获取附件详情
- `PUT /api/attachments/{id}` - 更新附件信息
- `DELETE /api/attachments/{id}` - 删除附件
- `GET /api/attachments/{id}/download` - 下载附件

### DASHBOARD (工作台)
- `GET /api/dashboard/stats` - 获取Dashboard统计数据
  - 今日Todo列表
  - 总收益
  - 平台收益统计
  - 待处理项目数
  - 进行中步骤数

### USERS (用户管理 - 仅管理员)
- `GET /api/users/` - 获取所有用户列表
- `GET /api/users/{id}` - 获取用户详情
- `PUT /api/users/{id}` - 更新用户信息
- `DELETE /api/users/{id}` - 删除用户

## 核心业务逻辑

### 1. 项目创建与默认步骤生成

当创建新项目时（`POST /api/projects/`），后端自动执行：

```python
1. 创建 Project 记录
2. 自动生成13个 ProjectStep，按顺序设置 order_index (0-12)
3. 所有步骤初始状态为 PENDING
4. is_todo 默认为 False
```

### 2. Todo 机制

- 用户可以在项目详情页手动将某个步骤标记为 `is_todo = True`
- Dashboard 显示所有 `is_todo = True` 且 `status != DONE` 的步骤
- 可以通过 `POST /api/projects/steps/{step_id}/toggle-todo` 切换Todo状态

### 3. 步骤状态流转

```
PENDING (待开始) -> IN_PROGRESS (进行中) -> DONE (已完成)
```

### 4. 权限控制

- **普通用户**：只能查看和管理自己的项目
- **管理员**：可以查看和管理所有项目，管理用户和平台

## 前端架构

### 路由结构
```
/ (MainLayout)
  ├── /dashboard - 工作台（今日Todo、收益统计）
  ├── /projects - 项目管理列表
  ├── /projects/:id - 项目详情（步骤管理）
  ├── /platforms - 平台管理
  └── /users - 用户管理（仅管理员）
```

### 状态管理 (Pinia)
- `userStore` - 用户信息和认证状态

### 主题系统
- **黑白极简线条风格**
- 全局CSS变量系统
- Element Plus组件主题定制
- 响应式设计支持

## 文件结构

```
fastapi_back/
├── app/
│   ├── api/              # API路由
│   │   ├── auth.py       # 认证
│   │   ├── platforms.py # 平台管理
│   │   ├── projects.py   # 项目管理
│   │   ├── dashboard.py  # Dashboard
│   │   ├── users.py      # 用户管理
│   │   └── attachments.py # 附件管理
│   ├── core/             # 核心配置
│   │   ├── config.py     # 配置
│   │   ├── database.py   # 数据库连接
│   │   ├── security.py   # 安全（密码、JWT）
│   │   └── dependencies.py # 依赖注入
│   ├── models/           # 数据模型
│   │   ├── user.py
│   │   ├── platform.py
│   │   ├── project.py
│   │   └── attachment.py
│   └── init_db.py        # 数据库初始化
├── main.py               # 应用入口
└── requirements.txt      # 依赖

project_manager_vue3/
├── src/
│   ├── api/              # API接口
│   ├── components/       # 组件
│   ├── layouts/          # 布局
│   ├── router/           # 路由
│   ├── stores/           # Pinia状态
│   ├── styles/           # 主题样式
│   │   ├── theme.css
│   │   ├── element-plus-theme.css
│   │   └── components.css
│   └── views/            # 页面视图
└── package.json
```

## 部署说明

### 开发环境
1. 后端：`cd fastapi_back && ./start.sh`
2. 前端：`cd project_manager_vue3 && npm run dev`

### 生产环境
1. 使用 Docker 容器化部署
2. 将 SQLite 替换为 PostgreSQL（可选）
3. 配置环境变量（SECRET_KEY等）
4. 使用 Nginx 反向代理

## 安全考虑

1. **密码安全**：使用 bcrypt 哈希，12轮加密
2. **JWT认证**：24小时有效期
3. **权限控制**：基于角色的访问控制（RBAC）
4. **文件上传**：限制文件类型和大小
5. **SQL注入防护**：使用 SQLModel ORM

## 扩展性

系统设计支持以下扩展：
- 多用户协作（项目分配）
- 项目模板（自定义默认步骤）
- 时间追踪（记录每个步骤耗时）
- 通知系统（截止时间提醒）
- 报表导出（Excel/PDF）


