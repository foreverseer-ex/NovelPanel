# NovelPanel

[English (README.en.md)](README.en.md)

NovelPanel：把小说“一键”锻造成漫画。粘贴小说文本，系统提取角色/场景/剧情，按行生成精准 Stable Diffusion 提示词，调用 SD‑Forge 渲染；你挑图，系统自动拼合为漫画。已支持模型管理与 Civitai 示例图联动。

- 桌面/网页 UI：Flet 0.28
- 生成引擎：SD‑Forge / sd-webui
- 在线资源：Civitai
- 配置：JSON 与环境变量
- Python：3.12+

## 功能

- 模型管理：扫描本地 SD‑Forge 模型（Checkpoint/LoRA/VAE），自动匹配 Civitai 元数据与示例图（本地缓存）。
- SD‑Forge 客户端：获取/切换模型与选项；文生图（txt2img）常用参数。
- 设置页面：可视化配置 Civitai 与 SD‑Forge，修改即保存。
- 通用组件：模型卡片、示例图对话框、可编辑文本、异步图片。

## 快速开始

- 需求：Python 3.12+、SD‑Forge（本地/远程）、可联网（用于 Civitai）。
- 使用 uv 运行：

```bash
uv run flet run          # 桌面模式
uv run flet run --web    # Web 模式
```

## 配置

- 复制并修改：`cp config.example.json config.json`
- 关键字段（也可在应用“设置”页可视化编辑并自动保存）：
  - `sd_forge.base_url`，默认 `http://127.0.0.1:7860`
  - `sd_forge.home` 指向 sd-webui-forge 根目录（含 models/*）
  - `civitai.api_token`（可选，用于访问私有内容）
- 环境变量覆盖（Windows 示例）：

```powershell
$env:SD_FORGE_SETTINGS__HOME = "C:\Users\<you>\sd-webui-forge"
$env:SD_FORGE_SETTINGS__BASE_URL = "http://127.0.0.1:7860"
$env:CIVITAI_SETTINGS__API_TOKEN = "<optional>"
```

更多见 docs/configuration.md。

## 结构（简）

```
src/
  main.py, app.py
  pages/           # 模型管理、设置、聊天
  components/      # 模型卡片/对话框、可编辑文本、异步图片
  routers/         # MCP 路由（接口已定义，待实现）
  schemas/         # Pydantic 数据模型
  services/        # Civitai / SD-Forge / 模型元数据
  settings/        # 应用与服务配置
  constants/, utils/
docs/
config.example.json
```

## 状态

- ✅ 已完成：模型管理 UI、设置页面、通用组件；配置管理（JSON+Env）；Civitai 集成；SD‑Forge 客户端（模型/选项/txt2img）。
- 🚧 进行中：MCP 路由接口已全部定义并标注 TODO，尚未实现；数据存储层（SQLModel + SQLite）。

## 路线图（摘）

- Phase 1：实现 Session/File/Reader/Actor/Memory/Draw 路由与存储层
- Phase 2：接入 LLM（Grok/Claude）用于提示词规划与抽取
- Phase 3：UI 完善（会话管理、章节树、角色库、评分/排序、导出）
- Phase 4：多引擎（InvokeAI、ComfyUI）
- Phase 5：高级功能（ControlNet、IPAdapter、模板库等）

## 故障排查

- 模型列表为空：检查 `sd_forge.home` 是否正确且含 `models/*`
- Civitai 拉取失败：检查网络，必要时配置 `civitai.api_token`
- 生成报错：确认 SD‑Forge 正在运行且地址可达，检查采样器与分辨率

## 许可与致谢

- License：见 LICENSE
- Acknowledgements：Flet、Stable Diffusion WebUI / SD‑Forge、Civitai
