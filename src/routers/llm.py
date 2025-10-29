"""
LLM 相关的路由。

提供 LLM 交互过程中需要的辅助功能，如添加选项等。
"""
from typing import List, Dict, Any
from fastapi import APIRouter

from schemas import ImageChoice, TextChoice, Choice


router = APIRouter(
    prefix="/llm",
    tags=["LLM 辅助"],
    responses={404: {"description": "资源不存在"}},
)


# 全局会话选项存储（临时方案，后续可能需要改进）
_session_choices: Dict[str, List[Choice]] = {}


@router.post("/add_choices", summary="添加选项到当前消息")
async def add_choices(
    session_id: str,
    choices: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    为当前会话的最后一条助手消息添加选项。
    
    用于 LLM 工具调用后，添加用户可选的选项：
    - 图像选项：draw/draw_batch 工具调用后，展示生成的图像供用户选择
    - 文字选项：提供快捷回复按钮
    
    Args:
        session_id: 会话ID
        choices: 选项列表，每个选项包含 type 和相关字段
            - 图像选项: {"type": "image", "url": "...", "label": "...", "metadata": {...}}
            - 文字选项: {"type": "text", "text": "...", "label": "..."}
    
    Returns:
        操作结果
    
    示例:
        ```python
        # 图像选项
        add_choices(
            session_id="default",
            choices=[
                {"type": "image", "url": "http://...", "label": "图片1"},
                {"type": "image", "url": "http://...", "label": "图片2"}
            ]
        )
        
        # 文字选项
        add_choices(
            session_id="default",
            choices=[
                {"type": "text", "text": "继续生成", "label": "继续"},
                {"type": "text", "text": "重新生成", "label": "重新"}
            ]
        )
        ```
    """
    # 解析并验证 choices
    parsed_choices: List[Choice] = []
    for choice_data in choices:
        choice_type = choice_data.get("type")
        
        if choice_type == "image":
            parsed_choices.append(ImageChoice(**choice_data))
        elif choice_type == "text":
            parsed_choices.append(TextChoice(**choice_data))
        else:
            raise ValueError(f"不支持的选项类型: {choice_type}")
    
    # 存储到全局字典（临时方案）
    _session_choices[session_id] = parsed_choices
    
    return {
        "success": True,
        "session_id": session_id,
        "choices_count": len(parsed_choices),
        "message": f"已为会话 {session_id} 添加 {len(parsed_choices)} 个选项"
    }


@router.get("/get_choices", summary="获取会话的选项")
async def get_choices(session_id: str) -> Dict[str, Any]:
    """
    获取指定会话的选项。
    
    Args:
        session_id: 会话ID
    
    Returns:
        选项列表
    """
    choices = _session_choices.get(session_id, [])
    return {
        "session_id": session_id,
        "choices": [choice.model_dump() for choice in choices]
    }


@router.delete("/clear_choices", summary="清除会话的选项")
async def clear_choices(session_id: str) -> Dict[str, Any]:
    """
    清除指定会话的选项。
    
    Args:
        session_id: 会话ID
    
    Returns:
        操作结果
    """
    if session_id in _session_choices:
        del _session_choices[session_id]
    
    return {
        "success": True,
        "session_id": session_id,
        "message": f"已清除会话 {session_id} 的选项"
    }

