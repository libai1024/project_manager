#!/usr/bin/env python3
"""
数据库迁移脚本：添加标签功能
使用Python虚拟环境执行
"""
import sys
import os
import sqlite3
import json
from pathlib import Path
from datetime import datetime

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
    """执行数据库迁移：添加标签相关表"""
    db_path = get_db_path()
    print(f"正在连接数据库: {db_path}")

    if not os.path.exists(db_path):
        print(f"错误: 数据库文件不存在: {db_path}")
        return False

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        print("\n" + "=" * 60)
        print("添加标签功能表")
        print("=" * 60)

        # 创建标签表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tag (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR NOT NULL UNIQUE,
                color VARCHAR NOT NULL DEFAULT '#409eff',
                description VARCHAR,
                user_id INTEGER,
                is_common BOOLEAN NOT NULL DEFAULT 0,
                usage_count INTEGER NOT NULL DEFAULT 0,
                created_at DATETIME NOT NULL,
                updated_at DATETIME NOT NULL,
                FOREIGN KEY (user_id) REFERENCES user (id)
            )
        """)
        conn.commit()
        print("✅ 创建标签表 (tag)")

        # 创建项目标签关联表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS projecttag (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL,
                tag_id INTEGER NOT NULL,
                created_at DATETIME NOT NULL,
                FOREIGN KEY (project_id) REFERENCES project (id) ON DELETE CASCADE,
                FOREIGN KEY (tag_id) REFERENCES tag (id) ON DELETE CASCADE,
                UNIQUE(project_id, tag_id)
            )
        """)
        conn.commit()
        print("✅ 创建项目标签关联表 (projecttag)")

        # 创建历史项目标签关联表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS historicalprojecttag (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                historical_project_id INTEGER NOT NULL,
                tag_id INTEGER NOT NULL,
                created_at DATETIME NOT NULL,
                FOREIGN KEY (historical_project_id) REFERENCES historicalproject (id) ON DELETE CASCADE,
                FOREIGN KEY (tag_id) REFERENCES tag (id) ON DELETE CASCADE,
                UNIQUE(historical_project_id, tag_id)
            )
        """)
        conn.commit()
        print("✅ 创建历史项目标签关联表 (historicalprojecttag)")

        # 创建索引
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_tag_name ON tag(name)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_tag_user_id ON tag(user_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_tag_is_common ON tag(is_common)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_projecttag_project_id ON projecttag(project_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_projecttag_tag_id ON projecttag(tag_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_historicalprojecttag_project_id ON historicalprojecttag(historical_project_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_historicalprojecttag_tag_id ON historicalprojecttag(tag_id)")
        conn.commit()
        print("✅ 创建索引")

        # 插入一些常用标签
        common_tags = [
            ("重要", "#f56c6c", "重要项目", True),
            ("紧急", "#e6a23c", "紧急项目", True),
            ("进行中", "#409eff", "正在进行的项目", True),
            ("已完成", "#67c23a", "已完成的项目", True),
            ("待结账", "#909399", "待结账的项目", True),
            ("毕设", "#9c27b0", "毕业设计项目", True),
            ("课程设计", "#00bcd4", "课程设计项目", True),
            ("竞赛", "#ff9800", "竞赛项目", True),
        ]

        for name, color, description, is_common in common_tags:
            cursor.execute("""
                INSERT OR IGNORE INTO tag (name, color, description, user_id, is_common, usage_count, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (name, color, description, None, is_common, 0, datetime.utcnow().isoformat(), datetime.utcnow().isoformat()))

        conn.commit()
        print("✅ 插入常用标签")

        print("\n✅ 标签功能迁移完成")
        return True

    except sqlite3.Error as e:
        print(f"数据库迁移错误: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    if migrate():
        print("标签功能数据库迁移成功。")
    else:
        print("标签功能数据库迁移失败。")
    sys.exit(0)

