"""应用内使用的 Pydantic 数据模型。

包含示例条目（Example）以及整合的模型元数据
（ModelMeta，通常由 Civitai 获取并在本地缓存）。
"""
from pathlib import Path
from typing import Literal, TYPE_CHECKING
import httpx

from pydantic import BaseModel
from utils.civitai import AIR

if TYPE_CHECKING:
    from .draw import DrawArgs


class Example(BaseModel):
    """单个示例图片引用及其对应生成参数。"""
    url: str | None = None
    args: 'DrawArgs'

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
    
    概念说明：
    - ecosystem: 生态系统/技术代际（sd1, sd2, sdxl）
    - base_model: 基础模型（pony, illustrious, standard 等）
    """
    filename: str
    name: str
    version: str
    desc: str | None
    model_id: int
    version_id: int
    type: Literal['checkpoint', 'lora', 'vae']  # 模型类型
    ecosystem: Literal['sd1', 'sd2', 'sdxl']  # 生态系统/技术代际
    base_model: str | None = None  # 基础模型（pony, illustrious, standard 等），可选
    sha256: str
    trained_words: list[str] = []
    url: str | None = None  # 下载链接（可选）
    web_page_url: str | None = None  # 模型网页链接（如 Civitai 页面）
    examples: list[Example] = []

    @property
    def version_name(self) -> str:
        """
        获取模型版本名称。
        """
        return f'{self.name}-{self.version}'


    @property
    def air(self) -> str:
        """
        生成 AIR (Artificial Intelligence Resources) 标识符。
        
        格式：urn:air:{ecosystem}:{type}:civitai:{model_id}@{version_id}
        
        示例：
        - Checkpoint: urn:air:sd1:checkpoint:civitai:4384@128713
        - LoRA: urn:air:sdxl:lora:civitai:328553@368189
        """
        air = AIR(
            ecosystem=self.ecosystem,
            type=self.type,
            model_id=self.model_id,
            version_id=self.version_id,
        )
        return str(air)


# 延迟解析 forward references
from .draw import DrawArgs  # noqa: E402, F811
Example.model_rebuild()
