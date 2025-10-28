"""
模型管理页面。

以响应式网格展示所有已发现的模型（Checkpoint、LoRA、VAE）的卡片；
数据来源于 ModelMetaService。
"""
import flet as ft

from components.model_card import ModelCard
from services.model_meta import model_meta_service
from constants.ui_size import GRID_COL_4, SPACING_SMALL


class ModelManagePage(ft.Column):
    """包含标题与响应式模型卡片网格的页面。"""
    def __init__(self):
        """初始化模型管理页面。
        
        加载所有模型（Checkpoint、LoRA、VAE）并以响应式网格展示。
        """
        super().__init__()
        # 准备合并列表；后续可添加过滤功能
        models = (
            model_meta_service.sd_list
            + model_meta_service.lora_list
            + model_meta_service.vae_list
        )
        cards = [
            ft.Container(content=ModelCard(meta), padding=6)
            for meta in models
        ]
        grid = ft.ResponsiveRow(
            controls=[
                ft.Container(content=c, col=GRID_COL_4)
                for c in cards
            ],
            run_spacing=SPACING_SMALL,
            spacing=SPACING_SMALL,
        )
        self.controls = [
            ft.Text("模型管理", size=20, weight=ft.FontWeight.BOLD),
            grid,
        ]
        self.expand = True
