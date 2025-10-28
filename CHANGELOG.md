# 更新日志

## 2025-10-28

### 🎉 新功能

#### 1. 设置页面
- ✅ 创建了全新的设置页面，支持可视化编辑应用配置
- ✅ 支持编辑 Civitai 和 SD Forge 的所有配置项
- ✅ 提供保存和重置为默认值功能
- ✅ 实时验证输入并显示保存状态

#### 2. 配置管理系统
- ✅ 实现了基于 JSON 的配置文件系统（`config.json`）
- ✅ 应用启动时自动加载配置
- ✅ 应用关闭时自动保存配置
- ✅ 配置文件不存在时使用默认值
- ✅ 添加配置示例文件 `config.example.json`

#### 3. UI 尺寸常量重构
- ✅ 简化 `ui_size.py`，从 101 行减少到 71 行
- ✅ 统一图片尺寸：缩略图 240x240，大图 600x450
- ✅ 统一对话框尺寸：标准 500x600，宽屏 900x650
- ✅ 统一间距系统：小(8)、中(15)、大(20)
- ✅ 统一 Loading 尺寸：小(20)、中(30)、大(40)

#### 4. 可编辑文本组件
- ✅ 创建了 `EditableText` 组件
- ✅ 支持单行和多行输入模式
- ✅ 单行模式：回车提交
- ✅ 多行模式：显示提交按钮
- ✅ 失去焦点时自动提交
- ✅ 应用于模型详情页的说明字段编辑

### 🔧 改进

#### UI 优化
- ✅ 模型卡片高度统一，解决了标题多行时 chip 被挤压的问题
- ✅ Chip 标签添加边框和前缀（"类型："、"基础模型："）
- ✅ Chip 标签支持 flow 布局，过长时自动换行
- ✅ 模型标题垂直居中，统一单行和多行标题的位置
- ✅ 示例图片放大一倍（240x240）
- ✅ 示例详情页优化：大图顶部对齐，参数显示简洁化
- ✅ 所有中文化标签

#### 代码质量
- ✅ 添加了完整的文档注释
- ✅ 统一了代码风格
- ✅ 优化了常量管理
- ✅ 减少了代码冗余

### 📁 新增文件

```
src/
├── components/
│   ├── async_image.py           # 异步图片加载组件
│   └── editable_text.py         # 可编辑文本组件
├── constants/
│   ├── actor.py                 # 角色常量
│   └── ui_size.py               # UI 尺寸常量（重构）
├── pages/
│   └── settings_page.py         # 设置页面
└── settings/
    └── config_manager.py        # 配置管理器

docs/
└── configuration.md             # 配置系统文档

config.example.json              # 配置示例文件
test_config.py                   # 配置系统测试脚本
```

### 🔄 修改文件

```
src/
├── app.py                       # 添加配置加载/保存逻辑，添加设置页面
├── components/
│   ├── __init__.py              # 导出新组件
│   └── model_card/
│       ├── __init__.py          # 使用新的 UI 常量
│       ├── example_image_dialog.py  # 使用新的 UI 常量
│       └── model_detail_dialog.py   # 集成 EditableText
├── pages/
│   ├── __init__.py              # 导出设置页面
│   └── model_manage_page.py     # 使用新的 UI 常量
├── settings/
│   └── __init__.py              # 导出配置管理器
└── services/
    └── model_meta.py            # 添加 update_desc 方法

.gitignore                       # 忽略 config.json
pyproject.toml                   # 修复 uv 依赖配置
```

### 🐛 修复

- ✅ 修复了 `AttributeError: 'ModelMeta' object has no attribute 'model_type'`
- ✅ 修复了 `AttributeError: 'Page' object has no attribute 'show_snack_bar'`
- ✅ 修复了 `AttributeError: module 'flet' has no attribute 'InkWell'`
- ✅ 修复了 `pyproject.toml` 中的 uv 依赖警告

### 📝 文档

- ✅ 创建了配置系统使用文档 `docs/configuration.md`
- ✅ 更新了 README，标记了所有待实现功能
- ✅ 为所有新增文件添加了完整的 docstring

### ✅ 测试

- ✅ 配置系统测试通过
- ✅ UI 组件手动测试通过
- ✅ 应用启动/关闭测试通过

## 下一步计划

### 数据库层
- [ ] 搭建 SQLModel + SQLite 数据库
- [ ] 设计数据表结构

### MCP Router 实现
- [ ] Session Router（11 个接口）
- [ ] File Router（4 个接口）
- [ ] Reader Router（8 个接口）
- [ ] Actor Router（5 个接口）
- [ ] Memory Router（5 个接口）
- [ ] Draw Router（6 个接口）

### UI 功能
- [ ] 添加小说上传页面
- [ ] 添加小说阅读页面
- [ ] 添加角色管理页面
- [ ] 添加记忆管理页面
- [ ] 添加图像生成页面

