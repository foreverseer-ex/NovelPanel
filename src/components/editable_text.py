"""
可编辑文本组件。

正常情况下显示为文本，点击后变为输入框，回车或失焦时自动提交。
"""
import flet as ft
from typing import Optional, Callable


class EditableText(ft.Container):
    """可编辑文本组件。
    
    特性：
    - 正常状态显示为文本
    - 点击后变为输入框
    - 回车或失去焦点时自动提交
    - 自定义提交回调
    """
    
    def __init__(
        self,
        value: Optional[str] = None,
        placeholder: str = "点击编辑...",
        on_submit: Optional[Callable[[str], None]] = None,
        text_size: int = 13,
        multiline: bool = False,
        min_lines: int = 1,
        max_lines: Optional[int] = None,
        selectable: bool = True,
        **kwargs
    ):
        """初始化可编辑文本组件。
        
        :param value: 初始值
        :param placeholder: 空值时的占位符
        :param on_submit: 提交回调函数，接收新值作为参数
        :param text_size: 文字大小
        :param multiline: 是否多行输入
        :param min_lines: 最小行数
        :param max_lines: 最大行数
        :param selectable: 文本是否可选择
        :param kwargs: 传递给 Container 的其他参数
        """
        super().__init__(**kwargs)
        
        self._value = value or ""
        self._placeholder = placeholder
        self._on_submit = on_submit
        self._text_size = text_size
        self._multiline = multiline
        self._min_lines = min_lines
        self._max_lines = max_lines
        self._selectable = selectable
        self._is_editing = False
        
        # 文本显示控件
        self._text_display = ft.Text(
            value=self._value if self._value else self._placeholder,
            size=self._text_size,
            selectable=self._selectable,
            color=ft.Colors.GREY_400 if not self._value else None,
            italic=not self._value,  # 占位符斜体
        )
        
        # 输入框控件
        self._text_field = ft.TextField(
            value=self._value,
            multiline=self._multiline,
            min_lines=self._min_lines,
            max_lines=self._max_lines,
            text_size=self._text_size,
            on_submit=lambda e: self._handle_submit() if not self._multiline else None,  # 单行时回车提交
            on_blur=lambda e: self._handle_submit(),     # 失去焦点时提交
            autofocus=True,
        )
        
        # 提交按钮（多行模式下显示）
        self._submit_button = ft.IconButton(
            icon=ft.Icons.CHECK_CIRCLE,
            icon_color=ft.Colors.GREEN_400,
            tooltip="保存 (或点击其他地方)",
            on_click=lambda e: self._handle_submit(),
            icon_size=20,
        )
        
        # 初始显示文本 - 简单的容器，点击切换到编辑模式
        self.content = ft.Container(
            content=self._text_display,
            on_click=lambda e: self._enter_edit_mode(),
            padding=5,
            border=ft.border.all(1, ft.Colors.TRANSPARENT),
            border_radius=4,
        )
        
        # 设置容器样式
        self.padding = ft.padding.symmetric(vertical=4, horizontal=0)
        self.expand = True
    
    @property
    def value(self) -> str:
        """获取当前值。"""
        return self._value
    
    @value.setter
    def value(self, new_value: Optional[str]):
        """设置新值。"""
        self._value = new_value or ""
        self._update_display()
    
    def _update_display(self):
        """更新显示内容。"""
        if self._value:
            self._text_display.value = self._value
            self._text_display.color = None
            self._text_display.italic = False
        else:
            self._text_display.value = self._placeholder
            self._text_display.color = ft.Colors.GREY_400
            self._text_display.italic = True
    
    def _enter_edit_mode(self):
        """进入编辑模式。"""
        if self._is_editing:
            return
        
        self._is_editing = True
        self._text_field.value = self._value
        
        # 多行模式：显示输入框 + 提交按钮
        # 单行模式：只显示输入框
        if self._multiline:
            self.content = ft.Column(
                controls=[
                    self._text_field,
                    ft.Row(
                        controls=[
                            self._submit_button,
                            ft.Text("回车换行，点击✓或其他地方保存", size=11, color=ft.Colors.GREY_500),
                        ],
                        spacing=8,
                    ),
                ],
                spacing=8,
                tight=True,
            )
        else:
            # 单行模式：回车直接提交
            self.content = self._text_field
        
        self.update()
    
    def _exit_edit_mode(self):
        """退出编辑模式。"""
        if not self._is_editing:
            return
        
        self._is_editing = False
        
        # 切换回文本显示 - 简单的容器
        self.content = ft.Container(
            content=self._text_display,
            on_click=lambda e: self._enter_edit_mode(),
            padding=5,
            border=ft.border.all(1, ft.Colors.TRANSPARENT),
            border_radius=4,
        )
        self.update()
    
    def _handle_submit(self):
        """处理提交事件（回车或失焦）。"""
        if not self._is_editing:
            return
            
        new_value = self._text_field.value or ""
        self._value = new_value
        self._update_display()
        self._exit_edit_mode()
        
        # 调用回调函数
        if self._on_submit:
            self._on_submit(new_value)

