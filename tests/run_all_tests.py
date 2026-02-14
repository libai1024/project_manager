#!/usr/bin/env python3
"""
运行所有API测试的主脚本
"""
import subprocess
import os
import sys
from datetime import datetime

# 测试模块配置
TEST_MODULES = [
    ("auth", "tests/auth/test_auth.py", 10),
    ("users", "tests/users/test_users.py", 10),
    ("platforms", "tests/platforms/test_platforms.py", 10),
    ("projects", "tests/projects/test_projects.py", 15),
    ("attachments", "tests/attachments/test_attachments.py", 20),
    ("folders", "tests/folders/test_folders.py", 10),
    ("tags", "tests/tags/test_tags.py", 12),
    ("todos", "tests/todos/test_todos.py", 12),
    ("dashboard", "tests/dashboard/test_dashboard.py", 10),
    ("historical_projects", "tests/historical_projects/test_historical_projects.py", 12),
    ("system_settings", "tests/system_settings/test_system_settings.py", 10),
    ("project_logs", "tests/project_logs/test_project_logs.py", 10),
    ("project_parts", "tests/project_parts/test_project_parts.py", 10),
    ("step_templates", "tests/step_templates/test_step_templates.py", 10),
    ("health", "tests/health/test_health.py", 8),
]

def run_test(module_name, script_path):
    """运行单个测试模块"""
    print(f"\n{'='*60}")
    print(f" 运行: {module_name}")
    print(f"{'='*60}")

    result = subprocess.run(
        [sys.executable, script_path],
        cwd="/Users/wangwei/Money/project_manager",
        capture_output=True,
        text=True
    )

    print(result.stdout)
    if result.stderr:
        print(f"错误: {result.stderr}")

    return result.returncode == 0


def main():
    print("\n" + "="*60)
    print("   外包项目管理系统 - API 全面测试")
    print("   总目标: 150+ 测试用例")
    print("="*60)
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    base_dir = "/Users/wangwei/Money/project_manager"
    results = {}
    total_passed = 0
    total_tests = 0

    for module_name, script_path, expected_tests in TEST_MODULES:
        full_path = os.path.join(base_dir, script_path)
        if os.path.exists(full_path):
            success = run_test(module_name, full_path)
            results[module_name] = "PASS" if success else "FAIL"
            total_tests += expected_tests
        else:
            print(f"跳过 {module_name}: 测试文件不存在")
            results[module_name] = "SKIP"

    # 生成总报告
    print("\n" + "="*60)
    print("   测试总结")
    print("="*60)

    report_path = os.path.join(base_dir, "tests/reports/summary_report.md")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# API 测试总报告\n\n")
        f.write(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("## 模块测试结果\n\n")
        f.write("| 模块 | 状态 | 测试文件 |\n")
        f.write("|------|------|----------|\n")
        for module_name, script_path, _ in TEST_MODULES:
            status = results.get(module_name, "SKIP")
            status_icon = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⏭️"
            f.write(f"| {module_name} | {status_icon} {status} | {script_path} |\n")

    print(f"\n总报告已保存: {report_path}")
    print("="*60)


if __name__ == "__main__":
    main()
