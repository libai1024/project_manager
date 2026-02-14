#!/usr/bin/env python3
"""
测试基础模块 - 所有API测试共用
"""
import requests
import json
import time
import os
from datetime import datetime
from typing import Optional, Dict, Any, List

BASE_URL = "http://localhost:8000"

class TestRunner:
    """测试运行器"""

    def __init__(self, module_name: str, module_dir: str):
        self.module_name = module_name
        self.module_dir = module_dir
        self.tests = []
        self.token = None
        self.real_data = {}
        self.created_data = []

    def login(self, username="admin", password="admin123") -> bool:
        """登录获取Token"""
        resp = requests.post(
            f"{BASE_URL}/api/auth/login",
            data={"username": username, "password": password}
        )
        if resp.status_code == 200:
            data = resp.json()
            self.token = data.get("access_token")
            return True
        return False

    def request(self, method: str, endpoint: str, data=None, params=None, files=None, form_data=False):
        """发送请求"""
        url = f"{BASE_URL}{endpoint}"
        headers = {}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"

        try:
            if method == "GET":
                return requests.get(url, headers=headers, params=params, timeout=30)
            elif method == "POST":
                if files:
                    return requests.post(url, headers=headers, data=data, files=files, timeout=60)
                elif form_data:
                    return requests.post(url, headers=headers, data=data, timeout=30)
                return requests.post(url, headers=headers, json=data, timeout=30)
            elif method == "PUT":
                return requests.put(url, headers=headers, json=data, timeout=30)
            elif method == "DELETE":
                return requests.delete(url, headers=headers, timeout=30)
        except Exception as e:
            class FakeResp:
                status_code = 0
                text = str(e)
                content = b""
                def json(self): return {"error": str(e)}
            return FakeResp()

    def extract_data(self, resp):
        """提取响应中的data字段"""
        try:
            json_data = resp.json()
            if isinstance(json_data, dict) and "data" in json_data:
                return json_data["data"]
            return json_data
        except:
            return resp.json()

    def log(self, name: str, passed: bool, detail: str = ""):
        """记录测试结果"""
        result = {
            "name": name,
            "result": "PASS" if passed else "FAIL",
            "detail": detail,
            "time": datetime.now().strftime("%H:%M:%S")
        }
        self.tests.append(result)
        status = "✅" if passed else "❌"
        print(f"{status} {name}")
        if detail:
            print(f"   └─ {detail[:80]}")
        return passed

    def skip(self, name: str, reason: str = ""):
        """跳过测试"""
        result = {
            "name": name,
            "result": "SKIP",
            "detail": reason,
            "time": datetime.now().strftime("%H:%M:%S")
        }
        self.tests.append(result)
        print(f"⏭️ {name}")
        if reason:
            print(f"   └─ {reason[:80]}")

    def save_report(self):
        """保存测试报告"""
        report_dir = os.path.join(self.module_dir, "reports")
        os.makedirs(report_dir, exist_ok=True)
        report_file = os.path.join(report_dir, f"{self.module_name}_report.md")

        passed = sum(1 for t in self.tests if t["result"] == "PASS")
        failed = sum(1 for t in self.tests if t["result"] == "FAIL")
        skipped = sum(1 for t in self.tests if t["result"] == "SKIP")
        total = len(self.tests)

        with open(report_file, "w", encoding="utf-8") as f:
            f.write(f"# {self.module_name} 测试报告\n\n")
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
            for t in self.tests:
                status = "✅" if t["result"] == "PASS" else "❌" if t["result"] == "FAIL" else "⏭️"
                f.write(f"- {status} **{t['name']}** [{t['time']}]\n")
                if t.get("detail"):
                    f.write(f"  - {t['detail']}\n")

        return report_file

    def summary(self):
        """打印测试总结"""
        passed = sum(1 for t in self.tests if t["result"] == "PASS")
        failed = sum(1 for t in self.tests if t["result"] == "FAIL")
        skipped = sum(1 for t in self.tests if t["result"] == "SKIP")
        total = len(self.tests)
        rate = passed / max(total, 1) * 100

        print(f"\n{'='*50}")
        print(f" {self.module_name} 测试完成")
        print(f"{'='*50}")
        print(f" 通过: {passed}/{total} ({rate:.1f}%)")
        print(f" 失败: {failed}")
        print(f" 跳过: {skipped}")

        return failed == 0
