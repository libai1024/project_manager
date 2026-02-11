#!/usr/bin/env python3
"""
检查数据库中的用户
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlmodel import Session, select
from app.core.database import engine
from app.models.user import User
from app.core.security import verify_password, get_password_hash

def check_users():
    """检查数据库中的用户"""
    print("=" * 50)
    print("检查数据库中的用户")
    print("=" * 50)
    
    with Session(engine) as session:
        users = session.exec(select(User)).all()
        
        if not users:
            print("\n❌ 数据库中没有用户！")
            print("请运行: python -m app.init_db")
            return False
        
        print(f"\n找到 {len(users)} 个用户：\n")
        
        for user in users:
            print(f"用户名: {user.username}")
            print(f"角色: {user.role}")
            print(f"密码哈希: {user.password_hash[:30]}...")
            
            # 测试密码验证
            test_password = "admin123"
            if verify_password(test_password, user.password_hash):
                print(f"✅ 密码 '{test_password}' 验证成功")
            else:
                print(f"❌ 密码 '{test_password}' 验证失败")
            
            print("-" * 50)
        
        return True

if __name__ == "__main__":
    check_users()

