"""
LLM (大语言模型) 服务。

提供 AI Agent 功能，自动调用 NovelPanel 的各种工具完成任务。
"""
from typing import List, Optional, AsyncIterator, Dict, Any
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from loguru import logger

from settings.app_setting import app_settings

# 从 routers 导入所有函数（排除 file）
from routers.session import (
    create_session,
    get_session,
    list_sessions,
    update_session,
    delete_session,
    update_session_status,
    update_progress,
)
from routers.actor import (
    create_actor,
    get_actor,
    list_actors,
    update_actor,
    remove_actor,
    get_tag_description,
    get_all_tag_descriptions,
)
from routers.memory import (
    create_memory,
    get_memory,
    query_memories,
    update_memory,
    delete_memory,
    get_key_description,
    get_all_key_descriptions,
)
from routers.reader import (
    parse_novel,
    get_line,
    get_line_chapter_index,
    get_chapters,
    get_chapter,
    get_chapter_summary,
    put_chapter_summary,
)
from routers.draw import (
    get_loras,
    get_sd_models,
    get_options,
    set_options,
    generate,
    get_image,
)


class LlmService:
    """
    LLM 服务类。
    
    提供 AI Agent 功能，自动将用户的自然语言请求转换为对应的 API 调用。
    """
    
    def __init__(self):
        """初始化 LLM 服务。"""
        self.llm: Optional[ChatOpenAI] = None
        self.agent = None
        self.tools: List[Any] = []
        self._initialize_tools()
    
    def _initialize_tools(self):
        """初始化所有工具函数。"""
        # 将所有 router 函数包装为工具
        all_functions = [
            # Session 管理
            create_session,
            get_session,
            list_sessions,
            update_session,
            delete_session,
            update_session_status,
            update_progress,
            
            # Actor 管理
            create_actor,
            get_actor,
            list_actors,
            update_actor,
            remove_actor,
            get_tag_description,
            get_all_tag_descriptions,
            
            # Memory 管理
            create_memory,
            get_memory,
            query_memories,
            update_memory,
            delete_memory,
            get_key_description,
            get_all_key_descriptions,
            
            # Reader 功能
            parse_novel,
            get_line,
            get_line_chapter_index,
            get_chapters,
            get_chapter,
            get_chapter_summary,
            put_chapter_summary,
            
            # Draw 功能
            get_loras,
            get_sd_models,
            get_options,
            set_options,
            generate,
            get_image,
        ]
        
        # 包装为工具
        self.tools = [tool(func) for func in all_functions]
        
        logger.info(f"已初始化 {len(self.tools)} 个工具函数")
    
    def initialize_llm(self) -> bool:
        """
        初始化 LLM 客户端。
        
        :return: 是否初始化成功
        """
        try:
            # 从配置创建 LLM
            self.llm = ChatOpenAI(
                model=app_settings.llm.model,
                api_key=app_settings.llm.api_key,
                base_url=app_settings.llm.base_url,
                temperature=app_settings.llm.temperature,
            )
            
            # 绑定工具
            llm_with_tools = self.llm.bind_tools(self.tools)
            
            # 创建 Agent
            self.agent = create_agent(llm_with_tools, self.tools)
            
            logger.success(
                f"LLM 服务初始化成功: {app_settings.llm.model} "
                f"({len(self.tools)} 个工具)"
            )
            return True
            
        except Exception as e:
            logger.error(f"LLM 服务初始化失败: {e}")
            return False
    
    def is_ready(self) -> bool:
        """
        检查 LLM 服务是否就绪。
        
        :return: 是否已初始化并可用
        """
        return self.llm is not None and self.agent is not None
    
    async def chat(
        self,
        message: str,
        stream: bool = True,
    ) -> AsyncIterator[Dict[str, Any]]:
        """
        与 AI 对话。
        
        :param message: 用户消息
        :param stream: 是否使用流式输出
        :yield: 事件字典，包含 AI 响应、工具调用等信息
        
        事件类型：
        - ai_message: AI 的文本回复（流式）
        - tool_call: 工具调用开始
        - tool_result: 工具返回结果
        - final_answer: 最终完整回答
        - error: 错误信息
        """
        if not self.is_ready():
            if not self.initialize_llm():
                yield {
                    "type": "error",
                    "content": "LLM 服务未就绪，请检查配置"
                }
                return
        
        try:
            # 构建消息
            messages = [
                {"role": "system", "content": app_settings.llm.system_prompt},
                {"role": "user", "content": message}
            ]
            
            # 流式处理 Agent 事件
            async for event in self.agent.astream_events(
                {"messages": messages},
                version="v1"
            ):
                event_type = event["event"]
                
                # LLM 输出流
                if event_type == "on_chat_model_stream":
                    content = event["data"]["chunk"].content
                    if content:
                        yield {
                            "type": "ai_message",
                            "content": content
                        }
                
                # 工具调用开始
                elif event_type == "on_tool_start":
                    tool_name = event["name"]
                    tool_input = event["data"].get("input", {})
                    
                    yield {
                        "type": "tool_call",
                        "tool_name": tool_name,
                        "tool_input": tool_input
                    }
                    
                    # 开发者模式：显示详细信息
                    if app_settings.llm.developer_mode:
                        logger.debug(f"[工具调用] {tool_name}({tool_input})")
                
                # 工具返回
                elif event_type == "on_tool_end":
                    output = event["data"]["output"]
                    
                    yield {
                        "type": "tool_result",
                        "content": output
                    }
                    
                    # 开发者模式：显示返回值
                    if app_settings.llm.developer_mode:
                        output_str = str(output)
                        if len(output_str) > 200:
                            logger.debug(f"[工具返回] {output_str[:200]}...")
                        else:
                            logger.debug(f"[工具返回] {output_str}")
                
                # 最终回答
                elif event_type == "on_chain_end":
                    output = event["data"]["output"]
                    if "messages" in output:
                        final = output["messages"][-1]
                        if hasattr(final, 'role') and final.role == "assistant":
                            if not hasattr(final, 'tool_calls') or not final.tool_calls:
                                yield {
                                    "type": "final_answer",
                                    "content": final.content
                                }
        
        except Exception as e:
            logger.error(f"对话处理失败: {e}")
            yield {
                "type": "error",
                "content": str(e)
            }
    
    async def simple_chat(self, message: str) -> str:
        """
        简化的对话接口，返回完整回复。
        
        :param message: 用户消息
        :return: AI 的完整回复
        """
        full_response = ""
        
        async for event in self.chat(message):
            if event["type"] == "ai_message":
                full_response += event["content"]
            elif event["type"] == "final_answer":
                # 如果有最终回答，使用最终回答
                return event["content"]
            elif event["type"] == "error":
                raise Exception(event["content"])
        
        return full_response
    
    def get_tool_list(self) -> List[Dict[str, str]]:
        """
        获取所有可用工具的列表。
        
        :return: 工具列表，每项包含 name 和 description
        """
        return [
            {
                "name": t.name,
                "description": t.description
            }
            for t in self.tools
        ]
    
    def reload_config(self):
        """
        重新加载配置并重新初始化 LLM。
        
        用于配置更新后刷新服务。
        """
        logger.info("重新加载 LLM 配置...")
        self.llm = None
        self.agent = None
        self.initialize_llm()


# 全局 LLM 服务实例
llm_service = LlmService()

