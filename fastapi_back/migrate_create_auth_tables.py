#!/usr/bin/env python3
"""
数据库迁移脚本：创建企业级认证系统相关表（使用纯SQLite）
"""
import sys
import os
import sqlite3
from pathlib import Path

# 获取数据库路径
def get_db_path():
    db_path = os.getenv('DATABASE_URL', 'sqlite:///./project_manager.db')
    if db_path.startswith('sqlite:///'):
        db_path = db_path.replace('sqlite:///', '')
    if not os.path.isabs(db_path):
        script_dir = Path(__file__).parent
        db_path = script_dir / db_path
    return str(db_path)

def migrate():
    """执行数据库迁移：创建企业级认证系统表"""
    db_path = get_db_path()
    print(f"正在连接数据库: {db_path}")
    
    if not os.path.exists(db_path):
        print(f"错误: 数据库文件不存在: {db_path}")
        return False
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        print("\n" + "=" * 60)
        print("创建企业级认证系统相关表")
        print("=" * 60)
        
        # 1. 创建 refreshtoken 表
        print("\n1. 创建 refreshtoken 表...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS refreshtoken (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                token VARCHAR NOT NULL UNIQUE,
                user_id INTEGER NOT NULL,
                expires_at DATETIME NOT NULL,
                is_revoked INTEGER NOT NULL DEFAULT 0,
                device_info VARCHAR,
                ip_address VARCHAR,
                created_at DATETIME NOT NULL,
                revoked_at DATETIME,
                FOREIGN KEY (user_id) REFERENCES user(id)
            )
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS ix_refreshtoken_token ON refreshtoken(token)")
        cursor.execute("CREATE INDEX IF NOT EXISTS ix_refreshtoken_user_id ON refreshtoken(user_id)")
        print("   ✓ refreshtoken 表已创建")
        
        # 2. 创建 tokenblacklist 表
        print("\n2. 创建 tokenblacklist 表...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tokenblacklist (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                token VARCHAR NOT NULL UNIQUE,
                expires_at DATETIME NOT NULL,
                created_at DATETIME NOT NULL,
                reason VARCHAR
            )
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS ix_tokenblacklist_token ON tokenblacklist(token)")
        print("   ✓ tokenblacklist 表已创建")
        
        # 3. 创建 loginlog 表
        print("\n3. 创建 loginlog 表...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS loginlog (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                username VARCHAR NOT NULL,
                status VARCHAR NOT NULL,
                ip_address VARCHAR,
                user_agent VARCHAR,
                device_info VARCHAR,
                failure_reason VARCHAR,
                created_at DATETIME NOT NULL,
                FOREIGN KEY (user_id) REFERENCES user(id)
            )
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS ix_loginlog_username ON loginlog(username)")
        cursor.execute("CREATE INDEX IF NOT EXISTS ix_loginlog_created_at ON loginlog(created_at)")
        cursor.execute("CREATE INDEX IF NOT EXISTS ix_loginlog_user_id ON loginlog(user_id)")
        print("   ✓ loginlog 表已创建")
        
        # 提交更改
        conn.commit()
        print("\n" + "=" * 60)
        print("✓ 数据库迁移完成！")
        print("=" * 60)
        print("\n已创建的表：")
        print("  - refreshtoken (刷新令牌表)")
        print("  - tokenblacklist (Token黑名单表)")
        print("  - loginlog (登录日志表)")
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
    print("创建企业级认证系统表 - 数据库迁移脚本")
    print("=" * 60)
    print("\n警告：此脚本将创建企业级认证系统相关表。")
    print("请确保已备份数据库。")
    
    # 确认执行
    if len(sys.argv) > 1 and sys.argv[1] == '--confirm':
        success = migrate()
        sys.exit(0 if success else 1)
    else:
        print("\n请使用 --confirm 参数确认执行：")
        print("  python migrate_create_auth_tables.py --confirm")
        sys.exit(1)

