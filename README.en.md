# NovelPanel

English | [中文](README.md)

**Novel Creation & Visualization Tool** with AI chat, image generation, and model management.

## ✨ Core Features

### 🤖 AI Creative Assistant
- **Multi-LLM Support**: OpenAI / xAI (Grok) / Ollama / Anthropic (Claude) / Google (Gemini)
- **Smart Chat**: Streaming output, persistent conversation history, multi-turn conversations
- **Tool Router System**: AI can invoke built-in tools (session management, character management, memory, novel reader, drawing, etc.)
- **Creative Aid**: Plot construction, character development, scene description, prompt generation
- **Developer Mode**: Customizable system prompts for enhanced creative possibilities

### 🎨 Image Generation
- **Dual Engine**: SD-Forge local generation / Civitai cloud generation
- **Model Management**:
  - Auto-scan local models (Checkpoint / LoRA / VAE)
  - Filter by ecosystem (SD1 / SD2 / SDXL)
  - Cloud import: Support AIR identifiers (`urn:air:sd1:checkpoint:civitai:123@456`)
  - Batch sync: Auto-fetch Civitai metadata from SD-Forge

### ⚙️ System Architecture
- **UI Framework**: Flet (supports desktop and web modes)
- **LLM Framework**: LangChain + LangGraph (tool calling, streaming chat)
- **API Support**: MCP (Model Context Protocol) service endpoint
- **Config Management**: JSON files + environment variables + visual settings page

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
├── pages/              # UI pages
│   ├── chat_page.py        # AI chat page
│   ├── model_manage_page.py # Model management page
│   ├── settings_page.py     # Settings page
│   └── help_page.py         # Help page
├── components/         # UI components
│   ├── chat/               # Chat components (message display, input, sidebar)
│   ├── model_card/         # Model card component
│   └── editable_text.py    # Editable text component
├── services/           # Business logic
│   ├── llm/                # LLM services (OpenAI/Ollama implementations)
│   ├── draw/               # Drawing services (SD-Forge/Civitai implementations)
│   └── model_meta/         # Model metadata (local/Civitai)
├── routers/            # Tool routers (APIs for LLM to call)
│   ├── session.py          # Session management
│   ├── actor.py            # Character management
│   ├── memory.py           # Memory management
│   ├── reader.py           # Novel reader
│   ├── draw.py             # Drawing tools
│   ├── file.py             # File management
│   └── llm.py              # LLM auxiliary tools
├── schemas/            # Data models (Pydantic)
├── settings/           # Config management (LLM/Civitai/SD-Forge/UI)
├── constants/          # Constants
└── utils/              # Utility functions
```

## 🎯 User Guide

### 1. Initial Setup
Go to "Settings" page and configure necessary parameters:
- **LLM Settings**: Choose provider, enter API Key, select model
- **SD-Forge Settings**: Fill in Base URL and installation directory (for local generation)
- **Civitai Settings**: Enter API Token (optional, for cloud generation and metadata sync)

### 2. AI Chat
- Default to "Drawing" page (chat interface)
- Interact with AI assistant for creative advice or guidance
- AI automatically calls tool functions (e.g., query model list, generate images)
- Conversation history auto-saves, recoverable after restart

### 3. Model Management
- Click "Models" tab to view recognized models
- **Local Models**: Auto-scan SD-Forge directory
- **Cloud Import**: Click cloud icon, input AIR identifier
  - Format: `urn:air:{ecosystem}:{type}:civitai:{model_id}@{version_id}`
  - Example: `urn:air:sd1:checkpoint:civitai:348620@390021`
- **Batch Sync**: Settings page → "Import from SD Forge" button
- **Dual Filters**:
  - Ecosystem filter: SD1 / SD2 / SDXL
  - Base model filter: Pony / Illustrious / Standard
  - Both filters can be applied simultaneously

### 4. Image Generation
- Describe requirements in natural language through AI chat
- AI automatically selects appropriate models and parameters to call drawing tools
- Or choose drawing backend in settings page (SD-Forge / Civitai)

## 💾 Data & Storage Paths

Default data directory is `storage/data`. You can override via environment variables:

- `FLET_APP_STORAGE_DATA`: data directory (default: `storage/data`)
- `FLET_APP_STORAGE_TEMP`: temp directory (default: `storage/temp`)

Structure & important files:

- Database: `storage/data/database.db`
- Chat history: `storage/data/chat_history/`
- Model metadata: `storage/data/model_meta/` (with `checkpoint/` and `lora/`)
- Projects: `storage/data/projects/`

## ✅ Testing & Code Quality

```bash
# Run tests
uv run pytest -q

# Lint (pylint configured via pyproject)
uv run pylint src
```

## 🛠️ Development Status

### ✅ Completed
- **AI Chat System**
  - Streaming output, multi-turn conversations
  - Persistent conversation history (JSON)
  - Tool calling framework (based on LangChain)
  - Multi-LLM support (OpenAI / xAI / Ollama / Anthropic / Google)
  - Developer mode and customizable system prompts
  
- **Model Management**
  - Local model scanning (Checkpoint / LoRA / VAE)
  - Civitai metadata fetching and caching
  - AIR identifier parsing and import
  - Batch sync (scan from SD-Forge and fetch metadata)
  - Ecosystem filtering (SD1 / SD2 / SDXL)
  - Example image display
  
- **UI Pages**
  - Chat page (message display, input, clear conversation)
  - Model management page (card display, filtering, import, clear)
  - Settings page (visual config, auto-save, re-initialize)
  - Help page
  
- **Configuration Management**
  - JSON config files + environment variables
  - Visual settings interface
  - Auto-save and load

### 🚧 In Progress / To Be Implemented
- **Tool Router Implementation** (API framework complete, partial functionality pending)
  - ✅ Session/Actor/Memory/Reader/Draw/File router definitions
  - ⏳ Concrete implementations (parse_novel, generate, etc.)
  
- **Drawing Functionality**
  - ✅ SD-Forge service base implementation
  - ⏳ Complete drawing workflow (parameter config, batch generation)
  
- **Novel Reader**
  - ✅ Router definitions
  - ⏳ Parsing, chapter management, summary generation

## 🐛 Troubleshooting

### LLM Service Not Ready
- Check if API Key is configured in settings page
- Verify Base URL is correct (especially for Ollama local service)
- Click "Reinitialize LLM" button to retry connection
- Check log output (console) for specific errors

### Empty Model List
- Check if SD-Forge installation directory path is correct
- Ensure `models/Stable-diffusion/` and `models/Lora/` folders exist
- Click refresh button on models page

### Civitai Import Failed
- Check network connection (requires access to civitai.com)
- Verify AIR format: must include `@{version_id}` part
- Correct format: `urn:air:sd1:checkpoint:civitai:348620@390021`
- For batch sync, ensure SD-Forge directory is configured

### Conversation History Lost
- Conversation history saved in `storage/data/chat_history/default.json`
- For backup, copy this file
- Cannot recover after clearing conversation, use with caution

## 📄 License

See [LICENSE](LICENSE)

## 🙏 Acknowledgements

- [Flet](https://flet.dev/) - Modern Python UI framework
- [Stable Diffusion WebUI](https://github.com/AUTOMATIC1111/stable-diffusion-webui) / [SD-Forge](https://github.com/lllyasviel/stable-diffusion-webui-forge) - Image generation engine
- [Civitai](https://civitai.com/) - AI model community
- [LangChain](https://www.langchain.com/) - LLM application framework
