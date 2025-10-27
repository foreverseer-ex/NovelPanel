import base64
import io

import flet as ft

from schemas.model import ModelMeta
from services.model_meta import model_meta_service
from .example_image_dialog import build_example_image_dialog
from .model_detail_dialog import build_model_detail_dialog


class ModelCard(ft.Column):
    def __init__(self, model_meta: ModelMeta):
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
                            ft.Container(content=info_control, on_click=lambda e: self._open_detail_dialog(e)),
                        ],
                        spacing=8,
                    ),
                    padding=10,
                )
            )
        ]

    @staticmethod
    def _pil_to_base64(img):
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return base64.b64encode(buf.getvalue()).decode("utf-8")

    def _build_image(self):
        if self.preview_image is None:
            return ft.Container(
                width=260,
                height=180,
                bgcolor=ft.Colors.GREY_800,
                border_radius=8,
                alignment=ft.alignment.center,
                content=ft.Text("No Image", color=ft.Colors.WHITE70),
                on_click=lambda e: self._open_examples_dialog(),
            )
        b64 = self._pil_to_base64(self.preview_image)
        return ft.Container(
            content=ft.Image(src_base64=b64, fit=ft.ImageFit.COVER),
            width=260,
            height=180,
            border_radius=8,
            clip_behavior=ft.ClipBehavior.HARD_EDGE,
            on_click=lambda e: self._open_examples_dialog(),
        )

    def _build_info(self):
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
        dlg = build_model_detail_dialog(self.model_meta)
        page = e.page if e else self.page
        page.dialog = dlg
        page.dialog.open = True
        page.update()

    def _open_examples_dialog(self):
        dlg = build_example_image_dialog(self.model_meta)
        self.page.dialog = dlg
        self.page.dialog.open = True
        self.page.update()
