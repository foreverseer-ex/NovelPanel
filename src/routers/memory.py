"""
记忆管理的路由。

存储和检索会话上下文信息：背景设定、世界观、用户偏好、重要情节等。
为 AI 提供长期记忆能力。

简化设计：
- 所有记忆使用 MemoryEntry 键值对存储
- 键名定义在 constants.memory 中：
  - novel_memory_description: 与小说内容相关（世界观、情节等）
  - user_memory_description: 与用户偏好相关（艺术风格、标签偏好等）
  - memory_description: 合并了上述两个字典
- 所有 value 统一使用纯文本字符串（列表类型用逗号分隔）
- 支持灵活的查询和聚合
"""
import uuid
from datetime import datetime
from typing import List, Optional, Dict
from fastapi import APIRouter, Query, HTTPException
from loguru import logger

from schemas.memory import MemoryEntry
from constants.memory import memory_description
from services.db import MemoryService

router = APIRouter(
    prefix="/memory",
    tags=["记忆系统"],
    responses={404: {"description": "记忆不存在"}},
)


# ==================== 记忆条目操作 ====================

@router.post("/create", response_model=MemoryEntry, summary="创建记忆条目")
async def create_memory(
    session_id: str,
    key: str,
    value: str,
    description: Optional[str] = None
) -> MemoryEntry:
    """
    创建新的记忆条目。
    
    Args:
        session_id: 会话ID
        key: 记忆键名（建议使用 constants.memory.memory_description 中定义的键）
        value: 记忆值（纯文本字符串，列表类型使用逗号分隔，如 "tag1, tag2, tag3"）
        description: 键的描述（可选，会自动从 constants.memory.memory_description 获取）
    
    Returns:
        创建的记忆条目（包含生成的 memory_id）
    
    实现要点：
    - 生成唯一 memory_id
    - 自动记录时间戳
    - 如果 description 为空，自动从 constants.memory.memory_description 获取
    """
    # 生成唯一记忆ID
    memory_id = str(uuid.uuid4())
    
    # 如果没有提供描述，从预定义字典获取
    if description is None:
        description = memory_description.get(key, "")
    
    # 创建记忆条目对象
    entry = MemoryEntry(
        memory_id=memory_id,
        session_id=session_id,
        key=key,
        value=value,
        description=description,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )
    
    # 保存到数据库
    created_entry = MemoryService.create_entry(entry)
    logger.info(f"创建记忆条目: {key} (session: {session_id})")
    
    return created_entry


@router.get("/{memory_id}", response_model=MemoryEntry, summary="获取记忆条目")
async def get_memory(
    session_id: str,
    memory_id: str
) -> MemoryEntry:
    """
    获取指定记忆条目。
    
    Args:
        session_id: 会话ID
        memory_id: 记忆ID
    
    Returns:
        记忆条目
    """
    entry = MemoryService.get_entry(memory_id)
    if not entry or entry.session_id != session_id:
        raise HTTPException(status_code=404, detail=f"记忆条目不存在: {memory_id}")
    
    return entry


@router.get("/query", response_model=List[MemoryEntry], summary="查询记忆")
async def query_memories(
    session_id: str,
    keys: Optional[List[str]] = Query(None, description="键名过滤"),
    limit: int = Query(100, ge=1, le=1000, description="返回数量")
) -> List[MemoryEntry]:
    """
    查询记忆条目。
    
    Args:
        session_id: 会话ID
        keys: 键名过滤（可选）
        limit: 返回数量限制（默认100，最大1000）
    
    Returns:
        符合条件的记忆列表
    
    实现要点：
    - 支持按键名查询
    - 按时间排序
    - 支持分页
    """
    # 获取所有记忆条目
    entries = MemoryService.list_entries(limit=limit)
    
    # 过滤：只返回属于该会话的记忆
    entries = [e for e in entries if e.session_id == session_id]
    
    # 如果提供了键名过滤，应用过滤
    if keys:
        entries = [e for e in entries if e.key in keys]
    
    return entries


@router.put("/{memory_id}", response_model=MemoryEntry, summary="更新记忆")
async def update_memory(
    session_id: str,
    memory_id: str,
    update_data: dict
) -> MemoryEntry:
    """
    更新记忆条目。
    
    Args:
        session_id: 会话ID
        memory_id: 记忆ID
        update_data: 更新内容
    
    Returns:
        更新后的记忆条目
    """
    # 先检查记忆是否存在且属于该会话
    entry = MemoryService.get_entry(memory_id)
    if not entry or entry.session_id != session_id:
        raise HTTPException(status_code=404, detail=f"记忆条目不存在: {memory_id}")
    
    # 自动更新时间戳
    update_data["updated_at"] = datetime.now()
    
    # 更新记忆
    updated_entry = MemoryService.update_entry(memory_id, **update_data)
    if not updated_entry:
        raise HTTPException(status_code=404, detail=f"记忆条目不存在: {memory_id}")
    
    return updated_entry


@router.delete("/{memory_id}", summary="删除记忆")
async def delete_memory(
    session_id: str,
    memory_id: str
) -> dict:
    """
    删除记忆条目。
    
    Args:
        session_id: 会话ID
        memory_id: 记忆ID
    
    Returns:
        删除结果
    """
    # 先检查记忆是否存在且属于该会话
    entry = MemoryService.get_entry(memory_id)
    if not entry or entry.session_id != session_id:
        raise HTTPException(status_code=404, detail=f"记忆条目不存在: {memory_id}")
    
    # 删除记忆
    success = MemoryService.delete_entry(memory_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"记忆条目不存在: {memory_id}")
    
    logger.info(f"删除记忆条目: {memory_id} (session: {session_id})")
    return {"message": "记忆条目删除成功", "memory_id": memory_id}


# ==================== 预定义键查询 ====================

@router.get("/key-description", summary="获取预定义键的描述")
async def get_key_description(
    key: str = Query(..., description="记忆键名")
) -> Dict[str, str]:
    """
    获取预定义键的描述。
    
    Args:
        key: 记忆键名
    
    Returns:
        包含键和描述的字典 {"key": "...", "description": "..."}
    
    Raises:
        404: 键名不在预定义列表中
    
    实现要点：
    - 从 constants.memory.memory_description 查找
    - 如果键不存在，返回 404
    """
    if key not in memory_description:
        raise HTTPException(status_code=404, detail=f"键名 '{key}' 不在预定义列表中")
    
    return {
        "key": key,
        "description": memory_description[key]
    }


@router.get("/key-descriptions", summary="获取所有预定义键和描述")
async def get_all_key_descriptions() -> Dict[str, str]:
    """
    获取所有预定义的记忆键和描述。
    
    Returns:
        所有预定义的键值对字典
    
    实现要点：
    - 返回 constants.memory.memory_description 完整字典
    - 包含 novel_memory_description 和 user_memory_description 的所有键
    
    示例返回：
    {
        "作品类型": "小说的类型/题材，如：修仙、都市、科幻...",
        "主题": "作品的核心主题和表达的思想...",
        "艺术风格": "用户偏好的画面风格",
        ...
    }
    """
    return memory_description

