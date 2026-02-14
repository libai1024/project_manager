#!/usr/bin/env python3
"""
API 02 - 用户管理模块测试
测试用例: 10个
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from base_test import TestRunner

def test_users():
    """用户管理模块测试"""
    runner = TestRunner("用户管理", os.path.dirname(os.path.abspath(__file__)))

    print(f"\n{'='*50}")
    print(" API 02 - 用户管理")
    print(f"{'='*50}\n")

    # 登录
    if not runner.login():
        print("登录失败，无法继续测试")
        return False

    # 1. 获取用户列表
    resp = runner.request("GET", "/api/users/")
    if resp.status_code == 200:
        users = runner.extract_data(resp)
        runner.real_data["users"] = users
        runner.log("获取用户列表", True, f"用户数: {len(users) if users else 0}")
    else:
        runner.log("获取用户列表", False, f"状态码: {resp.status_code}, {resp.text[:100] if hasattr(resp, 'text') else ''}")

    # 2. 获取指定用户详情
    resp = runner.request("GET", "/api/users/1")
    if resp.status_code == 200:
        data = runner.extract_data(resp)
        runner.log("获取用户详情", True, f"用户名: {data.get('username') if data else 'N/A'}")
    else:
        runner.log("获取用户详情", False, f"状态码: {resp.status_code}")

    # 3. 获取不存在的用户
    resp = runner.request("GET", "/api/users/99999")
    runner.log("获取不存在用户", resp.status_code == 404, f"状态码: {resp.status_code}")

    # 4. 更新用户信息
    resp = runner.request("PUT", "/api/users/2", data={"role": "user"})
    runner.log("更新用户信息", resp.status_code == 200, f"状态码: {resp.status_code}")

    # 5. 无Token获取用户列表
    old_token = runner.token
    runner.token = None
    resp = runner.request("GET", "/api/users/")
    runner.token = old_token
    runner.log("无Token获取用户列表", resp.status_code == 401, f"状态码: {resp.status_code}")

    # 6. 用户数据结构验证
    resp = runner.request("GET", "/api/users/1")
    if resp.status_code == 200:
        data = runner.extract_data(resp)
        required = ["id", "username", "role"]
        has_all = all(k in data for k in required) if data else False
        runner.log("用户数据结构验证", has_all, "包含必要字段" if has_all else "缺少必要字段")
    else:
        runner.log("用户数据结构验证", False, f"状态码: {resp.status_code}")

    # 7. 获取ID为0的用户
    resp = runner.request("GET", "/api/users/0")
    runner.log("获取ID为0的用户", resp.status_code in [404, 422], f"状态码: {resp.status_code}")

    # 8. 获取ID为负数的用户
    resp = runner.request("GET", "/api/users/-1")
    runner.log("获取ID为负数的用户", resp.status_code in [404, 422], f"状态码: {resp.status_code}")

    # 9. 获取ID为非数字的用户
    resp = runner.request("GET", "/api/users/abc")
    runner.log("获取ID为非数字的用户", resp.status_code in [404, 422], f"状态码: {resp.status_code}")

    # 10. 删除不存在用户
    resp = runner.request("DELETE", "/api/users/99999")
    runner.log("删除不存在用户", resp.status_code == 404, f"状态码: {resp.status_code}")

    # 保存报告
    report_file = runner.save_report()
    print(f"\n报告已保存: {report_file}")

    return runner.summary()


if __name__ == "__main__":
    success = test_users()
    sys.exit(0 if success else 1)
