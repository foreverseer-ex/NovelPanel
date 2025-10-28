"""
异步加载图片组件。

通用的图片容器，支持异步加载、loading 状态、错误处理。
可在所有需要显示模型示例图的场景复用。
"""
import base64
import asyncio
from typing import Callable, Optional
from pathlib import Path
from collections import OrderedDict

import flet as ft

from schemas.model_meta import ModelMeta
from services.model_meta import model_meta_service


class ImageCache:
    """图片 Base64 LRU 缓存类。
    
    使用 OrderedDict 实现 LRU（最近最少使用）缓存策略。
    当缓存满时，自动删除最久未使用的图片。
    
    通过 `cache[path]` 访问图片，自动处理缓存未命中的情况。
    """
    
    def __init__(self, max_size: int = 100):
        """初始化图片缓存。
        
        :param max_size: 最大缓存图片数量，默认 100
        """
        self._cache: OrderedDict[Path, str] = OrderedDict()
        self._max_size = max_size
    
    def get_cached(self, path: Path) -> Optional[str]:
        """同步获取已缓存的图片 base64 数据（不触发文件读取）。
        
        :param path: 图片文件路径
        :return: base64 编码的图片数据，如果不在缓存中则返回 None
        """
        if path in self._cache:
            # 移动到末尾（标记为最近使用）
            self._cache.move_to_end(path)
            return self._cache[path]
        return None
    
    def __getitem__(self, path: Path) -> str:
        """获取缓存的图片 base64 数据。
        
        如果缓存命中，返回缓存值并标记为最近使用。
        如果缓存未命中，从文件读取、缓存并返回。
        
        :param path: 图片文件路径
        :return: base64 编码的图片数据
        :raises FileNotFoundError: 文件不存在
        :raises IOError: 文件读取失败
        """
        # 缓存命中
        cached = self.get_cached(path)
        if cached is not None:
            return cached
        
        # 缓存未命中，从文件读取
        with open(path, 'rb') as f:
            base64_data = base64.b64encode(f.read()).decode('utf-8')
        
        # 存入缓存
        self._add_to_cache(path, base64_data)
        
        return base64_data
    
    def _add_to_cache(self, path: Path, base64_data: str):
        """将数据添加到缓存。
        
        如果缓存已满，自动删除最久未使用的项。
        
        :param path: 图片文件路径
        :param base64_data: base64 编码的图片数据
        """
        # 如果缓存已满，删除最旧的项
        if len(self._cache) >= self._max_size:
            # popitem(last=False) 删除第一个（最旧的）项
            self._cache.popitem(last=False)
        
        # 添加到末尾（最新）
        self._cache[path] = base64_data
    
    def clear(self):
        """清空所有缓存。"""
        self._cache.clear()
    
    def __len__(self) -> int:
        """返回当前缓存的图片数量。"""
        return len(self._cache)
    
    def __contains__(self, path: Path) -> bool:
        """检查路径是否在缓存中。
        
        :param path: 图片文件路径
        :return: 是否存在于缓存
        """
        return path in self._cache


# 全局图片缓存实例
_image_cache = ImageCache(max_size=100)


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
        :param on_click: 点击事件回调
        :param border_radius: 圆角半径
        :param loading_size: loading 环尺寸
        :param loading_text: loading 文本
        :param loading_text_size: loading 文本大小
        
        注意：图片填充模式固定为 CONTAIN，以保持完整图片不裁剪
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
        self._loaded = False
    
    
    def _get_image_path(self) -> Optional[Path]:
        """获取当前图片的文件路径。
        
        :return: 图片文件路径，如果不存在则返回 None
        """
        if not self.model_meta.examples or self.index >= len(self.model_meta.examples):
            return None
        
        try:
            image_path = model_meta_service.get_example_image_path(self.model_meta, self.index)
            return image_path if image_path and image_path.exists() else None
        except (IndexError, AttributeError, TypeError):
            return None
    
    async def load(self):
        """异步加载图片。
        
        加载完成后自动更新显示。
        如果已加载过，则跳过。
        优先使用缓存，缓存未命中时才加载文件。
        """
        if self._loaded:
            return
        
        try:
            # 获取图片路径
            image_path = self._get_image_path()
            
            if not image_path:
                # 没有图片
                self.content = ft.Text(
                    "无图片",
                    size=10,
                    color=ft.Colors.RED_400
                )
                self.bgcolor = ft.Colors.GREY_800
                if self.page:
                    self.page.update()
                return
            
            # 先检查缓存（同步，快速）
            b64 = _image_cache.get_cached(image_path)
            
            if b64 is None:
                # 缓存未命中，异步读取文件
                try:
                    b64 = await asyncio.to_thread(lambda: _image_cache[image_path])
                except (FileNotFoundError, IOError, OSError):
                    # 加载失败
                    self.content = ft.Text(
                        "加载失败",
                        size=10,
                        color=ft.Colors.RED_400
                    )
                    self.bgcolor = ft.Colors.GREY_800
                    if self.page:
                        self.page.update()
                    return
            
            # 使用缓存的或新加载的 base64 数据
            self.content = ft.Image(src_base64=b64, fit=ft.ImageFit.CONTAIN)
            self.bgcolor = None
            self.clip_behavior = ft.ClipBehavior.HARD_EDGE
            self._loaded = True
        
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

