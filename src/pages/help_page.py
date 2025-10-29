"""
帮助页面

显示应用的使用说明和文档。
"""

import flet as ft
from pathlib import Path
from loguru import logger


class HelpPage(ft.Container):
    """帮助页面组件"""

    def __init__(self, page: ft.Page = None):
        """
        初始化帮助页面
        
        :param page: Flet 页面对象（用于打开链接）
        """
        super().__init__()
        self.page = page
        self.expand = True
        self.padding = ft.padding.all(20)
        
        # 当前语言
        self.current_lang = "zh"  # zh 或 en
        
        # 读取 README 内容
        self.readme_zh = self._load_readme("README.md")
        self.readme_en = self._load_readme("README.en.md")
        
        # 创建 Markdown 显示组件
        self.markdown = ft.Markdown(
            value=self.readme_zh,
            selectable=True,
            extension_set=ft.MarkdownExtensionSet.GITHUB_WEB,
            on_tap_link=self._handle_link_click,
            expand=True,
        )
        
        # 语言切换按钮
        self.lang_button = ft.IconButton(
            icon=ft.Icons.LANGUAGE,
            tooltip="Switch Language / 切换语言",
            on_click=self._toggle_language,
        )
        
        # 布局
        self.content = ft.Column(
            [
                # 顶部栏
                ft.Container(
                    content=ft.Row(
                        [
                            ft.Text(
                                "帮助文档",
                                size=24,
                                weight=ft.FontWeight.BOLD,
                            ),
                            ft.Row(
                                [
                                    self.lang_button,
                                ],
                                spacing=10,
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    padding=ft.padding.only(bottom=20),
                ),
                # Markdown 内容
                ft.Container(
                    content=ft.Column(
                        [
                            self.markdown,
                        ],
                        scroll=ft.ScrollMode.AUTO,
                        expand=True,
                    ),
                    expand=True,
                    border=ft.border.all(1, ft.Colors.OUTLINE),
                    border_radius=ft.border_radius.all(8),
                    padding=ft.padding.all(20),
                ),
            ],
            expand=True,
            spacing=0,
        )
    
    def _load_readme(self, filename: str) -> str:
        """
        加载 README 文件内容。
        
        :param filename: README 文件名
        :return: README 内容
        """
        try:
            # README 文件在项目根目录
            readme_path = Path(__file__).parent.parent.parent / filename
            if readme_path.exists():
                return readme_path.read_text(encoding="utf-8")
            else:
                return f"# {filename} 未找到\n\nREADME 文件不存在。"
        except Exception as e:
            logger.exception(f"加载文档失败: {filename}")
            return f"# 加载失败\n\n无法加载 {filename}: {str(e)}"
    
    def _handle_link_click(self, e):
        """
        处理链接点击事件。
        
        智能判断链接类型：
        - README.en.md / README.md → 切换语言
        - http/https → 打开网页
        - 本地文件 → 使用系统默认程序打开
        
        :param e: 事件对象，e.data 包含链接 URL
        """
        if not e.data:
            return
        
        link = e.data.strip()
        
        # 1. 检查是否是 README 链接（切换语言）
        if link in ("README.en.md", "README.md"):
            if link == "README.en.md" and self.current_lang == "zh":
                # 切换到英文
                self._toggle_language(None)
            elif link == "README.md" and self.current_lang == "en":
                # 切换到中文
                self._toggle_language(None)
            return
        
        # 2. 检查是否是网页链接
        if link.startswith(("http://", "https://")):
            # 打开网页
            if self.page and hasattr(self.page, 'launch_url'):
                self.page.launch_url(link)
            return
        
        # 3. 本地文件或相对路径
        try:
            import os
            import subprocess
            from pathlib import Path
            
            # 获取项目根目录
            project_root = Path(__file__).parent.parent.parent
            
            # 处理相对路径
            if not Path(link).is_absolute():
                file_path = project_root / link
            else:
                file_path = Path(link)
            
            # 检查文件是否存在
            if file_path.exists():
                # 使用系统默认程序打开
                if os.name == 'nt':  # Windows
                    os.startfile(str(file_path))
                elif os.name == 'posix':  # Linux/macOS
                    if os.uname().sysname == 'Darwin':  # macOS
                        subprocess.run(['open', str(file_path)])
                    else:  # Linux
                        subprocess.run(['xdg-open', str(file_path)])
            else:
                # 文件不存在，尝试作为网页打开
                if self.page and hasattr(self.page, 'launch_url'):
                    self.page.launch_url(link)
        except Exception as ex:
            logger.exception(f"处理链接点击失败: {link}")
            # 出错时尝试作为网页打开
            if self.page and hasattr(self.page, 'launch_url'):
                self.page.launch_url(link)
    
    def _toggle_language(self, _e):
        """切换语言"""
        if self.current_lang == "zh":
            self.current_lang = "en"
            self.markdown.value = self.readme_en
        else:
            self.current_lang = "zh"
            self.markdown.value = self.readme_zh
        
        # 更新标题
        title_text = self.content.controls[0].content.controls[0]
        if isinstance(title_text, ft.Text):
            title_text.value = "Help" if self.current_lang == "en" else "帮助文档"
        
        self.update()

