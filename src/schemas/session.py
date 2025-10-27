"""
会话相关的数据模型。

每次小说转漫画任务都是一个会话，包含项目配置、进度状态等信息。
"""
from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel, Field, computed_field


class DependsConfig(BaseModel):
    """依赖配置。"""
    sd_backend_url: str = Field(description="SD后端地址")
    llm_backend_url: Optional[str] = Field(default=None, description="LLM后端地址")


class NovelInfo(BaseModel):
    """小说信息。"""

    # 小说元数据（来自原 NovelMetadata）
    author: Optional[str] = Field(default=None, description="小说作者")
    total_lines: int = Field(default=0, ge=0, description="小说总行数（段落数）")
    total_chapters: int = Field(default=0, ge=0, description="小说总章节数")
    current_line: int = Field(default=0, description="当前处理段落")
    current_chapter: int = Field(default=0, description="当前处理章节")

    @computed_field(description="当前进度百分比")
    @property
    def progress(self) -> float:
        """计算当前进度百分比。"""
        if self.total_lines == 0:
            return 0.0
        return self.current_line / self.total_lines


class Session(BaseModel):
    """会话主体。"""
    session_id: str = Field(description="会话唯一标识")
    title: str = Field(description="项目标题")
    novel_path: Optional[str] = Field(default=None, description="小说文件路径")
    project_path: str = Field(description="项目存储路径")

    depends: DependsConfig = Field(description="依赖配置")
    novel: NovelInfo = Field(description="小说信息")
    status: Literal['created', 'analyzing', 'generating', 'selecting', 'composing', 'completed', 'failed'] = Field(
        description="会话状态")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新时间")
