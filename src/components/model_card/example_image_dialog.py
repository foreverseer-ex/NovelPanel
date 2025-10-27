"""
模型示例图片对话框。

以网格形式展示已缓存的示例图，点击单项可查看对应生成参数；
图片与参数均由 ModelMetaService 的本地缓存加载。
"""
import base64
import io

import flet as ft
from schemas.model import ModelMeta
from services.model_meta import model_meta_service

def build_example_image_dialog(meta: ModelMeta) -> ft.AlertDialog:
    """构建示例图片与生成参数的弹窗。

    :param meta: 含示例条目的模型元数据
    :return: 配置好的 Flet AlertDialog
    """
    title_text = ft.Text("Example Images")
    content_container = ft.Container(width=600)

    state = {"view": 0, "selected_index": -1}

    def pil_to_base64(img):
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return base64.b64encode(buf.getvalue()).decode("utf-8")

    def render_content():
        if state["view"] == 0:
            tiles = []
            try:
                images = model_meta_service.load_example_images(meta)
            except (FileNotFoundError, IOError):
                # 如果图片文件不存在或无法读取，使用空列表
                images = []
            for idx, img in enumerate(images):
                b64 = pil_to_base64(img)
                tiles.append(
                    ft.Container(
                        content=ft.Image(src_base64=b64, fit=ft.ImageFit.COVER),
                        width=120,
                        height=120,
                        border_radius=8,
                        on_click=lambda e, i=idx: enter_detail(e, i),
                    )
                )
            grid = ft.ResponsiveRow(
                controls=[
                    ft.Container(content=t, col={'xs': 6, 'sm': 3, 'md': 2, 'lg': 2})
                    for t in tiles
                ],
                run_spacing=10,
                spacing=10,
            )
            content_container.content = grid
        else:
            idx = state["selected_index"]
            if 0 <= idx < len(meta.examples):
                ex = meta.examples[idx]
                items = [
                    ft.Text(f"{k}: {v}")
                    for k, v in ex.args.model_dump().items()
                ]
                content_container.content = ft.Column(
                    controls=items, tight=True, spacing=6, width=600
                )
            else:
                content_container.content = ft.Text("No example selected")

    def render_actions():
        if state["view"] == 0:
            dlg.actions = [ft.TextButton("Close", on_click=close_dialog)]
        else:
            dlg.actions = [
                ft.TextButton("Back", on_click=back_to_list),
                ft.TextButton("Close", on_click=close_dialog),
            ]

    def enter_detail(e: ft.ControlEvent, index: int):
        state["selected_index"] = index
        state["view"] = 1
        title_text.value = "Example Detail"
        render_content()
        render_actions()
        e.page.update()

    def back_to_list(e: ft.ControlEvent):
        state["view"] = 0
        state["selected_index"] = -1
        title_text.value = "Example Images"
        render_content()
        render_actions()
        e.page.update()

    def close_dialog(e: ft.ControlEvent):
        state["view"] = 0
        state["selected_index"] = -1
        if e.page and e.page.dialog:
            e.page.dialog.open = False
            e.page.update()

    dlg = ft.AlertDialog(
        modal=True,
        title=title_text,
        content=content_container,
        actions=[],
    )
    render_content()
    render_actions()
    return dlg
