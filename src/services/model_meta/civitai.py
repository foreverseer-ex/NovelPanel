"""
Civitai 模型元数据服务。

从 Civitai API 获取模型元数据。
"""
from pathlib import Path
from typing import Optional

import httpx
from loguru import logger

from schemas.model_meta import Example, DrawArgs, ModelMeta
from services.model_meta.local import local_model_meta_service
from services.model_meta.base import AbstractModelMetaService
from settings import app_settings
from constants.civitai import CIVITAI_BASE_URL
from utils.hash import sha256
from utils.civitai import parse_air, normalize_type

class CivitaiModelMetaService(AbstractModelMetaService):
    """
    Civitai 模型元数据服务。
    
    通过 Civitai API 获取远程模型元数据。
    """

    def test(self) -> bool:
        """
        测试 Civitai API 连接是否正常。

        :return: 是否连接成功
        """
        try:
            url = f"{CIVITAI_BASE_URL}/api/v1/models"
            with httpx.Client(timeout=app_settings.civitai.timeout) as client:
                resp = client.get(url)
                return resp.status_code == 200
        except Exception as e:
            logger.exception(f"测试 Civitai 连接失败: {e}")
            return False
    
    def _parse_version_data(self, version_data: dict) -> ModelMeta:
        """
        解析 Civitai API 返回的版本数据为 ModelMeta。
        
        :param version_data: Civitai API 返回的版本数据（from /api/v1/model-versions/*）
        :return: 模型元数据
        """

        
        # 获取模型基本信息（从 model 字段）
        model_info = version_data.get("model", {})

        
        # 通过 AIR 标识符来规范化字段
        # AIR 包含 ecosystem（技术代际）信息，而不是 base_model

        air = parse_air(version_data['air'])
        
        # 使用 AIR 解析出的规范化字段
        model_id = air.model_id
        version_id = air.version_id
        type_normalized = normalize_type(air.type)  # 规范化类型（LyCORIS -> lora）
        ecosystem_normalized = air.ecosystem
        
        # 从 version_data 中提取真正的 base_model（如 Pony, Illustrious）
        # Civitai API 的 baseModel 字段可能是 "Pony", "Illustrious" 等
        # 直接使用原始值（保持大小写）
        raw_base_model = version_data.get("baseModel")
        base_model_normalized = raw_base_model.strip() if raw_base_model else None
        
        # 解析示例图片
        examples: list[Example] = []
        for image_detail in version_data.get("images", []):
            meta = image_detail.get("meta", {})
            metadata = image_detail.get("metadata", {})
            
            examples.append(
                Example(
                    url=image_detail.get("url", ""),
                    args=DrawArgs(
                        width=metadata.get("width", 512),
                        height=metadata.get("height", 512),
                        seed=meta.get("seed", -1),
                        model=meta.get("Model", ""),
                        steps=meta.get("steps", 20),
                        prompt=meta.get("prompt", ""),
                        sampler=meta.get("sampler", "Euler a"),
                        cfg_scale=meta.get("cfgScale", 7.0),
                        negative_prompt=meta.get("negativePrompt", ""),
                        clip_skip=meta.get("clipSkip"),
                    ),
                )
            )
        
        # 获取文件信息
        files = version_data.get("files", [])
        file_name = files[0]["name"]
        # 构造 ModelMeta（使用解析后的规范化字段）
        model_meta = ModelMeta(
            filename=file_name,
            name=model_info.get("name", version_data.get("name", "")),
            version=version_data.get("name", ""),
            desc=model_info.get("description", version_data.get("description")),
            model_id=model_id,
            version_id=version_id,
            type=type_normalized,
            ecosystem=ecosystem_normalized,  # 从 AIR 解析的 ecosystem
            base_model=base_model_normalized,  # 从 version_data 解析的 base_model
            sha256=files[0].get("hashes", {}).get("SHA256", "") if files else "",
            trained_words=version_data.get("trainedWords", []),
            url=files[0].get("downloadUrl", "") if files else "",
            examples=examples,
        )
        
        return model_meta
    
    # ==================== 实现基类接口 ====================
    
    def get_by_name(self, name: str) -> Optional[ModelMeta]:
        """
        通过模型名称获取模型元数据。
        
        注意：Civitai API 不支持直接通过名称搜索单个模型。
        此方法返回 None。
        
        :param name: 模型名称
        :return: None（不支持）
        """
        logger.warning(f"Civitai 不支持通过名称直接获取模型: {name}")
        logger.info("建议使用 get_by_hash, get_by_path 或 get_by_id")
        return None
    
    def get_by_path(self, path: Path) -> Optional[ModelMeta]:
        """
        通过模型文件路径获取模型元数据。
        
        计算文件的 SHA-256 哈希值，然后从 Civitai API 获取元数据。
        
        :param path: 模型文件路径
        :return: 模型元数据，未找到返回 None
        """
        if not path.exists() or path.suffix.lower() != ".safetensors":
            logger.warning(f"无效的模型文件: {path}")
            return None
        
        # 计算文件哈希
        try:
            file_hash = sha256(path)
            logger.debug(f"计算文件哈希: {path.name} -> {file_hash}")
        except Exception as e:
            logger.exception(f"计算文件哈希失败: {e}")
            return None
        
        # 通过哈希获取元数据
        return self.get_by_hash(file_hash)
    
    def get_by_hash(self, file_hash: str) -> Optional[ModelMeta]:
        """
        通过模型文件哈希值获取模型元数据。
        
        :param file_hash: SHA-256 哈希值
        :return: 模型元数据，未找到返回 None
        """
        url = f"{CIVITAI_BASE_URL}/api/v1/model-versions/by-hash/{file_hash}"
        
        try:
            with httpx.Client(timeout=app_settings.civitai.timeout) as client:
                resp = client.get(url)
                if resp.status_code != 200:
                    logger.warning(f"未找到哈希为 {file_hash} 的模型 (status: {resp.status_code})")
                    return None
                
                version_data = resp.json()
            
            # 解析版本数据
            model_meta = self._parse_version_data(version_data)
            
            logger.success(f"从 Civitai 获取模型元数据成功: {model_meta.name}")
            return model_meta
            
        except (KeyError, IndexError, TypeError) as e:
            logger.exception(f"解析 Civitai API 响应失败: {e}")
            return None
        except Exception as e:
            logger.exception(f"从 Civitai 获取模型元数据失败: {e}")
            return None
    
    def get_by_id(self, version_id: int) -> Optional[ModelMeta]:
        """
        通过 Civitai 模型版本 ID 获取模型元数据。
        
        注意：此方法使用 version_id 而不是 model_id，因为在 Civitai 中，
        每个版本（version）才是实际可下载和使用的模型单元。
        
        :param version_id: Civitai 模型版本 ID
        :return: 模型元数据，未找到返回 None
        """
        url = f"{CIVITAI_BASE_URL}/api/v1/model-versions/{version_id}"
        
        try:
            with httpx.Client(timeout=app_settings.civitai.timeout) as client:
                resp = client.get(url)
                if resp.status_code != 200:
                    logger.warning(f"未找到版本 ID 为 {version_id} 的模型 (status: {resp.status_code})")
                    return None
                
                version_data = resp.json()
            
            # 解析版本数据
            model_meta = self._parse_version_data(version_data)
            
            logger.success(f"从 Civitai 获取模型元数据成功: {model_meta.name} (Version ID: {version_id})")
            return model_meta
            
        except (KeyError, IndexError, TypeError) as e:
            logger.error(f"解析 Civitai API 响应失败: {e}")
            return None
        except Exception as e:
            logger.exception(f"从 Civitai 获取模型元数据失败: {e}")
            return None
    
    async def save(self, model_meta: ModelMeta) -> ModelMeta:
        """
        保存模型元数据（委托给本地服务）。
        
        Civitai 服务不直接保存元数据，而是委托给 LocalModelMetaService。
        这样保持了职责分离：
        - Civitai 负责从远程获取数据
        - Local 负责本地存储管理
        
        :param model_meta: 模型元数据（必须包含 type 字段）
        :return: 保存后的模型元数据
        """
        # 延迟导入，避免循环依赖

        
        logger.debug(f"Civitai 服务委托本地服务保存: {model_meta.name}")
        return await local_model_meta_service.save(model_meta)
    
    async def sync_from_sd_forge(self):
        """
        从 SD-Forge 目录同步模型元数据。
        
        扫描 SD-Forge 的 checkpoint_home 和 lora_home 目录中的 .safetensors 文件，
        计算哈希值后从 Civitai 获取元数据并保存到本地。
        
        :return: 同步结果统计 {"success": int, "failed": int, "skipped": int}
        """
        logger.info("开始从 SD-Forge 同步模型元数据...")
        
        stats = {"success": 0, "failed": 0, "skipped": 0}
        
        # 同步 Checkpoint 模型
        logger.info(f"扫描 Checkpoint 目录: {app_settings.sd_forge.checkpoint_home}")
        if app_settings.sd_forge.checkpoint_home.exists():
            for safetensor_file in app_settings.sd_forge.checkpoint_home.glob("*.safetensors"):
                await self._sync_single_model(safetensor_file, stats)
        
        # 同步 LoRA 模型
        logger.info(f"扫描 LoRA 目录: {app_settings.sd_forge.lora_home}")
        if app_settings.sd_forge.lora_home.exists():
            for safetensor_file in app_settings.sd_forge.lora_home.glob("*.safetensors"):
                await self._sync_single_model(safetensor_file, stats)
        
        logger.success(
            f"同步完成 - 成功: {stats['success']}, 失败: {stats['failed']}, 跳过: {stats['skipped']}"
        )
        return stats
    
    async def _sync_single_model(self, safetensor_file: Path, stats: dict):
        """
        同步单个模型文件（内部方法）。
        
        :param safetensor_file: safetensors 文件路径
        :param stats: 统计信息字典
        """
        try:
            logger.info(f"处理模型: {safetensor_file.name}")
            
            # 检查本地是否已有元数据
            existing_meta = local_model_meta_service.get_by_name(safetensor_file.stem)
            if existing_meta is not None:
                logger.debug(f"跳过（已有元数据）: {safetensor_file.name}")
                stats["skipped"] += 1
                return
            
            # 计算文件哈希
            logger.debug(f"计算哈希: {safetensor_file.name}")
            file_hash = sha256(safetensor_file)
            
            # 从 Civitai 获取元数据
            logger.debug(f"从 Civitai 获取元数据: {file_hash}")
            model_meta = self.get_by_hash(file_hash)
            
            if model_meta is None:
                logger.warning(f"未找到元数据: {safetensor_file.name}")
                stats["failed"] += 1
                return
            
            # 保存到本地
            logger.debug(f"保存元数据: {model_meta.name}")
            await self.save(model_meta)
            
            stats["success"] += 1
            logger.success(f"同步成功: {safetensor_file.name} -> {model_meta.name}")
            
        except Exception as e:
            logger.exception(f"同步失败 ({safetensor_file.name}): {e}")
            stats["failed"] += 1


civitai_model_meta_service = CivitaiModelMetaService()
