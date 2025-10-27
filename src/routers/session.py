"""
管理会话的路由。

每次将小说转换成漫画的任务都是一次会话。
维护项目基本信息：项目位置、SD后端、LLM后端、session_id等。
"""
from typing import List, Optional, Literal
from fastapi import APIRouter, Query
from schemas.session import Session, DependsConfig, NovelInfo

router = APIRouter(
    prefix="/session",
    tags=["会话管理"],
    responses={404: {"description": "会话不存在"}},
)


# ==================== 会话管理 ====================

@router.post("/create", response_model=Session, summary="创建新会话")
async def create_session(
    title: str,
    novel_path: Optional[str] = None,
    depends: Optional[DependsConfig] = None
) -> Session:
    """
    创建新的小说转漫画会话。
    
    Args:
        title: 项目标题
        novel_path: 小说文件路径（可选）
        depends: 依赖配置（可选，使用默认配置）
    
    Returns:
        创建的会话对象，包含生成的 session_id
    
    实现要点：
    - 生成唯一 session_id（UUID）
    - 创建项目目录结构
    - 初始化依赖配置、小说信息和状态
    - 如果提供了小说路径，触发小说解析
    """
    pass


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
    pass


@router.get("/", response_model=List[Session], summary="列出所有会话")
async def list_sessions(
    limit: int = Query(50, ge=1, le=100, description="返回数量限制"),
    offset: int = Query(0, ge=0, description="偏移量"),
    status_filter: Optional[str] = Query(None, description="状态过滤")
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
    pass


@router.put("/{session_id}", response_model=Session, summary="更新会话")
async def update_session(
    session_id: str,
    title: Optional[str] = None,
    depends: Optional[DependsConfig] = None,
    novel: Optional[NovelInfo] = None,
    status: Optional[Literal['created', 'analyzing', 'generating', 'selecting', 'composing', 'completed', 'failed']] = None
) -> Session:
    """
    更新会话信息。
    
    Args:
        session_id: 会话ID
        title: 新标题（可选）
        depends: 新依赖配置（可选）
        novel: 新小说信息（可选）
        status: 新状态（可选）
    
    Returns:
        更新后的会话对象
    
    实现要点：
    - 只更新提供的字段
    - 自动更新 updated_at 时间戳
    """
    pass


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
    pass


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
    pass


@router.put("/{session_id}/depends", response_model=Session, summary="更新依赖配置")
async def update_depends_config(
        session_id: str,
        depends: DependsConfig
) -> Session:
    """
    更新会话依赖配置。

    Args:
        session_id: 会话ID
        depends: 依赖配置

    Returns:
        更新后的会话对象

    用途：
    - 更新会话依赖配置（如SD后端、LLM后端）
    - 触发重新分析或重新生成任务
    """
    pass

@router.put("/{session_id}/novel", response_model=Session, summary="更新小说信息")
async def update_novel_info(
    session_id: str,
    novel: NovelInfo
) -> Session:
    """
    更新小说信息（包括进度）。
    
    Args:
        session_id: 会话ID
        novel: 小说信息
    
    Returns:
        更新后的会话对象
    
    用途：
    - 更新小说元数据（作者、总行数、总章节数）
    - 更新处理进度（当前行、当前章节）
    - 进度百分比会自动计算
    """
    pass

