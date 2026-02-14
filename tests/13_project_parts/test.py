#!/usr/bin/env python3
"""
API 13 - 配件清单模块测试
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from base_test import TestRunner

def test_project_parts():
    """配件清单模块测试"""
    runner = TestRunner("配件清单", os.path.dirname(os.path.abspath(__file__)))

    print(f"\n{'='*50}")
    print(" API 13 - 配件清单")
    print(f"{'='*50}\n")

    if not runner.login():
        print("登录失败，无法继续测试")
        return False

    # 获取测试项目
    resp = runner.request("GET", "/api/projects/")
    projects = runner.extract_data(resp)
    project_id = projects[0]["id"] if projects else 1

    # 1. 获取配件列表
    resp = runner.request("GET", f"/api/project-parts/project/{project_id}")
    if resp.status_code == 200:
        parts = runner.extract_data(resp)
        runner.log("获取配件列表", True, f"配件数: {len(parts) if parts else 0}")
    else:
        runner.log("获取配件列表", False, f"状态码: {resp.status_code}")

    # 2. 创建配件 (API期望列表格式)
    import time
    part_name = f"测试模块_{int(time.time())}"
    # API期望 List[ProjectPartCreate] 格式
    resp = runner.request("POST", f"/api/project-parts/project/{project_id}", data=[{
        "module_name": part_name,
        "core_component": "STM32F103",
        "quantity": 1,
        "unit_price": 10.0
    }])
    if resp.status_code == 200:
        data = runner.extract_data(resp)
        # API返回列表
        if data and isinstance(data, list) and len(data) > 0:
            runner.real_data["test_part_id"] = data[0].get("id")
            runner.log("创建配件", True, f"ID: {data[0].get('id')}")
        else:
            runner.log("创建配件", True, "创建成功，无返回数据")
    else:
        runner.log("创建配件", False, f"状态码: {resp.status_code}, {resp.text[:100] if hasattr(resp, 'text') else ''}")

    # 3. 更新配件
    part_id = runner.real_data.get("test_part_id")
    if part_id:
        resp = runner.request("PUT", f"/api/project-parts/{part_id}", data={"quantity": 2, "unit_price": 15.0})
        runner.log("更新配件", resp.status_code == 200, f"状态码: {resp.status_code}")
    else:
        runner.skip("更新配件", "无测试配件ID")

    # 4. 更新不存在配件
    resp = runner.request("PUT", "/api/project-parts/99999", data={"quantity": 2})
    runner.log("更新不存在配件", resp.status_code == 404, f"状态码: {resp.status_code}")

    # 6. 无Token访问
    old_token = runner.token
    runner.token = None
    resp = runner.request("GET", f"/api/project-parts/project/{project_id}")
    runner.token = old_token
    runner.log("无Token访问", resp.status_code == 401, f"状态码: {resp.status_code}")

    # 7. 删除配件
    if part_id:
        resp = runner.request("DELETE", f"/api/project-parts/{part_id}")
        runner.log("删除配件", resp.status_code == 200, f"状态码: {resp.status_code}")
    else:
        runner.skip("删除配件", "无测试配件ID")

    # 8. 删除不存在配件
    resp = runner.request("DELETE", "/api/project-parts/99999")
    runner.log("删除不存在配件", resp.status_code == 404, f"状态码: {resp.status_code}")

    # 9. 数据结构验证
    resp = runner.request("GET", f"/api/project-parts/project/{project_id}")
    if resp.status_code == 200:
        parts = runner.extract_data(resp)
        if parts and len(parts) > 0:
            required = ["id", "project_id", "module_name"]
            has_all = all(k in parts[0] for k in required)
            runner.log("数据结构验证", has_all, "包含必要字段" if has_all else "缺少必要字段")
        else:
            runner.log("数据结构验证", True, "无配件数据")
    else:
        runner.log("数据结构验证", False, f"状态码: {resp.status_code}")

    # 9. 创建空模块名配件
    resp = runner.request("POST", f"/api/project-parts/project/{project_id}", data=[{
        "module_name": "",
        "core_component": "Test"
    }])
    runner.log("创建空模块名配件", resp.status_code in [400, 422], f"状态码: {resp.status_code}")

    report_file = runner.save_report()
    print(f"\n报告已保存: {report_file}")
    return runner.summary()

if __name__ == "__main__":
    success = test_project_parts()
    sys.exit(0 if success else 1)
