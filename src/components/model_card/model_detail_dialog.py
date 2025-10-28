"""
模型详情对话框。

展示模型的详细元数据和大图预览。
"""
import flet as ft
from schemas.model_meta import ModelMeta
from components.async_image import AsyncImage
from components.editable_text import EditableText
from services.model_meta import model_meta_service
from constants.ui_size import (
    DIALOG_STANDARD_WIDTH, DIALOG_STANDARD_HEIGHT,
    LARGE_IMAGE_WIDTH, LARGE_IMAGE_HEIGHT,
    LOADING_SIZE_LARGE, DETAIL_LABEL_WIDTH,
    SPACING_SMALL,
)


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
        self.width = DIALOG_STANDARD_WIDTH
        self.height = DIALOG_STANDARD_HEIGHT
        
        # 构建内容
        self.preview_image_control = AsyncImage(
            model_meta=model_meta,
            index=0,
            width=LARGE_IMAGE_WIDTH,
            height=LARGE_IMAGE_HEIGHT,
            fit=ft.ImageFit.CONTAIN,
            border_radius=8,
            loading_size=LOADING_SIZE_LARGE,
            loading_text="",
        )
        info_rows = self._build_info_rows()
        
        self.content = ft.Column(
            controls=[
                self.preview_image_control,
                ft.Divider(),
                ft.Column(controls=info_rows, tight=True, spacing=SPACING_SMALL, scroll=ft.ScrollMode.AUTO),
            ],
            tight=True,
            spacing=SPACING_SMALL,
        )
        
        # 构建底部按钮
        close_btn = ft.TextButton("关闭", on_click=self._close)
        self.actions = [close_btn]
    
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
                    ft.Text(f"{label}:", weight=ft.FontWeight.BOLD, width=DETAIL_LABEL_WIDTH),
                    ft.Text(value, selectable=True, expand=True),
                ],
                spacing=10,
            )
        
        def _make_editable_row(label: str, editable_control: ft.Control) -> ft.Row:
            """创建一行带可编辑控件的行。
            
            :param label: 标签文本
            :param editable_control: 可编辑控件
            :return: Row 控件
            """
            return ft.Row(
                controls=[
                    ft.Container(
                        content=ft.Text(f"{label}:", weight=ft.FontWeight.BOLD),
                        width=DETAIL_LABEL_WIDTH,
                        alignment=ft.alignment.top_left,
                    ),
                    editable_control,
                ],
                spacing=10,
                alignment=ft.MainAxisAlignment.START,
                vertical_alignment=ft.CrossAxisAlignment.START,
            )
        
        # 基础信息行
        rows = [
            _make_row("版本名称", meta.version_name),
            _make_row("模型类型", meta.type),
            _make_row("基础模型", meta.base_model),
        ]
        
        # 触发词
        if meta.trained_words:
            rows.append(_make_row("触发词", ", ".join(meta.trained_words)))
        
        # 可编辑的说明字段
        desc_editable = EditableText(
            value=meta.desc,
            placeholder="点击添加说明...",
            on_submit=lambda new_desc: self._handle_desc_update(new_desc),
            multiline=False,  # 单行输入，回车提交
        )
        rows.append(_make_editable_row("说明", desc_editable))
        
        return rows
    
    def _handle_desc_update(self, new_desc: str):
        """处理描述更新。
        
        :param new_desc: 新的描述内容
        """
        # 调用服务更新描述
        model_meta_service.update_desc(self.model_meta, new_desc)
        
        # 显示提示（可选）
        if self.page:
            snack_bar = ft.SnackBar(
                content=ft.Text("说明已保存"),
                duration=2000,
            )
            self.page.snack_bar = snack_bar
            snack_bar.open = True
            self.page.update()
    
    def _close(self, e: ft.ControlEvent):
        """关闭对话框。
        
        :param e: 控件事件对象
        """
        if e.page:
            e.page.close(self)
