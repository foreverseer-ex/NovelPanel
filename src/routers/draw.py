"""
绘图管理的路由。

简化设计：直接代理 SD-Forge API，所有接口添加 session_id 参数。
"""
from typing import Optional, Dict, Any, List
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from services.db import JobService, BatchJobService
from schemas.draw import Job, BatchJob


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
    # TODO: 实现获取 LoRA 列表逻辑
    raise NotImplementedError("获取 LoRA 列表功能尚未实现")


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
    # TODO: 实现获取 SD 模型列表逻辑
    raise NotImplementedError("获取 SD 模型列表功能尚未实现")


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
    # TODO: 实现获取 SD 选项逻辑
    raise NotImplementedError("获取 SD 选项功能尚未实现")


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
    # TODO: 实现设置 SD 选项逻辑
    raise NotImplementedError("设置 SD 选项功能尚未实现")


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
    # TODO: 实现文生图逻辑
    raise NotImplementedError("文生图功能尚未实现")


@router.get("/image", response_class=FileResponse, summary="获取生成的图像")
async def get_image(
    session_id: str,
    batch_id: str,
    index: int = 0
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
    # TODO: 实现获取图像逻辑
    raise NotImplementedError("获取图像功能尚未实现")


# ==================== Job 管理 ====================

@router.post("/jobs", summary="创建绘图任务", response_model=Job)
async def create_job(job_id: str) -> Job:
    """
    创建单个绘图任务。
    
    Args:
        job_id: 任务ID
    
    Returns:
        创建后的任务对象
    """
    from datetime import datetime
    job = Job(
        job_id=job_id,
        created_at=datetime.now()
    )
    return JobService.create(job)


@router.get("/jobs/{job_id}", summary="获取绘图任务", response_model=Job)
async def get_job(job_id: str) -> Job:
    """
    获取单个绘图任务。
    
    Args:
        job_id: 任务ID
    
    Returns:
        任务对象
    
    Raises:
        HTTPException: 任务不存在时返回 404
    """
    job = JobService.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"任务不存在: {job_id}")
    return job


@router.get("/jobs", summary="获取绘图任务列表", response_model=List[Job])
async def list_jobs(
    limit: Optional[int] = None,
    offset: int = 0
) -> List[Job]:
    """
    获取绘图任务列表。
    
    Args:
        limit: 返回数量限制（None 表示无限制）
        offset: 跳过的记录数
    
    Returns:
        任务列表
    """
    return JobService.list(limit=limit, offset=offset)


@router.delete("/jobs/{job_id}", summary="删除绘图任务")
async def delete_job(job_id: str) -> Dict[str, Any]:
    """
    删除单个绘图任务。
    
    Args:
        job_id: 任务ID
    
    Returns:
        删除结果
    
    Raises:
        HTTPException: 任务不存在时返回 404
    """
    success = JobService.delete(job_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"任务不存在: {job_id}")
    return {"message": "任务删除成功", "job_id": job_id}


# ==================== BatchJob 管理 ====================

@router.post("/batch-jobs", summary="创建批次任务", response_model=BatchJob)
async def create_batch_job(batch_id: str, job_ids: Optional[List[str]] = None) -> BatchJob:
    """
    创建批次任务。
    
    Args:
        batch_id: 批次ID
        job_ids: 任务ID列表（可选）
    
    Returns:
        创建后的批次任务对象
    """
    from datetime import datetime
    batch_job = BatchJob(
        batch_id=batch_id,
        job_ids=job_ids or [],
        created_at=datetime.now()
    )
    return BatchJobService.create(batch_job)


@router.get("/batch-jobs/{batch_id}", summary="获取批次任务", response_model=BatchJob)
async def get_batch_job(batch_id: str) -> BatchJob:
    """
    获取批次任务。
    
    Args:
        batch_id: 批次ID
    
    Returns:
        批次任务对象
    
    Raises:
        HTTPException: 批次任务不存在时返回 404
    """
    batch_job = BatchJobService.get(batch_id)
    if not batch_job:
        raise HTTPException(status_code=404, detail=f"批次任务不存在: {batch_id}")
    return batch_job


@router.get("/batch-jobs", summary="获取批次任务列表", response_model=List[BatchJob])
async def list_batch_jobs(
    limit: Optional[int] = None,
    offset: int = 0
) -> List[BatchJob]:
    """
    获取批次任务列表。
    
    Args:
        limit: 返回数量限制（None 表示无限制）
        offset: 跳过的记录数
    
    Returns:
        批次任务列表
    """
    return BatchJobService.list(limit=limit, offset=offset)


@router.put("/batch-jobs/{batch_id}", summary="更新批次任务", response_model=BatchJob)
async def update_batch_job(batch_id: str, **kwargs) -> BatchJob:
    """
    更新批次任务。
    
    Args:
        batch_id: 批次ID
        **kwargs: 要更新的字段
    
    Returns:
        更新后的批次任务对象
    
    Raises:
        HTTPException: 批次任务不存在时返回 404
    """
    batch_job = BatchJobService.update(batch_id, **kwargs)
    if not batch_job:
        raise HTTPException(status_code=404, detail=f"批次任务不存在: {batch_id}")
    return batch_job


@router.post("/batch-jobs/{batch_id}/jobs/{job_id}", summary="添加任务到批次")
async def add_job_to_batch(batch_id: str, job_id: str) -> BatchJob:
    """
    向批次任务添加任务。
    
    Args:
        batch_id: 批次ID
        job_id: 任务ID
    
    Returns:
        更新后的批次任务对象
    
    Raises:
        HTTPException: 批次任务不存在时返回 404
    """
    batch_job = BatchJobService.add_job(batch_id, job_id)
    if not batch_job:
        raise HTTPException(status_code=404, detail=f"批次任务不存在: {batch_id}")
    return batch_job


@router.delete("/batch-jobs/{batch_id}/jobs/{job_id}", summary="从批次移除任务")
async def remove_job_from_batch(batch_id: str, job_id: str) -> BatchJob:
    """
    从批次任务移除任务。
    
    Args:
        batch_id: 批次ID
        job_id: 任务ID
    
    Returns:
        更新后的批次任务对象
    
    Raises:
        HTTPException: 批次任务不存在时返回 404
    """
    batch_job = BatchJobService.remove_job(batch_id, job_id)
    if not batch_job:
        raise HTTPException(status_code=404, detail=f"批次任务不存在: {batch_id}")
    return batch_job


@router.delete("/batch-jobs/{batch_id}", summary="删除批次任务")
async def delete_batch_job(batch_id: str) -> Dict[str, Any]:
    """
    删除批次任务。
    
    Args:
        batch_id: 批次ID
    
    Returns:
        删除结果
    
    Raises:
        HTTPException: 批次任务不存在时返回 404
    """
    success = BatchJobService.delete(batch_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"批次任务不存在: {batch_id}")
    return {"message": "批次任务删除成功", "batch_id": batch_id}
