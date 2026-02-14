#!/usr/bin/env python3
"""
API 03 - 平台管理模块测试
测试用例: 10个
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from base_test import TestRunner

def test_platforms():
    """平台管理模块测试"""
    runner = TestRunner("平台管理", os.path.dirname(os.path.abspath(__file__)))

    print(f"\n{'='*50}")
    print(" API 03 - 平台管理")
    print(f"{'='*50}\n")

    # 登录
    if not runner.login():
        print("登录失败，无法继续测试")
        return False

    # 1. 获取平台列表
    resp = runner.request("GET", "/api/platforms/")
    if resp.status_code == 200:
        platforms = runner.extract_data(resp)
        runner.real_data["platforms"] = platforms
        runner.log("获取平台列表", True, f"平台数: {len(platforms) if platforms else 0}")
    else:
        runner.log("获取平台列表", False, f"状态码: {resp.status_code}")

    # 2. 创建测试平台
    import time
    platform_name = f"测试平台_{int(time.time())}"
    resp = runner.request("POST", "/api/platforms/", data={"name": platform_name})
    if resp.status_code == 200:
        data = runner.extract_data(resp)
        if data:
            runner.real_data["test_platform_id"] = data.get("id")
            runner.log("创建测试平台", True, f"平台ID: {data.get('id')}, 名称: {platform_name}")
        else:
            runner.log("创建测试平台", False, "响应数据为空")
    else:
        runner.log("创建测试平台", False, f"状态码: {resp.status_code}")

    # 3. 获取平台详情
    platform_id = runner.real_data.get("test_platform_id")
    if platform_id:
        resp = runner.request("GET", f"/api/platforms/{platform_id}")
        if resp.status_code == 200:
            data = runner.extract_data(resp)
            runner.log("获取平台详情", True, f"名称: {data.get('name') if data else 'N/A'}")
        else:
            runner.log("获取平台详情", False, f"状态码: {resp.status_code}")
    else:
        runner.skip("获取平台详情", "无测试平台ID")

    # 4. 更新平台信息
    if platform_id:
        resp = runner.request("PUT", f"/api/platforms/{platform_id}", data={"name": f"更新_{platform_name}"})
        runner.log("更新平台信息", resp.status_code == 200, f"状态码: {resp.status_code}")
    else:
        runner.skip("更新平台信息", "无测试平台ID")

    # 5. 获取不存在的平台
    resp = runner.request("GET", "/api/platforms/99999")
    runner.log("获取不存在平台", resp.status_code == 404, f"状态码: {resp.status_code}")

    # 6. 无Token访问
    old_token = runner.token
    runner.token = None
    resp = runner.request("GET", "/api/platforms/")
    runner.token = old_token
    runner.log("无Token访问", resp.status_code == 401, f"状态码: {resp.status_code}")

    # 7. 创建空名称平台
    resp = runner.request("POST", "/api/platforms/", data={"name": ""})
    runner.log("创建空名称平台", resp.status_code in [400, 422], f"状态码: {resp.status_code}")

    # 8. 创建超长名称平台
    long_name = "A" * 300
    resp = runner.request("POST", "/api/platforms/", data={"name": long_name})
    runner.log("创建超长名称平台", resp.status_code in [200, 400, 422], f"状态码: {resp.status_code}")

    # 9. 平台数据结构验证
    if platform_id:
        resp = runner.request("GET", f"/api/platforms/{platform_id}")
        if resp.status_code == 200:
            data = runner.extract_data(resp)
            required = ["id", "name"]
            has_all = all(k in data for k in required) if data else False
            runner.log("平台数据结构验证", has_all, "包含必要字段" if has_all else "缺少必要字段")
        else:
            runner.log("平台数据结构验证", False, f"状态码: {resp.status_code}")
    else:
        runner.skip("平台数据结构验证", "无测试平台ID")

    # 10. 删除测试平台（清理）
    if platform_id:
        resp = runner.request("DELETE", f"/api/platforms/{platform_id}")
        runner.log("删除测试平台", resp.status_code == 200, f"状态码: {resp.status_code}")
    else:
        runner.skip("删除测试平台", "无测试平台ID")

    # 11. 删除不存在平台
    resp = runner.request("DELETE", "/api/platforms/99999")
    runner.log("删除不存在平台", resp.status_code == 404, f"状态码: {resp.status_code}")

    # 保存报告
    report_file = runner.save_report()
    print(f"\n报告已保存: {report_file}")

    return runner.summary()


if __name__ == "__main__":
    success = test_platforms()
    sys.exit(0 if success else 1)
