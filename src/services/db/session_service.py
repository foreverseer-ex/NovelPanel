"""
会话（Session）数据库服务。

提供会话的增删改查操作。
"""
from typing import Optional
from loguru import logger
from sqlmodel import select

from .base import DatabaseSession
from schemas.session import Session


class SessionService:
    """
    会话数据库服务（单例模式）。
    
    使用类方法提供统一的 CRUD 接口。
    """
    
    @classmethod
    def create(cls, session: Session) -> Session:
        """
        创建会话。
        
        :param session: 会话对象
        :return: 创建后的会话对象（包含自动生成的字段）
        """
        with DatabaseSession() as db:
            db.add(session)
            db.flush()  # 刷新以获取自动生成的字段
            db.refresh(session)
            logger.info(f"创建会话: {session.session_id}")
            return session
    
    @classmethod
    def get(cls, session_id: str) -> Optional[Session]:
        """
        根据 ID 获取会话。
        
        :param session_id: 会话 ID
        :return: 会话对象，如果不存在则返回 None
        """
        with DatabaseSession() as db:
            session = db.get(Session, session_id)
            if session:
                logger.debug(f"获取会话: {session_id}")
            else:
                logger.warning(f"会话不存在: {session_id}")
            return session
    
    @classmethod
    def list(cls, limit: Optional[int] = None, offset: int = 0) -> list[Session]:
        """
        获取会话列表。
        
        :param limit: 返回数量限制（None 表示无限制）
        :param offset: 跳过的记录数
        :return: 会话列表
        """
        with DatabaseSession() as db:
            statement = select(Session).offset(offset)
            if limit is not None:
                statement = statement.limit(limit)
            
            sessions = db.exec(statement).all()
            logger.debug(f"获取会话列表: {len(sessions)} 条")
            return list(sessions)
    
    @classmethod
    def update(cls, session_id: str, **kwargs) -> Optional[Session]:
        """
        更新会话。
        
        :param session_id: 会话 ID
        :param kwargs: 要更新的字段
        :return: 更新后的会话对象，如果不存在则返回 None
        """
        with DatabaseSession() as db:
            session = db.get(Session, session_id)
            if not session:
                logger.warning(f"会话不存在，无法更新: {session_id}")
                return None
            
            # 更新字段
            for key, value in kwargs.items():
                if hasattr(session, key):
                    setattr(session, key, value)
            
            db.add(session)
            db.flush()
            db.refresh(session)
            logger.info(f"更新会话: {session_id}")
            return session
    
    @classmethod
    def delete(cls, session_id: str) -> bool:
        """
        删除会话。
        
        :param session_id: 会话 ID
        :return: 是否删除成功
        """
        with DatabaseSession() as db:
            session = db.get(Session, session_id)
            if not session:
                logger.warning(f"会话不存在，无法删除: {session_id}")
                return False
            
            db.delete(session)
            logger.info(f"删除会话: {session_id}")
            return True

