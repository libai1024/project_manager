"""
初始化数据库，创建默认管理员用户
"""
from sqlmodel import Session, select, SQLModel
from app.core.database import engine
from app.core.security import get_password_hash
# 导入所有模型以确保表被创建
from app.models.user import User
from app.models.platform import Platform
from app.models.project import Project, ProjectStep
from app.models.attachment import Attachment

# 创建所有表
SQLModel.metadata.create_all(engine)


def init_admin_user():
    """创建默认管理员用户"""
    try:
        with Session(engine) as session:
            # 检查是否已存在管理员
            admin = session.exec(select(User).where(User.username == "admin")).first()
            if not admin:
                # 生成密码哈希
                password = "admin123"
                password_hash = get_password_hash(password)
                
                admin = User(
                    username="admin",
                    password_hash=password_hash,
                    role="admin"
                )
                session.add(admin)
                session.commit()
                print("✅ 默认管理员用户创建成功: admin / admin123")
            else:
                print("ℹ️  管理员用户已存在")
    except Exception as e:
        print(f"❌ 创建管理员用户失败: {e}")
        import traceback
        traceback.print_exc()
        raise


if __name__ == "__main__":
    init_admin_user()

