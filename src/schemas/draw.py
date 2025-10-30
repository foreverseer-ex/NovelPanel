"""
绘图相关的数据模型。
"""
from datetime import datetime
from pydantic import BaseModel
from sqlalchemy import Column, JSON
from sqlalchemy.ext.mutable import MutableList
from sqlmodel import SQLModel, Field


class DrawArgs(BaseModel):
    """绘图参数。
    
    包含所有 Stable Diffusion 绘图所需的参数。
    """
    model: str
    prompt: str
    negative_prompt: str = ""
    steps: int = 20
    cfg_scale: float = 7.0
    sampler: str = "Euler a"
    seed: int = -1
    width: int = 512
    height: int = 512
    clip_skip: int | None = 2
    vae: str | None = None  # VAE 模型名称
    loras: dict[str, float] | None = None  # LoRA 字典 {name: strength}


class Job(SQLModel, table=True):
    """
    单个绘图任务。
    
    记录单次图像生成任务的基本信息。
    """
    job_id: str = Field(description="任务唯一标识", primary_key=True)
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")


class BatchJob(SQLModel, table=True):
    """
    批量绘图任务。
    
    管理一批相关的绘图任务。
    """
    batch_id: str = Field(description="批次唯一标识", primary_key=True)
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    job_ids: list[str] = Field(
        default_factory=list,
        sa_column=Column(MutableList.as_mutable(JSON())),
        description="关联的任务 ID 列表"
    )

