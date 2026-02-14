#!/usr/bin/env python3
"""
API 05 - 附件管理模块测试
测试用例: 15个
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from base_test import TestRunner
import io

def test_attachments():
    """附件管理模块测试"""
    runner = TestRunner("附件管理", os.path.dirname(os.path.abspath(__file__)))

    print(f"\n{'='*50}")
    print(" API 05 - 附件管理")
    print(f"{'='*50}\n")

    # 登录
    if not runner.login():
        print("登录失败，无法继续测试")
        return False

    # 获取或创建测试项目
    resp = runner.request("GET", "/api/projects/")
    if resp.status_code == 200:
        projects = runner.extract_data(resp)
        if projects:
            runner.real_data["test_project_id"] = projects[0]["id"]
        else:
            # 创建测试项目
            platforms_resp = runner.request("GET", "/api/platforms/")
            platforms = runner.extract_data(platforms_resp)
            platform_id = platforms[0]["id"] if platforms else 1
            resp = runner.request("POST", "/api/projects/", data={
                "title": "附件测试项目",
                "platform_id": platform_id
            })
            data = runner.extract_data(resp)
            runner.real_data["test_project_id"] = data.get("id") if data else 1

    project_id = runner.real_data.get("test_project_id")

    # 1. 获取项目附件列表
    if project_id:
        resp = runner.request("GET", f"/api/attachments/project/{project_id}")
        if resp.status_code == 200:
            attachments = runner.extract_data(resp)
            runner.real_data["attachments"] = attachments
            runner.log("获取项目附件列表", True, f"附件数: {len(attachments) if attachments else 0}")
        else:
            runner.log("获取项目附件列表", False, f"状态码: {resp.status_code}")
    else:
        runner.skip("获取项目附件列表", "无测试项目ID")

    # 2. 上传文本文件
    if project_id:
        test_content = b"Hello, this is a test file for attachment upload."
        files = {"file": ("test_upload.txt", io.BytesIO(test_content), "text/plain")}
        data = {"file_type": "其他"}
        resp = runner.request("POST", f"/api/attachments/project/{project_id}", data=data, files=files)
        if resp.status_code == 200:
            attachment = runner.extract_data(resp)
            if attachment:
                runner.real_data["test_attachment_id"] = attachment.get("id")
                runner.log("上传文本文件", True, f"附件ID: {attachment.get('id')}")
            else:
                runner.log("上传文本文件", False, "响应数据为空")
        else:
            runner.log("上传文本文件", False, f"状态码: {resp.status_code}, {resp.text[:100]}")
    else:
        runner.skip("上传文本文件", "无测试项目ID")

    # 3. 获取附件详情
    attachment_id = runner.real_data.get("test_attachment_id")
    if attachment_id:
        resp = runner.request("GET", f"/api/attachments/{attachment_id}")
        if resp.status_code == 200:
            data = runner.extract_data(resp)
            runner.log("获取附件详情", True, f"文件名: {data.get('file_name') if data else 'N/A'}")
        else:
            runner.log("获取附件详情", False, f"状态码: {resp.status_code}")
    else:
        runner.skip("获取附件详情", "无测试附件ID")

    # 4. 下载附件
    if attachment_id:
        resp = runner.request("GET", f"/api/attachments/{attachment_id}/download")
        is_success = resp.status_code == 200 and len(resp.content) > 0
        runner.log("下载附件", is_success, f"状态码: {resp.status_code}, 大小: {len(resp.content)}字节")
    else:
        runner.skip("下载附件", "无测试附件ID")

    # 5. 预览附件
    if attachment_id:
        resp = runner.request("GET", f"/api/attachments/{attachment_id}/preview")
        runner.log("预览附件", resp.status_code == 200, f"状态码: {resp.status_code}")
    else:
        runner.skip("预览附件", "无测试附件ID")

    # 6. 更新附件信息
    if attachment_id:
        resp = runner.request("PUT", f"/api/attachments/{attachment_id}", data={
            "description": "更新后的附件描述"
        })
        runner.log("更新附件信息", resp.status_code == 200, f"状态码: {resp.status_code}")
    else:
        runner.skip("更新附件信息", "无测试附件ID")

    # 7. 复制附件
    if attachment_id:
        resp = runner.request("POST", f"/api/attachments/{attachment_id}/copy")
        if resp.status_code == 200:
            data = runner.extract_data(resp)
            if data:
                runner.real_data["copied_attachment_id"] = data.get("id")
            runner.log("复制附件", True, f"复制后ID: {data.get('id') if data else 'N/A'}")
        else:
            runner.log("复制附件", False, f"状态码: {resp.status_code}")
    else:
        runner.skip("复制附件", "无测试附件ID")

    # 8. 批量获取附件
    if attachment_id:
        # API期望直接传入ID数组
        resp = runner.request("POST", "/api/attachments/batch", data=[attachment_id])
        if resp.status_code == 200:
            data = runner.extract_data(resp)
            runner.log("批量获取附件", True, f"返回附件数: {len(data) if data else 0}")
        else:
            runner.log("批量获取附件", False, f"状态码: {resp.status_code}")
    else:
        runner.skip("批量获取附件", "无测试附件ID")

    # 9. 获取不存在的附件
    resp = runner.request("GET", "/api/attachments/99999")
    runner.log("获取不存在附件", resp.status_code == 404, f"状态码: {resp.status_code}")

    # 10. 下载不存在的附件
    resp = runner.request("GET", "/api/attachments/99999/download")
    runner.log("下载不存在附件", resp.status_code == 404, f"状态码: {resp.status_code}")

    # 11. 预览不存在的附件
    resp = runner.request("GET", "/api/attachments/99999/preview")
    runner.log("预览不存在附件", resp.status_code == 404, f"状态码: {resp.status_code}")

    # 12. 无Token访问
    old_token = runner.token
    runner.token = None
    resp = runner.request("GET", f"/api/attachments/project/{project_id}" if project_id else "/api/attachments/project/1")
    runner.token = old_token
    runner.log("无Token访问", resp.status_code == 401, f"状态码: {resp.status_code}")

    # 13. 上传中文文件名文件
    if project_id:
        test_content = "中文文件名测试".encode('utf-8')
        files = {"file": ("测试文件_中文.txt", io.BytesIO(test_content), "text/plain")}
        data = {"file_type": "其他"}
        resp = runner.request("POST", f"/api/attachments/project/{project_id}", data=data, files=files)
        runner.log("上传中文文件名", resp.status_code == 200, f"状态码: {resp.status_code}")
    else:
        runner.skip("上传中文文件名", "无测试项目ID")

    # 14. 删除复制的附件（清理）
    copied_id = runner.real_data.get("copied_attachment_id")
    if copied_id:
        resp = runner.request("DELETE", f"/api/attachments/{copied_id}")
        runner.log("删除复制的附件", resp.status_code == 200, f"状态码: {resp.status_code}")
    else:
        runner.skip("删除复制的附件", "无复制附件ID")

    # 15. 删除测试附件（清理）
    if attachment_id:
        resp = runner.request("DELETE", f"/api/attachments/{attachment_id}")
        runner.log("删除测试附件", resp.status_code == 200, f"状态码: {resp.status_code}")
    else:
        runner.skip("删除测试附件", "无测试附件ID")

    # 保存报告
    report_file = runner.save_report()
    print(f"\n报告已保存: {report_file}")

    return runner.summary()


if __name__ == "__main__":
    success = test_attachments()
    sys.exit(0 if success else 1)
