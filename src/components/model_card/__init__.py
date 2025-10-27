"""
模型卡片 UI 组件。

为给定模型提供预览图与基础信息徽章的卡片展示；
支持打开"示例图片"与"模型详情"对话框。
"""
import base64
import io
import asyncio

import flet as ft

from schemas.model_meta import ModelMeta
from services.model_meta import model_meta_service
from constants.color import ModelTypeChipColor, BaseModelColor
from .example_image_dialog import ExampleImageDialog
from .model_detail_dialog import ModelDetailDialog


class ModelCard(ft.Column):
    """模型的可视化卡片，展示关键信息。"""
    def __init__(self, model_meta: ModelMeta):
        """初始化模型卡片。
        
        :param model_meta: 模型元数据对象
        """
        super().__init__()
        self.model_meta = model_meta
        # 不再在初始化时加载图片，而是异步加载
        self.preview_image = None
        self.image_container = self._build_image()
        info_control = self._build_info()
        self.controls = [
            ft.Card(
                content=ft.Container(
                    content=ft.Column(
                        controls=[
                            self.image_container,
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
        """构建预览图控件；初始显示loading，然后异步加载。"""
        # 初始显示loading状态
        return ft.Container(
            width=260,
            height=180,
            bgcolor=ft.Colors.GREY_100,
            border_radius=8,
            alignment=ft.alignment.center,
            content=ft.Column(
                controls=[
                    ft.ProgressRing(width=30, height=30),
                    ft.Text("加载中...", size=12, color=ft.Colors.GREY_600),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=8,
            ),
            on_click=self._open_examples_dialog,
        )

    async def _load_preview_image(self):
        """异步加载预览图。"""
        try:
            # 在后台线程加载图片
            self.preview_image = await asyncio.to_thread(
                model_meta_service.load_example_image, self.model_meta
            )
            
            if self.preview_image is None:
                # 没有图片
                self.image_container.content = ft.Text("无图片", color=ft.Colors.WHITE70)
                self.image_container.bgcolor = ft.Colors.GREY_800
            else:
                # 转换为base64并更新
                b64 = await asyncio.to_thread(self._pil_to_base64, self.preview_image)
                self.image_container.content = ft.Image(src_base64=b64, fit=ft.ImageFit.COVER)
                self.image_container.bgcolor = None
                self.image_container.clip_behavior = ft.ClipBehavior.HARD_EDGE
        except (FileNotFoundError, IOError, Exception):
            # 加载失败
            self.image_container.content = ft.Text("加载失败", color=ft.Colors.RED_400)
            self.image_container.bgcolor = ft.Colors.GREY_200
        
        # 刷新显示
        if self.page:
            self.page.update()

    def did_mount(self):
        """卡片挂载后，触发异步加载图片。"""
        super().did_mount()
        if self.page:
            self.page.run_task(self._load_preview_image)

    def _build_info(self):
        """构建标题与徽章，展示模型版本与基础类型。"""
        title = ft.Text(self.model_meta.version_name, size=16, weight=ft.FontWeight.BOLD)
        
        # 获取模型类型和基础模型的颜色
        type_color = ModelTypeChipColor.get(self.model_meta.type)
        base_model_color = BaseModelColor.get(self.model_meta.base_model)
        
        badges = ft.Row(
            controls=[
                ft.Chip(
                    label=ft.Text(str(self.model_meta.type)),
                    bgcolor=type_color,
                ),
                ft.Chip(
                    label=ft.Text(str(self.model_meta.base_model)),
                    bgcolor=base_model_color,
                ),
            ],
            spacing=10,
        )
        return ft.Column(controls=[title, badges], spacing=4)

    def _open_detail_dialog(self, e: ft.ControlEvent | None = None):
        """打开展示模型详细元数据的对话框。
        
        :param e: 控件事件对象
        """
        dlg = ModelDetailDialog(self.model_meta)
        page = e.page if e and e.page else self.page
        if page:
            # 先打开对话框（立即显示）
            page.open(dlg)
            # 然后异步加载图片
            page.run_task(dlg.load_preview_image)

    def _open_examples_dialog(self, e: ft.ControlEvent | None = None):
        """打开列出模型示例图片的对话框。
        
        :param e: 控件事件对象
        """
        dlg = ExampleImageDialog(self.model_meta)
        page = e.page if e and e.page else self.page
        if page:
            # 先打开对话框（立即显示）
            page.open(dlg)
            # 然后异步加载图片
            page.run_task(dlg.load_images)
