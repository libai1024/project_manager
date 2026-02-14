#!/usr/bin/env python3
"""
API 17 - Video Playbacks模块测试
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from base_test import TestRunner

def test_video_playbacks():
    """Video Playbacks模块测试"""
    runner = TestRunner("视频回放", os.path.dirname(os.path.abspath(__file__)))

    print(f"\n{'='*50}")
    print(" API 17 - Video Playbacks")
    print(f"{'='*50}\n")

    if not runner.login():
        print("登录失败，无法继续测试")
        return False

    # 获取测试项目
    resp = runner.request("GET", "/api/projects/")
    projects = runner.extract_data(resp)
    project_id = projects[0]["id"] if projects else 1

    # 1. 获取项目视频列表
    resp = runner.request("GET", f"/api/video-playbacks/project/{project_id}")
    if resp.status_code == 200:
        videos = runner.extract_data(resp)
        runner.real_data["videos"] = videos
        runner.log("获取项目视频列表", True, f"视频数: {len(videos) if videos else 0}")
    else:
        runner.log("获取项目视频列表", False, f"状态码: {resp.status_code}")

    # 2. 获取不存在项目的视频
    resp = runner.request("GET", "/api/video-playbacks/project/99999")
    runner.log("获取不存在项目视频", resp.status_code in [200, 404], f"状态码: {resp.status_code}")

    # 3. 更新不存在视频
    resp = runner.request("PUT", "/api/video-playbacks/99999", data={"title": "测试"})
    runner.log("更新不存在视频", resp.status_code == 404, f"状态码: {resp.status_code}")

    # 4. 无Token访问
    old_token = runner.token
    runner.token = None
    resp = runner.request("GET", f"/api/video-playbacks/project/{project_id}")
    runner.token = old_token
    runner.log("无Token访问", resp.status_code == 401, f"状态码: {resp.status_code}")

    # 5. 删除不存在视频
    resp = runner.request("DELETE", "/api/video-playbacks/99999")
    runner.log("删除不存在视频", resp.status_code == 404, f"状态码: {resp.status_code}")

    # 6. 获取不存在视频链接
    resp = runner.request("GET", "/api/video-playbacks/99999/links")
    runner.log("获取不存在视频链接", resp.status_code == 404, f"状态码: {resp.status_code}")

    # 7. 获取不存在视频统计
    resp = runner.request("GET", "/api/video-playbacks/99999/statistics")
    runner.log("获取不存在视频统计", resp.status_code == 404, f"状态码: {resp.status_code}")

    # 8. 负数项目ID
    resp = runner.request("GET", "/api/video-playbacks/project/-1")
    runner.log("负数项目ID测试", resp.status_code in [400, 404, 422], f"状态码: {resp.status_code}")

    # 9. 数据结构验证
    resp = runner.request("GET", f"/api/video-playbacks/project/{project_id}")
    if resp.status_code == 200:
        videos = runner.extract_data(resp)
        if videos and len(videos) > 0:
            required = ["id", "project_id"]
            has_all = all(k in videos[0] for k in required)
            runner.log("数据结构验证", has_all, "包含必要字段" if has_all else "缺少必要字段")
        else:
            runner.log("数据结构验证", True, "无视频数据")
    else:
        runner.log("数据结构验证", False, f"状态码: {resp.status_code}")

    # 10. 验证链接添加不存在视频
    resp = runner.request("POST", "/api/video-playbacks/99999/links", data={"platform": "bilibili", "url": "https://test.com"})
    runner.log("添加链接到不存在视频", resp.status_code in [404, 422], f"状态码: {resp.status_code}")

    # 11. 删除不存在链接
    resp = runner.request("DELETE", "/api/video-playbacks/links/99999")
    runner.log("删除不存在链接", resp.status_code == 404, f"状态码: {resp.status_code}")

    # 12. 分页参数测试
    resp = runner.request("GET", f"/api/video-playbacks/project/{project_id}", params={"skip": 0, "limit": 10})
    runner.log("分页参数测试", resp.status_code == 200, f"状态码: {resp.status_code}")

    report_file = runner.save_report()
    print(f"\n报告已保存: {report_file}")
    return runner.summary()

if __name__ == "__main__":
    success = test_video_playbacks()
    sys.exit(0 if success else 1)
