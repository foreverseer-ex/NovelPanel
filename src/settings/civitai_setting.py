"""
Civitai 服务配置
"""
import os
from typing import Optional
from pydantic import BaseModel, Field


class CivitaiSettings(BaseModel):
    """Civitai API 配置类。

    配置 Civitai 服务的基础 URL、API 密钥和请求超时。
    
    环境变量支持：
    - CIVITAI_API_TOKEN: 设置 api_token
    """
    api_token: Optional[str] = Field(
        default_factory=lambda: os.getenv("CIVITAI_API_TOKEN"),
        description="Civitai API Token（可选，用于访问私有内容）。可通过环境变量 CIVITAI_API_TOKEN 设置"
    )
    
    timeout: float = Field(
        default=30.0,
        gt=0,
        description="API 请求超时时间（秒）"
    )
