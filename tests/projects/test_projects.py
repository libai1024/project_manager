#!/usr/bin/env python3
"""
项目管理模块 (Projects) 测试 - 15个用例
"""
import sys
import os
import time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from test_utils import *

def test_projects():
    """项目管理模块测试"""
    module = "项目管理"
    tests = []
    print_module_header(module, 15)

    token = get_admin_token()
    if not token:
        print("无法获取Token，跳过测试")
        return tests

    # 1. 获取项目列表
    resp = make_request("GET", "/api/projects/", token=token)
    if resp.status_code == 200:
        projects = resp.json()
        real_data["projects"] = [p["id"] for p in projects] if projects else []
        tests.append({"name": "获取项目列表", "result": "PASS", "detail": f"项目数: {len(projects)}"})
    else:
        tests.append({"name": "获取项目列表", "result": "FAIL", "detail": f"状态码: {resp.status_code}"})
    log_test(module, tests[-1]["name"], tests[-1]["result"], tests[-1].get("detail", ""))

    # 2. 创建项目
    platform_id = real_data["platforms"][0] if real_data["platforms"] else None
    resp = make_request("POST", "/api/projects/", token=token, data={
        "title": f"测试项目_{int(time.time())}",
        "student_name": "测试学生",
        "platform_id": platform_id,
        "price": 1000.0
    })
    if resp.status_code == 200:
        new_id = resp.json().get("id")
        if new_id:
            created_data["projects"].append(new_id)
            real_data["projects"].append(new_id)
        tests.append({"name": "创建项目", "result": "PASS", "detail": f"新项目ID: {new_id}"})
    else:
        tests.append({"name": "创建项目", "result": "FAIL", "detail": f"状态码: {resp.status_code}"})
    log_test(module, tests[-1]["name"], tests[-1]["result"])

    # 3. 获取项目详情
    if real_data["projects"]:
        resp = make_request("GET", f"/api/projects/{real_data['projects'][0]}", token=token)
        tests.append({"name": "获取项目详情", "result": "PASS" if resp.status_code == 200 else "FAIL", "detail": f"状态码: {resp.status_code}"})
    else:
        tests.append({"name": "获取项目详情", "result": "SKIP", "detail": "无项目数据"})
    log_test(module, tests[-1]["name"], tests[-1]["result"])

    # 4. 更新项目
    if real_data["projects"]:
        resp = make_request("PUT", f"/api/projects/{real_data['projects'][0]}", token=token, data={
            "title": f"更新项目_{int(time.time())}"
        })
        tests.append({"name": "更新项目", "result": "PASS" if resp.status_code == 200 else "FAIL", "detail": f"状态码: {resp.status_code}"})
    else:
        tests.append({"name": "更新项目", "result": "SKIP", "detail": "无项目数据"})
    log_test(module, tests[-1]["name"], tests[-1]["result"])

    # 5. 按状态筛选
    resp = make_request("GET", "/api/projects/", token=token, params={"status": "进行中"})
    tests.append({"name": "按状态筛选项目", "result": "PASS" if resp.status_code == 200 else "FAIL", "detail": f"状态码: {resp.status_code}"})
    log_test(module, tests[-1]["name"], tests[-1]["result"])

    # 6. 按用户筛选
    resp = make_request("GET", "/api/projects/", token=token, params={"user_id": 1})
    tests.append({"name": "按用户筛选项目", "result": "PASS" if resp.status_code == 200 else "FAIL", "detail": f"状态码: {resp.status_code}"})
    log_test(module, tests[-1]["name"], tests[-1]["result"])

    # 7. 按平台筛选
    if real_data["platforms"]:
        resp = make_request("GET", "/api/projects/", token=token, params={"platform_id": real_data["platforms"][0]})
        tests.append({"name": "按平台筛选项目", "result": "PASS" if resp.status_code == 200 else "FAIL", "detail": f"状态码: {resp.status_code}"})
    else:
        tests.append({"name": "按平台筛选项目", "result": "SKIP", "detail": "无平台数据"})
    log_test(module, tests[-1]["name"], tests[-1]["result"])

    # 8. 分页查询
    resp = make_request("GET", "/api/projects/", token=token, params={"skip": 0, "limit": 5})
    tests.append({"name": "分页查询项目", "result": "PASS" if resp.status_code == 200 else "FAIL", "detail": f"状态码: {resp.status_code}"})
    log_test(module, tests[-1]["name"], tests[-1]["result"])

    # 9. 获取不存在项目
    resp = make_request("GET", "/api/projects/99999", token=token)
    tests.append({"name": "获取不存在项目", "result": "PASS" if resp.status_code == 404 else "FAIL", "detail": f"状态码: {resp.status_code}"})
    log_test(module, tests[-1]["name"], tests[-1]["result"])

    # 10. 无Token访问
    resp = make_request("GET", "/api/projects/")
    tests.append({"name": "无Token获取项目", "result": "PASS" if resp.status_code == 401 else "FAIL", "detail": f"状态码: {resp.status_code}"})
    log_test(module, tests[-1]["name"], tests[-1]["result"])

    # 11. 创建空项目验证
    resp = make_request("POST", "/api/projects/", token=token, data={})
    tests.append({"name": "创建空项目验证", "result": "PASS" if resp.status_code in [400, 422] else "FAIL", "detail": f"状态码: {resp.status_code}"})
    log_test(module, tests[-1]["name"], tests[-1]["result"])

    # 12. 项目结账
    if created_data["projects"]:
        resp = make_request("POST", f"/api/projects/{created_data['projects'][0]}/settle", token=token)
        tests.append({"name": "项目结账", "result": "PASS" if resp.status_code == 200 else "FAIL", "detail": f"状态码: {resp.status_code}"})
    else:
        tests.append({"name": "项目结账", "result": "SKIP", "detail": "无可结账项目"})
    log_test(module, tests[-1]["name"], tests[-1]["result"])

    # 13. 添加项目步骤
    if real_data["projects"]:
        resp = make_request("POST", f"/api/projects/{real_data['projects'][0]}/steps", token=token, data={
            "title": f"测试步骤_{int(time.time())}",
            "order": 1
        })
        tests.append({"name": "添加项目步骤", "result": "PASS" if resp.status_code == 200 else "FAIL", "detail": f"状态码: {resp.status_code}"})
    else:
        tests.append({"name": "添加项目步骤", "result": "SKIP", "detail": "无项目数据"})
    log_test(module, tests[-1]["name"], tests[-1]["result"])

    # 14. 项目列表响应结构
    resp = make_request("GET", "/api/projects/", token=token)
    if resp.status_code == 200:
        data = resp.json()
        if isinstance(data, list):
            tests.append({"name": "项目列表响应结构", "result": "PASS", "detail": "返回数组格式"})
        else:
            tests.append({"name": "项目列表响应结构", "result": "FAIL", "detail": "非数组格式"})
    else:
        tests.append({"name": "项目列表响应结构", "result": "FAIL", "detail": f"状态码: {resp.status_code}"})
    log_test(module, tests[-1]["name"], tests[-1]["result"])

    # 15. 组合筛选
    resp = make_request("GET", "/api/projects/", token=token, params={
        "status": "进行中",
        "skip": 0,
        "limit": 10
    })
    tests.append({"name": "组合筛选项目", "result": "PASS" if resp.status_code == 200 else "FAIL", "detail": f"状态码: {resp.status_code}"})
    log_test(module, tests[-1]["name"], tests[-1]["result"])

    save_report("projects", tests)

    passed = sum(1 for t in tests if t["result"] == "PASS")
    failed = sum(1 for t in tests if t["result"] == "FAIL")
    skipped = sum(1 for t in tests if t["result"] == "SKIP")
    print_module_summary(module, passed, failed, skipped)

    return tests


if __name__ == "__main__":
    test_projects()
