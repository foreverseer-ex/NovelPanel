"""
可编辑卡片组件

提供内联编辑功能的卡片，点击即可编辑，支持多行文本。
"""

import flet as ft
from typing import Callable, Optional


class EditableCard(ft.Card):
    """可编辑卡片组件
    
    特性：
    - 点击卡片任意位置进入编辑模式
    - 支持多行文本编辑
    - 按 Escape 取消编辑
    - 失去焦点或按 Ctrl+Enter 保存
    """
    
    def __init__(
        self,
        content: str,
        on_save: Callable[[str], None],
        min_lines: int = 1,
        max_lines: int = 20,
    ):
        """
        初始化可编辑卡片
        
        Args:
            content: 卡片内容
            on_save: 保存回调函数，接收新内容作为参数
            min_lines: 最小行数
            max_lines: 最大行数
        """
        super().__init__()
        
        self.current_content = content
        self.on_save_callback = on_save
        self.min_lines = min_lines
        self.max_lines = max_lines
        
        self.is_editing = False
        
        # 查看模式：显示文本
        self.text_display = ft.Text(
            content,
            selectable=False,  # 不可选择，专注于点击进入编辑
            size=14,
        )
        
        self.view_container = ft.Container(
            content=self.text_display,
            padding=15,
            on_click=self._on_card_click,
            ink=True,  # 添加点击水波纹效果
            # 确保容器填充整个可用空间
            expand=True,
            alignment=ft.alignment.top_left,
        )
        
        # 编辑模式：显示文本框
        self.text_field = ft.TextField(
            value=content,
            multiline=True,
            min_lines=min_lines,
            max_lines=max_lines,
            border_color=ft.Colors.BLUE_400,
            focused_border_color=ft.Colors.BLUE_600,
            expand=True,
            on_blur=self._on_text_field_blur,
            on_submit=self._save_and_exit,  # 不会触发（multiline=True），但保留
            autofocus=True,
        )
        
        # 编辑模式提示
        self.edit_hint = ft.Row(
            [
                ft.Text("Ctrl+Enter 保存", size=10, color=ft.Colors.GREY_400),
                ft.Text("•", size=10, color=ft.Colors.GREY_600),
                ft.Text("Esc 取消", size=10, color=ft.Colors.GREY_400),
            ],
            spacing=5,
        )
        
        self.edit_container = ft.Container(
            content=ft.Column(
                [
                    self.text_field,
                    self.edit_hint,
                ],
                spacing=5,
            ),
            padding=10,
            expand=True,
            alignment=ft.alignment.top_left,
        )
        
        # 初始内容（查看模式）
        self.content = self.view_container
        
        # 卡片样式
        self.elevation = 1
        self.margin = ft.margin.symmetric(vertical=5)
    
    def _on_card_click(self, _e):
        """处理卡片点击事件"""
        # 只在查看模式下响应点击
        if not self.is_editing:
            self._enter_edit_mode(_e)
    
    def _enter_edit_mode(self, _e):
        """进入编辑模式"""
        if self.is_editing:
            return
        
        self.is_editing = True
        
        # 更新文本框的值为当前内容
        self.text_field.value = self.current_content
        
        # 切换内容为编辑容器
        self.content = self.edit_container
        
        # 先更新页面，确保文本框已添加到页面
        self.update()
        
        # 然后聚焦到文本框
        self.text_field.focus()
    
    def _exit_edit_mode(self, save: bool = False):
        """退出编辑模式
        
        Args:
            save: 是否保存更改
        """
        if not self.is_editing:
            return
        
        if save:
            new_content = self.text_field.value.strip()
            if new_content != self.current_content:
                # 内容有变化，调用保存回调
                self.current_content = new_content
                self.text_display.value = new_content
                
                if self.on_save_callback:
                    self.on_save_callback(new_content)
        else:
            # 取消编辑，恢复原值
            self.text_field.value = self.current_content
        
        self.is_editing = False
        
        # 切换内容为查看容器
        self.content = self.view_container
        
        self.update()
    
    def _on_text_field_blur(self, _e):
        """文本框失去焦点时保存"""
        self._exit_edit_mode(save=True)
    
    def _save_and_exit(self, _e):
        """保存并退出编辑模式"""
        self._exit_edit_mode(save=True)
    
    def did_mount(self):
        """组件挂载后，注册键盘事件"""
        if hasattr(self, 'page') and self.page:
            # 注册键盘事件监听
            def on_keyboard(e: ft.KeyboardEvent):
                if not self.is_editing:
                    return
                
                # Escape: 取消编辑
                if e.key == "Escape":
                    self._exit_edit_mode(save=False)
                # Ctrl+Enter: 保存并退出
                elif e.key == "Enter" and e.ctrl:
                    self._exit_edit_mode(save=True)
            
            self.page.on_keyboard_event = on_keyboard
    
    def update_content(self, new_content: str):
        """外部更新内容
        
        Args:
            new_content: 新内容
        """
        self.current_content = new_content
        self.text_display.value = new_content
        if not self.is_editing:
            self.update()

