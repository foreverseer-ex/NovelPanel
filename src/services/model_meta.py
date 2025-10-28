"""
模型元数据管理器。
"""
import asyncio
from pathlib import Path
from typing import Literal

from PIL import Image
from loguru import logger

from schemas.model_meta import ModelMeta
from services.civitai import civitai_service
from utils.path import checkpoint_meta_home, lora_meta_home
from settings.app_setting import app_settings


class ModelMetaService:
    """
    模型元数据管理器。

    - 负责扫描本地 SD‑Forge 模型目录并维护内存列表（Checkpoint/LoRA/VAE）。
    - 若缺少本地元数据，则通过 Civitai 获取并缓存 `metadata.json` 与示例图。
    - 提供读取示例图片与批量下载示例图的能力。
    """

    def __init__(self):
        """初始化模型元数据管理器。
        
        初始化三个模型列表（LoRA、Checkpoint、VAE）并执行首次刷新。
        """
        self.lora_list: list[ModelMeta] = []
        self.sd_list: list[ModelMeta] = []
        self.vae_list: list[ModelMeta] = []
        self.flush()

    @staticmethod
    def load_meta(filename: str, model_type: Literal['Checkpoint', 'LORA']) -> ModelMeta | None:
        """
        读取Stable-diffusion模型元数据。

        :param model_type: 模型类型
        :param filename: 模型名称
        :return: 模型元数据
        """
        home = None
        match model_type:
            case 'Checkpoint':
                home = checkpoint_meta_home
            case 'LORA':
                home = lora_meta_home
        model_version_json = home / Path(filename).stem / 'metadata.json'
        if not model_version_json.exists():
            return None
        meta = ModelMeta.model_validate_json(model_version_json.read_text(encoding='utf-8'))
        return meta

    @staticmethod
    def save_meta(meta: ModelMeta, model_type: Literal['Checkpoint', 'LORA']):
        """
        保存Stable-diffusion模型元数据。
        :param meta: 模型元数据
        :param model_type: 模型类型
        """
        home = None
        match model_type:
            case 'Checkpoint':
                home = checkpoint_meta_home
            case 'LORA':
                home = lora_meta_home
        model_version_json = home / Path(meta.filename).stem / 'metadata.json'
        model_version_json.parent.mkdir(parents=True, exist_ok=True)
        model_version_json.write_text(meta.model_dump_json(indent=2), encoding='utf-8')

    @staticmethod
    def update_desc(meta: ModelMeta, new_desc: str) -> None:
        """
        更新模型描述并保存。
        
        :param meta: 模型元数据对象
        :param new_desc: 新的描述内容
        """
        # 更新描述
        meta.desc = new_desc if new_desc else None

        # 保存到文件
        ModelMetaService.save_meta(meta, meta.type)

        logger.info(f"已更新模型 {meta.name} 的描述")

    @staticmethod
    def get_example_image_path(meta: ModelMeta, index: int = 0) -> Path:
        """
        获取示例图片路径。

        :param meta: 模型元数据
        :param index: 示例图片索引
        :return: 示例图片路径
        """
        home = None
        match meta.type:
            case 'Checkpoint':
                home = checkpoint_meta_home / Path(meta.filename).stem
            case 'LORA':
                home = lora_meta_home / Path(meta.filename).stem
        # 忽略类型提示检查
        file = meta.examples[index].filename
        return home / file

    def flush(self):
        """
        刷新所有模型元数据。
        依次刷新 Checkpoint、LoRA、VAE 列表。
        """
        self.flush_checkpoint_meta()
        self.flush_lora_meta()
        self.flush_vae()

    def flush_lora_meta(self):
        """
        刷新Lora模型元数据。
        遍历 Lora 目录，若无本地缓存则从 Civitai 拉取并保存。
        """
        for file in app_settings.sd_forge.lora_home.glob('*.safetensors'):
            model_meta = self.load_meta(file.stem, 'LORA')
            if model_meta is None:
                logger.warning(f'未找到 {file.stem} 的模型元数据，尝试从 Civitai 获取')
                model_meta = civitai_service.get_model_meta_by_path(file)

                base_path = lora_meta_home / file.stem
                asyncio.run(self.download_example_images(base_path, model_meta))
                self.save_meta(model_meta, 'LORA')
            self.lora_list.append(model_meta)

    @staticmethod
    async def download_example_images(base_path: Path, model_meta: ModelMeta):
        """
        异步下载模型示例图片。

        :param base_path: 示例图片保存路径
        :param model_meta: 模型元数据
        """
        tasks = []

        for example in model_meta.examples:
            save_path = base_path / f'{example.filename}'
            save_path.parent.mkdir(parents=True, exist_ok=True)
            tasks.append(civitai_service.download_image(example.url, save_path))

        results = await asyncio.gather(*tasks)
        if all(results):
            logger.info(f'成功下载 {len(model_meta.examples)} 张示例图片')
        else:
            logger.warning(f'下载 {len(model_meta.examples)} 张示例图片，失败 {results.count(False)} 张')

    def flush_checkpoint_meta(self):
        """
        刷新Stable-diffusion模型元数据。
        遍历 Checkpoint 目录，若无本地缓存则从 Civitai 拉取并保存。
        """

        for file in app_settings.sd_forge.checkpoint_home.glob('*.safetensors'):
            model_meta = self.load_meta(file.stem, 'Checkpoint')
            if model_meta is None:
                logger.warning(f'未找到 {file.stem} 的模型元数据，尝试从 Civitai 获取')
                model_meta = civitai_service.get_model_meta_by_path(file)

                base_path = checkpoint_meta_home / file.stem
                asyncio.run(self.download_example_images(base_path, model_meta))
                self.save_meta(model_meta, 'Checkpoint')
            self.sd_list.append(model_meta)

    def flush_vae(self):
        """
        刷新VAE模型元数据。
        预留：可在此扩展从目录读取与元数据维护。
        """
        # 预留功能，暂未实现
        return


model_meta_service = ModelMetaService()
