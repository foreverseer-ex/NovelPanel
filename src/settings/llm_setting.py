"""
LLM (大语言模型) 配置。

支持配置 OpenAI 兼容的 API，包括 Grok、GPT、本地模型等。

环境变量支持：
- OPENAI_API_KEY: 设置 api_key（通用环境变量名）
- XAI_API_KEY: 设置 api_key（xAI 专用）
"""
import os
from pydantic import BaseModel, Field

from constants.llm import LlmProvider, LlmBaseUrl, DEFAULT_SYSTEM_PROMPT


class LlmSettings(BaseModel):
    """LLM 配置
    
    环境变量优先级：
    1. XAI_API_KEY（xAI 专用）
    2. OPENAI_API_KEY（OpenAI 兼容通用）
    3. 配置文件中的值
    """

    # 提供商选择
    provider: str = Field(
        default=LlmProvider.XAI,
        description="LLM 提供商：openai、xai、ollama、anthropic、google"
    )

    # API 配置
    model: str = Field(
        default="grok-4-fast-reasoning",
        description="模型名称，如：grok-4-fast-reasoning, gpt-4o, llama3.1, claude-3-5-sonnet"
    )

    api_key: str = Field(
        default_factory=lambda: os.getenv("XAI_API_KEY") or os.getenv("OPENAI_API_KEY") or "",
        description="API 密钥（Ollama 不需要）。可通过环境变量 OPENAI_API_KEY 或 XAI_API_KEY 设置"
    )

    base_url: str = Field(
        default=LlmBaseUrl.XAI,
        description=f"API 基础 URL（OpenAI: {LlmBaseUrl.OPENAI}, xAI: {LlmBaseUrl.XAI}, Ollama: {LlmBaseUrl.OLLAMA}）"
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
        default=DEFAULT_SYSTEM_PROMPT,
        description="系统提示词：定义 AI 助手的角色和行为"
    )

    summary_epoch: int = Field(
        default=100,
        ge=10,
        le=1000,
        description="对话总结周期：每隔多少轮对话进行一次总结（10-1000）"
    )

    class Config:
        json_schema_extra = {
            "examples": [
                # xAI (Grok) 配置
                {
                    "provider": "xai",
                    "model": "grok-4-fast-reasoning",
                    "api_key": "xai-xxx",
                    "base_url": LlmBaseUrl.XAI,
                    "temperature": 0.7,
                    "developer_mode": True,
                    "system_prompt": "你是 NovelPanel 的 AI 助手..."
                },
                # OpenAI 配置
                {
                    "provider": "openai",
                    "model": "gpt-4o",
                    "api_key": "sk-xxx",
                    "base_url": LlmBaseUrl.OPENAI,
                    "temperature": 0.7,
                },
                # Ollama 配置
                {
                    "provider": "ollama",
                    "model": "llama3.1",
                    "api_key": "",
                    "base_url": LlmBaseUrl.OLLAMA,
                    "temperature": 0.7,
                },
            ]
        }
