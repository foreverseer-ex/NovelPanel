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
        
        # 使用固定的会话 ID，以便重启后能加载历史记录
        self.session_id = "default"

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
    
    def did_mount(self):
        """组件挂载后加载历史记录"""
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
            assistant_message = None
            
            try:
                # 流式获取响应
                async for chunk in self.llm_service.chat(message, self.session_id):
                    response_text += chunk
                    
                    # 在主线程更新 UI
                    if self.page:
                        # 如果是第一个 chunk，移除指示器并创建助手消息
                        if assistant_message is None:
                            self.message_display.message_list.remove_typing_indicator(typing_indicator)
                            assistant_message = self.message_display.message_list.add_message(
                                MessageRole.ASSISTANT, ""  # 先创建空消息
                            )
                        
                        # 更新助手消息内容（流式输出效果）
                        assistant_message.update_content(response_text)
                
                # 如果没有收到任何响应
                if not response_text:
                    if self.page:
                        self.message_display.message_list.remove_typing_indicator(typing_indicator)
                        self.message_display.message_list.add_message(
                            MessageRole.SYSTEM,
                            "⚠️ 未收到响应，请检查 LLM 配置和网络连接。"
                        )
                        
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


