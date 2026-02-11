#!/usr/bin/env python3
"""
数据库迁移脚本：添加 actual_income 字段
运行方式: python migrate_add_actual_income.py
"""
import sys
from sqlmodel import Session, text
from app.core.database import engine

def migrate():
    """添加 actual_income 字段到 project 表"""
    try:
        with Session(engine) as session:
            # 检查字段是否已存在
            result = session.exec(text("PRAGMA table_info(project)"))
            columns = [row[1] for row in result]
            
            if 'actual_income' in columns:
                print("✓ actual_income 字段已存在，无需迁移")
                return
            
            # 添加字段
            print("正在添加 actual_income 字段...")
            session.exec(text("ALTER TABLE project ADD COLUMN actual_income REAL DEFAULT 0.0"))
            session.commit()
            print("✓ actual_income 字段添加成功！")
            
    except Exception as e:
        print(f"✗ 迁移失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    migrate()

