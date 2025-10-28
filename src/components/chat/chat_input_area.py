"""
聊天输入区域组件

包含文本输入框、发送按钮和文件上传功能。
"""

import flet as ft


class ChatInputField(ft.TextField):
    """聊天输入框"""

    def __init__(self, on_submit_callback=None):
        """
        初始化聊天输入框

        Args:
            on_submit_callback: 提交消息时的回调函数
        """
        super().__init__()

        self.border = ft.InputBorder.NONE
        self.focused_border_color = ft.Colors.TRANSPARENT
        self.hint_text = "输入消息...（按 Enter 发送，Shift+Enter 换行）"
        self.hint_style = ft.TextStyle(color=ft.Colors.GREY_600, size=13)
        self.text_size = 14
        self.multiline = True
        self.min_lines = 1
        self.max_lines = 5
        self.shift_enter = True
        self.expand = True
        self.autofocus = True

        self._on_submit_callback = on_submit_callback
        self.on_submit = self._handle_submit

    def _handle_submit(self, e: ft.ControlEvent):
        """处理提交事件"""
        if self._on_submit_callback and self.value.strip():
            self._on_submit_callback(self.value)
            self.value = ""
            self.focus()
            self.update()


class ChatInputArea(ft.Container):
    """聊天输入区域容器"""

    def __init__(self, on_send_message=None):
        """
        初始化聊天输入区域

        Args:
            on_send_message: 发送消息时的回调函数 (message: str) -> None
        """
        super().__init__()

        self._on_send_message = on_send_message

        # 创建输入框
        self.input_field = ChatInputField(on_submit_callback=self._handle_send)

        # 创建发送按钮
        self.send_button = ft.IconButton(
            icon=ft.Icons.SEND_ROUNDED,
            tooltip="发送消息",
            icon_size=20,
            on_click=self._handle_send_click,
            style=ft.ButtonStyle(
                color={
                    ft.ControlState.DEFAULT: ft.Colors.GREY_400,
                    ft.ControlState.HOVERED: ft.Colors.GREEN_400,
                }
            ),
        )

        # 组装布局：输入框和发送按钮在同一行
        self.content = ft.Container(
            content=ft.Row(
                [
                    # 输入框区域
                    ft.Container(
                        content=self.input_field,
                        expand=True,
                    ),
                    # 发送按钮
                    self.send_button,
                ],
                spacing=5,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            border_radius=10,
            border=ft.border.all(1, ft.Colors.GREY_800),
            bgcolor=ft.Colors.GREY_900,
            padding=ft.padding.symmetric(horizontal=10, vertical=5),
        )

        self.padding = ft.padding.symmetric(horizontal=0, vertical=15)
        self.expand = False

    def _handle_send(self, message: str = None):
        """
        处理发送消息

        Args:
            message: 消息内容（如果为 None 则从输入框获取）
        """
        if message is None:
            message = self.input_field.value

        if self._on_send_message and message.strip():
            self._on_send_message(message.strip())
            self.input_field.value = ""
            self.input_field.focus()
            self.update()

    def _handle_send_click(self, _e: ft.ControlEvent):
        """处理点击发送按钮"""
        self._handle_send()

    def clear_input(self):
        """清空输入框"""
        self.input_field.value = ""
        self.input_field.update()

    def set_enabled(self, enabled: bool):
        """
        设置输入区域是否可用

        Args:
            enabled: 是否可用
        """
        self.input_field.disabled = not enabled
        self.attach_button.disabled = not enabled
        self.send_button.disabled = not enabled
        self.update()

