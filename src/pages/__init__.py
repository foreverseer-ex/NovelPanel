"""应用页面包。

包含组装应用 UI 的顶层 Flet 视图。
"""
from .model_manage_page import ModelManagePage
from .settings_page import SettingsPage

__all__ = [
    'ModelManagePage',
    'SettingsPage',
]
