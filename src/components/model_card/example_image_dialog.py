"""
模型示例图片对话框。

以网格形式展示已缓存的示例图，点击单项可查看对应生成参数；
图片与参数均由 ModelMetaService 的本地缓存加载。
"""
import flet as ft
from schemas.model_meta import ModelMeta
from components.async_image import AsyncImage
from constants.ui_size import (
    DIALOG_WIDE_WIDTH, DIALOG_WIDE_HEIGHT,
    THUMBNAIL_WIDTH, THUMBNAIL_HEIGHT,
    LARGE_IMAGE_WIDTH, LARGE_IMAGE_HEIGHT,
    SPACING_SMALL, SPACING_MEDIUM,
    LOADING_SIZE_MEDIUM, LOADING_SIZE_LARGE,
    GRID_COL_4,
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
            async_img = AsyncImage(
                model_meta=self.model_meta,
                index=idx,
                width=THUMBNAIL_WIDTH,
                height=THUMBNAIL_HEIGHT,
                fit=ft.ImageFit.COVER,
                on_click=lambda e, i=idx: self._enter_detail(e, i),
                border_radius=8,
                loading_size=LOADING_SIZE_MEDIUM,
                loading_text="加载中",
                loading_text_size=12,
            )
            self._image_containers.append(async_img)
            tiles.append(async_img)
        
        grid = ft.ResponsiveRow(
            controls=[
                ft.Container(content=t, col=GRID_COL_4)
                for t in tiles
            ],
            run_spacing=SPACING_MEDIUM,
            spacing=SPACING_MEDIUM,
        )
        self.content_container.content = ft.Column(
            controls=[grid],
            scroll=ft.ScrollMode.AUTO,
        )
    
    def _render_detail(self):
        """渲染详情视图：顶部显示大图，下方显示生成参数。"""
        idx = self._selected_index
        if 0 <= idx < len(self.model_meta.examples):
            ex = self.model_meta.examples[idx]
            
            # 创建大图预览（使用 AsyncImage）
            large_image = AsyncImage(
                model_meta=self.model_meta,
                index=idx,
                width=LARGE_IMAGE_WIDTH,
                height=LARGE_IMAGE_HEIGHT,
                fit=ft.ImageFit.CONTAIN,  # 使用 CONTAIN 以保持完整图片
                border_radius=8,
                loading_size=LOADING_SIZE_LARGE,
                loading_text="",
            )
            
            # 构建参数信息行（参考 ModelDetailDialog 的样式）
            def _make_row(label: str, value: str) -> ft.Row:
                """创建一行标签-值对。"""
                return ft.Row(
                    controls=[
                        ft.Text(f"{label}:", weight=ft.FontWeight.BOLD, width=100),
                        ft.Text(value, selectable=True, expand=True),
                    ],
                    spacing=10,
                )
            
            args = ex.args
            param_rows = [
                # 第一行：基础模型
                _make_row("基础模型", args.model),
                
                # 第二行：正面提示词
                _make_row("正面提示词", args.prompt if args.prompt else "无"),
                
                # 第三行：负面提示词
                _make_row("负面提示词", args.negative_prompt if args.negative_prompt else "无"),
                
                # 第四行：参数汇总（cfg、采样器、步数、种子、尺寸）
                _make_row(
                    "生成参数",
                    f"CFG: {args.cfg_scale} | 采样器: {args.sampler} | 步数: {args.steps} | 种子: {args.seed} | 尺寸: {args.width}×{args.height}"
                ),
            ]
            
            # 组合布局：大图在上，参数在下（表单风格）
            self.content_container.content = ft.Column(
                controls=[
                    # 大图容器（靠上对齐，表单风格）
                    ft.Container(
                        content=large_image,
                        alignment=ft.alignment.top_center,
                        padding=ft.padding.only(bottom=SPACING_MEDIUM),
                    ),
                    # 分隔线
                    ft.Divider(height=1, color=ft.Colors.GREY_400),
                    # 参数列表（表单风格，无标题）
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
                spacing=0,
            )
        else:
            self.content_container.content = ft.Text("未选择示例")
    
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
