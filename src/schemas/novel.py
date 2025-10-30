"""
小说内容相关的数据模型。

将小说内容存储在数据库中，支持按章节、行号查询。
"""
from sqlmodel import SQLModel, Field, Column, Index
from sqlalchemy import String


class NovelContent(SQLModel, table=True):
    """
    小说内容表。
    
    将小说按行存储，支持按章节、行号快速查询。
    """
    __tablename__ = "novel_content"
    __table_args__ = (
        # 创建复合索引以提高查询性能
        Index('idx_session_chapter_line', 'session_id', 'chapter', 'line'),
        Index('idx_session_chapter', 'session_id', 'chapter'),
    )
    
    id: int | None = Field(default=None, primary_key=True, description="自增主键")
    session_id: str = Field(
        sa_column=Column(String(36), nullable=False, index=True),
        description="会话 ID（关联到 Session）"
    )
    chapter: int = Field(default=0, ge=0, description="章节号（0 表示未分章节）")
    line: int = Field(ge=0, description="行号（段落号，从 0 开始）")
    content: str = Field(description="段落内容")

