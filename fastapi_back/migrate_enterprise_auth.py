#!/usr/bin/env python3
"""
数据库迁移脚本：添加企业级身份认证系统相关表
使用Python虚拟环境执行
"""
import sys
import os
import sqlite3
from pathlib import Path
from sqlmodel import SQLModel, create_engine
from app.core.config import settings

# 导入所有模型以确保表结构正确
from app.models.user import User
from app.models.refresh_token import RefreshToken
from app.models.token_blacklist import TokenBlacklist
from app.models.login_log import LoginLog

def get_db_path():
    """获取数据库路径"""
    db_path = settings.DATABASE_URL
    if db_path.startswith('sqlite:///'):
        db_path = db_path.replace('sqlite:///', '')
    if not os.path.isabs(db_path):
        script_dir = Path(__file__).parent
        db_path = script_dir / db_path
    return str(db_path)

def update_user_table():
    """更新 user 表，添加企业级认证字段"""
    db_path = get_db_path()
    if not os.path.exists(db_path):
        print(f"错误: 数据库文件不存在: {db_path}")
        return False
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        print("\n1. 更新 user 表，添加企业级认证字段...")
        
        # 检查现有列
        cursor.execute("PRAGMA table_info(user)")
        columns = {col[1]: col for col in cursor.fetchall()}
        
        # 需要添加的字段
        new_fields = {
            'is_active': ('INTEGER', '1', '账户是否激活'),
            'is_locked': ('INTEGER', '0', '账户是否锁定'),
            'locked_until': ('DATETIME', 'NULL', '锁定到期时间'),
            'failed_login_attempts': ('INTEGER', '0', '失败登录次数'),
            'last_login_at': ('DATETIME', 'NULL', '最后登录时间'),
            'password_changed_at': ('DATETIME', 'NULL', '密码最后修改时间'),
            'must_change_password': ('INTEGER', '0', '是否必须修改密码'),
        }
        
        # 添加新字段
        added_count = 0
        for field_name, (field_type, default_value, description) in new_fields.items():
            if field_name not in columns:
                print(f"   添加字段: {field_name} ({description})")
                try:
                    if default_value == 'NULL':
                        cursor.execute(f"""
                            ALTER TABLE user 
                            ADD COLUMN {field_name} {field_type} DEFAULT NULL
                        """)
                    else:
                        cursor.execute(f"""
                            ALTER TABLE user 
                            ADD COLUMN {field_name} {field_type} DEFAULT {default_value}
                        """)
                    print(f"   ✓ {field_name} 字段已添加")
                    added_count += 1
                except sqlite3.Error as e:
                    print(f"   ✗ 添加 {field_name} 字段失败: {e}")
            else:
                print(f"   ✓ {field_name} 字段已存在")
        
        # 更新现有用户，设置默认值
        if added_count > 0:
            print("   更新现有用户数据...")
            cursor.execute("""
                UPDATE user 
                SET is_active = 1,
                    is_locked = 0,
                    failed_login_attempts = 0,
                    must_change_password = 0
                WHERE is_active IS NULL OR is_locked IS NULL
            """)
            updated_count = cursor.rowcount
            print(f"   ✓ 已更新 {updated_count} 个用户的默认值")
        
        conn.commit()
        return True
        
    except sqlite3.Error as e:
        conn.rollback()
        print(f"   ✗ 更新 user 表失败: {e}")
        return False
    finally:
        conn.close()

def migrate():
    """执行数据库迁移：添加企业级认证系统表"""
    print("=" * 60)
    print("企业级身份认证系统 - 数据库迁移脚本")
    print("=" * 60)
    
    # 先更新 user 表
    if not update_user_table():
        print("\n❌ 更新 user 表失败，迁移中止")
        return False
    
    # 创建数据库引擎
    engine = create_engine(
        settings.DATABASE_URL,
        connect_args={"check_same_thread": False},
        echo=False
    )
    
    try:
        print("\n2. 创建企业级认证系统相关表...")
        SQLModel.metadata.create_all(engine)
        
        print("\n✓ 数据库迁移完成！")
        print("\n已创建/更新的表：")
        print("  - refreshtoken (刷新令牌表)")
        print("  - tokenblacklist (Token黑名单表)")
        print("  - loginlog (登录日志表)")
        print("  - user (已更新，添加企业级认证字段)")
        
        print("\n企业级认证功能：")
        print("  ✓ Refresh Token 机制")
        print("  ✓ Token 黑名单/撤销机制")
        print("  ✓ 登录日志/审计")
        print("  ✓ 账户锁定机制")
        print("  ✓ 密码策略验证")
        print("  ✓ 失败登录次数限制")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 数据库迁移失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("\n警告：此脚本将更新数据库结构，添加企业级认证系统相关表。")
    print("请确保已备份数据库。")
    
    # 确认执行
    if len(sys.argv) > 1 and sys.argv[1] == '--confirm':
        success = migrate()
        sys.exit(0 if success else 1)
    else:
        print("\n请使用 --confirm 参数确认执行：")
        print("  python migrate_enterprise_auth.py --confirm")
        print("\n或者使用虚拟环境：")
        print("  source venv/bin/activate  # Linux/Mac")
        print("  venv\\Scripts\\activate  # Windows")
        print("  python migrate_enterprise_auth.py --confirm")
        sys.exit(1)

