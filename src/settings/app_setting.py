"""
应用全局配置。

包含所有子系统的配置，并提供加载和保存功能。
"""
import json
from pathlib import Path
from typing import Optional
from pydantic import BaseModel
from loguru import logger

from .civitai_setting import CivitaiSettings
from .sd_forge_setting import SdForgeSettings
from .ui_setting import UiSettings
from .llm_setting import LlmSettings


class AppSettings(BaseModel):
    """应用全局配置类。
    
    包含所有子系统的配置。
    """
    civitai: CivitaiSettings = CivitaiSettings()
    sd_forge: SdForgeSettings = SdForgeSettings()
    ui: UiSettings = UiSettings()
    llm: LlmSettings = LlmSettings()
    
    @classmethod
    def load(cls, config_path: Optional[Path] = None) -> "AppSettings":
        """从配置文件加载配置。
        
        :param config_path: 配置文件路径，默认为项目根目录下的 config.json
        :return: AppSettings 实例
        """
        if config_path is None:
            # 默认使用项目根目录下的 config.json
            project_root = Path(__file__).parent.parent.parent
            config_path = project_root / "config.json"
        
        if not config_path.exists():
            logger.warning(f"配置文件不存在: {config_path}，使用默认配置")
            return cls()
        
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            logger.success(f"配置加载成功: {config_path}")
            return cls(**data)
            
        except Exception as e:
            logger.error(f"加载配置失败: {e}，使用默认配置")
            return cls()
    
    def save(self, config_path: Optional[Path] = None) -> bool:
        """将配置保存到文件。
        
        :param config_path: 配置文件路径，默认为项目根目录下的 config.json
        :return: 是否成功保存
        """
        if config_path is None:
            # 默认使用项目根目录下的 config.json
            project_root = Path(__file__).parent.parent.parent
            config_path = project_root / "config.json"
        
        try:
            # 确保目录存在
            config_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 写入文件
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(self.model_dump(), f, indent=2, ensure_ascii=False)
            
            logger.success(f"配置保存成功: {config_path}")
            return True
            
        except Exception as e:
            logger.error(f"保存配置失败: {e}")
            return False


# 全局应用配置实例
app_settings = AppSettings.load()

