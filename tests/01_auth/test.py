#!/usr/bin/env python3
"""
API 01 - 认证模块测试
测试用例: 10个
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from base_test import TestRunner, BASE_URL
import requests

def test_auth():
    """认证模块测试"""
    runner = TestRunner("认证模块", os.path.dirname(os.path.abspath(__file__)))

    print(f"\n{'='*50}")
    print(" API 01 - 认证模块")
    print(f"{'='*50}\n")

    # 1. 管理员登录成功
    resp = runner.request("POST", "/api/auth/login",
                          data={"username": "admin", "password": "admin123"}, form_data=True)
    if resp.status_code == 200:
        data = resp.json()
        runner.token = data.get("access_token")
        runner.log("管理员登录成功", True, f"Token: {runner.token[:20]}...")
    else:
        runner.log("管理员登录成功", False, f"状态码: {resp.status_code}")

    # 2. 登录响应包含必要字段
    resp = runner.request("POST", "/api/auth/login",
                          data={"username": "admin", "password": "admin123"}, form_data=True)
    if resp.status_code == 200:
        data = resp.json()
        required = ["access_token", "refresh_token", "token_type"]
        has_all = all(k in data for k in required)
        runner.log("登录响应字段完整性", has_all, "包含所有必要字段" if has_all else "缺少字段")
    else:
        runner.log("登录响应字段完整性", False, f"状态码: {resp.status_code}")

    # 3. 错误密码登录失败
    resp = runner.request("POST", "/api/auth/login",
                          data={"username": "admin", "password": "wrongpassword"}, form_data=True)
    runner.log("错误密码登录失败", resp.status_code == 401, f"状态码: {resp.status_code}")

    # 4. 不存在用户登录失败
    resp = runner.request("POST", "/api/auth/login",
                          data={"username": "nonexistent", "password": "anypassword"}, form_data=True)
    runner.log("不存在用户登录失败", resp.status_code == 401, f"状态码: {resp.status_code}")

    # 5. 空密码登录失败
    resp = runner.request("POST", "/api/auth/login",
                          data={"username": "admin", "password": ""}, form_data=True)
    runner.log("空密码登录失败", resp.status_code in [401, 422], f"状态码: {resp.status_code}")

    # 6. 获取当前用户信息
    resp = runner.request("GET", "/api/auth/me")
    if resp.status_code == 200:
        data = resp.json()
        runner.log("获取当前用户信息", data.get("username") == "admin", f"用户: {data.get('username')}")
    else:
        runner.log("获取当前用户信息", False, f"状态码: {resp.status_code}")

    # 7. 无Token访问受保护接口
    old_token = runner.token
    runner.token = None
    resp = runner.request("GET", "/api/auth/me")
    runner.token = old_token
    runner.log("无Token访问受保护接口", resp.status_code == 401, f"状态码: {resp.status_code}")

    # 8. 无效Token访问
    runner.token = "invalid_token_xyz"
    resp = runner.request("GET", "/api/auth/me")
    runner.token = old_token
    runner.log("无效Token访问", resp.status_code == 401, f"状态码: {resp.status_code}")

    # 9. 过期Token访问
    runner.token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTAwMDAwMDAwMH0.invalid"
    resp = runner.request("GET", "/api/auth/me")
    runner.token = old_token
    runner.log("过期Token访问", resp.status_code == 401, f"状态码: {resp.status_code}")

    # 10. 用户登出
    resp = runner.request("POST", "/api/auth/logout")
    runner.log("用户登出", resp.status_code == 200, f"状态码: {resp.status_code}")

    # 保存报告
    report_file = runner.save_report()
    print(f"\n报告已保存: {report_file}")

    return runner.summary()


if __name__ == "__main__":
    success = test_auth()
    sys.exit(0 if success else 1)
