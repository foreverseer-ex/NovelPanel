"""
Civitai 绘图服务实现。
"""
from __future__ import annotations

import os
import io
from pathlib import Path
from typing import Dict, Any, Optional

import httpx
from PIL import Image
from loguru import logger

from settings import app_settings
from schemas.draw import DrawArgs
from .base import AbstractDrawService

# 在导入 civitai 之前设置环境变量
if app_settings.civitai.api_token:
    os.environ["CIVITAI_API_TOKEN"] = app_settings.civitai.api_token

import civitai


class CivitaiDrawService(AbstractDrawService):
    """
    Civitai 绘图服务。
    
    注意：对于 Civitai，job_id 实际上是 token。
    """

    def __init__(self):
        """初始化 Civitai 绘图服务，确保 API Token 已设置。"""
        # 确保环境变量已设置（如果 token 在初始化后被更新）
        if app_settings.civitai.api_token:
            os.environ["CIVITAI_API_TOKEN"] = app_settings.civitai.api_token

    def _create_text2image(
            self,
            *,
            model: str,
            prompt: str,
            negative_prompt: str = "",
            scheduler: str = "EulerA",
            steps: int = 25,
            cfg_scale: float = 7.0,
            width: int = 512,
            height: int = 768,
            seed: int = -1,
            clip_skip: int = 2,
            loras: Optional[Dict[str, float]] = None,
            vae: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        创建 Civitai 文生图任务，返回 { token }。
        
        :param model: 模型名称，如 "SDXL"
        :param prompt: 提示词
        :param negative_prompt: 负提示词
        :param scheduler: 调度器，如 "EulerA"
        :param steps: 推理步数
        :param cfg_scale: CFG 缩放因子
        :param width: 图像宽度
        :param height: 图像高度
        :param seed: 随机种子（-1 表示随机）
        :param clip_skip: CLIP 层跳过数
        :param loras: LoRA 字典，{ urn: 强度 }
        :param vae: VAE AIR 标识符
        :return: 包含 token 的字典
        """
        option: Dict[str, Any] = {
            "model": model,
            "params": {
                "prompt": prompt,
                "negativePrompt": negative_prompt,
                "scheduler": scheduler,
                "steps": steps,
                "cfgScale": cfg_scale,
                "width": width,
                "height": height,
                "seed": seed,
                "clipSkip": clip_skip,
            },
        }

        # 处理 additionalNetworks（LoRA 和 VAE）
        additional: Dict[str, Any] = {}
        
        # 添加 LoRA
        if loras:
            for air, strength in loras.items():
                additional[air] = {"type": "Lora", "strength": float(strength)}
        
        # 添加 VAE
        if vae:
            additional[vae] = {"type": "VAE", "strength": 1.0}
        
        if additional:
            option["additionalNetworks"] = additional

        logger.debug(f"civitai.image.create option={option}")
        resp = civitai.image.create(option)
        # 返回示例：{'token': '...'}
        return resp

    def _get_job(self, token: str) -> Dict[str, Any]:
        """
        查询任务状态。
        
        :param token: 任务 token
        :return: Civitai 的完整响应
        """
        try:
            resp = civitai.jobs.get(token=token)
            return resp
        except httpx.ReadTimeout as e:
            logger.warning(f"civitai.jobs.get 超时: {e}")
            raise

    # ========== 实现抽象接口 ==========

    def draw(self, args: DrawArgs) -> str:
        """
        执行单次绘图。
        
        :param args: 绘图参数
        :return: job_id（对于 Civitai 来说就是 token）
        """
        from services.model_meta import local_model_meta_service
        
        # 获取模型的 AIR 标识符
        model_meta = local_model_meta_service.get_by_name(args.model)
        if not model_meta:
            raise RuntimeError(f"未找到模型: {args.model}")
        
        model_air = model_meta.air
        logger.debug(f"模型 AIR: {model_air}")
        
        # 转换 LoRAs 名称为 AIR
        lora_airs: Dict[str, float] = {}
        if args.loras:
            for lora_name, strength in args.loras.items():
                lora_meta = local_model_meta_service.get_by_name(lora_name)
                if not lora_meta:
                    logger.warning(f"未找到 LoRA 元数据: {lora_name}，跳过")
                    continue
                lora_airs[lora_meta.air] = strength
                logger.debug(f"LoRA AIR: {lora_meta.air}")
        
        # 转换 VAE 名称为 AIR
        vae_air: Optional[str] = None
        if args.vae:
            vae_meta = local_model_meta_service.get_by_name(args.vae)
            if not vae_meta:
                logger.warning(f"未找到 VAE 元数据: {args.vae}，跳过")
            else:
                vae_air = vae_meta.air
                logger.debug(f"VAE AIR: {vae_air}")
        
        result = self._create_text2image(
            model=model_air,  # 使用 AIR 标识符而不是名称
            prompt=args.prompt,
            negative_prompt=args.negative_prompt,
            scheduler=args.sampler,  # sampler 映射到 scheduler
            steps=args.steps,
            cfg_scale=args.cfg_scale,
            width=args.width,
            height=args.height,
            seed=args.seed,
            clip_skip=args.clip_skip or 2,
            loras=lora_airs,  # 使用 AIR 字典
            vae=vae_air,  # 使用 VAE AIR
        )

        token = result.get("token")
        if not token:
            raise RuntimeError("Civitai 未返回 token")

        logger.success(f"Civitai 任务已创建: token={token}")
        return token  # 对于 Civitai，job_id 就是 token

    def draw_batch(self, args_list: list[DrawArgs]) -> str:
        """
        批量绘图（暂未实现）。
        
        :param args_list: 绘图参数列表
        :return: batch_id
        """
        raise NotImplementedError("Civitai 批量绘图功能暂未实现")

    def get_batch_status(self, batch_id: str) -> dict[str, bool]:
        """
        获取批次状态（暂未实现）。
        
        :param batch_id: 批次 ID
        :return: 字典 {job_id: 是否完成}
        """
        raise NotImplementedError("Civitai 批量绘图功能暂未实现")

    def get_job_status(self, job_id: str) -> bool:
        """
        获取任务状态。
        
        :param job_id: 任务 ID（对于 Civitai 来说是 token）
        :return: 是否完成
        """
        try:
            resp = self._get_job(job_id)
            jobs = resp.get("jobs", [])

            if not jobs:
                return False

            # 检查第一个 job 的状态
            job = jobs[0]
            result = job.get("result")

            if not result:
                return False

            # 检查是否有可用的结果
            available = result.get("available", False)
            return available

        except Exception as e:
            logger.exception(f"查询 Civitai 任务状态失败: {e}")
            return False

    def get_image(self, job_id: str) -> Image.Image:
        """
        获取生成的图片。
        
        :param job_id: 任务 ID（对于 Civitai 来说是 token）
        :return: PIL Image 对象
        """
        resp = self._get_job(job_id)
        jobs = resp.get("jobs", [])

        if not jobs:
            raise RuntimeError(f"任务无结果: {job_id}")

        job = jobs[0]
        result = job.get("result")

        if not result:
            raise RuntimeError(f"任务无结果: {job_id}")

        if not result.get("available"):
            raise RuntimeError(f"任务未完成: {job_id}")

        # 获取图片 URL
        blob_url = result.get("blobUrl")
        if not blob_url:
            raise RuntimeError(f"任务无图片 URL: {job_id}")

        # 下载图片
        with httpx.Client(timeout=app_settings.civitai.timeout) as client:
            resp = client.get(blob_url)
            resp.raise_for_status()
            img = Image.open(io.BytesIO(resp.content))

        return img

    def save_image(self, job_id: str, save_path: str | Path) -> None:
        """
        保存生成的图片到文件。
        
        :param job_id: 任务 ID（对于 Civitai 来说是 token）
        :param save_path: 保存路径
        """
        img = self.get_image(job_id)
        save_path = Path(save_path)
        save_path.parent.mkdir(parents=True, exist_ok=True)
        img.save(save_path)
        logger.info(f"图片已保存: {save_path}")


# 全局单例
civitai_draw_service = CivitaiDrawService()
