"""
模型元数据服务基类。

定义所有模型元数据服务的统一接口。
"""
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional

from schemas.model_meta import ModelMeta


class AbstractModelMetaService(ABC):
    """
    模型元数据服务抽象基类。
    
    定义统一的查询接口，支持通过名称、路径、哈希值、ID 获取模型元数据。
    """
    
    @abstractmethod
    def get_by_name(self, name: str) -> Optional[ModelMeta]:
        """
        通过模型名称获取模型元数据。
        
        :param name: 模型名称（如 "waiIllustriousSDXL_v150"）
        :return: 模型元数据，未找到返回 None
        """
        raise NotImplementedError
    
    @abstractmethod
    def get_by_path(self, path: Path) -> Optional[ModelMeta]:
        """
        通过模型文件路径获取模型元数据。
        
        :param path: 模型文件路径（.safetensors 文件）
        :return: 模型元数据，未找到返回 None
        """
        raise NotImplementedError
    
    @abstractmethod
    def get_by_hash(self, file_hash: str) -> Optional[ModelMeta]:
        """
        通过模型文件哈希值获取模型元数据。
        
        :param file_hash: 模型文件的 SHA-256 哈希值
        :return: 模型元数据，未找到返回 None
        """
        raise NotImplementedError
    
    @abstractmethod
    def get_by_id(self, version_id: int) -> Optional[ModelMeta]:
        """
        通过 Civitai 模型版本 ID 获取模型元数据。
        
        注意：此方法使用 version_id 而不是 model_id，因为在 Civitai 中，
        每个版本（version）才是实际可下载和使用的模型单元。
        
        :param version_id: Civitai 模型版本 ID
        :return: 模型元数据，未找到返回 None
        """
        raise NotImplementedError
    
    @abstractmethod
    def test(self) -> bool:
        """
        测试服务是否可用。
        
        对于本地服务：通常返回 True
        对于远程服务：测试 API 连接是否正常
        
        :return: 服务是否可用
        """
        raise NotImplementedError
    
    @abstractmethod
    async def save(self, model_meta: ModelMeta) -> ModelMeta:
        """
        保存模型元数据。
        
        对于本地服务（LocalModelMetaService）：
            - 下载远程示例图片到本地
            - 转换 URL 为本地 file:// URL
            - 序列化到本地 metadata.json
        
        对于远程服务（CivitaiService）：
            - 委托给 local_model_meta_service 保存
        
        :param model_meta: 模型元数据（必须包含 type 字段）
        :return: 保存后的模型元数据
        """
        raise NotImplementedError
