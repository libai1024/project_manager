#!/usr/bin/env python3
"""
API 16 - GitHub Commits模块测试
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from base_test import TestRunner

def test_github_commits():
    """GitHub Commits模块测试"""
    runner = TestRunner("GitHub Commits", os.path.dirname(os.path.abspath(__file__)))

    print(f"\n{'='*50}")
    print(" API 16 - GitHub Commits")
    print(f"{'='*50}\n")

    if not runner.login():
        print("登录失败，无法继续测试")
        return False

    # 获取测试项目
    resp = runner.request("GET", "/api/projects/")
    projects = runner.extract_data(resp)
    project_id = projects[0]["id"] if projects else 1

    # 1. 获取项目GitHub提交列表
    resp = runner.request("GET", f"/api/projects/{project_id}/commits")
    if resp.status_code == 200:
        commits = runner.extract_data(resp)
        runner.log("获取项目提交列表", True, f"提交数: {len(commits) if commits else 0}")
    else:
        runner.log("获取项目提交列表", False, f"状态码: {resp.status_code}")

    # 2. 同步项目GitHub提交
    resp = runner.request("POST", f"/api/projects/{project_id}/sync")
    # 同步可能成功或失败（取决于项目是否有GitHub URL）
    runner.log("同步项目提交", resp.status_code in [200, 400, 404], f"状态码: {resp.status_code}")

    # 3. 获取不存在项目的提交
    resp = runner.request("GET", "/api/projects/99999/commits")
    runner.log("获取不存在项目提交", resp.status_code == 404, f"状态码: {resp.status_code}")

    # 4. 同步不存在项目
    resp = runner.request("POST", "/api/projects/99999/sync")
    runner.log("同步不存在项目", resp.status_code == 404, f"状态码: {resp.status_code}")

    # 5. 无Token访问
    old_token = runner.token
    runner.token = None
    resp = runner.request("GET", f"/api/projects/{project_id}/commits")
    runner.token = old_token
    runner.log("无Token访问", resp.status_code == 401, f"状态码: {resp.status_code}")

    # 6. 数据结构验证
    resp = runner.request("GET", f"/api/projects/{project_id}/commits")
    if resp.status_code == 200:
        commits = runner.extract_data(resp)
        if commits and len(commits) > 0:
            required = ["id", "project_id"]
            has_all = all(k in commits[0] for k in required)
            runner.log("提交数据结构验证", has_all, "包含必要字段" if has_all else "缺少必要字段")
        else:
            runner.log("提交数据结构验证", True, "无提交数据")
    else:
        runner.log("提交数据结构验证", False, f"状态码: {resp.status_code}")

    # 7. 分页参数测试
    resp = runner.request("GET", f"/api/projects/{project_id}/commits", params={"skip": 0, "limit": 5})
    runner.log("分页参数测试", resp.status_code == 200, f"状态码: {resp.status_code}")

    # 8. 负数项目ID
    resp = runner.request("GET", "/api/projects/-1/commits")
    runner.log("负数项目ID测试", resp.status_code in [400, 404, 422], f"状态码: {resp.status_code}")

    report_file = runner.save_report()
    print(f"\n报告已保存: {report_file}")
    return runner.summary()

if __name__ == "__main__":
    success = test_github_commits()
    sys.exit(0 if success else 1)
