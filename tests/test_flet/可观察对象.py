"""
Flet 可观察对象测试示例。

演示如何使用 Flet 的 observable 装饰器和组件系统构建响应式用户界面。
"""
from dataclasses import dataclass, field

import flet as ft

@ft.observable
@dataclass
class User:
    """用户数据模型。
    
    使用 observable 装饰器使其可被 Flet 框架监听变化。
    """
    first_name: str
    last_name: str

    def update(self, first_name: str, last_name: str):
        """更新用户信息。
        
        :param first_name: 新的名字
        :param last_name: 新的姓氏
        """
        self.first_name = first_name
        self.last_name = last_name


@ft.observable
@dataclass
class App:
    """应用状态管理类。
    
    管理用户列表，提供添加和删除用户的功能。
    """
    users: list[User] = field(default_factory=list)

    def add_user(self, first_name: str, last_name: str):
        """添加新用户。
        
        :param first_name: 用户名字
        :param last_name: 用户姓氏
        """
        if first_name.strip() or last_name.strip():
            self.users.append(User(first_name, last_name))

    def delete_user(self, user: User):
        """删除指定用户。
        
        :param user: 要删除的用户对象
        """
        self.users.remove(user)


@ft.component
def UserView(user: User, delete_user) -> ft.Control:
    """用户视图组件。
    
    显示单个用户的信息，支持编辑和删除操作。
    
    :param user: 用户对象
    :param delete_user: 删除用户的回调函数
    :return: Flet 控件
    """
    # 本地（临时）编辑状态——不在 User 对象中
    is_editing, set_is_editing = ft.use_state(False)
    new_first_name, set_new_first_name = ft.use_state(user.first_name)
    new_last_name, set_new_last_name = ft.use_state(user.last_name)

    def start_edit():
        """开始编辑用户信息。"""
        set_new_first_name(user.first_name)
        set_new_last_name(user.last_name)
        set_is_editing(True)

    def save():
        """保存编辑的用户信息。"""
        user.update(new_first_name, new_last_name)
        set_is_editing(False)

    def cancel():
        """取消编辑操作。"""
        set_is_editing(False)

    if not is_editing:
        return ft.Row(
            [
                ft.Text(f"{user.first_name} {user.last_name}"),
                ft.Button("编辑", on_click=start_edit),
                ft.Button("删除", on_click=lambda: delete_user(user)),
            ]
        )

    return ft.Row(
        [
            ft.TextField(
                label="名字",
                value=new_first_name,
                on_change=lambda e: set_new_first_name(e.control.value),
                width=180,
            ),
            ft.TextField(
                label="姓氏",
                value=new_last_name,
                on_change=lambda e: set_new_last_name(e.control.value),
                width=180,
            ),
            ft.Button("保存", on_click=save),
            ft.Button("取消", on_click=cancel),
        ]
    )


@ft.component
def AddUserForm(add_user) -> ft.Control:
    """添加用户表单组件。
    
    提供输入框和按钮用于添加新用户。
    
    :param add_user: 添加用户的回调函数
    :return: Flet 控件
    """
    # 使用本地缓冲区；添加时调用父组件动作
    new_first_name, set_new_first_name = ft.use_state("")
    new_last_name, set_new_last_name = ft.use_state("")

    def add_user_and_clear():
        """添加用户并清空输入框。"""
        add_user(new_first_name, new_last_name)
        set_new_first_name("")
        set_new_last_name("")

    return ft.Row(
        controls=[
            ft.TextField(
                label="名字",
                width=200,
                value=new_first_name,
                on_change=lambda e: set_new_first_name(e.control.value),
            ),
            ft.TextField(
                label="姓氏",
                width=200,
                value=new_last_name,
                on_change=lambda e: set_new_last_name(e.control.value),
            ),
            ft.Button("添加", on_click=add_user_and_clear),
        ]
    )


@ft.component
def AppView() -> list[ft.Control]:
    """应用主视图组件。
    
    整合用户列表和添加用户表单。
    
    :return: Flet 控件列表
    """
    app, _ = ft.use_state(
        App(
            users=[
                User("John", "Doe"),
                User("Jane", "Doe"),
                User("Foo", "Bar"),
            ]
        )
    )

    return [
        AddUserForm(app.add_user),
        *[UserView(user, app.delete_user) for user in app.users],
    ]


ft.run(lambda page: page.render(AppView))