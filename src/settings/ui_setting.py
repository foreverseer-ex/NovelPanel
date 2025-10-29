"""
UI 设置
"""
from typing import Optional
from pydantic import BaseModel, Field


class UiSettings(BaseModel):
    """UI 设置项。
    
    包含模型管理页面等 UI 的筛选与显示相关选项。
    """
    ecosystem_filter: Optional[str] = Field(
        default=None,
        description="生态系统过滤器（None 表示显示所有模型）。可选值：sd1, sd2, sdxl"
    )
    
    base_model_filter: Optional[str] = Field(
        default=None,
        description="基础模型过滤器（None 表示显示所有模型）。可选值：pony, illustrious, standard 等"
    )
