"""应用常量包。

包含应用中使用的各类常量定义。
"""

from .memory import novel_memory_description, user_memory_description, memory_description
from .actor import character_tags_description
from .ui_size import *  # 导出所有 UI 尺寸常量
from .llm import (
    LlmProvider,
    LlmBaseUrl,
    RecommendedModels,
    PROVIDER_BASE_URL_MAP,
    PROVIDER_MODELS_MAP,
    get_base_url_for_provider,
    get_models_for_provider,
)
from .model_meta import ModelType, BaseModel