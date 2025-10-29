# NovelPanel

[English](README.en.md) | 中文

**小说创作与视觉化工具**，集成 AI 对话、图像生成和模型管理。

## ✨ 核心功能

### 🤖 AI 创作助手
- **多 LLM 支持**：OpenAI / xAI (Grok) / Ollama / Anthropic (Claude) / Google (Gemini)
- **智能对话**：流式输出、对话历史持久化、多轮会话
- **工具路由系统**：AI 可调用内置工具函数（会话管理、角色管理、记忆管理、小说阅读、绘图等）
- **创作辅助**：剧情构思、人物塑造、场景描写、提示词生成
- **开发者模式**：可自定义系统提示词，解锁更多创作可能

### 🎨 图像生成
- **双引擎**：SD-Forge 本地生成 / Civitai 云端生成
- **模型管理**：
  - 自动扫描本地模型（Checkpoint / LoRA / VAE）
  - 按生态系统筛选（SD1 / SD2 / SDXL）
  - 云端导入：支持 AIR 标识符（`urn:air:sd1:checkpoint:civitai:123@456`）
  - 批量同步：从 SD-Forge 自动获取 Civitai 元数据

### ⚙️ 系统架构
- **UI 框架**：Flet（支持桌面和 Web 模式）
- **LLM 框架**：LangChain + LangGraph（工具调用、流式对话）
- **API 支持**：MCP (Model Context Protocol) 服务端点
- **配置管理**：JSON 文件 + 环境变量 + 可视化设置页面

## 🚀 快速开始

### 环境要求
- Python 3.12+
- （可选）SD-Forge / sd-webui（用于本地图像生成）

### 安装运行

```bash
# 使用 uv（推荐）
# 第一次使用先同步依赖（创建本地虚拟环境）
uv sync

# 运行 Flet（桌面模式）
uv run flet run

# 运行 Flet（Web 模式）
uv run flet run --web
```

## ⚙️ 配置

### 方式 1：配置文件
在项目根目录新建 `config.json`（可选，亦可仅使用环境变量）

```json
{
  "llm": {
    "provider": "xai",
    "api_key": "your-key",
    "model": "grok-beta"
  },
  "sd_forge": {
    "base_url": "http://127.0.0.1:7860",
    "home": "C:\\path\\to\\sd-webui-forge"
  },
  "civitai": {
    "api_token": "optional-token"
  }
}
```

### 方式 2：环境变量（推荐用于密钥）

```bash
# Windows PowerShell
$env:OPENAI_API_KEY = "sk-..."
$env:XAI_API_KEY = "xai-..."
$env:CIVITAI_API_TOKEN = "..."

# Linux/macOS
export OPENAI_API_KEY="sk-..."
export XAI_API_KEY="xai-..."
export CIVITAI_API_TOKEN="..."
```

**优先级**：环境变量 > 配置文件 > 默认值

在应用内的"设置"页面也可以可视化配置并自动保存。

## 📁 项目结构

```
src/
├── app.py              # Flet 应用入口
├── __mcp__.py          # MCP 服务端点（FastAPI）
├── pages/              # UI 页面
│   ├── chat_page.py        # AI 对话页面
│   ├── model_manage_page.py # 模型管理页面
│   ├── settings_page.py     # 设置页面
│   └── help_page.py         # 帮助页面
├── components/         # UI 组件
│   ├── chat/               # 聊天组件（消息显示、输入框、侧边栏）
│   ├── model_card/         # 模型卡片组件
│   └── editable_text.py    # 可编辑文本组件
├── services/           # 业务逻辑
│   ├── llm/                # LLM 服务（OpenAI/Ollama 实现）
│   ├── draw/               # 绘图服务（SD-Forge/Civitai 实现）
│   └── model_meta/         # 模型元数据（本地/Civitai）
├── routers/            # 工具路由（供 LLM 调用的 API）
│   ├── session.py          # 会话管理
│   ├── actor.py            # 角色管理
│   ├── memory.py           # 记忆管理
│   ├── reader.py           # 小说阅读器
│   ├── draw.py             # 绘图工具
│   ├── file.py             # 文件管理
│   └── llm.py              # LLM 辅助工具
├── schemas/            # 数据模型（Pydantic）
├── settings/           # 配置管理（LLM/Civitai/SD-Forge/UI）
├── constants/          # 常量定义
└── utils/              # 工具函数
```

## 🔌 启动 MCP 服务

使用 FastAPI + fastapi-mcp 提供 MCP 端点。

```bash
# 开发模式（自动重载）
uv run uvicorn src.__mcp__:app --reload --host 127.0.0.1 --port 8000

# 生产模式（示例）
uv run uvicorn src.__mcp__:app --host 0.0.0.0 --port 8000
```

- 文档地址：`http://127.0.0.1:8000/docs`
- MCP 端点：`http://127.0.0.1:8000/mcp`

## 🎯 使用指南

### 1. 首次配置
进入"设置"页面，配置必要参数：
- **LLM 设置**：选择提供商、输入 API Key、选择模型
- **SD-Forge 设置**：填写 Base URL 和安装目录（如需本地生成）
- **Civitai 设置**：填写 API Token（可选，用于云端生成和元数据同步）

### 2. AI 对话
- 默认进入"绘画"页面（聊天界面）
- 与 AI 助手交流，获取创作建议或指导
- AI 会自动调用工具函数（如查询模型列表、生成图像等）
- 对话历史自动保存，重启后可恢复

### 3. 模型管理
- 点击"模型"标签页查看已识别的模型
- **本地模型**：自动扫描 SD-Forge 目录
- **云端导入**：点击云朵图标，输入 AIR 标识符
  - 格式：`urn:air:{ecosystem}:{type}:civitai:{model_id}@{version_id}`
  - 示例：`urn:air:sd1:checkpoint:civitai:348620@390021`
- **批量同步**：设置页面 → "从 SD Forge 导入" 按钮
- **双重筛选**：
  - 生态系统筛选：SD1 / SD2 / SDXL
  - 基础模型筛选：Pony / Illustrious / Standard
  - 两个筛选条件可同时生效

### 4. 图像生成
- 通过 AI 对话自然语言描述需求
- AI 会自动选择合适的模型和参数调用绘图工具
- 或在设置页面选择绘图后端（SD-Forge / Civitai）

## 💾 数据与存储路径

应用的默认数据目录位于 `storage/data`，可通过环境变量覆盖：

- `FLET_APP_STORAGE_DATA`：数据目录（默认：`storage/data`）
- `FLET_APP_STORAGE_TEMP`：临时目录（默认：`storage/temp`）

目录结构与重要文件：

- 数据库：`storage/data/database.db`
- 对话历史：`storage/data/chat_history/`
- 模型元数据：`storage/data/model_meta/`（含 `checkpoint/` 与 `lora/`）
- 项目文件：`storage/data/projects/`

## 🛠️ 开发状态

### ✅ 已完成
- **AI 对话系统**
  - 流式输出、多轮对话
  - 对话历史持久化（JSON）
  - 工具调用框架（基于 LangChain）
  - 多 LLM 支持（OpenAI / xAI / Ollama / Anthropic / Google）
  - 开发者模式和自定义系统提示词
  
- **模型管理**
  - 本地模型扫描（Checkpoint / LoRA / VAE）
  - Civitai 元数据获取和缓存
  - AIR 标识符解析和导入
  - 批量同步（从 SD-Forge 扫描并获取元数据）
  - 生态系统筛选（SD1 / SD2 / SDXL）
  - 示例图展示
  
- **UI 页面**
  - 聊天页面（消息显示、输入、清空对话）
  - 模型管理页面（卡片展示、筛选、导入、清空）
  - 设置页面（可视化配置、自动保存、重新初始化）
  - 帮助页面
  
- **配置管理**
  - JSON 配置文件 + 环境变量
  - 可视化设置界面
  - 自动保存和加载

### 🚧 进行中 / 待完善
- **工具路由实现**（API 框架已完成，部分功能待实现）
  - ✅ Session/Actor/Memory/Reader/Draw/File 路由定义
  - ⏳ 具体实现（parse_novel、generate 等）
  
- **绘图功能**
  - ✅ SD-Forge 服务基础实现
  - ⏳ 完整的绘图工作流（参数配置、批量生成）
  
- **小说阅读器**
  - ✅ 路由定义
  - ⏳ 解析、章节管理、梗概生成

## 🐛 故障排查

### LLM 服务未就绪
- 检查设置页面中的 API Key 是否已配置
- 验证 Base URL 是否正确（特别是 Ollama 本地服务）
- 点击"重新初始化 LLM"按钮尝试重新连接
- 查看日志输出（控制台）排查具体错误

### 模型列表为空
- 检查 SD-Forge 安装目录路径是否正确
- 确保目录下存在 `models/Stable-diffusion/` 和 `models/Lora/` 文件夹
- 点击模型页面的刷新按钮

### Civitai 导入失败
- 检查网络连接（需访问 civitai.com）
- 验证 AIR 格式：必须包含 `@{version_id}` 部分
- 正确格式：`urn:air:sd1:checkpoint:civitai:348620@390021`
- 如需批量同步，确保已配置 SD-Forge 目录

### 对话历史丢失
- 对话历史保存在 `storage/data/chat_history/default.json`
- 如需备份，复制此文件
- 清空对话后无法恢复，请谨慎操作

## 📄 许可证

见 [LICENSE](LICENSE)

## 🙏 致谢

- [Flet](https://flet.dev/) - 现代 Python UI 框架
- [Stable Diffusion WebUI](https://github.com/AUTOMATIC1111/stable-diffusion-webui) / [SD-Forge](https://github.com/lllyasviel/stable-diffusion-webui-forge) - 图像生成引擎
- [Civitai](https://civitai.com/) - AI 模型社区
- [LangChain](https://www.langchain.com/) - LLM 应用框架
