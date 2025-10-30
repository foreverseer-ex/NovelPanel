"""
Actor 卡片组件。

展示 Actor 的基本信息和缩略图。
"""
import flet as ft
from loguru import logger

from schemas.actor import Actor
from constants.ui_size import CARD_WIDTH, CARD_HEIGHT, SPACING_SMALL
from .actor_detail_dialog import ActorDetailDialog
from .actor_example_dialog import ActorExampleDialog


class ActorCard(ft.Card):
    """Actor 卡片组件。"""
    
    def __init__(self, actor: Actor, all_actors: list[Actor] = None, index: int = 0):
        """初始化 Actor 卡片。
        
        :param actor: Actor 对象
        :param all_actors: 所有 Actor 列表（用于详情对话框的切换）
        :param index: 当前 Actor 在列表中的索引
        """
        super().__init__()
        self.actor = actor
        self.all_actors = all_actors or [actor]
        self.index = index
        
        # 配置卡片样式
        self.elevation = 2
        self.width = CARD_WIDTH
        self.height = CARD_HEIGHT
        
        # 使用 Actor 的颜色作为边框颜色
        try:
            border_color = actor.color if actor.color else "#808080"
            self.surface_tint_color = border_color
        except:
            self.surface_tint_color = "#808080"
        
        # 构建卡片内容
        self.content = self._build_content()
    
    def _build_content(self) -> ft.Container:
        """构建卡片内容。"""
        # Actor 名称
        name_text = ft.Text(
            self.actor.name,
            size=16,
            weight=ft.FontWeight.BOLD,
            max_lines=1,
            overflow=ft.TextOverflow.ELLIPSIS,
        )
        
        # Actor 描述
        desc_text = ft.Text(
            self.actor.desc if self.actor.desc else "无描述",
            size=12,
            color=ft.Colors.GREY_600,
            max_lines=2,
            overflow=ft.TextOverflow.ELLIPSIS,
        )
        
        # 示例图数量
        example_count = len(self.actor.examples) if self.actor.examples else 0
        example_info = ft.Row(
            controls=[
                ft.Icon(ft.Icons.IMAGE, size=16, color=ft.Colors.BLUE_400),
                ft.Text(f"{example_count} 张示例图", size=12, color=ft.Colors.GREY_600),
            ],
            spacing=5,
        )
        
        # 标签数量
        tag_count = len(self.actor.tags) if self.actor.tags else 0
        tag_info = ft.Row(
            controls=[
                ft.Icon(ft.Icons.LABEL, size=16, color=ft.Colors.GREEN_400),
                ft.Text(f"{tag_count} 个标签", size=12, color=ft.Colors.GREY_600),
            ],
            spacing=5,
        )
        
        # 缩略图或占位符
        if example_count > 0:
            # 显示第一张示例图的占位符
            thumbnail = ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Icon(ft.Icons.IMAGE, size=48, color=ft.Colors.GREY_400),
                        ft.Text("点击查看", size=10, color=ft.Colors.GREY_500),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                width=CARD_WIDTH - 20,
                height=120,
                bgcolor=ft.Colors.GREY_200,
                border_radius=8,
                alignment=ft.alignment.center,
                on_click=self._open_example_dialog,
            )
        else:
            thumbnail = ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Icon(ft.Icons.PERSON, size=48, color=ft.Colors.GREY_400),
                        ft.Text("无示例图", size=10, color=ft.Colors.GREY_500),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                width=CARD_WIDTH - 20,
                height=120,
                bgcolor=ft.Colors.GREY_200,
                border_radius=8,
                alignment=ft.alignment.center,
            )
        
        # 信息区域
        info_column = ft.Column(
            controls=[
                name_text,
                desc_text,
                ft.Divider(height=1),
                example_info,
                tag_info,
            ],
            spacing=SPACING_SMALL,
            tight=True,
        )
        
        # 点击卡片打开详情对话框
        content_container = ft.Container(
            content=ft.Column(
                controls=[
                    thumbnail,
                    info_column,
                ],
                spacing=SPACING_SMALL,
                tight=True,
            ),
            padding=10,
            on_click=self._open_detail_dialog,
        )
        
        return content_container
    
    def _open_detail_dialog(self, e: ft.ControlEvent):
        """打开 Actor 详情对话框。"""
        if self.page:
            dialog = ActorDetailDialog(self.actor, self.all_actors, self.index)
            self.page.open(dialog)
    
    def _open_example_dialog(self, e: ft.ControlEvent):
        """打开 Actor 示例图对话框。"""
        e.control.disabled = True  # 防止重复点击
        
        if self.page:
            dialog = ActorExampleDialog(self.actor)
            self.page.open(dialog)
        
        e.control.disabled = False

