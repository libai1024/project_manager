# 毕设代做管理系统

一个专业的毕业设计代做项目管理系统，用于跟踪和提醒毕设项目的进度、报酬、关键资料等。

> 📖 **架构文档**：详细的技术架构和API文档请查看 [fastapi_back/ARCHITECTURE.md](./docs/0.0.1/fastapi_back/ARCHITECTURE.md)

## 技术栈

### 后端
- FastAPI
- SQLModel (SQLAlchemy + Pydantic)
- SQLite
- JWT认证

### 前端
- Vue 3 (Composition API)
- Element Plus
- Pinia (状态管理)
- Vue Router
- Axios
- ECharts (数据可视化)

## 功能特性

1. **用户管理**
   - 多用户登录系统
   - 管理员和普通用户角色
   - 用户CRUD操作（仅管理员）

2. **平台管理**
   - 支持多个接单平台
   - 平台信息管理

3. **项目管理**
   - 创建和管理毕设项目
   - 自动生成13个默认步骤
   - 手动添加和编辑步骤
   - 步骤状态跟踪（待开始/进行中/已完成）
   - 步骤Todo标记

4. **Dashboard**
   - 今日待办列表
   - 收益统计（总收益、平台收益）
   - 项目进度统计

## 快速开始

### 方式一：使用启动脚本（推荐）

#### 一键启动（同时启动前后端）

**Linux/macOS:**
```bash
./start_all.sh
```

**Windows:**
```cmd
start_all.bat
```

#### 分别启动

**后端启动（Linux/macOS）:**
```bash
cd fastapi_back
./start.sh
```

**后端启动（Windows）:**
```cmd
cd fastapi_back
start.bat
```

**前端启动（Linux/macOS）:**
```bash
cd project_manager_vue3
./start.sh
```

**前端启动（Windows）:**
```cmd
cd project_manager_vue3
start.bat
```

启动脚本会自动完成以下操作：
- ✅ 检查环境（Python/Node.js）
- ✅ 创建并激活虚拟环境（后端）
- ✅ 安装缺失的依赖包
- ✅ 初始化数据库（首次运行）
- ✅ 启动服务

### 方式二：手动启动

#### 后端启动

1. 进入后端目录：
```bash
cd fastapi_back
```

2. 创建虚拟环境（推荐）：
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

3. 安装依赖：
```bash
pip install -r requirements.txt
```

4. 初始化数据库（创建默认管理员）：
```bash
python app/init_db.py
```

5. 启动服务：
```bash
uvicorn main:app --reload --port 8000
```

#### 前端启动

1. 进入前端目录：
```bash
cd project_manager_vue3
```

2. 安装依赖：
```bash
npm install
```

3. 启动开发服务器：
```bash
npm run dev
```

### 默认账号

- 用户名：`admin`
- 密码：`admin123`

### 访问地址

- 前端界面：http://localhost:5173
- 后端API：http://localhost:8000
- API文档：http://localhost:8000/docs
- ReDoc文档：http://localhost:8000/redoc

## 项目结构

```
project_manager/
├── fastapi_back/          # 后端项目
│   ├── app/
│   │   ├── api/          # API路由
│   │   ├── core/         # 核心配置（数据库、认证等）
│   │   ├── models/       # 数据模型
│   │   └── init_db.py    # 数据库初始化脚本
│   ├── main.py           # 应用入口
│   └── requirements.txt  # Python依赖
│
└── project_manager_vue3/  # 前端项目
    ├── src/
    │   ├── api/          # API接口
    │   ├── components/   # 组件
    │   ├── layouts/      # 布局组件
    │   ├── router/       # 路由配置
    │   ├── stores/       # Pinia状态管理
    │   └── views/        # 页面视图
    └── package.json      # 前端依赖
```

## API文档

启动后端服务后，访问以下地址查看API文档：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 默认项目步骤

创建新项目时，系统会自动生成以下13个默认步骤：

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

这些步骤可以手动编辑、删除或重新排序。

## 开发说明

### 数据库

系统使用SQLite数据库，数据库文件位于 `fastapi_back/project_manager.db`

### 环境变量

后端可以通过 `.env` 文件配置环境变量：
- `DATABASE_URL`: 数据库连接URL
- `SECRET_KEY`: JWT密钥
- `CORS_ORIGINS`: CORS允许的源

### 生产部署

生产环境部署时，请：
1. 修改默认管理员密码
2. 更改 `SECRET_KEY` 为强随机字符串
3. 配置合适的CORS策略
4. 使用生产级数据库（如PostgreSQL）
5. 配置HTTPS

## 许可证

MIT License

