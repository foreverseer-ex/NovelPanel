"""
模型示例图片对话框。

以网格形式展示已缓存的示例图，点击单项可查看对应生成参数；
图片与参数均由 ModelMetaService 的本地缓存加载。
"""
import base64
import io
import asyncio

import flet as ft
from schemas.model_meta import ModelMeta
from services.model_meta import model_meta_service


class ExampleImageDialog(ft.AlertDialog):
    """示例图片对话框类。"""
    
    def __init__(self, model_meta: ModelMeta):
        """初始化示例图片对话框。
        
        :param model_meta: 模型元数据对象
        """
        super().__init__()
        self.model_meta = model_meta
        
        # 状态管理
        self._view = 0  # 0: 网格视图, 1: 详情视图
        self._selected_index = -1
        self._images = []  # 存储加载的图片（base64）
        self._loading = True
        
        # 配置对话框属性
        self.modal = True
        self.title_text = ft.Text("示例图片")
        self.title = self.title_text
        
        # 构建内容容器
        self.content_container = ft.Container(width=600, height=400)
        self.content = self.content_container
        
        # 初始渲染（显示loading）
        self._render_loading()
        self._render_actions()
    
    def _pil_to_base64(self, img) -> str:
        """将 PIL Image 编码为 base64 PNG 字符串。
        
        :param img: PIL Image 对象
        :return: base64 编码的字符串
        """
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return base64.b64encode(buf.getvalue()).decode("utf-8")
    
    def _render_loading(self):
        """渲染加载状态。"""
        self.content_container.content = ft.Container(
            content=ft.Column(
                controls=[
                    ft.ProgressRing(),
                    ft.Text("加载示例图片中...", size=14, color=ft.Colors.GREY_600),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            alignment=ft.alignment.center,
        )
    
    def _render_grid(self):
        """渲染图片网格。"""
        if not self._images:
            self.content_container.content = ft.Container(
                content=ft.Text("无示例图片", size=16, color=ft.Colors.GREY_400),
                alignment=ft.alignment.center,
            )
            return
        
        tiles = []
        for idx, img_data in enumerate(self._images):
            tiles.append(
                ft.Container(
                    content=ft.Image(src_base64=img_data, fit=ft.ImageFit.COVER),
                    width=120,
                    height=120,
                    border_radius=8,
                    on_click=lambda e, i=idx: self._enter_detail(e, i),
                )
            )
        
        grid = ft.ResponsiveRow(
            controls=[
                ft.Container(content=t, col={'xs': 6, 'sm': 3, 'md': 2, 'lg': 2})
                for t in tiles
            ],
            run_spacing=10,
            spacing=10,
        )
        self.content_container.content = ft.Column(
            controls=[grid],
            scroll=ft.ScrollMode.AUTO,
        )
    
    def _render_detail(self):
        """渲染详情视图。"""
        idx = self._selected_index
        if 0 <= idx < len(self.model_meta.examples):
            ex = self.model_meta.examples[idx]
            items = [
                ft.Text(f"{k}: {v}", selectable=True)
                for k, v in ex.args.model_dump().items()
            ]
            self.content_container.content = ft.Column(
                controls=items,
                tight=True,
                spacing=6,
                width=600,
                scroll=ft.ScrollMode.AUTO,
            )
        else:
            self.content_container.content = ft.Text("未选择示例")
    
    def _render_content(self):
        """根据当前状态渲染内容。"""
        if self._loading:
            self._render_loading()
        elif self._view == 0:
            self._render_grid()
        else:
            self._render_detail()
    
    def _render_actions(self):
        """根据当前视图状态渲染底部按钮。"""
        if self._view == 0:
            self.actions = [ft.TextButton("关闭", on_click=self._close)]
        else:
            self.actions = [
                ft.TextButton("返回", on_click=self._back_to_list),
                ft.TextButton("关闭", on_click=self._close),
            ]
    
    async def load_images(self):
        """异步加载所有示例图片。"""
        try:
            # 在后台线程加载图片
            images = await asyncio.to_thread(
                model_meta_service.load_example_images, 
                self.model_meta
            )
            
            if images:
                # 转换所有图片为 base64
                self._images = []
                for img in images:
                    b64 = await asyncio.to_thread(self._pil_to_base64, img)
                    self._images.append(b64)
        
        except (FileNotFoundError, IOError):
            # 加载失败，images 保持为空列表
            pass
        
        # 更新状态并重新渲染
        self._loading = False
        self._render_content()
        
        # 刷新显示
        if self.page:
            self.page.update()
    
    def _enter_detail(self, e: ft.ControlEvent, index: int):
        """进入示例图片详情视图。
        
        :param e: 控件事件对象
        :param index: 选中的示例图片索引
        """
        self._selected_index = index
        self._view = 1
        self.title_text.value = "示例详情"
        self._render_content()
        self._render_actions()
        if e.page:
            e.page.update()
    
    def _back_to_list(self, e: ft.ControlEvent):
        """返回示例图片列表视图。
        
        :param e: 控件事件对象
        """
        self._view = 0
        self._selected_index = -1
        self.title_text.value = "示例图片"
        self._render_content()
        self._render_actions()
        if e.page:
            e.page.update()
    
    def _close(self, e: ft.ControlEvent):
        """关闭对话框并重置状态。
        
        :param e: 控件事件对象
        """
        # 重置状态
        self._view = 0
        self._selected_index = -1
        self._loading = True
        self._images = []
        
        if e.page:
            e.page.close(self)
