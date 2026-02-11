# 故障排除指南

## 登录问题

如果遇到 "Incorrect username or password" 错误，请按以下步骤排查：

### 1. 检查数据库中的用户

```bash
cd fastapi_back
source venv/bin/activate  # Linux/macOS
# 或
venv\Scripts\activate  # Windows

python check_users.py
```

这会显示数据库中的所有用户及其密码验证状态。

### 2. 重置管理员密码

如果管理员用户不存在或密码有问题，运行：

```bash
python reset_admin.py
```

这会：
- 创建管理员用户（如果不存在）
- 重置密码为 `admin123`
- 验证密码是否正确

### 3. 重新初始化数据库

如果以上方法都不行，可以删除数据库文件重新初始化：

```bash
# 删除数据库文件
rm project_manager.db  # Linux/macOS
# 或
del project_manager.db  # Windows

# 重新初始化
PYTHONPATH=. python -m app.init_db
```

### 4. 检查密码哈希函数

如果密码验证一直失败，可能是 bcrypt 版本问题。运行：

```bash
python test_security.py
```

这会测试密码哈希和验证功能。

## 默认账号

- 用户名：`admin`
- 密码：`admin123`

## 常见问题

### Q: 登录时提示 "Incorrect username or password"
A: 
1. 运行 `python check_users.py` 检查用户是否存在
2. 运行 `python reset_admin.py` 重置密码
3. 确认前端发送的用户名和密码正确

### Q: 数据库中没有用户
A: 运行 `PYTHONPATH=. python -m app.init_db` 初始化数据库

### Q: 密码验证失败
A: 可能是 bcrypt 版本问题，运行 `python test_security.py` 检查

