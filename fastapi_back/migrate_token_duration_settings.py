#!/usr/bin/env python3
"""
数据库迁移脚本：添加 Token 持续时间设置
"""
import sqlite3
import json
from datetime import datetime

DB_PATH = "./project_manager.db"

def migrate():
    """执行迁移"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # 检查设置是否已存在
        cursor.execute("SELECT COUNT(*) FROM systemsettings WHERE key = ?", ("access_token_expire_minutes",))
        if cursor.fetchone()[0] == 0:
            # 添加 Access Token 过期时间设置（默认15分钟）
            cursor.execute("""
                INSERT INTO systemsettings (key, value, description, category, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                "access_token_expire_minutes",
                "15",
                "Access Token 过期时间（分钟）",
                "token",
                datetime.utcnow().isoformat(),
                datetime.utcnow().isoformat()
            ))
            print("✅ 已添加 access_token_expire_minutes 设置")
        else:
            print("ℹ️  access_token_expire_minutes 设置已存在，跳过")
        
        # 检查 Refresh Token 设置是否已存在
        cursor.execute("SELECT COUNT(*) FROM systemsettings WHERE key = ?", ("refresh_token_expire_days",))
        if cursor.fetchone()[0] == 0:
            # 添加 Refresh Token 过期时间设置（默认30天）
            cursor.execute("""
                INSERT INTO systemsettings (key, value, description, category, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                "refresh_token_expire_days",
                "30",
                "Refresh Token 过期时间（天）",
                "token",
                datetime.utcnow().isoformat(),
                datetime.utcnow().isoformat()
            ))
            print("✅ 已添加 refresh_token_expire_days 设置")
        else:
            print("ℹ️  refresh_token_expire_days 设置已存在，跳过")
        
        conn.commit()
        print("✅ Token 持续时间设置迁移完成")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ 迁移失败: {e}")
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()

