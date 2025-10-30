# NovelPanel

[English](README.en.md) | 中文

**AI 驱动的小说创作与视觉化工具**。内置智能对话、图像生成与模型管理，支持桌面与 Web 运行。

## ✨ 功能概览

- **AI 对话**：多提供商（OpenAI / xAI / Ollama / Anthropic / Google）、流式输出、历史自动保存、工具调用。
- **图像生成**：SD-Forge 本地生成与 Civitai 云端（基础功能），支持 AIR 标识符导入与元数据缓存。
- **模型管理**：自动扫描本地模型（Checkpoint/LoRA/VAE），按生态系统（SD1/SD2/SDXL）筛选。
- **基础设施**：Flet UI、FastAPI + MCP、SQLModel(SQLite)、配置可视化。

## 🚀 快速开始

- **环境**：Python 3.12+（可选：SD-Forge/sd-webui 用于本地图像）
- **安装与运行**：

```bash
# 使用 uv（推荐）
uv sync

# 桌面模式
uv run flet run

# Web 模式
uv run flet run --web
```

## ⚙️ 配置

- **环境变量（推荐）**：

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

- **config.json（可选）**：放在项目根目录。

```json
{
  "llm": {"provider": "xai", "api_key": "your-key", "model": "grok-beta"},
  "sd_forge": {"base_url": "http://127.0.0.1:7860", "home": "C:\\path\\to\\sd-webui-forge"},
  "civitai": {"api_token": "optional-token"}
}
```

优先级：环境变量 > 配置文件 > 默认值。应用内“设置”页支持可视化配置与自动保存。

## 📁 目录结构

```
src/
├── app.py           # Flet 入口
├── __mcp__.py       # FastAPI MCP 端点
├── pages/           # 页面：聊天/模型/设置/帮助
├── components/      # 组件：聊天区、模型卡等
├── services/        # 业务：llm/draw/model_meta/db
├── routers/         # API：session/actor/memory/reader/draw/llm
├── schemas/         # Pydantic 模型
├── settings/        # 配置
└── utils/           # 工具函数
```

## 🔌 MCP（可选）

```bash
uv run uvicorn src.__mcp__:app --reload --host 127.0.0.1 --port 8000
# 文档: http://127.0.0.1:8000/docs
# 端点: http://127.0.0.1:8000/mcp
```

## 📄 许可证

见 [LICENSE](LICENSE)
