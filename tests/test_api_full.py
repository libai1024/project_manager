#!/usr/bin/env python3
"""
外包项目管理系统 - API 全面测试脚本 V2
- 覆盖所有API端点
- 每个API至少5个测试用例
- 包含文件上传下载完整测试
- 总测试用例 150+
"""
import requests
import json
import time
import os
import io
from datetime import datetime, date
from typing import Optional, Dict, Any, List

# 配置
BASE_URL = "http://localhost:8000"
REPORT_FILE = os.path.join(os.path.dirname(__file__), "api_test_report.md")


def extract_data(resp) -> Any:
    """从响应中提取data字段（处理嵌套响应结构）"""
    try:
        json_data = resp.json()
        if isinstance(json_data, dict) and "data" in json_data:
            return json_data["data"]
        return json_data
    except:
        return resp.json()

# 测试结果存储
test_results = {
    "total": 0,
    "passed": 0,
    "failed": 0,
    "skipped": 0,
    "modules": {}
}

# 认证信息
auth_tokens = {"admin": None, "user": None}

# 真实数据 ID 存储
real_data = {
    "users": {"admin": 1, "user": 2},
    "platforms": [],
    "projects": [],
    "attachments": [],
    "tags": [],
    "folders": [],
    "todos": [],
    "historical_projects": []
}

# 测试创建的数据（用于清理）
created_data = {
    "platforms": [],
    "projects": [],
    "attachments": [],
    "tags": [],
    "todos": [],
    "historical_projects": [],
    "folders": []
}


def log_test(module: str, test_name: str, result: str, detail: str = ""):
    """记录测试结果"""
    test_results["total"] += 1
    if module not in test_results["modules"]:
        test_results["modules"][module] = {"total": 0, "passed": 0, "failed": 0, "skipped": 0, "tests": []}

    test_results["modules"][module]["total"] += 1
    test_results["modules"][module]["tests"].append({
        "name": test_name,
        "result": result,
        "detail": detail,
        "time": datetime.now().strftime("%H:%M:%S")
    })

    if result == "PASS":
        test_results["passed"] += 1
        test_results["modules"][module]["passed"] += 1
    elif result == "FAIL":
        test_results["failed"] += 1
        test_results["modules"][module]["failed"] += 1
    else:
        test_results["skipped"] += 1
        test_results["modules"][module]["skipped"] += 1

    status = "✅" if result == "PASS" else "❌" if result == "FAIL" else "⏭️"
    print(f"{status} [{module}] {test_name}")
    if detail:
        print(f"   └─ {detail[:100]}")


def make_request(method: str, endpoint: str, token: Optional[str] = None,
                 data: Optional[Dict] = None, files: Optional[Dict] = None,
                 params: Optional[Dict] = None, form_data: bool = False,
                 raw_response: bool = False) -> requests.Response:
    """发送HTTP请求"""
    url = f"{BASE_URL}{endpoint}"
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    try:
        if method == "GET":
            resp = requests.get(url, headers=headers, params=params, timeout=60)
        elif method == "POST":
            if files:
                resp = requests.post(url, headers=headers, data=data, files=files, timeout=120)
            elif form_data:
                resp = requests.post(url, headers=headers, data=data, timeout=30)
            else:
                resp = requests.post(url, headers=headers, json=data, timeout=30)
        elif method == "PUT":
            resp = requests.put(url, headers=headers, json=data, timeout=30)
        elif method == "DELETE":
            resp = requests.delete(url, headers=headers, timeout=30)
        else:
            resp = None
        return resp
    except Exception as e:
        class FakeResponse:
            status_code = 0
            text = str(e)
            content = b""
            headers = {}
            def json(self): return {"error": str(e)}
        return FakeResponse()


def update_report():
    """更新测试报告"""
    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        f.write("# API 全面测试报告\n\n")
        f.write(f"## 测试环境\n")
        f.write(f"- 后端地址: {BASE_URL}\n")
        f.write(f"- 测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

        f.write("## 测试统计\n")
        f.write(f"| 指标 | 数量 |\n")
        f.write(f"|------|------|\n")
        f.write(f"| 总用例 | {test_results['total']} |\n")
        f.write(f"| 通过 | {test_results['passed']} |\n")
        f.write(f"| 失败 | {test_results['failed']} |\n")
        f.write(f"| 跳过 | {test_results['skipped']} |\n")
        rate = test_results['passed']/max(test_results['total'],1)*100
        f.write(f"| 通过率 | {rate:.1f}% |\n\n")

        f.write("## 模块统计\n")
        f.write("| 模块 | 总用例 | 通过 | 失败 | 跳过 | 通过率 |\n")
        f.write("|------|--------|------|------|------|--------|\n")
        for module, stats in test_results["modules"].items():
            r = stats['passed']/max(stats['total'],1)*100
            f.write(f"| {module} | {stats['total']} | {stats['passed']} | {stats['failed']} | {stats['skipped']} | {r:.1f}% |\n")

        f.write("\n## 详细测试结果\n\n")
        for module, stats in test_results["modules"].items():
            f.write(f"### {module} ({stats['passed']}/{stats['total']})\n\n")
            for test in stats["tests"]:
                status = "✅" if test["result"] == "PASS" else "❌" if test["result"] == "FAIL" else "⏭️"
                f.write(f"- {status} **{test['name']}** [{test['time']}]\n")
                if test["detail"]:
                    f.write(f"  - {test['detail']}\n")
            f.write("\n")


# ==================== 认证模块测试 (10个) ====================
def test_auth_module():
    """认证模块测试 - 10个用例"""
    module = "认证模块"
    print(f"\n{'='*50}\n开始测试: {module}\n{'='*50}")

    # 1. 管理员登录成功
    resp = make_request("POST", "/api/auth/login", data={"username": "admin", "password": "admin123"}, form_data=True)
    if resp.status_code == 200 and "access_token" in resp.json():
        auth_tokens["admin"] = resp.json().get("access_token")
        log_test(module, "管理员登录成功", "PASS", f"Token获取成功")
    else:
        log_test(module, "管理员登录成功", "FAIL", f"状态码: {resp.status_code}")

    # 2. 登录响应包含必要字段
    resp = make_request("POST", "/api/auth/login", data={"username": "admin", "password": "admin123"}, form_data=True)
    if resp.status_code == 200:
        data = resp.json()
        required = ["access_token", "refresh_token", "token_type"]
        if all(k in data for k in required):
            log_test(module, "登录响应字段完整性", "PASS", "包含所有必要字段")
        else:
            log_test(module, "登录响应字段完整性", "FAIL", f"缺少字段: {set(required) - set(data.keys())}")
    else:
        log_test(module, "登录响应字段完整性", "FAIL", f"状态码: {resp.status_code}")

    # 3. 错误密码登录失败
    resp = make_request("POST", "/api/auth/login", data={"username": "admin", "password": "wrongpassword"}, form_data=True)
    log_test(module, "错误密码登录失败", "PASS" if resp.status_code == 401 else "FAIL", f"状态码: {resp.status_code}")

    # 4. 不存在用户登录失败
    resp = make_request("POST", "/api/auth/login", data={"username": "nonexistent", "password": "anypassword"}, form_data=True)
    log_test(module, "不存在用户登录失败", "PASS" if resp.status_code == 401 else "FAIL", f"状态码: {resp.status_code}")

    # 5. 空密码登录失败
    resp = make_request("POST", "/api/auth/login", data={"username": "admin", "password": ""}, form_data=True)
    log_test(module, "空密码登录失败", "PASS" if resp.status_code in [401, 422] else "FAIL", f"状态码: {resp.status_code}")

    # 6. 获取当前用户信息
    resp = make_request("GET", "/api/auth/me", token=auth_tokens["admin"])
    if resp.status_code == 200 and resp.json().get("username") == "admin":
        log_test(module, "获取当前用户信息", "PASS", f"用户: {resp.json().get('username')}")
    else:
        log_test(module, "获取当前用户信息", "FAIL", f"状态码: {resp.status_code}")

    # 7. 无Token访问受保护接口
    resp = make_request("GET", "/api/auth/me")
    log_test(module, "无Token访问受保护接口", "PASS" if resp.status_code == 401 else "FAIL", f"状态码: {resp.status_code}")

    # 8. 无效Token访问
    resp = make_request("GET", "/api/auth/me", token="invalid_token_xyz")
    log_test(module, "无效Token访问", "PASS" if resp.status_code == 401 else "FAIL", f"状态码: {resp.status_code}")

    # 9. 过期Token访问
    expired_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTAwMDAwMDAwMH0.invalid"
    resp = make_request("GET", "/api/auth/me", token=expired_token)
    log_test(module, "过期Token访问", "PASS" if resp.status_code == 401 else "FAIL", f"状态码: {resp.status_code}")

    # 10. 用户登出
    resp = make_request("POST", "/api/auth/logout", token=auth_tokens["admin"])
    log_test(module, "用户登出", "PASS" if resp.status_code == 200 else "FAIL", f"状态码: {resp.status_code}")

    # 重新登录获取新token
    resp = make_request("POST", "/api/auth/login", data={"username": "admin", "password": "admin123"}, form_data=True)
    if resp.status_code == 200:
        auth_tokens["admin"] = resp.json().get("access_token")


# ==================== 用户管理模块测试 (10个) ====================
def test_users_module():
    """用户管理模块测试 - 10个用例"""
    module = "用户管理"
    print(f"\n{'='*50}\n开始测试: {module}\n{'='*50}")

    # 1. 获取用户列表
    resp = make_request("GET", "/api/users/", token=auth_tokens["admin"])
    if resp.status_code == 200:
        users = resp.json()
        log_test(module, "获取用户列表", "PASS", f"用户数: {len(users)}")
    else:
        log_test(module, "获取用户列表", "FAIL", f"状态码: {resp.status_code}")

    # 2. 获取指定用户详情
    resp = make_request("GET", "/api/users/1", token=auth_tokens["admin"])
    if resp.status_code == 200 and resp.json().get("username"):
        log_test(module, "获取用户详情", "PASS", f"用户名: {resp.json().get('username')}")
    else:
        log_test(module, "获取用户详情", "FAIL", f"状态码: {resp.status_code}")

    # 3. 获取不存在的用户
    resp = make_request("GET", "/api/users/99999", token=auth_tokens["admin"])
    log_test(module, "获取不存在用户", "PASS" if resp.status_code == 404 else "FAIL", f"状态码: {resp.status_code}")

    # 4. 更新用户信息
    resp = make_request("PUT", "/api/users/2", token=auth_tokens["admin"], data={"role": "user"})
    log_test(module, "更新用户信息", "PASS" if resp.status_code == 200 else "FAIL", f"状态码: {resp.status_code}")

    # 5. 无权限获取用户列表
    resp = make_request("GET", "/api/users/")
    log_test(module, "无Token获取用户列表", "PASS" if resp.status_code == 401 else "FAIL", f"状态码: {resp.status_code}")

    # 6. 验证用户数据结构
    resp = make_request("GET", "/api/users/1", token=auth_tokens["admin"])
    if resp.status_code == 200:
        data = resp.json()
        required = ["id", "username", "role"]
        if all(k in data for k in required):
            log_test(module, "用户数据结构验证", "PASS", "包含必要字段")
        else:
            log_test(module, "用户数据结构验证", "FAIL", "缺少必要字段")
    else:
        log_test(module, "用户数据结构验证", "FAIL", f"状态码: {resp.status_code}")

    # 7. 普通用户无权访问用户管理
    # 先尝试用普通用户登录
    resp = make_request("POST", "/api/auth/login", data={"username": "bs", "password": "bs123456"}, form_data=True)
    if resp.status_code == 200:
        user_token = resp.json().get("access_token")
        resp2 = make_request("GET", "/api/users/", token=user_token)
        log_test(module, "普通用户访问用户管理", "PASS" if resp2.status_code == 403 else "FAIL", f"状态码: {resp2.status_code}")
    else:
        log_test(module, "普通用户访问用户管理", "SKIP", "无法获取普通用户token")

    # 8-10. 边界测试
    resp = make_request("GET", "/api/users/0", token=auth_tokens["admin"])
    log_test(module, "获取ID为0的用户", "PASS" if resp.status_code in [404, 422] else "FAIL", f"状态码: {resp.status_code}")

    resp = make_request("GET", "/api/users/-1", token=auth_tokens["admin"])
    log_test(module, "获取ID为负数的用户", "PASS" if resp.status_code in [404, 422] else "FAIL", f"状态码: {resp.status_code}")

    resp = make_request("GET", "/api/users/abc", token=auth_tokens["admin"])
    log_test(module, "获取ID为非数字的用户", "PASS" if resp.status_code in [404, 422] else "FAIL", f"状态码: {resp.status_code}")


# ==================== 平台管理模块测试 (10个) ====================
def test_platforms_module():
    """平台管理模块测试 - 10个用例"""
    module = "平台管理"
    print(f"\n{'='*50}\n开始测试: {module}\n{'='*50}")

    # 1. 获取平台列表
    resp = make_request("GET", "/api/platforms/", token=auth_tokens["admin"])
    if resp.status_code == 200:
        platforms = extract_data(resp)
        real_data["platforms"] = [p["id"] for p in platforms] if platforms else []
        log_test(module, "获取平台列表", "PASS", f"平台数: {len(platforms)}")
    else:
        log_test(module, "获取平台列表", "FAIL", f"状态码: {resp.status_code}")

    # 2. 创建平台
    resp = make_request("POST", "/api/platforms/", token=auth_tokens["admin"], data={
        "name": f"测试平台_{int(time.time())}",
        "description": "API测试创建"
    })
    if resp.status_code == 200:
        new_id = resp.json().get("id")
        if new_id:
            created_data["platforms"].append(new_id)
        log_test(module, "创建平台", "PASS", f"新平台ID: {new_id}")
    else:
        log_test(module, "创建平台", "FAIL", f"状态码: {resp.status_code}")

    # 3. 获取平台详情
    if real_data["platforms"]:
        resp = make_request("GET", f"/api/platforms/{real_data['platforms'][0]}", token=auth_tokens["admin"])
        log_test(module, "获取平台详情", "PASS" if resp.status_code == 200 else "FAIL", f"状态码: {resp.status_code}")
    else:
        log_test(module, "获取平台详情", "SKIP", "无平台数据")

    # 4. 更新平台
    if real_data["platforms"]:
        resp = make_request("PUT", f"/api/platforms/{real_data['platforms'][0]}", token=auth_tokens["admin"], data={
            "name": f"更新平台_{int(time.time())}"
        })
        log_test(module, "更新平台", "PASS" if resp.status_code == 200 else "FAIL", f"状态码: {resp.status_code}")
    else:
        log_test(module, "更新平台", "SKIP", "无平台数据")

    # 5. 获取不存在的平台
    resp = make_request("GET", "/api/platforms/99999", token=auth_tokens["admin"])
    log_test(module, "获取不存在平台", "PASS" if resp.status_code == 404 else "FAIL", f"状态码: {resp.status_code}")

    # 6. 无Token访问
    resp = make_request("GET", "/api/platforms/")
    log_test(module, "无Token获取平台", "PASS" if resp.status_code == 401 else "FAIL", f"状态码: {resp.status_code}")

    # 7. 创建空名称平台
    resp = make_request("POST", "/api/platforms/", token=auth_tokens["admin"], data={"name": ""})
    log_test(module, "创建空名称平台", "PASS" if resp.status_code in [400, 422] else "FAIL", f"状态码: {resp.status_code}")

    # 8. 创建超长名称平台
    long_name = "a" * 500
    resp = make_request("POST", "/api/platforms/", token=auth_tokens["admin"], data={"name": long_name})
    log_test(module, "创建超长名称平台", "PASS" if resp.status_code in [200, 400, 422] else "FAIL", f"状态码: {resp.status_code}")

    # 9. 删除平台
    if created_data["platforms"]:
        resp = make_request("DELETE", f"/api/platforms/{created_data['platforms'][0]}", token=auth_tokens["admin"])
        log_test(module, "删除平台", "PASS" if resp.status_code == 200 else "FAIL", f"状态码: {resp.status_code}")
    else:
        log_test(module, "删除平台", "SKIP", "无可删除的平台")

    # 10. 删除不存在的平台
    resp = make_request("DELETE", "/api/platforms/99999", token=auth_tokens["admin"])
    log_test(module, "删除不存在平台", "PASS" if resp.status_code == 404 else "FAIL", f"状态码: {resp.status_code}")


# ==================== 项目管理模块测试 (15个) ====================
def test_projects_module():
    """项目管理模块测试 - 15个用例"""
    module = "项目管理"
    print(f"\n{'='*50}\n开始测试: {module}\n{'='*50}")

    # 1. 获取项目列表
    resp = make_request("GET", "/api/projects/", token=auth_tokens["admin"])
    if resp.status_code == 200:
        projects = resp.json()
        real_data["projects"] = [p["id"] for p in projects] if projects else []
        log_test(module, "获取项目列表", "PASS", f"项目数: {len(projects)}")
    else:
        log_test(module, "获取项目列表", "FAIL", f"状态码: {resp.status_code}")

    # 2. 创建项目
    platform_id = real_data["platforms"][0] if real_data["platforms"] else None
    resp = make_request("POST", "/api/projects/", token=auth_tokens["admin"], data={
        "title": f"测试项目_{int(time.time())}",
        "student_name": "测试学生",
        "platform_id": platform_id,
        "price": 1000.0
    })
    if resp.status_code == 200:
        new_id = resp.json().get("id")
        if new_id:
            created_data["projects"].append(new_id)
            real_data["projects"].append(new_id)
        log_test(module, "创建项目", "PASS", f"新项目ID: {new_id}")
    else:
        log_test(module, "创建项目", "FAIL", f"状态码: {resp.status_code}")

    # 3. 获取项目详情
    if real_data["projects"]:
        resp = make_request("GET", f"/api/projects/{real_data['projects'][0]}", token=auth_tokens["admin"])
        log_test(module, "获取项目详情", "PASS" if resp.status_code == 200 else "FAIL", f"状态码: {resp.status_code}")

    # 4. 更新项目
    if real_data["projects"]:
        resp = make_request("PUT", f"/api/projects/{real_data['projects'][0]}", token=auth_tokens["admin"], data={
            "title": f"更新项目_{int(time.time())}"
        })
        log_test(module, "更新项目", "PASS" if resp.status_code == 200 else "FAIL", f"状态码: {resp.status_code}")

    # 5. 按状态筛选
    resp = make_request("GET", "/api/projects/", token=auth_tokens["admin"], params={"status": "进行中"})
    log_test(module, "按状态筛选项目", "PASS" if resp.status_code == 200 else "FAIL", f"状态码: {resp.status_code}")

    # 6. 按用户筛选
    resp = make_request("GET", "/api/projects/", token=auth_tokens["admin"], params={"user_id": 1})
    log_test(module, "按用户筛选项目", "PASS" if resp.status_code == 200 else "FAIL", f"状态码: {resp.status_code}")

    # 7. 按平台筛选
    if real_data["platforms"]:
        resp = make_request("GET", "/api/projects/", token=auth_tokens["admin"], params={"platform_id": real_data["platforms"][0]})
        log_test(module, "按平台筛选项目", "PASS" if resp.status_code == 200 else "FAIL", f"状态码: {resp.status_code}")

    # 8. 分页查询
    resp = make_request("GET", "/api/projects/", token=auth_tokens["admin"], params={"skip": 0, "limit": 5})
    log_test(module, "分页查询项目", "PASS" if resp.status_code == 200 else "FAIL", f"状态码: {resp.status_code}")

    # 9. 获取不存在项目
    resp = make_request("GET", "/api/projects/99999", token=auth_tokens["admin"])
    log_test(module, "获取不存在项目", "PASS" if resp.status_code == 404 else "FAIL", f"状态码: {resp.status_code}")

    # 10. 无Token访问
    resp = make_request("GET", "/api/projects/")
    log_test(module, "无Token获取项目", "PASS" if resp.status_code == 401 else "FAIL", f"状态码: {resp.status_code}")

    # 11. 创建项目必填字段验证
    resp = make_request("POST", "/api/projects/", token=auth_tokens["admin"], data={})
    log_test(module, "创建空项目验证", "PASS" if resp.status_code in [400, 422] else "FAIL", f"状态码: {resp.status_code}")

    # 12. 项目结账
    if created_data["projects"]:
        resp = make_request("POST", f"/api/projects/{created_data['projects'][0]}/settle", token=auth_tokens["admin"])
        log_test(module, "项目结账", "PASS" if resp.status_code == 200 else "FAIL", f"状态码: {resp.status_code}")

    # 13. 添加项目步骤
    if real_data["projects"]:
        resp = make_request("POST", f"/api/projects/{real_data['projects'][0]}/steps", token=auth_tokens["admin"], data={
            "title": f"测试步骤_{int(time.time())}",
            "order": 1
        })
        log_test(module, "添加项目步骤", "PASS" if resp.status_code == 200 else "FAIL", f"状态码: {resp.status_code}")

    # 14. 获取项目列表响应结构
    resp = make_request("GET", "/api/projects/", token=auth_tokens["admin"])
    if resp.status_code == 200:
        data = resp.json()
        if isinstance(data, list):
            log_test(module, "项目列表响应结构", "PASS", "返回数组格式")
        else:
            log_test(module, "项目列表响应结构", "FAIL", "非数组格式")

    # 15. 组合筛选
    resp = make_request("GET", "/api/projects/", token=auth_tokens["admin"], params={
        "status": "进行中",
        "skip": 0,
        "limit": 10
    })
    log_test(module, "组合筛选项目", "PASS" if resp.status_code == 200 else "FAIL", f"状态码: {resp.status_code}")


# ==================== 附件管理模块测试 (20个) ====================
def test_attachments_module():
    """附件管理模块测试 - 20个用例（包含上传下载）"""
    module = "附件管理"
    print(f"\n{'='*50}\n开始测试: {module}\n{'='*50}")

    project_id = real_data["projects"][0] if real_data["projects"] else 1

    # ========== 文件上传测试 ==========

    # 1. 上传文本文件
    text_content = b"Hello, this is a test file for API testing."
    files = {"file": ("test.txt", io.BytesIO(text_content), "text/plain")}
    data = {"file_type": "其他", "description": "API测试文本文件"}
    resp = make_request("POST", f"/api/attachments/project/{project_id}", token=auth_tokens["admin"], files=files, data=data)
    if resp.status_code == 200:
        att_id = resp.json().get("id")
        if att_id:
            created_data["attachments"].append(att_id)
        log_test(module, "上传文本文件", "PASS", f"附件ID: {att_id}")
    else:
        log_test(module, "上传文本文件", "FAIL", f"状态码: {resp.status_code}")

    # 2. 上传JSON文件
    json_content = json.dumps({"test": "data", "timestamp": time.time()}).encode()
    files = {"file": ("test.json", io.BytesIO(json_content), "application/json")}
    resp = make_request("POST", f"/api/attachments/project/{project_id}", token=auth_tokens["admin"], files=files, data=data)
    log_test(module, "上传JSON文件", "PASS" if resp.status_code == 200 else "FAIL", f"状态码: {resp.status_code}")

    # 3. 上传Markdown文件
    md_content = b"# Test Markdown\n\nThis is a **test** markdown file."
    files = {"file": ("test.md", io.BytesIO(md_content), "text/markdown")}
    resp = make_request("POST", f"/api/attachments/project/{project_id}", token=auth_tokens["admin"], files=files, data=data)
    log_test(module, "上传Markdown文件", "PASS" if resp.status_code == 200 else "FAIL", f"状态码: {resp.status_code}")

    # 4. 上传图片文件 (模拟PNG)
    # 创建一个最小的PNG文件头
    png_header = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde'
    files = {"file": ("test.png", io.BytesIO(png_header), "image/png")}
    resp = make_request("POST", f"/api/attachments/project/{project_id}", token=auth_tokens["admin"], files=files, data=data)
    log_test(module, "上传图片文件", "PASS" if resp.status_code == 200 else "FAIL", f"状态码: {resp.status_code}")

    # 5. 上传中文文件名文件
    chinese_content = "中文文件名测试内容".encode('utf-8')
    files = {"file": ("测试文件_中文.txt", io.BytesIO(chinese_content), "text/plain")}
    resp = make_request("POST", f"/api/attachments/project/{project_id}", token=auth_tokens["admin"], files=files, data=data)
    log_test(module, "上传中文文件名", "PASS" if resp.status_code == 200 else "FAIL", f"状态码: {resp.status_code}")

    # 6. 上传大文件名文件
    long_name = "a" * 200 + ".txt"
    files = {"file": (long_name, io.BytesIO(text_content), "text/plain")}
    resp = make_request("POST", f"/api/attachments/project/{project_id}", token=auth_tokens["admin"], files=files, data=data)
    log_test(module, "上传长文件名文件", "PASS" if resp.status_code == 200 else "FAIL", f"状态码: {resp.status_code}")

    # 7. 无Token上传
    files = {"file": ("noauth.txt", io.BytesIO(text_content), "text/plain")}
    resp = make_request("POST", f"/api/attachments/project/{project_id}", files=files, data=data)
    log_test(module, "无Token上传文件", "PASS" if resp.status_code == 401 else "FAIL", f"状态码: {resp.status_code}")

    # 8. 上传到不存在项目
    files = {"file": ("test.txt", io.BytesIO(text_content), "text/plain")}
    resp = make_request("POST", "/api/attachments/project/99999", token=auth_tokens["admin"], files=files, data=data)
    log_test(module, "上传到不存在项目", "PASS" if resp.status_code in [404, 403] else "FAIL", f"状态码: {resp.status_code}")

    # ========== 文件下载测试 ==========

    # 9. 获取项目附件列表
    resp = make_request("GET", f"/api/attachments/project/{project_id}", token=auth_tokens["admin"])
    if resp.status_code == 200:
        attachments = resp.json()
        real_data["attachments"] = [a["id"] for a in attachments] if attachments else []
        log_test(module, "获取项目附件列表", "PASS", f"附件数: {len(attachments)}")
    else:
        log_test(module, "获取项目附件列表", "FAIL", f"状态码: {resp.status_code}")

    # 10. 下载附件
    if real_data["attachments"]:
        resp = make_request("GET", f"/api/attachments/{real_data['attachments'][0]}/download", token=auth_tokens["admin"])
        if resp.status_code == 200:
            content_type = resp.headers.get("Content-Type", "")
            content_disp = resp.headers.get("Content-Disposition", "")
            log_test(module, "下载附件", "PASS", f"Content-Type: {content_type[:30]}")
        else:
            log_test(module, "下载附件", "FAIL", f"状态码: {resp.status_code}")

    # 11. 下载附件内容验证
    if created_data["attachments"]:
        resp = make_request("GET", f"/api/attachments/{created_data['attachments'][0]}/download", token=auth_tokens["admin"])
        if resp.status_code == 200 and resp.content:
            log_test(module, "下载附件内容验证", "PASS", f"内容大小: {len(resp.content)} bytes")
        else:
            log_test(module, "下载附件内容验证", "FAIL", f"状态码: {resp.status_code}")

    # 12. 下载不存在附件
    resp = make_request("GET", "/api/attachments/99999/download", token=auth_tokens["admin"])
    log_test(module, "下载不存在附件", "PASS" if resp.status_code == 404 else "FAIL", f"状态码: {resp.status_code}")

    # ========== 文件预览测试 ==========

    # 13. 预览附件
    if real_data["attachments"]:
        resp = make_request("GET", f"/api/attachments/{real_data['attachments'][0]}/preview", token=auth_tokens["admin"])
        log_test(module, "预览附件", "PASS" if resp.status_code == 200 else "FAIL", f"状态码: {resp.status_code}")

    # 14. 预览文本文件
    if created_data["attachments"]:
        resp = make_request("GET", f"/api/attachments/{created_data['attachments'][0]}/preview", token=auth_tokens["admin"])
        log_test(module, "预览文本文件", "PASS" if resp.status_code == 200 else "FAIL", f"状态码: {resp.status_code}")

    # 15. 预览不存在附件
    resp = make_request("GET", "/api/attachments/99999/preview", token=auth_tokens["admin"])
    log_test(module, "预览不存在附件", "PASS" if resp.status_code == 404 else "FAIL", f"状态码: {resp.status_code}")

    # ========== 其他操作测试 ==========

    # 16. 获取附件详情
    if real_data["attachments"]:
        resp = make_request("GET", f"/api/attachments/{real_data['attachments'][0]}", token=auth_tokens["admin"])
        log_test(module, "获取附件详情", "PASS" if resp.status_code == 200 else "FAIL", f"状态码: {resp.status_code}")

    # 17. 更新附件信息
    if real_data["attachments"]:
        resp = make_request("PUT", f"/api/attachments/{real_data['attachments'][0]}", token=auth_tokens["admin"], data={
            "description": f"更新描述_{int(time.time())}"
        })
        log_test(module, "更新附件信息", "PASS" if resp.status_code == 200 else "FAIL", f"状态码: {resp.status_code}")

    # 18. 批量获取附件
    if len(real_data["attachments"]) >= 2:
        resp = make_request("POST", "/api/attachments/batch", token=auth_tokens["admin"], data=real_data["attachments"][:3])
        log_test(module, "批量获取附件", "PASS" if resp.status_code == 200 else "FAIL", f"状态码: {resp.status_code}")

    # 19. 复制附件
    if real_data["attachments"] and real_data["projects"]:
        resp = make_request("POST", f"/api/attachments/{real_data['attachments'][0]}/copy", token=auth_tokens["admin"], data={
            "target_project_id": real_data["projects"][0]
        })
        log_test(module, "复制附件", "PASS" if resp.status_code == 200 else "FAIL", f"状态码: {resp.status_code}")

    # 20. 无Token下载
    resp = make_request("GET", f"/api/attachments/{real_data['attachments'][0]}/download" if real_data["attachments"] else "/api/attachments/1/download")
    log_test(module, "无Token下载附件", "PASS" if resp.status_code == 401 else "FAIL", f"状态码: {resp.status_code}")


# ==================== 附件文件夹模块测试 (10个) ====================
def test_folders_module():
    """附件文件夹模块测试 - 10个用例"""
    module = "附件文件夹"
    print(f"\n{'='*50}\n开始测试: {module}\n{'='*50}")

    project_id = real_data["projects"][0] if real_data["projects"] else 1

    # 1. 获取项目文件夹列表
    resp = make_request("GET", f"/api/attachment-folders/project/{project_id}", token=auth_tokens["admin"])
    if resp.status_code == 200:
        folders = resp.json()
        real_data["folders"] = [f["id"] for f in folders] if folders else []
        log_test(module, "获取项目文件夹列表", "PASS", f"文件夹数: {len(folders)}")
    else:
        log_test(module, "获取项目文件夹列表", "FAIL", f"状态码: {resp.status_code}")

    # 2. 创建文件夹
    resp = make_request("POST", f"/api/attachment-folders/project/{project_id}", token=auth_tokens["admin"], data={
        "name": f"测试文件夹_{int(time.time())}"
    })
    if resp.status_code == 200:
        folder_id = resp.json().get("id")
        if folder_id:
            created_data["folders"].append(folder_id)
        log_test(module, "创建文件夹", "PASS", f"文件夹ID: {folder_id}")
    else:
        log_test(module, "创建文件夹", "FAIL", f"状态码: {resp.status_code}")

    # 3. 更新文件夹
    if created_data["folders"]:
        resp = make_request("PUT", f"/api/attachment-folders/{created_data['folders'][0]}", token=auth_tokens["admin"], data={
            "name": f"更新文件夹_{int(time.time())}"
        })
        log_test(module, "更新文件夹", "PASS" if resp.status_code == 200 else "FAIL", f"状态码: {resp.status_code}")

    # 4. 创建空名称文件夹
    resp = make_request("POST", f"/api/attachment-folders/project/{project_id}", token=auth_tokens["admin"], data={"name": ""})
    log_test(module, "创建空名称文件夹", "PASS" if resp.status_code in [400, 422] else "FAIL", f"状态码: {resp.status_code}")

    # 5. 获取不存在项目的文件夹
    resp = make_request("GET", "/api/attachment-folders/project/99999", token=auth_tokens["admin"])
    log_test(module, "获取不存在项目文件夹", "PASS" if resp.status_code in [200, 404] else "FAIL", f"状态码: {resp.status_code}")

    # 6. 无Token访问
    resp = make_request("GET", f"/api/attachment-folders/project/{project_id}")
    log_test(module, "无Token获取文件夹", "PASS" if resp.status_code == 401 else "FAIL", f"状态码: {resp.status_code}")

    # 7. 删除文件夹
    if created_data["folders"]:
        # 先创建一个用于删除的文件夹
        resp = make_request("POST", f"/api/attachment-folders/project/{project_id}", token=auth_tokens["admin"], data={
            "name": f"待删除文件夹_{int(time.time())}"
        })
        if resp.status_code == 200:
            del_folder_id = resp.json().get("id")
            resp = make_request("DELETE", f"/api/attachment-folders/{del_folder_id}", token=auth_tokens["admin"])
            log_test(module, "删除文件夹", "PASS" if resp.status_code == 200 else "FAIL", f"状态码: {resp.status_code}")
        else:
            log_test(module, "删除文件夹", "SKIP", "无法创建测试文件夹")
    else:
        log_test(module, "删除文件夹", "SKIP", "无可删除的文件夹")

    # 8. 删除不存在文件夹
    resp = make_request("DELETE", "/api/attachment-folders/99999", token=auth_tokens["admin"])
    log_test(module, "删除不存在文件夹", "PASS" if resp.status_code == 404 else "FAIL", f"状态码: {resp.status_code}")

    # 9. 历史项目文件夹列表
    resp = make_request("GET", "/api/attachment-folders/historical-project/1", token=auth_tokens["admin"])
    log_test(module, "获取历史项目文件夹", "PASS" if resp.status_code in [200, 404] else "FAIL", f"状态码: {resp.status_code}")

    # 10. 文件夹数据结构验证
    if real_data["folders"]:
        resp = make_request("GET", f"/api/attachment-folders/project/{project_id}", token=auth_tokens["admin"])
        if resp.status_code == 200:
            folders = resp.json()
            if folders and "id" in folders[0] and "name" in folders[0]:
                log_test(module, "文件夹数据结构验证", "PASS", "包含必要字段")
            else:
                log_test(module, "文件夹数据结构验证", "FAIL", "缺少必要字段")


# ==================== 标签管理模块测试 (12个) ====================
def test_tags_module():
    """标签管理模块测试 - 12个用例"""
    module = "标签管理"
    print(f"\n{'='*50}\n开始测试: {module}\n{'='*50}")

    # 1. 获取标签列表
    resp = make_request("GET", "/api/tags/", token=auth_tokens["admin"])
    if resp.status_code == 200:
        tags = resp.json()
        real_data["tags"] = [t["id"] for t in tags] if tags else []
        log_test(module, "获取标签列表", "PASS", f"标签数: {len(tags)}")
    else:
        log_test(module, "获取标签列表", "FAIL", f"状态码: {resp.status_code}")

    # 2. 创建标签
    resp = make_request("POST", "/api/tags/", token=auth_tokens["admin"], data={
        "name": f"测试标签_{int(time.time())}",
        "color": "#FF5733"
    })
    if resp.status_code == 200:
        tag_id = resp.json().get("id")
        if tag_id:
            created_data["tags"].append(tag_id)
        log_test(module, "创建标签", "PASS", f"标签ID: {tag_id}")
    else:
        log_test(module, "创建标签", "FAIL", f"状态码: {resp.status_code}")

    # 3. 获取常用标签（公开接口）
    resp = make_request("GET", "/api/tags/common")
    log_test(module, "获取常用标签(公开)", "PASS" if resp.status_code == 200 else "FAIL", f"状态码: {resp.status_code}")

    # 4. 获取标签详情
    if real_data["tags"]:
        resp = make_request("GET", f"/api/tags/{real_data['tags'][0]}", token=auth_tokens["admin"])
        log_test(module, "获取标签详情", "PASS" if resp.status_code == 200 else "FAIL", f"状态码: {resp.status_code}")

    # 5. 更新标签
    if created_data["tags"]:
        resp = make_request("PUT", f"/api/tags/{created_data['tags'][0]}", token=auth_tokens["admin"], data={
            "name": f"更新标签_{int(time.time())}"
        })
        log_test(module, "更新标签", "PASS" if resp.status_code == 200 else "FAIL", f"状态码: {resp.status_code}")

    # 6. 为项目添加标签
    if real_data["projects"] and real_data["tags"]:
        resp = make_request("POST", f"/api/tags/project/{real_data['projects'][0]}/tags", token=auth_tokens["admin"], params={"tag_id": real_data["tags"][0]})
        log_test(module, "为项目添加标签", "PASS" if resp.status_code in [200, 400] else "FAIL", f"状态码: {resp.status_code}")

    # 7. 移除项目标签
    if real_data["projects"] and real_data["tags"]:
        resp = make_request("DELETE", f"/api/tags/project/{real_data['projects'][0]}/tags/{real_data['tags'][0]}", token=auth_tokens["admin"])
        log_test(module, "移除项目标签", "PASS" if resp.status_code in [200, 404] else "FAIL", f"状态码: {resp.status_code}")

    # 8. 获取不存在的标签
    resp = make_request("GET", "/api/tags/99999", token=auth_tokens["admin"])
    log_test(module, "获取不存在标签", "PASS" if resp.status_code == 404 else "FAIL", f"状态码: {resp.status_code}")

    # 9. 删除标签
    if created_data["tags"]:
        resp = make_request("DELETE", f"/api/tags/{created_data['tags'][0]}", token=auth_tokens["admin"])
        log_test(module, "删除标签", "PASS" if resp.status_code == 200 else "FAIL", f"状态码: {resp.status_code}")

    # 10. 无Token获取标签列表
    resp = make_request("GET", "/api/tags/")
    log_test(module, "无Token获取标签列表", "PASS" if resp.status_code == 401 else "FAIL", f"状态码: {resp.status_code}")

    # 11. 创建空名称标签
    resp = make_request("POST", "/api/tags/", token=auth_tokens["admin"], data={"name": ""})
    log_test(module, "创建空名称标签", "PASS" if resp.status_code in [400, 422] else "FAIL", f"状态码: {resp.status_code}")

    # 12. 获取标签列表（包含常用标签）
    resp = make_request("GET", "/api/tags/", token=auth_tokens["admin"], params={"include_common": True})
    log_test(module, "获取标签列表(含常用)", "PASS" if resp.status_code == 200 else "FAIL", f"状态码: {resp.status_code}")


# ==================== 待办管理模块测试 (12个) ====================
def test_todos_module():
    """待办管理模块测试 - 12个用例"""
    module = "待办管理"
    print(f"\n{'='*50}\n开始测试: {module}\n{'='*50}")

    today = str(date.today())

    # 1. 获取今日待办
    resp = make_request("GET", "/api/todos/", token=auth_tokens["admin"])
    if resp.status_code == 200:
        todos = resp.json()
        real_data["todos"] = [t["id"] for t in todos] if todos else []
        log_test(module, "获取今日待办", "PASS", f"待办数: {len(todos)}")
    else:
        log_test(module, "获取今日待办", "FAIL", f"状态码: {resp.status_code}")

    # 2. 创建待办
    resp = make_request("POST", "/api/todos/", token=auth_tokens["admin"], data={
        "title": f"测试待办_{int(time.time())}",
        "target_date": today,
        "estimated_income": 500.0
    })
    if resp.status_code == 200:
        todo_id = resp.json().get("id")
        if todo_id:
            created_data["todos"].append(todo_id)
        log_test(module, "创建待办", "PASS", f"待办ID: {todo_id}")
    else:
        log_test(module, "创建待办", "FAIL", f"状态码: {resp.status_code}, {resp.text[:100] if hasattr(resp, 'text') else ''}")

    # 3. 按日期获取待办
    resp = make_request("GET", "/api/todos/", token=auth_tokens["admin"], params={"target_date": today})
    log_test(module, "按日期获取待办", "PASS" if resp.status_code == 200 else "FAIL", f"状态码: {resp.status_code}")

    # 4. 获取日历数据
    year, month = date.today().year, date.today().month
    resp = make_request("GET", "/api/todos/calendar", token=auth_tokens["admin"], params={"year": year, "month": month})
    log_test(module, "获取日历数据", "PASS" if resp.status_code == 200 else "FAIL", f"状态码: {resp.status_code}")

    # 5. 更新待办
    if created_data["todos"]:
        resp = make_request("PUT", f"/api/todos/{created_data['todos'][0]}", token=auth_tokens["admin"], data={
            "title": f"更新待办_{int(time.time())}",
            "completed": True
        })
        log_test(module, "更新待办", "PASS" if resp.status_code == 200 else "FAIL", f"状态码: {resp.status_code}")

    # 6. 删除待办
    # 先创建一个用于删除的待办
    resp = make_request("POST", "/api/todos/", token=auth_tokens["admin"], data={
        "title": f"待删除待办_{int(time.time())}",
        "target_date": today
    })
    if resp.status_code == 200:
        del_todo_id = resp.json().get("id")
        resp = make_request("DELETE", f"/api/todos/{del_todo_id}", token=auth_tokens["admin"])
        log_test(module, "删除待办", "PASS" if resp.status_code == 200 else "FAIL", f"状态码: {resp.status_code}")
    else:
        log_test(module, "删除待办", "SKIP", "无法创建测试待办")

    # 7. 无Token访问
    resp = make_request("GET", "/api/todos/")
    log_test(module, "无Token获取待办", "PASS" if resp.status_code == 401 else "FAIL", f"状态码: {resp.status_code}")

    # 8. 获取不存在待办
    resp = make_request("PUT", "/api/todos/99999", token=auth_tokens["admin"], data={"title": "test"})
    log_test(module, "更新不存在待办", "PASS" if resp.status_code == 404 else "FAIL", f"状态码: {resp.status_code}")

    # 9. 创建空标题待办
    resp = make_request("POST", "/api/todos/", token=auth_tokens["admin"], data={"title": "", "target_date": today})
    log_test(module, "创建空标题待办", "PASS" if resp.status_code in [400, 422] else "FAIL", f"状态码: {resp.status_code}")

    # 10. 日历数据边界测试（未来日期）
    resp = make_request("GET", "/api/todos/calendar", token=auth_tokens["admin"], params={"year": 2030, "month": 12})
    log_test(module, "获取未来日历数据", "PASS" if resp.status_code == 200 else "FAIL", f"状态码: {resp.status_code}")

    # 11. 日历数据边界测试（过去日期）
    resp = make_request("GET", "/api/todos/calendar", token=auth_tokens["admin"], params={"year": 2020, "month": 1})
    log_test(module, "获取过去日历数据", "PASS" if resp.status_code == 200 else "FAIL", f"状态码: {resp.status_code}")

    # 12. 待办数据结构验证
    resp = make_request("GET", "/api/todos/", token=auth_tokens["admin"])
    if resp.status_code == 200:
        todos = resp.json()
        if todos and "id" in todos[0] and "title" in todos[0]:
            log_test(module, "待办数据结构验证", "PASS", "包含必要字段")
        elif not todos:
            log_test(module, "待办数据结构验证", "PASS", "空列表格式正确")
        else:
            log_test(module, "待办数据结构验证", "FAIL", "缺少必要字段")


# ==================== Dashboard模块测试 (10个) ====================
def test_dashboard_module():
    """Dashboard模块测试 - 10个用例"""
    module = "Dashboard"
    print(f"\n{'='*50}\n开始测试: {module}\n{'='*50}")

    # 1. 获取统计数据
    resp = make_request("GET", "/api/dashboard/stats", token=auth_tokens["admin"])
    log_test(module, "获取统计数据", "PASS" if resp.status_code == 200 else "FAIL", f"状态码: {resp.status_code}")

    # 2. 统计数据非空
    resp = make_request("GET", "/api/dashboard/stats", token=auth_tokens["admin"])
    if resp.status_code == 200:
        data = resp.json()
        log_test(module, "统计数据非空", "PASS" if data else "FAIL", f"数据: {str(data)[:50]}")

    # 3. 无Token访问
    resp = make_request("GET", "/api/dashboard/stats")
    log_test(module, "无Token访问Dashboard", "PASS" if resp.status_code == 401 else "FAIL", f"状态码: {resp.status_code}")

    # 4. 响应时间测试
    start = time.time()
    resp = make_request("GET", "/api/dashboard/stats", token=auth_tokens["admin"])
    elapsed = (time.time() - start) * 1000
    log_test(module, "Dashboard响应时间", "PASS" if elapsed < 1000 else "FAIL", f"响应时间: {elapsed:.0f}ms")

    # 5-10. 数据一致性检查
    resp = make_request("GET", "/api/dashboard/stats", token=auth_tokens["admin"])
    if resp.status_code == 200:
        data = resp.json()
        # 处理嵌套的响应结构
        if "data" in data:
            stats = data["data"]
        else:
            stats = data

        # 检查各字段存在性
        fields_to_check = ["total_projects", "completed_projects", "in_progress_projects", "total_income", "pending_income"]
        for field in fields_to_check:
            if field in stats:
                log_test(module, f"统计数据字段:{field}", "PASS", f"值: {stats[field]}")
            else:
                log_test(module, f"统计数据字段:{field}", "FAIL", "字段不存在")


# ==================== 历史项目模块测试 (12个) ====================
def test_historical_projects_module():
    """历史项目模块测试 - 12个用例"""
    module = "历史项目"
    print(f"\n{'='*50}\n开始测试: {module}\n{'='*50}")

    # 1. 获取历史项目列表
    resp = make_request("GET", "/api/historical-projects/", token=auth_tokens["admin"])
    if resp.status_code == 200:
        projects = resp.json()
        real_data["historical_projects"] = [p["id"] for p in projects] if projects else []
        log_test(module, "获取历史项目列表", "PASS", f"项目数: {len(projects)}")
    else:
        log_test(module, "获取历史项目列表", "FAIL", f"状态码: {resp.status_code}")

    # 2. 获取历史项目总数
    resp = make_request("GET", "/api/historical-projects/count", token=auth_tokens["admin"])
    log_test(module, "获取历史项目总数", "PASS" if resp.status_code == 200 else "FAIL", f"状态码: {resp.status_code}")

    # 3. 创建历史项目
    platform_id = real_data["platforms"][0] if real_data["platforms"] else None
    resp = make_request("POST", "/api/historical-projects/", token=auth_tokens["admin"], data={
        "title": f"测试历史项目_{int(time.time())}",
        "student_name": "测试学生",
        "platform_id": platform_id,
        "price": 800.0,
        "status": "已完成"
    })
    if resp.status_code == 200:
        hp_id = resp.json().get("id")
        if hp_id:
            created_data["historical_projects"].append(hp_id)
        log_test(module, "创建历史项目", "PASS", f"项目ID: {hp_id}")
    else:
        log_test(module, "创建历史项目", "FAIL", f"状态码: {resp.status_code}")

    # 4. 获取历史项目详情
    if created_data["historical_projects"]:
        resp = make_request("GET", f"/api/historical-projects/{created_data['historical_projects'][0]}", token=auth_tokens["admin"])
        log_test(module, "获取历史项目详情", "PASS" if resp.status_code == 200 else "FAIL", f"状态码: {resp.status_code}")

    # 5. 更新历史项目
    if created_data["historical_projects"]:
        resp = make_request("PUT", f"/api/historical-projects/{created_data['historical_projects'][0]}", token=auth_tokens["admin"], data={
            "title": f"更新历史项目_{int(time.time())}"
        })
        log_test(module, "更新历史项目", "PASS" if resp.status_code == 200 else "FAIL", f"状态码: {resp.status_code}")

    # 6. 按状态筛选
    resp = make_request("GET", "/api/historical-projects/", token=auth_tokens["admin"], params={"status": "已完成"})
    log_test(module, "按状态筛选历史项目", "PASS" if resp.status_code == 200 else "FAIL", f"状态码: {resp.status_code}")

    # 7. 搜索历史项目
    resp = make_request("GET", "/api/historical-projects/", token=auth_tokens["admin"], params={"search": "测试"})
    log_test(module, "搜索历史项目", "PASS" if resp.status_code == 200 else "FAIL", f"状态码: {resp.status_code}")

    # 8. 分页查询
    resp = make_request("GET", "/api/historical-projects/", token=auth_tokens["admin"], params={"skip": 0, "limit": 10})
    log_test(module, "分页查询历史项目", "PASS" if resp.status_code == 200 else "FAIL", f"状态码: {resp.status_code}")

    # 9. 获取不存在的历史项目
    resp = make_request("GET", "/api/historical-projects/99999", token=auth_tokens["admin"])
    log_test(module, "获取不存在历史项目", "PASS" if resp.status_code == 404 else "FAIL", f"状态码: {resp.status_code}")

    # 10. 无Token访问
    resp = make_request("GET", "/api/historical-projects/")
    log_test(module, "无Token获取历史项目", "PASS" if resp.status_code == 401 else "FAIL", f"状态码: {resp.status_code}")

    # 11. 删除历史项目
    # 先创建一个用于删除的项目
    resp = make_request("POST", "/api/historical-projects/", token=auth_tokens["admin"], data={
        "title": f"待删除历史项目_{int(time.time())}",
        "status": "已完成"
    })
    if resp.status_code == 200:
        del_id = resp.json().get("id")
        resp = make_request("DELETE", f"/api/historical-projects/{del_id}", token=auth_tokens["admin"])
        log_test(module, "删除历史项目", "PASS" if resp.status_code == 200 else "FAIL", f"状态码: {resp.status_code}")

    # 12. 从现有项目导入
    if real_data["projects"]:
        resp = make_request("POST", f"/api/historical-projects/import-from-project/{real_data['projects'][0]}", token=auth_tokens["admin"])
        log_test(module, "从现有项目导入", "PASS" if resp.status_code in [200, 400, 404] else "FAIL", f"状态码: {resp.status_code}")


# ==================== 系统设置模块测试 (10个) ====================
def test_system_settings_module():
    """系统设置模块测试 - 10个用例"""
    module = "系统设置"
    print(f"\n{'='*50}\n开始测试: {module}\n{'='*50}")

    # 1. 获取Token持续时间设置
    resp = make_request("GET", "/api/system-settings/token-duration", token=auth_tokens["admin"])
    log_test(module, "获取Token持续时间", "PASS" if resp.status_code == 200 else "FAIL", f"状态码: {resp.status_code}")

    # 2. 获取所有系统设置
    resp = make_request("GET", "/api/system-settings/", token=auth_tokens["admin"])
    log_test(module, "获取所有系统设置", "PASS" if resp.status_code == 200 else "FAIL", f"状态码: {resp.status_code}")

    # 3. 获取插件设置
    resp = make_request("GET", "/api/system-settings/plugin-settings", token=auth_tokens["admin"])
    log_test(module, "获取插件设置", "PASS" if resp.status_code == 200 else "FAIL", f"状态码: {resp.status_code}")

    # 4. 获取历史项目设置
    resp = make_request("GET", "/api/system-settings/historical-project", token=auth_tokens["admin"])
    log_test(module, "获取历史项目设置", "PASS" if resp.status_code == 200 else "FAIL", f"状态码: {resp.status_code}")

    # 5. 无Token访问
    resp = make_request("GET", "/api/system-settings/")
    log_test(module, "无Token访问系统设置", "PASS" if resp.status_code == 401 else "FAIL", f"状态码: {resp.status_code}")

    # 6. 更新Token持续时间
    resp = make_request("PUT", "/api/system-settings/token-duration", token=auth_tokens["admin"], data={
        "access_token_expire_minutes": 1440,
        "refresh_token_expire_days": 30
    })
    log_test(module, "更新Token持续时间", "PASS" if resp.status_code == 200 else "FAIL", f"状态码: {resp.status_code}")

    # 7. 获取特定设置
    resp = make_request("GET", "/api/system-settings/token-duration", token=auth_tokens["admin"])
    log_test(module, "获取特定设置", "PASS" if resp.status_code == 200 else "FAIL", f"状态码: {resp.status_code}")

    # 8. 更新插件设置
    resp = make_request("PUT", "/api/system-settings/plugin-settings", token=auth_tokens["admin"], data={})
    log_test(module, "更新插件设置", "PASS" if resp.status_code == 200 else "FAIL", f"状态码: {resp.status_code}")

    # 9. 设置数据结构验证
    resp = make_request("GET", "/api/system-settings/token-duration", token=auth_tokens["admin"])
    if resp.status_code == 200:
        data = resp.json()
        if "data" in data or "access_token_expire_minutes" in data:
            log_test(module, "设置数据结构验证", "PASS", "结构正确")
        else:
            log_test(module, "设置数据结构验证", "FAIL", "结构异常")

    # 10. 获取不存在的设置
    resp = make_request("GET", "/api/system-settings/nonexistent_setting_key", token=auth_tokens["admin"])
    log_test(module, "获取不存在设置", "PASS" if resp.status_code in [200, 404] else "FAIL", f"状态码: {resp.status_code}")


# ==================== 项目日志模块测试 (10个) ====================
def test_project_logs_module():
    """项目日志模块测试 - 10个用例"""
    module = "项目日志"
    print(f"\n{'='*50}\n开始测试: {module}\n{'='*50}")

    project_id = real_data["projects"][0] if real_data["projects"] else 1

    # 1. 获取项目日志列表
    resp = make_request("GET", f"/api/project-logs/project/{project_id}", token=auth_tokens["admin"])
    log_test(module, "获取项目日志列表", "PASS" if resp.status_code == 200 else "FAIL", f"状态码: {resp.status_code}")

    # 2. 获取日志带限制
    resp = make_request("GET", f"/api/project-logs/project/{project_id}", token=auth_tokens["admin"], params={"limit": 10})
    log_test(module, "获取项目日志(带限制)", "PASS" if resp.status_code == 200 else "FAIL", f"状态码: {resp.status_code}")

    # 3. 创建项目日志
    resp = make_request("POST", "/api/project-logs/", token=auth_tokens["admin"], data={
        "project_id": project_id,
        "action": "测试操作",
        "description": "API测试创建的日志"
    })
    log_test(module, "创建项目日志", "PASS" if resp.status_code == 200 else "FAIL", f"状态码: {resp.status_code}")

    # 4. 创建步骤更新日志
    resp = make_request("POST", "/api/project-logs/step-update", token=auth_tokens["admin"], data={
        "project_id": project_id,
        "step_id": 1,
        "old_status": "pending",
        "new_status": "completed"
    })
    log_test(module, "创建步骤更新日志", "PASS" if resp.status_code in [200, 404, 422] else "FAIL", f"状态码: {resp.status_code}")

    # 5. 获取不存在项目的日志
    resp = make_request("GET", "/api/project-logs/project/99999", token=auth_tokens["admin"])
    log_test(module, "获取不存在项目日志", "PASS" if resp.status_code in [200, 404] else "FAIL", f"状态码: {resp.status_code}")

    # 6. 无Token访问
    resp = make_request("GET", f"/api/project-logs/project/{project_id}")
    log_test(module, "无Token获取日志", "PASS" if resp.status_code == 401 else "FAIL", f"状态码: {resp.status_code}")

    # 7. 创建快照
    resp = make_request("POST", "/api/project-logs/snapshot", token=auth_tokens["admin"], data={
        "project_id": project_id,
        "snapshot_name": f"测试快照_{int(time.time())}"
    })
    log_test(module, "创建项目快照", "PASS" if resp.status_code in [200, 404, 422] else "FAIL", f"状态码: {resp.status_code}")

    # 8. 历史项目日志
    resp = make_request("GET", "/api/project-logs/historical-project/1", token=auth_tokens["admin"])
    log_test(module, "获取历史项目日志", "PASS" if resp.status_code in [200, 404] else "FAIL", f"状态码: {resp.status_code}")

    # 9. 删除日志
    # 先获取日志列表
    resp = make_request("GET", f"/api/project-logs/project/{project_id}", token=auth_tokens["admin"])
    if resp.status_code == 200:
        logs = resp.json()
        if logs and len(logs) > 0:
            log_id = logs[0].get("id")
            if log_id:
                resp = make_request("DELETE", f"/api/project-logs/{log_id}", token=auth_tokens["admin"])
                log_test(module, "删除项目日志", "PASS" if resp.status_code == 200 else "FAIL", f"状态码: {resp.status_code}")
            else:
                log_test(module, "删除项目日志", "SKIP", "无法获取日志ID")
        else:
            log_test(module, "删除项目日志", "SKIP", "无日志可删除")

    # 10. 日志数据结构验证
    resp = make_request("GET", f"/api/project-logs/project/{project_id}", token=auth_tokens["admin"])
    if resp.status_code == 200:
        logs = resp.json()
        if logs and "id" in logs[0] and "action" in logs[0]:
            log_test(module, "日志数据结构验证", "PASS", "包含必要字段")
        elif not logs:
            log_test(module, "日志数据结构验证", "PASS", "空列表格式正确")
        else:
            log_test(module, "日志数据结构验证", "FAIL", "缺少必要字段")


# ==================== 配件清单模块测试 (10个) ====================
def test_project_parts_module():
    """配件清单模块测试 - 10个用例"""
    module = "配件清单"
    print(f"\n{'='*50}\n开始测试: {module}\n{'='*50}")

    project_id = real_data["projects"][0] if real_data["projects"] else 1

    # 1. 获取项目配件清单
    resp = make_request("GET", f"/api/project-parts/project/{project_id}", token=auth_tokens["admin"])
    log_test(module, "获取项目配件清单", "PASS" if resp.status_code == 200 else "FAIL", f"状态码: {resp.status_code}")

    # 2. 批量创建配件
    resp = make_request("POST", f"/api/project-parts/project/{project_id}", token=auth_tokens["admin"], data=[
        {"name": f"测试配件_{int(time.time())}", "quantity": 1, "price": 100.0}
    ])
    log_test(module, "批量创建配件", "PASS" if resp.status_code == 200 else "FAIL", f"状态码: {resp.status_code}")

    # 3. 获取配件清单（验证创建）
    resp = make_request("GET", f"/api/project-parts/project/{project_id}", token=auth_tokens["admin"])
    if resp.status_code == 200:
        parts = resp.json()
        part_id = parts[0]["id"] if parts else None
        log_test(module, "验证配件创建", "PASS", f"配件数: {len(parts)}")
    else:
        part_id = None
        log_test(module, "验证配件创建", "FAIL", f"状态码: {resp.status_code}")

    # 4. 更新配件
    if part_id:
        resp = make_request("PUT", f"/api/project-parts/{part_id}", token=auth_tokens["admin"], data={
            "name": f"更新配件_{int(time.time())}",
            "quantity": 2
        })
        log_test(module, "更新配件", "PASS" if resp.status_code == 200 else "FAIL", f"状态码: {resp.status_code}")

    # 5. 删除配件
    if part_id:
        resp = make_request("DELETE", f"/api/project-parts/{part_id}", token=auth_tokens["admin"])
        log_test(module, "删除配件", "PASS" if resp.status_code == 200 else "FAIL", f"状态码: {resp.status_code}")

    # 6. 获取不存在项目的配件
    resp = make_request("GET", "/api/project-parts/project/99999", token=auth_tokens["admin"])
    log_test(module, "获取不存在项目配件", "PASS" if resp.status_code in [200, 404] else "FAIL", f"状态码: {resp.status_code}")

    # 7. 无Token访问
    resp = make_request("GET", f"/api/project-parts/project/{project_id}")
    log_test(module, "无Token获取配件", "PASS" if resp.status_code == 401 else "FAIL", f"状态码: {resp.status_code}")

    # 8. 更新不存在配件
    resp = make_request("PUT", "/api/project-parts/99999", token=auth_tokens["admin"], data={"name": "test"})
    log_test(module, "更新不存在配件", "PASS" if resp.status_code == 404 else "FAIL", f"状态码: {resp.status_code}")

    # 9. 删除不存在配件
    resp = make_request("DELETE", "/api/project-parts/99999", token=auth_tokens["admin"])
    log_test(module, "删除不存在配件", "PASS" if resp.status_code == 404 else "FAIL", f"状态码: {resp.status_code}")

    # 10. 历史项目配件
    resp = make_request("GET", "/api/project-parts/historical-project/1", token=auth_tokens["admin"])
    log_test(module, "获取历史项目配件", "PASS" if resp.status_code in [200, 404] else "FAIL", f"状态码: {resp.status_code}")


# ==================== 步骤模板模块测试 (10个) ====================
def test_step_templates_module():
    """步骤模板模块测试 - 10个用例"""
    module = "步骤模板"
    print(f"\n{'='*50}\n开始测试: {module}\n{'='*50}")

    # 1. 获取所有模板
    resp = make_request("GET", "/api/step-templates/", token=auth_tokens["admin"])
    log_test(module, "获取所有模板", "PASS" if resp.status_code == 200 else "FAIL", f"状态码: {resp.status_code}")

    # 2. 创建模板
    resp = make_request("POST", "/api/step-templates/", token=auth_tokens["admin"], data={
        "name": f"测试模板_{int(time.time())}",
        "steps": [{"title": "步骤1", "order": 1}]
    })
    if resp.status_code == 200:
        template_id = resp.json().get("id")
        log_test(module, "创建模板", "PASS", f"模板ID: {template_id}")
    else:
        template_id = None
        log_test(module, "创建模板", "FAIL", f"状态码: {resp.status_code}")

    # 3. 获取模板详情
    if template_id:
        resp = make_request("GET", f"/api/step-templates/{template_id}", token=auth_tokens["admin"])
        log_test(module, "获取模板详情", "PASS" if resp.status_code == 200 else "FAIL", f"状态码: {resp.status_code}")

    # 4. 更新模板
    if template_id:
        resp = make_request("PUT", f"/api/step-templates/{template_id}", token=auth_tokens["admin"], data={
            "name": f"更新模板_{int(time.time())}"
        })
        log_test(module, "更新模板", "PASS" if resp.status_code == 200 else "FAIL", f"状态码: {resp.status_code}")

    # 5. 获取不存在模板
    resp = make_request("GET", "/api/step-templates/99999", token=auth_tokens["admin"])
    log_test(module, "获取不存在模板", "PASS" if resp.status_code == 404 else "FAIL", f"状态码: {resp.status_code}")

    # 6. 确保默认模板存在
    resp = make_request("POST", "/api/step-templates/ensure-default", token=auth_tokens["admin"])
    log_test(module, "确保默认模板存在", "PASS" if resp.status_code == 200 else "FAIL", f"状态码: {resp.status_code}")

    # 7. 无Token访问
    resp = make_request("GET", "/api/step-templates/")
    log_test(module, "无Token获取模板", "PASS" if resp.status_code == 401 else "FAIL", f"状态码: {resp.status_code}")

    # 8. 删除模板
    if template_id:
        resp = make_request("DELETE", f"/api/step-templates/{template_id}", token=auth_tokens["admin"])
        log_test(module, "删除模板", "PASS" if resp.status_code == 200 else "FAIL", f"状态码: {resp.status_code}")

    # 9. 删除不存在模板
    resp = make_request("DELETE", "/api/step-templates/99999", token=auth_tokens["admin"])
    log_test(module, "删除不存在模板", "PASS" if resp.status_code == 404 else "FAIL", f"状态码: {resp.status_code}")

    # 10. 创建空模板
    resp = make_request("POST", "/api/step-templates/", token=auth_tokens["admin"], data={})
    log_test(module, "创建空模板", "PASS" if resp.status_code in [400, 422] else "FAIL", f"状态码: {resp.status_code}")


# ==================== 健康检查测试 (8个) ====================
def test_health_check():
    """健康检查测试 - 8个用例"""
    module = "健康检查"
    print(f"\n{'='*50}\n开始测试: {module}\n{'='*50}")

    # 1. 健康检查接口
    resp = make_request("GET", "/health")
    if resp.status_code == 200 and resp.json().get("status") == "ok":
        log_test(module, "健康检查接口", "PASS", "返回ok")
    else:
        log_test(module, "健康检查接口", "FAIL", f"状态码: {resp.status_code}")

    # 2. API根路径
    resp = make_request("GET", "/")
    log_test(module, "API根路径", "PASS" if resp.status_code == 200 else "FAIL", f"状态码: {resp.status_code}")

    # 3. OpenAPI文档
    resp = make_request("GET", "/docs")
    log_test(module, "OpenAPI文档", "PASS" if resp.status_code == 200 else "FAIL", f"状态码: {resp.status_code}")

    # 4. ReDoc文档
    resp = make_request("GET", "/redoc")
    log_test(module, "ReDoc文档", "PASS" if resp.status_code == 200 else "FAIL", f"状态码: {resp.status_code}")

    # 5. OpenAPI JSON
    resp = make_request("GET", "/openapi.json")
    log_test(module, "OpenAPI JSON", "PASS" if resp.status_code == 200 else "FAIL", f"状态码: {resp.status_code}")

    # 6. 响应时间测试
    start = time.time()
    resp = make_request("GET", "/health")
    elapsed = (time.time() - start) * 1000
    log_test(module, "响应时间测试", "PASS" if elapsed < 100 else "FAIL", f"响应时间: {elapsed:.0f}ms")

    # 7. 并发健康检查
    import concurrent.futures
    def check():
        return make_request("GET", "/health").status_code
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(check) for _ in range(5)]
        results = [f.result() for f in futures]
    if all(r == 200 for r in results):
        log_test(module, "并发健康检查", "PASS", "5个并发请求全部成功")
    else:
        log_test(module, "并发健康检查", "FAIL", f"结果: {results}")

    # 8. 健康检查无需认证
    resp = make_request("GET", "/health")
    log_test(module, "健康检查无需认证", "PASS" if resp.status_code == 200 else "FAIL", f"状态码: {resp.status_code}")


# ==================== 主函数 ====================
def main():
    print("\n" + "="*60)
    print("   外包项目管理系统 - API 全面测试 V2")
    print("   目标: 150+ 测试用例")
    print("="*60)
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"后端地址: {BASE_URL}")
    print("="*60)

    # 按模块执行测试
    test_auth_module()          # 10
    test_users_module()         # 10
    test_platforms_module()     # 10
    test_projects_module()      # 15
    test_attachments_module()   # 20
    test_folders_module()       # 10
    test_tags_module()          # 12
    test_todos_module()         # 12
    test_dashboard_module()     # 10
    test_historical_projects_module()  # 12
    test_system_settings_module()      # 10
    test_project_logs_module()  # 10
    test_project_parts_module() # 10
    test_step_templates_module() # 10
    test_health_check()         # 8

    # 更新报告
    update_report()

    # 打印总结
    print("\n" + "="*60)
    print("   测试完成!")
    print("="*60)
    print(f"总用例: {test_results['total']}")
    print(f"通过: {test_results['passed']}")
    print(f"失败: {test_results['failed']}")
    print(f"跳过: {test_results['skipped']}")
    print(f"通过率: {test_results['passed']/max(test_results['total'],1)*100:.1f}%")
    print(f"\n详细报告: {REPORT_FILE}")
    print("="*60)


if __name__ == "__main__":
    main()
