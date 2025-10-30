"""
Actor 相关的数据模型。

Actor 不仅指角色，也指小说中出现的要素（如国家、组织等）。
每个 Actor 可以有多个示例图（立绘）。
"""
from pydantic import BaseModel, ConfigDict
from sqlalchemy import Column, JSON
from sqlalchemy.ext.mutable import MutableDict, MutableList
from sqlmodel import SQLModel, Field
from .draw import DrawArgs


class ActorExample(BaseModel):
    """Actor 的示例图（立绘）。
    
    每个示例包含：
    - title: 示例标题/名称
    - desc: 示例说明
    - draw_args: 生成参数
    - image_path: 图片相对路径（相对于项目根目录）
    """
    title: str = Field(description="示例标题")
    desc: str = Field(description="示例说明")
    draw_args: DrawArgs = Field(description="生成参数")
    image_path: str = Field(description="图片相对路径")
    
    model_config = ConfigDict(
        arbitrary_types_allowed=True
    )


class Actor(SQLModel, table=True):
    """
    Actor 设定 - 包含基本信息、标签和示例图。
    
    Actor 可以是：
    - 角色（如主角、配角）
    - 地点（如城市、国家）
    - 组织（如帝国、公司）
    - 其他小说要素
    
    字段说明：
    - actor_id: 唯一标识
    - session_id: 所属会话
    - name: 名称
    - desc: 基本描述
    - color: 卡片颜色（用于 UI 展示，如 #FF69B4）
    - tags: 标签字典（键建议使用 constants.actor 中定义的标签）
    - examples: 示例图列表（立绘）
    """
    actor_id: str = Field(description="Actor 唯一标识", primary_key=True)
    session_id: str = Field(description="所属会话ID", index=True)
    name: str = Field(description="名称", index=True)
    desc: str = Field(default="", description="基本描述")
    color: str = Field(default="#808080", description="卡片颜色（如 #FF69B4）")
    tags: dict[str, str] = Field(default_factory=dict,
                                 sa_column=Column(MutableDict.as_mutable(JSON())),
                                 description="标签字典，键建议使用 constants.actor 中定义的标签")
    examples: list[dict] = Field(default_factory=list,
                                 sa_column=Column(MutableList.as_mutable(JSON())),
                                 description="示例图列表（序列化的 ActorExample）")
