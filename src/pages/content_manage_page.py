"""
内容管理页面。

用于查看和编辑当前会话的小说文本内容。
"""
import flet as ft
from loguru import logger
from flet_toast import flet_toast
from flet_toast.Types import Position

from components import EditableCard
from services.db import NovelContentService
from schemas.novel import NovelContent
from settings import app_settings


class ContentManagePage(ft.Column):
    """内容管理页面"""
    
    def __init__(self, page: ft.Page):
        """初始化内容管理页面"""
        super().__init__()
        self.page = page
        self.expand = True
        self.spacing = 20
        self.scroll = ft.ScrollMode.AUTO
        
        # 当前会话 ID
        self.session_id: str | None = None
        
        # 内容列表
        self.contents: list[NovelContent] = []
        
        # UI 组件
        self.content_list_view: ft.ListView | None = None
        
        # 构建 UI
        self._build_ui()
    
    def did_mount(self):
        """组件挂载后加载数据"""
        self.session_id = app_settings.ui.current_session_id
        if self.session_id:
            self._load_contents()
        else:
            self._show_empty_state()
    
    def _build_ui(self):
        """构建 UI 结构"""
        # 标题栏
        header = ft.Container(
            content=ft.Row(
                [
                    ft.Icon(ft.Icons.EDIT_NOTE, size=28),
                    ft.Text("内容管理", size=24, weight=ft.FontWeight.BOLD),
                    ft.Container(expand=True),
                    ft.ElevatedButton(
                        text="新增段落",
                        icon=ft.Icons.ADD,
                        on_click=self._on_create_content,
                    ),
                ],
                spacing=10,
            ),
            padding=20,
        )
        
        # 内容列表容器
        self.content_list_view = ft.ListView(
            expand=True,
            spacing=10,
            padding=20,
        )
        
        self.controls = [
            header,
            ft.Divider(),
            self.content_list_view,
        ]
    
    def _load_contents(self):
        """加载内容列表"""
        if not self.session_id:
            return
        
        try:
            # 获取前 100 行（分页加载可以后续优化）
            self.contents = NovelContentService.get_by_session(self.session_id)
            logger.info(f"加载了 {len(self.contents)} 行内容")
            
            # 更新列表视图
            if self.content_list_view:
                self.content_list_view.controls.clear()
                
                if len(self.contents) == 0:
                    self.content_list_view.controls.append(
                        ft.Container(
                            content=ft.Text(
                                "暂无内容",
                                size=16,
                                color=ft.Colors.GREY_600,
                                text_align=ft.TextAlign.CENTER,
                            ),
                            alignment=ft.alignment.center,
                            padding=40,
                        )
                    )
                else:
                    for content in self.contents[:100]:  # 限制显示前100行
                        self.content_list_view.controls.append(
                            self._build_content_card(content)
                        )
                    
                    if len(self.contents) > 100:
                        self.content_list_view.controls.append(
                            ft.Container(
                                content=ft.Text(
                                    f"...还有 {len(self.contents) - 100} 行内容（仅显示前100行）",
                                    size=14,
                                    color=ft.Colors.GREY_600,
                                    text_align=ft.TextAlign.CENTER,
                                ),
                                padding=20,
                            )
                        )
                
                self.update()
        
        except Exception as e:
            logger.exception(f"加载内容失败: {e}")
            self._show_toast(f"加载内容失败: {e}", ft.Colors.RED_700)
    
    def _build_content_card(self, content: NovelContent) -> ft.Row:
        """
        构建内容卡片。
        
        使用 EditableCard 组件实现内联编辑，删除按钮在右侧。
        """
        # 创建可编辑卡片
        card = EditableCard(
            content=content.content,
            on_save=lambda new_text, c=content: self._handle_card_save(c, new_text),
            min_lines=1,
            max_lines=20,
        )
        
        # 删除按钮
        delete_button = ft.IconButton(
            icon=ft.Icons.DELETE_OUTLINE,
            icon_color=ft.Colors.RED_400,
            tooltip="删除",
            on_click=lambda e, c=content: self._on_delete_content(c),
        )
        
        # 卡片 + 删除按钮的行布局
        return ft.Row(
            [
                ft.Container(content=card, expand=True),  # 卡片占据主要空间
                delete_button,  # 删除按钮在右侧
            ],
            spacing=10,
            vertical_alignment=ft.CrossAxisAlignment.START,
        )
    
    def _show_empty_state(self):
        """显示空状态"""
        if self.content_list_view:
            self.content_list_view.controls.clear()
            self.content_list_view.controls.append(
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Icon(ft.Icons.INFO_OUTLINE, size=64, color=ft.Colors.GREY_400),
                            ft.Text(
                                "请先选择一个会话",
                                size=18,
                                color=ft.Colors.GREY_600,
                            ),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=20,
                    ),
                    alignment=ft.alignment.center,
                    padding=40,
                )
            )
            self.update()
    
    def _on_create_content(self, e):
        """创建新段落"""
        logger.info("点击新增段落按钮")
        
        if not self.session_id:
            self._show_toast("请先选择一个会话", ft.Colors.RED_700)
            return
        
        # 打开编辑对话框（新增模式）
        self._open_edit_dialog(None)
    
    def _handle_card_save(self, content: NovelContent, new_text: str):
        """
        处理卡片保存。
        
        如果新文本包含多行，会自动分割成多个段落。
        
        Args:
            content: 原内容对象
            new_text: 新文本内容
        """
        if not new_text.strip():
            self._show_toast("内容不能为空", ft.Colors.RED_700)
            return
        
        try:
            # 检查是否包含换行符（需要分割）
            lines = new_text.split('\n')
            lines = [line.strip() for line in lines if line.strip()]
            
            if len(lines) == 1:
                # 单行，直接更新
                self._update_content(content, lines[0])
            else:
                # 多行，更新第一行并插入新行
                self._update_and_split_content(content, lines)
            
            # 刷新列表
            self._load_contents()
            
            self._show_toast("保存成功", ft.Colors.GREEN_700)
            
        except Exception as ex:
            logger.exception(f"保存内容失败: {ex}")
            self._show_toast(f"保存失败: {ex}", ft.Colors.RED_700)
    
    def _on_edit_content(self, content: NovelContent):
        """编辑段落"""
        logger.info(f"点击编辑段落: 章节{content.chapter} 行{content.line}")
        
        # 打开编辑对话框（编辑模式）
        self._open_edit_dialog(content)
    
    def _open_edit_dialog(self, content: NovelContent | None):
        """打开编辑对话框"""
        is_new = content is None
        
        # 创建编辑对话框
        dialog = EditParagraphDialog(
            is_new=is_new,
            content=content,
            on_save=self._on_paragraph_saved,
            on_error=lambda msg: self._show_toast(msg, ft.Colors.RED_700),
        )
        
        # 打开对话框
        self.page.open(dialog)
    
    def _on_paragraph_saved(self, is_new: bool, content, lines: list[str]):
        """段落保存成功的回调"""
        try:
            if is_new:
                # 新增模式
                self._create_new_paragraphs(lines)
            else:
                # 编辑模式
                if len(lines) == 1:
                    # 单行，直接更新
                    self._update_content(content, lines[0])
                else:
                    # 多行，更新第一行并插入新行
                    self._update_and_split_content(content, lines)
            
            # 刷新列表
            self._load_contents()
            self._show_toast("保存成功", ft.Colors.GREEN_700)
            
        except Exception as ex:
            logger.exception(f"保存内容失败: {ex}")
            self._show_toast(f"保存失败: {ex}", ft.Colors.RED_700)
    
    def _create_new_paragraphs(self, lines: list[str]):
        """
        创建新段落。
        
        Args:
            lines: 段落文本列表
        """
        if not self.session_id or not lines:
            return
        
        # 获取当前最大行号
        max_line = 0
        max_chapter = 0
        if self.contents:
            for c in self.contents:
                if c.chapter > max_chapter:
                    max_chapter = c.chapter
                    max_line = c.line
                elif c.chapter == max_chapter and c.line > max_line:
                    max_line = c.line
        
        # 创建新内容
        new_contents = []
        for i, line_text in enumerate(lines):
            new_content = NovelContent(
                session_id=self.session_id,
                chapter=max_chapter,
                line=max_line + i + 1,
                content=line_text,
            )
            new_contents.append(new_content)
        
        # 批量保存
        NovelContentService.batch_create(new_contents)
        logger.info(f"创建了 {len(new_contents)} 个新段落")
    
    def _update_content(self, content: NovelContent, new_text: str):
        """
        更新单个段落。
        
        Args:
            content: 原内容对象
            new_text: 新文本
        """
        NovelContentService.update(
            session_id=content.session_id,
            chapter=content.chapter,
            line=content.line,
            new_content=new_text,
        )
        logger.info(f"更新段落: 章节{content.chapter} 行{content.line}")
    
    def _update_and_split_content(self, content: NovelContent, lines: list[str]):
        """
        更新段落并分割成多个段落。
        
        Args:
            content: 原内容对象
            lines: 新的段落列表
        """
        if not lines:
            return
        
        # 更新第一行
        self._update_content(content, lines[0])
        
        # 如果有多行，需要在后面插入新段落
        if len(lines) > 1:
            # 获取该章节所有内容，找到插入位置
            chapter_contents = NovelContentService.get_by_chapter(
                content.session_id,
                content.chapter
            )
            
            # 找到当前行在章节中的位置
            insert_after_line = content.line
            
            # 为后续行重新编号（向后移动）
            lines_to_update = []
            for c in chapter_contents:
                if c.line > insert_after_line:
                    lines_to_update.append(c)
            
            # 从后往前更新，避免行号冲突
            lines_to_update.sort(key=lambda x: x.line, reverse=True)
            shift = len(lines) - 1  # 需要移动的行数
            
            for c in lines_to_update:
                NovelContentService.update(
                    session_id=c.session_id,
                    chapter=c.chapter,
                    line=c.line,
                    new_content=c.content,
                )
                # 先删除旧的
                NovelContentService.delete_single(
                    session_id=c.session_id,
                    chapter=c.chapter,
                    line=c.line,
                )
                # 创建新的（新行号）
                NovelContentService.create(
                    NovelContent(
                        session_id=c.session_id,
                        chapter=c.chapter,
                        line=c.line + shift,
                        content=c.content,
                    )
                )
            
            # 插入新段落
            for i, line_text in enumerate(lines[1:], start=1):
                NovelContentService.create(
                    NovelContent(
                        session_id=content.session_id,
                        chapter=content.chapter,
                        line=insert_after_line + i,
                        content=line_text,
                    )
                )
            
            logger.info(f"分割段落: 原行{content.line}分割成{len(lines)}段")
    
    def _on_delete_content(self, content: NovelContent):
        """删除段落"""
        logger.info(f"点击删除段落: 章节{content.chapter} 行{content.line}")
        
        # 创建删除确认对话框
        dialog = DeleteParagraphConfirmDialog(
            content=content,
            on_confirm=self._on_paragraph_deleted,
        )
        
        # 打开对话框
        self.page.open(dialog)
    
    def _on_paragraph_deleted(self, content):
        """段落删除成功的回调"""
        try:
            # 删除段落
            from services.db import NovelContentService
            success = NovelContentService.delete_single(
                session_id=content.session_id,
                chapter=content.chapter,
                line=content.line,
            )
            
            if success:
                # 刷新列表
                self._load_contents()
                self._show_toast("删除成功", ft.Colors.GREEN_700)
            else:
                self._show_toast("删除失败：段落不存在", ft.Colors.RED_700)
        
        except Exception as ex:
            logger.exception(f"删除段落失败: {ex}")
            self._show_toast(f"删除失败: {ex}", ft.Colors.RED_700)
    
    def _show_toast(self, message: str, bgcolor: str):
        """显示 Toast 提示"""
        try:
            duration_sec = 3
            if bgcolor == ft.Colors.GREEN_700:
                flet_toast.sucess(
                    page=self.page,
                    message=message,
                    position=Position.TOP_RIGHT,
                    duration=duration_sec
                )
            elif bgcolor == ft.Colors.RED_700:
                flet_toast.error(
                    page=self.page,
                    message=message,
                    position=Position.TOP_RIGHT,
                    duration=duration_sec
                )
        except Exception:
            logger.exception("显示 Toast 失败")
            print(f"Toast: {message}")


# ============================================================================
# Dialog 类定义
# ============================================================================

class EditParagraphDialog(ft.AlertDialog):
    """编辑段落对话框"""
    
    def __init__(self, is_new: bool, content, on_save: callable, on_error: callable):
        """
        初始化编辑段落对话框
        
        Args:
            is_new: 是否为新增模式
            content: 要编辑的内容对象（新增时为 None）
            on_save: 保存回调函数，接收参数 (is_new: bool, content, lines: list[str])
            on_error: 错误回调函数，接收参数 (message: str)
        """
        self.is_new = is_new
        self.content = content
        self.on_save = on_save
        self.on_error = on_error
        
        # 创建输入框
        self.text_field = ft.TextField(
            label="段落内容",
            value="" if is_new else content.content,
            multiline=True,
            min_lines=3,
            max_lines=10,
            autofocus=True,
            hint_text="支持多行输入，每行将作为一个独立段落保存",
        )
        
        super().__init__(
            modal=True,
            title=ft.Text("新增段落" if is_new else "编辑段落"),
            content=ft.Container(
                content=self.text_field,
                width=500,
            ),
            actions=[
                ft.TextButton("取消", on_click=self._on_cancel),
                ft.ElevatedButton("保存", on_click=self._on_confirm),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
    
    def _on_confirm(self, e):
        """确认保存"""
        new_text = self.text_field.value.strip()
        
        if not new_text:
            if self.on_error:
                self.on_error("内容不能为空")
            return
        
        # 检查是否包含换行符（需要分割）
        lines = new_text.split('\n')
        lines = [line.strip() for line in lines if line.strip()]
        
        # 关闭对话框
        self.open = False
        self.update()
        
        # 调用保存回调
        if self.on_save:
            self.on_save(self.is_new, self.content, lines)
    
    def _on_cancel(self, e):
        """取消编辑"""
        self.open = False
        self.update()


class DeleteParagraphConfirmDialog(ft.AlertDialog):
    """删除段落确认对话框"""
    
    def __init__(self, content, on_confirm: callable):
        """
        初始化删除确认对话框
        
        Args:
            content: 要删除的内容对象
            on_confirm: 确认回调函数，接收参数 (content)
        """
        self.content = content
        self.on_confirm = on_confirm
        
        # 截取内容预览
        preview = content.content[:100]
        if len(content.content) > 100:
            preview += "..."
        
        super().__init__(
            modal=True,
            title=ft.Text("确认删除"),
            content=ft.Text(f"确定要删除这个段落吗？\n\n内容预览：\n{preview}"),
            actions=[
                ft.TextButton("取消", on_click=self._on_cancel),
                ft.ElevatedButton(
                    "删除",
                    on_click=self._on_confirm_click,
                    bgcolor=ft.Colors.RED_400,
                    color=ft.Colors.WHITE,
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
    
    def _on_confirm_click(self, e):
        """确认删除"""
        # 关闭对话框
        self.open = False
        self.update()
        
        # 调用确认回调
        if self.on_confirm:
            self.on_confirm(self.content)
    
    def _on_cancel(self, e):
        """取消删除"""
        self.open = False
        self.update()
