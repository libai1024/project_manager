#!/usr/bin/env python3
"""
测试模型导入是否正常
"""
import sys
import os

# 添加当前目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    print("正在测试模型导入...")
    
    # 测试导入所有模型
    from app.models.user import User
    print("✅ User 模型导入成功")
    
    from app.models.platform import Platform
    print("✅ Platform 模型导入成功")
    
    from app.models.project import Project, ProjectStep
    print("✅ Project 和 ProjectStep 模型导入成功")
    
    from app.models.attachment import Attachment
    print("✅ Attachment 模型导入成功")
    
    # 测试关系定义
    print("\n正在测试关系定义...")
    project = Project.__dict__
    if 'steps' in project:
        print("✅ Project.steps 关系定义成功")
    if 'attachments' in project:
        print("✅ Project.attachments 关系定义成功")
    
    print("\n✅ 所有模型测试通过！")
    sys.exit(0)
    
except Exception as e:
    print(f"\n❌ 错误: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

