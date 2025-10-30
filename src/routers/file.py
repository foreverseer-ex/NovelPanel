"""
文件管理的路由。

简化设计：主要提供图像文件的访问。
小说文件的上传和管理通过 Session 和 NovelContent 服务处理。
"""
from pathlib import Path
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from services.db import ActorService
from schemas.actor import ActorExample

router = APIRouter(
    prefix="/file",
    tags=["文件管理"],
    responses={404: {"description": "文件不存在"}},
)


# ==================== Actor 示例图访问 ====================

@router.get("/actor-example/{actor_id}/{example_index}", response_class=FileResponse, summary="获取 Actor 示例图")
async def get_actor_example_image(actor_id: str, example_index: int) -> FileResponse:
    """
    获取 Actor 示例图文件。
    
    Args:
        actor_id: Actor ID
        example_index: 示例图索引
    
    Returns:
        图像文件
    
    Raises:
        HTTPException: 图像不存在时返回 404
    """
    actor = ActorService.get(actor_id)
    if not actor:
        raise HTTPException(status_code=404, detail=f"Actor 不存在: {actor_id}")
    
    if example_index < 0 or example_index >= len(actor.examples):
        raise HTTPException(status_code=404, detail=f"示例图索引越界: {example_index}")
    
    example_dict = actor.examples[example_index]
    example = ActorExample(**example_dict)
    image_path = Path(example.image_path)
    
    if not image_path.exists():
        raise HTTPException(status_code=404, detail=f"示例图文件不存在: {example.image_path}")
    
    return FileResponse(
        path=str(image_path),
        media_type="image/png",
        filename=image_path.name
    )


# ==================== 生成图像访问 ====================

@router.get("/image/{session_id}/{line}", response_class=FileResponse, summary="获取生成的图像")
async def get_generated_image(session_id: str, line: int) -> FileResponse:
    """
    获取指定行的生成图像。
    
    Args:
        session_id: 会话ID
        line: 行号（从0开始）
    
    Returns:
        图像文件
    
    Raises:
        HTTPException: 图像不存在时返回 404
    """
    # 图像保存在项目的 images 目录
    image_path = Path(f"storage/data/projects/{session_id}/images/{line}.png")
    
    if not image_path.exists():
        raise HTTPException(
            status_code=404,
            detail=f"生成图像不存在: line={line}"
        )
    
    return FileResponse(
        path=str(image_path),
        media_type="image/png",
        filename=f"{line}.png"
    )


# ==================== 项目文件访问 ====================

@router.get("/project/{session_id}/novel", response_class=FileResponse, summary="获取项目小说文件")
async def get_project_novel(session_id: str) -> FileResponse:
    """
    获取项目的原始小说文件。
    
    Args:
        session_id: 会话ID
    
    Returns:
        小说文件
    
    Raises:
        HTTPException: 文件不存在时返回 404
    
    注意：
        这个路由返回原始上传的小说文件，
        不是数据库中的 NovelContent。
    """
    from services.db import SessionService
    
    session = SessionService.get(session_id)
    if not session or not session.novel_path:
        raise HTTPException(status_code=404, detail="小说文件不存在")
    
    novel_path = Path(session.novel_path)
    if not novel_path.exists():
        raise HTTPException(status_code=404, detail="小说文件不存在")
    
    return FileResponse(
        path=str(novel_path),
        media_type="text/plain",
        filename=novel_path.name
    )
