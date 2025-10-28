"""
设置页面。

允许用户编辑 Civitai 和 SD Forge 的配置。
每个字段在失焦或回车时自动保存。
"""
import flet as ft
from typing import Any
from settings.app_setting import app_settings


class SettingsPage(ft.Column):
    """设置页面类。
    
    提供 UI 界面来编辑应用配置，包括 Civitai 和 SD Forge 设置。
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
        
        self.llm_model_field = ft.TextField(
            label="模型名称",
            value=app_settings.llm.model,
            hint_text=llm_fields['model'].description,
            expand=True,
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
            
            # Civitai 设置区域
            ft.Text("Civitai 设置", size=18, weight=ft.FontWeight.BOLD),
            ft.Container(
                content=ft.Column(
                    controls=[
                        self.civitai_api_token_field,
                        self.civitai_timeout_field,
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
            
            ft.Divider(),
            
            # LLM 设置区域
            ft.Text("AI 大模型设置", size=18, weight=ft.FontWeight.BOLD),
            ft.Container(
                content=ft.Column(
                    controls=[
                        self.llm_model_field,
                        self.llm_api_key_field,
                        self.llm_base_url_field,
                        self.llm_temperature_field,
                        self.llm_developer_mode_switch,
                        self.llm_system_prompt_field,
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
    def _save_llm_model(self):
        """保存 LLM 模型名称。"""
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
    
    def _save_config(self):
        """保存配置到文件并显示提示。"""
        if app_settings.save():
            self._show_success("已保存")
        else:
            self._show_error("保存失败，请查看日志")
    
    def _show_success(self, message: str):
        """显示成功提示。
        
        :param message: 消息内容
        """
        if self.page:
            snack_bar = ft.SnackBar(
                content=ft.Text(message, color=ft.Colors.WHITE),
                bgcolor=ft.Colors.GREEN_700,
                duration=1000,
            )
            self.page.snack_bar = snack_bar
            snack_bar.open = True
            self.page.update()
    
    def _show_error(self, message: str):
        """显示错误提示。
        
        :param message: 消息内容
        """
        if self.page:
            snack_bar = ft.SnackBar(
                content=ft.Text(message, color=ft.Colors.WHITE),
                bgcolor=ft.Colors.RED_700,
                duration=2000,
            )
            self.page.snack_bar = snack_bar
            snack_bar.open = True
            self.page.update()

