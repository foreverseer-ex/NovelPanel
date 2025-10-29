"""
绘图相关的数据模型。
"""
from pydantic import BaseModel


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

