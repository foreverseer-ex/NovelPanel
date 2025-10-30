"""
管理会话的路由。

每次将小说转换成漫画的任务都是一次会话。
维护项目基本信息：项目位置、session_id等。
依赖配置（SD后端、LLM后端）使用 settings 模块。
"""
import uuid
from datetime import datetime
from typing import List, Optional, Literal
from fastapi import APIRouter, HTTPException
from loguru import logger

from schemas.session import Session
from services.db import SessionService
from utils.path import project_home

router = APIRouter(
    prefix="/session",
    tags=["会话管理"],
    responses={404: {"description": "会话不存在"}},
)


# ==================== 会话管理 ====================

@router.post("/create", response_model=Session, summary="创建新会话")
async def create_session(
    title: str,
    novel_path: Optional[str] = None
) -> Session:
    """
    创建新的小说转漫画会话。
    
    Args:
        title: 项目标题
        novel_path: 小说文件路径（可选）
    
    Returns:
        创建的会话对象，包含生成的 session_id
    
    实现要点：
    - 生成唯一 session_id（UUID）
    - 创建项目目录结构
    - 初始化小说信息和状态
    - 如果提供了小说路径，触发小说解析
    - 依赖配置从 settings 模块读取
    """
    # 生成唯一会话ID
    session_id = str(uuid.uuid4())
    
    # 创建项目路径
    project_path = str(project_home / session_id)
    
    # 创建会话对象
    session = Session(
        session_id=session_id,
        title=title,
        novel_path=novel_path,
        project_path=project_path,
        status="created",
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )
    
    # 保存到数据库
    created_session = SessionService.create(session)
    logger.info(f"创建会话: {session_id}, 标题: {title}")
    
    return created_session


@router.get("/{session_id}", response_model=Session, summary="获取会话信息")
async def get_session(session_id: str) -> Session:
    """
    获取指定会话的详细信息。
    
    Args:
        session_id: 会话唯一标识
    
    Returns:
        完整的会话对象
    
    Raises:
        NotFoundError: 会话不存在
    """
    session = SessionService.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail=f"会话不存在: {session_id}")
    
    return session


@router.get("/", response_model=List[Session], summary="列出所有会话")
async def list_sessions(
    limit: int = 50,
    offset: int = 0,
    status_filter: Optional[str] = None
) -> List[Session]:
    """
    列出所有会话，支持分页和状态过滤。
    
    Args:
        limit: 返回数量限制
        offset: 偏移量
        status_filter: 按状态过滤（created/analyzing/generating等）
    
    Returns:
        会话列表
    """
    # 获取所有会话
    sessions = SessionService.list(limit=limit, offset=offset)
    
    # 如果有状态过滤，应用过滤
    if status_filter:
        sessions = [s for s in sessions if s.status == status_filter]
    
    return sessions


@router.put("/{session_id}", response_model=Session, summary="更新会话")
async def update_session(
    session_id: str,
    title: Optional[str] = None,
    author: Optional[str] = None,
    total_lines: Optional[int] = None,
    total_chapters: Optional[int] = None,
    current_line: Optional[int] = None,
    current_chapter: Optional[int] = None,
    status: Optional[Literal['created', 'analyzing', 'generating', 'selecting', 'composing', 'completed', 'failed']] = None
) -> Session:
    """
    更新会话信息。
    
    Args:
        session_id: 会话ID
        title: 新标题（可选）
        author: 小说作者（可选）
        total_lines: 总行数（可选）
        total_chapters: 总章节数（可选）
        current_line: 当前处理行（可选）
        current_chapter: 当前处理章节（可选）
        status: 新状态（可选）
    
    Returns:
        更新后的会话对象
    
    实现要点：
    - 只更新提供的字段
    - 自动更新 updated_at 时间戳
    """
    # 构建更新字典（只包含提供的字段）
    update_data = {}
    if title is not None:
        update_data["title"] = title
    if author is not None:
        update_data["author"] = author
    if total_lines is not None:
        update_data["total_lines"] = total_lines
    if total_chapters is not None:
        update_data["total_chapters"] = total_chapters
    if current_line is not None:
        update_data["current_line"] = current_line
    if current_chapter is not None:
        update_data["current_chapter"] = current_chapter
    if status is not None:
        update_data["status"] = status
    
    # 自动更新时间戳
    update_data["updated_at"] = datetime.now()
    
    # 更新会话
    updated_session = SessionService.update(session_id, **update_data)
    if not updated_session:
        raise HTTPException(status_code=404, detail=f"会话不存在: {session_id}")
    
    return updated_session


@router.delete("/{session_id}", summary="删除会话")
async def delete_session(session_id: str) -> dict:
    """
    删除会话及其所有相关数据。
    
    Args:
        session_id: 会话ID
    
    Returns:
        删除操作结果
    
    实现要点：
    - 删除会话记录
    - 可选：删除或归档项目文件
    - 清理关联的记忆、角色、图片等数据
    """
    success = SessionService.delete(session_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"会话不存在: {session_id}")
    
    logger.info(f"删除会话: {session_id}")
    return {"message": "会话删除成功", "session_id": session_id}


@router.put("/{session_id}/status", response_model=Session, summary="更新会话状态")
async def update_session_status(
    session_id: str,
    status: Literal['created', 'analyzing', 'generating', 'selecting', 'composing', 'completed', 'failed']
) -> Session:
    """
    更新会话状态。

    Args:
        session_id: 会话ID
        status: 新的状态

    Returns:
        更新后的会话对象

    用途：
    - 后台任务更新处理状态
    - 标记任务完成或失败
    """
    updated_session = SessionService.update(
        session_id,
        status=status,
        updated_at=datetime.now()
    )
    if not updated_session:
        raise HTTPException(status_code=404, detail=f"会话不存在: {session_id}")
    
    return updated_session


@router.put("/{session_id}/progress", response_model=Session, summary="更新处理进度")
async def update_progress(
    session_id: str,
    current_line: int,
    current_chapter: int
) -> Session:
    """
    更新小说处理进度。
    
    Args:
        session_id: 会话ID
        current_line: 当前处理行
        current_chapter: 当前处理章节
    
    Returns:
        更新后的会话对象
    
    用途：
    - 快速更新处理进度
    - 进度百分比可以通过 current_line / total_lines 计算
    """
    updated_session = SessionService.update(
        session_id,
        current_line=current_line,
        current_chapter=current_chapter,
        updated_at=datetime.now()
    )
    if not updated_session:
        raise HTTPException(status_code=404, detail=f"会话不存在: {session_id}")
    
    return updated_session

