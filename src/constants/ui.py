"""UI 响应式常量与字体体系。

兼容旧用法：保留与 `ui_size.py` 相同名的默认常量（取 md 断点），
并提供响应式映射与选择器以便按窗口宽度自适应。
"""

# ==================== 响应式断点 ====================

# 断点定义（单位：px）
BREAKPOINTS = {
    "xs": 0,        # < 480
    "sm": 480,     # 480 - 767
    "md": 768,     # 768 - 1023
    "lg": 1024,    # 1024 - 1439
    "xl": 1440,    # >= 1440
}


def get_scale(window_width: int) -> str:
    """根据窗口宽度返回断点标识。"""
    if window_width >= BREAKPOINTS["xl"]:
        return "xl"
    if window_width >= BREAKPOINTS["lg"]:
        return "lg"
    if window_width >= BREAKPOINTS["md"]:
        return "md"
    if window_width >= BREAKPOINTS["sm"]:
        return "sm"
    return "xs"


def pick(mapping: dict, window_width: int) -> int | float:
    """从响应式映射中按窗口宽度选择值。"""
    return mapping.get(get_scale(window_width))


# ==================== 图片尺寸 ====================

THUMBNAIL_WIDTH_MAP = {"xs": 140, "sm": 180, "md": 240, "lg": 260, "xl": 280}
THUMBNAIL_HEIGHT_MAP = {"xs": 140, "sm": 180, "md": 240, "lg": 260, "xl": 280}

LARGE_IMAGE_WIDTH_MAP = {"xs": 480, "sm": 600, "md": 720, "lg": 840, "xl": 960}
LARGE_IMAGE_HEIGHT_MAP = {"xs": 480, "sm": 600, "md": 720, "lg": 840, "xl": 960}

IMAGE_BORDER_RADIUS_MAP = {"xs": 6, "sm": 6, "md": 8, "lg": 10, "xl": 12}


# ==================== 对话框尺寸 ====================

DIALOG_STANDARD_WIDTH_MAP = {"xs": 360, "sm": 420, "md": 500, "lg": 560, "xl": 640}
DIALOG_STANDARD_HEIGHT_MAP = {"xs": 480, "sm": 560, "md": 600, "lg": 680, "xl": 760}

DIALOG_WIDE_WIDTH_MAP = {"xs": 720, "sm": 960, "md": 1200, "lg": 1320, "xl": 1440}
DIALOG_WIDE_HEIGHT_MAP = {"xs": 720, "sm": 960, "md": 1200, "lg": 1320, "xl": 1440}


# ==================== 间距系统 ====================

SPACING_SMALL_MAP = {"xs": 6, "sm": 8, "md": 8, "lg": 10, "xl": 12}
SPACING_MEDIUM_MAP = {"xs": 10, "sm": 12, "md": 15, "lg": 18, "xl": 20}
SPACING_LARGE_MAP = {"xs": 14, "sm": 16, "md": 20, "lg": 24, "xl": 28}


# ==================== Loading 尺寸 ====================

LOADING_SIZE_SMALL_MAP = {"xs": 16, "sm": 18, "md": 20, "lg": 24, "xl": 28}
LOADING_SIZE_MEDIUM_MAP = {"xs": 22, "sm": 24, "md": 30, "lg": 34, "xl": 36}
LOADING_SIZE_LARGE_MAP = {"xs": 28, "sm": 32, "md": 40, "lg": 44, "xl": 48}


# ==================== Chip 标签样式 ====================

CHIP_PADDING_H_MAP = {"xs": 6, "sm": 6, "md": 8, "lg": 10, "xl": 12}
CHIP_PADDING_V_MAP = {"xs": 3, "sm": 3, "md": 4, "lg": 5, "xl": 6}
CHIP_BORDER_RADIUS_MAP = {"xs": 10, "sm": 10, "md": 12, "lg": 12, "xl": 14}
CHIP_BORDER_WIDTH_MAP = {"xs": 1, "sm": 1, "md": 1, "lg": 1, "xl": 1}
CHIP_TEXT_SIZE_MAP = {"xs": 10, "sm": 10, "md": 11, "lg": 12, "xl": 12}


# ==================== 网格列配置 ====================

GRID_COL_4 = {"xs": 12, "sm": 6, "md": 4, "lg": 3, "xl": 3}
GRID_COL_3 = {"xs": 12, "sm": 6, "md": 4, "lg": 4, "xl": 4}


# ==================== 卡片与详情 ====================

CARD_WIDTH_MAP = {"xs": 180, "sm": 200, "md": 240, "lg": 260, "xl": 280}
CARD_HEIGHT_MAP = {"xs": 260, "sm": 290, "md": 320, "lg": 340, "xl": 360}
CARD_INFO_HEIGHT_MAP = {"xs": 110, "sm": 120, "md": 130, "lg": 140, "xl": 150}
CARD_TITLE_HEIGHT_MAP = {"xs": 40, "sm": 45, "md": 50, "lg": 54, "xl": 56}
CARD_TITLE_MAX_LINES = 2

DETAIL_LABEL_WIDTH_MAP = {"xs": 80, "sm": 90, "md": 100, "lg": 110, "xl": 120}
DETAIL_INFO_MIN_WIDTH_MAP = {"xs": 260, "sm": 300, "md": 350, "lg": 380, "xl": 420}


# ==================== 字体体系（响应式） ====================

# 语义层级：display > title > subtitle > body > caption
FONT_DISPLAY_MAP = {"xs": 24, "sm": 28, "md": 32, "lg": 36, "xl": 40}
FONT_TITLE_MAP = {"xs": 18, "sm": 20, "md": 22, "lg": 24, "xl": 26}
FONT_SUBTITLE_MAP = {"xs": 14, "sm": 15, "md": 16, "lg": 17, "xl": 18}
FONT_BODY_MAP = {"xs": 12, "sm": 12, "md": 13, "lg": 14, "xl": 14}
FONT_CAPTION_MAP = {"xs": 10, "sm": 10, "md": 11, "lg": 12, "xl": 12}

# 字重定义（如框架不支持可在组件处映射）
FONT_WEIGHT = {
    "regular": 400,
    "medium": 500,
    "semibold": 600,
    "bold": 700,
}


# ==================== 向后兼容（md 默认值） ====================

THUMBNAIL_WIDTH = THUMBNAIL_WIDTH_MAP["md"]
THUMBNAIL_HEIGHT = THUMBNAIL_HEIGHT_MAP["md"]
LARGE_IMAGE_WIDTH = LARGE_IMAGE_WIDTH_MAP["md"]
LARGE_IMAGE_HEIGHT = LARGE_IMAGE_HEIGHT_MAP["md"]
IMAGE_BORDER_RADIUS = IMAGE_BORDER_RADIUS_MAP["md"]

DIALOG_STANDARD_WIDTH = DIALOG_STANDARD_WIDTH_MAP["md"]
DIALOG_STANDARD_HEIGHT = DIALOG_STANDARD_HEIGHT_MAP["md"]
DIALOG_WIDE_WIDTH = DIALOG_WIDE_WIDTH_MAP["md"]
DIALOG_WIDE_HEIGHT = DIALOG_WIDE_HEIGHT_MAP["md"]

SPACING_SMALL = SPACING_SMALL_MAP["md"]
SPACING_MEDIUM = SPACING_MEDIUM_MAP["md"]
SPACING_LARGE = SPACING_LARGE_MAP["md"]

LOADING_SIZE_SMALL = LOADING_SIZE_SMALL_MAP["md"]
LOADING_SIZE_MEDIUM = LOADING_SIZE_MEDIUM_MAP["md"]
LOADING_SIZE_LARGE = LOADING_SIZE_LARGE_MAP["md"]

CHIP_PADDING_H = CHIP_PADDING_H_MAP["md"]
CHIP_PADDING_V = CHIP_PADDING_V_MAP["md"]
CHIP_BORDER_RADIUS = CHIP_BORDER_RADIUS_MAP["md"]
CHIP_BORDER_WIDTH = CHIP_BORDER_WIDTH_MAP["md"]
CHIP_TEXT_SIZE = CHIP_TEXT_SIZE_MAP["md"]

CARD_WIDTH = CARD_WIDTH_MAP["md"]
CARD_HEIGHT = CARD_HEIGHT_MAP["md"]
CARD_INFO_HEIGHT = CARD_INFO_HEIGHT_MAP["md"]
CARD_TITLE_HEIGHT = CARD_TITLE_HEIGHT_MAP["md"]

DETAIL_LABEL_WIDTH = DETAIL_LABEL_WIDTH_MAP["md"]
DETAIL_INFO_MIN_WIDTH = DETAIL_INFO_MIN_WIDTH_MAP["md"]

# 字体默认（md）
FONT_DISPLAY = FONT_DISPLAY_MAP["md"]
FONT_TITLE = FONT_TITLE_MAP["md"]
FONT_SUBTITLE = FONT_SUBTITLE_MAP["md"]
FONT_BODY = FONT_BODY_MAP["md"]
FONT_CAPTION = FONT_CAPTION_MAP["md"]


