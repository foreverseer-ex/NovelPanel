"""
角色管理的路由。

简化设计：基础的 CRUD 操作和预定义标签查询。
"""
from typing import List, Optional, Dict
from fastapi import APIRouter, Query, HTTPException
from schemas.actor import Character
from constants.actor import character_tags_description


router = APIRouter(
    prefix="/actor",
    tags=["角色管理"],
    responses={404: {"description": "角色不存在"}},
)


# ==================== 角色基本操作 ====================

@router.post("/create", response_model=Character, summary="创建角色")
async def create_actor(
    session_id: str,
    name: str,
    tags: Optional[Dict[str, str]] = None
) -> Character:
    """
    创建新角色。
    
    Args:
        session_id: 会话ID
        name: 角色名称
        tags: 角色标签字典（可选，建议使用 constants.actor.character_tags_description 中定义的键）
    
    Returns:
        创建的角色对象（包含生成的 character_id）
    
    实现要点：
    - 生成唯一 character_id
    - tags 字典的值都应该是纯文本字符串
    - 列表类型使用逗号分隔（如：别名、显著特征等）
    """
    # TODO: 实现角色创建逻辑
    raise NotImplementedError("角色创建功能尚未实现")


@router.get("/{character_id}", response_model=Character, summary="获取角色信息")
async def get_actor(
    session_id: str,
    character_id: str
) -> Character:
    """
    获取角色详细信息。
    
    Args:
        session_id: 会话ID
        character_id: 角色ID
    
    Returns:
        角色对象
    """
    # TODO: 实现获取角色信息逻辑
    raise NotImplementedError("获取角色功能尚未实现")


@router.get("/", response_model=List[Character], summary="列出所有角色")
async def list_actors(
    session_id: str,
    limit: int = Query(100, ge=1, le=1000, description="返回数量")
) -> List[Character]:
    """
    列出会话的所有角色。
    
    Args:
        session_id: 会话ID
        limit: 返回数量限制（默认100，最大1000）
    
    Returns:
        角色列表
    """
    # TODO: 实现角色列表查询逻辑
    raise NotImplementedError("角色列表功能尚未实现")


@router.put("/{character_id}", response_model=Character, summary="更新角色")
async def update_actor(
    session_id: str,
    character_id: str,
    name: Optional[str] = None,
    tags: Optional[Dict[str, str]] = None
) -> Character:
    """
    更新角色信息。
    
    Args:
        session_id: 会话ID
        character_id: 角色ID
        name: 新名称（可选）
        tags: 新标签字典（可选，会覆盖原有 tags）
    
    Returns:
        更新后的角色对象
    
    实现要点：
    - 只更新提供的字段
    - tags 如果提供，会完全覆盖原有的 tags
    """
    # TODO: 实现角色更新逻辑
    raise NotImplementedError("角色更新功能尚未实现")


@router.delete("/{character_id}", summary="删除角色")
async def remove_actor(
    session_id: str,
    character_id: str
) -> dict:
    """
    删除角色。
    
    Args:
        session_id: 会话ID
        character_id: 角色ID
    
    Returns:
        删除结果
    """
    # TODO: 实现角色删除逻辑
    raise NotImplementedError("角色删除功能尚未实现")


# ==================== 预定义标签查询 ====================

@router.get("/tag-description", summary="获取预定义标签的描述")
async def get_tag_description(
    tag: str = Query(..., description="标签名")
) -> Dict[str, str]:
    """
    获取预定义标签的描述。
    
    Args:
        tag: 标签名
    
    Returns:
        包含标签和描述的字典 {"tag": "...", "description": "..."}
    
    Raises:
        404: 标签名不在预定义列表中
    
    实现要点：
    - 从 constants.actor.character_tags_description 查找
    - 如果标签不存在，返回 404
    """
    if tag not in character_tags_description:
        raise HTTPException(status_code=404, detail=f"标签名 '{tag}' 不在预定义列表中")
    
    return {
        "tag": tag,
        "description": character_tags_description[tag]
    }


@router.get("/tag-descriptions", summary="获取所有预定义标签和描述")
async def get_all_tag_descriptions() -> Dict[str, str]:
    """
    获取所有预定义的角色标签和描述。
    
    Returns:
        所有预定义的标签字典
    
    实现要点：
    - 返回 constants.actor.character_tags_description 完整字典
    
    示例返回：
    {
        "别名": "角色的其他称呼，逗号分隔...",
        "角色定位": "角色在故事中的定位...",
        "性别": "角色性别...",
        ...
    }
    """
    return character_tags_description
