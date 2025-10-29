"""
Civitai 相关工具函数。

提供 AIR (Artificial Intelligence Resources) 标识符的合成和解析功能。

概念说明：
- Ecosystem（生态系统）：SD1, SD2, SDXL 等技术代际
- BaseModel（基础模型）：Pony, Illustrious 等具体基础模型
- AIR 标识符使用 ecosystem，不使用 base_model
"""
import re
from typing import Optional, Tuple
from dataclasses import dataclass

from constants.model_meta import ModelType, Ecosystem


@dataclass
class AirIdentifier:
    """
    AIR 标识符解析结果。
    
    格式：urn:air:{ecosystem}:{type}:civitai:{model_id}@{version_id}
    
    示例：
    - urn:air:sd1:checkpoint:civitai:348620@390021
    - urn:air:sdxl:lora:civitai:328553@368189
    """
    ecosystem: str  # sd1, sd2, sdxl 等
    type: str  # checkpoint, lora, vae
    model_id: int
    version_id: int
    
    def to_air(self) -> str:
        """
        合成 AIR 标识符字符串。
        
        :return: AIR 标识符字符串
        """

        return f"urn:air:{self.ecosystem}:{self.type}:civitai:{self.model_id}@{self.version_id}"

    
    def __str__(self) -> str:
        """字符串表示形式"""
        return self.to_air()


def parse_air(air_str: str) -> Optional[AirIdentifier]:
    """
    解析 AIR 标识符字符串。
    
    格式：urn:air:{ecosystem}:{type}:civitai:{model_id}@{version_id}
    
    :param air_str: AIR 标识符字符串
    :return: AirIdentifier 对象，解析失败返回 None
    
    示例：
    >>> air = parse_air("urn:air:sd1:checkpoint:civitai:348620@390021")
    >>> air.model_id
    348620
    >>> air.version_id
    390021
    """
    if not air_str:
        return None
    
    # 解析 AIR 格式
    # urn:air:{ecosystem}:{type}:civitai:{model_id}@{version_id}
    pattern = r'^urn:air:([\w]+):([\w]+):civitai:(\d+)(?:@(\d+))?$'
    match = re.match(pattern, air_str.strip())
    
    if not match:
        return None
    
    ecosystem = match.group(1)
    type_str = match.group(2)
    model_id = int(match.group(3))
    version_id = int(match.group(4)) if match.group(4) else None
    
    return AirIdentifier(
        ecosystem=ecosystem,
        type=type_str,
        model_id=model_id,
        version_id=version_id,
    )


def create_air(
    ecosystem: str,
    type_str: str,
    model_id: int,
    version_id: int,
) -> str:
    """
    创建 AIR 标识符字符串。
    
    :param ecosystem: 生态系统（sd1, sd2, sdxl 等）
    :param type_str: 模型类型（checkpoint, lora, vae）
    :param model_id: Civitai 模型 ID
    :param version_id: Civitai 模型版本 ID（可选）
    :return: AIR 标识符字符串
    
    示例：
    >>> create_air("sd1", "checkpoint", 348620, 390021)
    'urn:air:sd1:checkpoint:civitai:348620@390021'
    >>> create_air("sdxl", "lora", 328553)
    'urn:air:sdxl:lora:civitai:328553'
    """
    air = AirIdentifier(
        ecosystem=ecosystem.lower(),
        type=type_str.lower(),
        model_id=model_id,
        version_id=version_id,
    )
    return air.to_air()


def parse_air_ids(air_str: str) -> Optional[Tuple[int, Optional[int]]]:
    """
    快速解析 AIR 标识符中的 model_id 和 version_id。
    
    :param air_str: AIR 标识符字符串
    :return: (model_id, version_id) 元组，解析失败返回 None
    
    示例：
    >>> parse_air_ids("urn:air:sd1:checkpoint:civitai:348620@390021")
    (348620, 390021)
    >>> parse_air_ids("urn:air:sdxl:lora:civitai:328553")
    (328553, None)
    """
    air = parse_air(air_str)
    if air is None:
        return None
    return (air.model_id, air.version_id)


def normalize_ecosystem(ecosystem: str) -> str:
    """
    规范化 ecosystem 名称。
    
    :param ecosystem: 原始 ecosystem 名称
    :return: 规范化后的名称
    
    示例：
    >>> normalize_ecosystem("SD 1.5")
    'sd1'
    >>> normalize_ecosystem("SDXL 1.0")
    'sdxl'
    >>> normalize_ecosystem("SD 2.0")
    'sd2'
    """
    ecosystem_lower = ecosystem.lower().strip()
    
    # 规范化映射表（使用常量）
    normalization_map = {
        "sd 1.5": Ecosystem.SD1,
        "sd1.5": Ecosystem.SD1,
        "sd 1": Ecosystem.SD1,
        "sd 2.0": Ecosystem.SD2,
        "sd2.0": Ecosystem.SD2,
        "sd 2": Ecosystem.SD2,
        "sdxl 1.0": Ecosystem.SDXL,
        "sdxl1.0": Ecosystem.SDXL,
        "sdxl 1": Ecosystem.SDXL,
    }
    
    # 尝试映射
    normalized = normalization_map.get(ecosystem_lower)
    if normalized:
        return normalized
    
    # 如果没有映射，直接返回小写版本
    return ecosystem_lower


def normalize_type(type_str: str) -> str:
    """
    规范化模型类型名称。
    
    :param type_str: 原始类型名称
    :return: 规范化后的类型名称
    
    示例：
    >>> normalize_type("Checkpoint")
    'checkpoint'
    >>> normalize_type("LORA")
    'lora'
    >>> normalize_type("VAE")
    'vae'
    """
    type_lower = type_str.lower().strip()
    
    # 规范化映射表（使用常量）
    normalization_map = {
        "lora": ModelType.LORA,
        "locon": ModelType.LORA,  # LoRA 的变种
        "lycoris": ModelType.LORA,  # LoRA 的变种
        "checkpoint": ModelType.CHECKPOINT,
        "model": ModelType.CHECKPOINT,
        "vae": ModelType.VAE,
    }
    
    # 尝试映射
    normalized = normalization_map.get(type_lower)
    if normalized:
        return normalized
    
    # 如果没有映射，直接返回小写版本
    return type_lower

