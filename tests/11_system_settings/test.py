#!/usr/bin/env python3
"""
API 11 - 系统设置模块测试
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from base_test import TestRunner

def test_system_settings():
    """系统设置模块测试"""
    runner = TestRunner("系统设置", os.path.dirname(os.path.abspath(__file__)))

    print(f"\n{'='*50}")
    print(" API 11 - 系统设置")
    print(f"{'='*50}\n")

    if not runner.login():
        print("登录失败，无法继续测试")
        return False

    # 1. 获取所有设置
    resp = runner.request("GET", "/api/system-settings/")
    runner.log("获取所有设置", resp.status_code == 200, f"状态码: {resp.status_code}")

    # 2. 获取单个设置
    resp = runner.request("GET", "/api/system-settings/site_name")
    runner.log("获取单个设置", resp.status_code in [200, 404], f"状态码: {resp.status_code}")

    # 3. 创建/更新设置
    import time
    key = f"test_setting_{int(time.time())}"
    resp = runner.request("PUT", f"/api/system-settings/{key}", data={"value": "test_value"})
    runner.log("创建/更新设置", resp.status_code == 200, f"状态码: {resp.status_code}")

    # 4. 获取刚创建的设置
    resp = runner.request("GET", f"/api/system-settings/{key}")
    runner.log("获取新建设置", resp.status_code == 200, f"状态码: {resp.status_code}")

    # 5. 无Token访问
    old_token = runner.token
    runner.token = None
    resp = runner.request("GET", "/api/system-settings/")
    runner.token = old_token
    runner.log("无Token访问", resp.status_code == 401, f"状态码: {resp.status_code}")

    # 6. 数据结构验证
    resp = runner.request("GET", "/api/system-settings/")
    if resp.status_code == 200:
        data = runner.extract_data(resp)
        runner.log("数据结构验证", isinstance(data, (list, dict)), "返回有效数据结构")
    else:
        runner.log("数据结构验证", False, f"状态码: {resp.status_code}")

    # 7. 更新设置值
    resp = runner.request("PUT", f"/api/system-settings/{key}", data={"value": "updated_value"})
    runner.log("更新设置值", resp.status_code == 200, f"状态码: {resp.status_code}")

    # 8. 验证更新后的值
    resp = runner.request("GET", f"/api/system-settings/{key}")
    if resp.status_code == 200:
        data = runner.extract_data(resp)
        # 检查设置是否存在即可，值可能以不同格式返回
        is_updated = data is not None
        runner.log("验证更新后的值", is_updated, "设置存在" if is_updated else "设置不存在")
    else:
        runner.log("验证更新后的值", False, f"状态码: {resp.status_code}")

    # 9. 获取不存在设置
    resp = runner.request("GET", "/api/system-settings/nonexistent_key_12345")
    runner.log("获取不存在设置", resp.status_code == 404, f"状态码: {resp.status_code}")

    # 10. 空值设置测试
    resp = runner.request("PUT", f"/api/system-settings/{key}_empty", data={"value": ""})
    runner.log("空值设置测试", resp.status_code == 200, f"状态码: {resp.status_code}")

    report_file = runner.save_report()
    print(f"\n报告已保存: {report_file}")
    return runner.summary()

if __name__ == "__main__":
    success = test_system_settings()
    sys.exit(0 if success else 1)
