#!/usr/bin/env python3
"""
认证模块 (Auth) 测试 - 10个用例
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from test_utils import *

def test_auth():
    """认证模块测试"""
    module = "认证模块"
    tests = []
    print_module_header(module, 10)

    # 1. 管理员登录成功
    resp = make_request("POST", "/api/auth/login", data={"username": "admin", "password": "admin123"}, form_data=True)
    if resp.status_code == 200 and "access_token" in resp.json():
        auth_tokens["admin"] = resp.json().get("access_token")
        tests.append({"name": "管理员登录成功", "result": "PASS", "detail": "Token获取成功"})
    else:
        tests.append({"name": "管理员登录成功", "result": "FAIL", "detail": f"状态码: {resp.status_code}"})
    log_test(module, tests[-1]["name"], tests[-1]["result"], tests[-1]["detail"])

    # 2. 登录响应字段完整性
    resp = make_request("POST", "/api/auth/login", data={"username": "admin", "password": "admin123"}, form_data=True)
    if resp.status_code == 200:
        data = resp.json()
        required = ["access_token", "refresh_token", "token_type"]
        if all(k in data for k in required):
            tests.append({"name": "登录响应字段完整性", "result": "PASS", "detail": "包含所有必要字段"})
        else:
            tests.append({"name": "登录响应字段完整性", "result": "FAIL", "detail": f"缺少字段"})
    else:
        tests.append({"name": "登录响应字段完整性", "result": "FAIL", "detail": f"状态码: {resp.status_code}"})
    log_test(module, tests[-1]["name"], tests[-1]["result"])

    # 3. 错误密码登录失败
    resp = make_request("POST", "/api/auth/login", data={"username": "admin", "password": "wrongpassword"}, form_data=True)
    tests.append({"name": "错误密码登录失败", "result": "PASS" if resp.status_code == 401 else "FAIL", "detail": f"状态码: {resp.status_code}"})
    log_test(module, tests[-1]["name"], tests[-1]["result"])

    # 4. 不存在用户登录失败
    resp = make_request("POST", "/api/auth/login", data={"username": "nonexistent", "password": "anypassword"}, form_data=True)
    tests.append({"name": "不存在用户登录失败", "result": "PASS" if resp.status_code == 401 else "FAIL", "detail": f"状态码: {resp.status_code}"})
    log_test(module, tests[-1]["name"], tests[-1]["result"])

    # 5. 空密码登录失败
    resp = make_request("POST", "/api/auth/login", data={"username": "admin", "password": ""}, form_data=True)
    tests.append({"name": "空密码登录失败", "result": "PASS" if resp.status_code in [401, 422] else "FAIL", "detail": f"状态码: {resp.status_code}"})
    log_test(module, tests[-1]["name"], tests[-1]["result"])

    # 6. 获取当前用户信息
    resp = make_request("GET", "/api/auth/me", token=auth_tokens["admin"])
    if resp.status_code == 200 and resp.json().get("username") == "admin":
        tests.append({"name": "获取当前用户信息", "result": "PASS", "detail": f"用户: {resp.json().get('username')}"})
    else:
        tests.append({"name": "获取当前用户信息", "result": "FAIL", "detail": f"状态码: {resp.status_code}"})
    log_test(module, tests[-1]["name"], tests[-1]["result"])

    # 7. 无Token访问受保护接口
    resp = make_request("GET", "/api/auth/me")
    tests.append({"name": "无Token访问受保护接口", "result": "PASS" if resp.status_code == 401 else "FAIL", "detail": f"状态码: {resp.status_code}"})
    log_test(module, tests[-1]["name"], tests[-1]["result"])

    # 8. 无效Token访问
    resp = make_request("GET", "/api/auth/me", token="invalid_token_xyz")
    tests.append({"name": "无效Token访问", "result": "PASS" if resp.status_code == 401 else "FAIL", "detail": f"状态码: {resp.status_code}"})
    log_test(module, tests[-1]["name"], tests[-1]["result"])

    # 9. 过期Token访问
    expired_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTAwMDAwMDAwMH0.invalid"
    resp = make_request("GET", "/api/auth/me", token=expired_token)
    tests.append({"name": "过期Token访问", "result": "PASS" if resp.status_code == 401 else "FAIL", "detail": f"状态码: {resp.status_code}"})
    log_test(module, tests[-1]["name"], tests[-1]["result"])

    # 10. 用户登出
    resp = make_request("POST", "/api/auth/logout", token=auth_tokens["admin"])
    tests.append({"name": "用户登出", "result": "PASS" if resp.status_code == 200 else "FAIL", "detail": f"状态码: {resp.status_code}"})
    log_test(module, tests[-1]["name"], tests[-1]["result"])

    # 重新登录获取新token供后续测试使用
    resp = make_request("POST", "/api/auth/login", data={"username": "admin", "password": "admin123"}, form_data=True)
    if resp.status_code == 200:
        auth_tokens["admin"] = resp.json().get("access_token")

    # 保存报告
    save_report("auth", tests)

    # 打印总结
    passed = sum(1 for t in tests if t["result"] == "PASS")
    failed = sum(1 for t in tests if t["result"] == "FAIL")
    print_module_summary(module, passed, failed, 0)

    return tests


if __name__ == "__main__":
    test_auth()
