#!/usr/bin/env python3
"""
数据库迁移脚本：为 attachment 表添加 folder_id 列
"""
import sys
import sqlite3
from pathlib import Path
from app.core.config import settings

def migrate_attachment_table():
    """为 attachment 表添加 folder_id 列"""
    print("开始迁移 attachment 表...")
    
    # 获取数据库路径
    db_url = settings.DATABASE_URL
    if db_url.startswith('sqlite:///'):
        db_path = db_url.replace('sqlite:///', '')
    else:
        print(f"❌ 不支持的数据库类型: {db_url}")
        return False
    
    # 检查数据库文件是否存在
    if not Path(db_path).exists():
        print(f"❌ 数据库文件不存在: {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 检查 folder_id 列是否已存在
        cursor.execute("PRAGMA table_info(attachment)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'folder_id' in columns:
            print("✓ folder_id 列已存在，无需迁移")
            conn.close()
            return True
        
        # 添加 folder_id 列
        print("正在添加 folder_id 列...")
        cursor.execute("""
            ALTER TABLE attachment 
            ADD COLUMN folder_id INTEGER 
            REFERENCES attachmentfolder(id)
        """)
        
        conn.commit()
        conn.close()
        
        print("✓ 成功为 attachment 表添加 folder_id 列")
        return True
        
    except Exception as e:
        print(f"❌ 迁移失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = migrate_attachment_table()
    sys.exit(0 if success else 1)

