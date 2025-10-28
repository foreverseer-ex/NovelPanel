"""
SD Forge 服务配置
"""
from pathlib import Path
from pydantic import BaseModel, Field


class SdForgeSettings(BaseModel):
    """SD Forge (Stable Diffusion WebUI) 配置类。

    配置 SD Forge 服务的地址、本地目录和超时设置。
    """
    base_url: str = Field(
        default="http://127.0.0.1:7860",
        description="SD Forge WebUI 服务地址"
    )
    
    home: str = Field(
        default=r"C:\Users\zxb\Links\sd-webui-forge-aki-v1.0",
        description="SD Forge 安装目录"
    )
    
    timeout: float = Field(
        default=30.0,
        gt=0,
        description="API 请求超时时间（秒）"
    )
    
    generate_timeout: float = Field(
        default=120.0,
        gt=0,
        description="图像生成超时时间（秒）"
    )

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
