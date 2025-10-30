"""
记忆（Memory）数据库服务。

提供记忆条目和章节摘要的增删改查操作。
"""
from typing import Optional
from loguru import logger
from sqlmodel import select

from .base import DatabaseSession
from schemas.memory import MemoryEntry, ChapterSummary


class MemoryService:
    """
    记忆数据库服务（单例模式）。
    
    使用类方法提供统一的 CRUD 接口。
    """
    
    # ========== MemoryEntry 操作 ==========
    
    @classmethod
    def create_entry(cls, entry: MemoryEntry) -> MemoryEntry:
        """
        创建记忆条目。
        
        :param entry: 记忆条目对象
        :return: 创建后的记忆条目对象
        """
        with DatabaseSession() as db:
            db.add(entry)
            db.flush()
            db.refresh(entry)
            db.expunge(entry)
            logger.info(f"创建记忆条目: {entry.key}")
            return entry
    
    @classmethod
    def get_entry(cls, memory_id: str) -> Optional[MemoryEntry]:
        """
        根据 memory_id 获取记忆条目。
        
        :param memory_id: 记忆ID
        :return: 记忆条目对象，如果不存在则返回 None
        """
        with DatabaseSession() as db:
            entry = db.get(MemoryEntry, memory_id)
            if entry:
                db.expunge(entry)
                logger.debug(f"获取记忆条目: {memory_id}")
            else:
                logger.warning(f"记忆条目不存在: {memory_id}")
            return entry
    
    @classmethod
    def list_entries(cls, limit: Optional[int] = None, offset: int = 0) -> list[MemoryEntry]:
        """
        获取记忆条目列表。
        
        :param limit: 返回数量限制（None 表示无限制）
        :param offset: 跳过的记录数
        :return: 记忆条目列表
        """
        with DatabaseSession() as db:
            statement = select(MemoryEntry).offset(offset)
            if limit is not None:
                statement = statement.limit(limit)
            
            entries = db.exec(statement).all()
            for entry in entries:
                db.expunge(entry)
            logger.debug(f"获取记忆条目列表: {len(entries)} 条")
            return list(entries)
    
    @classmethod
    def list_entries_by_session(cls, session_id: str, limit: Optional[int] = None, offset: int = 0) -> list[MemoryEntry]:
        """
        根据会话 ID 获取记忆条目列表。
        
        :param session_id: 会话 ID
        :param limit: 返回数量限制（None 表示无限制）
        :param offset: 跳过的记录数
        :return: 记忆条目列表
        """
        with DatabaseSession() as db:
            statement = select(MemoryEntry).where(MemoryEntry.session_id == session_id).offset(offset)
            if limit is not None:
                statement = statement.limit(limit)
            
            entries = db.exec(statement).all()
            for entry in entries:
                db.expunge(entry)
            logger.debug(f"获取会话 {session_id} 的记忆条目: {len(entries)} 条")
            return list(entries)
    
    @classmethod
    def update_entry(cls, memory_id: str, **kwargs) -> Optional[MemoryEntry]:
        """
        更新记忆条目。
        
        :param memory_id: 记忆ID
        :param kwargs: 要更新的字段
        :return: 更新后的记忆条目对象，如果不存在则返回 None
        """
        with DatabaseSession() as db:
            entry = db.get(MemoryEntry, memory_id)
            if not entry:
                logger.warning(f"记忆条目不存在，无法更新: {memory_id}")
                return None
            
            # 更新字段
            for field, value in kwargs.items():
                if hasattr(entry, field):
                    setattr(entry, field, value)
            
            db.add(entry)
            db.flush()
            db.refresh(entry)
            db.expunge(entry)
            logger.info(f"更新记忆条目: {memory_id}")
            return entry
    
    @classmethod
    def delete_entry(cls, memory_id: str) -> bool:
        """
        删除记忆条目。
        
        :param memory_id: 记忆ID
        :return: 是否删除成功
        """
        with DatabaseSession() as db:
            entry = db.get(MemoryEntry, memory_id)
            if not entry:
                logger.warning(f"记忆条目不存在，无法删除: {memory_id}")
                return False
            
            db.delete(entry)
            logger.info(f"删除记忆条目: {memory_id}")
            return True
    
    # ========== ChapterSummary 操作 ==========
    
    @classmethod
    def create_summary(cls, summary: ChapterSummary) -> ChapterSummary:
        """
        创建章节摘要。
        
        :param summary: 章节摘要对象
        :return: 创建后的章节摘要对象
        """
        with DatabaseSession() as db:
            db.add(summary)
            db.flush()
            db.refresh(summary)
            db.expunge(summary)
            logger.info(f"创建章节摘要: chapter {summary.chapter_index}")
            return summary
    
    @classmethod
    def get_summary(cls, chapter_index: int) -> Optional[ChapterSummary]:
        """
        根据章节索引获取摘要。
        
        :param chapter_index: 章节索引
        :return: 章节摘要对象，如果不存在则返回 None
        """
        with DatabaseSession() as db:
            statement = select(ChapterSummary).where(
                ChapterSummary.chapter_index == chapter_index
            )
            summary = db.exec(statement).first()
            if summary:
                db.expunge(summary)
                logger.debug(f"获取章节摘要: chapter {chapter_index}")
            else:
                logger.warning(f"章节摘要不存在: chapter {chapter_index}")
            return summary
    
    @classmethod
    def list_summaries(cls, limit: Optional[int] = None, offset: int = 0) -> list[ChapterSummary]:
        """
        获取章节摘要列表。
        
        :param limit: 返回数量限制（None 表示无限制）
        :param offset: 跳过的记录数
        :return: 章节摘要列表
        """
        with DatabaseSession() as db:
            statement = select(ChapterSummary).offset(offset)
            if limit is not None:
                statement = statement.limit(limit)
            
            summaries = db.exec(statement).all()
            for summary in summaries:
                db.expunge(summary)
            logger.debug(f"获取章节摘要列表: {len(summaries)} 条")
            return list(summaries)
    
    @classmethod
    def list_summaries_by_session(cls, session_id: str, limit: Optional[int] = None, offset: int = 0) -> list[ChapterSummary]:
        """
        根据会话 ID 获取章节摘要列表。
        
        :param session_id: 会话 ID
        :param limit: 返回数量限制（None 表示无限制）
        :param offset: 跳过的记录数
        :return: 章节摘要列表
        """
        with DatabaseSession() as db:
            statement = select(ChapterSummary).where(ChapterSummary.session_id == session_id).offset(offset)
            if limit is not None:
                statement = statement.limit(limit)
            
            summaries = db.exec(statement).all()
            for summary in summaries:
                db.expunge(summary)
            logger.debug(f"获取会话 {session_id} 的章节摘要: {len(summaries)} 条")
            return list(summaries)
    
    @classmethod
    def update_summary(cls, chapter_index: int, **kwargs) -> Optional[ChapterSummary]:
        """
        更新章节摘要。
        
        :param chapter_index: 章节索引
        :param kwargs: 要更新的字段
        :return: 更新后的章节摘要对象，如果不存在则返回 None
        """
        with DatabaseSession() as db:
            statement = select(ChapterSummary).where(
                ChapterSummary.chapter_index == chapter_index
            )
            summary = db.exec(statement).first()
            if not summary:
                logger.warning(f"章节摘要不存在，无法更新: chapter {chapter_index}")
                return None
            
            # 更新字段
            for field, value in kwargs.items():
                if hasattr(summary, field):
                    setattr(summary, field, value)
            
            db.add(summary)
            db.flush()
            db.refresh(summary)
            db.expunge(summary)
            logger.info(f"更新章节摘要: chapter {chapter_index}")
            return summary
    
    @classmethod
    def delete_summary(cls, chapter_index: int) -> bool:
        """
        删除章节摘要。
        
        :param chapter_index: 章节索引
        :return: 是否删除成功
        """
        with DatabaseSession() as db:
            statement = select(ChapterSummary).where(
                ChapterSummary.chapter_index == chapter_index
            )
            summary = db.exec(statement).first()
            if not summary:
                logger.warning(f"章节摘要不存在，无法删除: chapter {chapter_index}")
                return False
            
            db.delete(summary)
            logger.info(f"删除章节摘要: chapter {chapter_index}")
            return True

