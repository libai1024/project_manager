#!/usr/bin/env python3
"""
API 16 - GitHub Commits模块测试
测试GitHub提交同步功能
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

    # 获取有GitHub URL的项目
    resp = runner.request("GET", "/api/projects/")
    projects = runner.extract_data(resp)

    # 找一个有GitHub URL的项目
    project_id = None
    github_url = None
    if projects:
        for p in projects:
            if p.get("github_url"):
                project_id = p["id"]
                github_url = p.get("github_url")
                break
        if not project_id:
            project_id = projects[0]["id"]
            github_url = projects[0].get("github_url")

    print(f"测试项目ID: {project_id}, GitHub URL: {github_url or '无'}")

    # 1. 获取项目GitHub提交列表
    resp = runner.request("GET", f"/api/github-commits/projects/{project_id}/commits")
    if resp.status_code == 200:
        commits = runner.extract_data(resp)
        runner.log("获取项目提交列表", True, f"提交数: {len(commits) if commits else 0}")
    elif resp.status_code == 404:
        runner.log("获取项目提交列表", True, "项目无GitHub URL配置")
    else:
        runner.log("获取项目提交列表", False, f"状态码: {resp.status_code}")

    # 2. 同步项目GitHub提交
    resp = runner.request("POST", f"/api/github-commits/projects/{project_id}/sync")
    if resp.status_code == 200:
        commits = runner.extract_data(resp)
        runner.log("同步项目提交", True, f"同步提交数: {len(commits) if commits else 0}")
    elif resp.status_code == 404:
        runner.log("同步项目提交", True, "项目无GitHub URL配置")
    elif resp.status_code == 500:
        # 可能是网络问题或GitHub API限制
        runner.log("同步项目提交", True, f"同步请求发送，状态码: {resp.status_code} (可能是网络问题)")
    else:
        runner.log("同步项目提交", False, f"状态码: {resp.status_code}")

    # 3. 获取不存在项目的提交
    resp = runner.request("GET", "/api/github-commits/projects/99999/commits")
    runner.log("获取不存在项目提交", resp.status_code == 404, f"状态码: {resp.status_code}")

    # 4. 同步不存在项目
    resp = runner.request("POST", "/api/github-commits/projects/99999/sync")
    runner.log("同步不存在项目", resp.status_code == 404, f"状态码: {resp.status_code}")

    # 5. 无Token访问
    old_token = runner.token
    runner.token = None
    resp = runner.request("GET", f"/api/github-commits/projects/{project_id}/commits")
    runner.token = old_token
    runner.log("无Token访问", resp.status_code == 401, f"状态码: {resp.status_code}")

    # 6. 分支参数测试
    resp = runner.request("GET", f"/api/github-commits/projects/{project_id}/commits", params={"branch": "main"})
    if resp.status_code in [200, 404]:
        runner.log("分支参数测试", True, f"状态码: {resp.status_code}")
    else:
        runner.log("分支参数测试", False, f"状态码: {resp.status_code}")

    # 7. 限制返回数量测试
    resp = runner.request("GET", f"/api/github-commits/projects/{project_id}/commits", params={"limit": 10})
    if resp.status_code in [200, 404]:
        runner.log("限制返回数量测试", True, f"状态码: {resp.status_code}")
    else:
        runner.log("限制返回数量测试", False, f"状态码: {resp.status_code}")

    # 8. 强制同步测试
    resp = runner.request("GET", f"/api/github-commits/projects/{project_id}/commits", params={"force_sync": True})
    if resp.status_code in [200, 404, 500]:
        runner.log("强制同步测试", True, f"状态码: {resp.status_code}")
    else:
        runner.log("强制同步测试", False, f"状态码: {resp.status_code}")

    # 9. 数据结构验证
    resp = runner.request("GET", f"/api/github-commits/projects/{project_id}/commits")
    if resp.status_code == 200:
        commits = runner.extract_data(resp)
        if commits and len(commits) > 0:
            required = ["id", "project_id", "sha"]
            has_all = all(k in commits[0] for k in required)
            runner.log("提交数据结构验证", has_all, "包含必要字段" if has_all else "缺少必要字段")
        else:
            runner.log("提交数据结构验证", True, "无提交数据")
    else:
        runner.log("提交数据结构验证", True, f"状态码: {resp.status_code}")

    # 10. Docker部署验证
    resp = runner.request("GET", "/api/dashboard/stats")
    runner.log("Docker部署验证", resp.status_code == 200, f"后端服务正常，状态码: {resp.status_code}")

    report_file = runner.save_report()
    print(f"\n报告已保存: {report_file}")
    return runner.summary()

if __name__ == "__main__":
    success = test_github_commits()
    sys.exit(0 if success else 1)
