"""
模型卡片 UI 组件。

为给定模型提供预览图与基础信息徽章的卡片展示；
支持打开“示例图片”与“模型详情”对话框。
"""
import base64
import io

import flet as ft

from schemas.model import ModelMeta
from services.model_meta import model_meta_service
from .example_image_dialog import build_example_image_dialog
from .model_detail_dialog import build_model_detail_dialog


class ModelCard(ft.Column):
    """模型的可视化卡片，展示关键信息。"""
    def __init__(self, model_meta: ModelMeta):
        """初始化模型卡片。
        
        :param model_meta: 模型元数据对象
        """
        super().__init__()
        self.model_meta = model_meta
        self.preview_image = model_meta_service.load_example_image(self.model_meta)
        img_control = self._build_image()
        info_control = self._build_info()
        self.controls = [
            ft.Card(
                content=ft.Container(
                    content=ft.Column(
                        controls=[
                            img_control,
                            ft.Container(
                                content=info_control,
                                on_click=self._open_detail_dialog
                            ),
                        ],
                        spacing=8,
                    ),
                    padding=10,
                )
            )
        ]

    @staticmethod
    def _pil_to_base64(img):
        """将 PIL Image 编码为 base64 PNG 字符串。"""
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return base64.b64encode(buf.getvalue()).decode("utf-8")

    def _build_image(self):
        """构建预览图控件；可点击打开示例图片对话框。"""
        if self.preview_image is None:
            return ft.Container(
                width=260,
                height=180,
                bgcolor=ft.Colors.GREY_800,
                border_radius=8,
                alignment=ft.alignment.center,
                content=ft.Text("无图片", color=ft.Colors.WHITE70),
                on_click=self._open_examples_dialog,
            )
        b64 = self._pil_to_base64(self.preview_image)
        return ft.Container(
            content=ft.Image(src_base64=b64, fit=ft.ImageFit.COVER),
            width=260,
            height=180,
            border_radius=8,
            clip_behavior=ft.ClipBehavior.HARD_EDGE,
            on_click=self._open_examples_dialog,
        )

    def _build_info(self):
        """构建标题与徽章，展示模型版本与基础类型。"""
        title = ft.Text(self.model_meta.version_name, size=16, weight=ft.FontWeight.BOLD)
        badges = ft.Row(
            controls=[
                ft.Chip(label=ft.Text(str(self.model_meta.type))),
                ft.Chip(label=ft.Text(str(self.model_meta.base_model))),
            ],
            spacing=10,
        )
        return ft.Column(controls=[title, badges], spacing=4)

    def _open_detail_dialog(self, e: ft.ControlEvent | None = None):
        """打开展示模型详细元数据的对话框。
        
        :param e: 控件事件对象
        """
        dlg = build_model_detail_dialog(self.model_meta)
        page = e.page if e and e.page else self.page
        if page:
            page.dialog = dlg
            page.dialog.open = True
            page.update()

    def _open_examples_dialog(self, e: ft.ControlEvent | None = None):
        """打开列出模型示例图片的对话框。
        
        :param e: 控件事件对象
        """
        dlg = build_example_image_dialog(self.model_meta)
        page = e.page if e and e.page else self.page
        if page:
            page.dialog = dlg
            page.dialog.open = True
            page.update()
