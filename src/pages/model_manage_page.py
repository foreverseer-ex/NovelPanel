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
            value=app_settings.ui.base_model_filter or "所有",
            on_change=self._on_filter_change,
            expand=True,
        )
        
        # Checkpoint 区域（占位，后面会动态填充）
        self.checkpoint_section = ft.Column(spacing=SPACING_MEDIUM)
        
        # LoRA 区域（占位，后面会动态填充）
        self.lora_section = ft.Column(spacing=SPACING_MEDIUM)
        
        # 右上角：通过模型ID同步 按钮
        self.sync_dialog_model_id = ft.TextField(label="Civitai 模型ID", keyboard_type=ft.KeyboardType.NUMBER)
        self.sync_dialog_model_type = ft.Dropdown(
            label="模型类型",
            options=[ft.dropdown.Option("Checkpoint"), ft.dropdown.Option("LORA")],
            value="Checkpoint",
        )
        self.sync_dialog_filename = ft.TextField(label="本地文件名（含后缀 .safetensors）")

        def do_sync_by_id(_: ft.ControlEvent):
            try:
                mid = int(self.sync_dialog_model_id.value)
            except Exception:
                self.page.snack_bar = ft.SnackBar(content=ft.Text("模型ID格式错误"), bgcolor=ft.Colors.RED_700)
                self.page.snack_bar.open = True
                self.page.update()
                return
            mtype = self.sync_dialog_model_type.value
            fname = self.sync_dialog_filename.value.strip()
            if not fname:
                self.page.snack_bar = ft.SnackBar(content=ft.Text("文件名不能为空"), bgcolor=ft.Colors.RED_700)
                self.page.snack_bar.open = True
                self.page.update()
                return
            # 同步并刷新
            from services.model_meta import model_meta_service
            model_meta_service.sync_by_model_id(mid, mtype, fname)
            # 刷新本页模型视图
            self.checkpoint_section.controls = []
            self.lora_section.controls = []
            self._render_models()
            self.page.snack_bar = ft.SnackBar(content=ft.Text("同步完成"), bgcolor=ft.Colors.GREEN_700)
            self.page.snack_bar.open = True
            self.page.update()

        self.sync_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("通过 Civitai 模型ID 同步"),
            content=ft.Column([
                self.sync_dialog_model_id,
                self.sync_dialog_model_type,
                self.sync_dialog_filename,
            ], tight=True, spacing=10),
            actions=[
                ft.TextButton("取消", on_click=lambda e: setattr(self.sync_dialog, 'open', False)),
                ft.ElevatedButton("开始同步", on_click=do_sync_by_id),
            ],
        )

        def open_sync_dialog(_: ft.ControlEvent):
            if self.page:
                self.page.dialog = self.sync_dialog
                self.sync_dialog.open = True
                self.page.update()

        self.sync_by_id_button = ft.IconButton(icon=ft.Icons.CLOUD_DOWNLOAD, tooltip="通过模型ID同步", on_click=open_sync_dialog)

        # 组合布局：筛选菜单 + 顶部按钮 + Checkpoint + 分隔线 + LoRA
        self.controls = [
            ft.Container(
                content=ft.Row(
                    controls=[
                        ft.Container(expand=1),
                        ft.Container(
                            content=self.filter_dropdown,
                            expand=2,
                        ),
                        ft.Container(content=self.sync_by_id_button, expand=1, alignment=ft.alignment.center_right),
                    ],
                    spacing=0,
                ),
                padding=ft.padding.only(top=SPACING_SMALL, bottom=SPACING_MEDIUM),
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
            app_settings.ui.base_model_filter = None
        else:
            app_settings.ui.base_model_filter = selected_value
        
        # 保存配置
        app_settings.save()
        
        # 重新渲染
        self._render_models()
    
    def _filter_models(self, models):
        """根据当前筛选条件过滤模型列表。
        
        :param models: 原始模型列表
        :return: 过滤后的模型列表
        """
        filter_value = app_settings.ui.base_model_filter
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
