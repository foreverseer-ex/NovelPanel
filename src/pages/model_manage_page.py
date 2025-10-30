"""
模型管理页面。

分区展示 Checkpoint 和 LoRA 模型卡片；
数据来源于 ModelMetaService。
"""
import flet as ft
from loguru import logger
from flet_toast import flet_toast
from flet_toast.Types import Position
import httpx

from components.model_card import ModelCard
from constants.model_meta import Ecosystem, BaseModel
from constants.ui_size import SPACING_SMALL, SPACING_MEDIUM
from schemas.model_meta import ModelMeta
from services.model_meta import local_model_meta_service, civitai_model_meta_service
from settings import app_settings
from utils.civitai import AIR


class ModelManagePage(ft.Column):
    """包含 Checkpoint 和 LoRA 两个分区的模型管理页面。"""

    def __init__(self):
        """初始化模型管理页面。
        
        分别加载 Checkpoint 和 LoRA 模型，以两个独立的 flow layout 展示。
        """
        super().__init__()
        
        # 生态系统筛选下拉菜单 - 动态生成选项
        ecosystem_options = [ft.dropdown.Option(None, "所有")]  # 使用空字符串代替None
        # 从 Ecosystem 常量类中获取所有生态系统

        for attr_name in dir(Ecosystem):
            if not attr_name.startswith('_'):  # 跳过私有属性
                attr_value = getattr(Ecosystem, attr_name)
                if isinstance(attr_value, str):  # 只获取字符串常量
                    # 使用自定义显示名称或大写格式

                    ecosystem_options.append(ft.dropdown.Option(attr_value, attr_value))
        
        self.ecosystem_filter_dropdown = ft.Dropdown(
            label="生态系统",
            options=ecosystem_options,
            value=app_settings.ui.ecosystem_filter or None,  # 使用空字符串代替None
            on_change=self._on_ecosystem_filter_change,
            expand=True,
        )
        
        # 基础模型筛选下拉菜单 - 动态生成选项
        base_model_options = [ft.dropdown.Option(None, "所有")]  # 使用空字符串代替None
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
            value=app_settings.ui.base_model_filter or None,  # 使用空字符串代替None
            on_change=self._on_base_model_filter_change,
            expand=True,
        )
        
        # Checkpoint 区域（占位，后面会动态填充）
        self.checkpoint_section = ft.Column(spacing=SPACING_MEDIUM)
        
        # LoRA 区域（占位，后面会动态填充）
        self.lora_section = ft.Column(spacing=SPACING_MEDIUM)
        

        async def do_import_from_civitai(air_str: str):
            """从 Civitai 导入模型元数据（后台运行）"""
            logger.info(f"后台任务开始从 Civitai 导入: {air_str}")
            
            try:
                # 解析 AIR 标识符
                air = AIR.parse(air_str)
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
                
                # 重新渲染视图（_render_models 会自动重建整个列表，无需手动清空）
                self._render_models()
                logger.info("重新渲染完成")
                
                # 显示成功消息
                self._show_toast(f"✅ 导入成功: {model_meta.name}", ft.Colors.GREEN_700)
                
            except Exception as e:
                logger.exception(f"导入失败: {e}")
                if isinstance(e, httpx.ConnectTimeout):
                    self._show_toast("❌ 下载超时：请检查网络/代理，或在设置中提高 Civitai 超时", ft.Colors.RED_700)
                else:
                    self._show_toast(f"❌ 导入失败: {str(e)}", ft.Colors.RED_700)

        # 保存 do_import_from_civitai 为实例方法
        self._do_import_from_civitai = do_import_from_civitai
        
        # 隐私模式图标按钮
        self.privacy_mode_button = ft.IconButton(
            icon=ft.Icons.VISIBILITY_OFF if app_settings.ui.privacy_mode else ft.Icons.VISIBILITY,
            icon_color=ft.Colors.BLUE_400 if app_settings.ui.privacy_mode else ft.Colors.GREY_400,
            tooltip="隐私模式：已启用（点击关闭）" if app_settings.ui.privacy_mode else "隐私模式：已关闭（点击启用）",
            on_click=self._on_privacy_mode_toggle,
        )

        self.import_button = ft.IconButton(
            icon=ft.Icons.CLOUD_DOWNLOAD,
            tooltip="从 Civitai 导入模型",
            on_click=self._open_import_dialog
        )
        
        self.export_button = ft.IconButton(
            icon=ft.Icons.CONTENT_COPY,
            tooltip="导出所有 AIR 到剪贴板",
            on_click=self._on_export_all_air
        )
        
        self.refresh_button = ft.IconButton(
            icon=ft.Icons.REFRESH,
            tooltip="重新下载所有模型元数据",
            icon_color=ft.Colors.BLUE_400,
            on_click=self._on_refresh_all_metadata
        )
        
        self.clear_button = ft.IconButton(
            icon=ft.Icons.DELETE_SWEEP,
            tooltip="清空所有模型元数据",
            icon_color=ft.Colors.RED_400,
            on_click=self._open_clear_confirm_dialog
        )
        
        # 组合布局：两个筛选菜单 + 隐私模式按钮 + 其他按钮 + Checkpoint + 分隔线 + LoRA
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
                        # 右侧按钮组（隐私模式 + 其他功能按钮）
                        ft.Container(
                            content=ft.Row([
                                self.privacy_mode_button,
                                self.import_button,
                                self.export_button,
                                self.refresh_button,
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
        """打开导入对话框"""
        logger.info("点击了从 Civitai 导入按钮")
        
        if not self.page:
            logger.error("self.page 为 None，无法打开对话框")
            return
        
        try:
            # 创建导入对话框
            dialog = ImportModelDialog(
                page=self.page,
                on_import=self._on_batch_import,
            )
            
            # 加载剪贴板内容
            dialog.load_from_clipboard()
            
            # 打开对话框
            self.page.open(dialog)
            logger.info("导入对话框已打开")
            
        except Exception as e:
            logger.exception(f"打开导入对话框失败: {e}")
    
    def _on_batch_import(self, air_list: list[str]):
        """批量导入 AIR"""
        logger.info(f"开始批量导入 {len(air_list)} 个 AIR")
        self._show_toast(f"⏳ 开始导入 {len(air_list)} 个模型...", ft.Colors.BLUE_700)
        self.page.run_task(self._do_batch_import_from_civitai, air_list)
    
    async def _do_batch_import_from_civitai(self, air_list: list[str]):
        """批量从 Civitai 导入模型元数据（后台运行）"""
        logger.info(f"开始批量导入 {len(air_list)} 个模型")
        
        success_count = 0
        failed_count = 0
        total_count = len(air_list)
        
        for air_str in air_list:
            try:
                current = success_count + failed_count + 1  # 当前是第几个（从1开始）
                logger.info(f"[{current}/{total_count}] 导入: {air_str}")
        
        # 解析 AIR 标识符
                air = AIR.parse(air_str)
                model_id = air.model_id
                version_id = air.version_id
                
                # 通过 version_id 获取模型元数据
                model_meta = civitai_model_meta_service.get_by_id(version_id)
                
                if not model_meta:
                    logger.error(f"[{current}/{total_count}] 从 Civitai 获取模型元数据失败: {air_str}")
                    failed_count += 1
                    continue
                
                logger.info(f"[{current}/{total_count}] 成功获取模型元数据: {model_meta.name}")
                
                # 保存到本地（异步调用需要 await）
                saved_meta = await local_model_meta_service.save(model_meta)
                
                if not saved_meta:
                    logger.error(f"[{current}/{total_count}] 保存模型元数据失败: {model_meta.name}")
                    failed_count += 1
                    continue
                
                logger.info(f"[{current}/{total_count}] 成功保存模型元数据: {saved_meta.name}")
                success_count += 1
                
                # 显示进度提示
                current = success_count + failed_count
                self._show_toast(
                    f"⏳ {current}/{total_count} 已完成：{saved_meta.name}",
                    ft.Colors.BLUE_700,
                    duration=1500
                )
                
            except Exception as e:
                current = success_count + failed_count + 1
                logger.exception(f"[{current}/{total_count}] 导入失败: {air_str}, 错误: {e}")
                failed_count += 1
                
                # 显示失败提示
                current = success_count + failed_count
                if isinstance(e, httpx.ConnectTimeout):
                    self._show_toast(
                        f"❌ {current}/{total_count} 超时：请检查网络/代理，或提高超时",
                        ft.Colors.RED_700,
                        duration=2000
                    )
                else:
                    self._show_toast(
                        f"❌ {current}/{total_count} 失败：{air_str.split(':')[-1][:20]}...",
                        ft.Colors.RED_700,
                        duration=1500
                    )
                continue
        
        # 所有导入完成后刷新页面
        if self.page:
            # 确保在主线程更新UI（Flet 需要协程函数）
            async def _update_ui():
                self._render_models()
                # 显示结果
                if failed_count == 0:
                    self._show_toast(f"✅ 成功导入 {success_count} 个模型", ft.Colors.GREEN_700)
                elif success_count == 0:
                    self._show_toast(f"❌ 全部导入失败（{failed_count} 个）", ft.Colors.RED_700)
                else:
                    self._show_toast(f"⚠️ 成功 {success_count} 个，失败 {failed_count} 个", ft.Colors.ORANGE_700)
            
            # 在主线程执行UI更新
            self.page.run_task(_update_ui)
    
    def _on_export_all_air(self, _: ft.ControlEvent):
        """导出所有模型的 AIR 到剪贴板"""
        logger.info("点击了导出所有 AIR 按钮")
        
        try:
            # 获取所有模型（从服务的属性读取）
            all_checkpoint_models = local_model_meta_service.sd_list
            all_lora_models = local_model_meta_service.lora_list
            all_models = all_checkpoint_models + all_lora_models
            
            if not all_models:
                self._show_toast("❌ 没有可导出的模型", ft.Colors.RED_700)
                return
            
            # 收集所有 AIR
            air_list = [model.air for model in all_models]
            air_text = '\n'.join(air_list)
            
            # 复制到剪贴板
            if self.page:
                self.page.set_clipboard(air_text)
                self._show_toast(f"✅ 已复制 {len(air_list)} 个模型的 AIR 到剪贴板", ft.Colors.GREEN_700)
                logger.info(f"已导出 {len(air_list)} 个 AIR")
        
        except Exception as e:
            logger.exception(f"导出 AIR 失败: {e}")
            self._show_toast(f"❌ 导出失败: {str(e)}", ft.Colors.RED_700)
    
    def _on_refresh_all_metadata(self, _: ft.ControlEvent):
        """重新下载所有模型的元数据"""
        logger.info("点击了重新下载所有元数据按钮")
        
        try:
            # 获取所有模型的 AIR（从服务的属性读取）
            all_checkpoint_models = local_model_meta_service.sd_list
            all_lora_models = local_model_meta_service.lora_list
            all_models = all_checkpoint_models + all_lora_models
            
            if not all_models:
                self._show_toast("❌ 没有需要刷新的模型", ft.Colors.RED_700)
                return
            
            # 收集所有 AIR
            air_list = [model.air for model in all_models]
            
            # 创建并显示确认对话框
            def on_confirm():
                self._show_toast(f"⏳ 正在重新下载 {len(air_list)} 个模型的元数据...", ft.Colors.BLUE_700, duration=3000)
                # 后台执行刷新任务
                self.page.run_task(self._do_batch_import_from_civitai, air_list)
            
            dialog = RefreshMetadataConfirmDialog(
                air_count=len(air_list),
                on_confirm=on_confirm,
            )
            
            if self.page:
                self.page.open(dialog)
        
        except Exception as e:
            logger.exception(f"刷新元数据失败: {e}")
            self._show_toast(f"❌ 刷新失败: {str(e)}", ft.Colors.RED_700)
    
    def _on_privacy_mode_toggle(self, e: ft.ControlEvent):
        """处理隐私模式按钮点击（切换状态）"""
        # 切换隐私模式状态
        new_value = not app_settings.ui.privacy_mode
        logger.info(f"隐私模式切换: {new_value}")
        
        # 更新设置
        app_settings.ui.privacy_mode = new_value
        app_settings.save()
        
        # 更新按钮图标和提示
        if new_value:
            self.privacy_mode_button.icon = ft.Icons.VISIBILITY_OFF
            self.privacy_mode_button.icon_color = ft.Colors.BLUE_400
            self.privacy_mode_button.tooltip = "隐私模式：已启用（点击关闭）"
        else:
            self.privacy_mode_button.icon = ft.Icons.VISIBILITY
            self.privacy_mode_button.icon_color = ft.Colors.GREY_400
            self.privacy_mode_button.tooltip = "隐私模式：已关闭（点击启用）"
        
        self.privacy_mode_button.update()
        
        # 重新渲染模型卡（使图片根据隐私模式显示/隐藏）
        self._render_models()
    
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
                flet_toast.sucess(
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
                flet_toast.sucess(
                    page=self.page,
                    message=message,
                    position=Position.TOP_RIGHT,
                    duration=duration_sec
                )
    
    def _open_clear_confirm_dialog(self, _: ft.ControlEvent):
        """打开清空确认对话框"""
        logger.info("点击了清空按钮")
        
        if not self.page:
            logger.error("self.page 为 None，无法打开对话框")
            return
        
        try:
            # 创建清空确认对话框
            dialog = ClearMetadataConfirmDialog(
                on_confirm=lambda: self.page.run_task(self._do_clear_all),
            )
            
            # 打开对话框
            self.page.open(dialog)
            logger.info("清空确认对话框已打开")
            
        except Exception as e:
            logger.exception(f"打开清空确认对话框失败: {e}")
    
    async def _do_clear_all(self):
        """执行清空所有模型元数据"""
        logger.info("开始清空所有模型元数据")
        
        try:
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
    
    def _on_model_delete(self, model_meta: ModelMeta):
        """处理模型删除回调。
        
        :param model_meta: 要删除的模型元数据
        """
        from loguru import logger
        logger.info(f"开始删除模型: {model_meta.name}")
        
        try:
            # 调用服务删除模型
            success = local_model_meta_service.delete(model_meta)
            
            if success:
                # 重新渲染视图
                self._render_models()
                
                # 显示成功消息
                self._show_toast(f"✅ 已删除: {model_meta.name}", ft.Colors.GREEN_700)
                logger.success(f"删除成功: {model_meta.name}")
            else:
                self._show_toast(f"❌ 删除失败: {model_meta.name}", ft.Colors.RED_700)
                logger.error(f"删除失败: {model_meta.name}")
        
        except Exception as e:
            logger.exception(f"删除模型时出错: {e}")
            self._show_toast(f"❌ 删除出错: {str(e)}", ft.Colors.RED_700)

    def _on_ecosystem_filter_change(self, e:ft.ControlEvent):
        """生态系统筛选条件改变时的回调。"""
        selected_value = e.control.key
        
        # 将空字符串转换为 None（表示显示所有）
        # 使用 or None 确保空字符串也会被转换为 None
        app_settings.ui.ecosystem_filter = selected_value or None
        
        # 保存配置
        app_settings.save()
        
        # 重新渲染
        self._render_models()
    
    def _on_base_model_filter_change(self, e):
        """基础模型筛选条件改变时的回调。"""
        selected_value = e.control.key
        
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
        if ecosystem_filter is not None:
            filtered = [m for m in filtered if m.ecosystem == ecosystem_filter]
        
        # 按基础模型筛选（空字符串和 None 都表示不筛选）
        base_model_filter = app_settings.ui.base_model_filter
        if base_model_filter is not None:
            # 注意：base_model 可能为 None，需要处理
            filtered = [m for m in filtered if m.base_model == base_model_filter]
        
        return filtered
    
    def _render_models(self):
        """根据当前筛选条件渲染模型卡。"""
        # 获取并筛选 Checkpoint 列表
        all_checkpoint_models = local_model_meta_service.sd_list
        filtered_checkpoint_models = self._filter_models(all_checkpoint_models)
        
        checkpoint_cards = [
            ModelCard(
                meta, 
                all_models=all_checkpoint_models, 
                index=all_checkpoint_models.index(meta),
                on_delete=self._on_model_delete
            )
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
            ModelCard(
                meta, 
                all_models=all_lora_models, 
                index=all_lora_models.index(meta),
                on_delete=self._on_model_delete
            )
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


# ============================================================================
# Dialog 类定义
# ============================================================================

class ImportModelDialog(ft.AlertDialog):
    """导入模型对话框"""
    
    def __init__(self, page: ft.Page, on_import: callable):
        """
        初始化导入模型对话框
        
        Args:
            page: Flet Page 对象（用于读取剪贴板）
            on_import: 导入回调函数，接收参数 (air_list: list[str])
        """
        self.host_page = page
        self.on_import = on_import
        
        # 创建输入字段
        self.import_dialog_air = ft.TextField(
            label="AIR 标识符（支持多行）",
            multiline=True,
            min_lines=3,
            max_lines=10,
            hint_text="每行一个 AIR，无效行将自动忽略",
            autofocus=True,
        )
        
        self.import_dialog_status = ft.Text("", size=12)
        
        super().__init__(
            modal=True,
            title=ft.Text("从 Civitai 导入模型"),
            content=ft.Column([
                ft.Text("输入 Civitai 模型 AIR 标识符，自动获取并保存模型元数据", size=12),
                ft.Text("支持多行输入，每行一个 AIR，无效行将自动忽略", size=11, weight=ft.FontWeight.BOLD),
                ft.Text("格式：urn:air:{ecosystem}:{type}:civitai:{model_id}@{version_id}", size=11,
                        color=ft.Colors.GREY_500),
                ft.Text("示例：urn:air:sd1:checkpoint:civitai:348620@390021", size=11, color=ft.Colors.GREY_500),
                self.import_dialog_air,
                self.import_dialog_status,
            ], tight=True, spacing=10, width=550),
            actions=[
                ft.TextButton("取消", on_click=self._on_cancel),
                ft.ElevatedButton("批量导入", on_click=self._on_import_click),
            ],
        )
    
    def load_from_clipboard(self):
        """从剪贴板读取并解析 AIR"""
        try:
            self.import_dialog_status.value = ""
            
            # 读取剪贴板并尝试解析 AIR（支持多行）
            try:
                clipboard_text = self.host_page.get_clipboard() if self.host_page else None
                if clipboard_text:
                    clipboard_text = clipboard_text.strip()
                    logger.debug(f"剪贴板内容: {clipboard_text}")
                    
                    # 如果是多行，逐行解析并过滤有效的 AIR
                    lines = clipboard_text.split('\n')
                    valid_airs = []
                    
                    for line in lines:
                        line = line.strip()
                        if not line:
                            continue
                        
                        try:
                            # 尝试解析 AIR
                            air = AIR.parse(line)
                            if air:
                                valid_airs.append(line)
                        except Exception:
                            # 忽略无法解析的行
                            continue
                    
                    # 如果找到有效的 AIR，填充到输入框
                    if valid_airs:
                        self.import_dialog_air.value = '\n'.join(valid_airs)
                        self.import_dialog_status.value = f"✅ 从剪贴板解析到 {len(valid_airs)} 个有效 AIR"
                        self.import_dialog_status.color = ft.Colors.GREEN_700
                        logger.info(f"从剪贴板解析到 {len(valid_airs)} 个有效 AIR")
                    else:
                        logger.debug("剪贴板内容不包含有效的 AIR")
                
            except Exception as e:
                logger.exception(e)
            
        except Exception as e:
            logger.exception(f"加载剪贴板内容失败: {e}")
    
    def _on_import_click(self, e: ft.ControlEvent):
        """处理导入按钮点击"""
        # 验证输入
        input_text = self.import_dialog_air.value.strip()
        logger.debug(f"输入内容: {input_text}")
        
        if not input_text:
            self.import_dialog_status.value = "❌ 请输入模型 AIR 标识符"
            self.import_dialog_status.color = ft.Colors.RED_700
            self.update()
            return
        
        # 解析多行 AIR
        lines = input_text.split('\n')
        valid_air_list = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            try:
                # 解析 AIR 标识符
                air = AIR.parse(line)
                
                if not air:
                    logger.warning(f"AIR 格式错误: {line}")
                    continue
                
                valid_air_list.append(line)
                
            except Exception as e:
                logger.warning(f"解析 AIR 失败: {line}, 错误: {e}")
                continue
        
        if not valid_air_list:
            self.import_dialog_status.value = "❌ 没有找到有效的 AIR 标识符"
            self.import_dialog_status.color = ft.Colors.RED_700
            self.update()
            return
        
        # 关闭对话框
        self.open = False
        self.update()
        
        # 调用导入回调
        if self.on_import:
            self.on_import(valid_air_list)
    
    def _on_cancel(self, e):
        """取消导入"""
        self.open = False
        self.import_dialog_air.value = ""
        self.import_dialog_status.value = ""
        self.update()


class ClearMetadataConfirmDialog(ft.AlertDialog):
    """清空元数据确认对话框"""
    
    def __init__(self, on_confirm: callable):
        """
        初始化清空确认对话框
        
        Args:
            on_confirm: 确认回调函数，无参数
        """
        self.on_confirm = on_confirm
        
        super().__init__(
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
                ft.TextButton("取消", on_click=self._on_cancel),
                ft.ElevatedButton(
                    "确认清空",
                    bgcolor=ft.Colors.RED_700,
                    color=ft.Colors.WHITE,
                    on_click=self._on_confirm_click
                ),
            ],
        )
    
    def _on_confirm_click(self, e):
        """确认清空"""
        # 关闭对话框
        self.open = False
        self.update()
        
        # 调用确认回调
        if self.on_confirm:
            self.on_confirm()
    
    def _on_cancel(self, e):
        """取消清空"""
        self.open = False
        self.update()


class RefreshMetadataConfirmDialog(ft.AlertDialog):
    """刷新元数据确认对话框"""
    
    def __init__(self, air_count: int, on_confirm: callable):
        """
        初始化刷新确认对话框
        
        Args:
            air_count: 要刷新的 AIR 数量
            on_confirm: 确认回调函数，无参数
        """
        self.on_confirm = on_confirm
        
        super().__init__(
            modal=True,
            title=ft.Text("确认重新下载", color=ft.Colors.BLUE_700),
            content=ft.Column([
                ft.Icon(ft.Icons.INFO_OUTLINE, size=48, color=ft.Colors.BLUE_700),
                ft.Text(f"即将重新下载 {air_count} 个模型的元数据", size=16, weight=ft.FontWeight.BOLD),
                ft.Text("此操作将：", size=12),
                ft.Text("• 从 Civitai 重新获取最新的模型信息", size=12),
                ft.Text("• 更新所有示例图片", size=12),
                ft.Text("• 覆盖现有的本地元数据", size=12, color=ft.Colors.GREY_600),
                ft.Divider(),
                ft.Text("⚠️ 此过程可能需要较长时间", size=14, color=ft.Colors.ORANGE_700, weight=ft.FontWeight.BOLD),
            ], tight=True, spacing=10, width=400, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            actions=[
                ft.TextButton("取消", on_click=self._on_cancel),
                ft.ElevatedButton(
                    "确认刷新",
                    bgcolor=ft.Colors.BLUE_700,
                    color=ft.Colors.WHITE,
                    on_click=self._on_confirm_click
                ),
            ],
        )
    
    def _on_confirm_click(self, e):
        """确认刷新"""
        # 关闭对话框
        self.open = False
        self.update()
        
        # 调用确认回调
        if self.on_confirm:
            self.on_confirm()
    
    def _on_cancel(self, e):
        """取消刷新"""
        self.open = False
        self.update()
