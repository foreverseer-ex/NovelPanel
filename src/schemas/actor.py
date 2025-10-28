"""
角色相关的数据模型。

简化设计：角色只包含基本信息和标签字典。
标签的键名定义在 constants/actor.py 中。
"""
from sqlalchemy import Column, JSON
from sqlalchemy.ext.mutable import MutableDict
from sqlmodel import SQLModel, Field


class Character(SQLModel, table=True):
    """
    角色设定 - 简化的键值对存储。
    
    标签（tags）是一个字典，用于存储角色的各种属性：
    - 建议使用 constants.actor.character_tags_description 中定义的键
    - 所有值都是纯文本字符串
    - 列表类型使用逗号分隔
    """
    character_id: str = Field(description="角色唯一标识", primary_key=True)
    session_id: str = Field(description="所属会话ID", index=True)
    name: str = Field(description="角色名称", index=True)
    tags: dict[str, str] = Field(default_factory=dict,
                                 sa_column=Column(MutableDict.as_mutable(JSON())),
                                 description="角色标签字典，键建议使用 constants.actor 中定义的标签")
