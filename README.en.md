# NovelPanel

[中文文档 (README.md)](README.md)

NovelPanel: turn any novel into a comic with one click. Paste a novel, let AI extract characters, scenes, and plot; iterate chapter by chapter and paragraph by paragraph to generate precise Stable Diffusion prompts; render with SD-Forge, with room for multi-engine backends like InvokeAI. You pick preferred frames and the system composes a complete comic.

## Features

- Model management: Scan local SD-Forge models (Checkpoint/Lora/VAE) and display model cards with examples from Civitai.
- Civitai integration: Given a .safetensors file, fetch model metadata and sample images from Civitai automatically and cache them locally.
- SD-Forge API client: List models, switch options, and call txt2img with common parameters.
- Flet UI: Desktop/web UI with NavigationRail and a responsive grid of model cards.

Note: The end-to-end novel-to-comic pipeline and MCP (grok, fastapi-mcp) integrations are on the roadmap; current codebase focuses on model browsing and SD‑Forge connectivity.

## Tech Stack

- App framework: Flet 0.28
- Services: SD‑Forge WebUI API, Civitai API
- Config: pydantic-settings
- Images: Pillow
- Build/Run: uv or Poetry

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

Using uv:

```
uv run flet run              # Desktop
uv run flet run --web        # Web
```

Using Poetry:

```
poetry install
poetry run flet run          # Desktop
poetry run flet run --web    # Web
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

## Current Workflow

- Model discovery: Read `.safetensors` from SD‑Forge `models` folders.
- Metadata fetch: If no local metadata, query Civitai by file hash and cache `metadata.json` plus sample images.
- Browse: Show cards in a responsive grid with example images and generation args.
- Generate: `services/sd_forge.py` exposes `create_text2image` calling `/sdapi/v1/txt2img` with prompt, negative, sampler, steps, CFG, seed, size, styles, and LoRA tags.

## Roadmap

- Novel → Comic pipeline: LLM-based extraction and per-paragraph prompt synthesis, frame selection, page composition.
- MCP integration: grok and fastapi-mcp as tools.
- Multi-engine render: Add InvokeAI backend.
- UI flows: Novel import, iterator, preview and selection, composition, export (CBZ/PDF).

## Troubleshooting

- Cannot list models: Verify `SD_FORGE_SETTINGS__HOME` and presence of `models/*` subfolders.
- Civitai fetch fails: Check internet and `CIVITAI_SETTINGS__BASE_URL`; consider API key.
- txt2img errors: Ensure SD‑Forge is running and reachable; validate `sampler_name` and resolution limits.

## Development Notes

- Entry: `src/main.py` registers `AppView` from `pages/app.py`.
- Model lists populate during `ModelMetaService.flush*`; first run may download metadata and sample images.

## License

See LICENSE.

## Acknowledgements

- Flet
- Stable Diffusion WebUI / SD‑Forge
- Civitai
