"""
Civitai 绘图服务。
参考 tests/civitai/测试civitai.py，封装创建与轮询任务。
"""
from __future__ import annotations

import os
from typing import Dict, Any, Optional

import httpx
from loguru import logger

from settings.app_setting import app_settings
from services.base.draw import BaseDrawService

try:
    import civitai  # civitai-py
except Exception as e:  # pragma: no cover
    civitai = None  # 延迟检查
    logger.warning(f"civitai 库未就绪: {e}")


class CivitaiDrawService(BaseDrawService):
    """Civitai 绘图服务。

    提供：
    - create_text2image: 创建生成任务，返回 token
    - get_job: 通过 token 查询任务状态与结果
    """

    @staticmethod
    def _ensure_token_env():
        token = app_settings.civitai.api_token
        if token and not os.environ.get("CIVITAI_API_TOKEN"):
            os.environ["CIVITAI_API_TOKEN"] = token

    @classmethod
    def create_text2image(
        cls,
        *,
        model: str,
        prompt: str,
        negativePrompt: str = "",
        scheduler: str = "EulerA",
        steps: int = 25,
        cfgScale: float = 7.0,
        width: int = 512,
        height: int = 768,
        seed: int = -1,
        clipSkip: Optional[int] = None,
        loras: Optional[Dict[str, float]] = None,
    ) -> Dict[str, Any]:
        """创建 civitai 文生图任务，返回 { token }。

        参数命名与 civitai 测试保持一致。
        loras 通过 additionalNetworks 传递。
        """
        if civitai is None:
            raise RuntimeError("civitai 依赖未安装或导入失败")

        cls._ensure_token_env()

        option: Dict[str, Any] = {
            "model": model,
            "params": {
                "prompt": prompt,
                "negativePrompt": negativePrompt,
                "scheduler": scheduler,
                "steps": steps,
                "cfgScale": cfgScale,
                "width": width,
                "height": height,
                "seed": seed,
            },
        }
        if clipSkip is not None:
            option["params"]["clipSkip"] = clipSkip

        if loras:
            # additionalNetworks 结构： { urn: { type: "Lora", strength: 1.0 } }
            additional: Dict[str, Any] = {}
            for urn, strength in loras.items():
                additional[urn] = {"type": "Lora", "strength": float(strength)}
            if additional:
                option["additionalNetworks"] = additional

        logger.debug(f"civitai.image.create option={option}")
        resp = civitai.image.create(option)
        # 返回示例：{'token': '...'}
        return resp

    @classmethod
    def get_job(cls, token: str) -> Dict[str, Any]:
        """查询任务状态。

        返回 civitai.jobs.get 的完整响应。
        可从中取：jobs[0].result[0].available 与 blob_url。
        """
        if civitai is None:
            raise RuntimeError("civitai 依赖未安装或导入失败")

        cls._ensure_token_env()

        try:
            resp = civitai.jobs.get(token=token)
        except httpx.ReadTimeout as e:  # 与测试保持一致，超时可重试
            logger.warning(f"civitai.jobs.get 超时: {e}")
            raise
        return resp

    # 统一抽象接口
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
    ) -> Dict[str, Any]:
        return self.create_text2image(
            model=model,
            prompt=prompt,
            negativePrompt=negative_prompt,
            scheduler=sampler,
            steps=steps,
            cfgScale=cfg_scale,
            width=width,
            height=height,
            seed=seed,
            clipSkip=clip_skip,
            loras=loras or {},
        )


civitai_draw_service = CivitaiDrawService()
