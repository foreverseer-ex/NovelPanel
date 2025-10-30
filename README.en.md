# NovelPanel

English | [中文](README.md)

**AI-Powered Novel Creation & Visualization Tool** - Intelligent chat, image generation, and model management.

## ✨ Core Features

### 🤖 AI Chat System
- **Multi-LLM Support**: OpenAI / xAI (Grok) / Ollama / Anthropic (Claude) / Google (Gemini)
- **Streaming Chat**: Real-time responses, auto-save conversation history, multi-turn context
- **Tool Calling**: AI can invoke built-in tools (session, character, memory, drawing, etc.)
- **Developer Mode**: Customizable system prompts for flexible configurations

### 🎨 Image Generation
- **Dual Engine**: SD-Forge local / Civitai cloud (basic implementation)
- **Model Management**:
  - Auto-scan local models (Checkpoint / LoRA / VAE)
  - Ecosystem filtering (SD1 / SD2 / SDXL)
  - Cloud import: AIR identifiers (e.g., `urn:air:sd1:checkpoint:civitai:123@456`)
  - Batch sync: Auto-fetch Civitai metadata from SD-Forge

### ⚙️ Technical Architecture
- **UI Framework**: Flet 0.28 (cross-platform desktop and web)
- **LLM Framework**: LangChain + LangGraph (tool calling, streaming)
- **API Service**: FastAPI + MCP (Model Context Protocol)
- **Database**: SQLModel (SQLite)
- **Config**: JSON + environment variables + visual settings page

## 🚀 Quick Start

### Requirements
- Python 3.12+
- (Optional) SD-Forge / sd-webui for local image generation

### Installation & Run

```bash
# Using uv (recommended)
# First time: sync dependencies (create local virtual env)
uv sync

# Run Flet (Desktop mode)
uv run flet run

# Run Flet (Web mode)
uv run flet run --web
```

## ⚙️ Configuration

### Method 1: Config File
Create `config.json` in the project root (optional; you can also rely on environment variables only)

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

### Method 2: Environment Variables (Recommended for secrets)

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

**Priority**: Environment Variables > Config File > Defaults

You can also configure visually in the app's "Settings" page with auto-save.

## 📁 Project Structure

```
src/
├── app.py              # Flet app entry
├── __mcp__.py          # MCP service endpoint (FastAPI)
├── pages/              # UI pages (chat, model management, settings, help)
├── components/         # UI components (chat, model cards, etc.)
├── services/           # Business logic
│   ├── llm/                # LLM services (OpenAI/Ollama/xAI/Anthropic/Google)
│   ├── draw/               # Drawing services (SD-Forge/Civitai)
│   ├── model_meta/         # Model metadata (local/Civitai)
│   └── db/                 # Database services
├── routers/            # API routers (for LLM tool calling)
│   ├── session.py          # Session management
│   ├── actor.py            # Character management
│   ├── memory.py           # Memory system
│   ├── reader.py           # Novel reader
│   ├── draw.py             # Drawing tools
│   └── llm.py              # LLM helpers
├── schemas/            # Data models (Pydantic)
├── settings/           # Configuration management
└── utils/              # Utility functions
```

## 🔌 MCP Service (Optional)

Provides MCP (Model Context Protocol) API endpoints for external tools.

```bash
# Start MCP service (development mode)
uv run uvicorn src.__mcp__:app --reload --host 127.0.0.1 --port 8000

# API docs: http://127.0.0.1:8000/docs
# MCP endpoint: http://127.0.0.1:8000/mcp
```

## 🎯 User Guide

### 1. Initial Setup
After launching, go to "Settings" page:
- **LLM Settings**: Choose provider, enter API Key, select model
- **SD-Forge Settings**: Fill in API URL and installation directory (optional, for local generation)
- **Civitai Settings**: Enter API Token (optional, for cloud generation and metadata sync)

### 2. AI Chat
- App opens to "Drawing" page (chat interface) by default
- Chat with AI for creative advice or image generation
- AI can auto-invoke tool functions (query models, generate images, etc.)
- Conversation history auto-saves (`storage/data/chat_history/default.json`)

### 3. Model Management
Click "Models" tab to manage models:
- **Local Models**: Auto-scan Checkpoint/LoRA/VAE from SD-Forge directory
- **Cloud Import**: Input AIR identifier to import Civitai models
  - Format: `urn:air:{ecosystem}:{type}:civitai:{model_id}@{version_id}`
  - Example: `urn:air:sdxl:checkpoint:civitai:123456@789012`
- **Batch Sync**: Settings page → "Import from SD Forge"
- **Filter Models**: By ecosystem (SD1/SD2/SDXL) or base model

## 💾 Data Storage

Default data directory: `storage/data` (customizable via environment variables)

```
storage/data/
├── database.db          # SQLite database
├── chat_history/        # Conversation history (JSON)
├── model_meta/          # Model metadata cache
│   ├── checkpoint/          # Checkpoint metadata and example images
│   └── lora/                # LoRA metadata and example images
└── projects/            # Project files (reserved)
```

Environment variables:
- `FLET_APP_STORAGE_DATA`: data directory (default `storage/data`)
- `FLET_APP_STORAGE_TEMP`: temp directory (default `storage/temp`)

## 🛠️ Development Status

### ✅ Core Features Complete
- **AI Chat System**
  - Streaming chat, multi-turn context
  - Persistent conversation history (JSON)
  - Tool calling framework (LangChain + LangGraph)
  - Support for 5 LLM providers
  - Developer mode and custom system prompts
  
- **Model Management**
  - Local model scanning (Checkpoint/LoRA/VAE)
  - Civitai metadata fetching and caching
  - AIR identifier parsing and cloud import
  - Batch sync from SD-Forge
  - Ecosystem filtering and example images
  
- **UI Interface**
  - Chat page (message display, input, history loading)
  - Model management page (card display, filtering, import)
  - Settings page (visual config, auto-save)
  - Help page
  
- **Infrastructure**
  - Database (SQLModel + SQLite)
  - MCP API service (FastAPI)
  - Configuration management (JSON + environment variables)

### 🚧 Partially Complete
- **Tool Routers**: API framework complete, some features pending
  - ✅ Session/Actor/Memory management (database operations)
  - ⏳ Reader novel parser (parsing, chapter management)
  - ⏳ Draw tools (AI integration)
  
- **Image Generation**: Basic services complete, workflow pending
  - ✅ SD-Forge basic service (txt2img)
  - ✅ Civitai basic service
  - ⏳ Complete workflow (batch generation, parameter config)

## 🐛 Troubleshooting

### LLM Service Not Ready
- Check API Key in "Settings" page
- Verify Base URL (Ollama local service needs correct address)
- Click "Reinitialize LLM" button to retry
- Check console logs for errors

### Empty Model List
- Check SD-Forge installation path
- Ensure directory contains `models/Stable-diffusion/` and `models/Lora/`
- Click refresh button on models page

### Civitai Import Failed
- Check network connection (requires access to civitai.com)
- Verify AIR format: `urn:air:{ecosystem}:{type}:civitai:{model_id}@{version_id}`
- Ensure `@{version_id}` part is included

### Conversation History Lost
- History saved in `storage/data/chat_history/default.json`
- Can manually backup this file
- Cannot recover after clearing

## 📄 License

See [LICENSE](LICENSE)

## 🙏 Acknowledgements

- [Flet](https://flet.dev/) - Modern Python UI framework
- [SD-Forge](https://github.com/lllyasviel/stable-diffusion-webui-forge) / [SD-WebUI](https://github.com/AUTOMATIC1111/stable-diffusion-webui) - Image generation
- [Civitai](https://civitai.com/) - AI model community
- [LangChain](https://www.langchain.com/) - LLM application framework
