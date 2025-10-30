"""
Actor 管理的路由。

Actor 可以是角色、地点、组织等小说要素。
提供 CRUD 操作、示例图管理和预定义标签查询。
"""
import uuid
from typing import List, Optional, Dict
from pathlib import Path
from datetime import datetime
from fastapi import APIRouter, HTTPException
from loguru import logger

from schemas.actor import Actor, ActorExample
from schemas.draw import DrawArgs
from constants.actor import character_tags_description
from services.db import ActorService
from services.draw.sd_forge import sd_forge_draw_service
from utils.path import project_home

router = APIRouter(
    prefix="/actor",
    tags=["Actor管理"],
    responses={404: {"description": "Actor不存在"}},
)


# ==================== Actor 基本操作 ====================

@router.post("/create", response_model=Actor, summary="创建Actor")
async def create_actor(
    session_id: str,
    name: str,
    desc: str = "",
    color: str = "#808080",
    tags: Optional[Dict[str, str]] = None
) -> Actor:
    """
    创建新 Actor。
    
    Args:
        session_id: 会话ID
        name: 名称
        desc: 描述
        color: 卡片颜色（如 #FF69B4，女性角色建议粉色）
        tags: 标签字典（可选，建议使用 constants.actor.character_tags_description 中定义的键）
    
    Returns:
        创建的 Actor 对象（包含生成的 actor_id）
    """
    # 生成唯一 Actor ID
    actor_id = str(uuid.uuid4())
    
    # 创建 Actor 对象
    actor = Actor(
        actor_id=actor_id,
        session_id=session_id,
        name=name,
        desc=desc,
        color=color,
        tags=tags or {},
        examples=[]
    )
    
    # 保存到数据库
    created_actor = ActorService.create(actor)
    logger.info(f"创建 Actor: {name} (session: {session_id})")
    
    return created_actor


@router.get("/{actor_id}", response_model=Actor, summary="获取Actor信息")
async def get_actor(
    session_id: str,
    actor_id: str
) -> Actor:
    """
    获取 Actor 详细信息。
    
    Args:
        session_id: 会话ID
        actor_id: Actor ID
    
    Returns:
        Actor 对象
    """
    actor = ActorService.get(actor_id)
    if not actor or actor.session_id != session_id:
        raise HTTPException(status_code=404, detail=f"Actor 不存在: {actor_id}")
    
    return actor


@router.get("/", response_model=List[Actor], summary="列出所有Actor")
async def list_actors(
    session_id: str,
    limit: int = 100
) -> List[Actor]:
    """
    列出会话的所有 Actor。
    
    Args:
        session_id: 会话ID
        limit: 返回数量限制（默认100，最大1000）
    
    Returns:
        Actor 列表
    """
    # 获取会话的所有 Actor
    actors = ActorService.list_by_session(session_id, limit=limit)
    
    return actors


@router.put("/{actor_id}", response_model=Actor, summary="更新Actor")
async def update_actor(
    session_id: str,
    actor_id: str,
    name: Optional[str] = None,
    desc: Optional[str] = None,
    color: Optional[str] = None,
    tags: Optional[Dict[str, str]] = None
) -> Actor:
    """
    更新 Actor 信息。
    
    Args:
        session_id: 会话ID
        actor_id: Actor ID
        name: 新名称（可选）
        desc: 新描述（可选）
        color: 新颜色（可选）
        tags: 新标签字典（可选，会覆盖原有 tags）
    
    Returns:
        更新后的 Actor 对象
    """
    # 先检查 Actor 是否存在且属于该会话
    actor = ActorService.get(actor_id)
    if not actor or actor.session_id != session_id:
        raise HTTPException(status_code=404, detail=f"Actor 不存在: {actor_id}")
    
    # 构建更新字典
    update_data = {}
    if name is not None:
        update_data["name"] = name
    if desc is not None:
        update_data["desc"] = desc
    if color is not None:
        update_data["color"] = color
    if tags is not None:
        update_data["tags"] = tags
    
    # 更新 Actor
    updated_actor = ActorService.update(actor_id, **update_data)
    if not updated_actor:
        raise HTTPException(status_code=404, detail=f"Actor 不存在: {actor_id}")
    
    return updated_actor


@router.delete("/{actor_id}", summary="删除Actor")
async def remove_actor(
    session_id: str,
    actor_id: str
) -> dict:
    """
    删除 Actor。
    
    Args:
        session_id: 会话ID
        actor_id: Actor ID
    
    Returns:
        删除结果
    """
    # 先检查 Actor 是否存在且属于该会话
    actor = ActorService.get(actor_id)
    if not actor or actor.session_id != session_id:
        raise HTTPException(status_code=404, detail=f"Actor 不存在: {actor_id}")
    
    # 删除 Actor
    success = ActorService.delete(actor_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Actor 不存在: {actor_id}")
    
    logger.info(f"删除 Actor: {actor_id} (session: {session_id})")
    return {"message": "Actor 删除成功", "actor_id": actor_id}


# ==================== 示例图管理 ====================

@router.post("/{actor_id}/example", response_model=Actor, summary="添加示例图")
async def add_example(
    session_id: str,
    actor_id: str,
    title: str,
    desc: str,
    image_path: str,
    # DrawArgs 参数
    model: str,
    prompt: str,
    negative_prompt: str = "",
    steps: int = 20,
    cfg_scale: float = 7.0,
    sampler: str = "Euler a",
    seed: int = -1,
    width: int = 512,
    height: int = 512,
    clip_skip: Optional[int] = 2,
    vae: Optional[str] = None,
    loras: Optional[Dict[str, float]] = None
) -> Actor:
    """
    为 Actor 添加示例图。
    
    Args:
        session_id: 会话ID（用于权限校验）
        actor_id: Actor ID
        title: 示例标题
        desc: 示例说明
        image_path: 图片相对路径
        model: 模型名称
        prompt: 正面提示词
        negative_prompt: 负面提示词
        steps: 采样步数
        cfg_scale: CFG 权重
        sampler: 采样器
        seed: 随机种子
        width: 图片宽度
        height: 图片高度
        clip_skip: CLIP skip
        vae: VAE 模型
        loras: LoRA 字典
    
    Returns:
        更新后的 Actor 对象
    """
    # 权限校验
    actor = ActorService.get(actor_id)
    if not actor or actor.session_id != session_id:
        raise HTTPException(status_code=404, detail=f"Actor 不存在: {actor_id}")
    
    # 构建 DrawArgs
    draw_args = DrawArgs(
        model=model,
        prompt=prompt,
        negative_prompt=negative_prompt,
        steps=steps,
        cfg_scale=cfg_scale,
        sampler=sampler,
        seed=seed,
        width=width,
        height=height,
        clip_skip=clip_skip,
        vae=vae,
        loras=loras
    )
    
    # 构建 ActorExample
    example = ActorExample(
        title=title,
        desc=desc,
        draw_args=draw_args,
        image_path=image_path
    )
    
    # 添加示例
    updated = ActorService.add_example(actor_id, example)
    if not updated:
        raise HTTPException(status_code=500, detail=f"添加示例失败: {actor_id}")
    
    logger.success(f"为 Actor 添加示例成功: {actor_id}, title={title}")
    return updated


@router.delete("/{actor_id}/example/{example_index}", response_model=Actor, summary="删除示例图")
async def remove_example(
    session_id: str,
    actor_id: str,
    example_index: int
) -> Actor:
    """
    删除 Actor 的指定示例图。
    
    Args:
        session_id: 会话ID（用于权限校验）
        actor_id: Actor ID
        example_index: 示例图索引
    
    Returns:
        更新后的 Actor 对象
    """
    # 权限校验
    actor = ActorService.get(actor_id)
    if not actor or actor.session_id != session_id:
        raise HTTPException(status_code=404, detail=f"Actor 不存在: {actor_id}")
    
    # 删除示例
    updated = ActorService.remove_example(actor_id, example_index)
    if not updated:
        raise HTTPException(status_code=500, detail=f"删除示例失败: {actor_id}, index={example_index}")
    
    logger.success(f"删除 Actor 示例成功: {actor_id}, index={example_index}")
    return updated


# ==================== 预定义标签查询 ====================

@router.get("/tag-description", summary="获取预定义标签的描述")
async def get_tag_description(
    tag: str
) -> Dict[str, str]:
    """
    获取预定义标签的描述。
    
    Args:
        tag: 标签名
    
    Returns:
        包含标签和描述的字典 {"tag": "...", "description": "..."}
    
    Raises:
        404: 标签名不在预定义列表中
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
    获取所有预定义的 Actor 标签和描述。
    
    Returns:
        所有预定义的标签字典
    """
    return character_tags_description


# ==================== 立绘生成 ====================

@router.post("/{actor_id}/generate_portrait", summary="为 Actor 生成立绘")
async def generate_portrait(
    session_id: str,
    actor_id: str,
    model: str,
    style: str = "",
    negative_prompt: str = "worst quality, lowres, bad anatomy, extra fingers, deformed, blurry",
    width: int = 768,
    height: int = 1152,
    steps: int = 28,
    cfg_scale: float = 6.5,
    sampler: str = "DPM++ 2M Karras",
    seed: int = -1,
    clip_skip: Optional[int] = 2,
    vae: Optional[str] = None,
    loras: Optional[Dict[str, float]] = None,
    save_example: bool = True,
) -> Dict[str, str]:
    """
    依据 Actor 设定快速生成“立绘”图片，并保存到项目目录。

    - prompt 自动由 Actor 的 name/desc/tags 与可选 style 组成
    - 生成后图片保存到 projects/{session_id}/actors/{actor_id}/
    - 若 save_example 为 True，会将该结果写入 Actor.examples
    """
    # 校验 actor 归属
    actor = ActorService.get(actor_id)
    if not actor or actor.session_id != session_id:
        raise HTTPException(status_code=404, detail=f"Actor 不存在: {actor_id}")

    # 组装 prompt
    tag_values = list((actor.tags or {}).values())
    prompt_parts = [actor.name]
    if actor.desc:
        prompt_parts.append(actor.desc)
    if tag_values:
        prompt_parts.extend(tag_values)
    if style:
        prompt_parts.append(style)
    prompt = ", ".join([p for p in prompt_parts if p and p.strip()])

    # 调用绘图
    args = DrawArgs(
        model=model,
        prompt=prompt,
        negative_prompt=negative_prompt or "",
        steps=steps,
        cfg_scale=cfg_scale,
        sampler=sampler,
        seed=seed,
        width=width,
        height=height,
        clip_skip=clip_skip,
        vae=vae,
        loras=loras or {},
    )

    job_id = sd_forge_draw_service.draw(args)

    # 保存图片到 projects 路径
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    out_dir: Path = project_home / session_id / "actors" / actor_id
    out_dir.mkdir(parents=True, exist_ok=True)
    filename = f"portrait-{ts}.png"
    out_path = out_dir / filename
    sd_forge_draw_service.save_image(job_id, out_path)

    # 生成相对路径（相对 projects 根）
    rel_path = out_path.relative_to(project_home).as_posix()

    # 可选：写入 Actor 示例
    if save_example:
        example = ActorExample(
            title=f"立绘 {ts}",
            desc=style or "",
            draw_args=args,
            image_path=rel_path,
        )
        updated = ActorService.add_example(actor_id, example)
        if not updated:
            raise HTTPException(status_code=500, detail="保存示例失败")

    logger.success(f"生成立绘成功: actor={actor.name}, file={rel_path}")
    return {"job_id": job_id, "image_path": rel_path}
