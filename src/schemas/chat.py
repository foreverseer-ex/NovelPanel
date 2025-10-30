"""
聊天相关的数据模型。
"""
import uuid
from typing import Literal, Union
from pydantic import BaseModel, Field, ConfigDict


# ============ 消息内容类型 ============

class TextMessage(BaseModel):
    """文本消息"""
    type: Literal["text"] = "text"
    content: str = Field(description="文本内容")


class ToolCall(BaseModel):
    """工具调用"""
    type: Literal["tool_call"] = "tool_call"
    tool_name: str = Field(description="工具名称")
    arguments: dict = Field(default_factory=dict, description="工具参数")
    result: str | None = Field(default=None, description="工具执行结果")


# 消息内容联合类型
MessageContent = Union[TextMessage, ToolCall]


# ============ 选项类型 ============

class ImageChoice(BaseModel):
    """图像选项（用于图片生成后的选择）"""
    type: Literal["image"] = "image"
    url: str = Field(description="图像 URL")
    label: str | None = Field(default=None, description="图像标签")
    metadata: dict = Field(default_factory=dict, description="图像元数据（如生成参数）")


class TextChoice(BaseModel):
    """文字选项（用于快捷回复）"""
    type: Literal["text"] = "text"
    text: str = Field(description="选项文本")
    label: str = Field(description="选项显示标签")


# 选项联合类型
Choice = Union[ImageChoice, TextChoice]


# ============ 聊天消息 ============

class ChatMessage(BaseModel):
    """聊天消息模型（支持多种内容类型和选项）"""
    
    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="消息唯一标识符（UUID）"
    )
    
    role: Literal["system", "user", "assistant"] = Field(
        description="消息角色：system（系统）、user（用户）、assistant（助手）"
    )
    
    messages: list[MessageContent] = Field(
        default_factory=list,
        description="消息内容列表，可包含文本和工具调用"
    )
    
    choices: list[Choice] | None = Field(
        default=None,
        description="可选的选项列表（图像选项或文字选项）"
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "id": "550e8400-e29b-41d4-a716-446655440000",
                    "role": "user",
                    "messages": [{"type": "text", "content": "你好，请帮我分析这段小说"}],
                    "choices": None
                },
                {
                    "id": "6ba7b810-9dad-11d1-80b4-00c04fd430c8",
                    "role": "assistant",
                    "messages": [
                        {"type": "text", "content": "好的，我来帮您生成一张插图"},
                        {"type": "tool_call", "tool_name": "generate", "arguments": {"prompt": "a girl"}, "result": "job_123"}
                    ],
                    "choices": [
                        {"type": "image", "url": "http://...", "label": "图片1"},
                        {"type": "image", "url": "http://...", "label": "图片2"}
                    ]
                }
            ]
        }
    )


class ChatHistory(BaseModel):
    """聊天历史记录"""
    
    messages: list[ChatMessage] = Field(
        default_factory=list,
        description="消息列表"
    )
    
    def add_message(
        self, 
        role: Literal["system", "user", "assistant"], 
        content: str | None = None,
        message_content: MessageContent | None = None
    ):
        """
        添加消息到历史记录。
        
        :param role: 消息角色
        :param content: 文本内容（简化方式）
        :param message_content: 消息内容对象（高级方式）
        """
        # 如果已存在同 role 的消息，追加到该消息的 messages 列表
        if self.messages and self.messages[-1].role == role:
            if content is not None:
                self.messages[-1].messages.append(TextMessage(content=content))
            elif message_content is not None:
                self.messages[-1].messages.append(message_content)
        else:
            # 创建新消息
            messages_list = []
            if content is not None:
                messages_list.append(TextMessage(content=content))
            elif message_content is not None:
                messages_list.append(message_content)
            
            new_message = ChatMessage(role=role, messages=messages_list)
            self.messages = self.messages + [new_message]
    
    def add_tool_call(self, tool_name: str, arguments: dict, result: str | None = None):
        """
        添加工具调用到最后一条助手消息。
        
        :param tool_name: 工具名称
        :param arguments: 工具参数
        :param result: 工具执行结果
        """
        tool_call = ToolCall(tool_name=tool_name, arguments=arguments, result=result)
        
        # 如果最后一条是 assistant 消息，追加工具调用
        if self.messages and self.messages[-1].role == "assistant":
            self.messages[-1].messages.append(tool_call)
        else:
            # 否则创建新的 assistant 消息
            new_message = ChatMessage(role="assistant", messages=[tool_call])
            self.messages = self.messages + [new_message]
    
    def add_choices(self, choices: list[Choice]):
        """
        为最后一条助手消息添加选项。
        
        :param choices: 选项列表
        """
        if self.messages and self.messages[-1].role == "assistant":
            self.messages[-1].choices = choices
    
    def clear(self):
        """清空历史记录"""
        self.messages = []
    
    def get_messages_for_llm(self) -> list[tuple[str, str]]:
        """
        获取适用于 LLM 的消息格式（扁平化文本内容）。
        
        :return: [(role, message), ...] 格式的消息列表
        """
        result = []
        for msg in self.messages:
            # 合并所有文本消息内容
            text_parts = []
            for content in msg.messages:
                if isinstance(content, TextMessage):
                    text_parts.append(content.content)
                elif isinstance(content, ToolCall):
                    # 工具调用也转换为文本描述
                    tool_desc = f"[调用工具: {content.tool_name}]"
                    if content.result:
                        tool_desc += f" → {content.result}"
                    text_parts.append(tool_desc)
            
            if text_parts:
                combined_text = "\n".join(text_parts)
                result.append((msg.role, combined_text))
        
        return result
    
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "messages": [
                        {
                            "id": "a1b2c3d4-e5f6-4789-0abc-def123456789",
                            "role": "user", 
                            "messages": [{"type": "text", "content": "你好"}],
                            "choices": None
                        },
                        {
                            "id": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
                            "role": "assistant", 
                            "messages": [{"type": "text", "content": "你好！我是 NovelPanel AI 助手"}],
                            "choices": None
                        }
                    ]
                }
            ]
        }
    )

