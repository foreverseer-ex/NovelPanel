"""
模型管理页面。

以响应式网格展示所有已发现的模型（Checkpoint、LoRA、VAE）的卡片；
数据来源于 ModelMetaService。
"""
import flet as ft

from components.model_card import ModelCard
from services.model_meta import model_meta_service


class ModelManagePage(ft.Column):
    """包含标题与响应式模型卡片网格的页面。"""
    def __init__(self):
        super().__init__()
        # prepare a combined list for now; can be filtered later
        models = (
            model_meta_service.sd_list
            + model_meta_service.lora_list
            + model_meta_service.vae_list
        )
        cards = [ft.Container(content=ModelCard(meta), padding=6) for meta in models]
        grid = ft.ResponsiveRow(
            controls=[ft.Container(content=c, col={"xs": 12, "sm": 6, "md": 4, "lg": 3}) for c in cards],
            run_spacing=8,
            spacing=8,
        )
        self.controls = [
            ft.Text("模型管理", size=20, weight=ft.FontWeight.BOLD),
            grid,
        ]
        self.expand = True
