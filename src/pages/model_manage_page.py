"""
模型管理页面。

分区展示 Checkpoint 和 LoRA 模型卡片；
数据来源于 ModelMetaService。
"""
import flet as ft

from components.model_card import ModelCard
from services.model_meta import model_meta_service
from constants.ui_size import SPACING_SMALL, SPACING_MEDIUM
from settings.app_setting import app_settings


class ModelManagePage(ft.Column):
    """包含 Checkpoint 和 LoRA 两个分区的模型管理页面。"""
    def __init__(self):
        """初始化模型管理页面。
        
        分别加载 Checkpoint 和 LoRA 模型，以两个独立的 flow layout 展示。
        """
        super().__init__()
        
        # 基础模型筛选下拉菜单
        self.filter_dropdown = ft.Dropdown(
            label="基础模型筛选",
            options=[
                ft.dropdown.Option("所有", "所有"),
                ft.dropdown.Option("SD 1.5", "SD 1.5"),
                ft.dropdown.Option("SDXL 1.0", "SDXL 1.0"),
                ft.dropdown.Option("Pony", "Pony"),
                ft.dropdown.Option("Illustrious", "Illustrious"),
            ],
            value=app_settings.model_meta.base_model_filter or "所有",
            on_change=self._on_filter_change,
            expand=True,
        )
        
        # Checkpoint 区域（占位，后面会动态填充）
        self.checkpoint_section = ft.Column(spacing=SPACING_MEDIUM)
        
        # LoRA 区域（占位，后面会动态填充）
        self.lora_section = ft.Column(spacing=SPACING_MEDIUM)
        
        # 组合布局：筛选菜单 + Checkpoint + 分隔线 + LoRA
        self.controls = [
            ft.Container(
                content=ft.Row(
                    controls=[
                        ft.Container(expand=1),  # 左侧弹性空间
                        ft.Container(
                            content=self.filter_dropdown,
                            expand=2,  # 占据至少 2/4 = 1/2 的宽度
                        ),
                        ft.Container(expand=1),  # 右侧弹性空间
                    ],
                    spacing=0,
                ),
                padding=ft.padding.only(bottom=SPACING_MEDIUM),
            ),
            self.checkpoint_section,
            ft.Divider(height=1, thickness=2),
            self.lora_section,
        ]
        self.expand = True
        self.scroll = ft.ScrollMode.AUTO
        self.alignment = ft.MainAxisAlignment.START
        self.spacing = SPACING_MEDIUM
    
    def did_mount(self):
        """组件挂载后，渲染模型卡。"""
        self._render_models()
    
    def _on_filter_change(self, e):
        """筛选条件改变时的回调。"""
        selected_value = e.control.value
        
        # 更新设置
        if selected_value == "所有":
            app_settings.model_meta.base_model_filter = None
        else:
            app_settings.model_meta.base_model_filter = selected_value
        
        # 保存配置
        app_settings.save()
        
        # 重新渲染
        self._render_models()
    
    def _filter_models(self, models):
        """根据当前筛选条件过滤模型列表。
        
        :param models: 原始模型列表
        :return: 过滤后的模型列表
        """
        filter_value = app_settings.model_meta.base_model_filter
        if filter_value is None:
            return models
        
        return [m for m in models if m.base_model == filter_value]
    
    def _render_models(self):
        """根据当前筛选条件渲染模型卡。"""
        # 获取并筛选 Checkpoint 列表
        all_checkpoint_models = model_meta_service.sd_list
        filtered_checkpoint_models = self._filter_models(all_checkpoint_models)
        
        checkpoint_cards = [
            ModelCard(meta, all_models=all_checkpoint_models, index=all_checkpoint_models.index(meta))
            for meta in filtered_checkpoint_models
        ]
        
        checkpoint_flow = ft.Row(
            controls=checkpoint_cards,
            wrap=True,
            run_spacing=SPACING_SMALL,
            spacing=SPACING_SMALL,
            alignment=ft.MainAxisAlignment.START,
            vertical_alignment=ft.CrossAxisAlignment.START,
        )
        
        # 更新 Checkpoint 区域
        self.checkpoint_section.controls = [
            ft.Text("Checkpoint", size=20, weight=ft.FontWeight.BOLD),
            checkpoint_flow,
        ]
        
        # 获取并筛选 LoRA 列表
        all_lora_models = model_meta_service.lora_list
        filtered_lora_models = self._filter_models(all_lora_models)
        
        lora_cards = [
            ModelCard(meta, all_models=all_lora_models, index=all_lora_models.index(meta))
            for meta in filtered_lora_models
        ]
        
        lora_flow = ft.Row(
            controls=lora_cards,
            wrap=True,
            run_spacing=SPACING_SMALL,
            spacing=SPACING_SMALL,
            alignment=ft.MainAxisAlignment.START,
            vertical_alignment=ft.CrossAxisAlignment.START,
        )
        
        # 更新 LoRA 区域
        self.lora_section.controls = [
            ft.Text("LoRA", size=20, weight=ft.FontWeight.BOLD),
            lora_flow,
        ]
        
        # 刷新界面
        self.update()
