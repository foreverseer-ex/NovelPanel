# UI 尺寸常量使用指南

## 概述

所有 UI 组件的尺寸配置已经抽象到 `src/constants/ui_size.py` 文件中，便于统一管理和调整。

## 文件结构

```
src/constants/
├── __init__.py           # 导出所有常量
├── ui_size.py           # UI 尺寸常量定义 ⭐
├── color.py             # 颜色常量
├── actor.py             # 角色标签常量
└── memory.py            # 记忆键常量
```

## 使用的文件

以下文件已更新使用尺寸常量：

### 1. 模型卡片 (`src/components/model_card/__init__.py`)
- ✅ 卡片预览图尺寸
- ✅ 卡片信息区域高度
- ✅ 标题尺寸和最大行数
- ✅ Chip 标签尺寸和间距
- ✅ 内边距和间距

### 2. 示例图片对话框 (`src/components/model_card/example_image_dialog.py`)
- ✅ 对话框尺寸
- ✅ 网格视图缩略图尺寸
- ✅ 网格间距
- ✅ 详情视图大图尺寸
- ✅ 参数显示文字大小

### 3. 模型详情对话框 (`src/components/model_card/model_detail_dialog.py`)
- ✅ 对话框尺寸
- ✅ 预览图尺寸
- ✅ 信息行间距
- ✅ 标签宽度

### 4. 模型管理页面 (`src/pages/model_manage_page.py`)
- ✅ 网格列配置
- ✅ 网格间距

## 常量分类

### 模型卡片相关

```python
CARD_PREVIEW_WIDTH = 260          # 预览图宽度
CARD_PREVIEW_HEIGHT = 180         # 预览图高度
CARD_INFO_HEIGHT = 130            # 信息区域总高度
CARD_TITLE_HEIGHT = 50            # 标题区域固定高度
CARD_TITLE_SIZE = 16              # 标题字体大小
CARD_TITLE_MAX_LINES = 2          # 标题最多行数
CARD_CHIP_TEXT_SIZE = 12          # Chip 文字大小
```

### 示例图片对话框相关

```python
EXAMPLE_DIALOG_WIDTH = 900               # 对话框宽度
EXAMPLE_DIALOG_HEIGHT = 650              # 对话框高度
EXAMPLE_GRID_IMAGE_WIDTH = 240           # 网格缩略图宽度
EXAMPLE_GRID_IMAGE_HEIGHT = 240          # 网格缩略图高度
EXAMPLE_DETAIL_IMAGE_WIDTH = 600         # 详情大图宽度
EXAMPLE_DETAIL_IMAGE_HEIGHT = 450        # 详情大图高度
```

### 模型详情对话框相关

```python
MODEL_DETAIL_DIALOG_WIDTH = 500          # 对话框宽度
MODEL_DETAIL_DIALOG_HEIGHT = 600         # 对话框高度
MODEL_DETAIL_IMAGE_WIDTH = 450           # 预览图宽度
MODEL_DETAIL_IMAGE_HEIGHT = 300          # 预览图高度
```

### 响应式网格配置

```python
MODEL_CARD_GRID_COL = {"xs": 12, "sm": 6, "md": 4, "lg": 3}
EXAMPLE_IMAGE_GRID_COL = {"xs": 12, "sm": 6, "md": 4, "lg": 3}
```

## 如何使用

### 导入方式

```python
# 方式 1: 从 constants 包导入
from constants import CARD_PREVIEW_WIDTH, CARD_PREVIEW_HEIGHT

# 方式 2: 从 ui_size 模块导入
from constants.ui_size import CARD_PREVIEW_WIDTH, CARD_PREVIEW_HEIGHT

# 方式 3: 导入所有（不推荐，除非确实需要）
from constants.ui_size import *
```

### 使用示例

```python
# 创建图片组件
image = AsyncImage(
    model_meta=meta,
    width=CARD_PREVIEW_WIDTH,    # 使用常量
    height=CARD_PREVIEW_HEIGHT,  # 使用常量
)

# 设置容器高度
container = ft.Container(
    content=...,
    height=CARD_INFO_HEIGHT,     # 使用常量
)
```

## 修改尺寸

如果需要调整 UI 尺寸，只需：

1. 打开 `src/constants/ui_size.py`
2. 修改对应的常量值
3. 重新运行应用，所有使用该常量的地方都会自动更新

### 示例：调整卡片高度

```python
# 在 ui_size.py 中修改
CARD_INFO_HEIGHT = 150  # 从 130 改为 150
```

所有模型卡片的信息区域高度都会变为 150px。

## 优势

✅ **统一管理**：所有尺寸在一个文件中，易于查找和修改  
✅ **避免硬编码**：不再在代码中到处写魔法数字  
✅ **易于维护**：修改一处，全局生效  
✅ **提高可读性**：常量名称清晰表达含义  
✅ **便于调试**：快速实验不同的尺寸配置  

## 最佳实践

1. **新增 UI 组件时**，优先使用现有常量
2. **需要新尺寸时**，在 `ui_size.py` 中添加新常量
3. **命名规范**：`组件名_用途_类型`（如 `CARD_TITLE_SIZE`）
4. **添加注释**：说明常量的用途和单位
5. **分类组织**：相关常量放在一起，用注释分隔

## 注意事项

⚠️ **不要直接修改引用常量的代码**，应该修改 `ui_size.py` 中的常量定义  
⚠️ **保持一致性**：相同用途的尺寸应使用相同的常量  
⚠️ **文档同步**：修改常量后，更新相关文档和注释  

## 相关文件

- 常量定义：`src/constants/ui_size.py`
- 常量导出：`src/constants/__init__.py`
- 使用示例：所有 `src/components/` 和 `src/pages/` 下的文件

