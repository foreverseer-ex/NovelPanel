"""
Actor 示例图（立绘）对话框。

以网格形式展示示例图，点击单项可查看大图和详细参数。
"""
import flet as ft
from flet_toast import flet_toast
from flet_toast.Types import Position

from schemas.actor import Actor, ActorExample
from schemas.draw import DrawArgs
from constants.ui import (
    DIALOG_WIDE_WIDTH, DIALOG_WIDE_HEIGHT,
    THUMBNAIL_WIDTH, THUMBNAIL_HEIGHT,
    LARGE_IMAGE_WIDTH, LARGE_IMAGE_HEIGHT,
    SPACING_SMALL, SPACING_MEDIUM,
)


class ActorExampleDialog(ft.AlertDialog):
    """Actor 示例图对话框类。"""
    
    def __init__(self, actor: Actor):
        """初始化示例图对话框。
        
        :param actor: Actor 对象
        """
        super().__init__()
        self.actor = actor
        
        # 状态管理
        self._view = 0  # 0: 网格视图, 1: 详情视图
        self._selected_index = -1
        self._total_examples = len(actor.examples) if actor.examples else 0
        
        # 配置对话框属性
        self.modal = True
        
        # 标题栏组件
        self.back_button = ft.IconButton(
            icon=ft.Icons.ARROW_BACK,
            on_click=self._back_to_list,
            visible=False,
            tooltip="返回",
        )
        self.title_text = ft.Text(f"{actor.name} - 示例图", size=18, weight=ft.FontWeight.BOLD)
        self.close_button = ft.IconButton(
            icon=ft.Icons.CLOSE,
            on_click=self._close,
            tooltip="关闭",
        )
        
        # 构建标题栏
        self.title = ft.Row(
            controls=[
                self.back_button,
                ft.Container(content=self.title_text, expand=True),
                self.close_button,
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )
        
        # 构建内容容器
        self.content_container = ft.Container(width=DIALOG_WIDE_WIDTH, height=DIALOG_WIDE_HEIGHT)
        self.content = self.content_container
        
        # 移除底部按钮
        self.actions = []
        
        # 初始渲染
        self._render_grid()
    
    def _render_grid(self):
        """渲染图片网格视图。"""
        if not self.actor.examples:
            self.content_container.content = ft.Container(
                content=ft.Text("无示例图", size=16, color=ft.Colors.GREY_400),
                alignment=ft.alignment.center,
            )
            return
        
        # 为每个示例创建占位符
        tiles = []
        for idx, example_dict in enumerate(self.actor.examples):
            # 解析示例数据
            example = ActorExample(**example_dict)
            
            # 创建缩略图占位符
            tile = ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Icon(ft.Icons.IMAGE, size=48, color=ft.Colors.GREY_400),
                        ft.Text(example.title, size=12, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                width=THUMBNAIL_WIDTH,
                height=THUMBNAIL_HEIGHT,
                bgcolor=ft.Colors.GREY_200,
                border_radius=8,
                alignment=ft.alignment.center,
                on_click=lambda e, i=idx: self._enter_detail(e, i),
            )
            tiles.append(tile)
        
        # 使用 Row + wrap=True 实现 flow layout
        flow_layout = ft.Row(
            controls=tiles,
            wrap=True,
            run_spacing=SPACING_MEDIUM,
            spacing=SPACING_MEDIUM,
            alignment=ft.MainAxisAlignment.START,
            vertical_alignment=ft.CrossAxisAlignment.START,
        )
        self.content_container.content = ft.Column(
            controls=[flow_layout],
            scroll=ft.ScrollMode.AUTO,
        )
    
    def _render_detail(self):
        """渲染详情视图。"""
        idx = self._selected_index
        if 0 <= idx < len(self.actor.examples):
            example_dict = self.actor.examples[idx]
            example = ActorExample(**example_dict)
            
            # 左右导航按钮
            prev_button = ft.ElevatedButton(
                content=ft.Icon(ft.Icons.CHEVRON_LEFT, size=40),
                on_click=self._go_previous,
                tooltip="上一张图片",
                disabled=idx == 0,
                style=ft.ButtonStyle(
                    shape=ft.RoundedRectangleBorder(radius=10),
                    padding=ft.padding.symmetric(horizontal=15, vertical=80),
                ),
                width=70,
            )
            
            next_button = ft.ElevatedButton(
                content=ft.Icon(ft.Icons.CHEVRON_RIGHT, size=40),
                on_click=self._go_next,
                tooltip="下一张图片",
                disabled=idx >= self._total_examples - 1,
                style=ft.ButtonStyle(
                    shape=ft.RoundedRectangleBorder(radius=10),
                    padding=ft.padding.symmetric(horizontal=15, vertical=80),
                ),
                width=70,
            )
            
            # 创建大图占位符
            large_image = ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Icon(ft.Icons.IMAGE, size=96, color=ft.Colors.GREY_400),
                        ft.Text(example.title, size=14),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                width=LARGE_IMAGE_WIDTH,
                height=LARGE_IMAGE_HEIGHT,
                bgcolor=ft.Colors.GREY_200,
                border_radius=8,
                alignment=ft.alignment.center,
            )
            
            # 图片行：左按钮 + 图片 + 右按钮
            self.image_row = ft.Row(
                controls=[
                    prev_button,
                    ft.Container(content=large_image, expand=True),
                    next_button,
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10,
            )
            
            # 构建参数信息行
            def _make_row(label: str, value: str) -> ft.Row:
                """创建一行标签-值对，支持点击复制。"""
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
                
                display_value = value if len(value) <= 50 else f"{value[:47]}..."
                
                label_control = ft.Container(
                    content=ft.Text(f"{label}:", weight=ft.FontWeight.BOLD),
                    on_click=_copy_to_clipboard,
                    tooltip=f"点击复制 {label}",
                    width=100,
                    padding=ft.padding.symmetric(horizontal=0, vertical=2),
                )
                
                value_control = ft.Container(
                    content=ft.Text(display_value),
                    on_click=_copy_to_clipboard,
                    tooltip="点击复制（完整内容）" if len(value) > 50 else "点击复制",
                    expand=True,
                    padding=ft.padding.symmetric(horizontal=5, vertical=2),
                )
                
                return ft.Row(
                    controls=[label_control, value_control],
                    spacing=10,
                )
            
            args = example.draw_args
            param_rows = [
                _make_row("标题", example.title),
                _make_row("说明", example.desc),
                _make_row("图片路径", example.image_path),
                ft.Divider(),
                _make_row("基础模型", args.model),
                _make_row("正面提示词", args.prompt if args.prompt else "无"),
                _make_row("负面提示词", args.negative_prompt if args.negative_prompt else "无"),
                _make_row(
                    "生成参数",
                    f"CFG: {args.cfg_scale} | 采样器: {args.sampler} | 步数: {args.steps} | 种子: {args.seed} | 尺寸: {args.width}×{args.height}"
                ),
            ]
            
            # 垂直布局（上图下详情）
            self.content_container.content = ft.Column(
                controls=[
                    self.image_row,
                    ft.Divider(height=1, color=ft.Colors.GREY_400),
                    ft.Container(
                        content=ft.Column(
                            controls=param_rows,
                            tight=True,
                            spacing=SPACING_SMALL,
                        ),
                        padding=ft.padding.only(top=SPACING_SMALL),
                    ),
                ],
                scroll=ft.ScrollMode.AUTO,
                width=DIALOG_WIDE_WIDTH,
                spacing=SPACING_MEDIUM,
            )
        else:
            self.content_container.content = ft.Text("未选择示例")
    
    def _go_previous(self, e: ft.ControlEvent):
        """切换到上一张图片。"""
        if self._selected_index > 0:
            self._selected_index -= 1
            self._render_detail()
            if e.page:
                e.page.update()
    
    def _go_next(self, e: ft.ControlEvent):
        """切换到下一张图片。"""
        if self._selected_index < self._total_examples - 1:
            self._selected_index += 1
            self._render_detail()
            if e.page:
                e.page.update()
    
    def _enter_detail(self, e: ft.ControlEvent, index: int):
        """进入示例图片详情视图。"""
        self._selected_index = index
        self._view = 1
        self.title_text.value = f"{self.actor.name} - 示例详情"
        self.back_button.visible = True
        self._render_detail()
        if e.page:
            e.page.update()
    
    def _back_to_list(self, e: ft.ControlEvent):
        """返回示例图片列表视图。"""
        self._view = 0
        self._selected_index = -1
        self.title_text.value = f"{self.actor.name} - 示例图"
        self.back_button.visible = False
        self._render_grid()
        if e.page:
            e.page.update()
    
    def _close(self, e: ft.ControlEvent):
        """关闭对话框并重置状态。"""
        self._view = 0
        self._selected_index = -1
        self.back_button.visible = False
        
        if e.page:
            e.page.close(self)

