#!/usr/bin/env python3
"""
API测试脚本
自动测试所有后端API并生成测试报告
"""
import requests
import json
from datetime import datetime
from typing import Dict, Any, List, Tuple, Optional

# 配置
BASE_URL = "http://localhost:8000"
TIMEOUT = 30

class TestResult:
    def __init__(self):
        self.passed: List[str] = []
        self.failed: List[Tuple[str, str]] = []
        self.skipped: List[Tuple[str, str]] = []

    def add_pass(self, test_name: str):
        self.passed.append(test_name)

    def add_fail(self, test_name: str, error: str):
        self.failed.append((test_name, error))

    def add_skip(self, test_name: str, reason: str):
        self.skipped.append((test_name, reason))

    def summary(self) -> str:
        total = len(self.passed) + len(self.failed) + len(self.skipped)
        pass_rate = len(self.passed) / total * 100 if total > 0 else 0
        return f"""
================================================================================
                              API测试报告
================================================================================
测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
总计: {total} 个测试
通过: {len(self.passed)} 个
失败: {len(self.failed)} 个
跳过: {len(self.skipped)} 个

通过率: {pass_rate:.1f}%
================================================================================
"""

results = TestResult()
token = None
admin_token = None
created_resources = {
    "platform_id": None,
    "project_id": None,
    "tag_id": None,
    "todo_id": None,
    "step_id": None,
    "folder_id": None,
    "attachment_id": None,
    "template_id": None
}


def api_request(method: str, endpoint: str, data: Dict = None, auth_token: str = None) -> Tuple[int, Optional[Dict]]:
    """发送API请求"""
    url = f"{BASE_URL}{endpoint}"
    headers = {}
    if auth_token:
        headers["Authorization"] = f"Bearer {auth_token}"

    try:
        if method == "GET":
            resp = requests.get(url, headers=headers, timeout=TIMEOUT)
        elif method == "POST":
            if data and "form_data" in data:
                # Form data request (for OAuth2)
                headers.pop("Content-Type", None)
                resp = requests.post(url, headers=headers, data=data["form_data"], timeout=TIMEOUT)
            else:
                headers["Content-Type"] = "application/json"
                resp = requests.post(url, headers=headers, json=data, timeout=TIMEOUT)
        elif method == "PUT":
            headers["Content-Type"] = "application/json"
            resp = requests.put(url, headers=headers, json=data, timeout=TIMEOUT)
        elif method == "DELETE":
            resp = requests.delete(url, headers=headers, timeout=TIMEOUT)
        else:
            return 400, {"error": f"Unknown method: {method}"}

        try:
            return resp.status_code, resp.json()
        except:
            return resp.status_code, {"raw": resp.text}
    except Exception as e:
        return 500, {"error": str(e)}


def test_api(name: str, method: str, endpoint: str, data: Dict = None,
             auth_token: str = None, expected_status: int = 200,
             check_field: str = None) -> Optional[Dict]:
    """测试单个API并记录结果"""
    status, response = api_request(method, endpoint, data, auth_token)

    if response is None:
        response = {}

    if status != expected_status:
        error_msg = f"状态码 {status} != 期望 {expected_status}, 响应: {response}"
        results.add_fail(name, error_msg)
        print(f"[FAIL] {name}: {error_msg[:100]}")
        return response

    if check_field and check_field not in response:
        error_msg = f"响应中缺少字段 '{check_field}': {response}"
        results.add_fail(name, error_msg)
        print(f"[FAIL] {name}: {error_msg[:100]}")
        return response

    results.add_pass(name)
    print(f"[PASS] {name}")
    return response


# ==================== 测试开始 ====================

print("\n" + "="*60)
print("开始API测试...")
print("="*60 + "\n")

# 1. 健康检查
print("\n--- 健康检查 ---")
test_api("GET /", "GET", "/")
test_api("GET /health", "GET", "/health")

# 2. 用户登录 (使用form data, OAuth2格式)
print("\n--- 用户认证 ---")
login_resp = test_api("POST /api/auth/login (admin)", "POST", "/api/auth/login", {
    "form_data": {"username": "admin", "password": "admin123"}
}, check_field="access_token")

if login_resp and "access_token" in login_resp:
    admin_token = login_resp["access_token"]
    token = admin_token
    print(f"    -> Admin token obtained: {admin_token[:20]}...")
else:
    print("    -> Warning: Could not get admin token, tests may fail")

# 3. 获取当前用户
print("\n--- 用户信息 ---")
test_api("GET /api/auth/me", "GET", "/api/auth/me", auth_token=token, check_field="id")

# 4. 平台管理
print("\n--- 平台管理 ---")
test_api("GET /api/platforms", "GET", "/api/platforms", auth_token=token, check_field="code")

platform_resp = test_api("POST /api/platforms", "POST", "/api/platforms", {
    "name": f"测试平台_{datetime.now().strftime('%Y%m%d%H%M%S')}",
    "url": "https://test.com"
}, auth_token=token, check_field="code")

if platform_resp and "data" in platform_resp and isinstance(platform_resp["data"], dict) and "id" in platform_resp["data"]:
    created_resources["platform_id"] = platform_resp["data"]["id"]

# 5. 标签管理
print("\n--- 标签管理 ---")
test_api("GET /api/tags", "GET", "/api/tags", auth_token=token, check_field="code")

tag_resp = test_api("POST /api/tags", "POST", "/api/tags", {
    "name": f"测试标签_{datetime.now().strftime('%Y%m%d%H%M%S')}",
    "color": "#409eff"
}, auth_token=token, check_field="code")

if tag_resp and "data" in tag_resp and isinstance(tag_resp["data"], dict) and "id" in tag_resp["data"]:
    created_resources["tag_id"] = tag_resp["data"]["id"]

# 6. 项目管理
print("\n--- 项目管理 ---")
test_api("GET /api/projects", "GET", "/api/projects", auth_token=token, check_field="code")

if created_resources["platform_id"]:
    project_resp = test_api("POST /api/projects", "POST", "/api/projects", {
        "title": f"测试项目_{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "platform_id": created_resources["platform_id"],
        "price": 100.0,
        "tag_ids": [created_resources["tag_id"]] if created_resources["tag_id"] else []
    }, auth_token=token, check_field="code")

    if project_resp and "data" in project_resp and isinstance(project_resp["data"], dict) and "id" in project_resp["data"]:
        created_resources["project_id"] = project_resp["data"]["id"]

if created_resources["project_id"]:
    pid = created_resources["project_id"]
    test_api("GET /api/projects/{id}", "GET", f"/api/projects/{pid}", auth_token=token, check_field="code")
    test_api("PUT /api/projects/{id}", "PUT", f"/api/projects/{pid}", {
        "title": "更新后的项目标题"
    }, auth_token=token, check_field="code")

# 7. 项目步骤
print("\n--- 项目步骤 ---")
if created_resources["project_id"]:
    pid = created_resources["project_id"]
    step_resp = test_api("POST /api/projects/{id}/steps", "POST", f"/api/projects/{pid}/steps", {
        "name": "测试步骤",
        "order_index": 100
    }, auth_token=token, check_field="code")

    if step_resp and "data" in step_resp and isinstance(step_resp["data"], dict) and "id" in step_resp["data"]:
        created_resources["step_id"] = step_resp["data"]["id"]

if created_resources["step_id"]:
    sid = created_resources["step_id"]
    test_api("PUT /api/projects/steps/{id}", "PUT", f"/api/projects/steps/{sid}", {
        "status": "进行中"
    }, auth_token=token, check_field="code")
    test_api("POST /api/projects/steps/{id}/toggle-todo", "POST",
             f"/api/projects/steps/{sid}/toggle-todo", auth_token=token, check_field="code")

# 8. Dashboard
print("\n--- Dashboard ---")
test_api("GET /api/dashboard/stats", "GET", "/api/dashboard/stats", auth_token=token, check_field="code")

# 9. 用户管理
print("\n--- 用户管理 ---")
test_api("GET /api/users", "GET", "/api/users", auth_token=admin_token, check_field="code")

# 10. Todo管理
print("\n--- Todo管理 ---")
test_api("GET /api/todos", "GET", "/api/todos", auth_token=token, check_field="code")

todo_resp = test_api("POST /api/todos", "POST", "/api/todos", {
    "title": f"测试待办_{datetime.now().strftime('%Y%m%d%H%M%S')}"
}, auth_token=token, check_field="code")

if todo_resp and "data" in todo_resp and isinstance(todo_resp["data"], dict) and "id" in todo_resp["data"]:
    created_resources["todo_id"] = todo_resp["data"]["id"]

if created_resources["todo_id"]:
    tid = created_resources["todo_id"]
    test_api("PUT /api/todos/{id}", "PUT", f"/api/todos/{tid}", {
        "title": "更新后的待办"
    }, auth_token=token, check_field="code")

# 11. 步骤模板
print("\n--- 步骤模板 ---")
test_api("GET /api/step-templates", "GET", "/api/step-templates", auth_token=token, check_field="code")

template_resp = test_api("POST /api/step-templates", "POST", "/api/step-templates", {
    "name": f"测试模板_{datetime.now().strftime('%Y%m%d%H%M%S')}",
    "description": "这是一个测试模板",
    "steps": ["步骤1", "步骤2", "步骤3"]
}, auth_token=token, check_field="code")

if template_resp and "data" in template_resp and isinstance(template_resp["data"], dict) and "id" in template_resp["data"]:
    created_resources["template_id"] = template_resp["data"]["id"]

# 12. 附件文件夹
print("\n--- 附件文件夹 ---")
if created_resources["project_id"]:
    test_api("GET /api/attachment-folders", "GET", "/api/attachment-folders",
             auth_token=token, check_field="code")

# 13. 项目日志
print("\n--- 项目日志 ---")
if created_resources["project_id"]:
    test_api("GET /api/project-logs/project/{id}", "GET",
             f"/api/project-logs/project/{created_resources['project_id']}",
             auth_token=token, check_field="code")

# 14. 系统设置
print("\n--- 系统设置 ---")
test_api("GET /api/system-settings", "GET", "/api/system-settings", auth_token=token, check_field="code")


# ==================== 清理测试数据 ====================
print("\n--- 清理测试数据 ---")

if created_resources["todo_id"]:
    test_api("DELETE /api/todos/{id}", "DELETE",
             f"/api/todos/{created_resources['todo_id']}", auth_token=token, check_field="code")

if created_resources["project_id"]:
    test_api("DELETE /api/projects/{id}", "DELETE",
             f"/api/projects/{created_resources['project_id']}", auth_token=token, check_field="code")

if created_resources["tag_id"]:
    test_api("DELETE /api/tags/{id}", "DELETE",
             f"/api/tags/{created_resources['tag_id']}", auth_token=token, check_field="code")

if created_resources["platform_id"]:
    test_api("DELETE /api/platforms/{id}", "DELETE",
             f"/api/platforms/{created_resources['platform_id']}", auth_token=token, check_field="code")

if created_resources["template_id"]:
    test_api("DELETE /api/step-templates/{id}", "DELETE",
             f"/api/step-templates/{created_resources['template_id']}", auth_token=token, check_field="code")


# ==================== 输出测试报告 ====================
print(results.summary())

# 输出失败详情
if results.failed:
    print("\n失败详情:")
    print("-" * 60)
    for name, error in results.failed:
        print(f"\n[FAIL] {name}")
        print(f"   错误: {error[:200]}")

print("\n" + "="*60)
print("测试完成")
print("="*60)
