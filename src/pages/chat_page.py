"""
聊天页面

提供与 AI 交互的界面，帮助用户分析小说、优化提示词等。
"""

import flet as ft
from loguru import logger
from flet_toast import flet_toast
from flet_toast.Types import Position
from components.chat import ChatMessageDisplay, ChatInputArea
from components.chat.chat_message_display import MessageRole
from services.llm import get_current_llm_service


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
        
        # 获取 LLM 服务
        self.llm_service = get_current_llm_service()
        
        # 使用当前选中的会话 ID，如果没有则使用 default
        from settings import app_settings
        self.session_id = app_settings.ui.current_session_id or "default"

        # 创建组件
        self.message_display = ChatMessageDisplay(on_delete_message=self._handle_delete_message)

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
    
    def did_mount(self):
        """组件挂载后加载历史记录"""
        # 更新 session_id（防止用户在主页切换了会话）
        from settings import app_settings
        self.session_id = app_settings.ui.current_session_id or "default"
        
        # 加载历史记录（必须在组件挂载到页面之后）
        self._load_history()
    
    def _load_history(self):
        """加载历史记录并显示在界面上"""
        try:
            if self.llm_service.load_history(self.session_id):
                # 如果成功加载历史记录，显示在界面
                for msg in self.llm_service.history.messages:
                    if msg.role == "user":
                        role = MessageRole.USER
                    elif msg.role == "assistant":
                        role = MessageRole.ASSISTANT
                    else:
                        role = MessageRole.SYSTEM
                    
                    # 调试日志：查看消息结构
                    logger.debug(f"加载消息 - 角色: {msg.role}, 内容数量: {len(msg.messages)}, 选项: {msg.choices}")
                    
                    # 将新格式的消息传递给渲染器（批量加载时不立即更新）
                    self.message_display.message_list.add_message_with_data(role, msg, update_ui=False)
                
                # 批量加载完成后，统一更新 UI
                try:
                    self.message_display.message_list.update()
                    # 自动滚动到底部，显示最新消息
                    self.message_display.message_list.scroll_to_bottom()
                except (AssertionError, AttributeError):
                    # 组件可能还未完全挂载，稍后会自动更新
                    pass
                
                logger.info(f"成功加载 {len(self.llm_service.history.messages)} 条历史消息")
        except Exception as e:
            logger.exception(f"加载历史记录失败: {e}")

    def _create_header(self) -> ft.Container:
        """
        创建顶部标题栏

        Returns:
            标题栏容器
        """
        return ft.Container(
            content=ft.Row(
                [
                    ft.Icon(ft.Icons.BRUSH, size=24, color=ft.Colors.BLUE_400),
                    ft.Text(
                        "NovelPanel 助手",
                        size=18,
                        weight=ft.FontWeight.BOLD,
                    ),
                    ft.Container(expand=True),
                    # 滚动到底部按钮
                    ft.IconButton(
                        icon=ft.Icons.ARROW_DOWNWARD,
                        tooltip="滚动到底部",
                        icon_size=20,
                        icon_color=ft.Colors.BLUE_400,
                        on_click=self._handle_scroll_to_bottom,
                    ),
                    # 清空对话按钮
                    ft.IconButton(
                        icon=ft.Icons.DELETE_SWEEP_ROUNDED,
                        tooltip="清空对话",
                        icon_size=20,
                        on_click=self._handle_clear_chat,
                    ),
                ],
                spacing=10,
            ),
            padding=ft.padding.all(15),
        )

    def _handle_scroll_to_bottom(self, _e: ft.ControlEvent):
        """处理滚动到底部按钮点击"""
        self.message_display.scroll_to_bottom()
    
    def _handle_clear_chat(self, _e: ft.ControlEvent):
        """处理清空对话"""
        # 清空 LLM 服务的历史记录
        self.llm_service.clear_history()
        
        # 清空消息显示区
        self.message_display.message_list.clear_messages()
        
        # 保存清空后的历史记录
        self.llm_service.save_history(self.session_id)

        # 显示通知
        if self.page:
            flet_toast.sucess(
                page=self.page,
                message="对话已清空",
                position=Position.TOP_RIGHT,
                duration=1
            )

    def _handle_delete_message(self, message_widget):
        """
        处理删除消息
        
        Args:
            message_widget: 要删除的消息组件
        """
        try:
            # 获取消息数据
            message_data = message_widget.message_data
            if not message_data:
                logger.warning("消息组件没有关联的数据，无法删除")
                return
            
            # 从历史记录中删除该消息
            if message_data in self.llm_service.history.messages:
                self.llm_service.history.messages.remove(message_data)
                logger.info(f"删除消息: {message_data.role}")
                
                # 保存历史记录
                self.llm_service.save_history(self.session_id)
                
                # 清空 UI 并重新加载
                self.message_display.message_list.clear_messages()
                self._load_history()
                
                # 显示成功提示
                flet_toast.sucess(
                    page=self.page,
                    message="消息已删除",
                    position=Position.TOP_RIGHT,
                    duration=1
                )
            else:
                logger.warning("消息在历史记录中不存在")
        except Exception as e:
            logger.exception(f"删除消息失败: {e}")
            flet_toast.error(
                page=self.page,
                message=f"删除失败: {str(e)}",
                position=Position.TOP_RIGHT,
                duration=2
            )

    def _handle_send_message(self, message: str):
        """
        处理发送消息

        Args:
            message: 用户消息内容
        """
        # 检查 LLM 服务是否就绪
        if not self.llm_service.is_ready():
            # 显示错误消息
            self.message_display.message_list.add_message(
                MessageRole.SYSTEM,
                "❌ LLM 服务未就绪，请在设置页面配置 LLM 参数并确保服务正常启动。"
            )
            return
        
        # 添加用户消息
        self.message_display.message_list.add_message(MessageRole.USER, message)

        # 显示正在输入指示器
        typing_indicator = self.message_display.message_list.add_typing_indicator()

        # 使用异步方式获取 AI 响应
        async def get_ai_response():
            response_text = ""
            assistant_message_widget = None
            last_update_time = 0
            update_interval = 0.1  # 最小更新间隔（秒）
            
            try:
                # 流式获取响应
                async for chunk in self.llm_service.chat(message, self.session_id):
                    response_text += chunk
                    
                    # 在主线程更新 UI（限流，避免过于频繁的更新）
                    if self.page:
                        import time
                        current_time = time.time()
                        
                        # 如果是第一个 chunk，移除指示器并创建助手消息占位符
                        if assistant_message_widget is None:
                            self.message_display.message_list.remove_typing_indicator(typing_indicator)
                            assistant_message_widget = self.message_display.message_list.add_message(
                                MessageRole.ASSISTANT, ""  # 临时占位
                            )
                            last_update_time = current_time
                        
                        # 限流更新：只在间隔足够时才更新UI
                        if current_time - last_update_time >= update_interval:
                            # 实时获取历史记录中的最新助手消息并更新显示
                            if self.llm_service.history.messages:
                                last_msg = self.llm_service.history.messages[-1]
                                if last_msg.role == "assistant":
                                    # 找到并替换占位消息
                                    if assistant_message_widget in self.message_display.message_list.controls:
                                        idx = self.message_display.message_list.controls.index(assistant_message_widget)
                                        # 移除旧的占位消息和分隔线
                                        if idx + 1 < len(self.message_display.message_list.controls):
                                            self.message_display.message_list.controls.pop(idx + 1)  # 分隔线
                                        self.message_display.message_list.controls.pop(idx)  # 占位消息
                                        
                                        # 在相同位置插入完整消息
                                        new_widget = self.message_display.message_list._create_message_widget(
                                            MessageRole.ASSISTANT, last_msg
                                        )
                                        self.message_display.message_list.controls.insert(idx, new_widget)
                                        self.message_display.message_list.controls.insert(idx + 1, ft.Divider(height=1))
                                        
                                        # 更新引用
                                        assistant_message_widget = new_widget
                                        self.page.update()
                            
                            last_update_time = current_time
                
                # 流式输出完成后，最后一次更新以确保显示完整内容
                if assistant_message_widget and self.page:
                    if self.llm_service.history.messages:
                        last_msg = self.llm_service.history.messages[-1]
                        if last_msg.role == "assistant":
                            # 最后一次更新
                            if assistant_message_widget in self.message_display.message_list.controls:
                                idx = self.message_display.message_list.controls.index(assistant_message_widget)
                                if idx + 1 < len(self.message_display.message_list.controls):
                                    self.message_display.message_list.controls.pop(idx + 1)
                                self.message_display.message_list.controls.pop(idx)
                                
                                new_widget = self.message_display.message_list._create_message_widget(
                                    MessageRole.ASSISTANT, last_msg
                                )
                                self.message_display.message_list.controls.insert(idx, new_widget)
                                self.message_display.message_list.controls.insert(idx + 1, ft.Divider(height=1))
                                self.page.update()
                
                # 如果没有收到任何响应
                if not response_text:
                    if self.page:
                        if assistant_message_widget:
                            # 移除占位消息
                            if assistant_message_widget in self.message_display.message_list.controls:
                                idx = self.message_display.message_list.controls.index(assistant_message_widget)
                                if idx + 1 < len(self.message_display.message_list.controls):
                                    self.message_display.message_list.controls.pop(idx + 1)
                                self.message_display.message_list.controls.pop(idx)
                        else:
                            self.message_display.message_list.remove_typing_indicator(typing_indicator)
                        
                        self.message_display.message_list.add_message(
                            MessageRole.SYSTEM,
                            "⚠️ 未收到响应，请检查 LLM 配置和网络连接。"
                        )
                        self.page.update()
                        
            except Exception as e:
                logger.exception(f"获取 AI 响应失败: {e}")
                if self.page:
                    self.message_display.message_list.remove_typing_indicator(typing_indicator)
                    self.message_display.message_list.add_message(
                        MessageRole.SYSTEM,
                        f"❌ 获取响应失败：{e}"
                    )
        
        # 使用 page 的事件循环运行异步任务
        if self.page:
            self.page.run_task(get_ai_response)


