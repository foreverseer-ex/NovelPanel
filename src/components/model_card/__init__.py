"""
模型卡片 UI 组件。

为给定模型提供预览图与基础信息徽章的卡片展示；
支持打开"示例图片"与"模型详情"对话框。
"""
import flet as ft

from schemas.model_meta import ModelMeta
from constants.color import ModelTypeChipColor, BaseModelColor
from constants.ui_size import (
    THUMBNAIL_WIDTH, THUMBNAIL_HEIGHT,
    CARD_INFO_HEIGHT, CARD_TITLE_HEIGHT, CARD_TITLE_MAX_LINES,
    CHIP_PADDING_H, CHIP_PADDING_V, CHIP_BORDER_RADIUS, CHIP_BORDER_WIDTH, CHIP_TEXT_SIZE,
    SPACING_SMALL,
)
from components.async_image import AsyncImage
from .example_image_dialog import ExampleImageDialog
from .model_detail_dialog import ModelDetailDialog


class ModelCard(ft.Column):
    """模型的可视化卡片，展示关键信息。"""
    def __init__(self, model_meta: ModelMeta, all_models: list[ModelMeta] = None, index: int = 0):
        """初始化模型卡片。
        
        :param model_meta: 模型元数据对象
        :param all_models: 所有模型列表（用于切换导航）
        :param index: 当前模型在列表中的索引
        """
        super().__init__()
        self.model_meta = model_meta
        self.all_models = all_models or [model_meta]
        self.index = index
        self.width = THUMBNAIL_WIDTH  # 固定宽度
        # 使用 AsyncImage 组件
        self.preview_image = AsyncImage(
            model_meta=model_meta,
            index=0,
            width=THUMBNAIL_WIDTH,
            height=THUMBNAIL_HEIGHT,
            on_click=self._open_examples_dialog,
            border_radius=8,
            loading_size=30,
            loading_text="加载中...",
            loading_text_size=12,
        )
        info_control = self._build_info()
        self.controls = [
            ft.Card(
                content=ft.Container(
                    content=ft.Column(
                        controls=[
                            self.preview_image,
                            ft.Container(
                                content=info_control,
                                on_click=self._open_detail_dialog
                            ),
                        ],
                        spacing=8,
                    ),
                    padding=SPACING_SMALL,
                )
            )
        ]

    def _build_info(self):
        """构建标题与徽章，展示模型版本与基础类型。"""
        # 标题：固定高度容器，垂直居中，限制最多2行，超出部分显示省略号
        title = ft.Container(
            content=ft.Text(
                self.model_meta.version_name,
                size=16,
                weight=ft.FontWeight.BOLD,
                max_lines=CARD_TITLE_MAX_LINES,
                overflow=ft.TextOverflow.ELLIPSIS,
                tooltip=self.model_meta.version_name,  # 鼠标悬停显示完整名称
            ),
            height=CARD_TITLE_HEIGHT,  # 固定标题区域高度
            alignment=ft.alignment.center_left,  # 垂直居中，水平左对齐
        )
        
        # 获取基础模型的颜色
        base_model_color = BaseModelColor.get(self.model_meta.base_model)
        
        # 基础模型 chip：占据整行宽度
        base_model_chip = ft.Container(
            content=ft.Text(
                self.model_meta.base_model,
                size=CHIP_TEXT_SIZE,
                color=ft.Colors.WHITE,
                weight=ft.FontWeight.BOLD,
                text_align=ft.TextAlign.CENTER,
            ),
            bgcolor=base_model_color,
            padding=ft.padding.symmetric(horizontal=CHIP_PADDING_H, vertical=CHIP_PADDING_V),
            border_radius=CHIP_BORDER_RADIUS,
            border=ft.border.all(CHIP_BORDER_WIDTH, ft.Colors.with_opacity(0.3, ft.Colors.WHITE)),
            alignment=ft.alignment.center,
        )
        
        # 信息区域：标题 + 基础模型 chip
        return ft.Column(
            controls=[title, base_model_chip],
            spacing=SPACING_SMALL,
            tight=True,  # 紧凑排列，缩小底部间距
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH,  # 子元素横向拉伸填充
        )

    def _open_detail_dialog(self, e: ft.ControlEvent | None = None):
        """打开展示模型详细元数据的对话框。
        
        :param e: 控件事件对象
        """
        dlg = ModelDetailDialog(
            model_meta=self.model_meta,
            all_models=self.all_models,
            current_index=self.index
        )
        page = e.page if e and e.page else self.page
        if page:
            # 打开对话框（AsyncImage 会自动加载）
            page.open(dlg)

    def _open_examples_dialog(self, e: ft.ControlEvent | None = None):
        """打开列出模型示例图片的对话框。
        
        :param e: 控件事件对象
        """
        dlg = ExampleImageDialog(self.model_meta)
        page = e.page if e and e.page else self.page
        if page:
            # 打开对话框（AsyncImage 会自动加载）
            page.open(dlg)
