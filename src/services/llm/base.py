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
from constants.llm import DEVELOP_MODE_PROMPTS, MCP_TOOLS_GUIDE
from schemas.chat import ChatHistory, ToolCall, TextMessage
from utils.path import chat_history_home

# 导入所有路由函数
from routers.session import (
    get_session, update_session,
    update_session_status, update_progress,
)
from routers.actor import (
    create_actor, get_actor, list_actors, update_actor,
    remove_actor, get_tag_description, get_all_tag_descriptions,
    add_example, remove_example, generate_portrait
)
from routers.memory import (
    create_memory, get_memory, list_memories, update_memory,
    delete_memory, get_key_description, get_all_key_descriptions,
)
from routers.reader import (
    get_line, get_chapter_lines, get_chapters,
    get_chapter, get_chapter_summary, put_chapter_summary, get_stats,
)
from routers.draw import (
    get_loras, get_sd_models, get_options, set_options, generate, get_image,
)
from routers.llm import (
    add_choices, get_choices, clear_choices,
)
from routers.novel import (
    get_session_content, get_chapter_content, get_line_content,
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
        import json
        import functools
        from langchain_core.tools import tool
        
        def tool_wrapper(func):
            """包装工具函数，确保返回值符合 OpenAI API 要求。"""
            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs):
                result = await func(*args, **kwargs)
                # 如果返回值是空列表，转换为描述性字符串
                if isinstance(result, list) and len(result) == 0:
                    return "无结果"
                # 如果返回值是列表，转换为 JSON 字符串
                elif isinstance(result, list):
                    # 使用 Pydantic 的 model_dump(mode='json') 来正确处理 datetime 等特殊类型
                    serialized_items = []
                    for item in result:
                        if hasattr(item, 'model_dump'):
                            serialized_items.append(item.model_dump(mode='json'))
                        else:
                            serialized_items.append(item)
                    return json.dumps(serialized_items, ensure_ascii=False, indent=2)
                return result
            
            @functools.wraps(func)
            def sync_wrapper(*args, **kwargs):
                result = func(*args, **kwargs)
                # 如果返回值是空列表，转换为描述性字符串
                if isinstance(result, list) and len(result) == 0:
                    return "无结果"
                # 如果返回值是列表，转换为 JSON 字符串
                elif isinstance(result, list):
                    # 使用 Pydantic 的 model_dump(mode='json') 来正确处理 datetime 等特殊类型
                    serialized_items = []
                    for item in result:
                        if hasattr(item, 'model_dump'):
                            serialized_items.append(item.model_dump(mode='json'))
                        else:
                            serialized_items.append(item)
                    return json.dumps(serialized_items, ensure_ascii=False, indent=2)
                return result
            
            # 检查函数是否是异步的
            import asyncio
            if asyncio.iscoroutinefunction(func):
                return async_wrapper
            else:
                return sync_wrapper
        
        all_functions = [
            # Session 管理（只允许查询和更新，不允许创建和删除）
            get_session, update_session, update_session_status, update_progress,
            # Actor 管理
            create_actor, get_actor, list_actors, update_actor,
            remove_actor, add_example, remove_example, generate_portrait,
            get_tag_description, get_all_tag_descriptions,
            # Memory 管理
            create_memory, get_memory, list_memories, update_memory,
            delete_memory, get_key_description, get_all_key_descriptions,
            # Reader 功能
            get_line, get_chapter_lines, get_chapters,
            get_chapter, get_chapter_summary, put_chapter_summary, get_stats,
            # Novel 内容管理
            get_session_content, get_chapter_content, get_line_content,
            # Draw 功能
            get_loras, get_sd_models, get_options, set_options, generate, get_image,
            # LLM 辅助功能
            add_choices, get_choices, clear_choices,
        ]
        # 先包装，再转换为工具
        self.tools = [tool(tool_wrapper(func)) for func in all_functions]
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
    
    async def _get_session_context(self, session_id: str) -> Optional[str]:
        """
        获取当前会话的上下文信息（包括会话基本信息和所有记忆条目）。
        
        :param session_id: 会话 ID
        :return: 格式化的会话信息（JSON 字符串），如果会话不存在则返回 None
        """
        try:
            # 查询会话信息
            session = await get_session(session_id)
            if not session:
                logger.warning(f"会话不存在: {session_id}")
                return None
            
            # 构建会话上下文信息
            context = {
                "session_id": session.session_id,
                "title": session.title,
                "status": session.status,
                "novel_path": session.novel_path,
                "author": session.author,
                "total_lines": session.total_lines,
                "total_chapters": session.total_chapters,
                "current_line": session.current_line,
                "current_chapter": session.current_chapter,
            }
            
            # 计算进度百分比
            if session.total_lines and session.total_lines > 0:
                progress = (session.current_line / session.total_lines) * 100
                context["progress_percentage"] = round(progress, 2)
            
            # 查询所有记忆条目
            memories = await list_memories(session_id=session_id, limit=1000)
            
            # 构建记忆字典（按 key 分组）
            memories_dict = {}
            for memory in memories:
                memories_dict[memory.key] = {
                    "value": memory.value,
                    "description": memory.description,
                }
            
            # 格式化为 JSON 字符串，包含提示信息
            session_info = f"""=== 当前会话上下文 (Current Session Context) ===

【会话基本信息】
{json.dumps(context, ensure_ascii=False, indent=2)}

【会话记忆条目】（共 {len(memories)} 条）
{json.dumps(memories_dict, ensure_ascii=False, indent=2)}

=== 字段说明 ===

会话基本信息：
- session_id: 会话唯一标识
- title: 项目标题
- status: 当前状态（created/analyzing/generating/selecting/composing/completed/failed）
- novel_path: 小说文件路径
- author: 小说作者
- total_lines: 小说总行数
- total_chapters: 总章节数
- current_line: 当前处理到的行号
- current_chapter: 当前处理到的章节号
- progress_percentage: 处理进度百分比

会话记忆条目：
记忆包含了与小说相关的重要信息（世界观、情节、人物设定等）和用户偏好（艺术风格、标签偏好等）。
每个记忆条目包含：
- key: 记忆的键名（如"作品类型"、"主题"、"世界观设定"等）
- value: 记忆的具体内容
- description: 对该键的说明

这些记忆对于理解项目背景和用户需求非常重要，请在回答时充分利用这些信息。

你可以使用工具函数进行更多操作：
- 查询小说内容: get_line(), get_chapter_lines()
- 管理记忆: create_memory(), update_memory(), delete_memory()
- 管理角色: create_actor(), list_actors()
- 查询章节: get_chapters(), get_chapter_summary()
等等。"""
            
            return session_info
            
        except Exception as e:
            logger.exception(f"获取会话上下文失败: {e}")
            return None
    
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
            
            # 3. 添加 MCP 工具使用指南
            messages.append(("system", MCP_TOOLS_GUIDE))
            logger.debug("已添加 MCP 工具使用指南")
            
            # 4. 添加当前会话信息
            session_info = await self._get_session_context(session_id)
            if session_info:
                messages.append(("system", session_info))
                logger.debug(f"已添加会话信息: session_id={session_id}")
            
            # 5. 添加历史消息（基于 summary_epoch 的滑动窗口）
            history_messages = self.history.get_messages_for_llm()
            summary_epoch = app_settings.llm.summary_epoch
            
            # 计算当前对话轮数和应该保留的历史范围
            total_messages = len(history_messages)
            current_epoch = total_messages // summary_epoch
            start_index = current_epoch * summary_epoch
            
            # 只保留当前 epoch 的消息
            messages_to_include = history_messages[start_index:]
            
            logger.debug(f"对话历史：总共 {total_messages} 条，当前 epoch {current_epoch}，"
                        f"保留 {start_index}-{total_messages} 共 {len(messages_to_include)} 条")
            
            # 检查是否需要提示总结（在 epoch 的最后一轮）
            messages_in_current_epoch = len(messages_to_include)
            if messages_in_current_epoch == summary_epoch - 1:
                # 即将达到 summary_epoch，提示模型总结
                summary_reminder = f"""
⚠️ 重要提示：
当前对话即将达到 {summary_epoch} 轮（当前第 {messages_in_current_epoch + 1} 轮）。
请在回答用户问题后，总结本轮对话的关键信息，并使用 create_memory 或 update_memory 工具更新 "chat_summary" 记忆条目。

总结应包含：
- 用户的主要需求和目标
- 已完成的重要操作
- 当前进展和状态
- 待办事项或下一步计划

这样可以在下一轮对话中保持连贯性。"""
                messages.append(("system", summary_reminder))
                logger.info(f"已添加对话总结提示（第 {messages_in_current_epoch + 1}/{summary_epoch} 轮）")
            
            # 添加历史消息
            for role, msg in messages_to_include:
                # 将 role 映射到 langchain 的格式
                if role == "user":
                    messages.append(("human", msg))
                elif role == "assistant":
                    messages.append(("ai", msg))
                # system 消息已经在前面添加了，这里跳过
            
            # 收集完整响应
            full_response = ""
            
            # 实现流式对话逻辑
            logger.info(f"开始流式对话，使用 {len(self.tools)} 个工具")
            has_tool_calls = False  # 标记是否有工具调用
            
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
                    has_tool_calls = True
                    tool_name = chunk.get("name", "")
                    tool_input = chunk.get("data", {}).get("input", {})
                    logger.info(f"✅ 工具调用开始: {tool_name}, 参数: {tool_input}")
                    
                    # 添加工具调用到历史记录（结果暂时为 None）
                    self.history.add_tool_call(tool_name, tool_input, result=None)
                
                elif event_type == "on_tool_end":
                    tool_name = chunk.get("name", "")
                    tool_output = chunk.get("data", {}).get("output")
                    logger.info(f"✅ 工具调用结束: {tool_name}, 结果长度={len(str(tool_output))}")
                    
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
            
            # 诊断日志
            if not has_tool_calls:
                logger.warning("⚠️ 本次对话没有触发任何工具调用！如果应该调用工具但没有调用，请检查：")
                logger.warning("  1. 模型是否支持 function calling（建议使用 GPT-4、Claude 3.5、Gemini 1.5 等）")
                logger.warning("  2. API 配置是否正确")
                logger.warning("  3. 模型是否被正确绑定了工具")
                
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

