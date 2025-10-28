"""
异步加载图片组件。

通用的图片容器，支持异步加载、loading 状态、错误处理。
可在所有需要显示模型示例图的场景复用。
"""
import base64
import io
import asyncio
from typing import Callable, Optional

import flet as ft
from PIL import Image

from schemas.model_meta import ModelMeta
from services.model_meta import model_meta_service


class AsyncImage(ft.Container):
    """异步加载图片的容器组件。
    
    特性：
    - 初始显示 loading 状态
    - 异步加载图片（不阻塞 UI）
    - 自动错误处理
    - 可配置尺寸、样式、点击事件
    """
    
    def __init__(
        self,
        model_meta: ModelMeta,
        index: int = 0,
        width: int = 120,
        height: int = 120,
        fit: ft.ImageFit = ft.ImageFit.COVER,
        on_click: Optional[Callable] = None,
        border_radius: int = 8,
        loading_size: int = 20,
        loading_text: str = "加载中",
        loading_text_size: int = 10,
    ):
        """初始化异步图片组件。
        
        :param model_meta: 模型元数据
        :param index: 示例图片索引
        :param width: 容器宽度
        :param height: 容器高度
        :param fit: 图片填充模式
        :param on_click: 点击事件回调
        :param border_radius: 圆角半径
        :param loading_size: loading 环尺寸
        :param loading_text: loading 文本
        :param loading_text_size: loading 文本大小
        """
        # 初始化为 loading 状态
        # 根据是否有文本决定显示内容
        loading_controls = [ft.ProgressRing(width=loading_size, height=loading_size, stroke_width=2)]
        if loading_text:  # 只有文本非空时才添加
            loading_controls.append(
                ft.Text(loading_text, size=loading_text_size, color=ft.Colors.GREY_600)
            )
        
        super().__init__(
            width=width,
            height=height,
            bgcolor=None,  # 透明背景
            border_radius=border_radius,
            alignment=ft.alignment.center,
            content=ft.Column(
                controls=loading_controls,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER,  # 垂直居中
                spacing=4,
            ),
            on_click=on_click,
        )
        
        # 保存配置
        self.model_meta = model_meta
        self.index = index
        self.fit = fit
        self._loaded = False
    
    @staticmethod
    def _pil_to_base64(img: Image.Image) -> str:
        """将 PIL Image 编码为 base64 PNG 字符串。
        
        :param img: PIL Image 对象
        :return: base64 编码的字符串
        """
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return base64.b64encode(buf.getvalue()).decode("utf-8")
    
    async def load(self):
        """异步加载图片。
        
        加载完成后自动更新显示。
        如果已加载过，则跳过。
        """
        if self._loaded:
            return
        
        try:
            # 在后台线程加载图片
            img = await asyncio.to_thread(
                model_meta_service.load_example_image,
                self.model_meta,
                self.index
            )
            
            if img:
                # 转换为 base64
                b64 = await asyncio.to_thread(self._pil_to_base64, img)
                # 更新内容为图片
                self.content = ft.Image(src_base64=b64, fit=self.fit)
                self.bgcolor = None
                self.clip_behavior = ft.ClipBehavior.HARD_EDGE
                self._loaded = True
            else:
                # 没有图片
                self.content = ft.Text(
                    "无图片",
                    size=10,
                    color=ft.Colors.RED_400
                )
                self.bgcolor = ft.Colors.GREY_800
        
        except (FileNotFoundError, IOError, Exception):
            # 加载失败
            self.content = ft.Text(
                "加载失败",
                size=10,
                color=ft.Colors.RED_400
            )
            self.bgcolor = ft.Colors.GREY_300
        
        # 刷新显示
        if self.page:
            self.page.update()
    
    def did_mount(self):
        """组件挂载后自动触发加载。"""
        super().did_mount()
        if self.page:
            self.page.run_task(self.load)

