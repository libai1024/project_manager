#!/usr/bin/env python3
"""
数据库迁移脚本：创建历史项目功能相关表
使用Python虚拟环境执行
"""
import sys
import os
import sqlite3
import json
from pathlib import Path
from app.models.system_settings import HISTORICAL_PROJECT_DEFAULT_SETTINGS

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
    """执行数据库迁移：创建历史项目功能相关表"""
    db_path = get_db_path()
    print(f"正在连接数据库: {db_path}")
    
    if not os.path.exists(db_path):
        print(f"错误: 数据库文件不存在: {db_path}")
        return False
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        print("\n" + "=" * 60)
        print("创建历史项目功能相关表")
        print("=" * 60)
        
        # 1. 创建 historicalproject 表
        print("\n1. 创建 historicalproject 表...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS historicalproject (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title VARCHAR NOT NULL,
                student_name VARCHAR,
                platform_id INTEGER,
                user_id INTEGER NOT NULL,
                price REAL NOT NULL DEFAULT 0.0,
                actual_income REAL NOT NULL DEFAULT 0.0,
                status VARCHAR NOT NULL DEFAULT '已完成',
                github_url VARCHAR,
                requirements VARCHAR,
                is_paid INTEGER NOT NULL DEFAULT 0,
                original_project_id INTEGER,
                imported_at DATETIME NOT NULL,
                import_source VARCHAR,
                completion_date DATETIME,
                notes VARCHAR,
                created_at DATETIME NOT NULL,
                updated_at DATETIME NOT NULL,
                FOREIGN KEY (platform_id) REFERENCES platform(id),
                FOREIGN KEY (user_id) REFERENCES user(id)
            )
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS ix_historicalproject_title ON historicalproject(title)")
        cursor.execute("CREATE INDEX IF NOT EXISTS ix_historicalproject_user_id ON historicalproject(user_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS ix_historicalproject_platform_id ON historicalproject(platform_id)")
        print("   ✓ historicalproject 表已创建")
        
        # 2. 创建 systemsettings 表
        print("\n2. 创建 systemsettings 表...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS systemsettings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key VARCHAR NOT NULL UNIQUE,
                value VARCHAR NOT NULL,
                description VARCHAR,
                category VARCHAR NOT NULL DEFAULT 'general',
                created_at DATETIME NOT NULL,
                updated_at DATETIME NOT NULL
            )
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS ix_systemsettings_key ON systemsettings(key)")
        cursor.execute("CREATE INDEX IF NOT EXISTS ix_systemsettings_category ON systemsettings(category)")
        print("   ✓ systemsettings 表已创建")
        
        # 3. 更新 attachment 表，添加 historical_project_id 列
        print("\n3. 更新 attachment 表...")
        cursor.execute("PRAGMA table_info(attachment)")
        columns = {col[1]: col for col in cursor.fetchall()}
        
        if 'historical_project_id' not in columns:
            print("   添加 historical_project_id 列...")
            cursor.execute("""
                ALTER TABLE attachment 
                ADD COLUMN historical_project_id INTEGER 
                REFERENCES historicalproject(id)
            """)
            cursor.execute("CREATE INDEX IF NOT EXISTS ix_attachment_historical_project_id ON attachment(historical_project_id)")
            print("   ✓ historical_project_id 列已添加")
        else:
            print("   ✓ historical_project_id 列已存在")
        
        # 4. 初始化历史项目功能设置
        print("\n4. 初始化历史项目功能设置...")
        settings_json = json.dumps(HISTORICAL_PROJECT_DEFAULT_SETTINGS, ensure_ascii=False)
        cursor.execute("""
            INSERT OR IGNORE INTO systemsettings (key, value, description, category, created_at, updated_at)
            VALUES (?, ?, ?, ?, datetime('now'), datetime('now'))
        """, (
            "historical_project_settings",
            settings_json,
            "历史项目功能开关设置",
            "historical_project"
        ))
        print("   ✓ 历史项目功能设置已初始化")
        
        # 提交更改
        conn.commit()
        print("\n" + "=" * 60)
        print("✓ 数据库迁移完成！")
        print("=" * 60)
        print("\n已创建/更新的表：")
        print("  - historicalproject (历史项目表)")
        print("  - systemsettings (系统设置表)")
        print("  - attachment (已更新，添加 historical_project_id 字段)")
        print("\n历史项目功能：")
        print("  ✓ 支持导入历史项目和文件")
        print("  ✓ 兼容现有所有模块（资源管理、待办、日志等）")
        print("  ✓ 系统设置统一控制功能开关")
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
    print("历史项目功能 - 数据库迁移脚本")
    print("=" * 60)
    print("\n警告：此脚本将创建历史项目功能相关表。")
    print("请确保已备份数据库。")
    
    # 确认执行
    if len(sys.argv) > 1 and sys.argv[1] == '--confirm':
        success = migrate()
        sys.exit(0 if success else 1)
    else:
        print("\n请使用 --confirm 参数确认执行：")
        print("  python migrate_historical_projects.py --confirm")
        print("\n或者使用虚拟环境：")
        print("  source venv/bin/activate  # Linux/Mac")
        print("  venv\\Scripts\\activate  # Windows")
        print("  python migrate_historical_projects.py --confirm")
        sys.exit(1)

