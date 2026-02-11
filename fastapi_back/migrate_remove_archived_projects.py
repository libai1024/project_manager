#!/usr/bin/env python3
"""
数据库迁移脚本：删除归档项目相关的表和字段
使用Python虚拟环境执行
"""
import sqlite3
import os
import sys
from pathlib import Path

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
    """执行数据库迁移：删除归档项目相关的表和字段"""
    db_path = get_db_path()
    print(f"正在连接数据库: {db_path}")
    
    if not os.path.exists(db_path):
        print(f"错误: 数据库文件不存在: {db_path}")
        return False
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        print("\n" + "=" * 60)
        print("开始删除归档项目相关数据...")
        print("=" * 60)
        
        # 1. 删除 attachment 表中的 archived_project_id 列
        # SQLite 不支持直接删除列，需要重建表
        print("\n1. 处理 attachment 表...")
        cursor.execute("PRAGMA table_info(attachment)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'archived_project_id' in columns:
            print("   检测到 archived_project_id 列，准备删除...")
            
            # 获取所有列名（排除 archived_project_id）
            keep_columns = [col[1] for col in cursor.fetchall() if col[1] != 'archived_project_id']
            cursor.execute("PRAGMA table_info(attachment)")
            all_columns = cursor.fetchall()
            keep_columns = [col[1] for col in all_columns if col[1] != 'archived_project_id']
            
            # 创建新表（不包含 archived_project_id）
            print("   创建临时表...")
            cursor.execute("""
                CREATE TABLE attachment_new (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_id INTEGER,
                    file_path VARCHAR NOT NULL,
                    file_name VARCHAR NOT NULL,
                    file_type VARCHAR NOT NULL DEFAULT '其他',
                    description VARCHAR,
                    folder_id INTEGER,
                    created_at DATETIME NOT NULL,
                    FOREIGN KEY (project_id) REFERENCES project(id),
                    FOREIGN KEY (folder_id) REFERENCES attachmentfolder(id)
                )
            """)
            
            # 复制数据（排除 archived_project_id）
            print("   复制数据到新表...")
            cursor.execute("""
                INSERT INTO attachment_new 
                (id, project_id, file_path, file_name, file_type, description, folder_id, created_at)
                SELECT id, project_id, file_path, file_name, file_type, description, folder_id, created_at
                FROM attachment
            """)
            
            # 删除旧表
            print("   删除旧表...")
            cursor.execute("DROP TABLE attachment")
            
            # 重命名新表
            print("   重命名新表...")
            cursor.execute("ALTER TABLE attachment_new RENAME TO attachment")
            
            # 重建索引
            print("   重建索引...")
            cursor.execute("CREATE INDEX IF NOT EXISTS ix_attachment_project_id ON attachment(project_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS ix_attachment_folder_id ON attachment(folder_id)")
            
            print("   ✓ attachment 表的 archived_project_id 列已删除")
        else:
            print("   ✓ attachment 表不包含 archived_project_id 列，跳过")
        
        # 2. 删除 archivedproject 表
        print("\n2. 处理 archivedproject 表...")
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='archivedproject'
        """)
        if cursor.fetchone():
            print("   检测到 archivedproject 表，准备删除...")
            
            # 先删除相关的索引
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='index' AND tbl_name='archivedproject'
            """)
            indexes = cursor.fetchall()
            for index in indexes:
                print(f"   删除索引: {index[0]}")
                cursor.execute(f"DROP INDEX IF EXISTS {index[0]}")
            
            # 删除表
            print("   删除 archivedproject 表...")
            cursor.execute("DROP TABLE IF EXISTS archivedproject")
            print("   ✓ archivedproject 表已删除")
        else:
            print("   ✓ archivedproject 表不存在，跳过")
        
        # 3. 清理 user 表中的关系（SQLite 不存储关系，但确保没有外键约束问题）
        print("\n3. 检查 user 表...")
        cursor.execute("PRAGMA table_info(user)")
        user_columns = [col[1] for col in cursor.fetchall()]
        print(f"   user 表列: {user_columns}")
        print("   ✓ user 表无需修改（关系在应用层）")
        
        # 提交更改
        conn.commit()
        print("\n" + "=" * 60)
        print("✓ 数据库迁移完成！")
        print("=" * 60)
        print("\n已删除的内容：")
        print("  - archivedproject 表")
        print("  - attachment 表中的 archived_project_id 列")
        print("\n注意：如果数据库中有归档项目的数据，这些数据已被永久删除。")
        return True
        
    except sqlite3.Error as e:
        conn.rollback()
        print(f"\n✗ 迁移失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        conn.close()

if __name__ == '__main__':
    print("=" * 60)
    print("删除归档项目功能 - 数据库迁移脚本")
    print("=" * 60)
    print("\n警告：此脚本将永久删除归档项目相关的表和字段！")
    print("请确保已备份数据库。")
    
    # 确认执行
    if len(sys.argv) > 1 and sys.argv[1] == '--confirm':
        success = migrate()
        sys.exit(0 if success else 1)
    else:
        print("\n请使用 --confirm 参数确认执行：")
        print("  python migrate_remove_archived_projects.py --confirm")
        print("\n或者使用虚拟环境：")
        print("  source venv/bin/activate  # Linux/Mac")
        print("  venv\\Scripts\\activate  # Windows")
        print("  python migrate_remove_archived_projects.py --confirm")
        sys.exit(1)

