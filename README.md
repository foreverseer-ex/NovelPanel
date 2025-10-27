# NovelPanel

[English (README.en.md)](README.en.md)

NovelPanel：一键将小说锻造成漫画。输入任意小说文本，AI 智能提取人物、场景、故事脉络；逐章逐段迭代，自动生成精准 Stable Diffusion Prompt；使用 SD‑Forge 渲染，并预留多引擎（如 InvokeAI）扩展能力。你只需挑选心仪画面，系统即可拼合完整漫画。

## 功能特性

- 模型管理：扫描本地 SD‑Forge 模型（Checkpoint/Lora/VAE），展示带示例图的模型卡片。
- Civitai 集成：基于 .safetensors 文件从 Civitai 自动获取模型元数据与示例图，并做本地缓存。
- SD‑Forge API 客户端：列出模型、切换选项、调用 txt2img 常用参数生成。
- Flet UI：桌面/网页双端 UI，带导航与响应式卡片网格。

说明：端到端“小说→漫画”流水线与 MCP（grok、fastapi-mcp）集成在路线图中；当前代码聚焦模型浏览与 SD‑Forge 连接。

## 技术栈

- 应用框架：Flet 0.28
- 服务：SD‑Forge WebUI API、Civitai API
- 配置：pydantic-settings
- 图像：Pillow
- 构建/运行：uv 或 Poetry

## 项目结构

```
src/
  main.py                # 应用入口（Flet）
  pages/
    app.py               # AppView：侧边导航 + 主内容区
    model_manage_page.py # 模型管理页
  components/
    model_card/          # 模型卡片组件（UI）
  services/
    sd_forge.py          # SD‑Forge API（列表、切换、txt2img）
    civitai.py           # Civitai API（元数据、示例图）
    model_meta.py        # 本地元数据与示例图下载
  schemas/
    model.py             # Pydantic 模型（ModelMeta、Example、GenerateArg）
  settings/
    sd_forge_setting.py  # SD‑Forge 连接与本地模型路径
    civitai_setting.py   # Civitai 基本配置
    path.py              # 元数据缓存路径（见源码）
```

## 环境要求

- Python 3.12+
- 本地或远程运行的 SD‑Forge / sd-webui（用于生成）
- 可访问互联网（用于 Civitai 元数据与示例图）

## 安装与运行

使用 uv：

```
uv run flet run              # 桌面模式
uv run flet run --web        # Web 模式
```

使用 Poetry：

```
poetry install
poetry run flet run          # 桌面模式
poetry run flet run --web    # Web 模式
```

## 配置

通过 pydantic-settings 支持环境变量覆盖。

- SD‑Forge（见 `src/settings/sd_forge_setting.py`）
  - `SD_FORGE_SETTINGS__BASE_URL` 默认 `http://127.0.0.1:7860`
  - `SD_FORGE_SETTINGS__HOME` 指向 sd-webui-forge 根目录（包含 `models/Stable-diffusion`、`models/Lora`、`models/VAE`）
  - `SD_FORGE_SETTINGS__TIMEOUT`、`SD_FORGE_SETTINGS__GENERATE_TIMEOUT`

- Civitai（见 `src/settings/civitai_setting.py`）
  - `CIVITAI_SETTINGS__BASE_URL` 默认 `https://civitai.com`
  - `CIVITAI_SETTINGS__API_KEY` 可选
  - `CIVITAI_SETTINGS__TIMEOUT`

Windows 示例：

```
$env:SD_FORGE_SETTINGS__HOME = "C:\Users\<you>\sd-webui-forge"
$env:SD_FORGE_SETTINGS__BASE_URL = "http://127.0.0.1:7860"
$env:CIVITAI_SETTINGS__API_KEY = "<optional>"
```

## 现有工作流

- 模型发现：从 SD‑Forge `models` 目录读取 `.safetensors`。
- 元数据获取：若无本地元数据，按文件哈希访问 Civitai，缓存 `metadata.json` 与示例图。
- 浏览：在响应式网格中展示模型卡片、示例图与生成参数。
- 生成：`services/sd_forge.py` 提供 `create_text2image`，调用 `/sdapi/v1/txt2img`（prompt、negative、sampler、steps、CFG、seed、尺寸、styles、LoRA 标签）。

## 路线图

- 小说→漫画：基于大模型抽取人物/场景/情节，逐段生成 Prompt，画面挑选与版面编排。
- MCP 集成：接入 grok 与 fastapi-mcp，作为 NLU、提示规划与迭代工具。
- 多引擎渲染：扩展 InvokeAI，支持无缝切换。
- UI 流程：小说导入、章节/段落迭代、预览与选择、拼版与导出（CBZ/PDF）。

## 故障排查

- 列表为空：检查 `SD_FORGE_SETTINGS__HOME` 是否正确且包含 `models/*` 子目录。
- Civitai 拉取失败：检查网络与 `CIVITAI_SETTINGS__BASE_URL`；必要时配置 API Key。
- txt2img 报错：确认 SD‑Forge 正在运行且地址可达；检查采样器与分辨率限制。

## 开发说明

- 入口：`src/main.py` 绑定 `pages/app.py` 的 `AppView`。
- 首次运行可能较慢：`ModelMetaService.flush*` 会下载元数据与示例图。

## 许可

详见仓库根目录 LICENSE。

## 致谢

- Flet
- Stable Diffusion WebUI / SD‑Forge
- Civitai
