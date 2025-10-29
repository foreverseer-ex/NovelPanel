"""
模型元数据服务模块。

提供本地和 Civitai 两种模型元数据服务，都实现了统一的基类接口。
"""
from .base import AbstractModelMetaService
from .civitai import CivitaiModelMetaService, civitai_model_meta_service
from .local import LocalModelModelMetaService, local_model_meta_service

__all__ = [
    # 基类
    "AbstractModelMetaService",
    # Civitai 服务
    "CivitaiModelMetaService",
    "civitai_model_meta_service",
    # 本地服务
    "LocalModelModelMetaService",
    "local_model_meta_service",
]
