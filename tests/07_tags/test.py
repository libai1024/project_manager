#!/usr/bin/env python3
"""
API 07 - 标签管理模块测试
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from base_test import TestRunner

def test_tags():
    """标签管理模块测试"""
    runner = TestRunner("标签管理", os.path.dirname(os.path.abspath(__file__)))

    print(f"\n{'='*50}")
    print(" API 07 - 标签管理")
    print(f"{'='*50}\n")

    if not runner.login():
        print("登录失败，无法继续测试")
        return False

    # 1. 获取标签列表
    resp = runner.request("GET", "/api/tags/")
    if resp.status_code == 200:
        tags = runner.extract_data(resp)
        runner.real_data["tags"] = tags
        runner.log("获取标签列表", True, f"标签数: {len(tags) if tags else 0}")
    else:
        runner.log("获取标签列表", False, f"状态码: {resp.status_code}")

    # 2. 创建标签
    import time
    tag_name = f"测试标签_{int(time.time())}"
    resp = runner.request("POST", "/api/tags/", data={"name": tag_name, "color": "#ff0000"})
    if resp.status_code == 200:
        data = runner.extract_data(resp)
        runner.real_data["test_tag_id"] = data.get("id") if data else None
        runner.log("创建标签", True, f"ID: {data.get('id') if data else 'N/A'}")
    else:
        runner.log("创建标签", False, f"状态码: {resp.status_code}")

    # 3. 获取标签详情
    tag_id = runner.real_data.get("test_tag_id")
    if tag_id:
        resp = runner.request("GET", f"/api/tags/{tag_id}")
        runner.log("获取标签详情", resp.status_code == 200, f"状态码: {resp.status_code}")
    else:
        runner.skip("获取标签详情", "无测试标签ID")

    # 4. 更新标签
    if tag_id:
        resp = runner.request("PUT", f"/api/tags/{tag_id}", data={"name": f"更新_{tag_name}"})
        runner.log("更新标签", resp.status_code == 200, f"状态码: {resp.status_code}")
    else:
        runner.skip("更新标签", "无测试标签ID")

    # 5. 获取常用标签
    resp = runner.request("GET", "/api/tags/common")
    runner.log("获取常用标签", resp.status_code == 200, f"状态码: {resp.status_code}")

    # 6. 获取不存在标签
    resp = runner.request("GET", "/api/tags/99999")
    runner.log("获取不存在标签", resp.status_code == 404, f"状态码: {resp.status_code}")

    # 7. 无Token访问
    old_token = runner.token
    runner.token = None
    resp = runner.request("GET", "/api/tags/")
    runner.token = old_token
    runner.log("无Token访问", resp.status_code == 401, f"状态码: {resp.status_code}")

    # 8. 创建空名称标签
    resp = runner.request("POST", "/api/tags/", data={"name": ""})
    runner.log("创建空名称标签", resp.status_code in [400, 422], f"状态码: {resp.status_code}")

    # 9. 删除标签
    if tag_id:
        resp = runner.request("DELETE", f"/api/tags/{tag_id}")
        runner.log("删除标签", resp.status_code == 200, f"状态码: {resp.status_code}")
    else:
        runner.skip("删除标签", "无测试标签ID")

    # 10. 删除不存在标签
    resp = runner.request("DELETE", "/api/tags/99999")
    runner.log("删除不存在标签", resp.status_code == 404, f"状态码: {resp.status_code}")

    report_file = runner.save_report()
    print(f"\n报告已保存: {report_file}")
    return runner.summary()

if __name__ == "__main__":
    success = test_tags()
    sys.exit(0 if success else 1)
