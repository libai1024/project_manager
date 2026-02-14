#!/usr/bin/env python3
"""
附件管理模块 (Attachments) 测试 - 20个用例
包含完整的文件上传和下载测试
"""
import sys
import os
import io
import json
import time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from test_utils import *

def test_attachments():
    """附件管理模块测试"""
    module = "附件管理"
    tests = []
    print_module_header(module, 20)

    # 获取token和项目ID
    token = get_admin_token()
    if not token:
        print("无法获取Token，跳过测试")
        return tests

    # 先获取项目列表
    resp = make_request("GET", "/api/projects/", token=token)
    project_id = 1
    if resp.status_code == 200:
        projects = extract_data(resp)
        if projects and len(projects) > 0:
            project_id = projects[0].get("id", 1)

    # ========== 文件上传测试 ==========

    # 1. 上传文本文件
    text_content = b"Hello, this is a test file for API testing."
    files = {"file": ("test.txt", io.BytesIO(text_content), "text/plain")}
    data = {"file_type": "其他", "description": "API测试文本文件"}
    resp = make_request("POST", f"/api/attachments/project/{project_id}", token=token, files=files, data=data)
    if resp.status_code == 200:
        att_id = resp.json().get("id")
        if att_id:
            created_data["attachments"].append(att_id)
            real_data["attachments"].append(att_id)
        tests.append({"name": "上传文本文件", "result": "PASS", "detail": f"附件ID: {att_id}"})
    else:
        tests.append({"name": "上传文本文件", "result": "FAIL", "detail": f"状态码: {resp.status_code}"})
    log_test(module, tests[-1]["name"], tests[-1]["result"], tests[-1].get("detail", ""))

    # 2. 上传JSON文件
    json_content = json.dumps({"test": "data", "timestamp": time.time()}).encode()
    files = {"file": ("test.json", io.BytesIO(json_content), "application/json")}
    resp = make_request("POST", f"/api/attachments/project/{project_id}", token=token, files=files, data=data)
    tests.append({"name": "上传JSON文件", "result": "PASS" if resp.status_code == 200 else "FAIL", "detail": f"状态码: {resp.status_code}"})
    log_test(module, tests[-1]["name"], tests[-1]["result"])

    # 3. 上传Markdown文件
    md_content = b"# Test Markdown\n\nThis is a **test** markdown file."
    files = {"file": ("test.md", io.BytesIO(md_content), "text/markdown")}
    resp = make_request("POST", f"/api/attachments/project/{project_id}", token=token, files=files, data=data)
    tests.append({"name": "上传Markdown文件", "result": "PASS" if resp.status_code == 200 else "FAIL", "detail": f"状态码: {resp.status_code}"})
    log_test(module, tests[-1]["name"], tests[-1]["result"])

    # 4. 上传图片文件 (模拟PNG)
    png_header = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde'
    files = {"file": ("test.png", io.BytesIO(png_header), "image/png")}
    resp = make_request("POST", f"/api/attachments/project/{project_id}", token=token, files=files, data=data)
    tests.append({"name": "上传图片文件", "result": "PASS" if resp.status_code == 200 else "FAIL", "detail": f"状态码: {resp.status_code}"})
    log_test(module, tests[-1]["name"], tests[-1]["result"])

    # 5. 上传中文文件名文件
    chinese_content = "中文文件名测试内容".encode('utf-8')
    files = {"file": ("测试文件_中文.txt", io.BytesIO(chinese_content), "text/plain")}
    resp = make_request("POST", f"/api/attachments/project/{project_id}", token=token, files=files, data=data)
    tests.append({"name": "上传中文文件名", "result": "PASS" if resp.status_code == 200 else "FAIL", "detail": f"状态码: {resp.status_code}"})
    log_test(module, tests[-1]["name"], tests[-1]["result"])

    # 6. 上传长文件名文件
    long_name = "a" * 200 + ".txt"
    files = {"file": (long_name, io.BytesIO(text_content), "text/plain")}
    resp = make_request("POST", f"/api/attachments/project/{project_id}", token=token, files=files, data=data)
    tests.append({"name": "上传长文件名文件", "result": "PASS" if resp.status_code == 200 else "FAIL", "detail": f"状态码: {resp.status_code}"})
    log_test(module, tests[-1]["name"], tests[-1]["result"])

    # 7. 无Token上传
    files = {"file": ("noauth.txt", io.BytesIO(text_content), "text/plain")}
    resp = make_request("POST", f"/api/attachments/project/{project_id}", files=files, data=data)
    tests.append({"name": "无Token上传文件", "result": "PASS" if resp.status_code == 401 else "FAIL", "detail": f"状态码: {resp.status_code}"})
    log_test(module, tests[-1]["name"], tests[-1]["result"])

    # 8. 上传到不存在项目
    files = {"file": ("test.txt", io.BytesIO(text_content), "text/plain")}
    resp = make_request("POST", "/api/attachments/project/99999", token=token, files=files, data=data)
    tests.append({"name": "上传到不存在项目", "result": "PASS" if resp.status_code in [404, 403] else "FAIL", "detail": f"状态码: {resp.status_code}"})
    log_test(module, tests[-1]["name"], tests[-1]["result"])

    # ========== 文件下载测试 ==========

    # 9. 获取项目附件列表
    resp = make_request("GET", f"/api/attachments/project/{project_id}", token=token)
    if resp.status_code == 200:
        attachments = resp.json()
        if attachments:
            for a in attachments:
                if a["id"] not in real_data["attachments"]:
                    real_data["attachments"].append(a["id"])
        tests.append({"name": "获取项目附件列表", "result": "PASS", "detail": f"附件数: {len(attachments)}"})
    else:
        tests.append({"name": "获取项目附件列表", "result": "FAIL", "detail": f"状态码: {resp.status_code}"})
    log_test(module, tests[-1]["name"], tests[-1]["result"], tests[-1].get("detail", ""))

    # 10. 下载附件
    if real_data["attachments"]:
        resp = make_request("GET", f"/api/attachments/{real_data['attachments'][0]}/download", token=token)
        if resp.status_code == 200:
            content_type = resp.headers.get("Content-Type", "")
            content_disp = resp.headers.get("Content-Disposition", "")
            tests.append({"name": "下载附件", "result": "PASS", "detail": f"Content-Type: {content_type[:30]}"})
        else:
            tests.append({"name": "下载附件", "result": "FAIL", "detail": f"状态码: {resp.status_code}"})
    else:
        tests.append({"name": "下载附件", "result": "SKIP", "detail": "无附件可下载"})
    log_test(module, tests[-1]["name"], tests[-1]["result"])

    # 11. 下载附件内容验证
    if created_data["attachments"]:
        resp = make_request("GET", f"/api/attachments/{created_data['attachments'][0]}/download", token=token)
        if resp.status_code == 200 and resp.content:
            tests.append({"name": "下载附件内容验证", "result": "PASS", "detail": f"内容大小: {len(resp.content)} bytes"})
        else:
            tests.append({"name": "下载附件内容验证", "result": "FAIL", "detail": f"状态码: {resp.status_code}"})
    else:
        tests.append({"name": "下载附件内容验证", "result": "SKIP", "detail": "无附件"})
    log_test(module, tests[-1]["name"], tests[-1]["result"])

    # 12. 下载不存在附件
    resp = make_request("GET", "/api/attachments/99999/download", token=token)
    tests.append({"name": "下载不存在附件", "result": "PASS" if resp.status_code == 404 else "FAIL", "detail": f"状态码: {resp.status_code}"})
    log_test(module, tests[-1]["name"], tests[-1]["result"])

    # ========== 文件预览测试 ==========

    # 13. 预览附件
    if real_data["attachments"]:
        resp = make_request("GET", f"/api/attachments/{real_data['attachments'][0]}/preview", token=token)
        tests.append({"name": "预览附件", "result": "PASS" if resp.status_code == 200 else "FAIL", "detail": f"状态码: {resp.status_code}"})
    else:
        tests.append({"name": "预览附件", "result": "SKIP", "detail": "无附件"})
    log_test(module, tests[-1]["name"], tests[-1]["result"])

    # 14. 预览文本文件
    if created_data["attachments"]:
        resp = make_request("GET", f"/api/attachments/{created_data['attachments'][0]}/preview", token=token)
        tests.append({"name": "预览文本文件", "result": "PASS" if resp.status_code == 200 else "FAIL", "detail": f"状态码: {resp.status_code}"})
    else:
        tests.append({"name": "预览文本文件", "result": "SKIP", "detail": "无附件"})
    log_test(module, tests[-1]["name"], tests[-1]["result"])

    # 15. 预览不存在附件
    resp = make_request("GET", "/api/attachments/99999/preview", token=token)
    tests.append({"name": "预览不存在附件", "result": "PASS" if resp.status_code == 404 else "FAIL", "detail": f"状态码: {resp.status_code}"})
    log_test(module, tests[-1]["name"], tests[-1]["result"])

    # ========== 其他操作测试 ==========

    # 16. 获取附件详情
    if real_data["attachments"]:
        resp = make_request("GET", f"/api/attachments/{real_data['attachments'][0]}", token=token)
        tests.append({"name": "获取附件详情", "result": "PASS" if resp.status_code == 200 else "FAIL", "detail": f"状态码: {resp.status_code}"})
    else:
        tests.append({"name": "获取附件详情", "result": "SKIP", "detail": "无附件"})
    log_test(module, tests[-1]["name"], tests[-1]["result"])

    # 17. 更新附件信息
    if real_data["attachments"]:
        resp = make_request("PUT", f"/api/attachments/{real_data['attachments'][0]}", token=token, data={
            "description": f"更新描述_{int(time.time())}"
        })
        tests.append({"name": "更新附件信息", "result": "PASS" if resp.status_code == 200 else "FAIL", "detail": f"状态码: {resp.status_code}"})
    else:
        tests.append({"name": "更新附件信息", "result": "SKIP", "detail": "无附件"})
    log_test(module, tests[-1]["name"], tests[-1]["result"])

    # 18. 批量获取附件
    if len(real_data["attachments"]) >= 2:
        resp = make_request("POST", "/api/attachments/batch", token=token, data=real_data["attachments"][:3])
        tests.append({"name": "批量获取附件", "result": "PASS" if resp.status_code == 200 else "FAIL", "detail": f"状态码: {resp.status_code}"})
    else:
        tests.append({"name": "批量获取附件", "result": "SKIP", "detail": "附件数量不足"})
    log_test(module, tests[-1]["name"], tests[-1]["result"])

    # 19. 复制附件
    if real_data["attachments"]:
        resp = make_request("POST", f"/api/attachments/{real_data['attachments'][0]}/copy", token=token, data={
            "target_project_id": project_id
        })
        tests.append({"name": "复制附件", "result": "PASS" if resp.status_code == 200 else "FAIL", "detail": f"状态码: {resp.status_code}"})
    else:
        tests.append({"name": "复制附件", "result": "SKIP", "detail": "无附件"})
    log_test(module, tests[-1]["name"], tests[-1]["result"])

    # 20. 无Token下载
    if real_data["attachments"]:
        resp = make_request("GET", f"/api/attachments/{real_data['attachments'][0]}/download")
        tests.append({"name": "无Token下载附件", "result": "PASS" if resp.status_code == 401 else "FAIL", "detail": f"状态码: {resp.status_code}"})
    else:
        tests.append({"name": "无Token下载附件", "result": "SKIP", "detail": "无附件"})
    log_test(module, tests[-1]["name"], tests[-1]["result"])

    # 保存报告
    save_report("attachments", tests)

    # 打印总结
    passed = sum(1 for t in tests if t["result"] == "PASS")
    failed = sum(1 for t in tests if t["result"] == "FAIL")
    skipped = sum(1 for t in tests if t["result"] == "SKIP")
    print_module_summary(module, passed, failed, skipped)

    return tests


if __name__ == "__main__":
    test_attachments()
