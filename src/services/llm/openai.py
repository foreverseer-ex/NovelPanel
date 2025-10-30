"""
OpenAI 兼容 LLM 服务实现（支持 xAI/OpenAI/Anthropic/Google 等）。
"""
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from loguru import logger

from settings import app_settings
from .base import AbstractLlmService


class OpenAILlmService(AbstractLlmService):
    """
    OpenAI 兼容的 LLM 服务。
    
    支持所有 OpenAI 兼容的 API 端点：
    - xAI (Grok)
    - OpenAI (GPT)
    - Anthropic (Claude)
    - Google (Gemini)
    - 自定义端点
    """

    def initialize_llm(self) -> bool:
        """
        初始化 OpenAI 兼容的 LLM 实例。
        
        :return: 初始化是否成功
        """
        try:
            self.llm = ChatOpenAI(
                model=app_settings.llm.model,
                api_key=app_settings.llm.api_key,
                base_url=app_settings.llm.base_url,
                temperature=app_settings.llm.temperature,
            )
            logger.info(f"正在绑定 {len(self.tools)} 个工具到模型...")
            llm_with_tools = self.llm.bind_tools(self.tools)
            self.agent = create_agent(llm_with_tools, self.tools)
            
            # 检查模型是否真的支持工具调用
            model_name = app_settings.llm.model.lower()
            if not any(keyword in model_name for keyword in ['gpt-4', 'gpt-3.5-turbo', 'claude', 'gemini']):
                logger.warning(f"⚠️ 模型 '{app_settings.llm.model}' 可能不支持 function calling")
                logger.warning("⚠️ 如果工具调用无法正常工作，请尝试使用 GPT-4、Claude 3.5 或 Gemini 1.5 等模型")
            
            logger.success(
                f"OpenAI 兼容服务初始化成功: {app_settings.llm.provider} / {app_settings.llm.model} "
                f"({len(self.tools)} 个工具)"
            )
            return True
        except Exception as e:
            logger.exception(f"OpenAI 兼容服务初始化失败: {e}")
            return False
