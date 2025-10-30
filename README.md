# NovelPanel

[English](README.en.md) | 中文

**AI 驱动的小说创作与视觉化工具**，集成智能对话、图像生成和模型管理。

## ✨ 核心功能

### 🤖 AI 对话系统
- **多 LLM 支持**：OpenAI / xAI (Grok) / Ollama / Anthropic (Claude) / Google (Gemini)
- **流式对话**：实时响应、对话历史自动保存、多轮上下文
- **工具调用**：AI 可调用内置工具（会话管理、角色管理、记忆系统、绘图等）
- **开发者模式**：自定义系统提示词，灵活配置

### 🎨 图像生成
- **双引擎**：SD-Forge 本地生成 / Civitai 云端生成（基础实现）
- **模型管理**：
  - 自动扫描本地模型（Checkpoint / LoRA / VAE）
  - 生态系统筛选（SD1 / SD2 / SDXL）
  - 云端导入：支持 AIR 标识符（如 `urn:air:sd1:checkpoint:civitai:123@456`）
  - 批量同步：从 SD-Forge 自动获取 Civitai 元数据

### ⚙️ 技术架构
- **UI 框架**：Flet 0.28（跨平台桌面和 Web 应用）
- **LLM 框架**：LangChain + LangGraph（工具调用、流式输出）
- **API 服务**：FastAPI + MCP (Model Context Protocol)
- **数据库**：SQLModel（SQLite）
- **配置管理**：JSON + 环境变量 + 可视化设置页面

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
├── pages/              # UI 页面（聊天、模型管理、设置、帮助）
├── components/         # UI 组件（聊天、模型卡片等）
├── services/           # 业务逻辑
│   ├── llm/                # LLM 服务（OpenAI/Ollama/xAI/Anthropic/Google）
│   ├── draw/               # 绘图服务（SD-Forge/Civitai）
│   ├── model_meta/         # 模型元数据（本地/Civitai）
│   └── db/                 # 数据库服务
├── routers/            # API 路由（供 LLM 工具调用）
│   ├── session.py          # 会话管理
│   ├── actor.py            # 角色管理
│   ├── memory.py           # 记忆系统
│   ├── reader.py           # 小说阅读器
│   ├── draw.py             # 绘图工具
│   └── llm.py              # LLM 辅助
├── schemas/            # 数据模型（Pydantic）
├── settings/           # 配置管理
└── utils/              # 工具函数
```

## 🔌 MCP 服务（可选）

提供 MCP (Model Context Protocol) API 端点，可供外部工具调用。

```bash
# 启动 MCP 服务（开发模式）
uv run uvicorn src.__mcp__:app --reload --host 127.0.0.1 --port 8000

# API 文档：http://127.0.0.1:8000/docs
# MCP 端点：http://127.0.0.1:8000/mcp
```

## 🎯 使用指南

### 1. 首次配置
启动应用后，进入"设置"页面配置：
- **LLM 设置**：选择提供商、输入 API Key、选择模型
- **SD-Forge 设置**：填写 API 地址和安装目录（可选，用于本地生成）
- **Civitai 设置**：填写 API Token（可选，用于云端生成和元数据同步）

### 2. AI 对话
- 应用默认打开"绘画"页面（聊天界面）
- 与 AI 对话，获取创作建议或生成图像
- AI 可自动调用工具函数（查询模型、生成图像等）
- 对话历史自动保存（`storage/data/chat_history/default.json`）

### 3. 模型管理
点击"模型"标签页管理模型：
- **本地模型**：自动扫描 SD-Forge 目录的 Checkpoint/LoRA/VAE
- **云端导入**：输入 AIR 标识符导入 Civitai 模型
  - 格式：`urn:air:{ecosystem}:{type}:civitai:{model_id}@{version_id}`
  - 示例：`urn:air:sdxl:checkpoint:civitai:123456@789012`
- **批量同步**：设置页面 → "从 SD Forge 导入"
- **筛选模型**：按生态系统（SD1/SD2/SDXL）或基础模型筛选

## 💾 数据存储

默认数据目录：`storage/data`（可通过环境变量自定义）

```
storage/data/
├── database.db          # SQLite 数据库
├── chat_history/        # 对话历史（JSON）
├── model_meta/          # 模型元数据缓存
│   ├── checkpoint/          # Checkpoint 元数据和示例图
│   └── lora/                # LoRA 元数据和示例图
└── projects/            # 项目文件（预留）
```

环境变量：
- `FLET_APP_STORAGE_DATA`：数据目录（默认 `storage/data`）
- `FLET_APP_STORAGE_TEMP`：临时目录（默认 `storage/temp`）

## 🛠️ 开发状态

### ✅ 核心功能完成
- **AI 对话系统**
  - 流式对话、多轮上下文
  - 对话历史持久化（JSON）
  - 工具调用框架（LangChain + LangGraph）
  - 支持 5 种 LLM 提供商
  - 开发者模式和自定义系统提示词
  
- **模型管理**
  - 本地模型扫描（Checkpoint/LoRA/VAE）
  - Civitai 元数据获取和缓存
  - AIR 标识符解析和云端导入
  - 批量同步 SD-Forge 模型
  - 生态系统筛选和示例图展示
  
- **UI 界面**
  - 聊天页面（消息显示、输入、历史加载）
  - 模型管理页面（卡片展示、筛选、导入）
  - 设置页面（可视化配置、自动保存）
  - 帮助页面
  
- **基础架构**
  - 数据库（SQLModel + SQLite）
  - MCP API 服务（FastAPI）
  - 配置管理（JSON + 环境变量）

### 🚧 部分完成
- **工具路由**：API 框架完整，部分具体功能待实现
  - ✅ Session/Actor/Memory 管理（数据库操作）
  - ⏳ Reader 小说阅读器（解析、章节管理）
  - ⏳ Draw 绘图工具（与 AI 集成）
  
- **图像生成**：基础服务完成，工作流待完善
  - ✅ SD-Forge 基础服务（txt2img）
  - ✅ Civitai 基础服务
  - ⏳ 完整工作流（批量生成、参数配置）

## 🐛 常见问题

### LLM 服务未就绪
- 检查"设置"页面中的 API Key 是否配置正确
- 验证 Base URL（Ollama 本地服务需要正确的地址）
- 点击"重新初始化 LLM"按钮重试
- 查看控制台日志排查错误

### 模型列表为空
- 检查 SD-Forge 安装路径是否正确
- 确保目录包含 `models/Stable-diffusion/` 和 `models/Lora/`
- 点击模型页面刷新按钮

### Civitai 导入失败
- 检查网络连接（需访问 civitai.com）
- 验证 AIR 格式：`urn:air:{ecosystem}:{type}:civitai:{model_id}@{version_id}`
- 确保包含 `@{version_id}` 部分

### 对话历史丢失
- 对话历史保存在 `storage/data/chat_history/default.json`
- 可手动备份此文件
- 清空对话后无法恢复

## 📄 许可证

见 [LICENSE](LICENSE)

## 🙏 致谢

- [Flet](https://flet.dev/) - 现代 Python UI 框架
- [Stable Diffusion WebUI](https://github.com/AUTOMATIC1111/stable-diffusion-webui) / [SD-Forge](https://github.com/lllyasviel/stable-diffusion-webui-forge) - 图像生成引擎
- [Civitai](https://civitai.com/) - AI 模型社区
- [LangChain](https://www.langchain.com/) - LLM 应用框架
