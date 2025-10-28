"""
LLM (大语言模型) 配置。

支持配置 OpenAI 兼容的 API，包括 Grok、GPT、本地模型等。
"""
from pydantic import BaseModel, Field


class LlmSettings(BaseModel):
    """LLM 配置"""

    # API 配置
    model: str = Field(
        default="grok-4-latest",
        description="模型名称，如：grok-4-latest, gpt-4, llama3.1"
    )

    api_key: str = Field(
        default="",
        description="API 密钥"
    )

    base_url: str = Field(
        default="https://api.x.ai/v1",
        description="API 基础 URL"
    )

    temperature: float = Field(
        default=0.7,
        ge=0.0,
        le=2.0,
        description="温度参数 (0.0-2.0)，控制输出的随机性"
    )

    # 高级配置
    developer_mode: bool = Field(
        default=True,
        description="开发者模式：是否突破模型限制"
    )

    system_prompt: str = Field(
        default=None,
        description="系统提示词：定义 AI 助手的角色和行为"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "model": "grok-4-latest",
                "api_key": "xai-xxx",
                "base_url": "https://api.x.ai/v1",
                "temperature": 0.7,
                "developer_mode": False,
                "system_prompt": "你是 NovelPanel 的 AI 助手..."
            }
        }
