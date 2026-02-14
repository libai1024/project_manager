#!/usr/bin/env python3
"""
外包项目管理系统 - API 全面测试脚本
包含真实数据和 Mock 数据测试
"""
import requests
import json
import time
import os
from datetime import datetime, date
from typing import Optional, Dict, Any, List

# 配置
BASE_URL = "http://localhost:8000"
REPORT_FILE = os.path.join(os.path.dirname(__file__), "api_test_report.md")

# 测试结果存储
test_results = {
    "total": 0,
    "passed": 0,
    "failed": 0,
    "skipped": 0,
    "modules": {}
}

# 认证信息
auth_tokens = {
    "admin": None,
    "user": None
}

# 真实数据 ID 存储（从数据库获取）
real_data = {
    "users": {"admin": 1, "user": 2},
    "platforms": [2, 4, 3, 1],
    "projects": [1, 3, 4, 5, 6],
    "attachments": [1, 2, 9, 10, 11],
    "tags": [7, 6, 3, 2, 1]
}


def log_test(module: str, test_name: str, result: str, detail: str = "", response_data: Any = None):
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
    print(f"{status} [{module}] {test_name}: {result}")
    if detail:
        print(f"   └─ {detail}")


def make_request(method: str, endpoint: str, token: Optional[str] = None,
                 data: Optional[Dict] = None, files: Optional[Dict] = None,
                 params: Optional[Dict] = None, form_data: bool = False) -> requests.Response:
    """发送HTTP请求"""
    url = f"{BASE_URL}{endpoint}"
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    try:
        if method == "GET":
            return requests.get(url, headers=headers, params=params, timeout=30)
        elif method == "POST":
            if files:
                return requests.post(url, headers=headers, data=data, files=files, timeout=60)
            if form_data:
                # 使用表单数据格式 (用于 OAuth2 登录)
                return requests.post(url, headers=headers, data=data, timeout=30)
            return requests.post(url, headers=headers, json=data, timeout=30)
        elif method == "PUT":
            return requests.put(url, headers=headers, json=data, timeout=30)
        elif method == "DELETE":
            return requests.delete(url, headers=headers, timeout=30)
    except requests.exceptions.RequestException as e:
        # 创建一个假的响应对象
        class FakeResponse:
            status_code = 0
            text = str(e)
            def json(self): return {"error": str(e)}
        return FakeResponse()


def update_report():
    """更新测试报告"""
    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        f.write("# API 测试报告\n\n")
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
        f.write(f"| 通过率 | {test_results['passed']/max(test_results['total'],1)*100:.1f}% |\n\n")

        f.write("## 模块统计\n")
        f.write("| 模块 | 总用例 | 通过 | 失败 | 跳过 | 通过率 |\n")
        f.write("|------|--------|------|------|------|--------|\n")
        for module, stats in test_results["modules"].items():
            rate = stats['passed']/max(stats['total'],1)*100
            f.write(f"| {module} | {stats['total']} | {stats['passed']} | {stats['failed']} | {stats['skipped']} | {rate:.1f}% |\n")

        f.write("\n## 详细测试结果\n\n")
        for module, stats in test_results["modules"].items():
            f.write(f"### {module}\n\n")
            for test in stats["tests"]:
                status = "✅" if test["result"] == "PASS" else "❌" if test["result"] == "FAIL" else "⏭️"
                f.write(f"- {status} **{test['name']}** [{test['time']}]\n")
                if test["detail"]:
                    f.write(f"  - {test['detail']}\n")
            f.write("\n")


# ==================== 认证模块测试 ====================
def test_auth_module():
    """认证模块测试"""
    module = "认证模块"
    print(f"\n{'='*50}\n开始测试: {module}\n{'='*50}")

    # 测试1: 管理员登录 - 真实数据 (使用 form_data=True)
    resp = make_request("POST", "/api/auth/login", data={
        "username": "admin",
        "password": "admin123"
    }, form_data=True)
    if resp.status_code == 200:
        data = resp.json()
        auth_tokens["admin"] = data.get("access_token")
        log_test(module, "管理员登录(真实数据)", "PASS", f"获取token: {auth_tokens['admin'][:20]}...")
    else:
        log_test(module, "管理员登录(真实数据)", "FAIL", f"状态码: {resp.status_code}, {resp.text}")

    # 测试2: 普通用户登录 - 真实数据
    resp = make_request("POST", "/api/auth/login", data={
        "username": "bs",
        "password": "bs123456"
    }, form_data=True)
    if resp.status_code == 200:
        data = resp.json()
        auth_tokens["user"] = data.get("access_token")
        log_test(module, "普通用户登录(真实数据)", "PASS", f"获取token: {auth_tokens['user'][:20]}...")
    else:
        log_test(module, "普通用户登录(真实数据)", "FAIL", f"状态码: {resp.status_code}")

    # 测试3: 错误密码登录 - Mock数据
    resp = make_request("POST", "/api/auth/login", data={
        "username": "admin",
        "password": "wrongpassword"
    }, form_data=True)
    if resp.status_code == 401:
        log_test(module, "错误密码登录(Mock数据)", "PASS", "正确返回401")
    else:
        log_test(module, "错误密码登录(Mock数据)", "FAIL", f"期望401, 实际: {resp.status_code}")

    # 测试4: 不存在的用户登录 - Mock数据
    resp = make_request("POST", "/api/auth/login", data={
        "username": "nonexistent_user",
        "password": "anypassword"
    }, form_data=True)
    if resp.status_code == 401:
        log_test(module, "不存在用户登录(Mock数据)", "PASS", "正确返回401")
    else:
        log_test(module, "不存在用户登录(Mock数据)", "FAIL", f"期望401, 实际: {resp.status_code}")

    # 测试5: 获取当前用户信息 - 真实数据
    resp = make_request("GET", "/api/auth/me", token=auth_tokens["admin"])
    if resp.status_code == 200 and resp.json().get("username") == "admin":
        log_test(module, "获取当前用户信息(真实数据)", "PASS", f"用户: {resp.json().get('username')}")
    else:
        log_test(module, "获取当前用户信息(真实数据)", "FAIL", f"状态码: {resp.status_code}")

    # 测试6: 无Token访问受保护接口
    resp = make_request("GET", "/api/auth/me")
    if resp.status_code == 401:
        log_test(module, "无Token访问受保护接口", "PASS", "正确返回401")
    else:
        log_test(module, "无Token访问受保护接口", "FAIL", f"期望401, 实际: {resp.status_code}")

    # 测试7: 无效Token访问
    resp = make_request("GET", "/api/auth/me", token="invalid_token_12345")
    if resp.status_code == 401:
        log_test(module, "无效Token访问", "PASS", "正确返回401")
    else:
        log_test(module, "无效Token访问", "FAIL", f"期望401, 实际: {resp.status_code}")

    # 测试8: 刷新Token
    resp = make_request("POST", "/api/auth/login", data={"username": "admin", "password": "admin123"}, form_data=True)
    refresh_token = resp.json().get("refresh_token") if resp.status_code == 200 else None
    if refresh_token:
        resp = make_request("POST", "/api/auth/refresh", data={"refresh_token": refresh_token})
        if resp.status_code == 200 and resp.json().get("access_token"):
            log_test(module, "刷新Token", "PASS", "成功获取新token")
        else:
            log_test(module, "刷新Token", "FAIL", f"状态码: {resp.status_code}")
    else:
        log_test(module, "刷新Token", "SKIP", "无法获取refresh_token")


# ==================== 用户管理模块测试 ====================
def test_users_module():
    """用户管理模块测试"""
    module = "用户管理"
    print(f"\n{'='*50}\n开始测试: {module}\n{'='*50}")

    # 测试1: 获取用户列表 - 管理员
    resp = make_request("GET", "/api/users/", token=auth_tokens["admin"])
    if resp.status_code == 200 and len(resp.json()) >= 2:
        log_test(module, "获取用户列表-管理员(真实数据)", "PASS", f"用户数: {len(resp.json())}")
    else:
        log_test(module, "获取用户列表-管理员(真实数据)", "FAIL", f"状态码: {resp.status_code}")

    # 测试2: 获取用户列表 - 普通用户(应失败)
    resp = make_request("GET", "/api/users/", token=auth_tokens["user"])
    if resp.status_code == 403:
        log_test(module, "获取用户列表-普通用户(权限)", "PASS", "正确返回403")
    else:
        log_test(module, "获取用户列表-普通用户(权限)", "FAIL", f"期望403, 实际: {resp.status_code}")

    # 测试3: 获取指定用户详情 - 真实数据
    resp = make_request("GET", f"/api/users/{real_data['users']['admin']}", token=auth_tokens["admin"])
    if resp.status_code == 200 and resp.json().get("username") == "admin":
        log_test(module, "获取用户详情(真实数据)", "PASS", f"用户: {resp.json().get('username')}")
    else:
        log_test(module, "获取用户详情(真实数据)", "FAIL", f"状态码: {resp.status_code}")

    # 测试4: 获取不存在的用户 - Mock数据
    resp = make_request("GET", "/api/users/99999", token=auth_tokens["admin"])
    if resp.status_code == 404:
        log_test(module, "获取不存在用户(Mock数据)", "PASS", "正确返回404")
    else:
        log_test(module, "获取不存在用户(Mock数据)", "FAIL", f"期望404, 实际: {resp.status_code}")

    # 测试5: 无权限获取用户列表
    resp = make_request("GET", "/api/users/")
    if resp.status_code == 401:
        log_test(module, "无Token获取用户列表", "PASS", "正确返回401")
    else:
        log_test(module, "无Token获取用户列表", "FAIL", f"期望401, 实际: {resp.status_code}")


# ==================== 平台管理模块测试 ====================
def test_platforms_module():
    """平台管理模块测试"""
    module = "平台管理"
    print(f"\n{'='*50}\n开始测试: {module}\n{'='*50}")

    # 测试1: 获取平台列表 - 真实数据
    resp = make_request("GET", "/api/platforms/", token=auth_tokens["admin"])
    if resp.status_code == 200 and len(resp.json()) >= 1:
        log_test(module, "获取平台列表(真实数据)", "PASS", f"平台数: {len(resp.json())}")
    else:
        log_test(module, "获取平台列表(真实数据)", "FAIL", f"状态码: {resp.status_code}")

    # 测试2: 获取指定平台详情 - 真实数据
    platform_id = real_data["platforms"][0]
    resp = make_request("GET", f"/api/platforms/{platform_id}", token=auth_tokens["admin"])
    if resp.status_code == 200:
        log_test(module, "获取平台详情(真实数据)", "PASS", f"平台ID: {platform_id}")
    else:
        log_test(module, "获取平台详情(真实数据)", "FAIL", f"状态码: {resp.status_code}")

    # 测试3: 创建平台 - Mock数据
    resp = make_request("POST", "/api/platforms/", token=auth_tokens["admin"], data={
        "name": f"测试平台_{int(time.time())}",
        "description": "API测试创建的平台"
    })
    if resp.status_code == 200:
        new_platform_id = resp.json().get("id")
        real_data["platforms"].append(new_platform_id)
        log_test(module, "创建平台(Mock数据)", "PASS", f"新平台ID: {new_platform_id}")
    else:
        log_test(module, "创建平台(Mock数据)", "FAIL", f"状态码: {resp.status_code}, {resp.text}")

    # 测试4: 更新平台 - Mock数据
    if len(real_data["platforms"]) > 0:
        resp = make_request("PUT", f"/api/platforms/{real_data['platforms'][0]}", token=auth_tokens["admin"], data={
            "name": f"更新平台_{int(time.time())}"
        })
        if resp.status_code == 200:
            log_test(module, "更新平台(Mock数据)", "PASS", f"更新平台ID: {real_data['platforms'][0]}")
        else:
            log_test(module, "更新平台(Mock数据)", "FAIL", f"状态码: {resp.status_code}")

    # 测试5: 获取不存在的平台 - Mock数据
    resp = make_request("GET", "/api/platforms/99999", token=auth_tokens["admin"])
    if resp.status_code == 404:
        log_test(module, "获取不存在平台(Mock数据)", "PASS", "正确返回404")
    else:
        log_test(module, "获取不存在平台(Mock数据)", "FAIL", f"期望404, 实际: {resp.status_code}")


# ==================== 项目管理模块测试 ====================
def test_projects_module():
    """项目管理模块测试"""
    module = "项目管理"
    print(f"\n{'='*50}\n开始测试: {module}\n{'='*50}")

    # 测试1: 获取项目列表 - 真实数据
    resp = make_request("GET", "/api/projects/", token=auth_tokens["admin"])
    if resp.status_code == 200:
        projects = resp.json()
        log_test(module, "获取项目列表(真实数据)", "PASS", f"项目数: {len(projects)}")
    else:
        log_test(module, "获取项目列表(真实数据)", "FAIL", f"状态码: {resp.status_code}")

    # 测试2: 获取指定项目详情 - 真实数据
    project_id = real_data["projects"][0]
    resp = make_request("GET", f"/api/projects/{project_id}", token=auth_tokens["admin"])
    if resp.status_code == 200:
        log_test(module, "获取项目详情(真实数据)", "PASS", f"项目: {resp.json().get('title', '')[:30]}")
    else:
        log_test(module, "获取项目详情(真实数据)", "FAIL", f"状态码: {resp.status_code}")

    # 测试3: 按状态筛选项目 - 真实数据
    resp = make_request("GET", "/api/projects/", token=auth_tokens["admin"], params={"status": "进行中"})
    if resp.status_code == 200:
        log_test(module, "按状态筛选项目(真实数据)", "PASS", f"进行中项目数: {len(resp.json())}")
    else:
        log_test(module, "按状态筛选项目(真实数据)", "FAIL", f"状态码: {resp.status_code}")

    # 测试4: 创建项目 - Mock数据
    resp = make_request("POST", "/api/projects/", token=auth_tokens["admin"], data={
        "title": f"测试项目_{int(time.time())}",
        "student_name": "测试学生",
        "platform_id": real_data["platforms"][0] if real_data["platforms"] else 1,
        "price": 1000.0
    })
    if resp.status_code == 200:
        new_project_id = resp.json().get("id")
        real_data["projects"].append(new_project_id)
        log_test(module, "创建项目(Mock数据)", "PASS", f"新项目ID: {new_project_id}")
    else:
        log_test(module, "创建项目(Mock数据)", "FAIL", f"状态码: {resp.status_code}, {resp.text}")

    # 测试5: 更新项目 - Mock数据
    if len(real_data["projects"]) > 0:
        resp = make_request("PUT", f"/api/projects/{real_data['projects'][0]}", token=auth_tokens["admin"], data={
            "title": f"更新项目_{int(time.time())}"
        })
        if resp.status_code == 200:
            log_test(module, "更新项目(Mock数据)", "PASS")
        else:
            log_test(module, "更新项目(Mock数据)", "FAIL", f"状态码: {resp.status_code}")

    # 测试6: 获取不存在的项目
    resp = make_request("GET", "/api/projects/99999", token=auth_tokens["admin"])
    if resp.status_code == 404:
        log_test(module, "获取不存在项目(Mock数据)", "PASS", "正确返回404")
    else:
        log_test(module, "获取不存在项目(Mock数据)", "FAIL", f"期望404, 实际: {resp.status_code}")

    # 测试7: 按用户筛选项目
    resp = make_request("GET", "/api/projects/", token=auth_tokens["admin"], params={"user_id": real_data["users"]["user"]})
    if resp.status_code == 200:
        log_test(module, "按用户筛选项目(真实数据)", "PASS", f"该用户项目数: {len(resp.json())}")
    else:
        log_test(module, "按用户筛选项目(真实数据)", "FAIL", f"状态码: {resp.status_code}")


# ==================== 附件管理模块测试 ====================
def test_attachments_module():
    """附件管理模块测试"""
    module = "附件管理"
    print(f"\n{'='*50}\n开始测试: {module}\n{'='*50}")

    # 测试1: 获取项目附件列表 - 真实数据
    project_id = real_data["projects"][0]
    resp = make_request("GET", f"/api/attachments/project/{project_id}", token=auth_tokens["admin"])
    if resp.status_code == 200:
        log_test(module, "获取项目附件列表(真实数据)", "PASS", f"附件数: {len(resp.json())}")
    else:
        log_test(module, "获取项目附件列表(真实数据)", "FAIL", f"状态码: {resp.status_code}")

    # 测试2: 获取附件详情 - 真实数据
    if len(real_data["attachments"]) > 0:
        attachment_id = real_data["attachments"][0]
        resp = make_request("GET", f"/api/attachments/{attachment_id}", token=auth_tokens["admin"])
        if resp.status_code == 200:
            log_test(module, "获取附件详情(真实数据)", "PASS", f"文件名: {resp.json().get('file_name', '')[:30]}")
        else:
            log_test(module, "获取附件详情(真实数据)", "FAIL", f"状态码: {resp.status_code}")

    # 测试3: 下载附件 - 真实数据
    if len(real_data["attachments"]) > 0:
        attachment_id = real_data["attachments"][0]
        resp = make_request("GET", f"/api/attachments/{attachment_id}/download", token=auth_tokens["admin"])
        if resp.status_code == 200:
            content_type = resp.headers.get("Content-Type", "")
            log_test(module, "下载附件(真实数据)", "PASS", f"Content-Type: {content_type}")
        else:
            log_test(module, "下载附件(真实数据)", "FAIL", f"状态码: {resp.status_code}")

    # 测试4: 预览附件 - 真实数据
    if len(real_data["attachments"]) > 0:
        attachment_id = real_data["attachments"][0]
        resp = make_request("GET", f"/api/attachments/{attachment_id}/preview", token=auth_tokens["admin"])
        if resp.status_code == 200:
            log_test(module, "预览附件(真实数据)", "PASS", f"状态码: {resp.status_code}")
        else:
            log_test(module, "预览附件(真实数据)", "FAIL", f"状态码: {resp.status_code}")

    # 测试5: 批量获取附件 - 真实数据
    if len(real_data["attachments"]) >= 2:
        resp = make_request("POST", "/api/attachments/batch", token=auth_tokens["admin"], data=real_data["attachments"][:3])
        if resp.status_code == 200:
            log_test(module, "批量获取附件(真实数据)", "PASS", f"获取数量: {len(resp.json())}")
        else:
            log_test(module, "批量获取附件(真实数据)", "FAIL", f"状态码: {resp.status_code}")

    # 测试6: 获取不存在的附件
    resp = make_request("GET", "/api/attachments/99999", token=auth_tokens["admin"])
    if resp.status_code == 404:
        log_test(module, "获取不存在附件(Mock数据)", "PASS", "正确返回404")
    else:
        log_test(module, "获取不存在附件(Mock数据)", "FAIL", f"期望404, 实际: {resp.status_code}")


# ==================== 标签管理模块测试 ====================
def test_tags_module():
    """标签管理模块测试"""
    module = "标签管理"
    print(f"\n{'='*50}\n开始测试: {module}\n{'='*50}")

    # 测试1: 获取标签列表 - 真实数据
    resp = make_request("GET", "/api/tags/", token=auth_tokens["admin"])
    if resp.status_code == 200:
        log_test(module, "获取标签列表(真实数据)", "PASS", f"标签数: {len(resp.json())}")
    else:
        log_test(module, "获取标签列表(真实数据)", "FAIL", f"状态码: {resp.status_code}")

    # 测试2: 获取常用标签(无需认证)
    resp = make_request("GET", "/api/tags/common")
    if resp.status_code == 200:
        log_test(module, "获取常用标签(公开)", "PASS", f"标签数: {len(resp.json())}")
    else:
        log_test(module, "获取常用标签(公开)", "FAIL", f"状态码: {resp.status_code}")

    # 测试3: 创建标签 - Mock数据
    resp = make_request("POST", "/api/tags/", token=auth_tokens["admin"], data={
        "name": f"测试标签_{int(time.time())}",
        "color": "#FF5733"
    })
    if resp.status_code == 200:
        new_tag_id = resp.json().get("id")
        real_data["tags"].append(new_tag_id)
        log_test(module, "创建标签(Mock数据)", "PASS", f"新标签ID: {new_tag_id}")
    else:
        log_test(module, "创建标签(Mock数据)", "FAIL", f"状态码: {resp.status_code}")

    # 测试4: 获取指定标签详情 - 真实数据
    if len(real_data["tags"]) > 0:
        tag_id = real_data["tags"][0]
        resp = make_request("GET", f"/api/tags/{tag_id}", token=auth_tokens["admin"])
        if resp.status_code == 200:
            log_test(module, "获取标签详情(真实数据)", "PASS", f"标签名: {resp.json().get('name')}")
        else:
            log_test(module, "获取标签详情(真实数据)", "FAIL", f"状态码: {resp.status_code}")

    # 测试5: 为项目添加标签 - 真实数据
    if len(real_data["projects"]) > 0 and len(real_data["tags"]) > 0:
        resp = make_request("POST", f"/api/tags/project/{real_data['projects'][0]}/tags",
                           token=auth_tokens["admin"], params={"tag_id": real_data["tags"][0]})
        if resp.status_code in [200, 400]:  # 400可能是已存在
            log_test(module, "为项目添加标签(真实数据)", "PASS", f"状态码: {resp.status_code}")
        else:
            log_test(module, "为项目添加标签(真实数据)", "FAIL", f"状态码: {resp.status_code}")

    # 测试6: 获取不存在的标签
    resp = make_request("GET", "/api/tags/99999", token=auth_tokens["admin"])
    if resp.status_code == 404:
        log_test(module, "获取不存在标签(Mock数据)", "PASS", "正确返回404")
    else:
        log_test(module, "获取不存在标签(Mock数据)", "FAIL", f"期望404, 实际: {resp.status_code}")


# ==================== 待办管理模块测试 ====================
def test_todos_module():
    """待办管理模块测试"""
    module = "待办管理"
    print(f"\n{'='*50}\n开始测试: {module}\n{'='*50}")

    # 测试1: 获取今日待办 - 真实数据
    resp = make_request("GET", "/api/todos/", token=auth_tokens["admin"])
    if resp.status_code == 200:
        log_test(module, "获取今日待办(真实数据)", "PASS", f"待办数: {len(resp.json())}")
    else:
        log_test(module, "获取今日待办(真实数据)", "FAIL", f"状态码: {resp.status_code}")

    # 测试2: 创建待办 - Mock数据
    resp = make_request("POST", "/api/todos/", token=auth_tokens["admin"], data={
        "title": f"测试待办_{int(time.time())}",
        "target_date": str(date.today()),
        "estimated_income": 500.0
    })
    if resp.status_code == 200:
        log_test(module, "创建待办(Mock数据)", "PASS", f"待办ID: {resp.json().get('id')}")
    else:
        log_test(module, "创建待办(Mock数据)", "FAIL", f"状态码: {resp.status_code}")

    # 测试3: 获取日历数据 - 真实数据
    today = date.today()
    resp = make_request("GET", "/api/todos/calendar", token=auth_tokens["admin"],
                       params={"year": today.year, "month": today.month})
    if resp.status_code == 200:
        log_test(module, "获取日历数据(真实数据)", "PASS", f"数据条数: {len(resp.json())}")
    else:
        log_test(module, "获取日历数据(真实数据)", "FAIL", f"状态码: {resp.status_code}")

    # 测试4: 按日期获取待办 - 真实数据
    resp = make_request("GET", "/api/todos/", token=auth_tokens["admin"],
                       params={"target_date": str(date.today())})
    if resp.status_code == 200:
        log_test(module, "按日期获取待办(真实数据)", "PASS", f"待办数: {len(resp.json())}")
    else:
        log_test(module, "按日期获取待办(真实数据)", "FAIL", f"状态码: {resp.status_code}")

    # 测试5: 无权限访问
    resp = make_request("GET", "/api/todos/")
    if resp.status_code == 401:
        log_test(module, "无Token获取待办", "PASS", "正确返回401")
    else:
        log_test(module, "无Token获取待办", "FAIL", f"期望401, 实际: {resp.status_code}")


# ==================== Dashboard模块测试 ====================
def test_dashboard_module():
    """Dashboard模块测试"""
    module = "Dashboard"
    print(f"\n{'='*50}\n开始测试: {module}\n{'='*50}")

    # 测试1: 获取统计数据 - 真实数据
    resp = make_request("GET", "/api/dashboard/stats", token=auth_tokens["admin"])
    if resp.status_code == 200:
        data = resp.json()
        log_test(module, "获取统计数据(真实数据)", "PASS", f"包含字段: {list(data.keys())[:5]}")
    else:
        log_test(module, "获取统计数据(真实数据)", "FAIL", f"状态码: {resp.status_code}")

    # 测试2: 统计数据结构验证
    resp = make_request("GET", "/api/dashboard/stats", token=auth_tokens["admin"])
    if resp.status_code == 200:
        data = resp.json()
        required_fields = ["total_projects", "completed_projects", "in_progress_projects"]
        if all(field in data for field in required_fields):
            log_test(module, "统计数据结构验证", "PASS", "包含必要字段")
        else:
            log_test(module, "统计数据结构验证", "FAIL", "缺少必要字段")

    # 测试3: 普通用户访问Dashboard
    resp = make_request("GET", "/api/dashboard/stats", token=auth_tokens["user"])
    if resp.status_code == 200:
        log_test(module, "普通用户访问Dashboard", "PASS", "可以访问")
    else:
        log_test(module, "普通用户访问Dashboard", "FAIL", f"状态码: {resp.status_code}")

    # 测试4: 无权限访问
    resp = make_request("GET", "/api/dashboard/stats")
    if resp.status_code == 401:
        log_test(module, "无Token访问Dashboard", "PASS", "正确返回401")
    else:
        log_test(module, "无Token访问Dashboard", "FAIL", f"期望401, 实际: {resp.status_code}")

    # 测试5: 数据一致性检查
    resp = make_request("GET", "/api/dashboard/stats", token=auth_tokens["admin"])
    if resp.status_code == 200:
        data = resp.json()
        total = data.get("total_projects", 0)
        completed = data.get("completed_projects", 0)
        in_progress = data.get("in_progress_projects", 0)
        if total >= completed + in_progress:
            log_test(module, "数据一致性检查", "PASS", f"总数({total}) >= 完成({completed}) + 进行中({in_progress})")
        else:
            log_test(module, "数据一致性检查", "FAIL", "数据不一致")


# ==================== 历史项目模块测试 ====================
def test_historical_projects_module():
    """历史项目模块测试"""
    module = "历史项目"
    print(f"\n{'='*50}\n开始测试: {module}\n{'='*50}")

    # 测试1: 获取历史项目列表
    resp = make_request("GET", "/api/historical-projects/", token=auth_tokens["admin"])
    if resp.status_code == 200:
        log_test(module, "获取历史项目列表(真实数据)", "PASS", f"项目数: {len(resp.json())}")
    else:
        log_test(module, "获取历史项目列表(真实数据)", "FAIL", f"状态码: {resp.status_code}")

    # 测试2: 获取历史项目总数
    resp = make_request("GET", "/api/historical-projects/count", token=auth_tokens["admin"])
    if resp.status_code == 200:
        log_test(module, "获取历史项目总数(真实数据)", "PASS", f"总数: {resp.json().get('count', 0)}")
    else:
        log_test(module, "获取历史项目总数(真实数据)", "FAIL", f"状态码: {resp.status_code}")

    # 测试3: 创建历史项目 - Mock数据
    resp = make_request("POST", "/api/historical-projects/", token=auth_tokens["admin"], data={
        "title": f"测试历史项目_{int(time.time())}",
        "student_name": "测试学生",
        "platform_id": real_data["platforms"][0] if real_data["platforms"] else None,
        "price": 800.0,
        "status": "已完成"
    })
    if resp.status_code == 200:
        log_test(module, "创建历史项目(Mock数据)", "PASS", f"项目ID: {resp.json().get('id')}")
    else:
        log_test(module, "创建历史项目(Mock数据)", "FAIL", f"状态码: {resp.status_code}")

    # 测试4: 按状态筛选
    resp = make_request("GET", "/api/historical-projects/", token=auth_tokens["admin"],
                       params={"status": "已完成"})
    if resp.status_code == 200:
        log_test(module, "按状态筛选历史项目(真实数据)", "PASS", f"已完成项目数: {len(resp.json())}")
    else:
        log_test(module, "按状态筛选历史项目(真实数据)", "FAIL", f"状态码: {resp.status_code}")

    # 测试5: 搜索历史项目
    resp = make_request("GET", "/api/historical-projects/", token=auth_tokens["admin"],
                       params={"search": "RFID"})
    if resp.status_code == 200:
        log_test(module, "搜索历史项目(真实数据)", "PASS", f"搜索结果数: {len(resp.json())}")
    else:
        log_test(module, "搜索历史项目(真实数据)", "FAIL", f"状态码: {resp.status_code}")

    # 测试6: 获取不存在的历史项目
    resp = make_request("GET", "/api/historical-projects/99999", token=auth_tokens["admin"])
    if resp.status_code == 404:
        log_test(module, "获取不存在历史项目(Mock数据)", "PASS", "正确返回404")
    else:
        log_test(module, "获取不存在历史项目(Mock数据)", "FAIL", f"期望404, 实际: {resp.status_code}")


# ==================== 系统设置模块测试 ====================
def test_system_settings_module():
    """系统设置模块测试"""
    module = "系统设置"
    print(f"\n{'='*50}\n开始测试: {module}\n{'='*50}")

    # 测试1: 获取Token持续时间设置
    resp = make_request("GET", "/api/system-settings/token-duration", token=auth_tokens["admin"])
    if resp.status_code == 200:
        log_test(module, "获取Token持续时间设置(真实数据)", "PASS", f"数据: {resp.json()}")
    else:
        log_test(module, "获取Token持续时间设置(真实数据)", "FAIL", f"状态码: {resp.status_code}")

    # 测试2: 获取所有系统设置
    resp = make_request("GET", "/api/system-settings/", token=auth_tokens["admin"])
    if resp.status_code == 200:
        log_test(module, "获取所有系统设置(真实数据)", "PASS", f"设置数: {len(resp.json())}")
    else:
        log_test(module, "获取所有系统设置(真实数据)", "FAIL", f"状态码: {resp.status_code}")

    # 测试3: 获取插件设置
    resp = make_request("GET", "/api/system-settings/plugin-settings", token=auth_tokens["admin"])
    if resp.status_code == 200:
        log_test(module, "获取插件设置(真实数据)", "PASS")
    else:
        log_test(module, "获取插件设置(真实数据)", "FAIL", f"状态码: {resp.status_code}")

    # 测试4: 普通用户访问(部分接口)
    resp = make_request("GET", "/api/system-settings/token-duration", token=auth_tokens["user"])
    if resp.status_code in [200, 403]:
        log_test(module, "普通用户访问系统设置", "PASS", f"状态码: {resp.status_code}")
    else:
        log_test(module, "普通用户访问系统设置", "FAIL", f"状态码: {resp.status_code}")

    # 测试5: 无权限访问
    resp = make_request("GET", "/api/system-settings/")
    if resp.status_code == 401:
        log_test(module, "无Token访问系统设置", "PASS", "正确返回401")
    else:
        log_test(module, "无Token访问系统设置", "FAIL", f"期望401, 实际: {resp.status_code}")


# ==================== 健康检查测试 ====================
def test_health_check():
    """健康检查测试"""
    module = "健康检查"
    print(f"\n{'='*50}\n开始测试: {module}\n{'='*50}")

    # 测试1: 健康检查接口
    resp = make_request("GET", "/health")
    if resp.status_code == 200 and resp.json().get("status") == "ok":
        log_test(module, "健康检查接口", "PASS", "返回ok")
    else:
        log_test(module, "健康检查接口", "FAIL", f"状态码: {resp.status_code}")

    # 测试2: API根路径
    resp = make_request("GET", "/")
    if resp.status_code == 200:
        log_test(module, "API根路径", "PASS", "可访问")
    else:
        log_test(module, "API根路径", "FAIL", f"状态码: {resp.status_code}")

    # 测试3: OpenAPI文档
    resp = make_request("GET", "/docs")
    if resp.status_code == 200:
        log_test(module, "OpenAPI文档", "PASS", "可访问")
    else:
        log_test(module, "OpenAPI文档", "FAIL", f"状态码: {resp.status_code}")

    # 测试4: ReDoc文档
    resp = make_request("GET", "/redoc")
    if resp.status_code == 200:
        log_test(module, "ReDoc文档", "PASS", "可访问")
    else:
        log_test(module, "ReDoc文档", "FAIL", f"状态码: {resp.status_code}")

    # 测试5: 响应时间测试
    start = time.time()
    resp = make_request("GET", "/health")
    elapsed = time.time() - start
    if elapsed < 1.0:
        log_test(module, "响应时间测试", "PASS", f"响应时间: {elapsed*1000:.0f}ms")
    else:
        log_test(module, "响应时间测试", "FAIL", f"响应时间过长: {elapsed*1000:.0f}ms")


# ==================== 主函数 ====================
def main():
    print("\n" + "="*60)
    print("   外包项目管理系统 - API 全面测试")
    print("="*60)
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"后端地址: {BASE_URL}")
    print("="*60)

    # 按模块执行测试
    test_auth_module()
    test_users_module()
    test_platforms_module()
    test_projects_module()
    test_attachments_module()
    test_tags_module()
    test_todos_module()
    test_dashboard_module()
    test_historical_projects_module()
    test_system_settings_module()
    test_health_check()

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
