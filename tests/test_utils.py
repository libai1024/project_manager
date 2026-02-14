#!/usr/bin/env python3
"""
测试工具模块 - 公共函数和配置
"""
import requests
import json
import time
import os
from datetime import datetime, date
from typing import Optional, Dict, Any, List

# 配置
BASE_URL = "http://localhost:8000"
REPORT_DIR = os.path.join(os.path.dirname(__file__), "reports")

# 确保报告目录存在
os.makedirs(REPORT_DIR, exist_ok=True)

# 全局测试结果
test_results = {
    "total": 0,
    "passed": 0,
    "failed": 0,
    "skipped": 0
}

# 认证Token
auth_tokens = {"admin": None, "user": None}

# 真实数据ID
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

# 测试创建的数据
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
    if result == "PASS":
        test_results["passed"] += 1
    elif result == "FAIL":
        test_results["failed"] += 1
    else:
        test_results["skipped"] += 1

    status = "✅" if result == "PASS" else "❌" if result == "FAIL" else "⏭️"
    print(f"{status} {test_name}")
    if detail:
        print(f"   └─ {detail[:100]}")


def extract_data(resp: requests.Response) -> Any:
    """从响应中提取data字段（处理嵌套响应结构）"""
    try:
        json_data = resp.json()
        if isinstance(json_data, dict) and "data" in json_data:
            return json_data["data"]
        return json_data
    except:
        return resp.json()


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
            return requests.get(url, headers=headers, params=params, timeout=60)
        elif method == "POST":
            if files:
                return requests.post(url, headers=headers, data=data, files=files, timeout=120)
            elif form_data:
                return requests.post(url, headers=headers, data=data, timeout=30)
            else:
                return requests.post(url, headers=headers, json=data, timeout=30)
        elif method == "PUT":
            return requests.put(url, headers=headers, json=data, timeout=30)
        elif method == "DELETE":
            return requests.delete(url, headers=headers, timeout=30)
    except Exception as e:
        class FakeResponse:
            status_code = 0
            text = str(e)
            content = b""
            headers = {}
            def json(self): return {"error": str(e)}
        return FakeResponse()


def get_admin_token() -> str:
    """获取管理员Token"""
    if auth_tokens["admin"]:
        return auth_tokens["admin"]

    resp = make_request("POST", "/api/auth/login", data={
        "username": "admin",
        "password": "admin123"
    }, form_data=True)

    if resp.status_code == 200:
        auth_tokens["admin"] = resp.json().get("access_token")
        return auth_tokens["admin"]
    return None


def save_report(module: str, tests: List[Dict]):
    """保存模块测试报告"""
    report_file = os.path.join(REPORT_DIR, f"{module}_report.md")

    passed = sum(1 for t in tests if t["result"] == "PASS")
    failed = sum(1 for t in tests if t["result"] == "FAIL")
    skipped = sum(1 for t in tests if t["result"] == "SKIP")
    total = len(tests)

    with open(report_file, "w", encoding="utf-8") as f:
        f.write(f"# {module} 模块测试报告\n\n")
        f.write(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("## 统计\n\n")
        f.write(f"| 指标 | 数量 |\n")
        f.write(f"|------|------|\n")
        f.write(f"| 总用例 | {total} |\n")
        f.write(f"| 通过 | {passed} |\n")
        f.write(f"| 失败 | {failed} |\n")
        f.write(f"| 跳过 | {skipped} |\n")
        f.write(f"| 通过率 | {passed/max(total,1)*100:.1f}% |\n\n")
        f.write("## 详细结果\n\n")
        for t in tests:
            status = "✅" if t["result"] == "PASS" else "❌" if t["result"] == "FAIL" else "⏭️"
            f.write(f"- {status} **{t['name']}**\n")
            if t.get("detail"):
                f.write(f"  - {t['detail']}\n")
        f.write("\n")


def print_module_header(module: str, total_tests: int):
    """打印模块测试头部"""
    print(f"\n{'='*50}")
    print(f" {module} (目标: {total_tests}个用例)")
    print(f"{'='*50}")


def print_module_summary(module: str, passed: int, failed: int, skipped: int):
    """打印模块测试总结"""
    total = passed + failed + skipped
    rate = passed / max(total, 1) * 100
    print(f"\n{module} 完成: {passed}/{total} 通过 ({rate:.1f}%)")
