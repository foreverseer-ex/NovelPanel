"""
应用主视图，包含左侧导航栏（NavigationRail）与右侧主内容区。
"""
import flet as ft
from pages.model_manage_page import ModelManagePage

class AppView(ft.Row):
    """应用主视图：左侧 NavigationRail + 右侧可切换的主内容区。

    目前仅包含一个目的地：模型管理页面。
    """
    def __init__(self):
        """初始化应用主视图。
        
        设置当前页面索引、展开状态和主内容区容器。
        """
        super().__init__()
        self.current_page = 0  # 0: 模型管理
        self.expand = True
        self.main_area = ft.Container(expand=True, padding=10)

    def _render_content(self):
        """根据当前选中的页面索引渲染主内容区。"""
        if self.current_page == 0:
            self.main_area.content = ModelManagePage()
        else:
            self.main_area.content = ft.Container()

    def _goto(self, page_index: int):
        """跳转到指定页面并刷新布局。

        :param page_index: 导航栏中的目的地索引
        """
        if page_index == self.current_page:
            return

        self.current_page = page_index
        self._render_content()
        self.update()

    def did_mount(self):
        """
        构建导航栏和初始内容
        """
        # 构建导航栏和初始内容
        rail = ft.NavigationRail(
            selected_index=self.current_page,
            label_type=ft.NavigationRailLabelType.ALL,
            min_width=72,
            min_extended_width=200,
            extended=False,
            destinations=[
                ft.NavigationRailDestination(
                    icon=ft.Icons.LIST_ALT_OUTLINED,
                    selected_icon=ft.Icons.LIST_ALT,
                    label="模型",
                ),
            ],
            on_change=lambda e: self._goto(e.control.selected_index),
        )
        self._render_content()
        self.controls = [rail, ft.VerticalDivider(width=1), self.main_area]
        self.update()


def main(page: ft.Page):
    """
    主函数：注册主题、字体与窗口标题，挂载 AppView。
    """
    page.title = "NovelPanel"
    page.theme = ft.Theme(
        color_scheme_seed=ft.Colors.BLUE,
        font_family="Microsoft YaHei",  # 设置全局字体为微软雅黑（Windows 系统自带）
    )
    page.add(AppView())


if __name__ == "__main__":
    ft.app(target=main)