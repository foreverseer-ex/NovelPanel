# NovelPanel

English | [中文](README.md)

**AI-Powered Novel Creation & Visualization Tool**. Built-in intelligent chat, image generation, and model management for desktop and web.

## ✨ Overview

- **AI Chat**: Multi-provider (OpenAI / xAI / Ollama / Anthropic / Google), streaming output, history auto-save, tool calling.
- **Image Generation**: SD-Forge local and Civitai cloud (basic), AIR identifier import, metadata caching.
- **Model Management**: Auto-scan local models (Checkpoint/LoRA/VAE), filter by ecosystem (SD1/SD2/SDXL).
- **Infrastructure**: Flet UI, FastAPI + MCP, SQLModel(SQLite), visual configuration.

## 🚀 Quick Start

- **Requirements**: Python 3.12+ (optional: SD-Forge/sd-webui for local image gen)
- **Install & Run**:

```bash
# Using uv (recommended)
uv sync

# Desktop mode
uv run flet run

# Web mode
uv run flet run --web
```

## ⚙️ Configuration

- **Environment variables (recommended)**:

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

- **config.json (optional)** in project root:

```json
{
  "llm": {"provider": "xai", "api_key": "your-key", "model": "grok-beta"},
  "sd_forge": {"base_url": "http://127.0.0.1:7860", "home": "C:\\path\\to\\sd-webui-forge"},
  "civitai": {"api_token": "optional-token"}
}
```

Priority: Env vars > Config file > Defaults. Visual config with auto-save is available in-app on the “Settings” page.

## 📁 Structure

```
src/
├── app.py           # Flet entry
├── __mcp__.py       # FastAPI MCP endpoint
├── pages/           # Pages: chat/models/settings/help
├── components/      # Components: chat area, model card, etc.
├── services/        # Biz: llm/draw/model_meta/db
├── routers/         # API: session/actor/memory/reader/draw/llm
├── schemas/         # Pydantic models
├── settings/        # Configuration
└── utils/           # Utilities
```

## 🔌 MCP (Optional)

```bash
uv run uvicorn src.__mcp__:app --reload --host 127.0.0.1 --port 8000
# Docs: http://127.0.0.1:8000/docs
# Endpoint: http://127.0.0.1:8000/mcp
```

## 📄 License

See [LICENSE](LICENSE)
