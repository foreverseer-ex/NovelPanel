# NovelPanel

[English](README.en.md) | 中文

AI 驱动的小说创作与可视化工具：对话、绘图、模型元数据，一体化桌面/Web 体验。

## ✨ 功能概览

- **AI 对话**：OpenAI / xAI / Ollama / Anthropic / Google，多流派接入；流式输出、会话持久化、工具调用。
- **本地图像生成**：对接 SD-Forge/sd-webui，支持 LoRA/模型切换，结果分会话/批次落盘。
- **模型元数据**：Civitai/AIR 标识解析与本地缓存；扫描本地 Checkpoint/LoRA，抓取示例图与参数。
- **基础设施**：Flet 桌面/Web UI；FastAPI MCP 服务；SQLite 存储；可视化设置自动保存。

## 🗂 目录结构（精炼）

- `main.py`：应用入口（Flet）。
- `src/app.py`、`src/main.py`：应用启动与页面路由装配。
- `src/pages/`：页面（聊天、模型/角色/记忆管理、内容管理、设置、帮助、首页）。
- `src/components/`：可复用组件（聊天区、卡片、对话框、异步媒体等）。
- `src/services/`：业务服务
  - `db/`：SQLite 访问与各领域服务（会话/记忆/小说/绘图/角色）。
  - `llm/`、`draw/`、`model_meta/`：大模型、绘图与模型元数据提供方适配。
- `src/routers/`、`src/schemas/`：后端路由与 Pydantic 模型（用于 MCP/本地 API）。
- `src/constants/`、`src/settings/`、`src/utils/`：常量、设置、工具函数。
- `src/__mcp__.py`：FastAPI MCP 应用。

## 🚀 快速开始

要求：Python 3.12+（可选：本机 SD-Forge 用于文生图）

```bash
uv sync

# 桌面模式
uv run flet run

# Web 开发（指定 8000 端口，监视变更）
uv run flet run --web -w --port 8000
```

环境变量（也可在应用“设置”里配置）：

```bash
# Windows PowerShell
$env:OPENAI_API_KEY = "sk-..."
$env:XAI_API_KEY = "xai-..."
$env:CIVITAI_API_TOKEN = "..."
```

可选 `config.json`（位于项目根目录）支持覆盖：`llm`、`sd_forge`、`civitai`。

## 🔌 MCP（可选）

```bash
uv run uvicorn src.__mcp__:app --reload --host 127.0.0.1 --port 8000
# 文档: http://127.0.0.1:8000/docs
# 端点: http://127.0.0.1:8000/mcp
```

## 📄 许可证

见 [LICENSE](LICENSE)
