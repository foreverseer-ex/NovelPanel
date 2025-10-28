"""
本地模型元数据组织者（local）。
从本地 SD-Forge 目录读取与缓存模型元数据，并在缺失时通过 Civitai 提供者拉取。
"""
import asyncio
from pathlib import Path
from typing import Literal

from PIL import Image  # noqa: F401  # 预留：后续可能用于图像处理
from loguru import logger

from schemas.model_meta import ModelMeta
from services.model_meta_provider.civitai import civitai_service
from utils.path import checkpoint_meta_home, lora_meta_home
from settings.app_setting import app_settings


class LocalModelMetaService:
    """
    模型元数据管理器（本地）。

    - 负责扫描本地 SD‑Forge 模型目录并维护内存列表（Checkpoint/LoRA/VAE）。
    - 若缺少本地元数据，则通过 Civitai 获取并缓存 `metadata.json` 与示例图。
    - 提供读取示例图片与批量下载示例图的能力。
    """

    def __init__(self):
        """初始化模型元数据管理器。"""
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
        """更新模型描述并保存。"""
        meta.desc = new_desc if new_desc else None
        LocalModelMetaService.save_meta(meta, meta.type)
        logger.info(f"已更新模型 {meta.name} 的描述")

    @staticmethod
    def get_example_image_path(meta: ModelMeta, index: int = 0) -> Path:
        """获取示例图片路径。"""
        home = None
        match meta.type:
            case 'Checkpoint':
                home = checkpoint_meta_home / Path(meta.filename).stem
            case 'LORA':
                home = lora_meta_home / Path(meta.filename).stem
        file = meta.examples[index].filename
        return home / file

    def flush(self):
        """刷新所有模型元数据。"""
        self.flush_checkpoint_meta()
        self.flush_lora_meta()
        self.flush_vae()

    def flush_lora_meta(self):
        """刷新Lora模型元数据。"""
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
        """异步下载模型示例图片。"""
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
        """刷新Stable-diffusion模型元数据。"""
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
        """刷新VAE模型元数据（预留）。"""
        return

    def sync_by_model_id(
        self,
        model_id: int,
        model_type: Literal['Checkpoint', 'LORA'],
        filename: str,
    ) -> ModelMeta | None:
        """通过 Civitai 模型 ID 拉取并缓存元数据与示例图。

        :param model_id: Civitai 模型 ID
        :param model_type: 模型类型（Checkpoint/LORA）
        :param filename: 本地 safetensors 文件名（用于确定缓存目录名）
        :return: 同步后的 ModelMeta，失败返回 None
        """
        detail = civitai_service.get_model_details(model_id)
        if not detail:
            logger.error(f"未获取到 Civitai 模型详情: {model_id}")
            return None

        # 兼容 Civitai /models/{id} 返回结构：model + modelVersions
        mv_list = detail.get("modelVersions") or []
        if not mv_list:
            logger.error(f"模型 {model_id} 未包含版本信息")
            return None
        mv = mv_list[0]

        # 构建 ModelMeta（尽最大努力从结构中提取）
        images = mv.get("images", [])
        trained_words = mv.get("trainedWords", [])
        files = mv.get("files", [])
        download_url = files[0].get("downloadUrl") if files else None
        base_model = mv.get("baseModel") or detail.get("type") or "sd1"

        # 生成 Example 列表（仅保留 URL，GenerateArg 填基本字段）
        from schemas.model_meta import Example, GenerateArg
        examples: list[Example] = []
        for img in images:
            meta = img.get("meta") or {}
            metadata = img.get("metadata") or {}
            examples.append(
                Example(
                    url=img.get("url"),
                    args=GenerateArg(
                        model=meta.get("Model") or detail.get("name", ""),
                        prompt=meta.get("prompt", ""),
                        negative_prompt=meta.get("negativePrompt", ""),
                        steps=int(meta.get("steps", 20) or 20),
                        cfg_scale=float(meta.get("cfgScale", 7.0) or 7.0),
                        sampler=str(meta.get("sampler", "Euler a") or "Euler a"),
                        seed=int(meta.get("seed", -1) or -1),
                        width=int(metadata.get("width", 512) or 512),
                        height=int(metadata.get("height", 512) or 512),
                        clip_skip=meta.get("clipSkip"),
                    ),
                )
            )

        model_meta = ModelMeta(
            filename=filename,
            name=detail.get("name", ""),
            version=mv.get("name", ""),
            desc=detail.get("description"),
            model_id=model_id,
            type=model_type,
            base_model=base_model,
            sha256=(files[0].get("hashes", {}).get("SHA256") if files else ""),
            trained_words=trained_words or [],
            download_url=download_url or "",
            examples=examples,
        )

        # 保存与下载示例图
        if model_type == 'Checkpoint':
            base_path = checkpoint_meta_home / Path(filename).stem
        else:
            base_path = lora_meta_home / Path(filename).stem
        asyncio.run(self.download_example_images(base_path, model_meta))
        self.save_meta(model_meta, model_type)
        logger.success(f"已通过模型ID同步元数据: {model_id} -> {filename}")
        return model_meta


local_model_meta_service = LocalModelMetaService()
# 兼容旧名称导出
ModelMetaService = LocalModelMetaService
model_meta_service = local_model_meta_service
