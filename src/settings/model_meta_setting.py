"""
模型元数据配置
"""
from typing import Optional, Literal
from pydantic import BaseModel


BaseModelType = Literal["SD 1.5", "SDXL 1.0", "Pony", "Illustrious"]


class ModelMetaSettings(BaseModel):
    """模型元数据配置类。
    
    配置模型筛选等选项。
    """
    base_model_filter: Optional[BaseModelType] = None  # None 表示不筛选

