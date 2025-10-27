"""
模型卡片颜色常量。

定义不同模型类型和基础模型的Chip颜色。
"""
import flet as ft


class ModelTypeChipColor:
    """模型类型的Chip颜色配置。"""
    CHECKPOINT = ft.Colors.BLUE_400
    LORA = ft.Colors.PURPLE_400
    VAE = ft.Colors.GREEN_400
    
    @classmethod
    def get(cls, model_type: str) -> str:
        """根据模型类型获取颜色。
        
        :param model_type: 模型类型
        :return: 颜色值
        """
        color_map = {
            'Checkpoint': cls.CHECKPOINT,
            'LORA': cls.LORA,
            'vae': cls.VAE,
        }
        return color_map.get(model_type, ft.Colors.GREY_400)


class BaseModelColor:
    """基础模型的Chip颜色配置。"""
    SD1 = ft.Colors.ORANGE_400
    SDXL = ft.Colors.PINK_400
    ILLUSTRIOUS = ft.Colors.CYAN_400
    
    @classmethod
    def get(cls, base_model: str) -> str:
        """根据基础模型获取颜色。
        
        :param base_model: 基础模型名称
        :return: 颜色值
        """
        color_map = {
            'sd1': cls.SD1,
            'sdxl': cls.SDXL,
            'Illustrious': cls.ILLUSTRIOUS,
        }
        return color_map.get(base_model, ft.Colors.GREY_400)
