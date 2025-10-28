# NovelPanel

[中文文档 (README.md)](README.md)

NovelPanel: turn any novel into a comic with one click. Paste a novel, let AI extract characters, scenes, and plot; iterate chapter by chapter and paragraph by paragraph to generate precise Stable Diffusion prompts; render with SD-Forge, with room for multi-engine backends like InvokeAI. You pick preferred frames and the system composes a complete comic.

## Features

- Model management: Scan local SD-Forge models (Checkpoint/Lora/VAE) and display model cards with examples from Civitai.
- Civitai integration: Given a .safetensors file, fetch model metadata and sample images from Civitai automatically and cache them locally.
- SD-Forge API client: List models, switch options, and call txt2img with common parameters.
- Flet UI: Desktop/web UI with NavigationRail and a responsive grid of model cards.

**Current Status:** MCP architecture and API definitions completed. All Router interfaces are defined and marked as TODO. Model management UI and SD-Forge/Civitai integration are fully functional.

## Tech Stack

- App framework: Flet 0.28
- Services: SD‑Forge WebUI API, Civitai API
- Config: pydantic-settings
- Images: Pillow
- Build/Run: uv

## Project Structure

```text
src/
  main.py                # Flet entrypoint
  app.py                 # Main app view: NavigationRail & main area
  
  # UI Layer (Flet)
  pages/
    model_manage_page.py # Model management page
    settings_page.py     # Settings page
  components/
    async_image.py       # Async image loading component
    editable_text.py     # Editable text component
    model_card/          # Model card components
      __init__.py        # ModelCard main component
      example_image_dialog.py  # Example images dialog
      model_detail_dialog.py   # Model detail dialog
  
  # MCP Layer (Model Context Protocol) - FastAPI style
  routers/
    session.py           # Session management
    file.py              # File management
    reader.py            # Novel reader
    actor.py             # Character management
    memory.py            # Memory system
    draw.py              # Drawing management
  
  # Schema Layer
  schemas/
    session.py           # Session models (with novel metadata)
    memory.py            # Memory models (MemoryEntry, ChapterSummary)
    actor.py             # Character models
    model_meta.py        # SD model metadata
  
  # Service Layer
  services/
    sd_forge.py          # SD‑Forge API client
    civitai.py           # Civitai API client
    model_meta.py        # Local model metadata manager
  
  # Configuration & Constants
  settings/
    config_manager.py    # Config manager (JSON config file)
    sd_forge_setting.py  # SD‑Forge settings
    civitai_setting.py   # Civitai settings
  utils/
    path.py              # Path utilities
  constants/
    color.py             # UI color constants
    ui_size.py           # UI size constants (images, dialogs, spacing, etc)
    memory.py            # Memory key definitions
    actor.py             # Character tag definitions

# Documentation
docs/
  configuration.md           # Configuration system docs
  EDITABLE_TEXT_COMPONENT.md # Editable text component docs
  UI_SIZE_CONSTANTS.md       # UI size constants docs

# Configuration Files
config.json                  # App config file (git ignored)
config.example.json          # Config example file
```

## Requirements

- Python 3.12+
- SD‑Forge / sd-webui running locally or remotely (for generation)
- Internet access for Civitai metadata and samples

## Installation

uv is the only supported workflow.

```bash
uv run flet run              # Desktop
uv run flet run --web        # Web
```

## Configuration

### Configuration Methods

#### Method 1: JSON Config File (Recommended)

Copy `config.example.json` to `config.json` and edit:

```json
{
  "civitai": {
    "base_url": "https://civitai.com",
    "api_key": null,
    "timeout": 10.0
  },
  "sd_forge": {
    "base_url": "http://127.0.0.1:7860",
    "home": "C:\\Users\\<you>\\sd-webui-forge",
    "timeout": 10.0,
    "generate_timeout": 300.0
  }
}
```

Or edit directly in the app's **Settings Page** for visual configuration with auto-save.

#### Method 2: Environment Variables Override

Settings are managed by pydantic-settings and can be overridden by environment variables.

- SD‑Forge (`src/settings/sd_forge_setting.py`)
  - `SD_FORGE_SETTINGS__BASE_URL` default `http://127.0.0.1:7860`
  - `SD_FORGE_SETTINGS__HOME` path to your sd-webui-forge directory (with `models/Stable-diffusion`, `models/Lora`, `models/VAE`)
  - `SD_FORGE_SETTINGS__TIMEOUT`, `SD_FORGE_SETTINGS__GENERATE_TIMEOUT`

- Civitai (`src/settings/civitai_setting.py`)
  - `CIVITAI_SETTINGS__BASE_URL` default `https://civitai.com`
  - `CIVITAI_SETTINGS__API_KEY` optional
  - `CIVITAI_SETTINGS__TIMEOUT`

Windows example:

```powershell
$env:SD_FORGE_SETTINGS__HOME = "C:\Users\<you>\sd-webui-forge"
$env:SD_FORGE_SETTINGS__BASE_URL = "http://127.0.0.1:7860"
$env:CIVITAI_SETTINGS__API_KEY = "<optional>"
```

For detailed configuration instructions, see [docs/configuration.md](docs/configuration.md).

## Features Status

### ✅ Implemented

- **UI Layer (Flet)**
  - ✅ Model management page: scan local SD-Forge models with example images
  - ✅ Settings page: visual editing of Civitai and SD Forge config, auto-save
  - ✅ Async image loading component: loading states, error handling, click events
  - ✅ Editable text component: single/multi-line input, click to edit, blur to save
  - ✅ Model card component: example browsing and detail viewing
  - ✅ Model detail dialog: metadata display, large image preview, editable description
  - ✅ Example images dialog: grid display of all examples, view generation parameters
  - ✅ Responsive grid layout, unified UI size system

- **Configuration Management**
  - ✅ ConfigManager: JSON config file loading/saving
  - ✅ Auto-load config on app startup
  - ✅ Auto-save config on app close
  - ✅ Config example file (config.example.json)
  - ✅ Environment variable override support

- **Service Layer**
  - ✅ Civitai integration: auto-fetch metadata and examples
  - ✅ SD-Forge API client: model lists, options, txt2img
  - ✅ Model metadata management: local cache, batch download, update descriptions

- **Schema Layer**
  - ✅ Session model with novel metadata
  - ✅ Character model with tag dictionary design
  - ✅ Memory models (MemoryEntry, ChapterSummary)
  - ✅ Model metadata (ModelMeta, Example, GenerateArg)

- **Constants Layer**
  - ✅ Character tag definitions (character_tags_description)
  - ✅ Memory key definitions (novel_memory_description, user_memory_description)
  - ✅ UI color constants (ModelTypeChipColor, BaseModelColor)
  - ✅ UI size constants (images, dialogs, spacing, chips, etc)

- **Documentation**
  - ✅ Configuration system docs (docs/configuration.md)
  - ✅ Editable text component docs (docs/EDITABLE_TEXT_COMPONENT.md)
  - ✅ UI size constants docs (docs/UI_SIZE_CONSTANTS.md)
  - ✅ Changelog (CHANGELOG.md)

### 🚧 TODO (API Defined, Implementation Pending)

All MCP Router interfaces are defined with `raise NotImplementedError()`:

- **Session Router** (`/session`) - 7 endpoints
  - POST /create, GET /{id}, GET /, PUT /{id}, DELETE /{id}, PUT /{id}/status, PUT /{id}/progress

- **File Router** (`/file`) - 4 endpoints
  - PUT /novel, GET /novel, PUT /image, GET /image

- **Reader Router** (`/reader`) - 8 endpoints
  - POST /parse, GET /line/{idx}, GET /line/{idx}/chapter
  - GET /chapters, GET /chapter/{idx}, GET /chapter/{idx}/summary, PUT /chapter/{idx}/summary

- **Actor Router** (`/actor`) - 7 endpoints (2 implemented)
  - POST /create, GET /{id}, GET /, PUT /{id}, DELETE /{id}
  - ✅ GET /tag-description, ✅ GET /tag-descriptions

- **Memory Router** (`/memory`) - 7 endpoints (2 implemented)
  - POST /create, GET /{id}, GET /query, PUT /{id}, DELETE /{id}
  - ✅ GET /key-description, ✅ GET /key-descriptions

- **Draw Router** (`/draw`) - 6 endpoints
  - GET /loras, GET /sd-models, GET /options, POST /options
  - POST /generate, GET /image

**Next Step:** Implement session management and file handling, set up database layer.

## Roadmap

### Phase 1: MCP Core Implementation (In Progress)

- [x] Complete MCP architecture design
- [x] Define all Router interfaces and Schemas (36 endpoints defined)
- [x] Add TODO markers and NotImplementedError for unimplemented endpoints
- [x] Implement Actor Router tag queries (2/7 endpoints)
- [x] Implement Memory Router key queries (2/7 endpoints)
- [x] Complete UI infrastructure (model management, settings page, common components)
- [x] Implement configuration management system (JSON config file)
- [ ] Set up database storage layer (SQLModel + SQLite)
- [ ] Implement Session/File Router (11 endpoints)
- [ ] Implement Reader Router (novel parsing, 8 endpoints)
- [ ] Implement Actor Router (character extraction, 5 endpoints remaining)
- [ ] Implement Memory Router (5 endpoints remaining)
- [ ] Implement Draw Router (prompt generation, 6 endpoints)

### Phase 2: AI Integration

- [ ] Integrate Grok/Claude for prompt planning
- [ ] Implement character appearance → SD tags conversion
- [ ] Implement scene description → prompt generation
- [ ] A/B testing for prompt quality

### Phase 3: UI Enhancement

- [ ] Session management interface
- [ ] Novel chapter tree view
- [ ] Character editor
- [ ] Image selection and rating
- [ ] Panel drag-and-drop ordering
- [ ] Export progress and preview

### Phase 4: Multi-Engine Support

- [ ] InvokeAI integration
- [ ] ComfyUI integration
- [ ] Seamless engine switching
- [ ] Performance comparison tools

### Phase 5: Advanced Features

- [ ] ControlNet/IPAdapter support
- [ ] Batch generation optimization
- [ ] Cloud rendering support
- [ ] Template library (style presets)

## Troubleshooting

- Cannot list models: Verify `SD_FORGE_SETTINGS__HOME` and presence of `models/*` subfolders.
- Civitai fetch fails: Check internet and `CIVITAI_SETTINGS__BASE_URL`; consider API key.
- txt2img errors: Ensure SD‑Forge is running and reachable; validate `sampler_name` and resolution limits.

## Development Notes

### Architecture Layers

1. **UI Layer (Flet)**: User interaction and presentation
2. **MCP Layer (Routers)**: Business logic and workflow orchestration, based on FastAPI
3. **Service Layer**: External service integration (SD-Forge, Civitai)
4. **Schema Layer**: Data model definitions (Pydantic)

### Development Standards

- **Router Definition**: Use FastAPI's `APIRouter`, each router file creates an independent router instance
- **Async Functions**: All route handlers use `async def`
- **Type Annotations**: Complete parameter and return type annotations using Pydantic models
- **Error Handling**: Use FastAPI's HTTPException and Pydantic ValidationError

### Testing

```bash
# Currently runnable: Model management UI
uv run flet run

# After MCP implementation: Complete workflow
python -m src.routers.session  # Test session management
```

### Adding New Features

1. Define data models in `schemas/`
2. Define business interfaces in `routers/`
3. Implement logic in `services/`
4. Call Router interfaces from UI layer

### Notes

- First run is slow: `ModelMetaService.flush*` downloads metadata and sample images
- Config file `config.json` is auto-created on first config save
- MCP Router interfaces are defined but not implemented; calls raise `NotImplementedError`
- Look for `# TODO:` markers in code to understand pending features
- MCP Router requires LLM API configuration (Grok/Claude) for AI features (Phase 2)
- Image generation requires SD-Forge running at configured address (default `http://127.0.0.1:7860`)

### Code Quality

- ✅ All files include complete docstring comments
- ✅ All functions have parameter and return value descriptions
- ✅ Unimplemented features marked with `# TODO:` and `raise NotImplementedError()`
- ✅ Code quality checked with pylint
- ✅ Follows PEP 8 code style

## License

See LICENSE.

## Acknowledgements

- Flet
- Stable Diffusion WebUI / SD‑Forge
- Civitai
