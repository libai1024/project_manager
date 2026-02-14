#!/usr/bin/env python3
"""
API 15 - 健康检查模块测试
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from base_test import TestRunner

def test_health():
    """健康检查模块测试"""
    runner = TestRunner("健康检查", os.path.dirname(os.path.abspath(__file__)))

    print(f"\n{'='*50}")
    print(" API 15 - 健康检查")
    print(f"{'='*50}\n")

    # 健康检查不需要登录

    # 1. 基本健康检查
    resp = runner.request("GET", "/health")
    runner.log("基本健康检查", resp.status_code == 200, f"状态码: {resp.status_code}")

    # 2. 根路径检查
    resp = runner.request("GET", "/")
    runner.log("根路径检查", resp.status_code == 200, f"状态码: {resp.status_code}")

    # 3. API文档访问
    resp = runner.request("GET", "/docs")
    runner.log("API文档访问", resp.status_code == 200, f"状态码: {resp.status_code}")

    # 4. ReDoc文档访问
    resp = runner.request("GET", "/redoc")
    runner.log("ReDoc文档访问", resp.status_code == 200, f"状态码: {resp.status_code}")

    # 5. OpenAPI JSON访问
    resp = runner.request("GET", "/openapi.json")
    runner.log("OpenAPI JSON访问", resp.status_code == 200, f"状态码: {resp.status_code}")

    # 6. 健康检查响应结构验证
    resp = runner.request("GET", "/health")
    if resp.status_code == 200:
        data = resp.json()
        has_status = "status" in data
        runner.log("健康检查响应结构验证", has_status, "包含status字段" if has_status else "缺少status字段")
    else:
        runner.log("健康检查响应结构验证", False, f"状态码: {resp.status_code}")

    # 7. 根路径响应验证
    resp = runner.request("GET", "/")
    if resp.status_code == 200:
        data = resp.json()
        has_message = "message" in data or "version" in data
        runner.log("根路径响应验证", has_message, "包含必要字段")
    else:
        runner.log("根路径响应验证", False, f"状态码: {resp.status_code}")

    # 8. 404路径测试
    resp = runner.request("GET", "/nonexistent-path")
    runner.log("404路径测试", resp.status_code == 404, f"状态码: {resp.status_code}")

    report_file = runner.save_report()
    print(f"\n报告已保存: {report_file}")
    return runner.summary()

if __name__ == "__main__":
    success = test_health()
    sys.exit(0 if success else 1)
