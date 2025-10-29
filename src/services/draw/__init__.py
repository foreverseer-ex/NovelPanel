"""
绘图服务模块。

提供 SD-Forge 和 Civitai 两种绘图服务实现，都实现了统一的基类接口。
"""
from .base import AbstractDrawService
from .sd_forge import SdForgeDrawService, sd_forge_draw_service
from .civitai import CivitaiDrawService, civitai_draw_service

# 简单的后端注册与获取器
DRAW_SERVICES: dict[str, AbstractDrawService] = {
    "sd_forge": sd_forge_draw_service,
    "civitai": civitai_draw_service,
}


def get_draw_service(name: str) -> AbstractDrawService:
    """
    根据名称获取绘图服务实例。
    
    :param name: 服务名称（sd_forge/civitai）
    :return: 绘图服务实例
    """
    service = DRAW_SERVICES.get(name)
    if not service:
        raise ValueError(f"未知的绘图服务: {name}")
    return service


def get_current_draw_service() -> AbstractDrawService:
    """
    根据当前配置获取绘图服务实例。
    
    从 app_settings.draw.backend 读取配置并返回对应的服务。
    
    :return: 当前配置的绘图服务实例
    """
    from settings import app_settings
    backend = app_settings.draw.backend
    return get_draw_service(backend)


__all__ = [
    # 基类
    "AbstractDrawService",
    # SD-Forge 服务
    "SdForgeDrawService",
    "sd_forge_draw_service",
    # Civitai 服务
    "CivitaiDrawService",
    "civitai_draw_service",
    # 服务注册
    "DRAW_SERVICES",
    "get_draw_service",
    "get_current_draw_service",
]
