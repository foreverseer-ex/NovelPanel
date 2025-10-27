"""
SD Forge 服务配置
"""
from pathlib import Path

from pydantic_settings import BaseSettings


class SdForgeSettings(BaseSettings):
    base_url: str = "http://127.0.0.1:7860"
    home: str = r"C:\Users\zxb\Links\sd-webui-forge-aki-v1.0"
    timeout: float = 30.0
    generate_timeout: float = 120.0

    @property
    def models_home(self):
        """
        获取模型存储目录。
        """
        return Path(self.home) / 'models'

    @property
    def lora_home(self):
        """
        获取Lora模型存储目录。
        """
        return self.models_home / 'Lora'

    @property
    def vae_home(self):
        """
        获取VAE模型存储目录。
        """
        return self.models_home / 'VAE'

    @property
    def checkpoint_home(self):
        """
        获取Stable-diffusion模型存储目录。
        """
        return self.models_home / 'Stable-diffusion'


sd_forge_settings = SdForgeSettings()
