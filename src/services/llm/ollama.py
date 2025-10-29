"""
Ollama LLM 服务实现。
"""
from langchain_ollama import ChatOllama
from langchain.agents import create_agent
from loguru import logger

from settings import app_settings
from .base import AbstractLlmService


class OllamaLlmService(AbstractLlmService):
    """
    Ollama LLM 服务。
    
    支持本地运行的 Ollama 模型：
    - llama3.1
    - qwen2.5
    - mistral
    - deepseek-r1
    - phi4
    等
    """

    def initialize_llm(self) -> bool:
        """
        初始化 Ollama LLM 实例。
        
        :return: 初始化是否成功
        """
        try:
            self.llm = ChatOllama(
                model=app_settings.llm.model,
                base_url=app_settings.llm.base_url,
                temperature=app_settings.llm.temperature,
            )
            llm_with_tools = self.llm.bind_tools(self.tools)
            self.agent = create_agent(llm_with_tools, self.tools)
            logger.success(
                f"Ollama 服务初始化成功: {app_settings.llm.model} "
                f"({len(self.tools)} 个工具)"
            )
            return True
        except Exception as e:
            logger.exception(f"Ollama 服务初始化失败: {e}")
            logger.info("请确保 Ollama 服务正在运行并且模型已下载")
            return False

