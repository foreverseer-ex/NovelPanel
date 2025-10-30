"""
模型卡片颜色常量。

定义不同模型类型和基础模型的Chip颜色。
"""
import flet as ft


class ModelTypeChipColor:
    """模型类型的Chip颜色配置。"""
    CHECKPOINT = ft.Colors.BLUE_400
    LORA = ft.Colors.PURPLE_400
    VAE = ft.Colors.GREEN_400
    
    @classmethod
    def get(cls, model_type: str) -> str:
        """根据模型类型获取颜色。
        
        :param model_type: 模型类型
        :return: 颜色值
        """
        color_map = {
            'Checkpoint': cls.CHECKPOINT,
            'LORA': cls.LORA,
            'vae': cls.VAE,
        }
        return color_map.get(model_type, ft.Colors.GREY_400)


class BaseModelColor:
    """基础模型的Chip颜色配置。"""
    # SDXL 系列
    PONY = ft.Colors.PINK_400
    ILLUSTRIOUS = ft.Colors.CYAN_400
    NOOBAI = ft.Colors.PURPLE_300
    SDXL_1_0 = ft.Colors.BLUE_300
    
    # SD 1.5 系列
    SD_1_5 = ft.Colors.ORANGE_400
    
    @classmethod
    def get(cls, base_model: str) -> str:
        """根据基础模型获取颜色。
        
        :param base_model: 基础模型名称（如 "Pony", "Illustrious", "NoobAI" 等）
        :return: 颜色值
        """
        color_map = {
            'Pony': cls.PONY,
            'Illustrious': cls.ILLUSTRIOUS,
            'NoobAI': cls.NOOBAI,
            'SDXL 1.0': cls.SDXL_1_0,
            'SD 1.5': cls.SD_1_5,
        }
        return color_map.get(base_model, ft.Colors.GREY_400)


class ToolRouterColor:
    """工具调用路由的颜色配置。"""
    SESSION = ft.Colors.BLUE_700       # 会话管理 - 蓝色
    MEMORY = ft.Colors.PURPLE_700      # 记忆管理 - 紫色
    ACTOR = ft.Colors.PINK_700         # 角色管理 - 粉色
    READER = ft.Colors.TEAL_700        # 读取器 - 青色
    NOVEL = ft.Colors.CYAN_700         # 小说内容 - 青蓝色
    DRAW = ft.Colors.ORANGE_700        # 绘画 - 橙色
    LLM = ft.Colors.GREEN_700          # LLM 辅助 - 绿色
    FILE = ft.Colors.AMBER_700         # 文件 - 琥珀色
    ILLUSTRATION = ft.Colors.DEEP_PURPLE_700  # 立绘 - 深紫色
    DEFAULT = ft.Colors.GREY_700       # 默认 - 灰色
    
    @classmethod
    def get(cls, tool_name: str) -> str:
        """根据工具名称获取对应的路由颜色。
        
        通过工具名称的前缀判断所属路由分类。
        
        :param tool_name: 工具名称（如 "create_session", "get_memory" 等）
        :return: 颜色值
        """
        # Session 管理工具
        if any(tool_name.startswith(prefix) for prefix in ['create_session', 'get_session', 'list_sessions', 
                                                             'update_session', 'delete_session', 'update_progress']):
            return cls.SESSION
        
        # Memory 管理工具
        if any(tool_name.startswith(prefix) for prefix in ['create_memory', 'get_memory', 'list_memories', 
                                                             'update_memory', 'delete_memory', 'get_key_description', 
                                                             'get_all_key_descriptions']):
            return cls.MEMORY
        
        # Actor 管理工具
        if any(tool_name.startswith(prefix) for prefix in ['create_actor', 'get_actor', 'list_actors', 
                                                             'update_actor', 'remove_actor', 'get_tag_description', 
                                                             'get_all_tag_descriptions']):
            return cls.ACTOR
        
        # Reader 工具
        if any(tool_name.startswith(prefix) for prefix in ['get_line', 'get_chapter_lines', 'get_chapters', 
                                                             'get_chapter', 'get_chapter_summary', 'put_chapter_summary', 
                                                             'get_stats']):
            return cls.READER
        
        # Novel 内容管理工具
        if any(tool_name.startswith(prefix) for prefix in ['get_session_content', 'get_chapter_content', 
                                                             'get_line_content']):
            return cls.NOVEL
        
        # Draw 工具
        if any(tool_name.startswith(prefix) for prefix in ['get_loras', 'get_sd_models', 'get_options', 
                                                             'set_options', 'generate', 'get_image']):
            return cls.DRAW
        
        # LLM 辅助工具
        if any(tool_name.startswith(prefix) for prefix in ['add_choices', 'get_choices', 'clear_choices']):
            return cls.LLM
        
        # Illustration 工具
        if any(tool_name.startswith(prefix) for prefix in ['create_illustration', 'list_illustrations', 
                                                             'get_illustration', 'update_illustration', 
                                                             'delete_illustration']):
            return cls.ILLUSTRATION
        
        # File 工具
        if any(tool_name.startswith(prefix) for prefix in ['get_project_novel', 'get_illustration_image']):
            return cls.FILE
        
        # 默认颜色
        return cls.DEFAULT