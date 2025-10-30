"""
Actor 详情对话框。

展示 Actor 的详细信息。
"""
import flet as ft
from flet_toast import flet_toast
from flet_toast.Types import Position

from schemas.actor import Actor
from constants.ui import (
    DIALOG_STANDARD_WIDTH, DIALOG_STANDARD_HEIGHT,
    SPACING_SMALL, DETAIL_LABEL_WIDTH,
)


class ActorDetailDialog(ft.AlertDialog):
    """Actor 详情对话框类。"""
    
    def __init__(self, actor: Actor, all_actors: list[Actor] = None, current_index: int = 0):
        """初始化 Actor 详情对话框。
        
        :param actor: Actor 对象
        :param all_actors: 所有 Actor 列表（用于切换导航）
        :param current_index: 当前 Actor 在列表中的索引
        """
        super().__init__()
        self.actor = actor
        self.all_actors = all_actors or [actor]
        self.current_index = current_index
        
        # 配置对话框属性
        self.modal = True
        self.width = DIALOG_STANDARD_WIDTH
        self.height = DIALOG_STANDARD_HEIGHT
        
        # 构建标题栏：标题 + 右侧关闭按钮
        self.title_text = ft.Text("Actor 详情", size=18, weight=ft.FontWeight.BOLD)
        self.close_button = ft.IconButton(
            icon=ft.Icons.CLOSE,
            on_click=self._close,
            tooltip="关闭",
        )
        
        self.title = ft.Row(
            controls=[
                ft.Container(content=self.title_text, expand=True),
                self.close_button,
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )
        
        # 构建导航按钮
        self.prev_button = ft.ElevatedButton(
            content=ft.Icon(ft.Icons.CHEVRON_LEFT, size=40),
            on_click=self._go_previous,
            tooltip="上一个 Actor",
            disabled=self.current_index == 0,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=10),
                padding=ft.padding.symmetric(horizontal=15, vertical=80),
            ),
            width=70,
        )
        
        self.next_button = ft.ElevatedButton(
            content=ft.Icon(ft.Icons.CHEVRON_RIGHT, size=40),
            on_click=self._go_next,
            tooltip="下一个 Actor",
            disabled=self.current_index >= len(self.all_actors) - 1,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=10),
                padding=ft.padding.symmetric(horizontal=15, vertical=80),
            ),
            width=70,
        )
        
        # 构建内容
        info_rows = self._build_info_rows()
        
        self.content = ft.Row(
            controls=[
                self.prev_button,
                ft.Container(
                    content=ft.Column(
                        controls=info_rows,
                        tight=True,
                        spacing=SPACING_SMALL,
                        scroll=ft.ScrollMode.AUTO,
                    ),
                    expand=True,
                ),
                self.next_button,
            ],
            spacing=10,
            expand=True,
        )
        
        # 移除底部按钮
        self.actions = []
    
    def _build_info_rows(self) -> list[ft.Row]:
        """构建信息行列表。"""
        actor = self.actor
        
        def _make_row(label: str, value: str) -> ft.Row:
            """创建一行标签-值对（可点击复制）。"""
            def _copy_to_clipboard(_e):
                if self.page:
                    self.page.set_clipboard(value)
                    display_value = value if len(value) <= 50 else f"{value[:47]}..."
                    flet_toast.sucess(
                        page=self.page,
                        message=f"✅ 已复制: {display_value}",
                        position=Position.TOP_RIGHT,
                        duration=2
                    )
            
            display_value = value if len(value) <= 100 else f"{value[:97]}..."
            
            label_control = ft.Container(
                content=ft.Text(f"{label}:", weight=ft.FontWeight.BOLD),
                on_click=_copy_to_clipboard,
                tooltip=f"点击复制 {label}",
                width=DETAIL_LABEL_WIDTH,
                padding=ft.padding.symmetric(horizontal=0, vertical=2),
            )
            
            value_control = ft.Container(
                content=ft.Text(display_value),
                on_click=_copy_to_clipboard,
                tooltip="点击复制（完整内容）" if len(value) > 100 else "点击复制",
                expand=True,
                padding=ft.padding.symmetric(horizontal=5, vertical=2),
            )
            
            return ft.Row(
                controls=[label_control, value_control],
                spacing=10,
            )
        
        # 基础信息行
        rows = [
            _make_row("名称", actor.name),
            _make_row("描述", actor.desc if actor.desc else "无"),
            _make_row("颜色", actor.color if actor.color else "#808080"),
            _make_row("Actor ID", actor.actor_id),
            _make_row("Session ID", actor.session_id),
        ]
        
        # 示例图数量
        example_count = len(actor.examples) if actor.examples else 0
        rows.append(_make_row("示例图数量", str(example_count)))
        
        # 标签信息
        if actor.tags:
            rows.append(ft.Row([ft.Text("标签:", weight=ft.FontWeight.BOLD, width=DETAIL_LABEL_WIDTH)]))
            for key, value in actor.tags.items():
                rows.append(_make_row(f"  {key}", value))
        else:
            rows.append(_make_row("标签", "无"))
        
        return rows
    
    def _go_previous(self, e: ft.ControlEvent):
        """切换到上一个 Actor。"""
        if self.current_index > 0:
            self.current_index -= 1
            self._update_content()
    
    def _go_next(self, e: ft.ControlEvent):
        """切换到下一个 Actor。"""
        if self.current_index < len(self.all_actors) - 1:
            self.current_index += 1
            self._update_content()
    
    def _update_content(self):
        """更新对话框内容以显示当前索引的 Actor。"""
        # 更新当前 Actor
        self.actor = self.all_actors[self.current_index]
        
        # 更新导航按钮状态
        self.prev_button.disabled = self.current_index == 0
        self.next_button.disabled = self.current_index >= len(self.all_actors) - 1
        
        # 重新构建信息行
        info_rows = self._build_info_rows()
        
        self.content = ft.Row(
            controls=[
                self.prev_button,
                ft.Container(
                    content=ft.Column(
                        controls=info_rows,
                        tight=True,
                        spacing=SPACING_SMALL,
                        scroll=ft.ScrollMode.AUTO,
                    ),
                    expand=True,
                ),
                self.next_button,
            ],
            spacing=10,
            expand=True,
        )
        
        # 更新界面
        if self.page:
            self.update()
    
    def _close(self, e: ft.ControlEvent = None):
        """关闭对话框。"""
        page = e.page if e else self.page
        if page:
            page.close(self)

