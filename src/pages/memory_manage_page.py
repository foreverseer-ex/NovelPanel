"""
记忆管理页面。

用于查看、编辑、删除和新增记忆条目。
"""
import flet as ft
from loguru import logger
from flet_toast import flet_toast
from flet_toast.Types import Position

from services.db import MemoryService
from schemas.memory import MemoryEntry
from settings import app_settings


class MemoryManagePage(ft.Column):
    """记忆管理页面"""
    
    def __init__(self, page: ft.Page):
        """初始化记忆管理页面"""
        super().__init__()
        self.page = page
        self.expand = True
        self.spacing = 20
        self.scroll = ft.ScrollMode.AUTO
        
        # 当前会话 ID
        self.session_id: str | None = None
        
        # 记忆列表
        self.memories: list[MemoryEntry] = []
        
        # UI 组件
        self.memory_list_view: ft.ListView | None = None
        
        # 构建 UI
        self._build_ui()
    
    def did_mount(self):
        """组件挂载后加载数据"""
        self.session_id = app_settings.ui.current_session_id
        if self.session_id:
            self._load_memories()
        else:
            self._show_empty_state()
    
    def _build_ui(self):
        """构建 UI 结构"""
        # 标题栏
        header = ft.Container(
            content=ft.Row(
                [
                    ft.Icon(ft.Icons.MEMORY, size=28),
                    ft.Text("记忆管理", size=24, weight=ft.FontWeight.BOLD),
                    ft.Container(expand=True),
                    ft.ElevatedButton(
                        text="新增记忆",
                        icon=ft.Icons.ADD,
                        on_click=self._on_create_memory,
                    ),
                ],
                spacing=10,
            ),
            padding=20,
        )
        
        # 记忆列表容器
        self.memory_list_view = ft.ListView(
            expand=True,
            spacing=10,
            padding=20,
        )
        
        self.controls = [
            header,
            ft.Divider(),
            self.memory_list_view,
        ]
    
    def _load_memories(self):
        """加载记忆列表"""
        if not self.session_id:
            return
        
        try:
            self.memories = MemoryService.list_entries_by_session(self.session_id)
            logger.info(f"加载了 {len(self.memories)} 条记忆")
            
            # 更新列表视图
            if self.memory_list_view:
                self.memory_list_view.controls.clear()
                
                if len(self.memories) == 0:
                    self.memory_list_view.controls.append(
                        ft.Container(
                            content=ft.Text(
                                "暂无记忆条目",
                                size=16,
                                color=ft.Colors.GREY_600,
                                text_align=ft.TextAlign.CENTER,
                            ),
                            alignment=ft.alignment.center,
                            padding=40,
                        )
                    )
                else:
                    for memory in self.memories:
                        self.memory_list_view.controls.append(
                            self._build_memory_card(memory)
                        )
                
                # 检查组件是否还在页面上
                if self.page:
                    self.update()
        
        except Exception as e:
            logger.exception(f"加载记忆失败: {e}")
            self._show_toast(f"加载记忆失败: {e}", ft.Colors.RED_700)
    
    def _build_memory_card(self, memory: MemoryEntry) -> ft.Card:
        """构建记忆卡片"""
        # 构建卡片内容列表
        card_contents = [
            ft.Row(
                [
                    ft.Text(
                        memory.key,
                        size=16,
                        weight=ft.FontWeight.BOLD,
                        selectable=True,  # 可选择和复制
                    ),
                    ft.Container(expand=True),
                    ft.IconButton(
                        icon=ft.Icons.EDIT,
                        tooltip="编辑",
                        on_click=lambda e, m=memory: self._on_edit_memory(m),
                    ),
                    ft.IconButton(
                        icon=ft.Icons.DELETE,
                        tooltip="删除",
                        icon_color=ft.Colors.RED_400,
                        on_click=lambda e, m=memory: self._on_delete_memory(m),
                    ),
                ],
            ),
            ft.Divider(),
            ft.Text(
                memory.value,
                size=14,
                max_lines=3,
                overflow=ft.TextOverflow.ELLIPSIS,
                selectable=True,  # 可选择和复制
            ),
        ]
        
        # 如果有说明，显示说明
        if memory.description:
            card_contents.append(
                ft.Text(
                    f"说明: {memory.description}",
                    size=12,
                    color=ft.Colors.GREY_500,
                    italic=True,
                    selectable=True,  # 可选择和复制
                )
            )
        
        card_contents.extend([
            ft.Container(height=5),
            ft.Text(
                f"创建时间: {memory.created_at.strftime('%Y-%m-%d %H:%M:%S')}",
                size=12,
                color=ft.Colors.GREY_600,
                selectable=True,  # 可选择和复制
            ),
        ])
        
        return ft.Card(
            content=ft.Container(
                content=ft.Column(card_contents),
                padding=15,
            ),
            elevation=1,
        )
    
    def _show_empty_state(self):
        """显示空状态"""
        if self.memory_list_view:
            self.memory_list_view.controls.clear()
            self.memory_list_view.controls.append(
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
    
    def _on_create_memory(self, e):
        """创建记忆"""
        logger.info("点击创建记忆按钮")
        
        if not self.session_id:
            self._show_toast("请先选择一个会话", ft.Colors.RED_700)
            return
        
        dialog = CreateMemoryDialog(
            session_id=self.session_id,
            on_success=self._on_memory_created,
            on_error=lambda msg: self._show_toast(msg, ft.Colors.RED_700),
        )
        self.page.open(dialog)
    
    def _on_memory_created(self, key: str):
        """记忆创建成功的回调"""
        self._show_toast(f"创建记忆成功: {key}", ft.Colors.GREEN_700)
        self._load_memories()
    
    def _on_edit_memory(self, memory: MemoryEntry):
        """编辑记忆"""
        logger.info(f"点击编辑记忆: {memory.memory_id}")
        
        if not self.session_id:
            return
        
        dialog = EditMemoryDialog(
            memory=memory,
            on_success=self._on_memory_updated,
            on_error=lambda msg: self._show_toast(msg, ft.Colors.RED_700),
        )
        self.page.open(dialog)
    
    def _on_memory_updated(self, key: str):
        """记忆更新成功的回调"""
        self._show_toast(f"更新记忆成功: {key}", ft.Colors.GREEN_700)
        self._load_memories()
    
    def _on_delete_memory(self, memory: MemoryEntry):
        """删除记忆"""
        logger.info(f"点击删除记忆: {memory.memory_id}")
        
        if not self.session_id:
            return
        
        dialog = DeleteMemoryConfirmDialog(
            memory=memory,
            on_success=self._on_memory_deleted,
            on_error=lambda msg: self._show_toast(msg, ft.Colors.RED_700),
        )
        self.page.open(dialog)
    
    def _on_memory_deleted(self):
        """记忆删除成功的回调"""
        self._show_toast("删除记忆成功", ft.Colors.GREEN_700)
        self._load_memories()
    
    def _show_toast(self, message: str, bgcolor: str):
        """显示 Toast 提示"""
        # 检查页面是否存在
        if not self.page:
            logger.debug(f"页面未挂载，跳过 Toast: {message}")
            return
        
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
            else:
                flet_toast.sucess(
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

class CreateMemoryDialog(ft.AlertDialog):
    """创建记忆对话框"""
    
    def __init__(self, session_id: str, on_success: callable, on_error: callable):
        """
        初始化创建记忆对话框
        
        Args:
            session_id: 会话ID
            on_success: 成功回调函数，接收参数 (key: str)
            on_error: 错误回调函数，接收参数 (message: str)
        """
        self.session_id = session_id
        self.on_success = on_success
        self.on_error = on_error
        
        # 创建输入字段
        self.key_field = ft.TextField(
            label="记忆键名",
            hint_text="例如：作品类型、主题、背景设定等",
            autofocus=True,
        )
        
        self.value_field = ft.TextField(
            label="记忆内容",
            hint_text="输入记忆的具体内容",
            multiline=True,
            min_lines=3,
            max_lines=5,
        )
        
        self.description_field = ft.TextField(
            label="说明（可选）",
            hint_text="对这条记忆的补充说明",
        )
        
        super().__init__(
            modal=True,
            title=ft.Text("新增记忆", weight=ft.FontWeight.BOLD),
            content=ft.Container(
                content=ft.Column(
                    [
                        self.key_field,
                        self.value_field,
                        self.description_field,
                    ],
                    tight=True,
                    spacing=10,
                ),
                width=500,
            ),
            actions=[
                ft.TextButton("取消", on_click=self._on_cancel),
                ft.ElevatedButton(
                    "创建",
                    on_click=self._on_confirm,
                    color=ft.Colors.WHITE,
                    bgcolor=ft.Colors.BLUE_700,
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
    
    def _on_confirm(self, e):
        """确认创建"""
        key = self.key_field.value
        value = self.value_field.value
        
        if not key or not key.strip():
            if self.on_error:
                self.on_error("键名不能为空")
            return
        
        if not value or not value.strip():
            if self.on_error:
                self.on_error("内容不能为空")
            return
        
        try:
            import uuid
            
            # 创建记忆条目
            memory = MemoryEntry(
                memory_id=str(uuid.uuid4()),
                session_id=self.session_id,
                key=key.strip(),
                value=value.strip(),
                description=self.description_field.value.strip() if self.description_field.value else None,
            )
            
            MemoryService.create_entry(memory)
            logger.success(f"创建记忆成功: {key}")
            
            # 关闭对话框
            self.open = False
            self.update()
            
            # 调用成功回调
            if self.on_success:
                self.on_success(key.strip())
                
        except Exception as ex:
            logger.exception(f"创建记忆失败: {ex}")
            
            # 关闭对话框
            self.open = False
            self.update()
            
            # 调用错误回调
            if self.on_error:
                self.on_error(f"创建记忆失败: {ex}")
    
    def _on_cancel(self, e):
        """取消创建"""
        self.open = False
        self.update()


class EditMemoryDialog(ft.AlertDialog):
    """编辑记忆对话框"""
    
    def __init__(self, memory: MemoryEntry, on_success: callable, on_error: callable):
        """
        初始化编辑记忆对话框
        
        Args:
            memory: 要编辑的记忆条目
            on_success: 成功回调函数，接收参数 (key: str)
            on_error: 错误回调函数，接收参数 (message: str)
        """
        self.memory = memory
        self.on_success = on_success
        self.on_error = on_error
        
        # 创建输入字段，预填充当前值
        self.key_field = ft.TextField(
            label="记忆键名",
            value=memory.key,
            autofocus=True,
        )
        
        self.value_field = ft.TextField(
            label="记忆内容",
            value=memory.value,
            multiline=True,
            min_lines=3,
            max_lines=5,
        )
        
        self.description_field = ft.TextField(
            label="说明（可选）",
            value=memory.description or "",
        )
        
        super().__init__(
            modal=True,
            title=ft.Text("编辑记忆", weight=ft.FontWeight.BOLD),
            content=ft.Container(
                content=ft.Column(
                    [
                        self.key_field,
                        self.value_field,
                        self.description_field,
                    ],
                    tight=True,
                    spacing=10,
                ),
                width=500,
            ),
            actions=[
                ft.TextButton("取消", on_click=self._on_cancel),
                ft.ElevatedButton(
                    "保存",
                    on_click=self._on_confirm,
                    color=ft.Colors.WHITE,
                    bgcolor=ft.Colors.BLUE_700,
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
    
    def _on_confirm(self, e):
        """确认保存"""
        key = self.key_field.value
        value = self.value_field.value
        
        if not key or not key.strip():
            if self.on_error:
                self.on_error("键名不能为空")
            return
        
        if not value or not value.strip():
            if self.on_error:
                self.on_error("内容不能为空")
            return
        
        try:
            MemoryService.update_entry(
                self.memory.memory_id,
                key=key.strip(),
                value=value.strip(),
                description=self.description_field.value.strip() if self.description_field.value else None,
            )
            logger.success(f"更新记忆成功: {key}")
            
            # 关闭对话框
            self.open = False
            self.update()
            
            # 调用成功回调
            if self.on_success:
                self.on_success(key.strip())
                
        except Exception as ex:
            logger.exception(f"更新记忆失败: {ex}")
            
            # 关闭对话框
            self.open = False
            self.update()
            
            # 调用错误回调
            if self.on_error:
                self.on_error(f"更新记忆失败: {ex}")
    
    def _on_cancel(self, e):
        """取消编辑"""
        self.open = False
        self.update()


class DeleteMemoryConfirmDialog(ft.AlertDialog):
    """删除记忆确认对话框"""
    
    def __init__(self, memory: MemoryEntry, on_success: callable, on_error: callable):
        """
        初始化删除确认对话框
        
        Args:
            memory: 要删除的记忆条目
            on_success: 成功回调函数，无参数
            on_error: 错误回调函数，接收参数 (message: str)
        """
        self.memory = memory
        self.on_success = on_success
        self.on_error = on_error
        
        # 截取部分值进行显示
        value_preview = memory.value[:100]
        if len(memory.value) > 100:
            value_preview += "..."
        
        super().__init__(
            modal=True,
            title=ft.Text("确认删除", weight=ft.FontWeight.BOLD),
            content=ft.Text(f"确定要删除这条记忆吗？\n\n键: {memory.key}\n值: {value_preview}"),
            actions=[
                ft.TextButton("取消", on_click=self._on_cancel),
                ft.ElevatedButton(
                    "删除",
                    on_click=self._on_confirm,
                    color=ft.Colors.WHITE,
                    bgcolor=ft.Colors.RED_700,
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
    
    def _on_confirm(self, e):
        """确认删除"""
        try:
            MemoryService.delete_entry(self.memory.memory_id)
            logger.success(f"删除记忆成功: {self.memory.memory_id}")
            
            # 关闭对话框
            self.open = False
            self.update()
            
            # 调用成功回调
            if self.on_success:
                self.on_success()
                
        except Exception as ex:
            logger.exception(f"删除记忆失败: {ex}")
            
            # 关闭对话框
            self.open = False
            self.update()
            
            # 调用错误回调
            if self.on_error:
                self.on_error(f"删除记忆失败: {ex}")
    
    def _on_cancel(self, e):
        """取消删除"""
        self.open = False
        self.update()

