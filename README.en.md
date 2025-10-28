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

```
src/
  main.py                # Flet entrypoint
  pages/
    app.py               # AppView: NavigationRail & main area
    model_manage_page.py # Model management page
  components/
    model_card/          # Model card component (UI)
  services/
    sd_forge.py          # SD‑Forge API (list, switch, txt2img)
    civitai.py           # Civitai API (metadata, samples)
    model_meta.py        # Local metadata manager & sample downloads
  schemas/
    model.py             # Pydantic models (ModelMeta, Example, GenerateArg)
  settings/
    sd_forge_setting.py  # SD‑Forge connection & model paths
    civitai_setting.py   # Civitai basic settings
    path.py              # Metadata cache paths (see source)
```

## Requirements

- Python 3.12+
- SD‑Forge / sd-webui running locally or remotely (for generation)
- Internet access for Civitai metadata and samples

## Installation

uv is the only supported workflow.

```
uv run flet run              # Desktop
uv run flet run --web        # Web
```

## Configuration

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

```
$env:SD_FORGE_SETTINGS__HOME = "C:\Users\<you>\sd-webui-forge"
$env:SD_FORGE_SETTINGS__BASE_URL = "http://127.0.0.1:7860"
$env:CIVITAI_SETTINGS__API_KEY = "<optional>"
```

## Features Status

### ✅ Implemented

- **UI Layer (Flet)**
  - ✅ Model management page with sample images
  - ✅ Async image loading component with loading states
  - ✅ Model card component with example browser
  - ✅ Responsive grid layout

- **Service Layer**
  - ✅ Civitai integration: auto-fetch metadata and examples
  - ✅ SD-Forge API client: model lists, options, txt2img
  - ✅ Model metadata management: local cache and batch download

- **Schema Layer**
  - ✅ Session model with novel metadata
  - ✅ Character model with tag dictionary design
  - ✅ Memory models (MemoryEntry, ChapterSummary)
  - ✅ Model metadata (ModelMeta, Example, GenerateArg)

- **Constants Layer**
  - ✅ Character tag definitions (character_tags_description)
  - ✅ Memory key definitions (novel_memory_description, user_memory_description)
  - ✅ UI color constants

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

- Entry: `src/main.py` registers `AppView` from `pages/app.py`.
- Model lists populate during `ModelMetaService.flush*`; first run may download metadata and sample images.
- MCP Router interfaces are defined but not yet implemented; calls will raise `NotImplementedError`.
- Look for `# TODO:` markers in code to understand pending features.
- MCP Router requires LLM API configuration (Grok/Claude) for AI features (Phase 2).

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
