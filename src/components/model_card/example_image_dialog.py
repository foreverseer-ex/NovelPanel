"""
模型示例图片对话框。

以网格形式展示已缓存的示例图，点击单项可查看对应生成参数；
图片与参数均由 LocalModelMetaService 的本地缓存加载。
"""
import flet as ft
from flet_toast import flet_toast
from flet_toast.Types import Position
from schemas.model_meta import ModelMeta
from components.async_media import AsyncMedia
from constants.ui import (
    DIALOG_WIDE_WIDTH, DIALOG_WIDE_HEIGHT,
    THUMBNAIL_WIDTH, THUMBNAIL_HEIGHT,
    LARGE_IMAGE_WIDTH, LARGE_IMAGE_HEIGHT,
    SPACING_SMALL, SPACING_MEDIUM,
    LOADING_SIZE_MEDIUM, LOADING_SIZE_LARGE,
    DETAIL_INFO_MIN_WIDTH,
)


class ExampleImageDialog(ft.AlertDialog):
    """示例图片对话框类。"""
    
    def __init__(self, model_meta: ModelMeta):
        """初始化示例图片对话框。
        
        :param model_meta: 模型元数据对象
        """
        super().__init__()
        self.model_meta = model_meta
        
        # 状态管理
        self._view = 0  # 0: 网格视图, 1: 详情视图
        self._selected_index = -1
        self._image_containers = []  # 存储每张图片的 AsyncImage 控件
        self._total_examples = len(model_meta.examples) if model_meta.examples else 0
        
        # 配置对话框属性
        self.modal = True
        
        # 标题栏组件
        self.back_button = ft.IconButton(
            icon=ft.Icons.ARROW_BACK,
            on_click=self._back_to_list,
            visible=False,  # 初始不可见
            tooltip="返回",
        )
        self.title_text = ft.Text("示例图片", size=18, weight=ft.FontWeight.BOLD)
        self.close_button = ft.IconButton(
            icon=ft.Icons.CLOSE,
            on_click=self._close,
            tooltip="关闭",
        )
        
        # 构建标题栏：左侧返回按钮 + 中间标题 + 右侧关闭按钮
        self.title = ft.Row(
            controls=[
                self.back_button,
                ft.Container(content=self.title_text, expand=True),
                self.close_button,
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )
        
        # 构建内容容器（增大尺寸以容纳更大的图片）
        self.content_container = ft.Container(width=DIALOG_WIDE_WIDTH, height=DIALOG_WIDE_HEIGHT)
        self.content = self.content_container
        
        # 移除底部按钮
        self.actions = []
        
        # 初始渲染（直接显示网格占位）
        self._render_grid_with_placeholders()
    
    def _render_grid_with_placeholders(self):
        """渲染图片网格占位（使用 AsyncImage）。"""
        if not self.model_meta.examples:
            self.content_container.content = ft.Container(
                content=ft.Text("无示例图片", size=16, color=ft.Colors.GREY_400),
                alignment=ft.alignment.center,
            )
            return
        
        # 为每个示例创建 AsyncImage（大尺寸展示）
        self._image_containers = []
        tiles = []
        for idx in range(len(self.model_meta.examples)):
            # 使用 AsyncImage 组件
            async_img = AsyncMedia(
                model_meta=self.model_meta,
                index=idx,
                width=THUMBNAIL_WIDTH,
                height=THUMBNAIL_HEIGHT,
                on_click=lambda e, i=idx: self._enter_detail(e, i),
                border_radius=8,
                loading_size=LOADING_SIZE_MEDIUM,
                loading_text="加载中",
                loading_text_size=12,
            )
            self._image_containers.append(async_img)
            tiles.append(async_img)
        
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
        """渲染详情视图：根据图片宽高比决定布局（上图下详情 或 左图右详情）。"""
        idx = self._selected_index
        if 0 <= idx < len(self.model_meta.examples):
            ex = self.model_meta.examples[idx]
            
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
            
            # 创建大图预览（使用 AsyncImage）
            self.large_image_control = AsyncMedia(
                model_meta=self.model_meta,
                index=idx,
                width=LARGE_IMAGE_WIDTH,
                height=LARGE_IMAGE_HEIGHT,
                border_radius=8,
                loading_size=LOADING_SIZE_LARGE,
                loading_text="",
            )
            
            # 图片行：左按钮 + 图片 + 右按钮
            self.image_row = ft.Row(
                controls=[
                    prev_button,
                    ft.Container(
                        content=self.large_image_control,
                        expand=True,
                    ),
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
                    """复制值到剪贴板并显示提示"""
                    if self.page:
                        self.page.set_clipboard(value)
                        # 如果值太长，只显示前 50 个字符
                        display_value = value if len(value) <= 50 else f"{value[:47]}..."
                        flet_toast.sucess(
                            page=self.page,
                            message=f"✅ 已复制: {display_value}",
                            position=Position.TOP_RIGHT,
                            duration=2
                        )
                
                # 显示值：如果超过 50 字符，显示为省略号
                display_value = value if len(value) <= 50 else f"{value[:47]}..."
                
                # 标签和值都可以点击复制（使用 Container 包裹以实现点击效果）
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
            
            args = ex.args
            param_rows = [
                _make_row("基础模型", args.model),
                _make_row("正面提示词", args.prompt if args.prompt else "无"),
                _make_row("负面提示词", args.negative_prompt if args.negative_prompt else "无"),
                _make_row(
                    "生成参数",
                    f"CFG: {args.cfg_scale} | 采样器: {args.sampler} | 步数: {args.steps} | 种子: {args.seed} | 尺寸: {args.width}×{args.height}"
                ),
            ]
            
            # 计算宽高比
            aspect_ratio = args.width / args.height if args.height > 0 else 1.5
            
            if aspect_ratio > 1.0:
                # 宽图：使用垂直布局（上图下详情）
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
                # 方图或高图：使用水平布局（左图右详情）
                # 构建“左侧：向左按钮 + 图片”
                image_with_left_nav = ft.Row(
                    controls=[
                        prev_button,
                        ft.Container(
                            content=self.large_image_control,
                            width=LARGE_IMAGE_WIDTH,
                        ),
                    ],
                    spacing=10,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                )

                # 详情区：每个字段上下两行（标题在上，值在下），均可点击复制
                def _make_item_vertical(label: str, value: str) -> ft.Container:
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
                    return ft.Container(
                        content=ft.Column(
                            controls=[
                                ft.Container(
                                    content=ft.Text(f"{label}:", weight=ft.FontWeight.BOLD),
                                    on_click=_copy_to_clipboard,
                                    tooltip=f"点击复制 {label}",
                                    padding=ft.padding.symmetric(horizontal=0, vertical=2),
                                ),
                                ft.Container(
                                    content=ft.Text(value if len(value) <= 200 else value[:197] + "..."),
                                    on_click=_copy_to_clipboard,
                                    tooltip="点击复制（完整内容）" if len(value) > 50 else "点击复制",
                                    padding=ft.padding.symmetric(horizontal=5, vertical=2),
                                ),
                            ],
                            tight=True,
                            spacing=2,
                        )
                    )

                param_items_vertical = [
                    _make_item_vertical("基础模型", args.model),
                    _make_item_vertical("正面提示词", args.prompt if args.prompt else "无"),
                    _make_item_vertical("负面提示词", args.negative_prompt if args.negative_prompt else "无"),
                    _make_item_vertical(
                        "生成参数",
                        f"CFG: {args.cfg_scale} | 采样器: {args.sampler} | 步数: {args.steps} | 种子: {args.seed} | 尺寸: {args.width}×{args.height}"
                    ),
                ]

                self.content_container.content = ft.Row(
                    controls=[
                        image_with_left_nav,
                        ft.VerticalDivider(width=1),
                        ft.Container(
                            content=ft.Column(
                                controls=param_items_vertical,
                                tight=True,
                                spacing=SPACING_SMALL,
                                scroll=ft.ScrollMode.AUTO,
                            ),
                            expand=True,
                            padding=ft.padding.symmetric(horizontal=SPACING_SMALL),
                            width=DETAIL_INFO_MIN_WIDTH,
                        ),
                        next_button,
                    ],
                    expand=True,
                    spacing=SPACING_SMALL,
                )
        else:
            self.content_container.content = ft.Text("未选择示例")
    
    def _go_previous(self, e: ft.ControlEvent):
        """切换到上一张图片。"""
        if self._selected_index > 0:
            self._selected_index -= 1
            self._update_detail_content()
            if e.page:
                e.page.update()
    
    def _go_next(self, e: ft.ControlEvent):
        """切换到下一张图片。"""
        if self._selected_index < self._total_examples - 1:
            self._selected_index += 1
            self._update_detail_content()
            if e.page:
                e.page.update()
    
    def _update_detail_content(self):
        """更新详情视图的内容（切换图片时调用）。"""
        idx = self._selected_index
        if 0 <= idx < len(self.model_meta.examples):
            ex = self.model_meta.examples[idx]
            
            # 更新按钮状态
            self.image_row.controls[0].disabled = idx == 0  # prev_button
            self.image_row.controls[2].disabled = idx >= self._total_examples - 1  # next_button
            
            # 重新创建 AsyncImage 以刷新图片
            self.large_image_control = AsyncMedia(
                model_meta=self.model_meta,
                index=idx,
                width=LARGE_IMAGE_WIDTH,
                height=LARGE_IMAGE_HEIGHT,
                border_radius=8,
                loading_size=LOADING_SIZE_LARGE,
                loading_text="",
            )
            self.image_row.controls[1] = ft.Container(
                content=self.large_image_control,
                expand=True,
            )
            
            # 更新参数信息
            def _make_row(label: str, value: str) -> ft.Row:
                """创建一行标签-值对，支持点击复制。"""
                def _copy_to_clipboard(_e):
                    """复制值到剪贴板并显示提示"""
                    if self.page:
                        self.page.set_clipboard(value)
                        # 如果值太长，只显示前 50 个字符
                        display_value = value if len(value) <= 50 else f"{value[:47]}..."
                        flet_toast.sucess(
                            page=self.page,
                            message=f"✅ 已复制: {display_value}",
                            position=Position.TOP_RIGHT,
                            duration=2
                        )
                
                # 显示值：如果超过 50 字符，显示为省略号
                display_value = value if len(value) <= 50 else f"{value[:47]}..."
                
                # 标签和值都可以点击复制（使用 Container 包裹以实现点击效果）
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
            
            args = ex.args
            param_rows = [
                _make_row("基础模型", args.model),
                _make_row("正面提示词", args.prompt if args.prompt else "无"),
                _make_row("负面提示词", args.negative_prompt if args.negative_prompt else "无"),
                _make_row(
                    "生成参数",
                    f"CFG: {args.cfg_scale} | 采样器: {args.sampler} | 步数: {args.steps} | 种子: {args.seed} | 尺寸: {args.width}×{args.height}"
                ),
            ]
            
            # 计算宽高比
            aspect_ratio = args.width / args.height if args.height > 0 else 1.5
            
            if aspect_ratio > 1.0:
                # 宽图：使用垂直布局（上图下详情）
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
                # 方图或高图：使用水平布局（左图右详情）
                # 重新构建“左侧：向左按钮 + 图片”
                image_with_left_nav = ft.Row(
                    controls=[
                        self.image_row.controls[0],  # prev_button
                        ft.Container(
                            content=self.large_image_control,
                            width=LARGE_IMAGE_WIDTH,
                        ),
                    ],
                    spacing=10,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                )

                # 右侧详情
                detail_container = ft.Container(
                    content=ft.Column(
                        controls=param_rows,
                        tight=True,
                        spacing=SPACING_SMALL,
                        scroll=ft.ScrollMode.AUTO,
                    ),
                    expand=True,
                    padding=ft.padding.only(left=SPACING_SMALL),
                )

                # 总布局：左按钮，图片，详情，右按钮
                self.content_container.content = ft.Row(
                    controls=[
                        image_with_left_nav,
                        ft.VerticalDivider(width=1),
                        detail_container,
                        self.image_row.controls[2],  # next_button
                    ],
                    expand=True,
                    spacing=SPACING_SMALL,
                )
    
    def _enter_detail(self, e: ft.ControlEvent, index: int):
        """进入示例图片详情视图。
        
        :param e: 控件事件对象
        :param index: 选中的示例图片索引
        """
        self._selected_index = index
        self._view = 1
        self.title_text.value = "示例详情"
        self.back_button.visible = True  # 显示返回按钮
        self._render_detail()
        if e.page:
            e.page.update()
    
    def _back_to_list(self, e: ft.ControlEvent):
        """返回示例图片列表视图。
        
        :param e: 控件事件对象
        """
        self._view = 0
        self._selected_index = -1
        self.title_text.value = "示例图片"
        self.back_button.visible = False  # 隐藏返回按钮
        self._render_grid_with_placeholders()
        if e.page:
            e.page.update()
    
    def _close(self, e: ft.ControlEvent):
        """关闭对话框并重置状态。
        
        :param e: 控件事件对象
        """
        # 重置状态
        self._view = 0
        self._selected_index = -1
        self._image_containers = []
        self.back_button.visible = False  # 重置返回按钮
        
        if e.page:
            e.page.close(self)
