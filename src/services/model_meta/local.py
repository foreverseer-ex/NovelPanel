"""
本地模型元数据组织者（local）。
从本地 SD-Forge 目录读取与缓存模型元数据。
"""
import asyncio
import shutil
from pathlib import Path
from typing import Optional

from loguru import logger

from schemas.model_meta import ModelMeta, Example
from services.model_meta.base import AbstractModelMetaService
from utils.path import checkpoint_meta_home, lora_meta_home
from utils.download import is_local_url, download_file
from settings import app_settings
from constants.model_meta import ModelType


class LocalModelModelMetaService(AbstractModelMetaService):
    """
    模型元数据管理器（本地）。

    - 负责扫描本地 SD‑Forge 模型目录并维护内存列表（Checkpoint/LoRA/VAE）。
    - 提供将远程模型元数据本地化的能力（下载示例图，转换URL）。
    - 序列化和读取本地元数据文件。
    """

    def __init__(self):
        """初始化模型元数据管理器。"""
        self.lora_list: list[ModelMeta] = []
        self.sd_list: list[ModelMeta] = []
        self.vae_list: list[ModelMeta] = []
        self.flush()

    def flush(self):
        """
        刷新所有模型元数据。
        
        从磁盘重新扫描并刷新内存缓存。
        适用于外部添加了新模型文件或元数据后，需要刷新服务状态的场景。
        """
        # 清空现有缓存
        self.lora_list.clear()
        self.sd_list.clear()
        self.vae_list.clear()
        
        # 重新加载
        self._flush_checkpoint_meta()
        self._flush_lora_meta()
        self._flush_vae()
    
    def clear_all(self) -> int:
        """
        清空所有模型元数据。
        
        删除本地存储的所有 Checkpoint 和 LoRA 元数据文件。
        
        :return: 删除的元数据数量
        """
        import shutil
        
        deleted_count = 0
        
        # 删除 Checkpoint 元数据
        if checkpoint_meta_home.exists():
            for meta_dir in checkpoint_meta_home.iterdir():
                if meta_dir.is_dir():
                    try:
                        shutil.rmtree(meta_dir)
                        deleted_count += 1
                        logger.debug(f"已删除 Checkpoint 元数据: {meta_dir.name}")
                    except Exception as e:
                        logger.exception(f"删除 Checkpoint 元数据失败 ({meta_dir}): {e}")
        
        # 删除 LoRA 元数据
        if lora_meta_home.exists():
            for meta_dir in lora_meta_home.iterdir():
                if meta_dir.is_dir():
                    try:
                        shutil.rmtree(meta_dir)
                        deleted_count += 1
                        logger.debug(f"已删除 LoRA 元数据: {meta_dir.name}")
                    except Exception as e:
                        logger.exception(f"删除 LoRA 元数据失败 ({meta_dir}): {e}")
        
        # 清空内存缓存
        self.lora_list.clear()
        self.sd_list.clear()
        self.vae_list.clear()
        
        logger.success(f"已清空所有模型元数据，共删除 {deleted_count} 个")
        return deleted_count

    def _flush_lora_meta(self):
        """
        刷新 LoRA 模型元数据（内部方法）。
        
        从 lora_meta_home 目录读取所有元数据文件，而不是从 safetensors 文件扫描。
        """
        if not lora_meta_home.exists():
            logger.debug(f"LoRA 元数据目录不存在: {lora_meta_home}")
            return
        
        # 遍历元数据目录中的所有子目录
        for meta_dir in lora_meta_home.iterdir():
            if not meta_dir.is_dir():
                continue
            
            metadata_file = meta_dir / "metadata.json"
            if not metadata_file.exists():
                logger.warning(f"元数据文件不存在: {metadata_file}")
                continue
            
            try:
                model_meta = ModelMeta.model_validate_json(
                    metadata_file.read_text(encoding='utf-8')
                )
                self.lora_list.append(model_meta)
                logger.debug(f"加载 LoRA 元数据: {model_meta.name}")
            except Exception as e:
                logger.exception(f"加载 LoRA 元数据失败 ({metadata_file}): {e}")
                continue

    def _flush_checkpoint_meta(self):
        """
        刷新 Checkpoint 模型元数据（内部方法）。
        
        从 checkpoint_meta_home 目录读取所有元数据文件，而不是从 safetensors 文件扫描。
        """
        if not checkpoint_meta_home.exists():
            logger.debug(f"Checkpoint 元数据目录不存在: {checkpoint_meta_home}")
            return
        
        # 遍历元数据目录中的所有子目录
        for meta_dir in checkpoint_meta_home.iterdir():
            if not meta_dir.is_dir():
                continue
            
            metadata_file = meta_dir / "metadata.json"
            if not metadata_file.exists():
                logger.warning(f"元数据文件不存在: {metadata_file}")
                continue
            
            try:
                model_meta = ModelMeta.model_validate_json(
                    metadata_file.read_text(encoding='utf-8')
                )
                self.sd_list.append(model_meta)
                logger.debug(f"加载 Checkpoint 元数据: {model_meta.name}")
            except Exception as e:
                logger.exception(f"加载 Checkpoint 元数据失败 ({metadata_file}): {e}")
                continue

    def _flush_vae(self):
        """刷新VAE模型元数据（预留，内部方法）。"""
        return

    def test(self) -> bool:
        """
        测试本地服务是否可用。
        
        本地服务始终可用。
        
        :return: True
        """
        return True
    
    @staticmethod
    def _save_meta_to_disk(meta: ModelMeta):
        """
        将模型元数据序列化到磁盘（内部方法）。
        
        :param meta: 模型元数据（必须包含 type 字段）
        """
        home = checkpoint_meta_home if meta.type == ModelType.CHECKPOINT else lora_meta_home
        meta_file = home / Path(meta.filename).stem / 'metadata.json'
        meta_file.parent.mkdir(parents=True, exist_ok=True)
        meta_file.write_text(meta.model_dump_json(indent=2), encoding='utf-8')
    
    async def save(self, model_meta: ModelMeta) -> ModelMeta:
        """
        将模型元数据本地化并保存。
        
        此方法会：
        1. 下载所有远程示例图片到本地
        2. 将 example 的 URL 转换为本地 file:// URL
        3. 序列化 ModelMeta 到本地 metadata.json
        
        :param model_meta: 模型元数据（必须包含 type 字段，可以是远程的或本地的）
        :return: 本地化后的 ModelMeta
        """
        # 确定基础路径（从 model_meta.type 获取类型）
        if model_meta.type == ModelType.CHECKPOINT:
            base_path = checkpoint_meta_home / Path(model_meta.filename).stem
        else:
            base_path = lora_meta_home / Path(model_meta.filename).stem
        
        base_path.mkdir(parents=True, exist_ok=True)
        
        # 处理示例图片
        localized_examples: list[Example] = []
        download_tasks = []
        
        for example in model_meta.examples:
            if is_local_url(example.url):
                # 已经是本地 URL，直接使用
                localized_examples.append(example)
                logger.debug(f"示例图片已是本地: {example.filename}")
            else:
                # 远程 URL，需要下载
                save_path = base_path / example.filename
                download_tasks.append((example, save_path))
        
        # 并发下载所有远程图片
        if download_tasks:
            logger.info(f"开始下载 {len(download_tasks)} 张示例图片...")
            download_results = await asyncio.gather(
                *[download_file(ex.url, path, app_settings.civitai.timeout) 
                  for ex, path in download_tasks]
            )
            
            success_count = sum(download_results)
            fail_count = len(download_results) - success_count
            
            if fail_count > 0:
                logger.warning(f"下载示例图片: 成功 {success_count}, 失败 {fail_count}")
            else:
                logger.success(f"成功下载 {success_count} 张示例图片")
            
            # 更新 URL 为本地 file:// URL
            for (example, save_path), success in zip(download_tasks, download_results):
                if success:
                    # 创建新的 Example，替换 URL 为本地 file:// URL
                    local_example = Example(
                        url=save_path.as_uri(),  # 转换为 file:// URL
                        args=example.args
                    )
                    localized_examples.append(local_example)
                else:
                    # 下载失败，保留原 URL（或跳过）
                    logger.warning(f"跳过下载失败的示例图片: {example.filename}")
        
        # 创建本地化的 ModelMeta
        localized_meta = ModelMeta(
            filename=model_meta.filename,
            name=model_meta.name,
            version=model_meta.version,
            desc=model_meta.desc,
            model_id=model_meta.model_id,
            version_id=model_meta.version_id,
            type=model_meta.type,
            base_model=model_meta.base_model,
            sha256=model_meta.sha256,
            trained_words=model_meta.trained_words,
            url=model_meta.url,
            examples=localized_examples,
            ecosystem=model_meta.ecosystem,
            web_page_url=model_meta.web_page_url,
        )
        
        # 保存元数据到本地
        self._save_meta_to_disk(localized_meta)
        logger.success(f"已保存模型元数据: {model_meta.name} ({model_meta.type})")
        
        return localized_meta
    
    def delete(self, model_meta: ModelMeta) -> bool:
        """
        删除模型元数据及其关联的示例图片。
        
        此方法会：
        1. 删除元数据目录（包括 metadata.json 和所有示例图片）
        2. 从内存缓存中移除该模型
        
        :param model_meta: 要删除的模型元数据
        :return: 删除成功返回 True，失败返回 False
        """
        try:
            # 确定元数据目录
            if model_meta.type == ModelType.CHECKPOINT:
                meta_dir = checkpoint_meta_home / Path(model_meta.filename).stem
                cache_list = self.sd_list
            elif model_meta.type == ModelType.LORA:
                meta_dir = lora_meta_home / Path(model_meta.filename).stem
                cache_list = self.lora_list
            else:
                logger.error(f"不支持的模型类型: {model_meta.type}")
                return False
            
            # 删除目录（包括所有内容）
            if meta_dir.exists():
                shutil.rmtree(meta_dir)
                logger.info(f"已删除元数据目录: {meta_dir}")
            else:
                logger.warning(f"元数据目录不存在: {meta_dir}")
            
            # 从内存缓存中移除
            try:
                cache_list.remove(model_meta)
                logger.debug(f"已从缓存中移除: {model_meta.name}")
            except ValueError:
                logger.warning(f"模型不在缓存中: {model_meta.name}")
            
            logger.success(f"已删除模型元数据: {model_meta.name} ({model_meta.type})")
            return True
            
        except Exception as e:
            logger.exception(f"删除模型元数据失败: {model_meta.name}")
            return False
    
    # ==================== 实现基类接口 ====================
    
    def get_by_name(self, name: str) -> Optional[ModelMeta]:
        """
        通过模型名称获取模型元数据（从内存缓存）。
        
        :param name: 模型名称或文件名（不含扩展名）
        :return: 模型元数据，未找到返回 None
        """
        # 去除可能的 .safetensors 后缀
        name_stem = Path(name).stem
        
        # 搜索所有列表
        for meta in self.sd_list + self.lora_list + self.vae_list:
            # 匹配文件名（不含后缀）或模型名称
            if Path(meta.filename).stem == name_stem or meta.name == name:
                return meta
        
        logger.debug(f"未在缓存中找到模型: {name}")
        return None
    
    def get_by_path(self, path: Path) -> Optional[ModelMeta]:
        """
        通过模型文件路径获取模型元数据。
        
        从内存缓存中查找，如果未找到返回 None。
        注意：需要先调用 flush() 或确保服务已初始化。
        
        :param path: 模型文件路径
        :return: 模型元数据，未找到返回 None
        """
        if not path.exists():
            logger.warning(f"模型文件不存在: {path}")
            return None
        
        # 从缓存中查找（使用文件名查找）
        filename = path.stem  # 去掉 .safetensors 后缀
        meta = self.get_by_name(filename)
        
        if meta is None:
            logger.debug(f"未找到元数据: {filename}")
        
        return meta
    
    def get_by_hash(self, file_hash: str) -> Optional[ModelMeta]:
        """
        通过模型文件哈希值获取模型元数据（仅从本地缓存）。
        
        :param file_hash: SHA-256 哈希值
        :return: 模型元数据，未找到返回 None
        """
        # 在所有已加载的模型中搜索
        for meta in self.sd_list + self.lora_list + self.vae_list:
            if meta.sha256.lower() == file_hash.lower():
                return meta
        
        logger.debug(f"未找到哈希值为 {file_hash} 的模型")
        return None
    
    def get_by_id(self, version_id: int) -> Optional[ModelMeta]:
        """
        通过 Civitai 模型版本 ID 获取模型元数据（仅从本地缓存）。
        
        :param version_id: Civitai 模型版本 ID
        :return: 模型元数据，未找到返回 None
        """
        # 在本地缓存中查找
        for meta in self.sd_list + self.lora_list + self.vae_list:
            if meta.version_id == version_id:
                return meta
        
        logger.debug(f"未找到版本 ID 为 {version_id} 的模型")
        return None


local_model_meta_service = LocalModelModelMetaService()
