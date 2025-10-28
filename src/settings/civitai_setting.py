"""
Civitai 服务配置
"""
from typing import Optional
from pydantic import BaseModel


class CivitaiSettings(BaseModel):
    """Civitai API 配置类。

    配置 Civitai 服务的基础 URL、API 密钥和请求超时。
    """
    base_url: str = "https://civitai.com"
    api_key: Optional[str] = None  # 如需鉴权可配置
    timeout: float = 30.0
