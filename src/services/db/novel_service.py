"""
小说内容数据库服务。

提供小说内容的增删改查操作。
"""
from typing import Optional
from loguru import logger
from sqlmodel import select

from .base import DatabaseSession
from schemas.novel import NovelContent


class NovelContentService:
    """
    小说内容数据库服务（单例模式）。
    
    使用类方法提供统一的 CRUD 接口。
    """
    
    @classmethod
    def create(cls, novel_content: NovelContent) -> NovelContent:
        """
        创建单条小说内容记录。
        
        :param novel_content: 小说内容对象
        :return: 创建后的对象
        """
        with DatabaseSession() as db:
            db.add(novel_content)
            db.flush()
            db.refresh(novel_content)
            db.expunge(novel_content)
            return novel_content
    
    @classmethod
    def batch_create(cls, novel_contents: list[NovelContent]) -> int:
        """
        批量创建小说内容记录。
        
        :param novel_contents: 小说内容对象列表
        :return: 创建的记录数
        """
        if not novel_contents:
            return 0
        
        with DatabaseSession() as db:
            for content in novel_contents:
                db.add(content)
            db.flush()
            logger.info(f"批量创建小说内容: {len(novel_contents)} 条")
            return len(novel_contents)
    
    @classmethod
    def get_by_session(cls, session_id: str, limit: Optional[int] = None) -> list[NovelContent]:
        """
        获取某个 session 的所有小说内容。
        
        :param session_id: 会话 ID
        :param limit: 返回数量限制
        :return: 小说内容列表（按章节、行号排序）
        """
        with DatabaseSession() as db:
            statement = select(NovelContent).where(
                NovelContent.session_id == session_id
            ).order_by(
                NovelContent.chapter,
                NovelContent.line
            )
            
            if limit is not None:
                statement = statement.limit(limit)
            
            contents = db.exec(statement).all()
            for content in contents:
                db.expunge(content)
            
            logger.debug(f"获取会话小说内容: {session_id}, 共 {len(contents)} 行")
            return list(contents)
    
    @classmethod
    def get_by_chapter(cls, session_id: str, chapter: int) -> list[NovelContent]:
        """
        获取某个章节的所有内容。
        
        :param session_id: 会话 ID
        :param chapter: 章节号
        :return: 小说内容列表（按行号排序）
        """
        with DatabaseSession() as db:
            statement = select(NovelContent).where(
                NovelContent.session_id == session_id,
                NovelContent.chapter == chapter
            ).order_by(NovelContent.line)
            
            contents = db.exec(statement).all()
            for content in contents:
                db.expunge(content)
            
            logger.debug(f"获取章节内容: {session_id} 第 {chapter} 章, 共 {len(contents)} 行")
            return list(contents)
    
    @classmethod
    def get_by_line(cls, session_id: str, chapter: int, line: int) -> Optional[NovelContent]:
        """
        获取某一行的内容。
        
        :param session_id: 会话 ID
        :param chapter: 章节号
        :param line: 行号
        :return: 小说内容对象，如果不存在则返回 None
        """
        with DatabaseSession() as db:
            statement = select(NovelContent).where(
                NovelContent.session_id == session_id,
                NovelContent.chapter == chapter,
                NovelContent.line == line
            )
            
            content = db.exec(statement).first()
            if content:
                db.expunge(content)
                logger.debug(f"获取行内容: {session_id} 第 {chapter} 章 第 {line} 行")
            
            return content
    
    @classmethod
    def get_line_range(
        cls, 
        session_id: str, 
        start_line: int, 
        end_line: int,
        chapter: Optional[int] = None
    ) -> list[NovelContent]:
        """
        获取指定行号范围的内容。
        
        :param session_id: 会话 ID
        :param start_line: 起始行号（包含）
        :param end_line: 结束行号（包含）
        :param chapter: 章节号（可选，不指定则跨章节查询）
        :return: 小说内容列表
        """
        with DatabaseSession() as db:
            statement = select(NovelContent).where(
                NovelContent.session_id == session_id,
                NovelContent.line >= start_line,
                NovelContent.line <= end_line
            )
            
            if chapter is not None:
                statement = statement.where(NovelContent.chapter == chapter)
            
            statement = statement.order_by(NovelContent.chapter, NovelContent.line)
            
            contents = db.exec(statement).all()
            for content in contents:
                db.expunge(content)
            
            logger.debug(f"获取行范围内容: {session_id} 行 {start_line}-{end_line}, 共 {len(contents)} 行")
            return list(contents)
    
    @classmethod
    def count_by_session(cls, session_id: str) -> int:
        """
        统计某个 session 的总行数。
        
        :param session_id: 会话 ID
        :return: 总行数
        """
        with DatabaseSession() as db:
            statement = select(NovelContent).where(
                NovelContent.session_id == session_id
            )
            contents = db.exec(statement).all()
            return len(contents)
    
    @classmethod
    def count_chapters(cls, session_id: str) -> int:
        """
        统计某个 session 的总章节数。
        
        :param session_id: 会话 ID
        :return: 总章节数
        """
        with DatabaseSession() as db:
            statement = select(NovelContent.chapter).where(
                NovelContent.session_id == session_id
            ).distinct()
            
            chapters = db.exec(statement).all()
            return len(chapters)
    
    @classmethod
    def delete_by_session(cls, session_id: str) -> int:
        """
        删除某个 session 的所有小说内容。
        
        :param session_id: 会话 ID
        :return: 删除的记录数
        """
        with DatabaseSession() as db:
            statement = select(NovelContent).where(
                NovelContent.session_id == session_id
            )
            contents = db.exec(statement).all()
            count = len(contents)
            
            for content in contents:
                db.delete(content)
            
            logger.info(f"删除会话小说内容: {session_id}, 共 {count} 行")
            return count
    
    @classmethod
    def delete_by_chapter(cls, session_id: str, chapter: int) -> int:
        """
        删除某个章节的所有内容。
        
        :param session_id: 会话 ID
        :param chapter: 章节号
        :return: 删除的记录数
        """
        with DatabaseSession() as db:
            statement = select(NovelContent).where(
                NovelContent.session_id == session_id,
                NovelContent.chapter == chapter
            )
            contents = db.exec(statement).all()
            count = len(contents)
            
            for content in contents:
                db.delete(content)
            
            logger.info(f"删除章节内容: {session_id} 第 {chapter} 章, 共 {count} 行")
            return count
    
    @classmethod
    def update(cls, session_id: str, chapter: int, line: int, new_content: str) -> Optional[NovelContent]:
        """
        更新指定行的内容。
        
        :param session_id: 会话 ID
        :param chapter: 章节号
        :param line: 行号
        :param new_content: 新的内容
        :return: 更新后的对象，如果不存在则返回 None
        """
        with DatabaseSession() as db:
            statement = select(NovelContent).where(
                NovelContent.session_id == session_id,
                NovelContent.chapter == chapter,
                NovelContent.line == line
            )
            
            content = db.exec(statement).first()
            if not content:
                logger.warning(f"行内容不存在，无法更新: {session_id} 第 {chapter} 章 第 {line} 行")
                return None
            
            content.content = new_content
            db.add(content)
            db.flush()
            db.refresh(content)
            db.expunge(content)
            
            logger.info(f"更新行内容: {session_id} 第 {chapter} 章 第 {line} 行")
            return content
    
    @classmethod
    def delete_single(cls, session_id: str, chapter: int, line: int) -> bool:
        """
        删除单条内容。
        
        :param session_id: 会话 ID
        :param chapter: 章节号
        :param line: 行号
        :return: 是否删除成功
        """
        with DatabaseSession() as db:
            statement = select(NovelContent).where(
                NovelContent.session_id == session_id,
                NovelContent.chapter == chapter,
                NovelContent.line == line
            )
            
            content = db.exec(statement).first()
            if not content:
                logger.warning(f"行内容不存在，无法删除: {session_id} 第 {chapter} 章 第 {line} 行")
                return False
            
            db.delete(content)
            logger.info(f"删除单条内容: {session_id} 第 {chapter} 章 第 {line} 行")
            return True

