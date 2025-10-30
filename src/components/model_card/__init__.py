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
from components.async_media import AsyncMedia
from .example_image_dialog import ExampleImageDialog
from .model_detail_dialog import ModelDetailDialog


class ModelCard(ft.Column):
    """模型的可视化卡片，展示关键信息。"""
    def __init__(
        self, 
        model_meta: ModelMeta, 
        all_models: list[ModelMeta] = None, 
        index: int = 0,
        on_delete: callable = None
    ):
        """初始化模型卡片。
        
        :param model_meta: 模型元数据对象
        :param all_models: 所有模型列表（用于切换导航）
        :param index: 当前模型在列表中的索引
        :param on_delete: 删除回调函数，接收 model_meta 作为参数
        """
        super().__init__()
        self.model_meta = model_meta
        self.all_models = all_models or [model_meta]
        self.index = index
        self.on_delete_callback = on_delete
        self.width = THUMBNAIL_WIDTH  # 固定宽度
        self.delete_confirm_dialog = None  # 延迟创建
        
        # 获取隐私模式设置
        from settings import app_settings
        privacy_mode = app_settings.ui.privacy_mode
        
        # 使用 AsyncImage 组件
        self.preview_image = AsyncMedia(
            model_meta=model_meta,
            index=0,
            width=THUMBNAIL_WIDTH,
            height=THUMBNAIL_HEIGHT,
            on_click=self._open_examples_dialog,
            border_radius=8,
            loading_size=30,
            loading_text="加载中...",
            loading_text_size=12,
            privacy_mode=privacy_mode,
        )
        info_control = self._build_info()
        
        # 获取基础模型的颜色（用于边框）
        base_model_color = BaseModelColor.get(self.model_meta.base_model)
        
        self.controls = [
            ft.GestureDetector(
                content=ft.Container(
                    content=ft.Card(
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
                        ),
                        elevation=2,  # 轻微阴影
                    ),
                    # ✨ 添加边框，颜色和 chip 一致
                    border=ft.border.all(2, base_model_color),
                    border_radius=10,
                ),
                on_secondary_tap_down=self._on_right_click,  # 右键菜单
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
        
        # 网页链接按钮（如果有）
        controls = [title, base_model_chip]
        if self.model_meta.web_page_url:
            web_link = ft.Container(
                content=ft.Row(
                    [
                        ft.Icon(ft.Icons.OPEN_IN_BROWSER, size=12, color=ft.Colors.BLUE_400),
                        ft.Text(
                            "查看网页",
                            size=11,
                            color=ft.Colors.BLUE_400,
                            weight=ft.FontWeight.W_500,
                        ),
                    ],
                    spacing=4,
                    tight=True,
                ),
                padding=ft.padding.symmetric(horizontal=4, vertical=2),
                on_click=lambda _: self._open_web_page(),
                ink=True,
                border_radius=4,
            )
            controls.append(web_link)
        
        # 信息区域：标题 + 基础模型 chip + 网页链接
        return ft.Column(
            controls=controls,
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
    
    def _open_web_page(self):
        """在浏览器中打开模型网页。"""
        if self.model_meta.web_page_url and self.page:
            self.page.launch_url(self.model_meta.web_page_url)
    
    def _on_right_click(self, e: ft.TapEvent):
        """右键菜单处理。
        
        :param e: 手势事件对象
        """
        if not self.on_delete_callback:
            return
        
        # 创建删除确认对话框
        self._open_delete_confirm_dialog(e)
    
    def _open_delete_confirm_dialog(self, e: ft.TapEvent):
        """打开删除确认对话框"""
        if not e.page:
            return
        
        # 创建删除确认对话框
        dialog = DeleteModelConfirmDialog(
            model_meta=self.model_meta,
            on_confirm=lambda: self.on_delete_callback(self.model_meta) if self.on_delete_callback else None,
        )
        
        e.page.open(dialog)


# ============================================================================
# Dialog 类定义
# ============================================================================

class DeleteModelConfirmDialog(ft.AlertDialog):
    """删除模型确认对话框"""
    
    def __init__(self, model_meta: 'ModelMeta', on_confirm: callable):
        """
        初始化删除模型确认对话框
        
        Args:
            model_meta: 要删除的模型元数据
            on_confirm: 确认回调函数，无参数
        """
        self.model_meta = model_meta
        self.on_confirm = on_confirm
        
        super().__init__(
            modal=True,
            title=ft.Text("确认删除", color=ft.Colors.RED_700),
            content=ft.Column([
                ft.Icon(ft.Icons.WARNING_AMBER_ROUNDED, size=48, color=ft.Colors.ORANGE_700),
                ft.Text("即将删除以下模型元数据：", size=16, weight=ft.FontWeight.BOLD),
                ft.Divider(),
                ft.Text(f"名称：{model_meta.name}", size=14),
                ft.Text(f"版本：{model_meta.version_name}", size=14),
                ft.Text(f"类型：{model_meta.type}", size=14),
                ft.Text(f"基础模型：{model_meta.base_model}", size=14),
                ft.Divider(),
                ft.Text("⚠️ 此操作将删除：", size=14, color=ft.Colors.RED_700, weight=ft.FontWeight.BOLD),
                ft.Text("• metadata.json 文件", size=12),
                ft.Text(f"• {len(model_meta.examples)} 张示例图片", size=12),
                ft.Text("• 整个元数据目录", size=12),
                ft.Divider(),
                ft.Text("⚠️ 此操作不可恢复！", size=14, color=ft.Colors.RED_700, weight=ft.FontWeight.BOLD),
            ], tight=True, spacing=8, width=400, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            actions=[
                ft.TextButton("取消", on_click=self._on_cancel),
                ft.ElevatedButton(
                    "确认删除",
                    bgcolor=ft.Colors.RED_700,
                    color=ft.Colors.WHITE,
                    on_click=self._on_confirm
                ),
            ],
        )
    
    def _on_confirm(self, e):
        """确认删除"""
        # 关闭对话框
        self.open = False
        self.update()
        
        # 调用确认回调
        if self.on_confirm:
            self.on_confirm()
    
    def _on_cancel(self, e):
        """取消删除"""
        self.open = False
        self.update()
