#!/usr/bin/env python3
"""
平台管理模块 (Platforms) 测试 - 10个用例
"""
import sys
import os
import time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from test_utils import *

def test_platforms():
    """平台管理模块测试"""
    module = "平台管理"
    tests = []
    print_module_header(module, 10)

    token = get_admin_token()
    if not token:
        print("无法获取Token，跳过测试")
        return tests

    # 1. 获取平台列表
    resp = make_request("GET", "/api/platforms/", token=token)
    if resp.status_code == 200:
        platforms = resp.json()
        real_data["platforms"] = [p["id"] for p in platforms] if platforms else []
        tests.append({"name": "获取平台列表", "result": "PASS", "detail": f"平台数: {len(platforms)}"})
    else:
        tests.append({"name": "获取平台列表", "result": "FAIL", "detail": f"状态码: {resp.status_code}"})
    log_test(module, tests[-1]["name"], tests[-1]["result"], tests[-1].get("detail", ""))

    # 2. 创建平台
    resp = make_request("POST", "/api/platforms/", token=token, data={
        "name": f"测试平台_{int(time.time())}",
        "description": "API测试创建"
    })
    if resp.status_code == 200:
        new_id = resp.json().get("id")
        if new_id:
            created_data["platforms"].append(new_id)
        tests.append({"name": "创建平台", "result": "PASS", "detail": f"新平台ID: {new_id}"})
    else:
        tests.append({"name": "创建平台", "result": "FAIL", "detail": f"状态码: {resp.status_code}"})
    log_test(module, tests[-1]["name"], tests[-1]["result"])

    # 3. 获取平台详情
    if real_data["platforms"]:
        resp = make_request("GET", f"/api/platforms/{real_data['platforms'][0]}", token=token)
        tests.append({"name": "获取平台详情", "result": "PASS" if resp.status_code == 200 else "FAIL", "detail": f"状态码: {resp.status_code}"})
    else:
        tests.append({"name": "获取平台详情", "result": "SKIP", "detail": "无平台数据"})
    log_test(module, tests[-1]["name"], tests[-1]["result"])

    # 4. 更新平台
    if real_data["platforms"]:
        resp = make_request("PUT", f"/api/platforms/{real_data['platforms'][0]}", token=token, data={
            "name": f"更新平台_{int(time.time())}"
        })
        tests.append({"name": "更新平台", "result": "PASS" if resp.status_code == 200 else "FAIL", "detail": f"状态码: {resp.status_code}"})
    else:
        tests.append({"name": "更新平台", "result": "SKIP", "detail": "无平台数据"})
    log_test(module, tests[-1]["name"], tests[-1]["result"])

    # 5. 获取不存在的平台
    resp = make_request("GET", "/api/platforms/99999", token=token)
    tests.append({"name": "获取不存在平台", "result": "PASS" if resp.status_code == 404 else "FAIL", "detail": f"状态码: {resp.status_code}"})
    log_test(module, tests[-1]["name"], tests[-1]["result"])

    # 6. 无Token访问
    resp = make_request("GET", "/api/platforms/")
    tests.append({"name": "无Token获取平台", "result": "PASS" if resp.status_code == 401 else "FAIL", "detail": f"状态码: {resp.status_code}"})
    log_test(module, tests[-1]["name"], tests[-1]["result"])

    # 7. 创建空名称平台
    resp = make_request("POST", "/api/platforms/", token=token, data={"name": ""})
    tests.append({"name": "创建空名称平台", "result": "PASS" if resp.status_code in [400, 422] else "FAIL", "detail": f"状态码: {resp.status_code}"})
    log_test(module, tests[-1]["name"], tests[-1]["result"])

    # 8. 创建超长名称平台
    long_name = "a" * 500
    resp = make_request("POST", "/api/platforms/", token=token, data={"name": long_name})
    tests.append({"name": "创建超长名称平台", "result": "PASS" if resp.status_code in [200, 400, 422] else "FAIL", "detail": f"状态码: {resp.status_code}"})
    log_test(module, tests[-1]["name"], tests[-1]["result"])

    # 9. 删除平台
    if created_data["platforms"]:
        resp = make_request("DELETE", f"/api/platforms/{created_data['platforms'][0]}", token=token)
        tests.append({"name": "删除平台", "result": "PASS" if resp.status_code == 200 else "FAIL", "detail": f"状态码: {resp.status_code}"})
    else:
        tests.append({"name": "删除平台", "result": "SKIP", "detail": "无可删除的平台"})
    log_test(module, tests[-1]["name"], tests[-1]["result"])

    # 10. 删除不存在的平台
    resp = make_request("DELETE", "/api/platforms/99999", token=token)
    tests.append({"name": "删除不存在平台", "result": "PASS" if resp.status_code == 404 else "FAIL", "detail": f"状态码: {resp.status_code}"})
    log_test(module, tests[-1]["name"], tests[-1]["result"])

    save_report("platforms", tests)

    passed = sum(1 for t in tests if t["result"] == "PASS")
    failed = sum(1 for t in tests if t["result"] == "FAIL")
    skipped = sum(1 for t in tests if t["result"] == "SKIP")
    print_module_summary(module, passed, failed, skipped)

    return tests


if __name__ == "__main__":
    test_platforms()
