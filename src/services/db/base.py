"""
数据库模块。

使用 SQLModel + SQLite 来管理应用数据。
"""
from typing import Generator
from sqlmodel import SQLModel, create_engine, Session
from loguru import logger

from utils.path import database_path

# noqa 标记：这些导入是必需的，用于注册表到 SQLModel.metadata
from schemas.session import Session as SessionModel  # noqa: F401
from schemas.memory import MemoryEntry, ChapterSummary  # noqa: F401
from schemas.actor import Character  # noqa: F401

# 创建数据库引擎
# check_same_thread=False 允许多线程访问（SQLite 默认只允许创建线程访问）
# echo=False 不打印 SQL 语句（生产环境建议设置为 False）
DATABASE_URL = f"sqlite:///{database_path}"
engine = create_engine(
    DATABASE_URL,
    echo=False,
    connect_args={"check_same_thread": False}
)


def init_db() -> None:
    """
    初始化数据库，创建所有表。
    
    应在应用启动时调用一次。
    """
    # 导入所有模型以确保它们被注册到 SQLModel.metadata

    # 创建所有表
    SQLModel.metadata.create_all(engine)
    logger.success(f"数据库已初始化: {database_path}")


def get_session() -> Generator[Session, None, None]:
    """
    获取数据库会话（用于依赖注入）。
    
    使用示例：
    ```python
    from services.db import get_session
    
    # 在 FastAPI 路由中
    @app.get("/items")
    def read_items(session: Session = Depends(get_session)):
        items = session.exec(select(Item)).all()
        return items
    
    # 在普通函数中
    with next(get_session()) as session:
        items = session.exec(select(Item)).all()
    ```
    
    :yield: SQLModel Session 对象
    """
    with Session(engine) as session:
        yield session


def get_db() -> Session:
    """
    获取数据库会话（同步方式，用于非 FastAPI 代码）。
    
    使用示例：
    ```python
    from services.db import get_db
    
    # 普通函数中使用
    db = get_db()
    try:
        items = db.exec(select(Item)).all()
        db.commit()
    finally:
        db.close()
    
    # 或使用 with 语句
    with get_db() as db:
        items = db.exec(select(Item)).all()
        db.commit()
    ```
    
    :return: SQLModel Session 对象
    """
    return Session(engine)


# 便捷的上下文管理器
class DatabaseSession:
    """
    数据库会话上下文管理器。
    
    使用示例：
    ```python
    from services.db import DatabaseSession
    
    with DatabaseSession() as db:
        items = db.exec(select(Item)).all()
        # 自动提交和关闭
    ```
    """

    def __init__(self):
        """初始化数据库会话上下文管理器"""
        self.session: Session | None = None

    def __enter__(self) -> Session:
        """进入上下文，创建会话"""
        self.session = Session(engine)
        return self.session

    def __exit__(self, exc_type, exc_val, exc_tb):
        """退出上下文，关闭会话"""
        if self.session is None:
            return

        if exc_type is not None:
            # 发生异常时回滚
            self.session.rollback()
        else:
            # 正常退出时提交
            self.session.commit()

        self.session.close()

