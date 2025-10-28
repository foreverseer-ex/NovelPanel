"""
记忆系统相关的数据模型。

用于存储背景设定、世界观、用户偏好、章节信息等上下文信息。
键值对设计，所有配置通过 MemoryEntry 存储，键名定义在 constants/memory.py 中。

所有 value 统一使用纯文本字符串，不使用 JSON 格式。
对于列表类型的数据（如标签列表），使用逗号分隔的字符串存储，例如 "tag1, tag2, tag3"。
"""
from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field


class MemoryEntry(SQLModel, table=True):
    """
    记忆条目 - 简化的键值对存储。
    
    常见的 key 类型：
    - 世界观设定：使用 constants.memory.novel_memory_description 中定义的中文键
      如：'作品类型'、'主题'、'背景设定'、'主要地点'、'故事梗概'
    - 用户偏好：使用 constants.memory.user_memory_description 中定义的中文键
      如：'艺术风格'、'避免的标签'、'喜欢的标签'、'补充说明'、'其他偏好'
    - 章节信息：通过 ChapterSummary 专门处理
    - 其他：自定义 key，如重要情节、角色笔记、用户反馈等
    """
    memory_id: str = Field(description="记忆唯一标识", primary_key=True)
    session_id: str = Field(description="所属会话ID", index=True)
    key: str = Field(description="记忆键名（建议使用 constants.memory.memory_description 中定义的键）", index=True)
    value: str = Field(description="记忆值（纯文本字符串，列表类型使用逗号分隔）")
    description: Optional[str] = Field(default=None, description="键的描述（可从 constants.memory.memory_description 自动填充）")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class ChapterSummary(SQLModel, table=True):
    """
    章节摘要。
    
    用于存储章节的元数据和AI生成的梗概。
    小说按行解析，每行对应一个段落和一张图片。
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    session_id: str = Field(description="所属会话ID", index=True)
    chapter_index: int = Field(ge=0, description="章节索引（从0开始）", index=True)
    title: str = Field(description="章节标题")
    summary: Optional[str] = Field(default=None, description="章节故事梗概（AI生成）")
    start_line: int = Field(ge=0, description="起始行号")
    end_line: int = Field(ge=0, description="结束行号")

