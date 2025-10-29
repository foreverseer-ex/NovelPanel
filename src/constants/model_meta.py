"""
模型元数据相关常量定义。

定义了模型类型、生态系统、基础模型等常量，用于统一管理，避免硬编码。

概念说明：
- Ecosystem（生态系统）：SD1, SD2, SDXL 等大的技术代际
- BaseModel（基础模型）：Pony, Illustrious 等具体的基础模型
- ModelType（模型类型）：Checkpoint, LoRA, VAE 等
"""


class ModelType:
    """模型类型常量"""
    CHECKPOINT = "checkpoint"
    LORA = "lora"
    VAE = "vae"


class Ecosystem:
    """生态系统常量（技术代际）"""
    SD1 = "sd1"
    SD2 = "sd2"
    SDXL = "sdxl"


class BaseModel:
    """基础模型常量（具体的基础模型）"""
    # SDXL 系列
    PONY = "Pony"
    ILLUSTRIOUS = "Illustrious"
    NOOBAI = "NoobAI"
    SDXL_1_0 = "SDXL 1.0"
    
    # SD 1.5 系列
    SD_1_5 = "SD 1.5"
    
    # 可以根据需要添加更多基础模型


