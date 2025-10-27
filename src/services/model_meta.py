"""
模型元数据管理器。
"""
import asyncio
from pathlib import Path
from typing import Literal

from PIL import Image
from loguru import logger

from schemas.model import ModelMeta
from services.civitai import civitai_service
from settings.path import checkpoint_meta_home, lora_meta_home
from settings.sd_forge_setting import sd_forge_settings


class ModelMetaService:
    """
    模型元数据管理器。

    - 负责扫描本地 SD‑Forge 模型目录并维护内存列表（Checkpoint/LoRA/VAE）。
    - 若缺少本地元数据，则通过 Civitai 获取并缓存 `metadata.json` 与示例图。
    - 提供读取示例图片与批量下载示例图的能力。
    """

    def __init__(self):
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
    def load_example_image(meta: ModelMeta, index: int = 0) -> Image.Image | None:
        """
        读取示例图片。

        :param meta: 模型元数据
        :param index: 示例图片索引
        :return: 示例图片对象
        """
        home = None
        match meta.type:
            case 'Checkpoint':
                home = checkpoint_meta_home / Path(meta.filename).stem
            case 'LORA':
                home = lora_meta_home / Path(meta.filename).stem
        # noinspection PyTypeHints
        file = meta.examples[index].filename
        return Image.open(home / file)

    @staticmethod
    def load_example_images(meta: ModelMeta) -> list[Image.Image]:
        """
        读取示例图片。

        :param meta: 模型元数据
        :return: 示例图片对象列表
        """
        home = checkpoint_meta_home / Path(meta.filename).stem
        return [Image.open(home / example.filename) for example in meta.examples]

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
        for file in sd_forge_settings.lora_home.glob('*.safetensors'):
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

        for file in sd_forge_settings.checkpoint_home.glob('*.safetensors'):
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
