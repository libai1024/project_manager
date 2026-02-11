#!/usr/bin/env python3
"""
数据库迁移脚本：更新 user 表，添加企业级认证字段
使用Python虚拟环境执行
"""
import sys
import os
import sqlite3
from pathlib import Path
from datetime import datetime

# 获取数据库路径
def get_db_path():
    # 尝试从环境变量或配置中获取
    db_path = os.getenv('DATABASE_URL', 'sqlite:///./project_manager.db')
    # 移除 sqlite:/// 前缀
    if db_path.startswith('sqlite:///'):
        db_path = db_path.replace('sqlite:///', '')
    # 如果是相对路径，转换为绝对路径
    if not os.path.isabs(db_path):
        # 假设数据库文件在 fastapi_back 目录下
        script_dir = Path(__file__).parent
        db_path = script_dir / db_path
    return str(db_path)

def migrate():
    """执行数据库迁移：更新 user 表，添加企业级认证字段"""
    db_path = get_db_path()
    print(f"正在连接数据库: {db_path}")
    
    if not os.path.exists(db_path):
        print(f"错误: 数据库文件不存在: {db_path}")
        return False
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        print("\n" + "=" * 60)
        print("更新 user 表，添加企业级认证字段")
        print("=" * 60)
        
        # 检查现有列
        cursor.execute("PRAGMA table_info(user)")
        columns = {col[1]: col for col in cursor.fetchall()}
        print(f"\n现有列: {list(columns.keys())}")
        
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
                print(f"\n添加字段: {field_name} ({description})")
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
                    print(f"  ✓ {field_name} 字段已添加")
                    added_count += 1
                except sqlite3.Error as e:
                    print(f"  ✗ 添加 {field_name} 字段失败: {e}")
            else:
                print(f"  ✓ {field_name} 字段已存在，跳过")
        
        # 更新现有用户，设置默认值
        if added_count > 0:
            print("\n更新现有用户数据...")
            cursor.execute("""
                UPDATE user 
                SET is_active = 1,
                    is_locked = 0,
                    failed_login_attempts = 0,
                    must_change_password = 0
                WHERE is_active IS NULL OR is_locked IS NULL
            """)
            updated_count = cursor.rowcount
            print(f"  ✓ 已更新 {updated_count} 个用户的默认值")
        
        # 提交更改
        conn.commit()
        print("\n" + "=" * 60)
        print("✓ user 表更新完成！")
        print("=" * 60)
        print(f"\n已添加 {added_count} 个新字段")
        return True
        
    except sqlite3.Error as e:
        conn.rollback()
        print(f"\n✗ 迁移失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    print("=" * 60)
    print("更新 user 表 - 添加企业级认证字段")
    print("=" * 60)
    print("\n警告：此脚本将更新 user 表结构。")
    print("请确保已备份数据库。")
    
    # 确认执行
    if len(sys.argv) > 1 and sys.argv[1] == '--confirm':
        success = migrate()
        sys.exit(0 if success else 1)
    else:
        print("\n请使用 --confirm 参数确认执行：")
        print("  python migrate_update_user_table.py --confirm")
        print("\n或者使用虚拟环境：")
        print("  source venv/bin/activate  # Linux/Mac")
        print("  venv\\Scripts\\activate  # Windows")
        print("  python migrate_update_user_table.py --confirm")
        sys.exit(1)

