"""
聊天页面

提供与 AI 交互的界面，帮助用户分析小说、优化提示词等。
"""

import flet as ft
from components.chat import ChatMessageDisplay, ChatInputArea
from components.chat.chat_message_display import MessageRole


class ChatPage(ft.Container):
    """聊天页面主组件"""

    def __init__(self, page: ft.Page):
        """
        初始化聊天页面

        Args:
            page: Flet 页面对象
        """
        super().__init__()

        self.page = page
        self.expand = True
        self.padding = ft.padding.all(10)

        # 创建组件
        self.message_display = ChatMessageDisplay()

        self.input_area = ChatInputArea(
            on_send_message=self._handle_send_message,
        )

        # 组装布局：垂直布局（标题栏 + 消息显示 + 输入框）
        self.content = ft.Column(
            [
                # 顶部标题栏
                self._create_header(),
                # 消息显示区
                self.message_display,
                # 输入区
                self.input_area,
            ],
            spacing=0,
            expand=True,
        )

    def _create_header(self) -> ft.Container:
        """
        创建顶部标题栏

        Returns:
            标题栏容器
        """
        return ft.Container(
            content=ft.Row(
                [
                    ft.Icon(ft.Icons.CHAT_ROUNDED, size=24, color=ft.Colors.BLUE_400),
                    ft.Text(
                        "AI 对话助手",
                        size=18,
                        weight=ft.FontWeight.BOLD,
                    ),
                    ft.Container(expand=True),
                    # 清空对话按钮
                    ft.IconButton(
                        icon=ft.Icons.DELETE_SWEEP_ROUNDED,
                        tooltip="清空对话",
                        icon_size=20,
                        on_click=self._handle_clear_chat,
                    ),
                    ft.IconButton(
                        icon=ft.Icons.SETTINGS_ROUNDED,
                        tooltip="设置",
                        icon_size=20,
                        on_click=self._handle_settings,
                    ),
                ],
                spacing=10,
            ),
            padding=ft.padding.all(15),
        )

    def _handle_clear_chat(self, _e: ft.ControlEvent):
        """处理清空对话"""
        # 清空消息显示区
        self.message_display.message_list.clear_messages()

        # 添加欢迎消息
        self.message_display.message_list.add_message(
            MessageRole.SYSTEM,
            "对话已清空！我是 NovelPanel AI 助手，有什么可以帮您的吗？",
        )

        # 显示通知
        if self.page:
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text("对话已清空"),
                duration=1000,
            )
            self.page.snack_bar.open = True
            self.page.update()

    def _handle_send_message(self, message: str):
        """
        处理发送消息

        Args:
            message: 用户消息内容
        """
        # 添加用户消息
        self.message_display.message_list.add_message(MessageRole.USER, message)

        # 显示正在输入指示器
        typing_indicator = self.message_display.message_list.add_typing_indicator()

        # 使用异步方式模拟 AI 响应
        import asyncio
        
        async def simulate_ai_response():
            # 模拟思考时间
            await asyncio.sleep(1.5)
            
            # 在主线程更新 UI
            if self.page:
                # 移除指示器
                self.message_display.message_list.remove_typing_indicator(typing_indicator)
                
                # 添加 AI 响应
                response = self._generate_mock_response(message)
                self.message_display.message_list.add_message(
                    MessageRole.ASSISTANT, response
                )
        
        # 使用 page 的事件循环运行异步任务
        if self.page:
            asyncio.create_task(simulate_ai_response())

    def _generate_mock_response(self, user_message: str) -> str:
        """
        生成模拟响应（演示用）

        Args:
            user_message: 用户消息

        Returns:
            模拟的 AI 响应
        """
        # 简单的关键词匹配响应
        message_lower = user_message.lower()

        if any(keyword in message_lower for keyword in ["角色", "人物", "character"]):
            return (
                "关于角色管理，NovelPanel 提供了完整的功能：\n\n"
                "- **自动提取**：AI 可以从小说中自动识别主要角色\n"
                "- **标签系统**：为每个角色添加外貌、性格等标签\n"
                "- **SD 标签**：自动转换为 Stable Diffusion 提示词\n"
                "- **一致性保证**：确保同一角色在不同图像中保持一致\n\n"
                "您可以在角色管理页面查看和编辑所有角色信息。"
            )
        elif any(
            keyword in message_lower for keyword in ["提示词", "prompt", "生成"]
        ):
            return (
                "关于提示词生成，有以下建议：\n\n"
                "## 基础结构\n"
                "```\n"
                "质量标签 + 角色描述 + 场景描述 + 风格标签\n"
                "```\n\n"
                "## 质量标签推荐\n"
                "- `masterpiece, best quality, detailed`\n"
                "- `highly detailed, 4k, sharp focus`\n\n"
                "## 负面提示词\n"
                "- `nsfw, low quality, blurry, distorted`\n\n"
                "系统会根据您的小说内容自动生成优化的提示词！"
            )
        elif any(keyword in message_lower for keyword in ["模型", "lora", "checkpoint"]):
            return (
                "关于模型选择：\n\n"
                "**Checkpoint 模型**：\n"
                "- 动漫风格：建议使用 Anything、NAI 系列\n"
                "- 真实风格：建议使用 Realistic Vision、DreamShaper\n\n"
                "**LoRA 模型**：\n"
                "- 用于强化特定风格或角色特征\n"
                "- 权重建议：0.6-0.8 之间\n\n"
                "您可以在模型管理页面浏览所有可用模型！"
            )
        else:
            return (
                f"收到您的消息：「{user_message}」\n\n"
                "我是 NovelPanel AI 助手，可以帮助您：\n"
                "- 分析小说内容和结构\n"
                "- 管理角色和世界观设定\n"
                "- 生成和优化 SD 提示词\n"
                "- 解答使用问题\n\n"
                "请告诉我更具体的需求，我会尽力帮助您！😊"
            )

    def _handle_settings(self, _e: ft.ControlEvent):
        """处理设置按钮点击"""
        if self.page:
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text("聊天设置功能即将推出"),
                duration=1500,
            )
            self.page.snack_bar.open = True
            self.page.update()

