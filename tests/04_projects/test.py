#!/usr/bin/env python3
"""
API 04 - 项目管理模块测试
测试用例: 15个
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from base_test import TestRunner

def test_projects():
    """项目管理模块测试"""
    runner = TestRunner("项目管理", os.path.dirname(os.path.abspath(__file__)))

    print(f"\n{'='*50}")
    print(" API 04 - 项目管理")
    print(f"{'='*50}\n")

    # 登录
    if not runner.login():
        print("登录失败，无法继续测试")
        return False

    # 1. 获取项目列表
    resp = runner.request("GET", "/api/projects/")
    if resp.status_code == 200:
        projects = runner.extract_data(resp)
        runner.real_data["projects"] = projects
        runner.log("获取项目列表", True, f"项目数: {len(projects) if projects else 0}")
    else:
        runner.log("获取项目列表", False, f"状态码: {resp.status_code}")

    # 2. 创建测试项目
    import time
    project_title = f"测试项目_{int(time.time())}"
    # 获取一个有效的平台ID
    platforms = runner.real_data.get("platforms", [])
    platform_id = platforms[0]["id"] if platforms else 1

    resp = runner.request("POST", "/api/projects/", data={
        "title": project_title,
        "platform_id": platform_id,
        "description": "测试项目描述"
    })
    if resp.status_code == 200:
        data = runner.extract_data(resp)
        if data:
            runner.real_data["test_project_id"] = data.get("id")
            runner.log("创建测试项目", True, f"项目ID: {data.get('id')}, 标题: {project_title}")
        else:
            runner.log("创建测试项目", False, "响应数据为空")
    else:
        runner.log("创建测试项目", False, f"状态码: {resp.status_code}, {resp.text[:100]}")

    # 3. 获取项目详情
    project_id = runner.real_data.get("test_project_id")
    if project_id:
        resp = runner.request("GET", f"/api/projects/{project_id}")
        if resp.status_code == 200:
            data = runner.extract_data(resp)
            runner.log("获取项目详情", True, f"标题: {data.get('title') if data else 'N/A'}")
        else:
            runner.log("获取项目详情", False, f"状态码: {resp.status_code}")
    else:
        runner.skip("获取项目详情", "无测试项目ID")

    # 4. 更新项目信息
    if project_id:
        resp = runner.request("PUT", f"/api/projects/{project_id}", data={
            "title": f"更新_{project_title}",
            "description": "更新后的描述"
        })
        runner.log("更新项目信息", resp.status_code == 200, f"状态码: {resp.status_code}")
    else:
        runner.skip("更新项目信息", "无测试项目ID")

    # 5. 按状态筛选项目
    resp = runner.request("GET", "/api/projects/", params={"status": "pending"})
    if resp.status_code == 200:
        data = runner.extract_data(resp)
        runner.log("按状态筛选项目", True, f"pending状态项目数: {len(data) if data else 0}")
    else:
        runner.log("按状态筛选项目", False, f"状态码: {resp.status_code}")

    # 6. 按平台筛选项目
    resp = runner.request("GET", "/api/projects/", params={"platform_id": platform_id})
    if resp.status_code == 200:
        data = runner.extract_data(resp)
        runner.log("按平台筛选项目", True, f"平台{platform_id}的项目数: {len(data) if data else 0}")
    else:
        runner.log("按平台筛选项目", False, f"状态码: {resp.status_code}")

    # 7. 分页查询
    resp = runner.request("GET", "/api/projects/", params={"skip": 0, "limit": 5})
    if resp.status_code == 200:
        data = runner.extract_data(resp)
        runner.log("分页查询", True, f"返回项目数: {len(data) if data else 0}")
    else:
        runner.log("分页查询", False, f"状态码: {resp.status_code}")

    # 8. 获取不存在的项目
    resp = runner.request("GET", "/api/projects/99999")
    runner.log("获取不存在项目", resp.status_code == 404, f"状态码: {resp.status_code}")

    # 9. 无Token访问
    old_token = runner.token
    runner.token = None
    resp = runner.request("GET", "/api/projects/")
    runner.token = old_token
    runner.log("无Token访问", resp.status_code == 401, f"状态码: {resp.status_code}")

    # 10. 创建空标题项目
    resp = runner.request("POST", "/api/projects/", data={
        "title": "",
        "platform_id": platform_id
    })
    runner.log("创建空标题项目", resp.status_code in [400, 422], f"状态码: {resp.status_code}")

    # 11. 添加项目步骤
    if project_id:
        resp = runner.request("POST", f"/api/projects/{project_id}/steps", data={
            "name": "测试步骤",
            "order_index": 1
        })
        if resp.status_code == 200:
            data = runner.extract_data(resp)
            runner.real_data["test_step_id"] = data.get("id") if data else None
            runner.log("添加项目步骤", True, f"步骤ID: {data.get('id') if data else 'N/A'}")
        else:
            runner.log("添加项目步骤", False, f"状态码: {resp.status_code}")
    else:
        runner.skip("添加项目步骤", "无测试项目ID")

    # 12. 项目结账（未完成步骤时应失败）
    if project_id:
        resp = runner.request("POST", f"/api/projects/{project_id}/settle")
        # 未完成最后一个步骤时，应该返回400
        runner.log("项目结账验证", resp.status_code == 400, f"状态码: {resp.status_code} (业务规则:需先完成步骤)")
    else:
        runner.skip("项目结账", "无测试项目ID")

    # 13. 项目数据结构验证
    if project_id:
        resp = runner.request("GET", f"/api/projects/{project_id}")
        if resp.status_code == 200:
            data = runner.extract_data(resp)
            required = ["id", "title", "status", "platform_id"]
            has_all = all(k in data for k in required) if data else False
            runner.log("项目数据结构验证", has_all, "包含必要字段" if has_all else "缺少必要字段")
        else:
            runner.log("项目数据结构验证", False, f"状态码: {resp.status_code}")
    else:
        runner.skip("项目数据结构验证", "无测试项目ID")

    # 14. 删除测试步骤
    step_id = runner.real_data.get("test_step_id")
    if step_id:
        resp = runner.request("DELETE", f"/api/projects/steps/{step_id}")
        runner.log("删除测试步骤", resp.status_code == 200, f"状态码: {resp.status_code}")
    else:
        runner.skip("删除测试步骤", "无测试步骤ID")

    # 15. 删除测试项目（清理）
    if project_id:
        resp = runner.request("DELETE", f"/api/projects/{project_id}")
        runner.log("删除测试项目", resp.status_code == 200, f"状态码: {resp.status_code}")
    else:
        runner.skip("删除测试项目", "无测试项目ID")

    # 保存报告
    report_file = runner.save_report()
    print(f"\n报告已保存: {report_file}")

    return runner.summary()


if __name__ == "__main__":
    success = test_projects()
    sys.exit(0 if success else 1)
