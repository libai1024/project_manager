# 归档项目管理功能

## 功能概述

归档项目管理功能允许用户上传和管理已完成项目的源码和说明文件。归档后的项目非管理员不可编辑，时间线步骤固定为"已归档"状态。

## 主要功能

### 1. 项目归档
- 上传项目源码文件
- 上传项目说明文件（README、文档等）
- 填写项目基本信息（标题、学生姓名、技术栈、完成日期、描述等）
- 自动创建"已归档"步骤（状态固定为已完成）

### 2. 项目查看
- 所有用户可查看归档项目列表
- 支持搜索（标题、学生姓名、技术栈、描述）
- 卡片式展示，美观直观
- 显示文件统计信息（源码文件数、说明文件数、总文件数）

### 3. 项目详情
- 查看项目完整信息
- 查看步骤时间线（固定为"已归档"状态）
- 分类查看源码文件和说明文件
- 文件预览和下载功能

### 4. 权限管理
- 所有用户可创建和查看归档项目
- 仅管理员可编辑和删除归档项目
- 非管理员创建的项目不可编辑

## 技术实现

### 后端

#### 数据模型
- `ArchivedProject`: 归档项目主表
- `Attachment`: 附件表（扩展支持归档项目）
- `ProjectStep`: 步骤表（扩展支持归档项目）

#### API路由
- `GET /api/archived-projects`: 获取归档项目列表
- `GET /api/archived-projects/count`: 获取总数
- `POST /api/archived-projects/upload-files`: 上传文件
- `POST /api/archived-projects`: 创建归档项目
- `GET /api/archived-projects/{id}`: 获取项目详情
- `PUT /api/archived-projects/{id}`: 更新项目（仅管理员）
- `DELETE /api/archived-projects/{id}`: 删除项目（仅管理员）
- `GET /api/archived-projects/{id}/attachments`: 获取附件列表

### 前端

#### 页面
- `ArchivedProjects.vue`: 归档项目列表页面
- `ArchivedProjectDetail.vue`: 归档项目详情页面

#### API客户端
- `archivedProject.ts`: 归档项目API封装

## 数据库迁移

由于新增了以下字段和表，需要执行数据库迁移：

### 新增表
- `archivedproject`: 归档项目表

### 修改表
- `attachment`: 新增字段
  - `archived_project_id`: 归档项目ID（可为空）
  - `is_source_code`: 是否为源码文件
  - `is_documentation`: 是否为说明文件
  - `project_id`: 改为可选（支持归档项目）

- `projectstep`: 新增字段
  - `archived_project_id`: 归档项目ID（可为空）
  - `project_id`: 改为可选（支持归档项目）

- `user`: 新增关系
  - `archived_projects`: 归档项目列表

### 迁移步骤

1. 备份数据库
2. 运行应用，SQLModel会自动创建新表和字段（如果使用SQLite）
3. 或者手动执行SQL迁移脚本

## UI设计特点

1. **卡片式布局**: 使用网格布局展示项目卡片，美观直观
2. **渐变效果**: 卡片hover时有渐变和阴影效果
3. **文件分类**: 源码文件和说明文件分开管理
4. **响应式设计**: 支持移动端和桌面端
5. **统一样式**: 与现有项目管理功能保持一致的设计风格

## 代码复用

- 复用了 `ProjectDetail.vue` 的步骤时间线样式
- 复用了文件预览和下载功能
- 复用了项目管理的基础UI组件和样式

## 使用说明

1. 访问"归档项目"菜单
2. 点击"新建归档项目"按钮
3. 填写项目信息
4. 上传源码文件和说明文件
5. 点击"创建归档项目"完成归档

## 注意事项

1. 归档项目创建后，非管理员无法编辑
2. 时间线步骤固定为"已归档"状态，不可修改
3. 文件上传后会自动分类为源码文件或说明文件
4. 删除归档项目会同时删除所有关联的附件和步骤


