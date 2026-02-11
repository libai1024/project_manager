# 数据库迁移指南

本文档说明如何执行数据库迁移脚本，包括删除归档项目功能和添加企业级身份认证系统。

## 前置要求

1. Python 3.8+
2. 已安装项目依赖（requirements.txt）
3. 已激活Python虚拟环境

## 迁移步骤

### 1. 激活虚拟环境

**Linux/Mac:**
```bash
cd fastapi_back
source venv/bin/activate
```

**Windows:**
```bash
cd fastapi_back
venv\Scripts\activate
```

### 2. 备份数据库（重要！）

在执行任何迁移之前，请先备份数据库：

```bash
# 备份数据库文件
cp project_manager.db project_manager.db.backup
```

### 3. 删除归档项目功能

执行迁移脚本删除归档项目相关的表和字段：

```bash
python migrate_remove_archived_projects.py --confirm
```

**此脚本将：**
- 删除 `archivedproject` 表
- 从 `attachment` 表中删除 `archived_project_id` 列
- 清理所有归档项目相关的数据

**注意：** 此操作不可逆，请确保已备份数据库。

### 4. 添加企业级身份认证系统

执行迁移脚本添加企业级认证系统相关表：

```bash
python migrate_enterprise_auth.py --confirm
```

**此脚本将：**
- 创建 `refreshtoken` 表（刷新令牌）
- 创建 `tokenblacklist` 表（Token黑名单）
- 创建 `loginlog` 表（登录日志）
- 更新 `user` 表，添加企业级认证字段：
  - `is_active` - 账户是否激活
  - `is_locked` - 账户是否锁定
  - `locked_until` - 锁定到期时间
  - `failed_login_attempts` - 失败登录次数
  - `last_login_at` - 最后登录时间
  - `password_changed_at` - 密码最后修改时间
  - `must_change_password` - 是否必须修改密码

## 企业级认证功能

迁移完成后，系统将支持以下企业级认证功能：

### 1. Refresh Token 机制
- 短期访问令牌（默认15分钟）
- 长期刷新令牌（默认30天）
- 支持多设备登录管理

### 2. Token 撤销机制
- Token 黑名单支持
- 支持撤销所有设备的令牌
- 自动清理过期的黑名单条目

### 3. 账户安全
- 账户锁定机制（失败登录次数限制）
- 账户激活/禁用
- 密码策略验证
- 密码过期提醒

### 4. 登录审计
- 完整的登录日志记录
- IP地址和设备信息追踪
- 失败登录原因记录

### 5. 安全配置

在 `app/core/config.py` 中可以配置：

```python
# JWT配置
ACCESS_TOKEN_EXPIRE_MINUTES = 15  # 访问令牌过期时间（分钟）
REFRESH_TOKEN_EXPIRE_DAYS = 30    # 刷新令牌过期时间（天）

# 安全配置
MAX_LOGIN_ATTEMPTS = 5            # 最大登录尝试次数
LOCKOUT_DURATION_MINUTES = 30     # 账户锁定时长（分钟）
PASSWORD_MIN_LENGTH = 8            # 密码最小长度
PASSWORD_REQUIRE_UPPERCASE = True # 要求大写字母
PASSWORD_REQUIRE_LOWERCASE = True # 要求小写字母
PASSWORD_REQUIRE_NUMBER = True    # 要求数字
PASSWORD_REQUIRE_SPECIAL = False  # 要求特殊字符
PASSWORD_EXPIRE_DAYS = None       # 密码过期天数（None表示不过期）
```

## API 变更

### 登录接口变更

**之前：**
```json
POST /api/auth/login
Response:
{
  "access_token": "...",
  "token_type": "bearer"
}
```

**现在：**
```json
POST /api/auth/login
Response:
{
  "access_token": "...",
  "refresh_token": "...",
  "token_type": "bearer",
  "expires_in": 900
}
```

### 新增接口

1. **刷新令牌**
   ```
   POST /api/auth/refresh
   Body: { "refresh_token": "..." }
   ```

2. **登出**
   ```
   POST /api/auth/logout
   Body: { "refresh_token": "..." }  # 可选
   ```

3. **登出所有设备**
   ```
   POST /api/auth/logout-all
   ```

4. **获取登录日志**
   ```
   GET /api/auth/login-logs?limit=100
   ```

## 故障排除

### 问题：迁移脚本执行失败

**解决方案：**
1. 确保已激活虚拟环境
2. 检查数据库文件权限
3. 查看错误日志，确认具体问题
4. 如果表已存在，可能需要手动删除后重新执行

### 问题：用户无法登录

**解决方案：**
1. 检查用户账户是否被锁定（`is_locked` 字段）
2. 检查用户账户是否激活（`is_active` 字段）
3. 查看登录日志了解失败原因

### 问题：Token 验证失败

**解决方案：**
1. 检查 Token 是否在黑名单中
2. 确认 Token 未过期
3. 验证 SECRET_KEY 配置正确

## 回滚

如果需要回滚迁移：

1. **恢复数据库备份：**
   ```bash
   cp project_manager.db.backup project_manager.db
   ```

2. **或者手动删除新表：**
   ```sql
   DROP TABLE IF EXISTS refreshtoken;
   DROP TABLE IF EXISTS tokenblacklist;
   DROP TABLE IF EXISTS loginlog;
   ```

## 注意事项

1. **生产环境：** 请在生产环境执行迁移前进行充分测试
2. **数据备份：** 始终在执行迁移前备份数据库
3. **停机时间：** 迁移可能需要短暂停机，请规划好维护窗口
4. **配置更新：** 迁移后需要更新前端代码以支持新的认证流程

## 支持

如有问题，请查看：
- 项目文档
- 代码注释
- 日志文件

