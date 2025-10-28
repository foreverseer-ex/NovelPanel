"""
OpenAI LLM 服务实现。
从原 services.llm 迁移。
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
    LLM 服务类（OpenAI）。
    """

    def __init__(self):
        self.llm: Optional[ChatOpenAI] = None
        self.agent = None
        self.tools: List[Any] = []
        self._initialize_tools()

    def _initialize_tools(self):
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
        self.tools = [tool(func) for func in all_functions]
        logger.info(f"已初始化 {len(self.tools)} 个工具函数")

    def initialize_llm(self) -> bool:
        try:
            self.llm = ChatOpenAI(
                model=app_settings.llm.model,
                api_key=app_settings.llm.api_key,
                base_url=app_settings.llm.base_url,
                temperature=app_settings.llm.temperature,
            )
            llm_with_tools = self.llm.bind_tools(self.tools)
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
        return self.llm is not None and self.agent is not None

    async def chat(self, message: str, stream: bool = True) -> AsyncIterator[Dict[str, Any]]:
        if not self.is_ready():
            if not self.initialize_llm():
                yield {"type": "error", "content": "LLM 服务未就绪，请检查配置"}
                return
        try:
            messages = [
                {"role": "system", "content": app_settings.llm.system_prompt},
                {"role": "user", "content": message},
            ]
            async for event in self.agent.astream_events({"messages": messages}, version="v1"):
                event_type = event["event"]
                if event_type == "on_chat_model_stream":
                    content = event["data"]["chunk"].content
                    if content:
                        yield {"type": "ai_message", "content": content}
                elif event_type == "on_tool_start":
                    tool_name = event["name"]
                    tool_input = event["data"].get("input", {})
                    yield {"type": "tool_call", "tool_name": tool_name, "tool_input": tool_input}
                    if app_settings.llm.developer_mode:
                        logger.debug(f"[工具调用] {tool_name}({tool_input})")
                elif event_type == "on_tool_end":
                    output = event["data"]["output"]
                    yield {"type": "tool_result", "content": output}
                    if app_settings.llm.developer_mode:
                        output_str = str(output)
                        logger.debug(f"[工具返回] {output_str[:200]}..." if len(output_str) > 200 else f"[工具返回] {output_str}")
                elif event_type == "on_chain_end":
                    output = event["data"]["output"]
                    if "messages" in output:
                        final = output["messages"][-1]
                        if hasattr(final, 'role') and final.role == "assistant":
                            if not hasattr(final, 'tool_calls') or not final.tool_calls:
                                yield {"type": "final_answer", "content": final.content}
        except Exception as e:
            logger.error(f"对话处理失败: {e}")
            yield {"type": "error", "content": str(e)}

    async def simple_chat(self, message: str) -> str:
        full_response = ""
        async for event in self.chat(message):
            if event["type"] == "ai_message":
                full_response += event["content"]
            elif event["type"] == "final_answer":
                return event["content"]
            elif event["type"] == "error":
                raise Exception(event["content"])
        return full_response

    def get_tool_list(self) -> List[Dict[str, str]]:
        return [{"name": t.name, "description": t.description} for t in self.tools]

    def reload_config(self):
        logger.info("重新加载 LLM 配置...")
        self.llm = None
        self.agent = None
        self.initialize_llm()


llm_service = LlmService()
