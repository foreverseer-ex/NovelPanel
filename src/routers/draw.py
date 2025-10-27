"""
绘图管理的路由。

简化设计：直接代理 SD-Forge API，所有接口添加 session_id 参数。
"""
from typing import Optional, Dict, Any, List
from fastapi import APIRouter, Query
from fastapi.responses import FileResponse


router = APIRouter(
    prefix="/draw",
    tags=["绘图管理"],
    responses={404: {"description": "资源不存在"}},
)


# ==================== SD-Forge API 代理 ====================

@router.get("/loras", summary="获取 LoRA 模型列表")
async def get_loras(session_id: str) -> Dict[str, Any]:
    """
    获取 LoRA 模型列表。
    
    Args:
        session_id: 会话ID
    
    Returns:
        LoRA 模型列表（来自 sd-forge /sdapi/v1/loras）
    
    实现要点：
    - 直接调用 sd_forge_service.get_loras()
    """
    pass


@router.get("/sd-models", summary="获取 SD 模型列表")
async def get_sd_models(session_id: str) -> Dict[str, Any]:
    """
    获取 SD 模型列表。
    
    Args:
        session_id: 会话ID
    
    Returns:
        SD 模型列表（来自 sd-forge /sdapi/v1/sd-models）
    
    实现要点：
    - 直接调用 sd_forge_service.get_sd_models()
    """
    pass


@router.get("/options", summary="获取 SD 选项")
async def get_options(session_id: str) -> Dict[str, Any]:
    """
    获取 SD 选项配置。
    
    Args:
        session_id: 会话ID
    
    Returns:
        SD 选项配置（来自 sd-forge /sdapi/v1/options）
    
    实现要点：
    - 直接调用 sd_forge_service.get_options()
    """
    pass


@router.post("/options", summary="设置 SD 选项")
async def set_options(
    session_id: str,
    sd_model_checkpoint: Optional[str] = None,
    sd_vae: Optional[str] = None
) -> dict:
    """
    设置 SD 选项（切换模型）。
    
    Args:
        session_id: 会话ID
        sd_model_checkpoint: 模型检查点（来自 /sdapi/v1/sd-models 的 title 字段）
        sd_vae: VAE 模型
    
    Returns:
        设置结果
    
    实现要点：
    - 直接调用 sd_forge_service.set_options()
    """
    pass


# ==================== 图像生成 ====================

@router.post("/generate", summary="文生图")
async def generate(
    session_id: str,
    batch_id: str,
    prompt: str,
    negative_prompt: str = "",
    loras: Optional[Dict[str, float]] = None,
    styles: Optional[List[str]] = None,
    seed: int = -1,
    sampler_name: str = "DPM++ 2M Karras",
    batch_size: int = 1,
    n_iter: int = 1,
    steps: int = 30,
    cfg_scale: float = 7.0,
    width: int = 1024,
    height: int = 1024,
    save_images: bool = True
) -> Dict[str, Any]:
    """
    文生图。
    
    Args:
        session_id: 会话ID
        batch_id: 批次ID（用于标识这次生成）
        prompt: 正向提示词
        negative_prompt: 负向提示词
        loras: LoRA 配置 {name: weight}
        styles: 样式预设列表
        seed: 随机种子（-1 表示随机）
        sampler_name: 采样器名称
        batch_size: 批量大小
        n_iter: 迭代次数
        steps: 采样步数
        cfg_scale: CFG Scale
        width: 图像宽度
        height: 图像高度
        save_images: 是否在服务端保存图像
    
    Returns:
        生成结果（包含 base64 图像列表、info、parameters）
    
    实现要点：
    - 调用 sd_forge_service.create_text2image()
    - 保存图像到 storage/sessions/{session_id}/batches/{batch_id}/
    - 图像命名：0.png, 1.png, ...（根据 batch_size）
    """
    pass


@router.get("/image", response_class=FileResponse, summary="获取生成的图像")
async def get_image(
    session_id: str,
    batch_id: str,
    index: int = Query(0, ge=0, description="图像索引（batch 中的第几张）")
) -> FileResponse:
    """
    获取生成的图像文件。
    
    Args:
        session_id: 会话ID
        batch_id: 批次ID
        index: 图像索引（默认0，即批次中的第一张）
    
    Returns:
        图像文件
    
    实现要点：
    - 返回 storage/sessions/{session_id}/batches/{batch_id}/{index}.png
    - 设置正确的 Content-Type
    - 如果文件不存在，返回404
    """
    pass
