#!/usr/bin/env python3
"""
API 06 - 文件夹管理模块测试
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from base_test import TestRunner

def test_folders():
    """文件夹管理模块测试"""
    runner = TestRunner("文件夹管理", os.path.dirname(os.path.abspath(__file__)))

    print(f"\n{'='*50}")
    print(" API 06 - 文件夹管理")
    print(f"{'='*50}\n")

    if not runner.login():
        print("登录失败，无法继续测试")
        return False

    # 获取测试项目
    resp = runner.request("GET", "/api/projects/")
    projects = runner.extract_data(resp)
    project_id = projects[0]["id"] if projects else 1

    # 1. 获取文件夹列表
    resp = runner.request("GET", f"/api/attachment-folders/project/{project_id}")
    if resp.status_code == 200:
        folders = runner.extract_data(resp)
        runner.real_data["folders"] = folders
        runner.log("获取文件夹列表", True, f"文件夹数: {len(folders) if folders else 0}")
    else:
        runner.log("获取文件夹列表", False, f"状态码: {resp.status_code}")

    # 2. 创建文件夹
    import time
    folder_name = f"测试文件夹_{int(time.time())}"
    resp = runner.request("POST", f"/api/attachment-folders/project/{project_id}", data={"name": folder_name})
    if resp.status_code == 200:
        data = runner.extract_data(resp)
        runner.real_data["test_folder_id"] = data.get("id") if data else None
        runner.log("创建文件夹", True, f"ID: {data.get('id') if data else 'N/A'}")
    else:
        runner.log("创建文件夹", False, f"状态码: {resp.status_code}")

    # 3. 更新文件夹
    folder_id = runner.real_data.get("test_folder_id")
    if folder_id:
        resp = runner.request("PUT", f"/api/attachment-folders/{folder_id}", data={"name": f"更新_{folder_name}"})
        runner.log("更新文件夹", resp.status_code == 200, f"状态码: {resp.status_code}")
    else:
        runner.skip("更新文件夹", "无测试文件夹ID")

    # 4. 删除文件夹
    if folder_id:
        resp = runner.request("DELETE", f"/api/attachment-folders/{folder_id}")
        runner.log("删除文件夹", resp.status_code == 200, f"状态码: {resp.status_code}")
    else:
        runner.skip("删除文件夹", "无测试文件夹ID")

    # 5. 删除不存在文件夹
    resp = runner.request("DELETE", "/api/attachment-folders/99999")
    runner.log("删除不存在文件夹", resp.status_code == 404, f"状态码: {resp.status_code}")

    # 6. 无Token访问
    old_token = runner.token
    runner.token = None
    resp = runner.request("GET", f"/api/attachment-folders/project/{project_id}")
    runner.token = old_token
    runner.log("无Token访问", resp.status_code == 401, f"状态码: {resp.status_code}")

    # 7. 创建空名称文件夹
    resp = runner.request("POST", f"/api/attachment-folders/project/{project_id}", data={"name": ""})
    runner.log("创建空名称文件夹", resp.status_code in [400, 422], f"状态码: {resp.status_code}")

    # 8. 历史项目文件夹列表
    resp = runner.request("GET", "/api/attachment-folders/historical-project/1")
    runner.log("获取历史项目文件夹", resp.status_code in [200, 404], f"状态码: {resp.status_code}")

    # 9. 文件夹数据结构验证
    resp = runner.request("GET", f"/api/attachment-folders/project/{project_id}")
    if resp.status_code == 200:
        folders = runner.extract_data(resp)
        if folders and len(folders) > 0:
            required = ["id", "name", "project_id"]
            has_all = all(k in folders[0] for k in required)
            runner.log("文件夹数据结构验证", has_all, "包含必要字段" if has_all else "缺少必要字段")
        else:
            runner.log("文件夹数据结构验证", True, "无文件夹数据")
    else:
        runner.log("文件夹数据结构验证", False, f"状态码: {resp.status_code}")

    # 10. 创建超长名称文件夹
    long_name = "A" * 300
    resp = runner.request("POST", f"/api/attachment-folders/project/{project_id}", data={"name": long_name})
    runner.log("创建超长名称文件夹", resp.status_code in [200, 400, 422], f"状态码: {resp.status_code}")

    report_file = runner.save_report()
    print(f"\n报告已保存: {report_file}")
    return runner.summary()

if __name__ == "__main__":
    success = test_folders()
    sys.exit(0 if success else 1)
