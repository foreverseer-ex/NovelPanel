"""
LLM 服务基础抽象类。

定义所有 LLM 服务的统一接口。
"""
from abc import ABC, abstractmethod
from typing import Optional, List, Any, AsyncGenerator
from pathlib import Path
import json
from loguru import logger

from settings import app_settings
from constants.llm import DEVELOP_MODE_PROMPTS
from schemas.chat import ChatHistory, ToolCall, TextMessage
from utils.path import chat_history_home

# 导入所有路由函数
from routers.session import (
    create_session, get_session, list_sessions, update_session,
    delete_session, update_session_status, update_progress,
)
from routers.actor import (
    create_actor, get_actor, list_actors, update_actor,
    remove_actor, get_tag_description, get_all_tag_descriptions,
)
from routers.memory import (
    create_memory, get_memory, query_memories, update_memory,
    delete_memory, get_key_description, get_all_key_descriptions,
)
from routers.reader import (
    parse_novel, get_line, get_line_chapter_index, get_chapters,
    get_chapter, get_chapter_summary, put_chapter_summary,
)
from routers.draw import (
    get_loras, get_sd_models, get_options, set_options, generate, get_image,
)
from routers.llm import (
    add_choices, get_choices, clear_choices,
)


class AbstractLlmService(ABC):
    """
    LLM 服务抽象基类。
    
    定义统一的 LLM 接口，支持不同的提供商（OpenAI、Ollama 等）。
    """
    
    def __init__(self):
        """初始化服务。"""
        self.llm: Optional[Any] = None
        self.agent: Optional[Any] = None
        self.tools: List[Any] = []
        self.history: ChatHistory = ChatHistory()  # 聊天历史记录
        self._initialize_tools()
        
        # 尝试初始化 LLM 服务
        try:
            self.initialize_llm()
        except Exception as e:
            logger.exception(f"LLM 服务初始化失败（将在首次使用时重试）: {e}")
    
    def _initialize_tools(self):
        """初始化工具函数列表。"""
        from langchain_core.tools import tool
        
        all_functions = [
            # Session 管理
            create_session, get_session, list_sessions, update_session,
            delete_session, update_session_status, update_progress,
            # Actor 管理
            create_actor, get_actor, list_actors, update_actor,
            remove_actor, get_tag_description, get_all_tag_descriptions,
            # Memory 管理
            create_memory, get_memory, query_memories, update_memory,
            delete_memory, get_key_description, get_all_key_descriptions,
            # Reader 功能
            parse_novel, get_line, get_line_chapter_index, get_chapters,
            get_chapter, get_chapter_summary, put_chapter_summary,
            # Draw 功能
            get_loras, get_sd_models, get_options, set_options, generate, get_image,
            # LLM 辅助功能
            add_choices, get_choices, clear_choices,
        ]
        self.tools = [tool(func) for func in all_functions]
        logger.info(f"已初始化 {len(self.tools)} 个工具函数")
    
    @abstractmethod
    def initialize_llm(self) -> bool:
        """
        初始化 LLM 实例。
        
        由子类实现具体的 LLM 初始化逻辑（如 ChatOpenAI、ChatOllama 等）。
        
        :return: 初始化是否成功
        """
        raise NotImplementedError
    
    def is_ready(self) -> bool:
        """
        检查服务是否就绪。
        
        :return: 服务是否已初始化且可用
        """
        return self.llm is not None and self.agent is not None
    
    async def chat(self, message: str, session_id: str = "default") -> AsyncGenerator[str, None]:
        """
        与 LLM 进行对话（流式返回）。
        
        支持开发者模式和自定义系统提示词：
        - 如果启用开发者模式，会在消息前添加开发者模式提示词
        - 如果配置了系统提示词，会在开发者模式提示词之后添加
        - 自动管理聊天历史记录（支持文本和工具调用）
        
        :param message: 用户消息
        :param session_id: 会话 ID
        :yield: LLM 响应的文本片段
        """
        if not self.is_ready():
            logger.error("LLM 服务未就绪")
            yield "错误：LLM 服务未就绪，请先初始化 LLM"
            return
        
        try:
            # 添加用户消息到历史记录
            self.add_message("user", message)
            
            # 构建消息列表
            messages = []
            
            # 1. 如果启用开发者模式，添加开发者模式提示词
            if app_settings.llm.developer_mode:
                messages.append(("system", DEVELOP_MODE_PROMPTS))
                logger.debug("已启用开发者模式")
            
            # 2. 如果配置了系统提示词（非空），添加系统提示词
            if app_settings.llm.system_prompt and app_settings.llm.system_prompt.strip():
                messages.append(("system", app_settings.llm.system_prompt))
                logger.debug(f"已添加系统提示词: {app_settings.llm.system_prompt[:50]}...")
            
            # 3. 添加历史消息
            history_messages = self.history.get_messages_for_llm()
            for role, msg in history_messages:
                # 将 role 映射到 langchain 的格式
                if role == "user":
                    messages.append(("human", msg))
                elif role == "assistant":
                    messages.append(("ai", msg))
                # system 消息已经在前面添加了，这里跳过
            
            # 收集完整响应
            full_response = ""
            
            # 实现流式对话逻辑
            async for chunk in self.agent.astream_events(
                {"messages": messages},
                version="v2"
            ):
                event_type = chunk.get("event")
                
                # 处理文本流事件
                if event_type == "on_chat_model_stream":
                    # chunk["data"]["chunk"] 是 AIMessageChunk 对象
                    message_chunk = chunk.get("data", {}).get("chunk")
                    if message_chunk and hasattr(message_chunk, "content"):
                        content = message_chunk.content
                        if content:
                            # 检查当前助手消息的最后一个内容
                            # 如果末尾是工具调用，需要新建文本消息
                            # 如果末尾是文本消息，追加内容
                            if self.history.messages and self.history.messages[-1].role == "assistant":
                                last_msg = self.history.messages[-1]
                                if last_msg.messages and isinstance(last_msg.messages[-1], ToolCall):
                                    # 末尾是工具调用，创建新的文本消息
                                    self.history.add_message("assistant", content=content)
                                else:
                                    # 末尾是文本或空，追加内容
                                    if not last_msg.messages:
                                        last_msg.messages.append(TextMessage(content=content))
                                    else:
                                        # 追加到最后一个文本消息
                                        last_content = last_msg.messages[-1]
                                        if isinstance(last_content, TextMessage):
                                            last_content.content += content
                                        else:
                                            # 不是文本消息，创建新的
                                            last_msg.messages.append(TextMessage(content=content))
                            else:
                                # 还没有助手消息，创建新的
                                self.history.add_message("assistant", content=content)
                            
                            full_response += content
                            yield content
                
                # 处理工具调用事件
                elif event_type == "on_tool_start":
                    tool_name = chunk.get("name", "")
                    tool_input = chunk.get("data", {}).get("input", {})
                    logger.debug(f"工具调用开始: {tool_name}, 参数: {tool_input}")
                    
                    # 添加工具调用到历史记录（结果暂时为 None）
                    self.history.add_tool_call(tool_name, tool_input, result=None)
                
                elif event_type == "on_tool_end":
                    tool_output = chunk.get("data", {}).get("output")
                    logger.debug(f"工具调用结束: 结果={tool_output}")
                    
                    # 更新最后一个工具调用的结果
                    if self.history.messages and self.history.messages[-1].role == "assistant":
                        last_msg = self.history.messages[-1]
                        if last_msg.messages and isinstance(last_msg.messages[-1], ToolCall):
                            last_msg.messages[-1].result = str(tool_output)
                    
                    # 如果工具是 add_choices，从全局存储获取 choices 并添加
                    if chunk.get("name") == "add_choices":
                        from routers.llm import _session_choices
                        choices = _session_choices.get(session_id)
                        if choices:
                            self.history.add_choices(choices)
                            logger.debug(f"已为会话添加 {len(choices)} 个选项")
            
            # 自动保存历史记录
            self.save_history(session_id)
                
        except Exception as e:
            logger.exception(f"对话失败: {e}")
            error_msg = f"错误：{e}"
            yield error_msg
    
    async def simple_chat(self, message: str) -> str:
        """
        简单对话（非流式）。
        
        支持开发者模式和自定义系统提示词：
        - 如果启用开发者模式，会在消息前添加开发者模式提示词
        - 如果配置了系统提示词，会在开发者模式提示词之后添加
        
        :param message: 用户消息
        :return: LLM 完整响应
        """
        if not self.is_ready():
            logger.error("LLM 服务未就绪")
            return "错误：LLM 服务未就绪"
        
        try:
            # 构建消息列表
            messages = []
            
            # 1. 如果启用开发者模式，添加开发者模式提示词
            if app_settings.llm.developer_mode:
                messages.append(("system", DEVELOP_MODE_PROMPTS))
                logger.debug("已启用开发者模式")
            
            # 2. 如果配置了系统提示词（非空），添加系统提示词
            if app_settings.llm.system_prompt and app_settings.llm.system_prompt.strip():
                messages.append(("system", app_settings.llm.system_prompt))
                logger.debug(f"已添加系统提示词: {app_settings.llm.system_prompt[:50]}...")
            
            # 3. 添加用户消息
            messages.append(("human", message))
            
            response = await self.llm.ainvoke(messages)
            return response.content
        except Exception as e:
            logger.exception(f"对话失败: {e}")
            return f"错误：{e}"
    
    def get_tool_list(self) -> List[str]:
        """
        获取可用工具列表。
        
        :return: 工具名称列表
        """
        return [tool.name for tool in self.tools]
    
    def load_history(self, session_id: str) -> bool:
        """
        从文件加载聊天历史记录。
        
        :param session_id: 会话 ID
        :return: 是否加载成功
        """
        try:
            history_file = chat_history_home / f"{session_id}.json"
            if not history_file.exists():
                logger.info(f"会话 {session_id} 的历史记录不存在，创建新会话")
                self.history = ChatHistory()
                return False
            
            with open(history_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.history = ChatHistory(**data)
            
            logger.success(f"已加载会话 {session_id} 的历史记录（{len(self.history.messages)} 条消息）")
            return True
            
        except Exception as e:
            logger.exception(f"加载历史记录失败: {e}")
            self.history = ChatHistory()
            return False
    
    def save_history(self, session_id: str) -> bool:
        """
        保存聊天历史记录到文件。
        
        :param session_id: 会话 ID
        :return: 是否保存成功
        """
        try:
            history_file = chat_history_home / f"{session_id}.json"
            with open(history_file, "w", encoding="utf-8") as f:
                json.dump(self.history.model_dump(), f, ensure_ascii=False, indent=2)
            
            logger.debug(f"已保存会话 {session_id} 的历史记录（{len(self.history.messages)} 条消息）")
            return True
            
        except Exception as e:
            logger.exception(f"保存历史记录失败: {e}")
            return False
    
    def clear_history(self):
        """清空当前会话的历史记录。"""
        self.history.clear()
        logger.info("已清空聊天历史记录")
    
    def add_message(self, role: str, message: str = None, content: str = None):
        """
        添加消息到历史记录。
        
        :param role: 消息角色（system/user/assistant）
        :param message: 消息内容（已废弃，使用 content）
        :param content: 文本内容
        """
        # 兼容旧 API
        text_content = content or message
        if text_content:
            self.history.add_message(role, content=text_content)  # type: ignore

