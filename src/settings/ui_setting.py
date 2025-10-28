"""
UI 设置
"""
from typing import Optional, Literal
from pydantic import BaseModel, Field


BaseModelType = Literal["SD 1.5", "SDXL 1.0", "Pony", "Illustrious"]


class UiSettings(BaseModel):
    """UI 设置项。
    
    包含模型管理页面等 UI 的筛选与显示相关选项。
    """
    base_model_filter: Optional[BaseModelType] = Field(
        default=None,
        description="基础模型过滤器（None 表示显示所有模型）"
    )
