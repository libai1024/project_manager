#!/usr/bin/env python3
"""
数据库迁移脚本
用于创建新的 attachmentfolder 表并更新现有表结构
"""
import sys
from sqlmodel import SQLModel, create_engine
from app.core.config import settings

# 导入所有模型以确保表结构正确
from app.models.user import User
from app.models.platform import Platform
from app.models.project import Project, ProjectStep
from app.models.attachment import Attachment
from app.models.attachment_folder import AttachmentFolder
from app.models.todo import Todo
from app.models.project_log import ProjectLog
from app.models.step_template import StepTemplate, StepTemplateItem
from app.models.project_part import ProjectPart

def migrate_database():
    """执行数据库迁移"""
    print("开始数据库迁移...")
    
    # 首先为 attachment 表添加 folder_id 列（如果不存在）
    from add_folder_id_column import migrate_attachment_table
    migrate_attachment_table()
    
    # 创建数据库引擎
    engine = create_engine(
        settings.DATABASE_URL,
        connect_args={"check_same_thread": False},
        echo=True
    )
    
    try:
        # 创建所有表（如果不存在）
        print("创建/更新数据库表...")
        SQLModel.metadata.create_all(engine)
        print("✓ 数据库迁移完成！")
        print("\n已创建/更新的表：")
        print("  - attachmentfolder (新表)")
        print("  - attachment (已更新，添加 folder_id 字段)")
        print("  - project (已更新，添加 folders 关系)")
        print("  - steptemplate (新表)")
        print("  - steptemplateitem (新表)")
        print("  - projectpart (新表，项目配件清单)")
        
        # 检查是否需要为现有项目创建默认文件夹
        from sqlmodel import Session, select
        with Session(engine) as session:
            from app.repositories.project_repository import ProjectRepository
            from app.repositories.attachment_folder_repository import AttachmentFolderRepository
            
            project_repo = ProjectRepository(session)
            folder_repo = AttachmentFolderRepository(session)
            
            # 获取所有项目
            projects = project_repo.list()
            
            created_count = 0
            for project in projects:
                # 检查是否已有默认文件夹
                existing_folders = folder_repo.get_default_folders(project.id)
                if not existing_folders:
                    # 为项目创建默认文件夹
                    folder_repo.create_default_folders(project.id)
                    created_count += 1
                    print(f"  ✓ 为项目 '{project.title}' 创建了默认文件夹")
            
            if created_count > 0:
                print(f"\n✓ 为 {created_count} 个现有项目创建了默认文件夹")
            else:
                print("\n✓ 所有项目已有默认文件夹")
            
            # 确保默认模板存在
            from app.services.step_template_service import StepTemplateService
            template_service = StepTemplateService(session)
            default_template = template_service.ensure_default_template()
            print(f"\n✓ 默认步骤模板已创建/验证: '{default_template.name}'")
        
        print("\n数据库迁移成功完成！")
        return True
        
    except Exception as e:
        print(f"❌ 数据库迁移失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = migrate_database()
    sys.exit(0 if success else 1)

