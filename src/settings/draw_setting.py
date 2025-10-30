"""
绘图服务配置。

配置使用的绘图后端（SD-Forge 或 Civitai）。
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Literal


class DrawSettings(BaseModel):
    """绘图服务配置类。
    
    配置使用哪个绘图后端服务。
    """
    
    backend: Literal["sd_forge", "civitai"] = Field(
        default="sd_forge",
        description="绘图后端：sd_forge（本地 SD-Forge）或 civitai（Civitai 云端）"
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "backend": "sd_forge"
            }
        }
    )

