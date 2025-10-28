"""
聊天消息显示组件

用于显示聊天消息列表，支持文本和图片消息的展示。
"""

import flet as ft
from enum import Enum


class MessageRole(Enum):
    """消息角色枚举"""

    USER = ("用户", ft.Colors.BLUE_400)
    ASSISTANT = ("AI助手", ft.Colors.GREEN_400)
    SYSTEM = ("系统", ft.Colors.GREY_400)

    def __init__(self, display_name: str, color: str):
        self._display_name = display_name
        self._color = color

    @property
    def display_name(self) -> str:
        """显示名称"""
        return self._display_name

    @property
    def color(self) -> str:
        """头像颜色"""
        return self._color


class ChatMessage(ft.Row):
    """单条聊天消息组件"""

    def __init__(self, role: MessageRole, content: str, is_markdown: bool = True):
        """
        初始化聊天消息

        Args:
            role: 消息角色
            content: 消息内容
            is_markdown: 是否使用 Markdown 渲染（默认 True）
        """
        super().__init__()

        self.role = role
        self.message_content = content
        self.vertical_alignment = ft.CrossAxisAlignment.START
        self.spacing = 10

        # 创建头像
        avatar = ft.CircleAvatar(
            content=ft.Text(role.display_name[0], size=14, weight=ft.FontWeight.BOLD),
            color=ft.Colors.WHITE,
            bgcolor=role.color,
            radius=20,
        )

        # 创建消息内容
        if is_markdown:
            message_widget = ft.Container(
                content=ft.Markdown(
                    content,
                    selectable=True,
                    extension_set=ft.MarkdownExtensionSet.GITHUB_WEB,
                    md_style_sheet=ft.MarkdownStyleSheet(
                        blockquote_decoration=ft.BoxDecoration(
                            bgcolor=ft.Colors.GREY_800,
                            border_radius=5,
                        ),
                    ),
                ),
                expand=True,
            )
        else:
            message_widget = ft.Container(
                content=ft.SelectionArea(
                    content=ft.Text(content, selectable=True)
                ),
                expand=True,
            )

        # 根据角色决定布局：用户消息在右侧，其他消息在左侧
        if role == MessageRole.USER:
            # 用户消息：右对齐，头像在右侧，文本右对齐
            self.alignment = ft.MainAxisAlignment.END
            
            # 消息内容列（右对齐）
            message_column = ft.Column(
                [
                    ft.Text(
                        role.display_name,
                        size=12,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.GREY_400,
                        text_align=ft.TextAlign.RIGHT,
                    ),
                    message_widget,
                ],
                spacing=5,
                expand=True,
                horizontal_alignment=ft.CrossAxisAlignment.END,  # 内容右对齐
            )
            
            self.controls = [
                message_column,
                avatar,
            ]
        else:
            # AI/系统消息：左对齐，头像在左侧
            self.alignment = ft.MainAxisAlignment.START
            
            # 消息内容列（左对齐）
            message_column = ft.Column(
                [
                    ft.Text(
                        role.display_name,
                        size=12,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.GREY_400,
                    ),
                    message_widget,
                ],
                spacing=5,
                expand=True,
            )
            
            self.controls = [
                avatar,
                message_column,
            ]


class TypingIndicator(ft.Row):
    """正在输入指示器"""

    def __init__(self, message: str = "AI 正在思考..."):
        """
        初始化输入指示器

        Args:
            message: 提示消息
        """
        super().__init__()
        self.spacing = 10

        self.controls = [
            ft.ProgressRing(height=16, width=16, stroke_width=2),
            ft.Text(message, color=ft.Colors.GREY_400, size=12, italic=True),
        ]


class ChatMessageList(ft.ListView):
    """聊天消息列表容器"""

    def __init__(self):
        """初始化聊天消息列表"""
        super().__init__()

        self.expand = True
        self.spacing = 15
        self.padding = ft.padding.all(20)
        self.auto_scroll = False  # 禁用自动滚动

    def add_message(self, role: MessageRole, content: str, is_markdown: bool = True):
        """
        添加一条消息

        Args:
            role: 消息角色
            content: 消息内容
            is_markdown: 是否使用 Markdown 渲染
        """
        # 添加消息
        message = ChatMessage(role, content, is_markdown)
        self.controls.append(message)
        
        # 在消息后面添加分隔线
        divider = ft.Divider(height=1, color=ft.Colors.GREY_800)
        self.controls.append(divider)
        
        self.update()

    def add_typing_indicator(self):
        """添加正在输入指示器"""
        # 添加输入指示器（不需要后面的分割线，因为会被移除）
        indicator = TypingIndicator()
        self.controls.append(indicator)
        self.update()
        return indicator

    def remove_typing_indicator(self, indicator: TypingIndicator):
        """
        移除正在输入指示器

        Args:
            indicator: 要移除的指示器实例
        """
        if indicator in self.controls:
            self.controls.remove(indicator)
            self.update()

    def clear_messages(self):
        """清空所有消息"""
        self.controls.clear()
        self.update()
    
    def scroll_to_bottom(self):
        """滚动到底部"""
        if self.controls:
            # 滚动到最后一个元素
            self.scroll_to(offset=-1, duration=300)


class ChatMessageDisplay(ft.Container):
    """聊天消息显示容器"""

    def __init__(self):
        """初始化聊天消息显示容器"""
        super().__init__()

        self.expand = True
        self.border_radius = 10
        self.border = ft.border.all(1, ft.Colors.GREY_800)
        self.padding = 0
        self.margin = ft.margin.symmetric(horizontal=0, vertical=0)

        # 创建消息列表
        self.message_list = ChatMessageList()
        
        # 创建滚动到底部按钮
        self.scroll_button = ft.FloatingActionButton(
            icon=ft.Icons.ARROW_DOWNWARD,
            mini=True,
            tooltip="滚动到底部",
            on_click=self._scroll_to_bottom,
            bgcolor=ft.Colors.BLUE_700,
        )
        
        # 使用 Stack 布局，将按钮悬浮在右下角
        self.content = ft.Stack(
            controls=[
                self.message_list,
                ft.Container(
                    content=self.scroll_button,
                    right=20,
                    bottom=20,
                ),
            ],
            expand=True,
        )
    
    def _scroll_to_bottom(self, _e: ft.ControlEvent):
        """处理滚动到底部按钮点击"""
        self.message_list.scroll_to_bottom()

    def did_mount(self):
        """组件挂载后添加示例消息"""
        self._add_demo_messages()

    def _add_demo_messages(self):
        """添加示例消息（演示用）"""
        self.message_list.add_message(
            MessageRole.SYSTEM, "欢迎使用 NovelPanel AI 助手！我可以帮助您：\n\n"
            "- 📖 分析和理解小说内容\n"
            "- 👤 提取和管理角色信息\n"
            "- 🎨 生成高质量的 Stable Diffusion 提示词\n"
            "- 🖼️ 优化图像生成参数\n\n"
            "请告诉我您需要什么帮助！"
        )

        self.message_list.add_message(
            MessageRole.USER, "你好！我想将一部修仙小说转换成漫画，应该从哪里开始？"
        )

        self.message_list.add_message(
            MessageRole.ASSISTANT,
            "很高兴帮助您！将小说转换成漫画的流程如下：\n\n"
            "## 1. 上传小说\n"
            "首先上传您的小说文本文件（.txt 格式）\n\n"
            "## 2. 解析内容\n"
            "系统会自动：\n"
            "- 按行分割文本（每行生成一张图）\n"
            "- 识别章节结构\n"
            "- 提取角色信息\n"
            "- 分析世界观设定\n\n"
            "## 3. 生成图像\n"
            "- AI 会为每一行文本生成合适的提示词\n"
            "- 使用 SD-Forge 渲染图像\n"
            "- 您可以选择满意的图像\n\n"
            "## 4. 组合导出\n"
            "将选中的图像按顺序组合成完整漫画\n\n"
            "现在就开始吧！😊",
        )

