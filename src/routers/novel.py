"""
小说内容管理的路由。

提供对小说文本内容的 CRUD 操作，按章节和行号组织。
"""
from typing import List, Optional
from fastapi import APIRouter, HTTPException
from loguru import logger

from schemas.novel import NovelContent
from services.db import NovelContentService

router = APIRouter(
    prefix="/novel",
    tags=["小说内容"],
    responses={404: {"description": "内容不存在"}},
)


# ==================== 小说内容操作 ====================

@router.post("/content", summary="创建小说内容", response_model=NovelContent)
async def create_content(
    session_id: str,
    chapter: int,
    line: int,
    content: str
) -> NovelContent:
    """
    创建新的小说内容条目。
    
    Args:
        session_id: 会话ID
        chapter: 章节号（从0开始）
        line: 行号（从0开始）
        content: 行内容
    
    Returns:
        创建的小说内容对象
    """
    novel_content = NovelContent(
        session_id=session_id,
        chapter=chapter,
        line=line,
        content=content
    )
    created = NovelContentService.create(novel_content)
    logger.info(f"创建小说内容: session={session_id}, chapter={chapter}, line={line}")
    return created


@router.post("/content/batch", summary="批量创建小说内容", response_model=List[NovelContent])
async def batch_create_content(
    contents: List[dict]
) -> List[NovelContent]:
    """
    批量创建小说内容。
    
    Args:
        contents: 内容列表，每项包含 session_id, chapter, line, content
    
    Returns:
        创建的小说内容列表
    """
    novel_contents = [
        NovelContent(
            session_id=c["session_id"],
            chapter=c["chapter"],
            line=c["line"],
            content=c["content"]
        )
        for c in contents
    ]
    created = NovelContentService.batch_create(novel_contents)
    logger.info(f"批量创建小说内容: {len(created)} 条")
    return created


@router.get("/content/session/{session_id}", summary="获取会话的所有内容", response_model=List[NovelContent])
async def get_session_content(
    session_id: str,
    limit: Optional[int] = None
) -> List[NovelContent]:
    """
    获取会话的所有小说内容。
    
    Args:
        session_id: 会话ID
        limit: 返回数量限制
    
    Returns:
        小说内容列表
    """
    return NovelContentService.get_by_session(session_id, limit=limit)


@router.get("/content/chapter/{session_id}/{chapter}", summary="获取指定章节的内容", response_model=List[NovelContent])
async def get_chapter_content(
    session_id: str,
    chapter: int
) -> List[NovelContent]:
    """
    获取指定章节的所有内容。
    
    Args:
        session_id: 会话ID
        chapter: 章节号
    
    Returns:
        章节内容列表
    """
    return NovelContentService.get_by_chapter(session_id, chapter)


@router.get("/content/line/{session_id}/{chapter}/{line}", summary="获取指定行的内容", response_model=NovelContent)
async def get_line_content(
    session_id: str,
    chapter: int,
    line: int
) -> NovelContent:
    """
    获取指定行的内容。
    
    Args:
        session_id: 会话ID
        chapter: 章节号
        line: 行号
    
    Returns:
        行内容
    
    Raises:
        HTTPException: 内容不存在时返回 404
    """
    content = NovelContentService.get_by_line(session_id, chapter, line)
    if not content:
        raise HTTPException(status_code=404, detail=f"内容不存在: chapter={chapter}, line={line}")
    return content


@router.get("/content/range/{session_id}/{chapter}", summary="获取行范围的内容", response_model=List[NovelContent])
async def get_line_range_content(
    session_id: str,
    chapter: int,
    start_line: int,
    end_line: int
) -> List[NovelContent]:
    """
    获取指定行范围的内容。
    
    Args:
        session_id: 会话ID
        chapter: 章节号
        start_line: 起始行号（包含）
        end_line: 结束行号（包含）
    
    Returns:
        行内容列表
    """
    return NovelContentService.get_line_range(session_id, chapter, start_line, end_line)


@router.get("/content/count/{session_id}", summary="获取会话的内容总数")
async def count_session_content(session_id: str) -> dict:
    """
    获取会话的小说内容总数。
    
    Args:
        session_id: 会话ID
    
    Returns:
        包含总数的字典
    """
    count = NovelContentService.count_by_session(session_id)
    return {"session_id": session_id, "count": count}


@router.get("/content/chapters/count/{session_id}", summary="获取会话的章节总数")
async def count_session_chapters(session_id: str) -> dict:
    """
    获取会话的章节总数。
    
    Args:
        session_id: 会话ID
    
    Returns:
        包含章节数的字典
    """
    count = NovelContentService.count_chapters(session_id)
    return {"session_id": session_id, "chapters": count}


@router.delete("/content/session/{session_id}", summary="删除会话的所有内容")
async def delete_session_content(session_id: str) -> dict:
    """
    删除会话的所有小说内容。
    
    Args:
        session_id: 会话ID
    
    Returns:
        删除结果
    """
    count = NovelContentService.delete_by_session(session_id)
    logger.info(f"删除会话小说内容: {session_id}, 共 {count} 条")
    return {"message": "会话内容删除成功", "session_id": session_id, "deleted_count": count}


@router.delete("/content/chapter/{session_id}/{chapter}", summary="删除指定章节的内容")
async def delete_chapter_content(session_id: str, chapter: int) -> dict:
    """
    删除指定章节的所有内容。
    
    Args:
        session_id: 会话ID
        chapter: 章节号
    
    Returns:
        删除结果
    """
    count = NovelContentService.delete_by_chapter(session_id, chapter)
    logger.info(f"删除章节内容: session={session_id}, chapter={chapter}, 共 {count} 条")
    return {"message": "章节内容删除成功", "session_id": session_id, "chapter": chapter, "deleted_count": count}

