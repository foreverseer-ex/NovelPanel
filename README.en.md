# NovelPanel

[中文文档 (README.md)](README.md)

NovelPanel turns a novel into a comic with “one click.” Paste your novel, the system extracts characters/scenes/plot, generates accurate Stable Diffusion prompts line-by-line, and renders via SD‑Forge. You pick the frames; the app stitches them into a comic. Model management with Civitai samples is supported.

- UI: Flet 0.28 (desktop/web)
- Engine: SD‑Forge / sd-webui
- Online: Civitai
- Config: JSON & env vars
- Python: 3.12+

## Features

- Model management: scan local SD‑Forge models (Checkpoint/LoRA/VAE), auto-match Civitai metadata and samples (cached locally).
- SD‑Forge client: list/switch models & options; txt2img with common params.
- Settings page: visual config for Civitai and SD‑Forge with auto-save.
- Common components: model cards, sample dialog, editable text, async image.

## Quick Start

- Requirements: Python 3.12+, SD‑Forge (local/remote), internet for Civitai.
- Run with uv:

```bash
uv run flet run          # Desktop
uv run flet run --web    # Web
```

## Configuration

- Copy and edit: `cp config.example.json config.json`
- Key fields (also editable from the in-app Settings page):
  - `sd_forge.base_url` default `http://127.0.0.1:7860`
  - `sd_forge.home` path to sd-webui-forge root (with models/*)
  - `civitai.api_token` (optional, for private content)
- Env override (Windows example):

```powershell
$env:SD_FORGE_SETTINGS__HOME = "C:\Users\<you>\sd-webui-forge"
$env:SD_FORGE_SETTINGS__BASE_URL = "http://127.0.0.1:7860"
$env:CIVITAI_SETTINGS__API_TOKEN = "<optional>"
```

See docs/configuration.md for details.

## Structure (Brief)

```
src/
  main.py, app.py
  pages/           # model management, settings, chat
  components/      # model cards/dialogs, editable text, async image
  routers/         # MCP routers (defined, pending implementation)
  schemas/         # Pydantic models
  services/        # Civitai / SD‑Forge / model metadata
  settings/        # app & service settings
  constants/, utils/
docs/
config.example.json
```

## Status

- Done: model management UI, settings page, common components; config mgmt (JSON+Env); Civitai integration; SD‑Forge client (models/options/txt2img).
- In progress: MCP routers defined with TODO, not implemented yet; storage layer (SQLModel + SQLite).

## Roadmap (Excerpt)

- Phase 1: implement Session/File/Reader/Actor/Memory/Draw routers and storage layer
- Phase 2: integrate LLM (Grok/Claude) for prompt planning & extraction
- Phase 3: UI enhancements (session mgmt, chapter tree, character editor, rating/sorting, export)
- Phase 4: multi-engine (InvokeAI, ComfyUI)
- Phase 5: advanced features (ControlNet, IPAdapter, templates)

## Troubleshooting

- Empty model list: check `sd_forge.home` and presence of `models/*`.
- Civitai fetch fails: verify network; set `civitai.api_token` if needed.
- Generation errors: ensure SD‑Forge is running and reachable; check sampler and resolution.

## License & Acknowledgements

- License: see LICENSE
- Acknowledgements: Flet, Stable Diffusion WebUI / SD‑Forge, Civitai
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
