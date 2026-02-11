#!/usr/bin/env python3
"""
直接测试 bcrypt 功能
"""
import sys
import os
import bcrypt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_bcrypt():
    """测试 bcrypt 功能"""
    print("=" * 50)
    print("测试 bcrypt 功能")
    print("=" * 50)
    
    password = "admin123"
    print(f"\n测试密码: {password}")
    
    # 转换为字节
    password_bytes = password.encode('utf-8')
    print(f"密码字节长度: {len(password_bytes)}")
    
    # 生成哈希
    try:
        salt = bcrypt.gensalt(rounds=12)
        print(f"✅ Salt 生成成功")
        
        hashed = bcrypt.hashpw(password_bytes, salt)
        print(f"✅ 密码哈希生成成功: {hashed.decode('utf-8')[:30]}...")
        
        # 验证密码
        if bcrypt.checkpw(password_bytes, hashed):
            print("✅ 密码验证成功")
        else:
            print("❌ 密码验证失败")
            return False
        
        # 测试错误密码
        wrong_password = "wrong".encode('utf-8')
        if not bcrypt.checkpw(wrong_password, hashed):
            print("✅ 错误密码正确拒绝")
        else:
            print("❌ 错误密码验证应该失败")
            return False
        
        print("\n✅ 所有测试通过！")
        return True
        
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_bcrypt()
    sys.exit(0 if success else 1)

