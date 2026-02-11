# 后端认证架构文档

## 概述

本文档描述了后端项目中 JWT token 认证的统一管理架构。所有需要认证的 API 端点都使用统一的认证依赖，确保 token 解析逻辑一致。

## 架构设计

### 1. 核心模块

#### `app/core/dependencies.py` - 认证依赖模块
**职责：**
- 提供统一的 token 提取函数
- 提供统一的用户认证函数
- 作为所有需要认证的端点的统一入口

**关键函数：**

1. **`extract_token_from_request(request: Request) -> Optional[str]`**
   - 统一的 token 提取函数
   - 支持多种 header 格式：
     - `Authorization: Bearer <token>` (标准格式)
     - `authorization: Bearer <token>` (小写格式)
     - `X-Authorization: Bearer <token>` (备用格式)
   - 自动处理大小写不敏感
   - 返回清理后的 token 字符串

2. **`get_current_user(...) -> User`**
   - 统一的用户认证入口
   - 所有需要认证的端点都使用此函数
   - 流程：
     1. 尝试从 `OAuth2PasswordBearer` 获取 token
     2. 如果失败，使用 `extract_token_from_request` 直接提取
     3. 验证 token 格式和有效性
     4. 解析 token payload 获取用户名
     5. 从数据库查询用户信息
     6. 返回用户对象

3. **`get_current_active_user(...) -> User`**
   - 获取当前活跃用户（包装 `get_current_user`）
   - 用于需要认证但不需要特殊权限的端点

4. **`get_current_admin_user(...) -> User`**
   - 获取当前管理员用户
   - 检查用户角色是否为 `admin`
   - 用于需要管理员权限的端点

### 2. Token 提取流程

```
请求到达
    ↓
OAuth2PasswordBearer 尝试提取
    ↓ (失败)
extract_token_from_request
    ↓
检查多种 header 格式
    ↓
提取 Bearer token
    ↓
验证 token 格式
    ↓
decode_access_token
    ↓
解析 payload 获取用户名
    ↓
从数据库查询用户
    ↓
返回 User 对象
```

### 3. 使用方式

#### 在 API 端点中使用

```python
from app.core.dependencies import get_current_active_user, get_current_admin_user
from app.models.user import User

# 需要认证的端点
@router.get("/items")
async def list_items(
    current_user: User = Depends(get_current_active_user)
):
    # current_user 已通过认证
    return {"items": []}

# 需要管理员权限的端点
@router.delete("/items/{id}")
async def delete_item(
    id: int,
    current_user: User = Depends(get_current_admin_user)
):
    # current_user 是管理员
    return {"message": "deleted"}
```

### 4. 支持的 Header 格式

后端支持以下 header 格式（不区分大小写）：

1. **标准格式**（推荐）：
   ```
   Authorization: Bearer <token>
   ```

2. **小写格式**：
   ```
   authorization: Bearer <token>
   ```

3. **备用格式**：
   ```
   X-Authorization: Bearer <token>
   ```

### 5. 错误处理

认证失败时，会抛出 `HTTPException`，状态码为 `401 Unauthorized`：

```python
HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Not authenticated",
    headers={"WWW-Authenticate": "Bearer"},
)
```

### 6. 日志记录

认证过程会记录详细的日志：

- **DEBUG 级别**：token 提取成功、用户认证成功
- **WARNING 级别**：token 缺失、格式错误、用户不存在
- **ERROR 级别**：意外的认证错误

### 7. 安全性考虑

1. **Token 验证**：
   - 验证 token 格式（必须是 Bearer 格式）
   - 验证 token 签名（JWT 签名验证）
   - 验证 token 过期时间

2. **用户验证**：
   - 验证用户是否存在
   - 验证用户是否活跃（如果需要）

3. **权限控制**：
   - 基于角色的访问控制（RBAC）
   - 管理员权限检查

## 统一性保证

### 所有 API 端点使用统一的认证

所有需要认证的端点都使用以下依赖之一：

- `get_current_active_user` - 需要认证
- `get_current_admin_user` - 需要管理员权限

这确保了：
1. 所有端点的认证逻辑一致
2. Token 提取方式统一
3. 错误处理统一
4. 日志记录统一

### 文件清单

使用统一认证的 API 文件：
- `app/api/auth.py`
- `app/api/projects.py`
- `app/api/archived_projects.py`
- `app/api/attachments.py`
- `app/api/attachment_folders.py`
- `app/api/todos.py`
- `app/api/project_logs.py`
- `app/api/step_templates.py`
- `app/api/project_parts.py`
- `app/api/github_commits.py`
- `app/api/video_playbacks.py`
- `app/api/dashboard.py`
- `app/api/users.py`
- `app/api/platforms.py`

## 最佳实践

1. **始终使用依赖注入**：
   ```python
   # ✅ 正确
   current_user: User = Depends(get_current_active_user)
   
   # ❌ 错误 - 不要手动提取 token
   token = request.headers.get("Authorization")
   ```

2. **根据权限需求选择依赖**：
   ```python
   # 需要认证
   get_current_active_user
   
   # 需要管理员权限
   get_current_admin_user
   ```

3. **不要绕过认证**：
   - 所有需要认证的端点都应该使用 `Depends(get_current_active_user)`
   - 不要手动提取和验证 token

## 故障排查

### 问题：401 Unauthorized

可能原因：
1. Token 未发送（检查前端请求头）
2. Token 格式错误（必须是 `Bearer <token>`）
3. Token 已过期
4. Token 签名无效
5. 用户不存在

检查步骤：
1. 查看后端日志，确认 token 是否被提取
2. 检查前端请求头格式
3. 验证 token 是否有效（使用 JWT 工具）

### 问题：Token 提取失败

可能原因：
1. Header 名称不匹配
2. Header 格式错误

解决方案：
- 确保使用 `Authorization: Bearer <token>` 格式
- 检查 header 名称大小写

## 未来改进

1. **Token 刷新机制**：
   - 实现 refresh token
   - 自动刷新过期的 access token

2. **更细粒度的权限控制**：
   - 基于权限的访问控制（PBAC）
   - 资源级别的权限控制

3. **Token 黑名单**：
   - 支持 token 撤销
   - 登出时使 token 失效


