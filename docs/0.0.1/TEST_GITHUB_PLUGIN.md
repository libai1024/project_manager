# GitHub插件测试指南

## 测试仓库
- **仓库地址**: https://github.com/UsefulElectronics/esp32s3-gc9a01-lvgl
- **默认分支**: main
- **预期结果**: 应该能获取到76个commits（根据GitHub页面显示）

## 前置条件

### 1. 确保后端服务运行
```bash
cd fastapi_back
./start.sh
# 或
source venv/bin/activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

后端应该运行在：http://localhost:8000

### 2. 确保前端服务运行
```bash
cd project_manager_vue3
./start.sh
# 或
npm run dev
```

前端应该运行在：http://localhost:5173

### 3. 确保已安装依赖
- 后端：`requests` 库已安装（已在requirements.txt中添加）
- 数据库：`github_commit` 表已创建（迁移脚本已执行）

## 测试步骤

### 步骤1：登录系统
1. 访问 http://localhost:5173
2. 使用管理员账号登录

### 步骤2：创建或编辑项目
1. 进入项目列表页面（http://localhost:5173/projects）
2. 选择一个项目，或创建一个新项目
3. 进入项目详情页面（http://localhost:5173/projects/{project_id}）

### 步骤3：启用GitHub插件
1. 在项目详情页面，确保GitHub插件已启用
   - 如果未启用，前往：设置 → 插件管理 → GitHub插件 → 选择该项目启用

### 步骤4：添加GitHub地址
1. 在项目详情页面，找到"GitHub 仓库"卡片
2. 点击"添加"或"编辑"按钮
3. 输入GitHub地址：`https://github.com/UsefulElectronics/esp32s3-gc9a01-lvgl`
4. 点击"确定"保存

### 步骤5：测试自动同步
1. 保存GitHub地址后，系统会自动：
   - 从GitHub API获取commits
   - 存储到数据库
   - 显示在界面上

2. 观察结果：
   - 应该能看到commits列表
   - 每个commit显示：消息、作者、时间、SHA
   - 可以点击SHA复制
   - 可以点击"查看详情"跳转到GitHub

### 步骤6：测试手动同步
1. 点击"同步"按钮
2. 观察：
   - 按钮显示"同步中..."
   - 完成后显示"同步成功"
   - Commits列表更新

### 步骤7：测试1分钟限流
1. 在1分钟内多次点击"同步"按钮
2. 观察：
   - 第一次会从GitHub同步
   - 后续请求会使用缓存（如果1分钟内）

### 步骤8：测试分支切换
1. 在分支选择下拉框中选择不同分支（如果有）
2. 观察：
   - Commits列表会根据分支更新
   - 每个分支的commits是独立存储的

## API测试（可选）

### 使用curl测试后端API

#### 1. 获取commits（自动同步）
```bash
curl -X GET "http://localhost:8000/api/github-commits/projects/1/commits?branch=main" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Accept: application/json"
```

#### 2. 强制同步
```bash
curl -X GET "http://localhost:8000/api/github-commits/projects/1/commits?branch=main&force_sync=true" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Accept: application/json"
```

#### 3. 手动触发同步
```bash
curl -X POST "http://localhost:8000/api/github-commits/projects/1/sync?branch=main" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Accept: application/json"
```

## 预期结果

### 成功情况
- ✅ GitHub地址保存成功
- ✅ Commits自动同步并显示
- ✅ 能看到76个commits（根据仓库实际情况）
- ✅ 每个commit信息完整（SHA、消息、作者、时间、URL）
- ✅ 手动同步功能正常
- ✅ 1分钟限流生效
- ✅ 数据存储在数据库中

### 可能的问题

#### 1. GitHub API速率限制
- **现象**: 返回403错误
- **原因**: 未认证的GitHub API每小时只有60次请求
- **解决**: 
  - 等待一段时间后重试
  - 或在`github_service.py`中添加GitHub Token

#### 2. 仓库不存在或分支不存在
- **现象**: 返回404错误
- **原因**: 仓库地址错误或分支不存在
- **解决**: 检查仓库地址和分支名称

#### 3. 网络连接问题
- **现象**: 请求超时或连接失败
- **原因**: 无法访问GitHub API
- **解决**: 检查网络连接

#### 4. 数据库错误
- **现象**: 同步失败
- **原因**: 数据库表未创建或连接失败
- **解决**: 运行迁移脚本 `python3 migrate_add_github_commits.py`

## 验证数据库

### 检查commits是否存储
```bash
cd fastapi_back
source venv/bin/activate
python3 -c "
from sqlmodel import create_engine, Session, select
from app.models.github_commit import GitHubCommit

engine = create_engine('sqlite:///project_manager.db')
with Session(engine) as session:
    commits = session.exec(select(GitHubCommit)).all()
    print(f'数据库中共有 {len(commits)} 条commits')
    for commit in commits[:5]:
        print(f'- {commit.sha[:7]}: {commit.message[:50]}...')
"
```

## 调试技巧

### 1. 查看后端日志
后端服务会输出详细的日志，包括：
- GitHub API请求状态
- 同步进度
- 错误信息

### 2. 查看浏览器控制台
前端会在控制台输出：
- API请求和响应
- 错误信息

### 3. 检查网络请求
在浏览器开发者工具的Network标签中：
- 查看API请求URL
- 查看请求参数
- 查看响应数据

## 测试检查清单

- [ ] 后端服务正常运行
- [ ] 前端服务正常运行
- [ ] 已登录系统
- [ ] GitHub插件已启用
- [ ] GitHub地址已添加
- [ ] Commits自动同步成功
- [ ] Commits列表正确显示
- [ ] 手动同步功能正常
- [ ] 1分钟限流生效
- [ ] 数据存储在数据库
- [ ] 所有UI交互正常

