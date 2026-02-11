#!/usr/bin/env python3
"""
数据库迁移脚本：为现有表添加历史项目支持字段
使用Python虚拟环境执行
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
    """执行数据库迁移：为现有表添加历史项目支持字段"""
    db_path = get_db_path()
    print(f"正在连接数据库: {db_path}")
    
    if not os.path.exists(db_path):
        print(f"错误: 数据库文件不存在: {db_path}")
        return False
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        print("\n" + "=" * 60)
        print("为现有表添加历史项目支持字段")
        print("=" * 60)
        
        # 需要更新的表和字段
        tables_to_update = {
            'attachment': 'historical_project_id',
            'todo': 'historical_project_id',
            'projectlog': 'historical_project_id',
            'projectpart': 'historical_project_id',
            'github_commit': 'historical_project_id',
            'videoplayback': 'historical_project_id',
            'attachmentfolder': 'historical_project_id',
        }
        
        updated_count = 0
        for table_name, column_name in tables_to_update.items():
            print(f"\n检查 {table_name} 表...")
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = {col[1]: col for col in cursor.fetchall()}
            
            if column_name not in columns:
                print(f"   添加 {column_name} 列...")
                try:
                    cursor.execute(f"""
                        ALTER TABLE {table_name} 
                        ADD COLUMN {column_name} INTEGER 
                        REFERENCES historicalproject(id)
                    """)
                    # 创建索引
                    cursor.execute(f"""
                        CREATE INDEX IF NOT EXISTS ix_{table_name}_{column_name} 
                        ON {table_name}({column_name})
                    """)
                    print(f"   ✓ {column_name} 列已添加")
                    updated_count += 1
                except sqlite3.Error as e:
                    print(f"   ✗ 添加 {column_name} 列失败: {e}")
            else:
                print(f"   ✓ {column_name} 列已存在")
        
        # 提交更改
        conn.commit()
        print("\n" + "=" * 60)
        print("✓ 数据库迁移完成！")
        print("=" * 60)
        print(f"\n已更新 {updated_count} 个表")
        print("\n更新的表：")
        for table_name in tables_to_update.keys():
            print(f"  - {table_name}")
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
    print("添加历史项目支持字段 - 数据库迁移脚本")
    print("=" * 60)
    print("\n警告：此脚本将为现有表添加历史项目支持字段。")
    print("请确保已备份数据库。")
    
    # 确认执行
    if len(sys.argv) > 1 and sys.argv[1] == '--confirm':
        success = migrate()
        sys.exit(0 if success else 1)
    else:
        print("\n请使用 --confirm 参数确认执行：")
        print("  python migrate_add_historical_project_fields.py --confirm")
        print("\n或者使用虚拟环境：")
        print("  source venv/bin/activate  # Linux/Mac")
        print("  venv\\Scripts\\activate  # Windows")
        print("  python migrate_add_historical_project_fields.py --confirm")
        sys.exit(1)

