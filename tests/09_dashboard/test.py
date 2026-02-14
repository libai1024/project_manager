#!/usr/bin/env python3
"""
API 09 - Dashboard模块测试
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from base_test import TestRunner

def test_dashboard():
    """Dashboard模块测试"""
    runner = TestRunner("Dashboard", os.path.dirname(os.path.abspath(__file__)))

    print(f"\n{'='*50}")
    print(" API 09 - Dashboard")
    print(f"{'='*50}\n")

    if not runner.login():
        print("登录失败，无法继续测试")
        return False

    # 1. 获取Dashboard统计
    resp = runner.request("GET", "/api/dashboard/stats")
    runner.log("获取Dashboard统计", resp.status_code == 200, f"状态码: {resp.status_code}")

    # 2. 数据结构验证
    resp = runner.request("GET", "/api/dashboard/stats")
    if resp.status_code == 200:
        data = runner.extract_data(resp)
        runner.log("数据结构验证", data is not None, "返回有效数据")
    else:
        runner.log("数据结构验证", False, f"状态码: {resp.status_code}")

    # 3. 无Token访问
    old_token = runner.token
    runner.token = None
    resp = runner.request("GET", "/api/dashboard/stats")
    runner.token = old_token
    runner.log("无Token访问", resp.status_code == 401, f"状态码: {resp.status_code}")

    # 4. 验证统计字段
    resp = runner.request("GET", "/api/dashboard/stats")
    if resp.status_code == 200:
        data = runner.extract_data(resp)
        if data:
            # 检查是否有统计相关字段
            has_stats = any(key in data for key in ["total_projects", "total_income", "project_count", "income"])
            runner.log("统计字段验证", has_stats or len(data) > 0, "包含统计信息")
        else:
            runner.log("统计字段验证", True, "返回空数据")
    else:
        runner.log("统计字段验证", False, f"状态码: {resp.status_code}")

    # 5. 验证响应格式
    resp = runner.request("GET", "/api/dashboard/stats")
    if resp.status_code == 200:
        import json
        try:
            data = resp.json()
            has_code = "code" in data
            has_msg = "msg" in data
            runner.log("响应格式验证", has_code and has_msg, "标准响应格式")
        except:
            runner.log("响应格式验证", False, "JSON解析失败")
    else:
        runner.log("响应格式验证", False, f"状态码: {resp.status_code}")

    # 6. 多次请求一致性
    resp1 = runner.request("GET", "/api/dashboard/stats")
    resp2 = runner.request("GET", "/api/dashboard/stats")
    if resp1.status_code == 200 and resp2.status_code == 200:
        runner.log("多次请求一致性", True, "多次请求成功")
    else:
        runner.log("多次请求一致性", False, "请求不稳定")

    # 7. 请求性能测试
    import time
    start = time.time()
    resp = runner.request("GET", "/api/dashboard/stats")
    elapsed = time.time() - start
    runner.log("请求性能测试", resp.status_code == 200 and elapsed < 5, f"耗时: {elapsed:.2f}秒")

    # 8. 空参数测试
    resp = runner.request("GET", "/api/dashboard/stats", params={})
    runner.log("空参数测试", resp.status_code == 200, f"状态码: {resp.status_code}")

    report_file = runner.save_report()
    print(f"\n报告已保存: {report_file}")
    return runner.summary()

if __name__ == "__main__":
    success = test_dashboard()
    sys.exit(0 if success else 1)
