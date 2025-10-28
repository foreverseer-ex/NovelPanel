"""
会话相关的数据模型。

每次小说转漫画任务都是一个会话，包含项目配置、进度状态等信息。
"""
from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field


class Session(SQLModel, table=True):
    """会话主体。"""
    session_id: str = Field(description="会话唯一标识", primary_key=True)
    title: str = Field(description="项目标题", index=True)
    novel_path: Optional[str] = Field(default=None, description="小说文件路径")
    project_path: str = Field(description="项目存储路径")
    
    # 小说元数据
    author: Optional[str] = Field(default=None, description="小说作者")
    total_lines: int = Field(default=0, ge=0, description="小说总行数（段落数）")
    total_chapters: int = Field(default=0, ge=0, description="小说总章节数")
    current_line: int = Field(default=0, description="当前处理段落")
    current_chapter: int = Field(default=0, description="当前处理章节", index=True)
    
    # 状态和时间
    status: str = Field(default='created', description="会话状态", index=True)
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新时间")
