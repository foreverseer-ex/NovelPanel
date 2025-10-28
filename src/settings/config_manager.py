"""
配置管理器。

负责加载和保存应用配置到 config.json。
"""
import json
from pathlib import Path
from typing import Optional
from loguru import logger

from .civitai_setting import CivitaiSettings, civitai_settings
from .sd_forge_setting import SdForgeSettings, sd_forge_settings


class ConfigManager:
    """配置管理器类。
    
    负责从 config.json 加载配置到全局 settings 对象，
    并在需要时将配置保存回文件。
    """
    
    def __init__(self, config_path: Optional[Path] = None):
        """初始化配置管理器。
        
        :param config_path: 配置文件路径，默认为项目根目录下的 config.json
        """
        if config_path is None:
            # 默认使用项目根目录下的 config.json
            project_root = Path(__file__).parent.parent.parent
            config_path = project_root / "config.json"
        
        self.config_path = config_path
        logger.info(f"配置文件路径: {self.config_path}")
    
    def load(self) -> bool:
        """从配置文件加载配置到全局 settings 对象。
        
        :return: 是否成功加载
        """
        if not self.config_path.exists():
            logger.warning(f"配置文件不存在: {self.config_path}，使用默认配置")
            return False
        
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            # 更新 Civitai 设置
            if "civitai" in data:
                for key, value in data["civitai"].items():
                    if hasattr(civitai_settings, key):
                        setattr(civitai_settings, key, value)
                logger.info("已加载 Civitai 配置")
            
            # 更新 SD Forge 设置
            if "sd_forge" in data:
                for key, value in data["sd_forge"].items():
                    if hasattr(sd_forge_settings, key):
                        setattr(sd_forge_settings, key, value)
                logger.info("已加载 SD Forge 配置")
            
            logger.success(f"配置加载成功: {self.config_path}")
            return True
            
        except Exception as e:
            logger.error(f"加载配置失败: {e}")
            return False
    
    def save(self) -> bool:
        """将当前全局 settings 对象保存到配置文件。
        
        :return: 是否成功保存
        """
        try:
            # 构建配置字典
            config = {
                "civitai": {
                    "base_url": civitai_settings.base_url,
                    "api_key": civitai_settings.api_key,
                    "timeout": civitai_settings.timeout,
                },
                "sd_forge": {
                    "base_url": sd_forge_settings.base_url,
                    "home": sd_forge_settings.home,
                    "timeout": sd_forge_settings.timeout,
                    "generate_timeout": sd_forge_settings.generate_timeout,
                }
            }
            
            # 确保目录存在
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 写入文件
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            logger.success(f"配置保存成功: {self.config_path}")
            return True
            
        except Exception as e:
            logger.error(f"保存配置失败: {e}")
            return False


# 全局配置管理器实例
config_manager = ConfigManager()

