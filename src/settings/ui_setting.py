"""
UI 设置
"""
import socket
from typing import Optional
from pydantic import BaseModel, Field


class UiSettings(BaseModel):
    """UI 设置项。
    
    包含模型管理页面等 UI 的筛选与显示相关选项。
    """
    # 用户设置
    default_username: str = Field(
        default_factory=socket.gethostname,
        description="默认用户名（默认为计算机名）"
    )
    
    # 会话管理
    current_session_id: Optional[str] = Field(
        default=None,
        description="当前选中的会话 ID"
    )
    
    # 模型管理
    ecosystem_filter: Optional[str] = Field(
        default=None,
        description="生态系统过滤器（None 表示显示所有模型）。可选值：sd1, sd2, sdxl"
    )
    
    base_model_filter: Optional[str] = Field(
        default=None,
        description="基础模型过滤器（None 表示显示所有模型）。可选值：pony, illustrious, standard 等"
    )
    
    # 创作页面
    draft_message: str = Field(
        default="",
        description="创作页面输入框的草稿内容（自动保存）"
    )
    
    # 隐私模式
    privacy_mode: bool = Field(
        default=True,
        description="隐私模式：启用时，模型卡的预览图默认不显示"
    )
