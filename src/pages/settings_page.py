"""
设置页面。

允许用户编辑应用的各项配置，包括绘图服务、LLM、Civitai 和 SD Forge 设置。
每个字段在失焦或回车时自动保存。
"""
import flet as ft
from typing import Any
from flet_toast import flet_toast
from flet_toast.Types import Position
from settings import app_settings
from constants.llm import (
    LlmProvider,
    get_base_url_for_provider,
    get_models_for_provider,
)
from services.model_meta import civitai_model_meta_service, local_model_meta_service


class SettingsPage(ft.Column):
    """设置页面类。
    
    提供 UI 界面来编辑应用配置，包括：
    - 绘图服务设置
    - AI 大模型设置
    - Civitai 设置
    - SD Forge 设置
    
    所有字段在失焦或回车时自动保存并验证。
    """
    
    def __init__(self):
        """初始化设置页面。"""
        super().__init__()
        self.spacing = 20
        self.scroll = ft.ScrollMode.AUTO
        
        # 保存旧值用于验证失败时恢复
        self._old_values = {
            'civitai_timeout': app_settings.civitai.timeout,
            'sd_forge_timeout': app_settings.sd_forge.timeout,
            'sd_forge_generate_timeout': app_settings.sd_forge.generate_timeout,
            'llm_temperature': app_settings.llm.temperature,
        }
        
        # Civitai 设置字段
        civitai_fields: Any = app_settings.civitai.model_fields
        
        self.civitai_api_token_field = ft.TextField(
            label="Civitai API Token",
            value=app_settings.civitai.api_token or "",
            hint_text=civitai_fields['api_token'].description,
            password=True,
            can_reveal_password=True,
            expand=True,
            on_blur=lambda _: self._save_civitai_api_token(),
            on_submit=lambda _: self._save_civitai_api_token(),
        )
        
        self.civitai_timeout_field = ft.TextField(
            label="Civitai 请求超时",
            value=str(app_settings.civitai.timeout),
            hint_text=civitai_fields['timeout'].description,
            keyboard_type=ft.KeyboardType.NUMBER,
            width=200,
            on_blur=lambda _: self._save_civitai_timeout(),
            on_submit=lambda _: self._save_civitai_timeout(),
        )
        
        # 从 SD Forge 导入按钮
        self.civitai_sync_button = ft.ElevatedButton(
            text="从 SD Forge 导入",
            icon=ft.Icons.SYNC,
            tooltip="扫描 SD-Forge 目录中的 .safetensors 文件，从 Civitai 获取元数据并保存到本地",
            on_click=self._on_sync_button_click,
        )
        
        # SD Forge 设置字段
        sd_forge_fields: Any = app_settings.sd_forge.model_fields
        
        self.sd_forge_base_url_field = ft.TextField(
            label="SD Forge Base URL",
            value=app_settings.sd_forge.base_url,
            hint_text=sd_forge_fields['base_url'].description,
            expand=True,
            on_blur=lambda _: self._save_sd_forge_base_url(),
            on_submit=lambda _: self._save_sd_forge_base_url(),
        )
        
        self.sd_forge_home_field = ft.TextField(
            label="SD Forge 安装目录",
            value=app_settings.sd_forge.home,
            hint_text=sd_forge_fields['home'].description,
            expand=True,
            on_blur=lambda _: self._save_sd_forge_home(),
            on_submit=lambda _: self._save_sd_forge_home(),
        )
        
        self.sd_forge_timeout_field = ft.TextField(
            label="SD Forge 请求超时",
            value=str(app_settings.sd_forge.timeout),
            hint_text=sd_forge_fields['timeout'].description,
            keyboard_type=ft.KeyboardType.NUMBER,
            width=200,
            on_blur=lambda _: self._save_sd_forge_timeout(),
            on_submit=lambda _: self._save_sd_forge_timeout(),
        )
        
        self.sd_forge_generate_timeout_field = ft.TextField(
            label="SD Forge 生成超时",
            value=str(app_settings.sd_forge.generate_timeout),
            hint_text=sd_forge_fields['generate_timeout'].description,
            keyboard_type=ft.KeyboardType.NUMBER,
            width=200,
            on_blur=lambda _: self._save_sd_forge_generate_timeout(),
            on_submit=lambda _: self._save_sd_forge_generate_timeout(),
        )
        
        # LLM 设置字段
        llm_fields: Any = app_settings.llm.model_fields
        
        # Provider 下拉选择
        self.llm_provider_dropdown = ft.Dropdown(
            label="提供商",
            hint_text=llm_fields['provider'].description,
            value=app_settings.llm.provider,
            options=[
                ft.dropdown.Option(key=LlmProvider.XAI, text="xAI (Grok)"),
                ft.dropdown.Option(key=LlmProvider.OPENAI, text="OpenAI (GPT)"),
                ft.dropdown.Option(key=LlmProvider.OLLAMA, text="Ollama (本地)"),
                ft.dropdown.Option(key=LlmProvider.ANTHROPIC, text="Anthropic (Claude)"),
                ft.dropdown.Option(key=LlmProvider.GOOGLE, text="Google (Gemini)"),
                ft.dropdown.Option(key=LlmProvider.CUSTOM, text="自定义"),
            ],
            width=250,
            on_change=lambda e: self._on_provider_changed(e.control.value),
        )
        
        # Model 下拉选择（根据 provider 动态更新）
        current_models = get_models_for_provider(app_settings.llm.provider)
        self.llm_model_dropdown = ft.Dropdown(
            label="模型",
            hint_text=llm_fields['model'].description,
            value=app_settings.llm.model if app_settings.llm.model in current_models else None,
            options=[ft.dropdown.Option(key=m, text=m) for m in current_models] if current_models else [],
            width=350,
            on_change=lambda e: self._on_model_changed(e.control.value),
        )
        
        # 自定义模型输入框（当选择自定义提供商或手动输入时）
        self.llm_model_field = ft.TextField(
            label="自定义模型名称",
            value=app_settings.llm.model if not current_models or app_settings.llm.model not in current_models else "",
            hint_text="手动输入模型名称",
            expand=True,
            visible=app_settings.llm.provider == LlmProvider.CUSTOM or not current_models,
            on_blur=lambda _: self._save_llm_model(),
            on_submit=lambda _: self._save_llm_model(),
        )
        
        self.llm_api_key_field = ft.TextField(
            label="API Key",
            value=app_settings.llm.api_key,
            hint_text=llm_fields['api_key'].description,
            password=True,
            can_reveal_password=True,
            expand=True,
            on_blur=lambda _: self._save_llm_api_key(),
            on_submit=lambda _: self._save_llm_api_key(),
        )
        
        self.llm_base_url_field = ft.TextField(
            label="API Base URL",
            value=app_settings.llm.base_url,
            hint_text=llm_fields['base_url'].description,
            expand=True,
            on_blur=lambda _: self._save_llm_base_url(),
            on_submit=lambda _: self._save_llm_base_url(),
        )
        
        self.llm_temperature_field = ft.TextField(
            label="Temperature",
            value=str(app_settings.llm.temperature),
            hint_text=llm_fields['temperature'].description,
            keyboard_type=ft.KeyboardType.NUMBER,
            width=200,
            on_blur=lambda _: self._save_llm_temperature(),
            on_submit=lambda _: self._save_llm_temperature(),
        )
        
        self.llm_developer_mode_switch = ft.Switch(
            label=llm_fields['developer_mode'].description,
            value=app_settings.llm.developer_mode,
            on_change=lambda _: self._save_llm_developer_mode(),
        )
        
        self.llm_system_prompt_field = ft.TextField(
            label="系统提示词",
            value=app_settings.llm.system_prompt,
            hint_text=llm_fields['system_prompt'].description,
            multiline=True,
            min_lines=5,
            max_lines=10,
            expand=True,
            on_blur=lambda _: self._save_llm_system_prompt(),
        )
        
        # LLM 重新初始化按钮
        self.llm_reinit_button = ft.ElevatedButton(
            text="重新初始化 LLM",
            icon=ft.Icons.REFRESH,
            tooltip="应用当前配置并重新初始化 LLM 服务",
            on_click=self._on_llm_reinit_click,
        )
        
        # Draw 设置字段
        draw_fields: Any = app_settings.draw.model_fields
        
        self.draw_backend_dropdown = ft.Dropdown(
            label="绘图后端",
            hint_text=draw_fields['backend'].description,
            value=app_settings.draw.backend,
            options=[
                ft.dropdown.Option(key="sd_forge", text="SD-Forge (本地)"),
                ft.dropdown.Option(key="civitai", text="Civitai (云端)"),
            ],
            width=300,
            on_change=lambda e: self._save_draw_backend(e.control.value),
        )
        
        # 构建页面
        self.controls = [
            ft.Text("应用设置", size=24, weight=ft.FontWeight.BOLD),
            ft.Container(
                content=ft.Text(
                    "提示：修改后回车或点击其他地方自动保存",
                    size=12,
                    color=ft.Colors.GREY_600,
                    italic=True,
                ),
                padding=ft.padding.only(bottom=10),
            ),
            ft.Divider(),
            
            # Draw 设置区域
            ft.Text("绘图服务设置", size=18, weight=ft.FontWeight.BOLD),
            ft.Container(
                content=ft.Column(
                    controls=[
                        self.draw_backend_dropdown,
                    ],
                    spacing=10,
                ),
                padding=ft.padding.only(left=20),
            ),
            
            ft.Divider(),
            
            # LLM 设置区域
            ft.Text("AI 大模型设置", size=18, weight=ft.FontWeight.BOLD),
            ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Row(
                            controls=[
                                self.llm_provider_dropdown,
                                self.llm_model_dropdown,
                            ],
                            spacing=20,
                        ),
                        self.llm_model_field,
                        self.llm_api_key_field,
                        self.llm_base_url_field,
                        self.llm_temperature_field,
                        self.llm_developer_mode_switch,
                        self.llm_system_prompt_field,
                        self.llm_reinit_button,
                    ],
                    spacing=10,
                ),
                padding=ft.padding.only(left=20),
            ),
            
            ft.Divider(),
            
            # Civitai 设置区域
            ft.Text("Civitai 设置", size=18, weight=ft.FontWeight.BOLD),
            ft.Container(
                content=ft.Column(
                    controls=[
                        self.civitai_api_token_field,
                        self.civitai_timeout_field,
                        self.civitai_sync_button,
                    ],
                    spacing=10,
                ),
                padding=ft.padding.only(left=20),
            ),
            
            ft.Divider(),
            
            # SD Forge 设置区域
            ft.Text("SD Forge 设置", size=18, weight=ft.FontWeight.BOLD),
            ft.Container(
                content=ft.Column(
                    controls=[
                        self.sd_forge_base_url_field,
                        self.sd_forge_home_field,
                        ft.Row(
                            controls=[
                                self.sd_forge_timeout_field,
                                self.sd_forge_generate_timeout_field,
                            ],
                            spacing=20,
                        ),
                    ],
                    spacing=10,
                ),
                padding=ft.padding.only(left=20),
            ),
        ]
    
    # Civitai 设置保存方法
    def _save_civitai_api_token(self):
        """保存 Civitai API Token。"""
        new_value = self.civitai_api_token_field.value.strip() or None
        app_settings.civitai.api_token = new_value
        self._save_config()
    
    def _save_civitai_timeout(self):
        """保存 Civitai 请求超时。"""
        try:
            new_value = float(self.civitai_timeout_field.value)
            if new_value <= 0:
                raise ValueError("超时时间必须大于 0")
            
            app_settings.civitai.timeout = new_value
            self._old_values['civitai_timeout'] = new_value
            self._save_config()
            
        except ValueError as e:
            self._show_error(f"超时时间格式错误: {e}")
            # 恢复旧值
            self.civitai_timeout_field.value = str(self._old_values['civitai_timeout'])
            self.civitai_timeout_field.update()
    
    # SD Forge 设置保存方法
    def _save_sd_forge_base_url(self):
        """保存 SD Forge Base URL。"""
        new_value = self.sd_forge_base_url_field.value.strip()
        if not new_value:
            self._show_error("Base URL 不能为空")
            self.sd_forge_base_url_field.value = app_settings.sd_forge.base_url
            self.sd_forge_base_url_field.update()
            return
        
        app_settings.sd_forge.base_url = new_value
        self._save_config()
    
    def _save_sd_forge_home(self):
        """保存 SD Forge 安装目录。"""
        new_value = self.sd_forge_home_field.value.strip()
        if not new_value:
            self._show_error("安装目录不能为空")
            self.sd_forge_home_field.value = app_settings.sd_forge.home
            self.sd_forge_home_field.update()
            return
        
        app_settings.sd_forge.home = new_value
        self._save_config()
    
    def _save_sd_forge_timeout(self):
        """保存 SD Forge 请求超时。"""
        try:
            new_value = float(self.sd_forge_timeout_field.value)
            if new_value <= 0:
                raise ValueError("超时时间必须大于 0")
            
            app_settings.sd_forge.timeout = new_value
            self._old_values['sd_forge_timeout'] = new_value
            self._save_config()
            
        except ValueError as e:
            self._show_error(f"超时时间格式错误: {e}")
            # 恢复旧值
            self.sd_forge_timeout_field.value = str(self._old_values['sd_forge_timeout'])
            self.sd_forge_timeout_field.update()
    
    def _save_sd_forge_generate_timeout(self):
        """保存 SD Forge 生成超时。"""
        try:
            new_value = float(self.sd_forge_generate_timeout_field.value)
            if new_value <= 0:
                raise ValueError("超时时间必须大于 0")
            
            app_settings.sd_forge.generate_timeout = new_value
            self._old_values['sd_forge_generate_timeout'] = new_value
            self._save_config()
            
        except ValueError as e:
            self._show_error(f"超时时间格式错误: {e}")
            # 恢复旧值
            self.sd_forge_generate_timeout_field.value = str(self._old_values['sd_forge_generate_timeout'])
            self.sd_forge_generate_timeout_field.update()
    
    # LLM 设置保存方法
    def _on_provider_changed(self, provider: str):
        """当提供商改变时的处理。"""
        # 保存 provider
        app_settings.llm.provider = provider
        
        # 自动填充 base_url
        base_url = get_base_url_for_provider(provider)
        self.llm_base_url_field.value = base_url
        app_settings.llm.base_url = base_url
        
        # 更新模型列表
        models = get_models_for_provider(provider)
        
        if models:
            # 有推荐模型，显示下拉框
            self.llm_model_dropdown.options = [ft.dropdown.Option(key=m, text=m) for m in models]
            self.llm_model_dropdown.value = models[0]  # 默认选择第一个
            self.llm_model_dropdown.visible = True
            self.llm_model_field.visible = False
            
            # 保存第一个模型
            app_settings.llm.model = models[0]
        else:
            # 无推荐模型（自定义），显示输入框
            self.llm_model_dropdown.visible = False
            self.llm_model_field.visible = True
            self.llm_model_field.value = ""
        
        # 更新页面
        self._save_config()
        if self.page:
            self.llm_model_dropdown.update()
            self.llm_model_field.update()
            self.llm_base_url_field.update()
    
    def _on_model_changed(self, model: str):
        """当模型改变时的处理。"""
        if model:
            app_settings.llm.model = model
            self._save_config()
    
    def _save_llm_model(self):
        """保存 LLM 模型名称（自定义输入）。"""
        new_value = self.llm_model_field.value.strip()
        if not new_value:
            self._show_error("模型名称不能为空")
            self.llm_model_field.value = app_settings.llm.model
            self.llm_model_field.update()
            return
        
        app_settings.llm.model = new_value
        self._save_config()
    
    def _save_llm_api_key(self):
        """保存 LLM API Key。"""
        new_value = self.llm_api_key_field.value.strip()
        if not new_value:
            self._show_error("API Key 不能为空")
            self.llm_api_key_field.value = app_settings.llm.api_key
            self.llm_api_key_field.update()
            return
        
        app_settings.llm.api_key = new_value
        self._save_config()
    
    def _save_llm_base_url(self):
        """保存 LLM Base URL。"""
        new_value = self.llm_base_url_field.value.strip()
        if not new_value:
            self._show_error("Base URL 不能为空")
            self.llm_base_url_field.value = app_settings.llm.base_url
            self.llm_base_url_field.update()
            return
        
        app_settings.llm.base_url = new_value
        self._save_config()
    
    def _save_llm_temperature(self):
        """保存 LLM Temperature。"""
        try:
            new_value = float(self.llm_temperature_field.value)
            if not (0.0 <= new_value <= 2.0):
                raise ValueError("Temperature 必须在 0.0 到 2.0 之间")
            
            app_settings.llm.temperature = new_value
            self._old_values['llm_temperature'] = new_value
            self._save_config()
            
        except ValueError as e:
            self._show_error(f"Temperature 格式错误: {e}")
            # 恢复旧值
            self.llm_temperature_field.value = str(self._old_values['llm_temperature'])
            self.llm_temperature_field.update()
    
    def _save_llm_developer_mode(self):
        """保存 LLM 开发者模式。"""
        app_settings.llm.developer_mode = self.llm_developer_mode_switch.value
        self._save_config()
    
    def _save_llm_system_prompt(self):
        """保存 LLM 系统提示词。"""
        new_value = self.llm_system_prompt_field.value.strip()
        if not new_value:
            self._show_error("系统提示词不能为空")
            self.llm_system_prompt_field.value = app_settings.llm.system_prompt
            self.llm_system_prompt_field.update()
            return
        
        app_settings.llm.system_prompt = new_value
        self._save_config()
    
    def _on_llm_reinit_click(self, _e):
        """处理 LLM 重新初始化按钮点击。"""
        if self.page:
            self.page.run_task(self._reinit_llm)
    
    async def _reinit_llm(self):
        """重新初始化 LLM 服务（异步任务）。"""
        self.llm_reinit_button.disabled = True
        self.llm_reinit_button.text = "正在初始化..."
        self.llm_reinit_button.update()
        
        try:
            # 导入 LLM 服务
            from services.llm import get_current_llm_service
            
            # 重新调用工厂函数创建新实例（旧实例会被垃圾回收）
            from loguru import logger
            logger.info("重新创建 LLM 服务实例")
            new_service = get_current_llm_service()
            success = new_service.is_ready()
            logger.debug(f"新服务实例: {new_service}")
            
            if success:
                self._show_success("LLM 服务初始化成功！")
            else:
                self._show_error("LLM 服务初始化失败，请检查配置")
                
        except Exception as e:
            logger.exception(f"初始化失败: {e}")
            self._show_error(f"初始化失败: {e}")
        
        finally:
            self.llm_reinit_button.disabled = False
            self.llm_reinit_button.text = "重新初始化 LLM"
            self.llm_reinit_button.update()
    
    # Draw 设置保存方法
    def _save_draw_backend(self, backend: str):
        """保存绘图后端。"""
        if backend not in ("sd_forge", "civitai"):
            self._show_error(f"未知的绘图后端: {backend}")
            self.draw_backend_dropdown.value = app_settings.draw.backend
            self.draw_backend_dropdown.update()
            return
        
        app_settings.draw.backend = backend
        self._save_config()
    
    def _save_config(self):
        """保存配置到文件并显示提示。"""
        if app_settings.save():
            self._show_success("已保存")
        else:
            self._show_error("保存失败，请查看日志")
    
    def _on_sync_button_click(self, _e):
        """处理同步按钮点击事件，立即显示 Toast 并在后台执行导入。"""
        # ✅ 立即显示正在导入的 Toast
        self._show_toast("⏳ 正在从 SD Forge 导入模型...", ft.Colors.BLUE_700, duration=2000)
        
        if self.page:
            # 使用 page.run_task 来执行异步任务
            self.page.run_task(self._sync_from_sd_forge)
    
    async def _sync_from_sd_forge(self):
        """从 SD Forge 导入模型元数据（后台运行）。"""
        
        try:
            # 调用同步方法
            stats = await civitai_model_meta_service.sync_from_sd_forge()
            
            # 刷新本地元数据缓存
            local_model_meta_service.flush()
            
            # 显示结果
            message = (
                f"✅ 导入完成！\n"
                f"成功: {stats['success']} | "
                f"失败: {stats['failed']} | "
                f"跳过: {stats['skipped']}"
            )
            self._show_toast(message, ft.Colors.GREEN_700, duration=4000)
            
        except Exception as e:
            logger.exception(f"导入失败: {e}")
            self._show_toast(f"❌ 导入失败: {e}", ft.Colors.RED_700)
    
    def _show_toast(self, message: str, bgcolor=ft.Colors.GREEN_700, duration: int = 1000):
        """显示 Toast 提示。
        
        :param message: 消息内容
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
    
    def _show_success(self, message: str, duration: int = 1000):
        """显示成功提示（已废弃，使用 _show_toast 替代）。
        
        :param message: 消息内容
        :param duration: 显示时长（毫秒）
        """
        self._show_toast(message, ft.Colors.GREEN_700, duration)
    
    def _show_error(self, message: str, duration: int = 2000):
        """显示错误提示（已废弃，使用 _show_toast 替代）。
        
        :param message: 消息内容
        :param duration: 显示时长（毫秒）
        """
        self._show_toast(message, ft.Colors.RED_700, duration)

