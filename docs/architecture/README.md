# 系统架构文档

## 技术栈

### 后端
- **FastAPI**: 高性能 Python Web 框架
- **SQLModel**: ORM 框架，结合 SQLAlchemy 和 Pydantic
- **SQLite**: 数据库（生产环境计划迁移到 PostgreSQL）
- **Pydantic**: 数据验证和序列化
- **python-jose**: JWT 认证
- **bcrypt**: 密码哈希

### 前端
- **Vue 3**: 渐进式 JavaScript 框架
- **TypeScript**: 类型安全的 JavaScript 超集
- **Vite**: 下一代前端构建工具
- **Pinia**: Vue 状态管理
- **Element Plus**: Vue 3 UI 组件库
- **Axios**: HTTP 客户端

---

## 系统架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                        前端 (Vue 3)                              │
├─────────────────────────────────────────────────────────────────┤
│  Views ←→ Stores (Pinia) ←→ Composables ←→ Services ←→ API     │
│    ↓                                                             │
│  Components                                                      │
└───────────────────────────────┬─────────────────────────────────┘
                                │ HTTP/REST
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                       后端 (FastAPI)                             │
├─────────────────────────────────────────────────────────────────┤
│  API Layer (Routers) → Service Layer → Repository Layer         │
│         ↓                ↓                  ↓                   │
│  Responses/Exceptions   Business Logic    Data Access           │
└───────────────────────────────┬─────────────────────────────────┘
                                │ SQLModel
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                        数据库 (SQLite)                           │
└─────────────────────────────────────────────────────────────────┘
```

---

## 后端架构

### 目录结构

```
fastapi_back/
├── main.py                    # 应用入口
├── requirements.txt           # 依赖
├── pytest.ini                 # 测试配置
├── app/
│   ├── api/                   # API 路由层
│   │   ├── deps.py            # 依赖注入
│   │   ├── responses.py       # 统一响应模型
│   │   └── v1/endpoints/      # API 端点
│   │       ├── auth.py
│   │       ├── users.py
│   │       ├── projects.py
│   │       └── ...
│   ├── core/                  # 核心配置
│   │   ├── config.py          # 应用配置
│   │   ├── database.py        # 数据库连接
│   │   ├── security.py        # 安全相关
│   │   ├── dependencies.py    # 认证依赖
│   │   └── exceptions.py      # 自定义异常
│   ├── models/                # ORM 模型
│   │   ├── user.py
│   │   ├── project.py
│   │   ├── platform.py
│   │   └── ...
│   ├── schemas/               # Pydantic Schema (DTO)
│   │   ├── base.py            # 基础 Schema
│   │   ├── user.py
│   │   ├── project.py
│   │   └── ...
│   ├── services/              # 业务逻辑层
│   │   ├── user_service.py
│   │   ├── project_service.py
│   │   └── ...
│   ├── repositories/          # 数据访问层
│   │   ├── base.py            # BaseRepository
│   │   ├── user_repository.py
│   │   ├── project_repository.py
│   │   └── ...
│   ├── utils/                 # 工具函数
│   │   ├── constants.py       # 常量/枚举
│   │   └── permissions.py     # 权限检查
│   └── exceptions/            # 异常处理器
│       └── handlers.py
├── tests/                     # 测试
│   ├── conftest.py            # Pytest 配置
│   ├── unit/                  # 单元测试
│   └── integration/           # 集成测试
└── uploads/                   # 文件存储
```

### 分层架构

#### 1. API 层 (`app/api/`)
- 处理 HTTP 请求/响应
- 路由定义和参数验证
- 调用 Service 层处理业务逻辑
- 返回统一格式的响应

```python
@router.get("/", response_model=ApiResponse[List[ProjectRead]])
async def list_projects(
    service: ProjectService = Depends(get_project_service),
    current_user: User = Depends(get_current_user)
):
    projects = service.list_projects(
        user_id=current_user.id,
        is_admin=current_user.role == "admin"
    )
    return success(projects)
```

#### 2. Service 层 (`app/services/`)
- 实现业务逻辑
- 事务管理
- 权限检查
- 跨实体操作编排

```python
class ProjectService:
    def update_project(self, id: int, data: ProjectUpdate, current_user_id: int, is_admin: bool):
        project = self._get_project_or_raise(id)
        check_project_access(current_user_id, project, is_admin)
        return self.project_repo.update(project, data.model_dump(exclude_unset=True))
```

#### 3. Repository 层 (`app/repositories/`)
- 数据库 CRUD 操作
- 继承 `BaseRepository` 获得通用方法
- 实现实体特定的查询方法

```python
class ProjectRepository(BaseRepository[Project]):
    def list_by_user(self, user_id: int) -> List[Project]:
        return self.find_many(user_id=user_id)

    def list_by_platform(self, platform_id: int) -> List[Project]:
        return self.find_many(platform_id=platform_id)
```

### 统一响应格式

所有 API 响应使用统一格式：

```python
# 成功响应
{
    "code": 200,
    "msg": "success",
    "data": { ... }
}

# 错误响应
{
    "code": 400,
    "msg": "错误消息",
    "data": null
}
```

### 异常处理

自定义异常类：
- `NotFoundException`: 资源不存在
- `ForbiddenException`: 权限不足
- `BusinessException`: 业务逻辑错误

全局异常处理器将异常转换为统一响应格式。

---

## 前端架构

### 目录结构

```
project_manager_vue3/src/
├── main.ts                    # 应用入口
├── App.vue                    # 根组件
├── router/                    # 路由配置
│   └── index.ts
├── stores/                    # Pinia 状态管理
│   ├── user.ts
│   ├── project.ts
│   └── platform.ts
├── api/                       # API 客户端
│   ├── request.ts             # Axios 实例
│   ├── project.ts
│   ├── user.ts
│   └── ...
├── services/                  # 前端服务层
│   ├── project.service.ts
│   ├── platform.service.ts
│   └── ...
├── composables/               # 组合式函数
│   ├── useProject.ts
│   ├── usePluginSettings.ts
│   └── ...
├── components/                # 组件
│   ├── common/                # 通用组件
│   ├── business/              # 业务组件
│   └── project-detail/        # 项目详情相关组件
│       ├── ProjectInfoCard.vue
│       ├── ProjectStepsTimeline.vue
│       └── dialogs/           # 对话框组件
├── views/                     # 页面视图
├── types/                     # TypeScript 类型定义
├── constants/                 # 常量定义
├── utils/                     # 工具函数
└── styles/                    # 样式文件
```

### 状态管理 (Pinia)

```typescript
export const useProjectStore = defineStore('project', () => {
  // 状态
  const projects = ref<Project[]>([])
  const currentProject = ref<Project | null>(null)

  // 计算属性
  const projectCount = computed(() => projects.value.length)

  // 方法
  const loadProjects = async () => { ... }
  const createProject = async (data) => { ... }

  return { projects, currentProject, projectCount, loadProjects, createProject }
})
```

### 组合式函数 (Composables)

```typescript
export function usePluginSettings() {
  const pluginEnabledIds = ref<Map<PluginType, number[]>>(new Map())

  const isProjectEnabled = (projectId: number, pluginType: PluginType) => {
    return pluginEnabledIds.value.get(pluginType)?.includes(projectId) ?? false
  }

  return { pluginEnabledIds, isProjectEnabled, ... }
}
```

### 组件拆分原则

大型组件（如 ProjectDetail.vue）按功能拆分：
1. **卡片组件**: `ProjectInfoCard`, `ProjectRequirementsCard`, `ProjectTagsCard`
2. **时间线组件**: `ProjectStepsTimeline`, `ProjectLogsTimeline`
3. **功能组件**: `ProjectFilesManager`
4. **对话框组件**: `AddStepDialog`, `UploadDialog`, `FilePreviewDialog`
5. **插件组件**: `GraduationPlugin`, `GitHubPlugin`, `ProjectPartsPlugin`

---

## 认证流程

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│    Client    │────▶│   FastAPI    │────▶│   Database   │
└──────────────┘     └──────────────┘     └──────────────┘
       │                    │
       │  1. Login          │
       │  username/password │
       │ ──────────────────▶│
       │                    │ 2. Verify password
       │                    │ ─────────────────▶
       │                    │
       │  3. JWT Token      │
       │ ◀──────────────────│
       │                    │
       │  4. API Request    │
       │  + Bearer Token    │
       │ ──────────────────▶│
       │                    │ 5. Validate token
       │                    │    & get user
       │  6. Response       │
       │ ◀──────────────────│
```

---

## 测试策略

### 后端测试 (pytest)

```python
# tests/unit/test_project_service.py
def test_create_project(session, test_user, test_platform):
    service = ProjectService(session)
    project_data = ProjectCreate(
        title="新项目",
        platform_id=test_platform.id,
        user_id=test_user.id
    )
    project = service.create_project(project_data)
    assert project.id is not None
    assert project.title == "新项目"
```

### 前端测试 (Vitest)

```typescript
// src/__tests__/stores/platform.store.test.ts
describe('Platform Store', () => {
  it('loadPlatforms 加载平台列表', async () => {
    const store = usePlatformStore()
    await store.loadPlatforms()
    expect(store.platforms.length).toBeGreaterThan(0)
    expect(store.loaded).toBe(true)
  })
})
```

---

## 部署架构（计划）

```
                    ┌─────────────┐
                    │   Nginx     │
                    │  (反向代理)  │
                    └──────┬──────┘
                           │
          ┌────────────────┼────────────────┐
          │                │                │
          ▼                ▼                ▼
    ┌──────────┐    ┌──────────┐    ┌──────────┐
    │ Frontend │    │ Backend  │    │ Database │
    │ (静态文件) │    │ (FastAPI)│    │(PostgreSQL)│
    └──────────┘    └──────────┘    └──────────┘
```

---

## 扩展阅读

- [API 文档](./api/README.md)
- [CLAUDE.md](../../CLAUDE.md) - Claude Code 项目指南
- [FastAPI 官方文档](https://fastapi.tiangolo.com/)
- [Vue 3 官方文档](https://vuejs.org/)
- [Pinia 官方文档](https://pinia.vuejs.org/)
