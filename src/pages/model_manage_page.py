"""
模型管理页面。

分区展示 Checkpoint 和 LoRA 模型卡片；
数据来源于 ModelMetaService。
"""
import flet as ft
from loguru import logger
from flet_toast import flet_toast
from flet_toast.Types import Position

from components.model_card import ModelCard
from constants.model_meta import Ecosystem, BaseModel
from constants.ui_size import SPACING_SMALL, SPACING_MEDIUM
from services.model_meta import local_model_meta_service, civitai_model_meta_service
from settings import app_settings
from utils.civitai import parse_air


class ModelManagePage(ft.Column):
    """包含 Checkpoint 和 LoRA 两个分区的模型管理页面。"""
    def __init__(self):
        """初始化模型管理页面。
        
        分别加载 Checkpoint 和 LoRA 模型，以两个独立的 flow layout 展示。
        """
        super().__init__()
        
        # 清理可能存在的空字符串配置（历史遗留问题）
        if app_settings.ui.ecosystem_filter == "":
            app_settings.ui.ecosystem_filter = None
        if app_settings.ui.base_model_filter == "":
            app_settings.ui.base_model_filter = None
        
        # 生态系统筛选下拉菜单 - 动态生成选项
        ecosystem_options = [ft.dropdown.Option("", "所有")]  # 使用空字符串代替None
        # 从 Ecosystem 常量类中获取所有生态系统
        ecosystem_display_names = {
            "sd1": "SD 1.5",
            "sd2": "SD 2.0",
            "sdxl": "SDXL",
        }
        for attr_name in dir(Ecosystem):
            if not attr_name.startswith('_'):  # 跳过私有属性
                attr_value = getattr(Ecosystem, attr_name)
                if isinstance(attr_value, str):  # 只获取字符串常量
                    # 使用自定义显示名称或大写格式
                    display_name = ecosystem_display_names.get(attr_value, attr_value.upper())
                    ecosystem_options.append(ft.dropdown.Option(attr_value, display_name))
        
        self.ecosystem_filter_dropdown = ft.Dropdown(
            label="生态系统",
            options=ecosystem_options,
            value=app_settings.ui.ecosystem_filter or "",  # 使用空字符串代替None
            on_change=self._on_ecosystem_filter_change,
            expand=True,
        )
        
        # 基础模型筛选下拉菜单 - 动态生成选项
        base_model_options = [ft.dropdown.Option("", "所有")]  # 使用空字符串代替None
        # 从 BaseModel 常量类中获取所有基础模型
        for attr_name in dir(BaseModel):
            if not attr_name.startswith('_'):  # 跳过私有属性
                attr_value = getattr(BaseModel, attr_name)
                if isinstance(attr_value, str):  # 只获取字符串常量
                    # 直接使用原始值作为显示名称
                    base_model_options.append(ft.dropdown.Option(attr_value, attr_value))
        
        self.base_model_filter_dropdown = ft.Dropdown(
            label="基础模型",
            options=base_model_options,
            value=app_settings.ui.base_model_filter or "",  # 使用空字符串代替None
            on_change=self._on_base_model_filter_change,
            expand=True,
        )
        
        # Checkpoint 区域（占位，后面会动态填充）
        self.checkpoint_section = ft.Column(spacing=SPACING_MEDIUM)
        
        # LoRA 区域（占位，后面会动态填充）
        self.lora_section = ft.Column(spacing=SPACING_MEDIUM)
        
        # 右上角：从 Civitai 导入按钮
        self.import_dialog_air = ft.TextField(
            label="模型 AIR",
            hint_text="例如：urn:air:sd1:checkpoint:civitai:348620@390021",
            autofocus=True,
            multiline=False,
        )
        self.import_dialog_status = ft.Text("", size=12, color=ft.Colors.GREY_600)

        async def do_import_from_civitai(air_str: str):
            """从 Civitai 导入模型元数据（后台运行）"""
            from utils.civitai import parse_air

            logger.info(f"后台任务开始从 Civitai 导入: {air_str}")
            
            try:
                # 解析 AIR 标识符
                air = parse_air(air_str)
                model_id = air.model_id
                version_id = air.version_id
                logger.info(f"解析 AIR: model_id={model_id}, version_id={version_id}")
                
                # 通过 version_id 获取模型元数据
                logger.info(f"调用 get_by_id({version_id})")
                model_meta = civitai_model_meta_service.get_by_id(version_id)
                logger.info(f"get_by_id 返回: {model_meta}")
                
                if not model_meta:
                    self._show_toast(f"❌ 未找到版本 ID: {version_id}", ft.Colors.RED_700)
                    return
                
                # 保存到本地
                logger.info(f"调用 save({model_meta.name})")
                await civitai_model_meta_service.save(model_meta)
                logger.info("save 完成")
                
                # 刷新本地缓存
                logger.info("调用 flush()")
                local_model_meta_service.flush()
                logger.info("flush 完成")
                
                # 重新渲染视图
                self.checkpoint_section.controls = []
                self.lora_section.controls = []
                self._render_models()
                logger.info("重新渲染完成")
                
                # 显示成功消息
                self._show_toast(f"✅ 导入成功: {model_meta.name}", ft.Colors.GREEN_700)
                
            except Exception as e:
                logger.exception(f"导入失败: {e}")
                self._show_toast(f"❌ 导入失败: {str(e)}", ft.Colors.RED_700)

        # 保存 do_import_from_civitai 为实例方法
        self._do_import_from_civitai = do_import_from_civitai
        
        self.import_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("从 Civitai 导入模型"),
            content=ft.Column([
                ft.Text("输入 Civitai 模型 AIR 标识符，自动获取并保存模型元数据", size=12),
                ft.Text("格式：urn:air:{ecosystem}:{type}:civitai:{model_id}@{version_id}", size=11, color=ft.Colors.GREY_500),
                ft.Text("示例：urn:air:sd1:checkpoint:civitai:348620@390021", size=11, color=ft.Colors.GREY_500),
                self.import_dialog_air,
                self.import_dialog_status,
            ], tight=True, spacing=10, width=550),
            actions=[
                ft.TextButton("取消", on_click=lambda e: self._close_import_dialog()),
                ft.ElevatedButton("导入", on_click=self._on_import_click),
            ],
        )

        self.import_button = ft.IconButton(
            icon=ft.Icons.CLOUD_DOWNLOAD,
            tooltip="从 Civitai 导入模型",
            on_click=self._open_import_dialog
        )
        
        self.clear_button = ft.IconButton(
            icon=ft.Icons.DELETE_SWEEP,
            tooltip="清空所有模型元数据",
            icon_color=ft.Colors.RED_400,
            on_click=self._open_clear_confirm_dialog
        )
        
        # 确认清空对话框
        self.clear_confirm_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("确认清空", color=ft.Colors.RED_700),
            content=ft.Column([
                ft.Icon(ft.Icons.WARNING_AMBER_ROUNDED, size=48, color=ft.Colors.ORANGE_700),
                ft.Text("即将删除所有模型元数据！", size=16, weight=ft.FontWeight.BOLD),
                ft.Text("此操作将删除：", size=12),
                ft.Text("• 所有 Checkpoint 元数据", size=12),
                ft.Text("• 所有 LoRA 元数据", size=12),
                ft.Text("• 包括下载的示例图片", size=12, color=ft.Colors.GREY_600),
                ft.Divider(),
                ft.Text("⚠️ 此操作不可恢复！", size=14, color=ft.Colors.RED_700, weight=ft.FontWeight.BOLD),
            ], tight=True, spacing=10, width=400, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            actions=[
                ft.TextButton("取消", on_click=lambda e: self._close_clear_confirm_dialog()),
                ft.ElevatedButton(
                    "确认清空", 
                    bgcolor=ft.Colors.RED_700,
                    color=ft.Colors.WHITE,
                    on_click=self._on_clear_confirm_click
                ),
            ],
        )

        # 组合布局：两个筛选菜单 + 顶部按钮 + Checkpoint + 分隔线 + LoRA
        self.controls = [
            ft.Container(
                content=ft.Row(
                    controls=[
                        # 生态系统筛选（占一半）
                        ft.Container(
                            content=self.ecosystem_filter_dropdown,
                            expand=1,
                        ),
                        # 基础模型筛选（占一半）
                        ft.Container(
                            content=self.base_model_filter_dropdown,
                            expand=1,
                        ),
                        # 右侧按钮组
                        ft.Container(
                            content=ft.Row([
                                self.import_button,
                                self.clear_button,
                            ], spacing=5),
                            alignment=ft.alignment.center_right
                        ),
                    ],
                    spacing=10,
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
    
    def _open_import_dialog(self, _: ft.ControlEvent):
        """打开导入对话框，自动读取剪贴板并尝试解析 AIR"""

        logger.info("点击了从 Civitai 导入按钮")
        
        if not self.page:
            logger.error("self.page 为 None，无法打开对话框")
            return
        
        try:
            # 重置状态
            self.import_dialog_status.value = ""
            
            # 读取剪贴板并尝试解析 AIR
            try:
                clipboard_text = self.page.get_clipboard()
                if clipboard_text:
                    clipboard_text = clipboard_text.strip()
                    logger.debug(f"剪贴板内容: {clipboard_text}")
                    
                    # 尝试解析 AIR
                    air = parse_air(clipboard_text)
                    if air and air.version_id:
                        # 解析成功，自动填充
                        self.import_dialog_air.value = clipboard_text
                        logger.info(f"自动填充 AIR: {clipboard_text}")
                    else:
                        # 解析失败，清空输入框
                        self.import_dialog_air.value = ""
                else:
                    self.import_dialog_air.value = ""
            except Exception as e:
                logger.warning(f"读取或解析剪贴板失败: {e}")
                self.import_dialog_air.value = ""
            
            # 使用 Flet 推荐的方式打开对话框
            self.page.open(self.import_dialog)
            
            logger.info("导入对话框已打开")
            logger.debug(f"import_dialog.open: {self.import_dialog.open}")
        except Exception as e:
            logger.exception(f"打开导入对话框失败: {e}")
    
    def _on_import_click(self, e: ft.ControlEvent):
        """处理导入按钮点击，立即关闭对话框并在后台执行导入"""
        from utils.civitai import parse_air
        from loguru import logger
        
        # 验证输入
        air_str = self.import_dialog_air.value.strip()
        logger.debug(f"输入 AIR: {air_str}")
        
        if not air_str:
            self._show_toast("❌ 请输入模型 AIR 标识符", ft.Colors.RED_700)
            return
        
        # 解析 AIR 标识符
        air = parse_air(air_str)
        
        if not air:
            self._show_toast("❌ AIR 格式错误", ft.Colors.RED_700)
            return
        
        # 验证必须有 version_id
        if not air.version_id:
            self._show_toast("❌ AIR 标识符必须包含版本 ID（@{version_id}）", ft.Colors.RED_700)
            logger.warning(f"AIR 缺少 version_id: {air_str}")
            return
        
        # ✅ 立即关闭对话框（同步操作）
        if self.page:
            self.page.close(self.import_dialog)
            self.import_dialog_air.value = ""
            self.import_dialog_status.value = ""
            self.page.update()
        
        # ✅ 立即显示正在导入的 Toast
        self._show_toast("⏳ 正在从 Civitai 导入模型...", ft.Colors.BLUE_700, duration=2000)
        
        # ✅ 后台执行导入任务
        if self.page:
            self.page.run_task(self._do_import_from_civitai, air_str)
    
    def _close_import_dialog(self):
        """关闭导入对话框"""
        if self.page:
            self.page.close(self.import_dialog)
            self.import_dialog_air.value = ""
            self.import_dialog_status.value = ""
    
    def _show_error(self, message: str):
        """显示错误消息（已废弃，使用 _show_toast 替代）"""
        self.import_dialog_status.value = f"❌ {message}"
        self.import_dialog_status.color = ft.Colors.RED_700
        if self.page:
            self.page.update()
    
    def _show_toast(self, message: str, bgcolor=ft.Colors.GREEN_700, duration: int = 3000):
        """显示 Toast 提示
        
        :param message: 提示消息
        :param bgcolor: 背景颜色（用于判断类型）
        :param duration: 显示时长（毫秒）
        """
        if self.page:
            # 转换毫秒为秒
            duration_sec = duration / 1000
            
            # 根据颜色判断类型
            if bgcolor == ft.Colors.GREEN_700:
                flet_toast.success(
                    page=self.page,
                    message=message,
                    position=Position.TOP_RIGHT,
                    duration=duration_sec
                )
            elif bgcolor == ft.Colors.RED_700:
                flet_toast.error(
                    page=self.page,
                    message=message,
                    position=Position.TOP_RIGHT,
                    duration=duration_sec
                )
            elif bgcolor == ft.Colors.BLUE_700:
                # 信息类型用 warning（蓝色的提示）
                flet_toast.warning(
                    page=self.page,
                    message=message,
                    position=Position.TOP_RIGHT,
                    duration=duration_sec
                )
            else:
                # 默认为 success
                flet_toast.success(
                    page=self.page,
                    message=message,
                    position=Position.TOP_RIGHT,
                    duration=duration_sec
                )
    
    def _open_clear_confirm_dialog(self, _: ft.ControlEvent):
        """打开清空确认对话框"""
        from loguru import logger
        logger.info("点击了清空按钮")
        
        if not self.page:
            logger.error("self.page 为 None，无法打开对话框")
            return
        
        try:
            # 使用 Flet 推荐的方式打开对话框
            self.page.open(self.clear_confirm_dialog)
            
            logger.info("清空确认对话框已打开")
            logger.debug(f"clear_confirm_dialog.open: {self.clear_confirm_dialog.open}")
        except Exception as e:
            logger.exception(f"打开清空确认对话框失败: {e}")
    
    def _close_clear_confirm_dialog(self):
        """关闭清空确认对话框"""
        if self.page:
            self.page.close(self.clear_confirm_dialog)
    
    def _on_clear_confirm_click(self, e: ft.ControlEvent):
        """处理确认清空按钮点击"""
        if self.page:
            self.page.run_task(self._do_clear_all, e)
    
    async def _do_clear_all(self, _: ft.ControlEvent):
        """执行清空所有模型元数据"""
        from loguru import logger
        logger.info("开始清空所有模型元数据")
        
        try:
            # 关闭确认对话框
            self._close_clear_confirm_dialog()
            
            # 执行清空
            deleted_count = local_model_meta_service.clear_all()
            
            # 重新渲染视图
            self.checkpoint_section.controls = []
            self.lora_section.controls = []
            self._render_models()
            
            # 显示成功消息
            self._show_toast(f"✅ 已清空所有模型元数据，共删除 {deleted_count} 个")
            
            logger.success(f"清空完成，共删除 {deleted_count} 个模型元数据")
            
        except Exception as e:
            logger.exception(f"清空失败: {e}")
            self._show_toast(f"❌ 清空失败: {str(e)}", ft.Colors.RED_700)
    
    def _on_ecosystem_filter_change(self, e):
        """生态系统筛选条件改变时的回调。"""
        selected_value = e.control.value
        
        # 将空字符串转换为 None（表示显示所有）
        # 使用 or None 确保空字符串也会被转换为 None
        app_settings.ui.ecosystem_filter = selected_value or None
        
        # 保存配置
        app_settings.save()
        
        # 重新渲染
        self._render_models()
    
    def _on_base_model_filter_change(self, e):
        """基础模型筛选条件改变时的回调。"""
        selected_value = e.control.value
        
        # 将空字符串转换为 None（表示显示所有）
        # 使用 or None 确保空字符串也会被转换为 None
        app_settings.ui.base_model_filter = selected_value or None
        
        # 保存配置
        app_settings.save()
        
        # 重新渲染
        self._render_models()
    
    def _filter_models(self, models):
        """根据当前筛选条件过滤模型列表。
        
        同时支持生态系统和基础模型两个维度的筛选。
        
        :param models: 原始模型列表
        :return: 过滤后的模型列表
        """
        filtered = models
        
        # 按生态系统筛选（空字符串和 None 都表示不筛选）
        ecosystem_filter = app_settings.ui.ecosystem_filter
        if ecosystem_filter and ecosystem_filter != "":
            filtered = [m for m in filtered if m.ecosystem == ecosystem_filter]
        
        # 按基础模型筛选（空字符串和 None 都表示不筛选）
        base_model_filter = app_settings.ui.base_model_filter
        if base_model_filter and base_model_filter != "":
            # 注意：base_model 可能为 None，需要处理
            filtered = [m for m in filtered if m.base_model == base_model_filter]
        
        return filtered
    
    def _render_models(self):
        """根据当前筛选条件渲染模型卡。"""
        # 获取并筛选 Checkpoint 列表
        all_checkpoint_models = local_model_meta_service.sd_list
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
        all_lora_models = local_model_meta_service.lora_list
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
