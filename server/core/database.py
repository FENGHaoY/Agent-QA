"""
数据库模块。

基于 SQLAlchemy 2.x 创建数据库引擎、会话工厂与声明式基类，
并提供 FastAPI 依赖 get_db 用于在请求中获取数据库会话。
"""

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from server.core.config import settings

# 创建数据库引擎，pool_pre_ping 可避免连接长时间空闲后失效
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=False,
)

# 会话工厂
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    """所有 ORM 模型的声明式基类。"""

    pass


def get_db() -> Generator[Session, None, None]:
    """FastAPI 依赖：提供一个数据库会话，请求结束后自动关闭。"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
