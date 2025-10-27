"""
角色相关的数据模型。

包含角色设定、外貌描述、一致性标签等。
"""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class CharacterAppearance(BaseModel):
    """角色外貌描述。"""
    gender: Optional[str] = Field(default=None, description="性别")
    age_range: Optional[str] = Field(default=None, description="年龄段")
    height: Optional[str] = Field(default=None, description="身高描述")
    build: Optional[str] = Field(default=None, description="体型")
    hair: Optional[str] = Field(default=None, description="发型发色")
    eyes: Optional[str] = Field(default=None, description="眼睛特征")
    face: Optional[str] = Field(default=None, description="面部特征")
    clothing: Optional[str] = Field(default=None, description="常见服饰")
    distinctive_features: List[str] = Field(default_factory=list, description="显著特征")


class Character(BaseModel):
    """角色设定。"""
    character_id: str = Field(description="角色唯一标识")
    name: str = Field(description="角色名称")
    aliases: List[str] = Field(default_factory=list, description="别名/称呼")
    role: Optional[str] = Field(default=None, description="角色定位（主角/配角等）")
    personality: Optional[str] = Field(default=None, description="性格描述")
    appearance: CharacterAppearance = Field(description="外貌描述")
    background: Optional[str] = Field(default=None, description="背景故事")
    relationships: Dict[str, str] = Field(default_factory=dict, description="与其他角色的关系")
    sd_tags: List[str] = Field(default_factory=list, description="SD提示词标签（用于一致性）")
    reference_images: List[str] = Field(default_factory=list, description="参考图路径")
    first_appearance: Optional[str] = Field(default=None, description="首次出现位置")


class SceneCharacter(BaseModel):
    """场景中的角色引用。"""
    character_id: str
    emotion: Optional[str] = Field(default=None, description="情绪状态")
    action: Optional[str] = Field(default=None, description="动作描述")
    position: Optional[str] = Field(default=None, description="位置描述")

