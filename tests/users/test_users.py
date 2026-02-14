#!/usr/bin/env python3
"""
用户管理模块 (Users) 测试 - 10个用例
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from test_utils import *

def test_users():
    """用户管理模块测试"""
    module = "用户管理"
    tests = []
    print_module_header(module, 10)

    token = get_admin_token()
    if not token:
        print("无法获取Token，跳过测试")
        return tests

    # 1. 获取用户列表
    resp = make_request("GET", "/api/users/", token=token)
    if resp.status_code == 200:
        users = resp.json()
        tests.append({"name": "获取用户列表", "result": "PASS", "detail": f"用户数: {len(users)}"})
    else:
        tests.append({"name": "获取用户列表", "result": "FAIL", "detail": f"状态码: {resp.status_code}"})
    log_test(module, tests[-1]["name"], tests[-1]["result"], tests[-1].get("detail", ""))

    # 2. 获取指定用户详情
    resp = make_request("GET", "/api/users/1", token=token)
    if resp.status_code == 200 and resp.json().get("username"):
        tests.append({"name": "获取用户详情", "result": "PASS", "detail": f"用户名: {resp.json().get('username')}"})
    else:
        tests.append({"name": "获取用户详情", "result": "FAIL", "detail": f"状态码: {resp.status_code}"})
    log_test(module, tests[-1]["name"], tests[-1]["result"])

    # 3. 获取不存在的用户
    resp = make_request("GET", "/api/users/99999", token=token)
    tests.append({"name": "获取不存在用户", "result": "PASS" if resp.status_code == 404 else "FAIL", "detail": f"状态码: {resp.status_code}"})
    log_test(module, tests[-1]["name"], tests[-1]["result"])

    # 4. 更新用户信息
    resp = make_request("PUT", "/api/users/2", token=token, data={"role": "user"})
    tests.append({"name": "更新用户信息", "result": "PASS" if resp.status_code == 200 else "FAIL", "detail": f"状态码: {resp.status_code}"})
    log_test(module, tests[-1]["name"], tests[-1]["result"])

    # 5. 无Token获取用户列表
    resp = make_request("GET", "/api/users/")
    tests.append({"name": "无Token获取用户列表", "result": "PASS" if resp.status_code == 401 else "FAIL", "detail": f"状态码: {resp.status_code}"})
    log_test(module, tests[-1]["name"], tests[-1]["result"])

    # 6. 验证用户数据结构
    resp = make_request("GET", "/api/users/1", token=token)
    if resp.status_code == 200:
        data = resp.json()
        required = ["id", "username", "role"]
        if all(k in data for k in required):
            tests.append({"name": "用户数据结构验证", "result": "PASS", "detail": "包含必要字段"})
        else:
            tests.append({"name": "用户数据结构验证", "result": "FAIL", "detail": "缺少必要字段"})
    else:
        tests.append({"name": "用户数据结构验证", "result": "FAIL", "detail": f"状态码: {resp.status_code}"})
    log_test(module, tests[-1]["name"], tests[-1]["result"])

    # 7. 获取ID为0的用户
    resp = make_request("GET", "/api/users/0", token=token)
    tests.append({"name": "获取ID为0的用户", "result": "PASS" if resp.status_code in [404, 422] else "FAIL", "detail": f"状态码: {resp.status_code}"})
    log_test(module, tests[-1]["name"], tests[-1]["result"])

    # 8. 获取ID为负数的用户
    resp = make_request("GET", "/api/users/-1", token=token)
    tests.append({"name": "获取ID为负数的用户", "result": "PASS" if resp.status_code in [404, 422] else "FAIL", "detail": f"状态码: {resp.status_code}"})
    log_test(module, tests[-1]["name"], tests[-1]["result"])

    # 9. 获取ID为非数字的用户
    resp = make_request("GET", "/api/users/abc", token=token)
    tests.append({"name": "获取ID为非数字的用户", "result": "PASS" if resp.status_code in [404, 422] else "FAIL", "detail": f"状态码: {resp.status_code}"})
    log_test(module, tests[-1]["name"], tests[-1]["result"])

    # 10. 删除不存在用户
    resp = make_request("DELETE", "/api/users/99999", token=token)
    tests.append({"name": "删除不存在用户", "result": "PASS" if resp.status_code == 404 else "FAIL", "detail": f"状态码: {resp.status_code}"})
    log_test(module, tests[-1]["name"], tests[-1]["result"])

    save_report("users", tests)

    passed = sum(1 for t in tests if t["result"] == "PASS")
    failed = sum(1 for t in tests if t["result"] == "FAIL")
    print_module_summary(module, passed, failed, 0)

    return tests


if __name__ == "__main__":
    test_users()
