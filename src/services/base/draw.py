"""
绘图服务基础抽象类。
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Dict


class BaseDrawService(ABC):
    """绘图服务统一接口。"""

    @abstractmethod
    def draw(
        self,
        *,
        model: str,
        prompt: str,
        negative_prompt: str = "",
        steps: int = 20,
        cfg_scale: float = 7.0,
        sampler: str = "Euler a",
        seed: int = -1,
        width: int = 512,
        height: int = 512,
        clip_skip: int | None = 2,
        loras: Dict[str, float] | None = None,
    ) -> Dict:
        """执行文生图。

        返回后端的原始响应或规范化结果字典。
        """
        raise NotImplementedError
