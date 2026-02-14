#!/usr/bin/env python3
"""
API 测试生成器
自动为新模块生成测试文件
"""
import os
import re
import sys
from pathlib import Path


# 模块名称中英文映射
MODULE_NAMES = {
    "auth": "认证模块",
    "users": "用户管理",
    "platforms": "平台管理",
    "projects": "项目管理",
    "attachments": "附件管理",
    "attachment_folders": "文件夹管理",
    "folders": "文件夹管理",
    "tags": "标签管理",
    "todos": "待办管理",
    "dashboard": "Dashboard",
    "historical_projects": "历史项目",
    "system_settings": "系统设置",
    "project_logs": "项目日志",
    "project_parts": "配件清单",
    "step_templates": "步骤模板",
    "health": "健康检查",
    "github_commits": "GitHub Commits",
    "video_playbacks": "视频回放",
}


def get_next_module_number(tests_dir: str) -> int:
    """获取下一个模块序号"""
    existing = []
    for item in os.listdir(tests_dir):
        if os.path.isdir(os.path.join(tests_dir, item)):
            match = re.match(r'^(\d+)_', item)
            if match:
                existing.append(int(match.group(1)))
    return max(existing, default=0) + 1


def analyze_api_file(api_path: str) -> dict:
    """分析 API 路由文件"""
    with open(api_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 提取路由前缀
    prefix_match = re.search(r'router\s*=\s*APIRouter\([^)]*prefix\s*=\s*["\']([^"\']+)["\']', content)
    prefix = prefix_match.group(1) if prefix_match else ""

    # 提取端点
    endpoints = []
    endpoint_pattern = r'@router\.(get|post|put|delete|patch)\(["\']([^"\']*)["\']'
    for match in re.finditer(endpoint_pattern, content, re.IGNORECASE):
        method = match.group(1).upper()
        path = match.group(2)
        endpoints.append({"method": method, "path": path})

    return {
        "prefix": prefix,
        "endpoints": endpoints
    }


def analyze_model_file(model_path: str) -> dict:
    """分析模型文件"""
    with open(model_path, 'r', encoding='utf-8') as f:
        content = f.read()

    fields = []

    # 提取表类
    table_match = re.search(r'class\s+(\w+)\(.*table=True', content)
    table_name = table_match.group(1) if table_match else None

    # 提取 Create 类的字段
    create_match = re.search(r'class\s+\w*Create[^:]*:\s*([^{\n]+)', content, re.DOTALL)
    if create_match:
        create_section = content[create_match.start():create_match.end()+500]

        # 提取字段定义
        field_pattern = r'(\w+)\s*:\s*(?:Optional\[)?(\w+)(?:\])?\s*=\s*Field\(([^)]*)\)'
        for match in re.finditer(field_pattern, create_section):
            field_name = match.group(1)
            field_type = match.group(2)
            field_attrs = match.group(3)

            # 检查是否必填
            is_required = "Optional" not in match.group(0) and "default" not in field_attrs.lower()

            fields.append({
                "name": field_name,
                "type": field_type,
                "required": is_required
            })

    return {
        "table_name": table_name,
        "fields": fields
    }


def generate_test_file(module_num: int, module_name: str, api_info: dict, model_info: dict) -> str:
    """生成测试文件内容"""
    cn_name = MODULE_NAMES.get(module_name, module_name)
    api_path = api_info.get("prefix", f"/{module_name}").lstrip("/")

    # 确定名称字段
    name_field = "name"
    for field in model_info.get("fields", []):
        if field["name"] in ["name", "title", "description"]:
            name_field = field["name"]
            break

    # 获取必填字段
    required_fields = [f for f in model_info.get("fields", []) if f.get("required")]

    template = f'''#!/usr/bin/env python3
"""
API {module_num} - {cn_name}模块测试
测试{cn_name}相关功能
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from base_test import TestRunner

def test_{module_name}():
    """{cn_name}模块测试"""
    runner = TestRunner("{cn_name}", os.path.dirname(os.path.abspath(__file__)))

    print(f"\\n{{'='*50}}")
    print(" API {module_num} - {cn_name}")
    print(f"{{'='*50}}\\n")

    if not runner.login():
        print("登录失败，无法继续测试")
        return False

    # 获取测试项目（如需要关联项目）
    resp = runner.request("GET", "/api/projects/")
    projects = runner.extract_data(resp)
    project_id = projects[0]["id"] if projects else 1

    # 1. 获取列表
    resp = runner.request("GET", "/api/{api_path}/")
    if resp.status_code == 200:
        items = runner.extract_data(resp)
        runner.log("获取{cn_name}列表", True, f"数量: {{len(items) if items else 0}}")
    else:
        runner.log("获取{cn_name}列表", False, f"状态码: {{resp.status_code}}")

    # 2. 创建
    import time
    item_name = f"测试{cn_name}_{{int(time.time())}}"
    resp = runner.request("POST", "/api/{api_path}/", data={{
        "{name_field}": item_name,
        # TODO: 添加其他必填字段
    }})
    if resp.status_code == 200:
        data = runner.extract_data(resp)
        runner.real_data["test_item_id"] = data.get("id") if data else None
        runner.log("创建{cn_name}", True, f"ID: {{data.get('id') if data else 'N/A'}}")
    else:
        runner.log("创建{cn_name}", False, f"状态码: {{resp.status_code}}, {{resp.text[:100] if hasattr(resp, 'text') else ''}}")

    item_id = runner.real_data.get("test_item_id")

    # 3. 获取详情
    if item_id:
        resp = runner.request("GET", f"/api/{api_path}/{{item_id}}")
        runner.log("获取{cn_name}详情", resp.status_code == 200, f"状态码: {{resp.status_code}}")
    else:
        runner.skip("获取{cn_name}详情", "无测试ID")

    # 4. 更新
    if item_id:
        resp = runner.request("PUT", f"/api/{api_path}/{{item_id}}", data={{
            "{name_field}": f"更新_{{item_name}}"
        }})
        runner.log("更新{cn_name}", resp.status_code == 200, f"状态码: {{resp.status_code}}")
    else:
        runner.skip("更新{cn_name}", "无测试ID")

    # 5. 删除
    if item_id:
        resp = runner.request("DELETE", f"/api/{api_path}/{{item_id}}")
        runner.log("删除{cn_name}", resp.status_code == 200, f"状态码: {{resp.status_code}}")
    else:
        runner.skip("删除{cn_name}", "无测试ID")

    # 6. 获取不存在资源
    resp = runner.request("GET", "/api/{api_path}/99999")
    runner.log("获取不存在{cn_name}", resp.status_code == 404, f"状态码: {{resp.status_code}}")

    # 7. 删除不存在资源
    resp = runner.request("DELETE", "/api/{api_path}/99999")
    runner.log("删除不存在{cn_name}", resp.status_code == 404, f"状态码: {{resp.status_code}}")

    # 8. 无Token访问
    old_token = runner.token
    runner.token = None
    resp = runner.request("GET", "/api/{api_path}/")
    runner.token = old_token
    runner.log("无Token访问", resp.status_code == 401, f"状态码: {{resp.status_code}}")

    # 9. 空{name_field}验证
    resp = runner.request("POST", "/api/{api_path}/", data={{"{name_field}": ""}})
    runner.log("创建空{name_field}{cn_name}", resp.status_code == 422, f"状态码: {{resp.status_code}}")

    # 10. 数据结构验证
    resp = runner.request("GET", "/api/{api_path}/")
    if resp.status_code == 200:
        items = runner.extract_data(resp)
        if items and len(items) > 0:
            required = ["id", "{name_field}"]
            has_all = all(k in items[0] for k in required)
            runner.log("{cn_name}数据结构验证", has_all, "包含必要字段" if has_all else "缺少必要字段")
        else:
            runner.log("{cn_name}数据结构验证", True, "无数据")
    else:
        runner.log("{cn_name}数据结构验证", False, f"状态码: {{resp.status_code}}")

    # 11. Docker部署验证
    resp = runner.request("GET", "/api/dashboard/stats")
    runner.log("Docker部署验证", resp.status_code == 200, f"后端服务正常，状态码: {{resp.status_code}}")

    report_file = runner.save_report()
    print(f"\\n报告已保存: {{report_file}}")
    return runner.summary()

if __name__ == "__main__":
    success = test_{module_name}()
    sys.exit(0 if success else 1)
'''

    return template


def create_test_module(module_name: str, api_file: str = None, model_file: str = None):
    """创建测试模块"""
    # 获取路径
    base_dir = Path(__file__).parent
    tests_dir = base_dir

    # 获取下一个序号
    module_num = get_next_module_number(str(tests_dir))

    # 分析文件
    api_info = {}
    model_info = {}

    if api_file and os.path.exists(api_file):
        api_info = analyze_api_file(api_file)

    if model_file and os.path.exists(model_file):
        model_info = analyze_model_file(model_file)

    # 创建目录
    module_dir = tests_dir / f"{module_num:02d}_{module_name}"
    module_dir.mkdir(exist_ok=True)

    # 创建 reports 目录
    (module_dir / "reports").mkdir(exist_ok=True)

    # 生成测试文件
    test_content = generate_test_file(module_num, module_name, api_info, model_info)
    test_file = module_dir / "test.py"

    with open(test_file, 'w', encoding='utf-8') as f:
        f.write(test_content)

    print(f"已创建测试模块: {module_dir}")
    print(f"测试文件: {test_file}")
    print(f"\n请编辑 {test_file} 添加其他必填字段和特殊测试用例")
    print(f"\n运行测试: python {test_file}")

    return str(test_file)


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法: python test_generator.py <模块名> [api文件路径] [model文件路径]")
        print("示例: python test_generator.py notifications")
        print("示例: python test_generator.py notifications fastapi_back/app/api/notifications.py fastapi_back/app/models/notification.py")
        sys.exit(1)

    module_name = sys.argv[1]
    api_file = sys.argv[2] if len(sys.argv) > 2 else None
    model_file = sys.argv[3] if len(sys.argv) > 3 else None

    # 自动查找文件
    base_path = Path(__file__).parent.parent / "fastapi_back" / "app"

    if not api_file:
        # 尝试查找 API 文件
        api_dir = base_path / "api"
        for f in api_dir.glob("*.py"):
            if module_name in f.name:
                api_file = str(f)
                break

    if not model_file:
        # 尝试查找 model 文件
        model_dir = base_path / "models"
        for f in model_dir.glob("*.py"):
            if module_name.rstrip('s') in f.name or module_name in f.name:
                model_file = str(f)
                break

    create_test_module(module_name, api_file, model_file)


if __name__ == "__main__":
    main()
