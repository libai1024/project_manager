#!/usr/bin/env python3
"""
验证环境设置是否正确
"""
import sys
import os

# 添加当前目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def check_imports():
    """检查所有必要的导入"""
    print("=" * 50)
    print("1. 检查模块导入...")
    print("=" * 50)
    
    try:
        from app.models.user import User
        print("✅ User 模型")
        
        from app.models.platform import Platform
        print("✅ Platform 模型")
        
        from app.models.project import Project, ProjectStep
        print("✅ Project 和 ProjectStep 模型")
        
        from app.models.attachment import Attachment
        print("✅ Attachment 模型")
        
        return True
    except Exception as e:
        print(f"❌ 导入失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_password_hashing():
    """检查密码哈希功能"""
    print("\n" + "=" * 50)
    print("2. 检查密码哈希功能...")
    print("=" * 50)
    
    try:
        from app.core.security import get_password_hash, verify_password
        
        # 测试正常密码
        password = "admin123"
        print(f"\n测试密码: {password}")
        
        hash_result = get_password_hash(password)
        print(f"✅ 哈希生成成功: {hash_result[:30]}...")
        
        # 验证密码
        if verify_password(password, hash_result):
            print("✅ 密码验证成功")
        else:
            print("❌ 密码验证失败")
            return False
        
        # 测试错误密码
        if not verify_password("wrong", hash_result):
            print("✅ 错误密码正确拒绝")
        else:
            print("❌ 错误密码验证应该失败")
            return False
        
        return True
    except Exception as e:
        print(f"❌ 密码哈希测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_database():
    """检查数据库连接和表创建"""
    print("\n" + "=" * 50)
    print("3. 检查数据库...")
    print("=" * 50)
    
    try:
        from sqlmodel import Session, select, SQLModel
        from app.core.database import engine
        from app.models.user import User
        
        # 创建表
        print("\n创建数据库表...")
        SQLModel.metadata.create_all(engine)
        print("✅ 数据库表创建成功")
        
        # 测试数据库连接
        print("\n测试数据库连接...")
        with Session(engine) as session:
            users = session.exec(select(User)).all()
            print(f"✅ 数据库连接成功，当前用户数: {len(users)}")
        
        return True
    except Exception as e:
        print(f"❌ 数据库测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("\n" + "=" * 50)
    print("  环境验证脚本")
    print("=" * 50 + "\n")
    
    results = []
    
    # 运行所有检查
    results.append(("模块导入", check_imports()))
    results.append(("密码哈希", check_password_hashing()))
    results.append(("数据库", check_database()))
    
    # 汇总结果
    print("\n" + "=" * 50)
    print("验证结果汇总")
    print("=" * 50)
    
    all_passed = True
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{name}: {status}")
        if not result:
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("✅ 所有检查通过！环境配置正确。")
        sys.exit(0)
    else:
        print("❌ 部分检查失败，请查看上面的错误信息。")
        sys.exit(1)

if __name__ == "__main__":
    main()

