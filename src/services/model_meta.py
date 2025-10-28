"""
模型元数据管理器（兼容包装）。
将导入转发到 services.model_meta_provider.local。
"""
from services.model_meta_provider.local import (
    LocalModelMetaService as ModelMetaService,
    local_model_meta_service as model_meta_service,
)
