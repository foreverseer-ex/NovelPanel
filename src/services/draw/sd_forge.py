"""
sd-forge 服务（迁移到 services.draw）
"""
from typing import Optional, Dict, Any

import httpx

from settings.app_setting import app_settings
from services.base.draw import BaseDrawService


class SdForgeService(BaseDrawService):
    """SD‑Forge（Stable Diffusion WebUI）HTTP API 客户端封装。

    - base_url：sd-forge/sd-webui 服务地址，默认 http://127.0.0.1:7860
    - 功能：获取模型列表、读取/设置 options、调用 txt2img 生成。
    """

    @staticmethod
    def get_loras() -> Dict[str, Any]:
        """
        获取 LoRA 模型列表（/sdapi/v1/loras）。

        :return: LoRA 模型列表
        """
        url = f"{app_settings.sd_forge.base_url}/sdapi/v1/loras"
        with httpx.Client(timeout=app_settings.sd_forge.timeout) as client:
            resp = client.get(url)
            resp.raise_for_status()
            return resp.json()

    @staticmethod
    def get_sd_models() -> Dict[str, Any]:
        """
        获取 SD 模型列表（/sdapi/v1/sd-models）。

        :return: SD 模型列表
        """
        url = f"{app_settings.sd_forge.base_url}/sdapi/v1/sd-models"
        with httpx.Client(timeout=app_settings.sd_forge.timeout) as client:
            resp = client.get(url)
            resp.raise_for_status()
            return resp.json()

    @staticmethod
    def get_options() -> Dict[str, Any]:
        """
        获取 SD 模型选项（/sdapi/v1/options）。

        :return: SD 模型选项
        """
        url = f"{app_settings.sd_forge.base_url}/sdapi/v1/options"
        with httpx.Client(timeout=app_settings.sd_forge.timeout) as client:
            resp = client.get(url)
            resp.raise_for_status()
            return resp.json()

    @staticmethod
    def set_options(
            sd_model_checkpoint: str | None = None,
            sd_vae: str | None = None,
    ) -> None:
        """
        切换 SD 模型（/sdapi/v1/options）。

        :param sd_model_checkpoint: 模型检查点，来自 /sdapi/v1/sd-models 的 title 字段
        :param sd_vae: VAE 模型，来自 /sdapi/v1/options 的 sd_vae 字段
        :return: None
        """
        url = f"{app_settings.sd_forge.base_url}/sdapi/v1/options"
        payload = {}
        if sd_model_checkpoint:
            payload["sd_model_checkpoint"] = sd_model_checkpoint
        if sd_vae:
            payload["sd_vae"] = sd_vae
        with httpx.Client(timeout=app_settings.sd_forge.timeout) as client:
            resp = client.post(url, json=payload)
            resp.raise_for_status()

    @classmethod
    # pylint: disable=too-many-arguments,too-many-positional-arguments,too-many-locals
    def create_text2image(
            cls,
            prompt: str,
            negativePrompt: str = "",
            loras: Optional[Dict[str, float]] = None,
            styles: list[str] = (),
            seed: int = -1,
            scheduler: str = 'DPM++ 2M Karras',
            steps: int = 30,
            cfgScale: float = 7.0,
            width: int = 1024,
            height: int = 1024,
            clipSkip: int | None = None,
            save_images: bool = True,
    ) -> Dict[str, Any]:
        """
        文生图（/sdapi/v1/txt2img）。
        """
        final_prompt = prompt
        if loras:
            tags = []
            for name, weight in loras.items():
                tags.append(f"<lora:{name}:{weight}>")
            if tags:
                final_prompt = " ".join(tags) + " " + (prompt or "")

        payload: Dict[str, Any] = {
            "prompt": final_prompt,
            "negative_prompt": negativePrompt or "",
            "width": width,
            "height": height,
            "steps": steps,
            "cfg_scale": cfgScale,
            "n_iter": 1,
            "batch_size": 1,
            # 保存策略：保存单图、不保存网格
            "save_images": bool(save_images),
            "do_not_save_grid": True,
            "do_not_save_samples": not bool(save_images),
            # 响应返回图片
            "send_images": True,
        }
        if scheduler:
            payload["sampler_name"] = scheduler
        payload["seed"] = seed
        if styles:
            payload["styles"] = list(styles)
        # 映射 clipSkip 到 webui 的 CLIP_stop_at_last_layers
        if clipSkip is not None:
            payload["CLIP_stop_at_last_layers"] = clipSkip

        url = f"{app_settings.sd_forge.base_url}/sdapi/v1/txt2img"
        with httpx.Client(timeout=app_settings.sd_forge.generate_timeout) as client:
            resp = client.post(url, json=payload)
            resp.raise_for_status()
            return resp.json()

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
        # NOTE: sd-forge 本地模型不通过此处切换 model，保持当前加载模型
        # 参数名称映射至 create_text2image
        return self.create_text2image(
            prompt=prompt,
            negativePrompt=negative_prompt,
            loras=loras or {},
            styles=(),
            seed=seed,
            scheduler=sampler,
            steps=steps,
            cfgScale=cfg_scale,
            width=width,
            height=height,
            clipSkip=clip_skip,
            save_images=True,
        )


sd_forge_service = SdForgeService()
