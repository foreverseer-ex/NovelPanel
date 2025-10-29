"""
LLM 服务模块。

提供多种 LLM 服务实现和统一的管理接口。
"""
from typing import Optional
from loguru import logger

from constants.llm import LlmProvider
from .base import AbstractLlmService
from .openai import OpenAILlmService
from .ollama import OllamaLlmService


def get_llm_service(provider: Optional[str] = None) -> AbstractLlmService:
    """
    获取 LLM 服务实例（工厂函数）。
    
    每次调用都会创建新的服务实例。
    
    :param provider: 提供商名称（如果为 None，则使用配置中的提供商）
    :return: 新创建的 LLM 服务实例
    """
    if provider is None:
        from settings import app_settings
        provider = app_settings.llm.provider
    
    provider = provider.lower()
    
    # Ollama 使用专用服务
    if provider == LlmProvider.OLLAMA:
        logger.debug("创建新的 OllamaLlmService 实例")
        return OllamaLlmService()
    
    # 其他所有提供商都使用 OpenAI 兼容服务
    # 包括: openai, xai, anthropic, google, custom
    if provider in (
        LlmProvider.OPENAI, 
        LlmProvider.XAI, 
        LlmProvider.ANTHROPIC, 
        LlmProvider.GOOGLE, 
        LlmProvider.CUSTOM
    ):
        logger.debug(f"创建新的 OpenAILlmService 实例 (provider: {provider})")
        return OpenAILlmService()
    
    # 未知提供商，默认使用 OpenAI 兼容服务
    logger.warning(
        f"未知的 LLM 提供商: {provider}，使用默认 OpenAI 兼容服务。"
        f"支持的提供商: {LlmProvider.OPENAI}, {LlmProvider.XAI}, "
        f"{LlmProvider.OLLAMA}, {LlmProvider.ANTHROPIC}, "
        f"{LlmProvider.GOOGLE}, {LlmProvider.CUSTOM}"
    )
    return OpenAILlmService()


def get_current_llm_service() -> AbstractLlmService:
    """
    获取当前配置的 LLM 服务实例。
    
    每次调用都会创建新的服务实例。
    
    :return: 新创建的 LLM 服务实例
    """
    return get_llm_service()


__all__ = [
    # 基类
    "AbstractLlmService",
    # 具体实现
    "OpenAILlmService",
    "OllamaLlmService",
    # 工厂函数
    "get_llm_service",
    "get_current_llm_service",
]
