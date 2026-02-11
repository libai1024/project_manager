#!/usr/bin/env python3
"""
重置管理员密码
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlmodel import Session, select
from app.core.database import engine
from app.models.user import User
from app.core.security import get_password_hash, verify_password

def reset_admin_password():
    """重置管理员密码"""
    print("=" * 50)
    print("重置管理员密码")
    print("=" * 50)
    
    password = "admin123"
    
    with Session(engine) as session:
        # 查找管理员用户
        admin = session.exec(select(User).where(User.username == "admin")).first()
        
        if not admin:
            print("\n❌ 未找到管理员用户，正在创建...")
            admin = User(
                username="admin",
                password_hash=get_password_hash(password),
                role="admin"
            )
            session.add(admin)
            print("✅ 管理员用户已创建")
        else:
            print(f"\n找到管理员用户: {admin.username}")
            print(f"当前密码哈希: {admin.password_hash[:30]}...")
            
            # 测试当前密码
            if verify_password(password, admin.password_hash):
                print("✅ 当前密码验证成功，无需重置")
                return
            
            # 重置密码
            print("\n正在重置密码...")
            admin.password_hash = get_password_hash(password)
            session.add(admin)
            print("✅ 密码已重置")
        
        session.commit()
        
        # 验证新密码
        session.refresh(admin)
        if verify_password(password, admin.password_hash):
            print(f"\n✅ 密码重置成功！")
            print(f"   用户名: admin")
            print(f"   密码: {password}")
        else:
            print("\n❌ 密码重置后验证失败！")

if __name__ == "__main__":
    reset_admin_password()

