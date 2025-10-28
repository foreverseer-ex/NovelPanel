"""
Civitai 服务配置
"""
from typing import Optional
from pydantic import BaseModel, Field


class CivitaiSettings(BaseModel):
    """Civitai API 配置类。

    配置 Civitai 服务的基础 URL、API 密钥和请求超时。
    """
    base_url: str = Field(
        default="https://civitai.com",
        description="Civitai 服务地址"
    )
    
    api_key: Optional[str] = Field(
        default=None,
        description="Civitai API Key（可选，用于访问私有内容）"
    )
    
    timeout: float = Field(
        default=30.0,
        gt=0,
        description="API 请求超时时间（秒）"
    )
