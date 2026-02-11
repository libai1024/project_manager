from sqlmodel import SQLModel, create_engine, Session
from app.core.config import settings

engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False},  # SQLite需要这个参数
    echo=True  # 开发时打印SQL语句
)


def get_session():
    with Session(engine) as session:
        yield session

