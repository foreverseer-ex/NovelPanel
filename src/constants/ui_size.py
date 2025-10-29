"""UI 尺寸常量定义。

只定义通用的、可复用的尺寸，避免过度设计。
"""

# ==================== 通用图片尺寸 ====================

# 缩略图/网格图（用于卡片预览、示例图网格等）
THUMBNAIL_WIDTH = 240
THUMBNAIL_HEIGHT = 240

# 大图预览（用于详情页、示例大图等）
LARGE_IMAGE_WIDTH = 800
LARGE_IMAGE_HEIGHT = 800

# 图片圆角
IMAGE_BORDER_RADIUS = 8


# ==================== 通用对话框尺寸 ====================

# 标准对话框（详情、表单等）
DIALOG_STANDARD_WIDTH = 500
DIALOG_STANDARD_HEIGHT = 600

# 宽对话框（图片网格、展示等）
DIALOG_WIDE_WIDTH = 1200
DIALOG_WIDE_HEIGHT = 1200


# ==================== 通用间距系统 ====================

SPACING_SMALL = 8      # 紧凑间距（chip、小元素）
SPACING_MEDIUM = 15    # 中等间距（网格、列表）
SPACING_LARGE = 20     # 宽松间距（区块）


# ==================== 通用 Loading 尺寸 ====================

LOADING_SIZE_SMALL = 20    # 小型 loading（缩略图）
LOADING_SIZE_MEDIUM = 30   # 中型 loading（网格）
LOADING_SIZE_LARGE = 40    # 大型 loading（大图）


# ==================== Chip 标签样式 ====================

CHIP_PADDING_H = 8           # 水平内边距
CHIP_PADDING_V = 4           # 垂直内边距
CHIP_BORDER_RADIUS = 12      # 圆角
CHIP_BORDER_WIDTH = 1        # 边框宽度
CHIP_TEXT_SIZE = 11          # 文字大小


# ==================== 响应式网格列配置 ====================

# 通用网格列配置（4列布局）
GRID_COL_4 = {"xs": 12, "sm": 6, "md": 4, "lg": 3}

# 通用网格列配置（3列布局）
GRID_COL_3 = {"xs": 12, "sm": 6, "md": 4}


# ==================== 特定组件配置 ====================

# 模型卡片（需要特殊高度控制）
CARD_INFO_HEIGHT = 130      # 卡片信息区域总高度
CARD_TITLE_HEIGHT = 50      # 标题区域固定高度
CARD_TITLE_MAX_LINES = 2    # 标题最多行数

# 详情页标签宽度
DETAIL_LABEL_WIDTH = 100

# 详情页右侧详情区域最小宽度（横向布局时）
DETAIL_INFO_MIN_WIDTH = 350

