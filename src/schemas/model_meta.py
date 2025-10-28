"""应用内使用的 Pydantic 数据模型。

包含生成参数（GenerateArg）、示例条目（Example）以及整合的模型元数据
（ModelMeta，通常由 Civitai 获取并在本地缓存）。
"""
from pathlib import Path
from typing import Literal
import httpx

from pydantic import BaseModel


class GenerateArg(BaseModel):
    """示例图片的 Stable Diffusion 生成参数。"""
    model: str
    prompt: str
    negative_prompt: str = ""
    steps: int = 20
    cfg_scale: float = 7.0
    sampler: str = "Euler a"
    seed: int = -1
    width: int = 512
    height: int = 512
    batch_size: int = 1


class Example(BaseModel):
    """单个示例图片引用及其对应生成参数。"""
    url: str | None = None
    args: GenerateArg

    @property
    def filename(self) -> Path | None:
        """
        获取示例的文件名。
        """
        if self.url is None:
            return None
        return Path(httpx.URL(self.url).path.split('/')[-1])


class ModelMeta(BaseModel):
    """
    模型元数据。
    """
    filename: str
    name: str
    version: str
    desc: str | None
    model_id: int
    type: Literal['Checkpoint', 'LORA', 'vae']
    base_model: Literal['sd1', 'sdxl', 'Illustrious']
    sha256: str
    trained_words: list[str] = []
    download_url: str
    examples: list[Example] = []

    @property
    def version_name(self) -> str:
        """
        获取模型版本名称。
        """
        return f'{self.name}-{self.version}'
        # return Path(self.filename).stem
