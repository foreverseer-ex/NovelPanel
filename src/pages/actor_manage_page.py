"""
Actor 管理页面。

展示所有 Actor 卡片（包括角色、地点、组织等）。
"""
import flet as ft
from loguru import logger
from flet_toast import flet_toast
from flet_toast.Types import Position

from components.actor_card import ActorCard
from constants.ui_size import SPACING_SMALL, SPACING_MEDIUM
from services.db import ActorService
from settings import app_settings


class ActorManagePage(ft.Column):
    """Actor 管理页面。"""
    
    def __init__(self):
        """初始化 Actor 管理页面。"""
        super().__init__()
        
        # Actor 区域（占位，后面会动态填充）
        self.actor_section = ft.Column(spacing=SPACING_MEDIUM)
        
        # 右上角：创建 Actor 按钮
        self.create_button = ft.IconButton(
            icon=ft.Icons.ADD,
            tooltip="创建 Actor",
            on_click=self._open_create_dialog
        )
        
        
        # 组合布局
        self.controls = [
            ft.Container(
                content=ft.Row(
                    controls=[
                        ft.Container(expand=True),  # 左侧留空
                        self.create_button,
                    ],
                    alignment=ft.MainAxisAlignment.END,
                ),
                padding=ft.padding.only(top=SPACING_SMALL, bottom=SPACING_MEDIUM),
            ),
            self.actor_section,
        ]
        self.expand = True
        self.scroll = ft.ScrollMode.AUTO
        self.alignment = ft.MainAxisAlignment.START
        self.spacing = SPACING_MEDIUM
    
    def did_mount(self):
        """组件挂载后，渲染 Actor 卡。"""
        self._render_actors()
    
    def _open_create_dialog(self, _: ft.ControlEvent):
        """打开创建 Actor 对话框"""
        if not self.page:
            logger.error("self.page 为 None，无法打开对话框")
            return
        
        try:
            # 创建对话框
            dialog = CreateActorDialog(
                session_id=app_settings.ui.current_session_id or "default",
                on_create=lambda name, desc, color: self.page.run_task(self._do_create, name, desc, color),
                on_error=lambda msg: self._show_toast(msg, ft.Colors.RED_700),
            )
            
            # 打开对话框
            self.page.open(dialog)
            logger.info("创建 Actor 对话框已打开")
        except Exception as e:
            logger.exception(f"打开创建对话框失败: {e}")
    
    async def _do_create(self, name: str, desc: str, color: str):
        """执行创建 Actor 任务。"""
        try:
            from schemas.actor import Actor
            import uuid
            
            # 获取当前 session_id
            session_id = app_settings.ui.current_session_id or "default"
            
            # 创建 Actor
            actor = Actor(
                actor_id=str(uuid.uuid4()),
                session_id=session_id,
                name=name,
                desc=desc,
                color=color,
                tags={},
                examples=[]
            )
            
            created = ActorService.create(actor)
            logger.success(f"创建 Actor 成功: {name}")
            
            # 重新渲染
            self._render_actors()
            
            # 显示成功消息
            self._show_toast(f"✅ 创建成功: {name}", ft.Colors.GREEN_700)
        except Exception as ex:
            logger.exception(f"创建 Actor 失败: {ex}")
            self._show_toast(f"❌ 创建失败: {str(ex)}", ft.Colors.RED_700)
    
    def _show_toast(self, message: str, bgcolor=ft.Colors.GREEN_700, duration: int = 3000):
        """显示 Toast 提示。"""
        if self.page:
            duration_sec = duration / 1000
            
            if bgcolor == ft.Colors.GREEN_700:
                flet_toast.sucess(
                    page=self.page,
                    message=message,
                    position=Position.TOP_RIGHT,
                    duration=duration_sec
                )
            elif bgcolor == ft.Colors.RED_700:
                flet_toast.error(
                    page=self.page,
                    message=message,
                    position=Position.TOP_RIGHT,
                    duration=duration_sec
                )
    
    def _render_actors(self):
        """渲染 Actor 卡。"""
        # 获取当前 session 的所有 Actor
        session_id = app_settings.ui.current_session_id or "default"
        all_actors = ActorService.list_by_session(session_id, limit=1000)
        
        actor_cards = [
            ActorCard(actor, all_actors=all_actors, index=all_actors.index(actor))
            for actor in all_actors
        ]
        
        actor_flow = ft.Row(
            controls=actor_cards,
            wrap=True,
            run_spacing=SPACING_SMALL,
            spacing=SPACING_SMALL,
            alignment=ft.MainAxisAlignment.START,
            vertical_alignment=ft.CrossAxisAlignment.START,
        )
        
        # 更新 Actor 区域
        self.actor_section.controls = [
            ft.Text("Actor", size=20, weight=ft.FontWeight.BOLD),
            actor_flow if actor_cards else ft.Text("暂无 Actor，点击右上角 + 创建", size=14, color=ft.Colors.GREY_500),
        ]
        
        # 刷新界面
        self.update()


# ============================================================================
# Dialog 类定义
# ============================================================================

class CreateActorDialog(ft.AlertDialog):
    """创建 Actor 对话框"""
    
    def __init__(self, session_id: str, on_create: callable, on_error: callable):
        """
        初始化创建 Actor 对话框
        
        Args:
            session_id: 会话ID
            on_create: 创建回调函数，接收参数 (name: str, desc: str, color: str)
            on_error: 错误回调函数，接收参数 (message: str)
        """
        self.session_id = session_id
        self.on_create = on_create
        self.on_error = on_error
        
        # 创建输入字段
        self.name_field = ft.TextField(
            label="名称",
            hint_text="如：主角、帝国、纽约",
            autofocus=True,
        )
        
        self.desc_field = ft.TextField(
            label="描述",
            hint_text="简要描述",
            multiline=True,
            min_lines=2,
            max_lines=4,
        )
        
        self.color_field = ft.TextField(
            label="颜色",
            hint_text="如：#FF69B4（粉色）、#4169E1（蓝色）",
            value="#808080",
        )
        
        super().__init__(
            modal=True,
            title=ft.Text("创建 Actor"),
            content=ft.Column([
                ft.Text("提示：", size=12, weight=ft.FontWeight.BOLD),
                ft.Text("• Actor 可以是角色、地点、组织等小说要素", size=11, color=ft.Colors.GREY_600),
                ft.Text("• 颜色建议：女性→粉色 #FF69B4，男性→蓝色 #4169E1，地点→绿色 #228B22", size=11, color=ft.Colors.GREY_600),
                ft.Divider(),
                self.name_field,
                self.desc_field,
                self.color_field,
            ], tight=True, spacing=10, width=400),
            actions=[
                ft.TextButton("取消", on_click=self._on_cancel),
                ft.ElevatedButton("创建", on_click=self._on_confirm),
            ],
        )
    
    def _on_confirm(self, e):
        """确认创建"""
        # 验证输入
        name = self.name_field.value.strip()
        if not name:
            if self.on_error:
                self.on_error("❌ 请输入名称")
            return
        
        desc = self.desc_field.value.strip()
        color = self.color_field.value.strip()
        if not color:
            color = "#808080"
        
        # 验证颜色格式
        if not color.startswith("#") or len(color) != 7:
            if self.on_error:
                self.on_error("❌ 颜色格式错误，应为 #RRGGBB")
            return
        
        # 关闭对话框
        self.open = False
        self.update()
        
        # 调用创建回调
        if self.on_create:
            self.on_create(name, desc, color)
    
    def _on_cancel(self, e):
        """取消创建"""
        self.open = False
        self.update()

