#!/usr/bin/env python3
"""
API 10 - 历史项目模块测试
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from base_test import TestRunner

def test_historical_projects():
    """历史项目模块测试"""
    runner = TestRunner("历史项目", os.path.dirname(os.path.abspath(__file__)))

    print(f"\n{'='*50}")
    print(" API 10 - 历史项目")
    print(f"{'='*50}\n")

    if not runner.login():
        print("登录失败，无法继续测试")
        return False

    # 获取平台ID
    resp = runner.request("GET", "/api/platforms/")
    platforms = runner.extract_data(resp)
    platform_id = platforms[0]["id"] if platforms else 1

    # 1. 获取历史项目列表
    resp = runner.request("GET", "/api/historical-projects/")
    if resp.status_code == 200:
        projects = runner.extract_data(resp)
        runner.log("获取历史项目列表", True, f"项目数: {len(projects) if projects else 0}")
    else:
        runner.log("获取历史项目列表", False, f"状态码: {resp.status_code}")

    # 2. 创建历史项目
    import time
    title = f"测试历史项目_{int(time.time())}"
    resp = runner.request("POST", "/api/historical-projects/", data={"title": title, "platform_id": platform_id})
    if resp.status_code == 200:
        data = runner.extract_data(resp)
        runner.real_data["test_project_id"] = data.get("id") if data else None
        runner.log("创建历史项目", True, f"ID: {data.get('id') if data else 'N/A'}")
    else:
        runner.log("创建历史项目", False, f"状态码: {resp.status_code}")

    # 3. 获取历史项目详情
    project_id = runner.real_data.get("test_project_id")
    if project_id:
        resp = runner.request("GET", f"/api/historical-projects/{project_id}")
        runner.log("获取历史项目详情", resp.status_code == 200, f"状态码: {resp.status_code}")
    else:
        runner.skip("获取历史项目详情", "无测试项目ID")

    # 4. 更新历史项目
    if project_id:
        resp = runner.request("PUT", f"/api/historical-projects/{project_id}", data={"title": f"更新_{title}"})
        runner.log("更新历史项目", resp.status_code == 200, f"状态码: {resp.status_code}")
    else:
        runner.skip("更新历史项目", "无测试项目ID")

    # 5. 获取不存在项目
    resp = runner.request("GET", "/api/historical-projects/99999")
    runner.log("获取不存在项目", resp.status_code == 404, f"状态码: {resp.status_code}")

    # 6. 无Token访问
    old_token = runner.token
    runner.token = None
    resp = runner.request("GET", "/api/historical-projects/")
    runner.token = old_token
    runner.log("无Token访问", resp.status_code == 401, f"状态码: {resp.status_code}")

    # 7. 按平台筛选
    resp = runner.request("GET", "/api/historical-projects/", params={"platform_id": platform_id})
    runner.log("按平台筛选", resp.status_code == 200, f"状态码: {resp.status_code}")

    # 8. 分页查询
    resp = runner.request("GET", "/api/historical-projects/", params={"skip": 0, "limit": 5})
    runner.log("分页查询", resp.status_code == 200, f"状态码: {resp.status_code}")

    # 9. 删除历史项目
    if project_id:
        resp = runner.request("DELETE", f"/api/historical-projects/{project_id}")
        runner.log("删除历史项目", resp.status_code == 200, f"状态码: {resp.status_code}")
    else:
        runner.skip("删除历史项目", "无测试项目ID")

    # 10. 删除不存在项目
    resp = runner.request("DELETE", "/api/historical-projects/99999")
    runner.log("删除不存在项目", resp.status_code == 404, f"状态码: {resp.status_code}")

    # 11. 创建空标题项目 - 测试验证
    resp = runner.request("POST", "/api/historical-projects/", data={"title": "", "platform_id": platform_id})
    runner.log("创建空标题项目", resp.status_code in [400, 422], f"状态码: {resp.status_code}")

    # 12. 数据结构验证
    resp = runner.request("GET", "/api/historical-projects/")
    if resp.status_code == 200:
        projects = runner.extract_data(resp)
        if projects and len(projects) > 0:
            required = ["id", "title", "platform_id"]
            has_all = all(k in projects[0] for k in required)
            runner.log("数据结构验证", has_all, "包含必要字段" if has_all else "缺少必要字段")
        else:
            runner.log("数据结构验证", True, "无历史项目数据")
    else:
        runner.log("数据结构验证", False, f"状态码: {resp.status_code}")

    report_file = runner.save_report()
    print(f"\n报告已保存: {report_file}")
    return runner.summary()

if __name__ == "__main__":
    success = test_historical_projects()
    sys.exit(0 if success else 1)
