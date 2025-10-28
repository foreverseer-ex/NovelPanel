"""
设置页面。

允许用户编辑 Civitai 和 SD Forge 的配置。
每个字段在失焦或回车时自动保存。
"""
import flet as ft
from settings.civitai_setting import civitai_settings
from settings.sd_forge_setting import sd_forge_settings
from settings.config_manager import config_manager


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
            'civitai_timeout': civitai_settings.timeout,
            'sd_forge_timeout': sd_forge_settings.timeout,
            'sd_forge_generate_timeout': sd_forge_settings.generate_timeout,
        }
        
        # Civitai 设置字段
        self.civitai_base_url_field = ft.TextField(
            label="Civitai Base URL",
            value=civitai_settings.base_url,
            hint_text="https://civitai.com",
            expand=True,
            on_blur=lambda _: self._save_civitai_base_url(),
            on_submit=lambda _: self._save_civitai_base_url(),
        )
        
        self.civitai_api_key_field = ft.TextField(
            label="Civitai API Key (可选)",
            value=civitai_settings.api_key or "",
            hint_text="输入 API Key 以访问私有内容",
            password=True,
            can_reveal_password=True,
            expand=True,
            on_blur=lambda _: self._save_civitai_api_key(),
            on_submit=lambda _: self._save_civitai_api_key(),
        )
        
        self.civitai_timeout_field = ft.TextField(
            label="Civitai 请求超时 (秒)",
            value=str(civitai_settings.timeout),
            keyboard_type=ft.KeyboardType.NUMBER,
            width=200,
            on_blur=lambda _: self._save_civitai_timeout(),
            on_submit=lambda _: self._save_civitai_timeout(),
        )
        
        # SD Forge 设置字段
        self.sd_forge_base_url_field = ft.TextField(
            label="SD Forge Base URL",
            value=sd_forge_settings.base_url,
            hint_text="http://127.0.0.1:7860",
            expand=True,
            on_blur=lambda _: self._save_sd_forge_base_url(),
            on_submit=lambda _: self._save_sd_forge_base_url(),
        )
        
        self.sd_forge_home_field = ft.TextField(
            label="SD Forge 安装目录",
            value=sd_forge_settings.home,
            hint_text=r"C:\path\to\sd-webui-forge",
            expand=True,
            on_blur=lambda _: self._save_sd_forge_home(),
            on_submit=lambda _: self._save_sd_forge_home(),
        )
        
        self.sd_forge_timeout_field = ft.TextField(
            label="SD Forge 请求超时 (秒)",
            value=str(sd_forge_settings.timeout),
            keyboard_type=ft.KeyboardType.NUMBER,
            width=200,
            on_blur=lambda _: self._save_sd_forge_timeout(),
            on_submit=lambda _: self._save_sd_forge_timeout(),
        )
        
        self.sd_forge_generate_timeout_field = ft.TextField(
            label="SD Forge 生成超时 (秒)",
            value=str(sd_forge_settings.generate_timeout),
            keyboard_type=ft.KeyboardType.NUMBER,
            width=200,
            on_blur=lambda _: self._save_sd_forge_generate_timeout(),
            on_submit=lambda _: self._save_sd_forge_generate_timeout(),
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
                        self.civitai_base_url_field,
                        self.civitai_api_key_field,
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
        ]
    
    # Civitai 设置保存方法
    def _save_civitai_base_url(self):
        """保存 Civitai Base URL。"""
        new_value = self.civitai_base_url_field.value.strip()
        if not new_value:
            self._show_error("Base URL 不能为空")
            self.civitai_base_url_field.value = civitai_settings.base_url
            self.civitai_base_url_field.update()
            return
        
        civitai_settings.base_url = new_value
        self._save_config()
    
    def _save_civitai_api_key(self):
        """保存 Civitai API Key。"""
        new_value = self.civitai_api_key_field.value.strip() or None
        civitai_settings.api_key = new_value
        self._save_config()
    
    def _save_civitai_timeout(self):
        """保存 Civitai 请求超时。"""
        try:
            new_value = float(self.civitai_timeout_field.value)
            if new_value <= 0:
                raise ValueError("超时时间必须大于 0")
            
            civitai_settings.timeout = new_value
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
            self.sd_forge_base_url_field.value = sd_forge_settings.base_url
            self.sd_forge_base_url_field.update()
            return
        
        sd_forge_settings.base_url = new_value
        self._save_config()
    
    def _save_sd_forge_home(self):
        """保存 SD Forge 安装目录。"""
        new_value = self.sd_forge_home_field.value.strip()
        if not new_value:
            self._show_error("安装目录不能为空")
            self.sd_forge_home_field.value = sd_forge_settings.home
            self.sd_forge_home_field.update()
            return
        
        sd_forge_settings.home = new_value
        self._save_config()
    
    def _save_sd_forge_timeout(self):
        """保存 SD Forge 请求超时。"""
        try:
            new_value = float(self.sd_forge_timeout_field.value)
            if new_value <= 0:
                raise ValueError("超时时间必须大于 0")
            
            sd_forge_settings.timeout = new_value
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
            
            sd_forge_settings.generate_timeout = new_value
            self._old_values['sd_forge_generate_timeout'] = new_value
            self._save_config()
            
        except ValueError as e:
            self._show_error(f"超时时间格式错误: {e}")
            # 恢复旧值
            self.sd_forge_generate_timeout_field.value = str(self._old_values['sd_forge_generate_timeout'])
            self.sd_forge_generate_timeout_field.update()
    
    def _save_config(self):
        """保存配置到文件并显示提示。"""
        if config_manager.save():
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

