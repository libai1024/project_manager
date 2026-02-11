#!/usr/bin/env python3
"""
数据库迁移脚本：添加GitHub Commits表
"""
import sqlite3
import sys
from pathlib import Path

# 获取数据库路径
db_path = Path(__file__).parent / "project_manager.db"

if not db_path.exists():
    print(f"❌ 数据库文件不存在: {db_path}")
    sys.exit(1)

print(f"📦 开始迁移数据库: {db_path}")
print("=" * 50)

try:
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    # 检查表是否已存在
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name='github_commit'
    """)
    
    if cursor.fetchone():
        print("✅ github_commit 表已存在，跳过创建")
    else:
        print("📝 创建 github_commit 表...")
        
        # 创建表
        cursor.execute("""
            CREATE TABLE github_commit (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL,
                sha VARCHAR(40) NOT NULL,
                branch VARCHAR(255) NOT NULL,
                author VARCHAR(255) NOT NULL,
                message TEXT NOT NULL,
                commit_date DATETIME NOT NULL,
                url VARCHAR(500) NOT NULL,
                synced_at DATETIME NOT NULL,
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (project_id) REFERENCES project (id) ON DELETE CASCADE
            )
        """)
        
        # 创建索引
        print("📝 创建索引...")
        cursor.execute("CREATE INDEX idx_github_commit_project_id ON github_commit(project_id)")
        cursor.execute("CREATE INDEX idx_github_commit_sha ON github_commit(sha)")
        cursor.execute("CREATE INDEX idx_github_commit_branch ON github_commit(branch)")
        cursor.execute("CREATE INDEX idx_github_commit_project_branch ON github_commit(project_id, branch)")
        
        conn.commit()
        print("✅ github_commit 表创建成功")
        print("✅ 索引创建成功")
    
    print("=" * 50)
    print("✅ 数据库迁移完成！")
    
except sqlite3.Error as e:
    print(f"❌ 数据库错误: {e}")
    conn.rollback()
    sys.exit(1)
except Exception as e:
    print(f"❌ 迁移失败: {e}")
    sys.exit(1)
finally:
    conn.close()

