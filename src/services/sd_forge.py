"""
sd-forge 服务
"""
import httpx
from typing import Optional, Dict, Any

from settings.sd_forge_setting import sd_forge_settings


class SdForgeService:
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
        url = f"{sd_forge_settings.base_url}/sdapi/v1/loras"
        with httpx.Client(timeout=sd_forge_settings.timeout) as client:
            resp = client.get(url)
            resp.raise_for_status()
            return resp.json()

    @staticmethod
    def get_sd_models() -> Dict[str, Any]:
        """
        获取 SD 模型列表（/sdapi/v1/sd-models）。

        :return: SD 模型列表
        """
        url = f"{sd_forge_settings.base_url}/sdapi/v1/sd-models"
        with httpx.Client(timeout=sd_forge_settings.timeout) as client:
            resp = client.get(url)
            resp.raise_for_status()
            return resp.json()

    @staticmethod
    def get_options() -> Dict[str, Any]:
        """
        获取 SD 模型选项（/sdapi/v1/options）。

        :return: SD 模型选项
        """
        url = f"{sd_forge_settings.base_url}/sdapi/v1/options"
        with httpx.Client(timeout=sd_forge_settings.timeout) as client:
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
        url = f"{sd_forge_settings.base_url}/sdapi/v1/options"
        payload = dict()
        if sd_model_checkpoint:
            payload["sd_model_checkpoint"] = sd_model_checkpoint
        if sd_vae:
            payload["sd_vae"] = sd_vae
        with httpx.Client(timeout=sd_forge_settings.timeout) as client:
            resp = client.post(url, json=payload)
            resp.raise_for_status()

    @classmethod
    def create_text2image(
            cls,
            prompt: str,
            negative_prompt: str = "",
            loras: Optional[Dict[str, float]] = None,
            styles: list[str] = (),
            seed: int = -1,
            sampler_name: str = 'DPM++ 2M Karras',
            batch_size: int = 1,
            n_iter: int = 1,
            steps: int = 30,
            cfg_scale: float = 7.0,
            width: int = 1024,
            height: int = 1024,
            save_images: bool = True,
    ) -> Dict[str, Any]:
        """
        文生图（/sdapi/v1/txt2img）。

        参数：
        - prompt：正向提示词，可包含 LoRA 标签，如 <lora:name:0.8>
        - negative_prompt：反向提示词
        - loras：{lora_name: weight}，会自动拼接为标签前缀
        - styles：样式预设列表（UI 中保存的样式名）
        - seed：随机种子（-1 表示随机）
        - sampler_name：采样器名称（如 'DPM++ 2M Karras'）
        - batch_size, n_iter：批量与重复次数
        - steps, cfg_scale：步数与 CFG
        - width, height：分辨率
        - save_images：是否在服务端保存单图（网格默认不保存）
        - model_title：可选，一次性切换模型后再生成
        - timeout：请求超时

        返回：sd-webui 原始响应（含 base64 images 列表、info、parameters）
        """

        final_prompt = prompt
        if loras:
            tags = []
            for name, weight in loras.items():
                # Use sd-webui lora tag syntax
                tags.append(f"<lora:{name}:{weight}>")
            if tags:
                final_prompt = " ".join(tags) + " " + (prompt or "")

        payload: Dict[str, Any] = {
            "prompt": final_prompt,
            "negative_prompt": negative_prompt or "",
            "width": width,
            "height": height,
            "steps": steps,
            "cfg_scale": cfg_scale,
            "n_iter": n_iter,
            "batch_size": batch_size,
            # 保存策略：保存单图、不保存网格
            "save_images": bool(save_images),
            "do_not_save_grid": True,
            "do_not_save_samples": not bool(save_images),
            # 响应返回图片
            "send_images": True,
        }
        if sampler_name:
            payload["sampler_name"] = sampler_name
        # 种子：-1 表示随机，按 webui 习惯直接传递该值
        payload["seed"] = seed
        # styles：为空也可传，或仅在非空时传递
        if styles:
            payload["styles"] = list(styles)

        url = f"{sd_forge_settings.base_url}/sdapi/v1/txt2img"
        with httpx.Client(timeout=sd_forge_settings.generate_timeout) as client:
            resp = client.post(url, json=payload)
            resp.raise_for_status()
            return resp.json()


sd_forge_service = SdForgeService()
