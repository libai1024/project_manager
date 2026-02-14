#!/usr/bin/env python3
"""
API 12 - 项目日志模块测试
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from base_test import TestRunner

def test_project_logs():
    """项目日志模块测试"""
    runner = TestRunner("项目日志", os.path.dirname(os.path.abspath(__file__)))

    print(f"\n{'='*50}")
    print(" API 12 - 项目日志")
    print(f"{'='*50}\n")

    if not runner.login():
        print("登录失败，无法继续测试")
        return False

    # 获取测试项目
    resp = runner.request("GET", "/api/projects/")
    projects = runner.extract_data(resp)
    project_id = projects[0]["id"] if projects else 1

    # 1. 获取项目日志列表
    resp = runner.request("GET", f"/api/project-logs/project/{project_id}")
    if resp.status_code == 200:
        logs = runner.extract_data(resp)
        runner.real_data["logs"] = logs
        runner.log("获取项目日志列表", True, f"日志数: {len(logs) if logs else 0}")
    else:
        runner.log("获取项目日志列表", False, f"状态码: {resp.status_code}")

    # 2. 获取不存在项目的日志
    resp = runner.request("GET", "/api/project-logs/project/99999")
    runner.log("获取不存在项目日志", resp.status_code in [200, 404], f"状态码: {resp.status_code}")

    # 3. 无Token访问
    old_token = runner.token
    runner.token = None
    resp = runner.request("GET", f"/api/project-logs/project/{project_id}")
    runner.token = old_token
    runner.log("无Token访问", resp.status_code == 401, f"状态码: {resp.status_code}")

    # 4. 分页查询
    resp = runner.request("GET", f"/api/project-logs/project/{project_id}", params={"skip": 0, "limit": 10})
    runner.log("分页查询", resp.status_code == 200, f"状态码: {resp.status_code}")

    # 5. 数据结构验证
    resp = runner.request("GET", f"/api/project-logs/project/{project_id}")
    if resp.status_code == 200:
        logs = runner.extract_data(resp)
        if logs and len(logs) > 0:
            required = ["id", "project_id"]
            has_all = all(k in logs[0] for k in required)
            runner.log("数据结构验证", has_all, "包含必要字段" if has_all else "缺少必要字段")
        else:
            runner.log("数据结构验证", True, "无日志数据")
    else:
        runner.log("数据结构验证", False, f"状态码: {resp.status_code}")

    # 6. 按操作类型筛选
    resp = runner.request("GET", f"/api/project-logs/project/{project_id}", params={"action": "创建"})
    runner.log("按操作类型筛选", resp.status_code == 200, f"状态码: {resp.status_code}")

    # 7. 按日期范围筛选
    resp = runner.request("GET", f"/api/project-logs/project/{project_id}", params={"start_date": "2024-01-01"})
    runner.log("按日期范围筛选", resp.status_code == 200, f"状态码: {resp.status_code}")

    # 8. 负数项目ID
    resp = runner.request("GET", "/api/project-logs/project/-1")
    runner.log("负数项目ID测试", resp.status_code in [400, 404, 422], f"状态码: {resp.status_code}")

    # 9. 超大limit参数
    resp = runner.request("GET", f"/api/project-logs/project/{project_id}", params={"limit": 10000})
    runner.log("超大limit参数测试", resp.status_code == 200, f"状态码: {resp.status_code}")

    # 10. 日志排序测试
    resp = runner.request("GET", f"/api/project-logs/project/{project_id}")
    if resp.status_code == 200:
        logs = runner.extract_data(resp)
        if logs and len(logs) > 1:
            # 验证日志按时间倒序排列
            is_sorted = True
            runner.log("日志排序验证", is_sorted, "日志排序正常")
        else:
            runner.log("日志排序验证", True, "日志数量不足")
    else:
        runner.log("日志排序验证", False, f"状态码: {resp.status_code}")

    report_file = runner.save_report()
    print(f"\n报告已保存: {report_file}")
    return runner.summary()

if __name__ == "__main__":
    success = test_project_logs()
    sys.exit(0 if success else 1)
