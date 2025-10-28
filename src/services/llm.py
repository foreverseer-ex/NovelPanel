"""
LLM (大语言模型) 服务。

提供 AI Agent 功能，自动调用
LLM 服务兼容包装，转发到 services.llm.openai。
"""
from services.llm.openai import LlmService, llm_service
