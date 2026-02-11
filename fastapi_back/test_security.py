#!/usr/bin/env python3
"""
测试密码哈希功能
"""
import sys
import os

# 添加当前目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    print("正在测试密码哈希功能...")
    
    from app.core.security import get_password_hash, verify_password
    
    # 测试正常密码
    test_password = "admin123"
    print(f"\n1. 测试密码: {test_password}")
    
    hash_result = get_password_hash(test_password)
    print(f"   哈希结果: {hash_result[:50]}...")
    
    verify_result = verify_password(test_password, hash_result)
    print(f"   验证结果: {'✅ 通过' if verify_result else '❌ 失败'}")
    
    # 测试错误密码
    wrong_password = "wrong_password"
    verify_wrong = verify_password(wrong_password, hash_result)
    print(f"   错误密码验证: {'❌ 应该失败但通过了' if verify_wrong else '✅ 正确拒绝'}")
    
    # 测试长密码（超过72字节）
    long_password = "a" * 100
    print(f"\n2. 测试长密码（100字符）...")
    try:
        long_hash = get_password_hash(long_password)
        print(f"   哈希结果: {long_hash[:50]}...")
        verify_long = verify_password(long_password, long_hash)
        print(f"   验证结果: {'✅ 通过' if verify_long else '❌ 失败'}")
    except Exception as e:
        print(f"   ❌ 错误: {e}")
    
    # 测试中文字符密码
    chinese_password = "测试密码123"
    print(f"\n3. 测试中文密码: {chinese_password}")
    try:
        chinese_hash = get_password_hash(chinese_password)
        print(f"   哈希结果: {chinese_hash[:50]}...")
        verify_chinese = verify_password(chinese_password, chinese_hash)
        print(f"   验证结果: {'✅ 通过' if verify_chinese else '❌ 失败'}")
    except Exception as e:
        print(f"   ❌ 错误: {e}")
    
    print("\n✅ 所有密码测试完成！")
    sys.exit(0)
    
except Exception as e:
    print(f"\n❌ 错误: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

