"""
Civitai 服务配置
"""
from typing import Optional
from pydantic_settings import BaseSettings


class CivitaiSettings(BaseSettings):
    base_url: str = "https://civitai.com"
    api_key: Optional[str] = None  # 如需鉴权可配置
    timeout: float = 30.0


civitai_settings = CivitaiSettings()
