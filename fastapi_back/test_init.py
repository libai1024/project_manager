#!/usr/bin/env python3
"""
测试数据库初始化功能
"""
import sys
import os

# 添加当前目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    print("正在测试数据库初始化...")
    
    # 导入所有必要的模块
    from sqlmodel import Session, select, SQLModel
    from app.core.database import engine
    from app.core.security import get_password_hash, verify_password
    from app.models.user import User
    from app.models.platform import Platform
    from app.models.project import Project, ProjectStep
    from app.models.attachment import Attachment
    
    print("✅ 所有模块导入成功")
    
    # 创建所有表
    print("\n正在创建数据库表...")
    SQLModel.metadata.create_all(engine)
    print("✅ 数据库表创建成功")
    
    # 测试密码哈希
    print("\n正在测试密码哈希...")
    test_password = "admin123"
    password_hash = get_password_hash(test_password)
    print(f"✅ 密码哈希生成成功: {password_hash[:30]}...")
    
    # 验证密码
    is_valid = verify_password(test_password, password_hash)
    print(f"✅ 密码验证: {'通过' if is_valid else '失败'}")
    
    # 测试创建管理员用户
    print("\n正在测试创建管理员用户...")
    with Session(engine) as session:
        # 检查是否已存在管理员
        admin = session.exec(select(User).where(User.username == "admin")).first()
        if not admin:
            admin = User(
                username="admin",
                password_hash=password_hash,
                role="admin"
            )
            session.add(admin)
            session.commit()
            print("✅ 管理员用户创建成功")
        else:
            print("ℹ️  管理员用户已存在")
    
    print("\n✅ 所有测试通过！")
    sys.exit(0)
    
except Exception as e:
    print(f"\n❌ 错误: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

