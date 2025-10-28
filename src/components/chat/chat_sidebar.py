"""
聊天侧边栏组件

包含新建对话、历史对话列表等功能。
"""

import flet as ft
from datetime import datetime


class ChatHistoryItem(ft.Container):
    """历史对话项"""

    def __init__(
        self, title: str, timestamp: datetime = None, on_click=None, on_delete=None
    ):
        """
        初始化历史对话项

        Args:
            title: 对话标题
            timestamp: 时间戳
            on_click: 点击回调
            on_delete: 删除回调
        """
        super().__init__()

        self.title = title
        self.timestamp = timestamp or datetime.now()
        self._on_click_callback = on_click
        self._on_delete_callback = on_delete

        # 时间显示
        time_str = self.timestamp.strftime("%m-%d %H:%M")

        # 删除按钮（鼠标悬停时显示）
        self.delete_button = ft.IconButton(
            icon=ft.Icons.DELETE_OUTLINE_ROUNDED,
            icon_size=16,
            tooltip="删除对话",
            on_click=self._handle_delete,
            visible=False,
            style=ft.ButtonStyle(
                color={
                    ft.ControlState.DEFAULT: ft.Colors.GREY_400,
                    ft.ControlState.HOVERED: ft.Colors.RED_400,
                }
            ),
        )

        # 组装内容
        self.content = ft.Row(
            [
                ft.Icon(ft.Icons.CHAT_BUBBLE_OUTLINE_ROUNDED, size=16, color=ft.Colors.GREY_500),
                ft.Column(
                    [
                        ft.Text(
                            title,
                            size=13,
                            weight=ft.FontWeight.W_500,
                            overflow=ft.TextOverflow.ELLIPSIS,
                            max_lines=1,
                        ),
                        ft.Text(time_str, size=11, color=ft.Colors.GREY_600),
                    ],
                    spacing=2,
                    expand=True,
                ),
                self.delete_button,
            ],
            spacing=10,
        )

        self.border_radius = 8
        self.padding = ft.padding.all(10)
        self.ink = True
        self.on_click = self._handle_click
        self.on_hover = self._handle_hover

    def _handle_click(self, _e: ft.ControlEvent):
        """处理点击事件"""
        if self._on_click_callback:
            self._on_click_callback(self)

    def _handle_delete(self, _e: ft.ControlEvent):
        """处理删除事件"""
        if self._on_delete_callback:
            self._on_delete_callback(self)

    def _handle_hover(self, e: ft.HoverEvent):
        """处理鼠标悬停事件"""
        is_hovered = e.data == "true"
        self.bgcolor = ft.Colors.GREY_800 if is_hovered else None
        self.delete_button.visible = is_hovered
        self.update()


class ChatHistoryList(ft.ListView):
    """历史对话列表"""

    def __init__(self, on_select_chat=None, on_delete_chat=None):
        """
        初始化历史对话列表

        Args:
            on_select_chat: 选择对话的回调
            on_delete_chat: 删除对话的回调
        """
        super().__init__()

        self.expand = True
        self.spacing = 5
        self.padding = ft.padding.all(10)

        self._on_select_chat = on_select_chat
        self._on_delete_chat = on_delete_chat

        # 添加示例历史记录
        self._add_demo_history()

    def _add_demo_history(self):
        """添加示例历史记录"""
        demo_chats = [
            ("如何提取角色信息", datetime(2025, 10, 28, 14, 30)),
            ("优化提示词技巧", datetime(2025, 10, 27, 16, 45)),
            ("修仙小说场景描述", datetime(2025, 10, 27, 10, 20)),
            ("角色一致性问题", datetime(2025, 10, 26, 9, 15)),
            ("LoRA 模型选择建议", datetime(2025, 10, 25, 20, 30)),
        ]

        for title, timestamp in demo_chats:
            item = ChatHistoryItem(
                title=title,
                timestamp=timestamp,
                on_click=self._handle_select_chat,
                on_delete=self._handle_delete_chat,
            )
            self.controls.append(item)

    def _handle_select_chat(self, item: ChatHistoryItem):
        """处理选择对话"""
        if self._on_select_chat:
            self._on_select_chat(item.title)

    def _handle_delete_chat(self, item: ChatHistoryItem):
        """处理删除对话"""
        if item in self.controls:
            self.controls.remove(item)
            self.update()

        if self._on_delete_chat:
            self._on_delete_chat(item.title)

    def add_chat(self, title: str, timestamp: datetime = None):
        """
        添加新对话到列表顶部

        Args:
            title: 对话标题
            timestamp: 时间戳
        """
        item = ChatHistoryItem(
            title=title,
            timestamp=timestamp,
            on_click=self._handle_select_chat,
            on_delete=self._handle_delete_chat,
        )
        self.controls.insert(0, item)
        self.update()


class ChatSidebar(ft.Container):
    """聊天侧边栏"""

    def __init__(
        self, on_new_chat=None, on_select_chat=None, on_delete_chat=None
    ):
        """
        初始化聊天侧边栏

        Args:
            on_new_chat: 新建对话的回调
            on_select_chat: 选择对话的回调
            on_delete_chat: 删除对话的回调
        """
        super().__init__()

        self._on_new_chat = on_new_chat

        # 新建对话按钮
        self.new_chat_button = ft.ElevatedButton(
            "新建对话",
            icon=ft.Icons.ADD_COMMENT_ROUNDED,
            on_click=self._handle_new_chat,
            style=ft.ButtonStyle(
                bgcolor={
                    ft.ControlState.DEFAULT: ft.Colors.BLUE_700,
                    ft.ControlState.HOVERED: ft.Colors.BLUE_600,
                },
                color=ft.Colors.WHITE,
                shape=ft.RoundedRectangleBorder(radius=8),
            ),
            expand=True,
        )

        # 历史对话列表
        self.history_list = ChatHistoryList(
            on_select_chat=on_select_chat, on_delete_chat=on_delete_chat
        )

        # 组装侧边栏
        self.content = ft.Column(
            [
                # 标题区域
                ft.Container(
                    content=ft.Text(
                        "AI 对话助手",
                        size=18,
                        weight=ft.FontWeight.BOLD,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    padding=ft.padding.all(15),
                ),
                ft.Divider(height=1, color=ft.Colors.GREY_800),
                # 新建按钮
                ft.Container(
                    content=self.new_chat_button,
                    padding=ft.padding.all(10),
                ),
                # 历史标题
                ft.Container(
                    content=ft.Text(
                        "历史对话",
                        size=12,
                        weight=ft.FontWeight.W_500,
                        color=ft.Colors.GREY_500,
                    ),
                    padding=ft.padding.only(left=15, right=15, top=10, bottom=5),
                ),
                # 历史列表
                ft.Container(
                    content=self.history_list,
                    expand=True,
                ),
            ],
            spacing=0,
        )

        self.width = 280
        self.bgcolor = ft.Colors.GREY_900
        self.border_radius = 10
        self.padding = 0

    def _handle_new_chat(self, _e: ft.ControlEvent):
        """处理新建对话"""
        if self._on_new_chat:
            self._on_new_chat()

        # 添加新对话到历史列表
        self.history_list.add_chat(f"新对话 {len(self.history_list.controls) + 1}")

