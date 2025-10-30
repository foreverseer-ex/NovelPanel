"""
应用主视图，包含左侧导航栏（NavigationRail）与右侧主内容区。
"""
import flet as ft
from pages.home_page import HomePage
from pages.memory_manage_page import MemoryManagePage
from pages.actor_manage_page import ActorManagePage
from pages.content_manage_page import ContentManagePage
from pages.model_manage_page import ModelManagePage
from pages.settings_page import SettingsPage
from pages.chat_page import ChatPage
from pages.help_page import HelpPage
from settings import app_settings

class AppView(ft.Row):
    """应用主视图：左侧 NavigationRail + 右侧可切换的主内容区。

    包含八个目的地：
    - 主页（会话管理）
    - 创作（AI对话）
    - 记忆管理
    - Actor 管理（角色、地点、组织等）
    - 内容管理
    - 模型管理页面
    - 设置页面
    - 帮助页面
    """
    def __init__(self, page: ft.Page):
        """初始化应用主视图。
        
        设置当前页面索引、展开状态和主内容区容器。
        
        Args:
            page: Flet 页面对象
        """
        super().__init__()
        self.page = page
        self.current_page = 0  # 0: 主页, 1: 创作, 2: 记忆, 3: Actor, 4: 内容, 5: 模型, 6: 设置, 7: 帮助
        self.expand = True
        self.main_area = ft.Container(
            expand=True,
            padding=10,
            alignment=ft.alignment.top_left,  # 内容从左上角开始对齐
        )

    def _render_content(self):
        """根据当前选中的页面索引渲染主内容区。"""
        if self.current_page == 0:
            self.main_area.content = HomePage(self.page)
        elif self.current_page == 1:
            self.main_area.content = ChatPage(self.page)
        elif self.current_page == 2:
            self.main_area.content = MemoryManagePage(self.page)
        elif self.current_page == 3:
            self.main_area.content = ActorManagePage()
        elif self.current_page == 4:
            self.main_area.content = ContentManagePage(self.page)
        elif self.current_page == 5:
            self.main_area.content = ModelManagePage()
        elif self.current_page == 6:
            self.main_area.content = SettingsPage()
        elif self.current_page == 7:
            self.main_area.content = HelpPage(self.page)
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
                    icon=ft.Icons.HOME_OUTLINED,
                    selected_icon=ft.Icons.HOME,
                    label="主页",
                ),
                ft.NavigationRailDestination(
                    icon=ft.Icons.BRUSH_OUTLINED,
                    selected_icon=ft.Icons.BRUSH,
                    label="创作",
                ),
                ft.NavigationRailDestination(
                    icon=ft.Icons.MEMORY_OUTLINED,
                    selected_icon=ft.Icons.MEMORY,
                    label="记忆",
                ),
                ft.NavigationRailDestination(
                    icon=ft.Icons.PEOPLE_OUTLINED,
                    selected_icon=ft.Icons.PEOPLE,
                    label="角色",
                ),
                ft.NavigationRailDestination(
                    icon=ft.Icons.EDIT_NOTE_OUTLINED,
                    selected_icon=ft.Icons.EDIT_NOTE,
                    label="内容",
                ),
                ft.NavigationRailDestination(
                    icon=ft.Icons.LIST_ALT_OUTLINED,
                    selected_icon=ft.Icons.LIST_ALT,
                    label="模型",
                ),
                ft.NavigationRailDestination(
                    icon=ft.Icons.SETTINGS_OUTLINED,
                    selected_icon=ft.Icons.SETTINGS,
                    label="设置",
                ),
                ft.NavigationRailDestination(
                    icon=ft.Icons.HELP_OUTLINE,
                    selected_icon=ft.Icons.HELP,
                    label="帮助",
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
    
    在应用关闭时自动保存配置。
    """
    # 注册应用关闭时的回调，自动保存配置
    def on_window_event(e):
        """处理窗口事件。"""
        if e.data == "close":
            # 保存配置
            app_settings.save()

    
    page.on_window_event = on_window_event
    page.window_prevent_close = True  # 阻止默认关闭，使用自定义处理
    
    # 设置页面属性
    page.title = "NovelPanel"
    page.window_full_screen = True  # 默认全屏
    page.theme = ft.Theme(
        color_scheme_seed=ft.Colors.BLUE,
        font_family="Microsoft YaHei",  # 设置全局字体为微软雅黑（Windows 系统自带）
    )
    page.theme_mode = ft.ThemeMode.DARK  # 设置暗色主题，更适合聊天界面
    page.add(AppView(page))


if __name__ == "__main__":
    # 初始化数据库
    from services.db import init_db
    init_db()
    
    # 启动应用
    ft.app(target=main)