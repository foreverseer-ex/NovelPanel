"""
SD-Forge 绘图服务实现。
"""
from __future__ import annotations

import base64
import io
from pathlib import Path
from typing import Optional, Dict, Any

import httpx
from PIL import Image
from loguru import logger

from settings import app_settings
from schemas.draw import DrawArgs
from .base import AbstractDrawService


class SdForgeDrawService(AbstractDrawService):
    """
    SD-Forge（Stable Diffusion WebUI）绘图服务。
    
    - base_url：sd-forge/sd-webui 服务地址，默认 http://127.0.0.1:7860
    - 功能：获取模型列表、读取/设置 options、调用 txt2img 生成。
    """

    def __init__(self):
        """初始化服务。"""
        self._jobs: dict[str, dict[str, Any]] = {}  # 存储任务信息 {job_id: result}

    @staticmethod
    def _get_loras() -> Dict[str, Any]:
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
    def _get_sd_models() -> Dict[str, Any]:
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
    def _get_options() -> Dict[str, Any]:
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
    def _set_options(
        sd_model_checkpoint: str | None = None,
        sd_vae: str | None = None,
    ) -> None:
        """
        切换 SD 模型（/sdapi/v1/options）。
        
        :param sd_model_checkpoint: 模型检查点，来自 /sdapi/v1/sd-models 的 title 字段
        :param sd_vae: VAE 模型，来自 /sdapi/v1/options 的 sd_vae 字段
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

    def _create_text2image(
        self,
        prompt: str,
        negative_prompt: str = "",
        loras: Optional[Dict[str, float]] = None,
        styles: list[str] = (),
        seed: int = -1,
        sampler: str = 'DPM++ 2M Karras',
        steps: int = 30,
        cfg_scale: float = 7.0,
        width: int = 1024,
        height: int = 1024,
        clip_skip: int | None = None,
        save_images: bool = True,
    ) -> Dict[str, Any]:
        """
        文生图（/sdapi/v1/txt2img）。
        
        :return: 包含 images、parameters 等字段的响应
        """
        # 处理 LoRA
        final_prompt = prompt
        if loras:
            tags = []
            for name, weight in loras.items():
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
            "n_iter": 1,
            "batch_size": 1,
            # 保存策略：保存单图、不保存网格
            "save_images": bool(save_images),
            "do_not_save_grid": True,
            "do_not_save_samples": not bool(save_images),
            # 响应返回图片
            "send_images": True,
        }
        
        if sampler:
            payload["sampler_name"] = sampler
        payload["seed"] = seed
        if styles:
            payload["styles"] = list(styles)
        # 映射 clip_skip 到 webui 的 CLIP_stop_at_last_layers
        if clip_skip is not None:
            payload["CLIP_stop_at_last_layers"] = clip_skip

        url = f"{app_settings.sd_forge.base_url}/sdapi/v1/txt2img"
        with httpx.Client(timeout=app_settings.sd_forge.generate_timeout) as client:
            resp = client.post(url, json=payload)
            resp.raise_for_status()
            return resp.json()

    # ========== 实现抽象接口 ==========

    def draw(self, args: DrawArgs) -> str:
        """
        执行单次绘图。
        
        :param args: 绘图参数
        :return: job_id
        """
        import uuid
        job_id = str(uuid.uuid4())
        
        try:
            # 如果指定了 VAE，先设置 VAE
            if args.vae:
                logger.debug(f"设置 VAE: {args.vae}")
                self._set_options(sd_vae=args.vae)
            
            # 调用 SD-Forge API
            result = self._create_text2image(
                prompt=args.prompt,
                negative_prompt=args.negative_prompt,
                loras=args.loras or {},
                seed=args.seed,
                sampler=args.sampler,
                steps=args.steps,
                cfg_scale=args.cfg_scale,
                width=args.width,
                height=args.height,
                clip_skip=args.clip_skip,
                save_images=True,
            )
            
            # 存储结果
            self._jobs[job_id] = {
                "completed": True,
                "result": result,
            }
            
            logger.success(f"SD-Forge 绘图完成: job_id={job_id}")
            return job_id
            
        except Exception as e:
            logger.exception(f"SD-Forge 绘图失败: {e}")
            self._jobs[job_id] = {
                "completed": False,
                "error": str(e),
            }
            raise

    def draw_batch(self, args_list: list[DrawArgs]) -> str:
        """
        批量绘图（暂未实现）。
        
        :param args_list: 绘图参数列表
        :return: batch_id
        """
        raise NotImplementedError("SD-Forge 批量绘图功能暂未实现")

    def get_batch_status(self, batch_id: str) -> dict[str, bool]:
        """
        获取批次状态（暂未实现）。
        
        :param batch_id: 批次 ID
        :return: 字典 {job_id: 是否完成}
        """
        raise NotImplementedError("SD-Forge 批量绘图功能暂未实现")

    def get_job_status(self, job_id: str) -> bool:
        """
        获取任务状态。
        
        :param job_id: 任务 ID
        :return: 是否完成
        """
        job = self._jobs.get(job_id)
        if not job:
            raise ValueError(f"任务不存在: {job_id}")
        return job.get("completed", False)

    def get_image(self, job_id: str) -> Image.Image:
        """
        获取生成的图片。
        
        :param job_id: 任务 ID
        :return: PIL Image 对象
        """
        job = self._jobs.get(job_id)
        if not job:
            raise ValueError(f"任务不存在: {job_id}")
        
        if not job.get("completed"):
            raise RuntimeError(f"任务未完成: {job_id}")
        
        result = job.get("result", {})
        images = result.get("images", [])
        
        if not images:
            raise RuntimeError(f"任务无图片结果: {job_id}")
        
        # SD-Forge 返回的是 base64 编码的图片
        img_base64 = images[0]
        img_bytes = base64.b64decode(img_base64)
        img = Image.open(io.BytesIO(img_bytes))
        
        return img

    def save_image(self, job_id: str, save_path: str | Path) -> None:
        """
        保存生成的图片到文件。
        
        :param job_id: 任务 ID
        :param save_path: 保存路径
        """
        img = self.get_image(job_id)
        save_path = Path(save_path)
        save_path.parent.mkdir(parents=True, exist_ok=True)
        img.save(save_path)
        logger.info(f"图片已保存: {save_path}")


# 全局单例
sd_forge_draw_service = SdForgeDrawService()
