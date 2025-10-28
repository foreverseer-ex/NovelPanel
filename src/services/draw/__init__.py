from .sd_forge import SdForgeService, sd_forge_service
from .civitai import CivitaiDrawService, civitai_draw_service
from services.base import BaseDrawService

# 简单的后端注册与获取器
DRAW_SERVICES: dict[str, BaseDrawService] = {
    "sd_forge": sd_forge_service,
    "civitai": civitai_draw_service,
}

def get_draw_service(name: str) -> BaseDrawService:
    return DRAW_SERVICES[name]
