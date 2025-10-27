"""
入口
"""
import flet as ft
from pages.app import AppView


def main(page: ft.Page):
    """
    主函数：注册主题与窗口标题，挂载 AppView。
    """
    page.title = "AI Storer"
    page.theme = ft.Theme(color_scheme_seed=ft.Colors.BLUE)
    page.add(AppView())


if __name__ == "__main__":
    ft.app(target=main)
