"""
阅读器的路由。

简化设计：按行读取小说，每行对应一个段落/一张图片。
基于 NovelContentService 实现。
"""
from typing import List
from fastapi import APIRouter, HTTPException
from loguru import logger

from schemas.novel import NovelContent
from schemas.memory import ChapterSummary
from services.db import NovelContentService, MemoryService

router = APIRouter(
    prefix="/reader",
    tags=["阅读器"],
    responses={404: {"description": "内容不存在"}},
)


# ==================== 行读取 ====================

@router.get("/line/{session_id}/{chapter}/{line}", summary="读取指定行", response_model=NovelContent)
async def get_line(
    session_id: str,
    chapter: int,
    line: int
) -> NovelContent:
    """
    读取指定行的内容。
    
    Args:
        session_id: 会话ID
        chapter: 章节号（从0开始）
        line: 行号（从0开始）
    
    Returns:
        行内容对象
    
    Raises:
        HTTPException: 内容不存在时返回 404
    """
    content = NovelContentService.get_by_line(session_id, chapter, line)
    if not content:
        raise HTTPException(
            status_code=404,
            detail=f"行内容不存在: chapter={chapter}, line={line}"
        )
    return content


@router.get("/lines/{session_id}/{chapter}", summary="读取章节的所有行", response_model=List[NovelContent])
async def get_chapter_lines(
    session_id: str,
    chapter: int
) -> List[NovelContent]:
    """
    读取指定章节的所有行。
    
    Args:
        session_id: 会话ID
        chapter: 章节号
    
    Returns:
        章节所有行的内容列表
    """
    return NovelContentService.get_by_chapter(session_id, chapter)


# ==================== 章节管理 ====================

@router.get("/chapters/{session_id}", summary="获取所有章节", response_model=List[ChapterSummary])
async def get_chapters(session_id: str) -> List[ChapterSummary]:
    """
    获取会话的所有章节摘要列表。
    
    Args:
        session_id: 会话ID
    
    Returns:
        章节摘要列表
    """
    return MemoryService.list_summaries_by_session(session_id)


@router.get("/chapter/{session_id}/{chapter_index}", summary="获取章节详情", response_model=ChapterSummary)
async def get_chapter(
    session_id: str,
    chapter_index: int
) -> ChapterSummary:
    """
    获取指定章节的详细信息。
    
    Args:
        session_id: 会话ID
        chapter_index: 章节索引
    
    Returns:
        章节摘要
    
    Raises:
        HTTPException: 章节不存在时返回 404
    """
    summary = MemoryService.get_summary(chapter_index)
    if not summary or summary.session_id != session_id:
        raise HTTPException(
            status_code=404,
            detail=f"章节不存在: chapter_index={chapter_index}"
        )
    return summary


@router.get("/chapter/{session_id}/{chapter_index}/summary", summary="获取章节梗概")
async def get_chapter_summary(
    session_id: str,
    chapter_index: int
) -> dict:
    """
    获取指定章节的故事梗概（AI生成）。
    
    Args:
        session_id: 会话ID
        chapter_index: 章节索引
    
    Returns:
        包含梗概的字典，如果未生成则返回 None
    """
    summary = MemoryService.get_summary(chapter_index)
    if not summary or summary.session_id != session_id:
        raise HTTPException(
            status_code=404,
            detail=f"章节不存在: chapter_index={chapter_index}"
        )
    return {
        "session_id": session_id,
        "chapter_index": chapter_index,
        "summary": summary.summary
    }


@router.put("/chapter/{session_id}/{chapter_index}/summary", summary="设置章节梗概", response_model=ChapterSummary)
async def put_chapter_summary(
    session_id: str,
    chapter_index: int,
    summary_text: str
) -> ChapterSummary:
    """
    设置/更新章节的故事梗概。
    
    Args:
        session_id: 会话ID
        chapter_index: 章节索引
        summary_text: 故事梗概内容
    
    Returns:
        更新后的章节摘要
    
    Raises:
        HTTPException: 章节不存在时返回 404
    """
    # 更新摘要
    updated_summary = MemoryService.update_summary(
        chapter_index=chapter_index,
        summary=summary_text
    )
    
    if not updated_summary or updated_summary.session_id != session_id:
        raise HTTPException(
            status_code=404,
            detail=f"章节不存在: chapter_index={chapter_index}"
        )
    
    logger.info(f"更新章节梗概: session={session_id}, chapter={chapter_index}")
    return updated_summary


# ==================== 统计信息 ====================

@router.get("/stats/{session_id}", summary="获取阅读统计信息")
async def get_stats(session_id: str) -> dict:
    """
    获取会话的阅读统计信息。
    
    Args:
        session_id: 会话ID
    
    Returns:
        统计信息字典，包含总行数、章节数等
    """
    total_lines = NovelContentService.count_by_session(session_id)
    total_chapters = NovelContentService.count_chapters(session_id)
    
    return {
        "session_id": session_id,
        "total_lines": total_lines,
        "total_chapters": total_chapters
    }
