"""
Civitai 相关工具函数。

提供 AIR (Artificial Intelligence Resources) 标识符的合成和解析功能。
"""
import re
from typing import Optional, Literal
from dataclasses import dataclass


def normalize_type(raw_type: str) -> Literal['checkpoint', 'lora', 'vae']:
    """
    规范化模型类型。
    
    将 Civitai 返回的各种类型名称转换为标准类型。
    
    :param raw_type: 原始类型字符串
    :return: 规范化后的类型
    
    示例：
    >>> normalize_type("LyCORIS")
    'lora'
    >>> normalize_type("Checkpoint")
    'checkpoint'
    """
    type_lower = raw_type.lower().strip()
    
    # LyCORIS/LoHA/LoKR 等都归类为 lora
    if type_lower in ('lycoris', 'locon', 'loha', 'lokr'):
        return 'lora'
    
    # 标准类型
    if type_lower in ('checkpoint', 'lora', 'vae'):
        return type_lower  # type: ignore
    
    # 默认返回 checkpoint（最常见的类型）
    return 'checkpoint'


@dataclass
class AIR:
    """
    AIR 标识符（Artificial Intelligence Resources）。
    
    格式：urn:air:{ecosystem}:{type}:civitai:{model_id}@{version_id}
    
    示例：
    - urn:air:sd1:checkpoint:civitai:348620@390021
    - urn:air:sdxl:lora:civitai:328553@368189
    """
    ecosystem: str  # sd1, sd2, sdxl
    type: str  # checkpoint, lora, vae
    model_id: int
    version_id: int
    
    def __str__(self) -> str:
        """转换为 AIR 标识符字符串"""
        return f"urn:air:{self.ecosystem}:{self.type}:civitai:{self.model_id}@{self.version_id}"
    
    @classmethod
    def parse(cls, air_str: str) -> Optional['AIR']:
        """
        从字符串解析 AIR 标识符。
        
        :param air_str: AIR 标识符字符串
        :return: AIR 对象，解析失败返回 None
        
        示例：
        >>> air = AIR.parse("urn:air:sd1:checkpoint:civitai:348620@390021")
        >>> air.model_id
        348620
        >>> air.version_id
        390021
        """
        if not air_str:
            return None
        
        # 解析格式：urn:air:{ecosystem}:{type}:civitai:{model_id}@{version_id}
        pattern = r'^urn:air:([\w]+):([\w]+):civitai:(\d+)@(\d+)$'
        match = re.match(pattern, air_str.strip())
        
        if not match:
            return None
        
        return cls(
            ecosystem=match.group(1),
            type=match.group(2),
            model_id=int(match.group(3)),
            version_id=int(match.group(4)),
        )

