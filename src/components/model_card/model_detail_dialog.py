"""
模型详情对话框。

展示模型的详细元数据和大图预览。
"""
import flet as ft
from flet_toast import flet_toast
from flet_toast.Types import Position
from schemas.model_meta import ModelMeta
from components.async_media import AsyncMedia
from components.editable_text import EditableText
from services.model_meta import local_model_meta_service
from constants.ui_size import (
    DIALOG_STANDARD_WIDTH, DIALOG_STANDARD_HEIGHT,
    LARGE_IMAGE_WIDTH, LARGE_IMAGE_HEIGHT,
    LOADING_SIZE_LARGE, DETAIL_LABEL_WIDTH,
    SPACING_SMALL, DETAIL_INFO_MIN_WIDTH,
)


class ModelDetailDialog(ft.AlertDialog):
    """模型详情对话框类。"""
    
    def __init__(self, model_meta: ModelMeta, all_models: list[ModelMeta] = None, current_index: int = 0):
        """初始化模型详情对话框。
        
        :param model_meta: 模型元数据对象
        :param all_models: 所有模型列表（用于切换导航）
        :param current_index: 当前模型在列表中的索引
        """
        super().__init__()
        self.model_meta = model_meta
        self.all_models = all_models or [model_meta]
        self.current_index = current_index
        
        # 配置对话框属性
        self.modal = True
        self.width = DIALOG_STANDARD_WIDTH
        self.height = DIALOG_STANDARD_HEIGHT
        
        # 构建标题栏：标题 + 右侧关闭按钮
        self.title_text = ft.Text("模型详情", size=18, weight=ft.FontWeight.BOLD)
        self.close_button = ft.IconButton(
            icon=ft.Icons.CLOSE,
            on_click=self._close,
            tooltip="关闭",
        )
        
        self.title = ft.Row(
            controls=[
                ft.Container(content=self.title_text, expand=True),
                self.close_button,
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )
        
        # 构建导航按钮（大尺寸圆角矩形，高度增加）
        self.prev_button = ft.ElevatedButton(
            content=ft.Icon(ft.Icons.CHEVRON_LEFT, size=40),
            on_click=self._go_previous,
            tooltip="上一个模型",
            disabled=self.current_index == 0,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=10),
                padding=ft.padding.symmetric(horizontal=15, vertical=80),
            ),
            width=70,
        )
        
        self.next_button = ft.ElevatedButton(
            content=ft.Icon(ft.Icons.CHEVRON_RIGHT, size=40),
            on_click=self._go_next,
            tooltip="下一个模型",
            disabled=self.current_index >= len(self.all_models) - 1,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=10),
                padding=ft.padding.symmetric(horizontal=15, vertical=80),
            ),
            width=70,
        )
        
        # 构建图片预览
        self.preview_image_control = AsyncMedia(
            model_meta=model_meta,
            index=0,
            width=LARGE_IMAGE_WIDTH,
            height=LARGE_IMAGE_HEIGHT,
            border_radius=8,
            loading_size=LOADING_SIZE_LARGE,
            loading_text="",
        )
        
        # 图片区域：左按钮 + 图片 + 右按钮
        self.image_row = ft.Row(
            controls=[
                self.prev_button,
                ft.Container(
                    content=self.preview_image_control,
                    expand=True,
                ),
                self.next_button,
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10,
        )
        
        info_rows = self._build_info_rows()
        
        # 根据图片宽高比决定布局方式
        aspect_ratio = self._get_aspect_ratio()
        
        if aspect_ratio > 1.0:
            # 宽图：使用垂直布局（上图下详情）
            self.content = ft.Column(
                controls=[
                    self.image_row,
                    ft.Divider(),
                    ft.Column(controls=info_rows, tight=True, spacing=SPACING_SMALL),
                ],
                tight=True,
                spacing=SPACING_SMALL,
                scroll=ft.ScrollMode.AUTO,
            )
        else:
            image_with_left_nav = ft.Row(
                controls=[
                    self.prev_button,
                    ft.Container(
                        content=self.preview_image_control,
                        width=LARGE_IMAGE_WIDTH,
                    ),
                ],
                spacing=10,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            )

            def _make_item_vertical(label: str, value: str) -> ft.Container:
                def _copy_to_clipboard(_e):
                    if self.page:
                        self.page.set_clipboard(value)
                        display_value = value if len(value) <= 50 else f"{value[:47]}..."
                        flet_toast.sucess(
                            page=self.page,
                            message=f"✅ 已复制: {display_value}",
                            position=Position.TOP_RIGHT,
                            duration=2
                        )
                return ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Container(
                                content=ft.Text(f"{label}:", weight=ft.FontWeight.BOLD),
                                on_click=_copy_to_clipboard,
                                tooltip=f"点击复制 {label}",
                                padding=ft.padding.symmetric(horizontal=0, vertical=2),
                            ),
                            ft.Container(
                                content=ft.Text(value if len(value) <= 200 else value[:197] + "..."),
                                on_click=_copy_to_clipboard,
                                tooltip="点击复制（完整内容）" if len(value) > 50 else "点击复制",
                                padding=ft.padding.symmetric(horizontal=5, vertical=2),
                            ),
                        ],
                        tight=True,
                        spacing=2,
                    )
                )

            meta = self.model_meta
            vertical_items = [
                _make_item_vertical("版本名称", meta.version_name),
                _make_item_vertical("模型类型", meta.type),
                _make_item_vertical("生态系统", meta.ecosystem.upper()),
                _make_item_vertical("基础模型", meta.base_model if meta.base_model else "未知"),
                _make_item_vertical("AIR 标识符", meta.air),
            ]

            desc_editable = EditableText(
                value=meta.desc,
                placeholder="点击添加说明...",
                on_submit=lambda new_desc: self._handle_desc_update(new_desc),
                multiline=False,
            )
            vertical_items.append(
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Text("说明:", weight=ft.FontWeight.BOLD),
                            desc_editable,
                        ],
                        tight=True,
                        spacing=2,
                    )
                )
            )

            detail_container = ft.Container(
                content=ft.Column(
                    controls=vertical_items,
                    tight=True,
                    spacing=SPACING_SMALL,
                    scroll=ft.ScrollMode.AUTO,
                ),
                expand=True,
                padding=ft.padding.symmetric(horizontal=SPACING_SMALL),
                width=DETAIL_INFO_MIN_WIDTH,
            )

            self.content = ft.Row(
                controls=[
                    image_with_left_nav,
                    ft.VerticalDivider(width=1),
                    detail_container,
                    self.next_button,
                ],
                spacing=SPACING_SMALL,
                expand=True,
            )
        
        # 移除底部按钮（关闭按钮已在标题栏右上角）
        self.actions = []
    
    def _build_info_rows(self) -> list[ft.Row]:
        """构建信息行列表。
        
        :return: 包含标签-值对的 Row 控件列表
        """
        meta = self.model_meta
        
        def _make_row(label: str, value: str) -> ft.Row:
            """创建一行标签-值对（可点击复制）。
            
            :param label: 标签文本
            :param value: 值文本（原始完整值，用于复制）
            :return: Row 控件
            """
            def _copy_to_clipboard(_e):
                """复制值到剪贴板并显示提示"""
                if self.page:
                    self.page.set_clipboard(value)
                    # 如果值太长，只显示前 50 个字符
                    display_value = value if len(value) <= 50 else f"{value[:47]}..."
                    flet_toast.sucess(
                        page=self.page,
                        message=f"✅ 已复制: {display_value}",
                        position=Position.TOP_RIGHT,
                        duration=2
                    )
            
            # 显示值：如果超过 50 字符，显示为省略号（但复制时用完整值）
            display_value = value if len(value) <= 50 else f"{value[:47]}..."
            
            # 标签和值都可以点击复制（使用 Container 包裹以实现点击效果）
            label_control = ft.Container(
                content=ft.Text(f"{label}:", weight=ft.FontWeight.BOLD),
                on_click=_copy_to_clipboard,
                tooltip=f"点击复制 {label}",
                width=DETAIL_LABEL_WIDTH,
                padding=ft.padding.symmetric(horizontal=0, vertical=2),
            )
            
            value_control = ft.Container(
                content=ft.Text(display_value),  # 使用截断后的显示值
                on_click=_copy_to_clipboard,
                tooltip="点击复制（完整内容）" if len(value) > 50 else "点击复制",
                expand=True,
                padding=ft.padding.symmetric(horizontal=5, vertical=2),
            )
            
            return ft.Row(
                controls=[label_control, value_control],
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
                    ft.Text(f"{label}:", weight=ft.FontWeight.BOLD, width=DETAIL_LABEL_WIDTH),
                    editable_control,
                ],
                spacing=10,
                alignment=ft.MainAxisAlignment.START,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,  # 垂直居中对齐
            )
        
        # 基础信息行
        rows = [
            _make_row("版本名称", meta.version_name),
            _make_row("模型类型", meta.type),
            _make_row("生态系统", meta.ecosystem.upper()),  # SD1, SD2, SDXL
            _make_row("基础模型", meta.base_model if meta.base_model else "未知"),
            _make_row("AIR 标识符", meta.air),  # ✨ 新增 AIR 行
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
    
    def _get_aspect_ratio(self) -> float:
        """获取当前模型示例图片的宽高比。
        
        :return: 宽高比（width / height），如果无法获取则返回 1.5（默认宽图）
        """
        if self.model_meta.examples:
            # 获取第一个示例的尺寸
            first_example = self.model_meta.examples[0]
            width = first_example.args.width
            height = first_example.args.height
            if height > 0:
                return width / height
        
        # 默认返回 1.5（宽图）
        return 1.5
    
    def _handle_desc_update(self, new_desc: str):
        """处理描述更新。
        
        :param new_desc: 新的描述内容
        """
        import asyncio
        
        # 更新描述并保存
        self.model_meta.desc = new_desc if new_desc else None
        asyncio.run(local_model_meta_service.save(self.model_meta))
        
        # 显示提示（可选）
        if self.page:
            flet_toast.sucess(
                page=self.page,
                message="说明已保存",
                position=Position.TOP_RIGHT,
                duration=2
            )
    
    def _go_previous(self, e: ft.ControlEvent):
        """切换到上一个模型。
        
        :param e: 控件事件对象
        """
        if self.current_index > 0:
            self.current_index -= 1
            self._update_content()
    
    def _go_next(self, e: ft.ControlEvent):
        """切换到下一个模型。
        
        :param e: 控件事件对象
        """
        if self.current_index < len(self.all_models) - 1:
            self.current_index += 1
            self._update_content()
    
    def _update_content(self):
        """更新对话框内容以显示当前索引的模型。"""
        # 更新当前模型
        self.model_meta = self.all_models[self.current_index]
        
        # 更新导航按钮状态
        self.prev_button.disabled = self.current_index == 0
        self.next_button.disabled = self.current_index >= len(self.all_models) - 1
        
        # 重新创建图片控件（修复图片不更新的问题）
        self.preview_image_control = AsyncMedia(
            model_meta=self.model_meta,
            index=0,
            width=LARGE_IMAGE_WIDTH,
            height=LARGE_IMAGE_HEIGHT,
            border_radius=8,
            loading_size=LOADING_SIZE_LARGE,
            loading_text="",
        )
        
        # 更新图片行
        self.image_row.controls[1] = ft.Container(
            content=self.preview_image_control,
            expand=True,
        )
        
        # 重新构建信息行
        info_rows = self._build_info_rows()
        
        # 根据图片宽高比决定布局方式
        aspect_ratio = self._get_aspect_ratio()
        
        if aspect_ratio > 1.0:
            # 宽图：使用垂直布局（上图下详情）
            self.content = ft.Column(
                controls=[
                    self.image_row,
                    ft.Divider(),
                    ft.Column(controls=info_rows, tight=True, spacing=SPACING_SMALL),
                ],
                tight=True,
                spacing=SPACING_SMALL,
                scroll=ft.ScrollMode.AUTO,
            )
        else:
            image_with_left_nav = ft.Row(
                controls=[
                    self.prev_button,
                    ft.Container(
                        content=self.preview_image_control,
                        width=LARGE_IMAGE_WIDTH,
                    ),
                ],
                spacing=10,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            )

            def _make_item_vertical(label: str, value: str) -> ft.Container:
                def _copy_to_clipboard(_e):
                    if self.page:
                        self.page.set_clipboard(value)
                        display_value = value if len(value) <= 50 else f"{value[:47]}..."
                        flet_toast.sucess(
                            page=self.page,
                            message=f"✅ 已复制: {display_value}",
                            position=Position.TOP_RIGHT,
                            duration=2
                        )
                return ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Container(
                                content=ft.Text(f"{label}:", weight=ft.FontWeight.BOLD),
                                on_click=_copy_to_clipboard,
                                tooltip=f"点击复制 {label}",
                                padding=ft.padding.symmetric(horizontal=0, vertical=2),
                            ),
                            ft.Container(
                                content=ft.Text(value if len(value) <= 200 else value[:197] + "..."),
                                on_click=_copy_to_clipboard,
                                tooltip="点击复制（完整内容）" if len(value) > 50 else "点击复制",
                                padding=ft.padding.symmetric(horizontal=5, vertical=2),
                            ),
                        ],
                        tight=True,
                        spacing=2,
                    )
                )

            meta = self.model_meta
            vertical_items = [
                _make_item_vertical("版本名称", meta.version_name),
                _make_item_vertical("模型类型", meta.type),
                _make_item_vertical("生态系统", meta.ecosystem.upper()),
                _make_item_vertical("基础模型", meta.base_model if meta.base_model else "未知"),
                _make_item_vertical("AIR 标识符", meta.air),
            ]

            desc_editable = EditableText(
                value=meta.desc,
                placeholder="点击添加说明...",
                on_submit=lambda new_desc: self._handle_desc_update(new_desc),
                multiline=False,
            )
            vertical_items.append(
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Text("说明:", weight=ft.FontWeight.BOLD),
                            desc_editable,
                        ],
                        tight=True,
                        spacing=2,
                    )
                )
            )

            detail_container = ft.Container(
                content=ft.Column(
                    controls=vertical_items,
                    tight=True,
                    spacing=SPACING_SMALL,
                    scroll=ft.ScrollMode.AUTO,
                ),
                expand=True,
                padding=ft.padding.symmetric(horizontal=SPACING_SMALL),
            )

            self.content = ft.Row(
                controls=[
                    image_with_left_nav,
                    ft.VerticalDivider(width=1),
                    detail_container,
                    self.next_button,
                ],
                spacing=SPACING_SMALL,
                expand=True,
            )
        
        # 更新界面
        if self.page:
            self.update()
    
    def _close(self, e: ft.ControlEvent = None):
        """关闭对话框。
        
        :param e: 控件事件对象（可选）
        """
        page = e.page if e else self.page
        if page:
            page.close(self)
