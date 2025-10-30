"""
对话框组件。

按照 Flet 官方推荐的方式实现对话框。
参考：https://flet.dev/docs/controls/alertdialog/
"""
import flet as ft
from pathlib import Path
from loguru import logger
import uuid
import time
from flet_toast import flet_toast
from flet_toast.Types import Position

from services.db import SessionService
from schemas.session import Session
from services.transform import transform_service
from settings import app_settings


class CreateSessionDialog(ft.AlertDialog):
    """
    创建会话对话框。
    
    用法：
        dialog = CreateSessionDialog(page, on_success=callback)
        page.open(dialog)
    """
    
    def __init__(self, page: ft.Page, on_success=None):
        """
        初始化创建会话对话框。
        
        :param page: Flet 页面对象
        :param on_success: 创建成功后的回调函数
        """
        self.page = page
        self.on_success = on_success
        self.uploaded_file_path = None
        
        # 表单字段
        self.title_field = ft.TextField(
            label="会话标题",
            hint_text="不填写将使用文件名",
            autofocus=True,
        )
        
        self.author_field = ft.TextField(
            label="作者",
            value=app_settings.ui.default_username,
            hint_text="小说作者",
        )
        
        self.file_info_text = ft.Text(
            "未选择文件",
            size=12,
            color=ft.Colors.ON_SURFACE_VARIANT,
        )
        
        # 文件选择器
        self.file_picker = ft.FilePicker(on_result=self._on_file_picked)
        page.overlay.append(self.file_picker)
        
        # 构建表单
        form = ft.Column(
            [
                self.title_field,
                self.author_field,
                ft.Container(height=10),
                ft.Row(
                    [
                        ft.ElevatedButton(
                            "选择文件",
                            icon=ft.Icons.UPLOAD_FILE,
                            on_click=lambda _: self.file_picker.pick_files(
                                allowed_extensions=["txt", "pdf", "doc", "docx"],
                                dialog_title="选择小说文件",
                            ),
                        ),
                        self.file_info_text,
                    ],
                    spacing=10,
                ),
                ft.Container(
                    content=ft.Text(
                        "支持格式: TXT, PDF, DOC, DOCX",
                        size=11,
                        color=ft.Colors.ON_SURFACE_VARIANT,
                        italic=True,
                    ),
                    padding=ft.padding.only(top=5),
                ),
            ],
            spacing=10,
            tight=True,
        )
        
        # 初始化对话框
        super().__init__(
            modal=True,
            title=ft.Text("创建会话", size=20, weight=ft.FontWeight.BOLD),
            content=ft.Container(
                content=form,
                width=500,
                padding=10,
            ),
            actions=[
                ft.TextButton("取消", on_click=self._on_cancel),
                ft.ElevatedButton("创建", on_click=self._on_create),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
            on_dismiss=self._on_dismiss,
        )
    
    def _on_file_picked(self, e: ft.FilePickerResultEvent):
        """文件选择回调"""
        if e.files and len(e.files) > 0:
            file = e.files[0]
            self.uploaded_file_path = file.path
            file_name = Path(file.path).name
            self.file_info_text.value = f"已选择: {file_name}"
            
            # 如果标题为空，使用文件名（去掉扩展名）
            if not self.title_field.value or not self.title_field.value.strip():
                self.title_field.value = Path(file.path).stem
                self.title_field.update()
            
            self.file_info_text.update()
            logger.info(f"选择文件: {self.uploaded_file_path}")
        else:
            self.uploaded_file_path = None
            self.file_info_text.value = "未选择文件"
            self.file_info_text.update()
    
    def _on_cancel(self, _e):
        """取消按钮点击"""
        logger.info("取消创建会话")
        self.open = False
        self.page.update()
        time.sleep(0.1)  # 添加小延迟以避免白屏问题，参考: https://github.com/flet-dev/flet/discussions/1942
    
    def _on_dismiss(self, _e):
        """对话框关闭时清理"""
        logger.info("创建会话对话框已关闭")
        # 清理文件选择器
        if self.file_picker in self.page.overlay:
            self.page.overlay.remove(self.file_picker)
    
    def _on_create(self, _e):
        """创建按钮点击"""
        title = self.title_field.value.strip() if self.title_field.value else ""
        author = self.author_field.value.strip() if self.author_field.value else ""
        
        # 验证
        if not title:
            self._show_toast("请输入会话标题或选择文件", ft.Colors.RED_700)
            return
        
        try:
            # 生成会话 ID 和项目路径
            session_id = str(uuid.uuid4())
            project_path = Path(f"storage/data/projects/{session_id}")
            
            # 处理文件上传（保存原始文件路径，不拷贝）
            novel_path = None
            if self.uploaded_file_path:
                source_file = Path(self.uploaded_file_path)
                
                # 检查文件格式
                if not transform_service.is_supported(source_file):
                    self._show_toast(
                        f"不支持的文件格式: {source_file.suffix}",
                        ft.Colors.RED_700
                    )
                    return
                
                # 直接使用原始文件路径（不拷贝文件）
                novel_path = str(source_file.absolute())
                logger.info(f"使用原始文件路径: {novel_path}")
            
            # 创建会话（后端会自动创建文件夹结构并将小说内容存入数据库）
            new_session = Session(
                session_id=session_id,
                title=title,
                project_path=str(project_path),
                novel_path=novel_path,
                author=author or None,
            )
            
            created = SessionService.create(new_session)
            logger.info(f"创建会话成功: {created.session_id}, 项目路径: {created.project_path}")
            
            # 关闭对话框
            self.open = False
            self.page.update()
            time.sleep(0.1)  # 添加小延迟以避免白屏问题
            
            # 调用成功回调
            if self.on_success:
                self.on_success(created)
            
            self._show_toast(f"创建会话成功: {title}", ft.Colors.GREEN_700)
            
        except Exception as ex:  # pylint: disable=broad-except
            logger.exception(f"创建会话失败: {ex}")
            self._show_toast(f"创建会话失败: {ex}", ft.Colors.RED_700)
    
    def _show_toast(self, message: str, bgcolor: str):
        """显示 Toast 提示"""
        try:
            duration_sec = 3  # 转换为秒
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
                # 默认为 success
                flet_toast.sucess(
                    page=self.page,
                    message=message,
                    position=Position.TOP_RIGHT,
                    duration=duration_sec
                )
        except Exception:  # pylint: disable=broad-except
            logger.exception("显示 Toast 失败")
            print(f"Toast: {message}")


class DeleteSessionDialog(ft.AlertDialog):
    """
    删除会话确认对话框。
    
    用法：
        dialog = DeleteSessionDialog(page, session, on_success=callback)
        page.open(dialog)
    """
    
    def __init__(self, page: ft.Page, session: Session, on_success=None):
        """
        初始化删除会话对话框。
        
        :param page: Flet 页面对象
        :param session: 要删除的会话对象
        :param on_success: 删除成功后的回调函数
        """
        self.page = page
        self.session = session
        self.on_success = on_success
        
        # 初始化对话框
        super().__init__(
            modal=True,
            title=ft.Text("确认删除", size=20, weight=ft.FontWeight.BOLD),
            content=ft.Text(
                f'确定要删除会话 "{session.title}" 吗？\n此操作不可恢复。',
                size=16,
            ),
            actions=[
                ft.TextButton("取消", on_click=self._on_cancel),
                ft.ElevatedButton(
                    "删除",
                    on_click=self._on_delete,
                    style=ft.ButtonStyle(
                        bgcolor=ft.Colors.RED_700,
                        color=ft.Colors.WHITE,
                    ),
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
    
    def _on_cancel(self, _e):
        """取消按钮点击"""
        logger.info("取消删除会话")
        self.open = False
        self.page.update()
        time.sleep(0.1)  # 添加小延迟以避免白屏问题
    
    def _on_delete(self, _e):
        """删除按钮点击"""
        try:
            success = SessionService.delete(self.session.session_id)
            if success:
                logger.info(f"删除会话: {self.session.session_id}")
                
                # 关闭对话框
                self.open = False
                self.page.update()
                time.sleep(0.1)  # 添加小延迟以避免白屏问题
                
                # 调用成功回调
                if self.on_success:
                    self.on_success()
                
                self._show_toast(
                    f"删除会话成功: {self.session.title}",
                    ft.Colors.GREEN_700
                )
            else:
                self.open = False
                self.page.update()
                time.sleep(0.1)  # 添加小延迟以避免白屏问题
                self._show_toast("删除会话失败", ft.Colors.RED_700)
                    
        except Exception as ex:  # pylint: disable=broad-except
            logger.exception(f"删除会话失败: {ex}")
            self.open = False
            self.page.update()
            time.sleep(0.1)  # 添加小延迟以避免白屏问题
            self._show_toast(f"删除会话失败: {ex}", ft.Colors.RED_700)
    
    def _show_toast(self, message: str, bgcolor: str):
        """显示 Toast 提示"""
        try:
            duration_sec = 3  # 转换为秒
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
                # 默认为 success
                flet_toast.sucess(
                    page=self.page,
                    message=message,
                    position=Position.TOP_RIGHT,
                    duration=duration_sec
                )
        except Exception:  # pylint: disable=broad-except
            logger.exception("显示 Toast 失败")
            print(f"Toast: {message}")

