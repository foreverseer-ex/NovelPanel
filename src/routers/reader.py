"""
阅读器的路由。

简化设计：按行读取小说，每行对应一个段落/一张图片。
小说元数据已合并到 Session 模型中。
"""
from typing import Optional
from fastapi import APIRouter, Query
from schemas.memory import ChapterSummary

router = APIRouter(
    prefix="/reader",
    tags=["阅读器"],
    responses={404: {"description": "内容不存在"}},
)


# ==================== 小说解析 ====================

@router.post("/parse", summary="解析小说")
async def parse_novel(
        session_id: str,
) -> dict:
    """
    解析 TXT 小说文件，按行分割，并更新 Session 元数据。
    
    Args:
        session_id: 会话ID
    
    Returns:
        解析结果摘要（success, total_lines, total_chapters）
    
    实现要点：
    - 读取 TXT 文件，按行分割
    - 智能识别章节标题（第X章、Chapter X等）
    - 记录每个章节的起止行号
    - 更新 Session 的 total_lines、author 等字段
    - 缓存章节摘要到会话目录
    """
    pass


# ==================== 行读取 ====================

@router.get("/line/{line_index}", response_model=str, summary="读取第 n 行")
async def get_line(
        session_id: str,
        line_index: int = Query(..., ge=0, description="行号（从0开始）")
) -> str:
    """
    读取指定行的内容。
    
    Args:
        session_id: 会话ID
        line_index: 行号（全局，从0开始）
    
    Returns:
        行内容（字符串）
    """
    pass


@router.get("/line/{line_index}/chapter", response_model=int, summary="获取行对应的章节索引")
async def get_line_chapter_index(
        session_id: str,
        line_index: int
) -> int:
    """
    返回指定行所属的章节索引。
    
    Args:
        session_id: 会话ID
        line_index: 行号
    
    Returns:
        章节索引（从0开始）
    """
    pass


# ==================== 章节管理 ====================

@router.get("/chapters", response_model=list[ChapterSummary], summary="获取所有章节")
async def get_chapters(
        session_id: str
) -> list[ChapterSummary]:
    """
    获取所有章节的摘要列表。
    
    Args:
        session_id: 会话ID
    
    Returns:
        章节摘要列表
    """
    pass


@router.get("/chapter/{chapter_index}", response_model=ChapterSummary, summary="获取章节详情")
async def get_chapter(
        session_id: str,
        chapter_index: int = Query(..., ge=0, description="章节索引")
) -> ChapterSummary:
    """
    获取指定章节的详细信息。
    
    Args:
        session_id: 会话ID
        chapter_index: 章节索引
    
    Returns:
        章节摘要
    """
    pass


@router.get("/chapter/{chapter_index}/summary", response_model=Optional[str], summary="获取章节梗概")
async def get_chapter_summary(
        session_id: str,
        chapter_index: int = Query(..., ge=0, description="章节索引")
) -> Optional[str]:
    """
    获取指定章节的故事梗概（AI生成）。
    
    Args:
        session_id: 会话ID
        chapter_index: 章节索引
    
    Returns:
        章节梗概，如果未生成则返回 None
    """
    pass


@router.put("/chapter/{chapter_index}/summary", response_model=ChapterSummary, summary="设置章节梗概")
async def put_chapter_summary(
        session_id: str,
        chapter_index: int,
        summary: str
) -> ChapterSummary:
    """
    设置/更新章节的故事梗概。
    
    Args:
        session_id: 会话ID
        chapter_index: 章节索引
        summary: 故事梗概内容
    
    Returns:
        更新后的章节摘要
    
    实现要点：
    - 存储到会话目录
    - 用于 AI 生成图像时提供上下文
    """
    pass
