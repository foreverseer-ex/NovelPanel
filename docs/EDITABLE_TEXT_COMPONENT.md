# 可编辑文本组件 (EditableText)

## 概述

`EditableText` 是一个通用的可编辑文本组件，支持点击编辑、提交和取消操作。

## 文件位置

```
src/components/editable_text.py
```

## 功能特性

### ✨ 核心功能

- **双模式切换**
  - 正常状态：显示为可点击的文本
  - 编辑状态：显示为输入框 + 操作按钮

- **交互方式**
  - 点击文本进入编辑模式
  - Enter 键或点击✓按钮提交
  - Esc 键或点击✗按钮取消

- **多行支持**
  - 支持单行和多行输入
  - 可配置最小/最大行数

- **回调机制**
  - 提交时触发自定义回调函数
  - 传递新值作为参数

## 使用方法

### 基本用法

```python
from components.editable_text import EditableText

# 创建可编辑文本
editable = EditableText(
    value="初始值",
    placeholder="点击编辑...",
    on_submit=lambda new_value: print(f"新值: {new_value}"),
)
```

### 完整参数

```python
editable = EditableText(
    value="初始值",                    # 初始文本
    placeholder="点击编辑...",         # 空值占位符
    on_submit=callback_function,      # 提交回调
    text_size=13,                     # 文字大小
    multiline=True,                   # 多行模式
    min_lines=2,                      # 最小行数
    max_lines=5,                      # 最大行数
    selectable=True,                  # 文本可选择
)
```

## 参数说明

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `value` | `Optional[str]` | `None` | 初始值 |
| `placeholder` | `str` | `"点击编辑..."` | 空值占位符 |
| `on_submit` | `Optional[Callable[[str], None]]` | `None` | 提交回调函数 |
| `text_size` | `int` | `13` | 文字大小 |
| `multiline` | `bool` | `False` | 是否多行输入 |
| `min_lines` | `int` | `1` | 最小行数 |
| `max_lines` | `Optional[int]` | `None` | 最大行数 |
| `selectable` | `bool` | `True` | 文本是否可选择 |

## 属性和方法

### 属性

- `value`: 获取或设置当前值

```python
# 获取值
current_value = editable.value

# 设置值
editable.value = "新值"
```

### 内部方法

- `_enter_edit_mode()`: 进入编辑模式
- `_exit_edit_mode()`: 退出编辑模式
- `_handle_submit()`: 处理提交
- `_handle_cancel()`: 处理取消

## 视觉状态

### 正常模式
```
┌─────────────────────────┐
│ 这是文本内容             │  ← 点击可编辑
└─────────────────────────┘
```

### 空值占位符
```
┌─────────────────────────┐
│ 点击编辑...             │  ← 灰色斜体
└─────────────────────────┘
```

### 编辑模式
```
┌─────────────────────────┐
│ ┏━━━━━━━━━━━━━━━━━━━┓  │
│ ┃ 输入框内容        ┃  │  ← 蓝色边框
│ ┗━━━━━━━━━━━━━━━━━━━┛  │
│ [✓保存] [✗取消]          │
└─────────────────────────┘
```

## 实际应用示例

### 1. 模型详情对话框

在 `ModelDetailDialog` 中用于编辑模型描述：

```python
# 创建可编辑的说明字段
desc_editable = EditableText(
    value=meta.desc,                          # 模型描述
    placeholder="点击添加说明...",             # 空值提示
    on_submit=lambda new_desc: self._handle_desc_update(new_desc),
    multiline=True,                           # 多行输入
    min_lines=2,
    max_lines=5,
)

# 添加到信息行
rows.append(_make_editable_row("说明", desc_editable))
```

### 2. 保存回调

```python
def _handle_desc_update(self, new_desc: str):
    """处理描述更新。"""
    # 调用服务更新
    model_meta_service.update_desc(self.model_meta, new_desc)
    
    # 显示成功提示
    if self.page:
        self.page.show_snack_bar(
            ft.SnackBar(
                content=ft.Text("说明已保存"),
                duration=2000,
            )
        )
```

## 配套服务

### ModelMetaService.update_desc()

在 `src/services/model_meta.py` 中添加的方法：

```python
@staticmethod
def update_desc(meta: ModelMeta, new_desc: str) -> None:
    """
    更新模型描述并保存。
    
    :param meta: 模型元数据对象
    :param new_desc: 新的描述内容
    """
    # 更新描述
    meta.desc = new_desc if new_desc else None
    
    # 保存到文件
    ModelMetaService.save_meta(meta, meta.type)
    
    logger.info(f"已更新模型 {meta.name} 的描述")
```

## 样式说明

### 文本状态样式

- **有值**：正常颜色，正常字体
- **空值**：灰色（GREY_400），斜体
- **输入框**：蓝色边框（BLUE_400）

### 按钮样式

- **提交按钮**：绿色✓图标
- **取消按钮**：红色✗图标

## 扩展建议

### 可能的增强功能

1. **验证功能**
   ```python
   on_validate: Callable[[str], bool]  # 验证输入
   ```

2. **自动保存**
   ```python
   auto_save: bool = False  # 失去焦点自动保存
   ```

3. **撤销/重做**
   ```python
   enable_undo: bool = True  # 支持撤销
   ```

4. **字符计数**
   ```python
   max_length: int = None  # 最大字符数
   show_counter: bool = False  # 显示计数器
   ```

## 注意事项

⚠️ **回调函数**：确保 `on_submit` 回调不会抛出异常  
⚠️ **长文本**：多行模式建议设置 `max_lines` 避免界面过大  
⚠️ **性能**：频繁更新大文本时注意性能影响  
⚠️ **并发**：同一对象多次点击编辑时会忽略重复请求  

## 相关文件

- 组件定义：`src/components/editable_text.py`
- 使用示例：`src/components/model_card/model_detail_dialog.py`
- 服务支持：`src/services/model_meta.py`
- 数据模型：`src/schemas/model_meta.py`

