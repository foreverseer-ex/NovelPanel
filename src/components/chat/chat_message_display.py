"""
聊天消息显示组件

用于显示聊天消息列表，支持文本和图片消息的展示。
"""

import flet as ft
from enum import Enum
from typing import Optional
from schemas.chat import ChatMessage as ChatMessageData, TextMessage, ToolCall, ImageChoice, TextChoice
from constants.color import ToolRouterColor


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
    """单条聊天消息组件（支持多种内容类型）"""

    def __init__(
        self, 
        role: MessageRole, 
        content: str = "", 
        is_markdown: bool = True,
        message_data: Optional[ChatMessageData] = None,
        on_delete: callable = None
    ):
        """
        初始化聊天消息

        Args:
            role: 消息角色
            content: 消息内容（简单模式）
            is_markdown: 是否使用 Markdown 渲染（默认 True）
            message_data: 完整的消息数据对象（高级模式）
            on_delete: 删除消息的回调函数
        """
        super().__init__()

        self.role = role
        self.message_content = content
        self.is_markdown = is_markdown
        self.message_data = message_data
        self.on_delete_callback = on_delete
        self.vertical_alignment = ft.CrossAxisAlignment.START
        self.spacing = 10

        # 创建头像
        avatar = ft.CircleAvatar(
            content=ft.Text(role.display_name[0], size=14, weight=ft.FontWeight.BOLD),
            color=ft.Colors.WHITE,
            bgcolor=role.color,
            radius=20,
        )
        
        # 创建删除按钮
        delete_button = ft.IconButton(
            icon=ft.Icons.DELETE_OUTLINE,
            icon_size=16,
            tooltip="删除此消息",
            icon_color=ft.Colors.GREY_600,
            on_click=lambda e: self._handle_delete() if self.on_delete_callback else None,
            visible=on_delete is not None,  # 只有提供了回调才显示
        )
        
        # 头像和删除按钮的列
        avatar_column = ft.Column(
            [avatar, delete_button],
            spacing=5,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )

        # 创建消息内容区域
        if message_data:
            # 高级模式：渲染多种类型的内容
            content_widgets = self._create_content_widgets(message_data)
            
            # 如果没有内容控件（messages 为空），显示占位符
            if not content_widgets:
                if is_markdown:
                    self.content_widget = ft.Markdown(
                        "(空消息)",
                        selectable=True,
                        extension_set=ft.MarkdownExtensionSet.GITHUB_WEB,
                    )
                else:
                    self.content_widget = ft.Text("(空消息)", selectable=True)
                content_widgets = [ft.Container(content=self.content_widget, expand=True)]
            
            message_widget = ft.Column(
                controls=content_widgets,
                spacing=10,
                expand=True,
            )
            # 存储第一个文本组件用于流式更新
            if not hasattr(self, 'content_widget'):
                for widget in content_widgets:
                    if isinstance(widget, ft.Container) and isinstance(widget.content, ft.Markdown):
                        self.content_widget = widget.content
                        break
                    elif isinstance(widget, ft.Container) and hasattr(widget.content, 'content'):
                        if isinstance(widget.content.content, ft.Text):
                            self.content_widget = widget.content.content
                            break
        else:
            # 简单模式：单一文本内容
            if is_markdown:
                self.content_widget = ft.Markdown(
                    content,
                    selectable=True,
                    extension_set=ft.MarkdownExtensionSet.GITHUB_WEB,
                    md_style_sheet=ft.MarkdownStyleSheet(
                        blockquote_decoration=ft.BoxDecoration(
                            bgcolor=ft.Colors.GREY_800,
                            border_radius=5,
                        ),
                    ),
                )
                message_widget = ft.Container(
                    content=self.content_widget,
                    expand=True,
                )
            else:
                self.content_widget = ft.Text(content, selectable=True)
                message_widget = ft.Container(
                    content=ft.SelectionArea(
                        content=self.content_widget
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
                avatar_column,
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
                avatar_column,
                message_column,
            ]
    
    def _handle_delete(self):
        """处理删除消息"""
        if self.on_delete_callback:
            self.on_delete_callback(self)
    
    def _create_content_widgets(self, message_data: ChatMessageData) -> list:
        """
        根据消息数据创建内容控件列表
        
        Args:
            message_data: 消息数据对象
        
        Returns:
            控件列表
        """
        widgets = []
        
        # 渲染消息内容（文本 + 工具调用）
        for msg_content in message_data.messages:
            if isinstance(msg_content, TextMessage):
                # 渲染文本消息
                if self.is_markdown:
                    text_widget = ft.Markdown(
                        msg_content.content,
                        selectable=True,
                        extension_set=ft.MarkdownExtensionSet.GITHUB_WEB,
                        md_style_sheet=ft.MarkdownStyleSheet(
                            blockquote_decoration=ft.BoxDecoration(
                                bgcolor=ft.Colors.GREY_800,
                                border_radius=5,
                            ),
                        ),
                    )
                    widgets.append(ft.Container(content=text_widget, expand=True))
                else:
                    text_widget = ft.Text(msg_content.content, selectable=True)
                    widgets.append(
                        ft.Container(
                            content=ft.SelectionArea(content=text_widget),
                            expand=True
                        )
                    )
            
            elif isinstance(msg_content, ToolCall):
                # 渲染工具调用按钮
                # 格式化参数：arg1=xxx, arg2=xxx
                args_str = ", ".join([f"{k}={repr(v)}" for k, v in msg_content.arguments.items()])
                
                # 构建完整的显示文本：funcname(arg1=xxx,arg2=xxx) -> 返回值
                if msg_content.result:
                    result_display = msg_content.result
                    if len(result_display) > 50:  # 结果截断到50字符
                        result_display = result_display[:50] + "..."
                    tool_text = f"{msg_content.tool_name}({args_str}) -> {result_display}"
                else:
                    tool_text = f"{msg_content.tool_name}({args_str}) -> (无返回值)"
                
                # 如果整体文本过长，截断
                max_display_length = 120
                if len(tool_text) > max_display_length:
                    tool_text = tool_text[:max_display_length] + "..."
                
                # 根据工具名称获取对应的路由颜色
                tool_color = ToolRouterColor.get(msg_content.tool_name)
                
                # 使用 ElevatedButton 代替 Chip，更明显的可点击外观
                tool_button = ft.ElevatedButton(
                    content=ft.Row(
                        [
                            ft.Icon(ft.Icons.BUILD, size=16, color=ft.Colors.WHITE),
                            ft.Text(
                                tool_text, 
                                size=11, 
                                font_family="Consolas",
                                color=ft.Colors.WHITE,
                                overflow=ft.TextOverflow.ELLIPSIS,  # 额外保险
                                max_lines=1,
                            ),
                        ],
                        spacing=8,
                        tight=True,
                    ),
                    style=ft.ButtonStyle(
                        bgcolor=tool_color,
                        color=ft.Colors.WHITE,
                        padding=ft.padding.symmetric(horizontal=12, vertical=8),
                        shape=ft.RoundedRectangleBorder(radius=8),
                    ),
                    # 点击显示工具调用详情
                    on_click=lambda e, tool=msg_content: self._show_tool_detail_dialog(tool),
                )
                widgets.append(tool_button)
        
        # 渲染选项（choices）
        if message_data.choices:
            choice_widgets = []
            for choice in message_data.choices:
                if isinstance(choice, ImageChoice):
                    # 渲染图像选项
                    image_widget = ft.Container(
                        content=ft.Column(
                            [
                                ft.Image(
                                    src=choice.url,
                                    width=200,
                                    height=200,
                                    fit=ft.ImageFit.CONTAIN,
                                    border_radius=5,
                                ),
                                ft.Text(choice.label or "图片", size=10),
                            ],
                            spacing=5,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                        border=ft.border.all(1, ft.Colors.GREY_700),
                        border_radius=5,
                        padding=5,
                        # TODO: 实现点击选择图像
                        on_click=None,
                    )
                    choice_widgets.append(image_widget)
                
                elif isinstance(choice, TextChoice):
                    # 渲染文字选项按钮
                    text_button = ft.ElevatedButton(
                        text=choice.label,
                        style=ft.ButtonStyle(
                            bgcolor=ft.Colors.GREEN_900,
                            color=ft.Colors.WHITE,
                        ),
                        # TODO: 实现点击快捷回复
                        on_click=None,
                    )
                    choice_widgets.append(text_button)
            
            # 将选项包装在一个容器中
            if choice_widgets:
                choices_container = ft.Container(
                    content=ft.Row(
                        controls=choice_widgets,
                        spacing=10,
                        wrap=True,
                    ),
                    border=ft.border.all(1, ft.Colors.GREY_700),
                    border_radius=5,
                    padding=10,
                )
                widgets.append(choices_container)
        
        return widgets
    
    def update_content(self, new_content: str):
        """
        更新消息内容（用于流式输出）
        
        Args:
            new_content: 新的消息内容
        """
        self.message_content = new_content
        if hasattr(self, 'content_widget'):
            if self.is_markdown:
                self.content_widget.value = new_content
            else:
                self.content_widget.value = new_content
            
            # 尝试更新控件，如果控件未添加到页面则跳过
            try:
                self.content_widget.update()
            except (AssertionError, AttributeError):
                # 控件未添加到页面或页面不存在，在测试环境中会出现
                pass
    
    def _show_tool_detail_dialog(self, tool_call: ToolCall):
        """显示工具调用详情对话框"""
        if not self.page:
            return
        dialog = ToolCallDetailDialog(tool_call)
        self.page.open(dialog)


class ToolCallDetailDialog(ft.AlertDialog):
    """工具调用详情对话框"""
    
    def __init__(self, tool_call: ToolCall):
        """
        初始化工具调用详情对话框
        
        Args:
            tool_call: 工具调用对象
        """
        import json
        
        # 构建参数表单式展示（格式化 JSON）
        param_text = json.dumps(tool_call.arguments, ensure_ascii=False, indent=2)
        
        # 格式化返回值
        result_text = self._format_result(tool_call.result)
        
        # 工具名称和结果
        dialog_content = ft.Column(
            [
                # 工具名称
                ft.Row(
                    [
                        ft.Icon(ft.Icons.BUILD, size=20, color=ft.Colors.BLUE_400),
                        ft.Text(
                            tool_call.tool_name,
                            size=18,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.BLUE_400,
                        ),
                    ],
                    spacing=10,
                ),
                ft.Divider(),
                
                # 参数标题
                ft.Text("参数", size=15, weight=ft.FontWeight.BOLD),
                ft.Container(height=5),
                
                # 参数列表（JSON 格式）
                ft.Container(
                    content=ft.Text(
                        param_text,
                        size=12,
                        selectable=True,
                        font_family="Microsoft YaHei",
                        color=ft.Colors.CYAN_400,
                    ) if param_text else ft.Text("无参数", color=ft.Colors.GREY_600),
                    padding=10,
                    bgcolor=ft.Colors.GREY_900,
                    border_radius=8,
                ),
                
                ft.Container(height=10),
                
                # 返回值标题
                ft.Text("返回值", size=15, weight=ft.FontWeight.BOLD),
                ft.Container(height=5),
                
                # 返回值内容（格式化显示）
                ft.Container(
                    content=ft.Text(
                        result_text,
                        size=12,
                        selectable=True,
                        font_family="Microsoft YaHei",
                        color=ft.Colors.GREEN_400 if tool_call.result else ft.Colors.GREY_600,
                    ),
                    padding=15,
                    bgcolor=ft.Colors.GREY_900,
                    border_radius=8,
                ),
            ],
            spacing=10,
            scroll=ft.ScrollMode.AUTO,
        )
        
        super().__init__(
            modal=True,
            title=ft.Text("工具调用详情", weight=ft.FontWeight.BOLD),
            content=ft.Container(
                content=dialog_content,
                width=600,
                height=500,
            ),
            actions=[
                ft.TextButton("关闭", on_click=self._on_close),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
    
    def _format_result(self, result: str) -> str:
        """格式化工具返回值
        
        Args:
            result: 原始返回值字符串
            
        Returns:
            格式化后的字符串
        """
        import json
        import re
        
        if not result:
            return "(无返回值)"
        
        # 尝试解析为 JSON
        try:
            parsed = json.loads(result)
            return json.dumps(parsed, ensure_ascii=False, indent=2)
        except:
            pass
        
        # 尝试解析为 Python 对象字符串（如 Pydantic 的 __str__）
        # 例如：content="actor_id='xxx' name='xxx' ..."
        if result.startswith("content=") or "=" in result:
            # 按照键值对分割
            lines = []
            # 使用正则提取 key='value' 或 key=value 模式
            pattern = r"(\w+)=('([^']*)'|\"([^\"]*)\"|([^\s]+))"
            matches = re.findall(pattern, result)
            
            if matches:
                for match in matches:
                    key = match[0]
                    # match[2], match[3], match[4] 分别对应不同引号或无引号的值
                    value = match[2] or match[3] or match[4]
                    
                    # 如果值太长，换行显示
                    if len(value) > 80:
                        lines.append(f"{key}=")
                        # 按 80 字符分割
                        for i in range(0, len(value), 80):
                            lines.append(f"  {value[i:i+80]}")
                    else:
                        lines.append(f"{key}={value}")
                
                return "\n".join(lines)
        
        # 如果没有特殊格式，尝试按长度换行
        if len(result) > 100:
            lines = []
            for i in range(0, len(result), 100):
                lines.append(result[i:i+100])
            return "\n".join(lines)
        
        return result
    
    def _on_close(self, e):
        """关闭对话框"""
        self.open = False
        self.update()


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

    def __init__(self, on_delete_message: callable = None):
        """
        初始化聊天消息列表
        
        Args:
            on_delete_message: 删除消息的回调函数 (message_widget) -> None
        """
        super().__init__()

        self.expand = True
        self.spacing = 15
        self.padding = ft.padding.all(20)
        self.auto_scroll = False  # 禁用自动滚动
        self.on_delete_message_callback = on_delete_message

    def add_message(self, role: MessageRole, content: str, is_markdown: bool = True):
        """
        添加一条消息（简单模式）

        Args:
            role: 消息角色
            content: 消息内容
            is_markdown: 是否使用 Markdown 渲染
            
        Returns:
            创建的消息对象
        """
        # 添加消息
        message = ChatMessage(role, content, is_markdown, on_delete=self.on_delete_message_callback)
        self.controls.append(message)
        
        # 在消息后面添加分隔线
        divider = ft.Divider(height=1, color=ft.Colors.GREY_800)
        self.controls.append(divider)
        
        self.update()
        return message
    
    def add_message_with_data(self, role: MessageRole, message_data: ChatMessageData, update_ui: bool = True):
        """
        添加一条消息（高级模式，支持多种内容类型）

        Args:
            role: 消息角色
            message_data: 完整的消息数据对象
            update_ui: 是否立即更新 UI（默认 True）
            
        Returns:
            创建的消息对象
        """
        # 添加消息
        message = ChatMessage(role, message_data=message_data, on_delete=self.on_delete_message_callback)
        self.controls.append(message)
        
        # 在消息后面添加分隔线
        divider = ft.Divider(height=1, color=ft.Colors.GREY_800)
        self.controls.append(divider)
        
        if update_ui:
            try:
                self.update()
            except (AssertionError, AttributeError):
                # 组件尚未添加到页面，稍后会自动更新
                pass
        return message

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
    
    def _create_message_widget(self, role: MessageRole, message_data: ChatMessageData = None, content: str = None, is_markdown: bool = True):
        """
        创建消息控件（内部方法）
        
        Args:
            role: 消息角色
            message_data: 完整的消息数据对象（优先使用）
            content: 简单文本内容（当 message_data 为 None 时使用）
            is_markdown: 是否使用 Markdown 渲染
            
        Returns:
            ChatMessage 控件
        """
        if message_data:
            return ChatMessage(role, message_data=message_data)
        else:
            return ChatMessage(role, content or "", is_markdown)
    


class ChatMessageDisplay(ft.Container):
    """聊天消息显示容器"""

    def __init__(self, on_delete_message: callable = None):
        """
        初始化聊天消息显示容器
        
        Args:
            on_delete_message: 删除消息的回调函数 (message_widget) -> None
        """
        super().__init__()

        self.expand = True
        self.border_radius = 10
        self.border = ft.border.all(1, ft.Colors.GREY_800)
        self.padding = 0
        self.margin = ft.margin.symmetric(horizontal=0, vertical=0)

        # 创建消息列表
        self.message_list = ChatMessageList(on_delete_message=on_delete_message)
        
        # 直接显示消息列表（不使用 Stack 和浮动按钮）
        self.content = self.message_list
    
    def scroll_to_bottom(self):
        """滚动到底部（公开方法，供外部调用）"""
        self.message_list.scroll_to_bottom()

