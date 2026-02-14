# API Test Generator Skill

自动为 FastAPI 后端模块生成完整的 API 测试套件。

## 触发条件

用户请求以下操作时自动激活：
- "为新模块生成测试"
- "创建 API 测试"
- "添加模块测试"
- "/api-test"
- "测试 [模块名] 模块"

## 功能

1. 分析 API 路由文件，提取所有端点
2. 分析数据模型，识别字段和验证规则
3. 生成完整的测试文件
4. 创建测试目录结构

## 测试模板规范

### 目录结构

```
tests/
├── base_test.py          # 测试基类（已存在）
├── {nn}_{module_name}/   # 新模块测试目录
│   ├── test.py           # 测试脚本
│   └── reports/          # 测试报告目录（自动创建）
```

### 命名规范

- 目录名: `{序号}_{模块名}` (如 `18_notifications`)
- 序号递增，从 18 开始（现有 17 个模块）

### 测试用例类型

每个模块必须包含以下测试类型：

1. **基础 CRUD 测试**
   - 获取列表 (GET /)
   - 创建 (POST /)
   - 获取详情 (GET /{id})
   - 更新 (PUT /{id})
   - 删除 (DELETE /{id})

2. **边界测试**
   - 获取不存在的资源 (404)
   - 删除不存在的资源 (404)
   - 更新不存在的资源 (404)

3. **认证测试**
   - 无 Token 访问 (401)

4. **验证测试**
   - 空名称/描述字段 (422)
   - 超长字段测试

5. **数据结构验证**
   - 验证响应包含必要字段

6. **Docker 部署验证**
   - 调用 /api/dashboard/stats 或 /health

### 测试文件模板

```python
#!/usr/bin/env python3
"""
API {序号} - {模块中文名}模块测试
测试{模块中文名}相关功能
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from base_test import TestRunner

def test_{module_name}():
    """{模块中文名}模块测试"""
    runner = TestRunner("{模块中文名}", os.path.dirname(os.path.abspath(__file__)))

    print(f"\\n{'='*50}")
    print(" API {序号} - {模块中文名}")
    print(f"{'='*50}\\n")

    if not runner.login():
        print("登录失败，无法继续测试")
        return False

    # 获取测试项目（如需要）
    resp = runner.request("GET", "/api/projects/")
    projects = runner.extract_data(resp)
    project_id = projects[0]["id"] if projects else 1

    # 1. 获取列表
    resp = runner.request("GET", "/api/{api_path}/")
    if resp.status_code == 200:
        items = runner.extract_data(resp)
        runner.log("获取{实体}列表", True, f"数量: {len(items) if items else 0}")
    else:
        runner.log("获取{实体}列表", False, f"状态码: {resp.status_code}")

    # 2. 创建
    import time
    item_name = f"测试{实体}_{int(time.time())}"
    resp = runner.request("POST", "/api/{api_path}/", data={
        "{name_field}": item_name,
        # 其他必填字段...
    })
    if resp.status_code == 200:
        data = runner.extract_data(resp)
        runner.real_data["test_item_id"] = data.get("id") if data else None
        runner.log("创建{实体}", True, f"ID: {data.get('id') if data else 'N/A'}")
    else:
        runner.log("创建{实体}", False, f"状态码: {resp.status_code}, {resp.text[:100] if hasattr(resp, 'text') else ''}")

    item_id = runner.real_data.get("test_item_id")

    # 3. 获取详情
    if item_id:
        resp = runner.request("GET", f"/api/{api_path}/{item_id}")
        runner.log("获取{实体}详情", resp.status_code == 200, f"状态码: {resp.status_code}")
    else:
        runner.skip("获取{实体}详情", "无测试ID")

    # 4. 更新
    if item_id:
        resp = runner.request("PUT", f"/api/{api_path}/{item_id}", data={
            "{name_field}": f"更新_{item_name}"
        })
        runner.log("更新{实体}", resp.status_code == 200, f"状态码: {resp.status_code}")
    else:
        runner.skip("更新{实体}", "无测试ID")

    # 5. 删除
    if item_id:
        resp = runner.request("DELETE", f"/api/{api_path}/{item_id}")
        runner.log("删除{实体}", resp.status_code == 200, f"状态码: {resp.status_code}")
    else:
        runner.skip("删除{实体}", "无测试ID")

    # 6. 获取不存在资源
    resp = runner.request("GET", "/api/{api_path}/99999")
    runner.log("获取不存在{实体}", resp.status_code == 404, f"状态码: {resp.status_code}")

    # 7. 删除不存在资源
    resp = runner.request("DELETE", "/api/{api_path}/99999")
    runner.log("删除不存在{实体}", resp.status_code == 404, f"状态码: {resp.status_code}")

    # 8. 无Token访问
    old_token = runner.token
    runner.token = None
    resp = runner.request("GET", "/api/{api_path}/")
    runner.token = old_token
    runner.log("无Token访问", resp.status_code == 401, f"状态码: {resp.status_code}")

    # 9. 空名称验证
    resp = runner.request("POST", "/api/{api_path}/", data={"{name_field}": ""})
    runner.log("创建空名称{实体}", resp.status_code == 422, f"状态码: {resp.status_code}")

    # 10. 数据结构验证
    resp = runner.request("GET", "/api/{api_path}/")
    if resp.status_code == 200:
        items = runner.extract_data(resp)
        if items and len(items) > 0:
            required = ["id", "{name_field}"]  # 必要字段列表
            has_all = all(k in items[0] for k in required)
            runner.log("{实体}数据结构验证", has_all, "包含必要字段" if has_all else "缺少必要字段")
        else:
            runner.log("{实体}数据结构验证", True, "无数据")
    else:
        runner.log("{实体}数据结构验证", False, f"状态码: {resp.status_code}")

    # 11. Docker部署验证
    resp = runner.request("GET", "/api/dashboard/stats")
    runner.log("Docker部署验证", resp.status_code == 200, f"后端服务正常，状态码: {resp.status_code}")

    report_file = runner.save_report()
    print(f"\\n报告已保存: {report_file}")
    return runner.summary()

if __name__ == "__main__":
    success = test_{module_name}()
    sys.exit(0 if success else 1)
```

## 执行流程

当用户请求生成测试时：

### 步骤 1: 识别 API 模块

1. 读取 `fastapi_back/app/api/` 目录下的路由文件
2. 提取路由前缀和端点信息
3. 确定模块序号（当前最大序号 + 1）

### 步骤 2: 分析数据模型

1. 读取对应的 model 文件
2. 识别字段名称、类型、验证规则
3. 确定必填字段和可选字段

### 步骤 3: 生成测试文件

1. 创建测试目录
2. 生成 test.py 文件
3. 根据端点类型生成对应测试用例

### 步骤 4: 验证测试

1. 运行生成的测试
2. 修复任何问题
3. 确保测试通过

## 特殊端点处理

### 文件上传

```python
# 文件上传测试
with open("test_file.txt", "wb") as f:
    f.write(b"test content")
with open("test_file.txt", "rb") as f:
    resp = runner.request("POST", "/api/{path}/upload",
        files={"file": ("test.txt", f, "text/plain")},
        data={"project_id": project_id}
    )
```

### 关联资源

```python
# 需要先创建关联资源
resp = runner.request("POST", "/api/projects/", data={"title": "测试项目"})
project_id = runner.extract_data(resp)["id"]

# 再创建目标资源
resp = runner.request("POST", "/api/{path}/", data={
    "name": "test",
    "project_id": project_id
})
```

### 特殊查询参数

```python
# 分页测试
resp = runner.request("GET", "/api/{path}/", params={"skip": 0, "limit": 10})

# 过滤测试
resp = runner.request("GET", "/api/{path}/", params={"status": "active"})
```

## 常见状态码期望

| 操作 | 期望状态码 |
|------|-----------|
| 成功创建 | 200 |
| 成功获取 | 200 |
| 成功更新 | 200 |
| 成功删除 | 200 |
| 资源不存在 | 404 |
| 未认证 | 401 |
| 验证失败 | 422 |
| 重复资源 | 400 |

## 运行所有测试

```bash
# 激活虚拟环境并运行所有测试
source tests/venv/bin/activate && for dir in tests/*/; do
  if [ -f "${dir}test.py" ]; then
    python "${dir}test.py"
  fi
done
```

## 示例用法

```
用户: 为 notifications 模块生成测试
Claude: [分析 API 路由] [生成测试文件] [运行测试]

用户: 创建一个新的 API 模块 webhooks，并生成测试
Claude: [创建模型] [创建路由] [创建仓储] [生成测试]
```
