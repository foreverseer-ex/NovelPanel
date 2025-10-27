"""
模型详情对话框。

展示模型的详细元数据和大图预览。
"""
import base64
import io
import asyncio

import flet as ft
from schemas.model_meta import ModelMeta
from services.model_meta import model_meta_service


class ModelDetailDialog(ft.AlertDialog):
    """模型详情对话框类。"""
    
    def __init__(self, model_meta: ModelMeta):
        """初始化模型详情对话框。
        
        :param model_meta: 模型元数据对象
        """
        super().__init__()
        self.model_meta = model_meta
        
        # 配置对话框属性
        self.modal = True
        self.title = ft.Text("模型详情", size=20, weight=ft.FontWeight.BOLD)
        self.width = 500
        self.height = 600
        
        # 构建内容
        self.preview_image_control = self._build_preview_image()
        info_rows = self._build_info_rows()
        
        self.content = ft.Column(
            controls=[
                self.preview_image_control,
                ft.Divider(),
                ft.Column(controls=info_rows, tight=True, spacing=8, scroll=ft.ScrollMode.AUTO),
            ],
            tight=True,
            spacing=10,
        )
        
        # 构建底部按钮
        close_btn = ft.TextButton("关闭", on_click=self._close)
        self.actions = [close_btn]
    
    def _build_preview_image(self) -> ft.Container:
        """构建预览图容器（初始显示 loading）。
        
        :return: 包含 loading 或图片的容器
        """
        return ft.Container(
            width=450,
            height=300,
            bgcolor=ft.Colors.GREY_800,
            border_radius=8,
            alignment=ft.alignment.center,
            content=ft.ProgressRing(width=40, height=40, stroke_width=3),
        )
    
    def _build_info_rows(self) -> list[ft.Row]:
        """构建信息行列表。
        
        :return: 包含标签-值对的 Row 控件列表
        """
        meta = self.model_meta
        
        def _make_row(label: str, value: str) -> ft.Row:
            """创建一行标签-值对。
            
            :param label: 标签文本
            :param value: 值文本
            :return: Row 控件
            """
            return ft.Row(
                controls=[
                    ft.Text(f"{label}:", weight=ft.FontWeight.BOLD, width=100),
                    ft.Text(value, selectable=True, expand=True),
                ],
                spacing=10,
            )
        
        rows = [
            _make_row("版本名称", meta.version_name),
            _make_row("模型类型", meta.model_type),
            _make_row("基础模型", meta.base_model),
        ]
        
        if meta.trained_words:
            rows.append(_make_row("触发词", ", ".join(meta.trained_words)))
        
        return rows
    
    def _pil_to_base64(self, img) -> str:
        """将 PIL Image 编码为 base64 PNG 字符串。
        
        :param img: PIL Image 对象
        :return: base64 编码的字符串
        """
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return base64.b64encode(buf.getvalue()).decode("utf-8")
    
    async def load_preview_image(self):
        """异步加载预览图。"""
        try:
            img = await asyncio.to_thread(
                model_meta_service.load_example_image, 
                self.model_meta
            )
            if img:
                b64 = await asyncio.to_thread(self._pil_to_base64, img)
                self.preview_image_control.content = ft.Image(
                    src_base64=b64, 
                    fit=ft.ImageFit.CONTAIN
                )
            else:
                self.preview_image_control.content = ft.Text(
                    "无预览图", 
                    color=ft.Colors.WHITE70
                )
        except (FileNotFoundError, IOError):
            self.preview_image_control.content = ft.Text(
                "预览图加载失败", 
                color=ft.Colors.RED_500
            )
        except Exception as e:
            self.preview_image_control.content = ft.Text(
                f"加载错误: {e}", 
                color=ft.Colors.RED_500
            )
        
        # 更新页面显示
        if self.page:
            self.page.update()
    
    def _close(self, e: ft.ControlEvent):
        """关闭对话框。
        
        :param e: 控件事件对象
        """
        if e.page:
            e.page.close(self)
