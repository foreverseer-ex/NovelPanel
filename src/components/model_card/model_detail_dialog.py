
"""
模型详情对话框。
"""
import flet as ft

from schemas.model import ModelMeta

def build_model_detail_dialog(meta: ModelMeta) -> ft.AlertDialog:
    """构建一个弹窗，列出模型的关键元数据字段。

    :param meta: 已整合好的模型元数据
    :return: 配置完成的 Flet AlertDialog
    """
    fields = [
        ("filename", meta.filename),
        ("name", meta.name),
        ("version", meta.version),
        ("desc", meta.desc or ""),
        ("model_id", meta.model_id),
        ("type", meta.type),
        ("base_model", meta.base_model),
        ("sha256", meta.sha256),
        ("trained_words", ", ".join(meta.trained_words or [])),
        ("download_url", meta.download_url),
    ]
    rows = [ft.Text(f"{k}: {v}") for k, v in fields]

    def _close(e: ft.ControlEvent):
        """关闭对话框的回调函数。
        
        :param e: 控件事件对象
        """
        if e.page and e.page.dialog:
            e.page.dialog.open = False
            e.page.update()

    return ft.AlertDialog(
        modal=True,
        title=ft.Text("模型详情"),
        content=ft.Column(controls=rows, tight=True, spacing=6, scroll=ft.ScrollMode.AUTO),
        actions=[ft.TextButton("关闭", on_click=_close)],
    )
