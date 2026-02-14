#!/usr/bin/env python3
"""
API 14 - 步骤模板模块测试
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from base_test import TestRunner

def test_step_templates():
    """步骤模板模块测试"""
    runner = TestRunner("步骤模板", os.path.dirname(os.path.abspath(__file__)))

    print(f"\n{'='*50}")
    print(" API 14 - 步骤模板")
    print(f"{'='*50}\n")

    if not runner.login():
        print("登录失败，无法继续测试")
        return False

    # 1. 获取模板列表
    resp = runner.request("GET", "/api/step-templates/")
    if resp.status_code == 200:
        templates = runner.extract_data(resp)
        runner.real_data["templates"] = templates
        runner.log("获取模板列表", True, f"模板数: {len(templates) if templates else 0}")
    else:
        runner.log("获取模板列表", False, f"状态码: {resp.status_code}")

    # 2. 创建模板 (使用正确的字段，steps是必需的)
    import time
    template_name = f"测试模板_{int(time.time())}"
    resp = runner.request("POST", "/api/step-templates/", data={
        "name": template_name,
        "description": "测试描述",
        "steps": ["步骤1", "步骤2", "步骤3"]
    })
    if resp.status_code == 200:
        data = runner.extract_data(resp)
        runner.real_data["test_template_id"] = data.get("id") if data else None
        runner.log("创建模板", True, f"ID: {data.get('id') if data else 'N/A'}")
    else:
        runner.log("创建模板", False, f"状态码: {resp.status_code}, {resp.text[:100] if hasattr(resp, 'text') else ''}")

    # 3. 获取模板详情
    template_id = runner.real_data.get("test_template_id")
    if template_id:
        resp = runner.request("GET", f"/api/step-templates/{template_id}")
        runner.log("获取模板详情", resp.status_code == 200, f"状态码: {resp.status_code}")
    else:
        runner.skip("获取模板详情", "无测试模板ID")

    # 4. 更新模板
    if template_id:
        resp = runner.request("PUT", f"/api/step-templates/{template_id}", data={"name": f"更新_{template_name}"})
        runner.log("更新模板", resp.status_code == 200, f"状态码: {resp.status_code}")
    else:
        runner.skip("更新模板", "无测试模板ID")

    # 5. 获取不存在模板
    resp = runner.request("GET", "/api/step-templates/99999")
    runner.log("获取不存在模板", resp.status_code == 404, f"状态码: {resp.status_code}")

    # 6. 无Token访问
    old_token = runner.token
    runner.token = None
    resp = runner.request("GET", "/api/step-templates/")
    runner.token = old_token
    runner.log("无Token访问", resp.status_code == 401, f"状态码: {resp.status_code}")

    # 7. 删除模板
    if template_id:
        resp = runner.request("DELETE", f"/api/step-templates/{template_id}")
        runner.log("删除模板", resp.status_code == 200, f"状态码: {resp.status_code}")
    else:
        runner.skip("删除模板", "无测试模板ID")

    # 8. 删除不存在模板
    resp = runner.request("DELETE", "/api/step-templates/99999")
    runner.log("删除不存在模板", resp.status_code == 404, f"状态码: {resp.status_code}")

    # 9. 创建空名称模板
    resp = runner.request("POST", "/api/step-templates/", data={"name": "", "steps": ["步骤1"]})
    runner.log("创建空名称模板", resp.status_code in [400, 422], f"状态码: {resp.status_code}")

    # 10. 创建空步骤列表模板
    resp = runner.request("POST", "/api/step-templates/", data={"name": "测试", "steps": []})
    runner.log("创建空步骤列表模板", resp.status_code in [200, 400, 422], f"状态码: {resp.status_code}")

    # 11. 数据结构验证
    resp = runner.request("GET", "/api/step-templates/")
    if resp.status_code == 200:
        templates = runner.extract_data(resp)
        if templates and len(templates) > 0:
            required = ["id", "name"]
            has_all = all(k in templates[0] for k in required)
            runner.log("数据结构验证", has_all, "包含必要字段" if has_all else "缺少必要字段")
        else:
            runner.log("数据结构验证", True, "无模板数据")
    else:
        runner.log("数据结构验证", False, f"状态码: {resp.status_code}")

    report_file = runner.save_report()
    print(f"\n报告已保存: {report_file}")
    return runner.summary()

if __name__ == "__main__":
    success = test_step_templates()
    sys.exit(0 if success else 1)
