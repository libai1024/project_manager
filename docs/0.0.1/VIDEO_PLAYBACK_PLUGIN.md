# 视频回放插件开发文档

## 功能概述

视频回放插件是一个企业级的视频管理解决方案，允许用户：
1. 上传视频文件
2. 生成带密码保护的观看链接
3. 设置链接有效期和最大观看次数
4. 统计观看数据（观看次数、时长、百分比等）
5. 提供美观的在线观看界面

## 架构设计

### 后端架构

#### 数据模型
- **VideoPlayback**: 视频主表
  - 存储视频基本信息（标题、描述、文件路径、大小等）
  - 关联项目和观看链接
  
- **VideoPlaybackLink**: 观看链接表
  - 存储访问令牌（token）
  - 密码（SHA256哈希）
  - 有效期、最大观看次数
  - 观看统计
  
- **VideoPlaybackStat**: 观看统计表
  - IP地址、用户代理
  - 观看时长、观看百分比
  - 来源页面

#### API端点
- `POST /api/video-playbacks/project/{project_id}/upload` - 上传视频
- `GET /api/video-playbacks/project/{project_id}` - 获取项目视频列表
- `PUT /api/video-playbacks/{video_id}` - 更新视频信息
- `DELETE /api/video-playbacks/{video_id}` - 删除视频
- `POST /api/video-playbacks/{video_id}/links` - 创建观看链接
- `GET /api/video-playbacks/{video_id}/links` - 获取链接列表
- `DELETE /api/video-playbacks/links/{link_id}` - 删除链接
- `GET /api/video-playbacks/{video_id}/statistics` - 获取统计信息
- `POST /api/video-playbacks/watch/{token}/verify` - 验证密码
- `GET /api/video-playbacks/watch/{token}/video` - 获取视频文件
- `POST /api/video-playbacks/watch/{token}/record` - 记录观看统计

### 前端架构

#### 组件结构
- **VideoPlaybackPlugin.vue**: 主插件组件
  - 视频列表展示
  - 上传视频
  - 链接管理
  - 统计查看
  
- **VideoWatch.vue**: 观看页面
  - 密码验证
  - 视频播放
  - 观看统计记录

#### 路由配置
- `/video/watch/:token` - 视频观看页面（无需登录）

## 安全特性

1. **密码保护**: 使用SHA256哈希存储密码
2. **唯一令牌**: 每个链接使用唯一的token
3. **有效期控制**: 支持设置链接过期时间
4. **观看次数限制**: 支持设置最大观看次数
5. **权限验证**: 只有项目所有者和管理员可以管理视频

## 统计功能

- 总观看次数
- 平均观看时长
- 总观看时长
- 平均观看百分比
- IP地址和用户代理记录
- 观看时间记录

## 使用说明

### 1. 启用插件
在项目创建时或设置界面中启用"视频回放"插件

### 2. 上传视频
1. 进入项目详情页
2. 在视频回放插件中点击"上传视频"
3. 填写标题和描述
4. 选择视频文件（支持MP4、AVI、MOV等格式，最大2GB）
5. 点击上传

### 3. 创建观看链接
1. 在视频列表中点击"管理链接"
2. 点击"创建新链接"
3. 设置访问密码
4. 可选：设置有效期和最大观看次数
5. 创建链接

### 4. 分享链接
1. 复制生成的观看链接
2. 分享给客户
3. 客户访问链接后输入密码即可观看

### 5. 查看统计
1. 在视频列表中点击"统计"
2. 查看观看数据

## 技术实现

### 后端技术栈
- FastAPI
- SQLModel
- SHA256密码哈希
- secrets模块生成安全token

### 前端技术栈
- Vue 3 Composition API
- Element Plus
- Axios
- HTML5 Video API

## 待完成工作

1. ✅ 后端数据模型
2. ✅ 后端API实现
3. ✅ 前端插件组件
4. ✅ 观看页面
5. ⚠️ 更新usePluginSettings支持video-playback（部分完成）
6. ⚠️ 在ProjectDetail中集成插件
7. ⚠️ 在Settings中添加插件管理
8. ⚠️ 在Projects中添加插件选择

## 注意事项

1. 视频文件存储在 `uploads/videos/` 目录
2. 需要确保目录有写入权限
3. 大文件上传可能需要调整nginx配置
4. 建议使用CDN存储视频文件以提高性能
5. 观看统计每10秒记录一次，避免频繁请求

## 扩展建议

1. 视频转码和缩略图生成
2. 视频加密和DRM保护
3. 播放速度控制
4. 字幕支持
5. 多分辨率支持
6. 观看进度保存
7. 评论和反馈功能

