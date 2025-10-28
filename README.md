# NovelPanel

[English (README.en.md)](README.en.md)

NovelPanel：一键将小说锻造成漫画。输入任意小说文本，AI 智能提取人物、场景、故事脉络；逐章逐段迭代，自动生成精准 Stable Diffusion Prompt；使用 SD‑Forge 渲染，并预留多引擎（如 InvokeAI）扩展能力。你只需挑选心仪画面，系统即可拼合完整漫画。

## 功能特性

- 模型管理：扫描本地 SD‑Forge 模型（Checkpoint/Lora/VAE），展示带示例图的模型卡片。
- Civitai 集成：基于 .safetensors 文件从 Civitai 自动获取模型元数据与示例图，并做本地缓存。
- SD‑Forge API 客户端：列出模型、切换选项、调用 txt2img 常用参数生成。
- Flet UI：桌面/网页双端 UI，带导航与响应式卡片网格。

**当前状态：** 已完成 MCP 架构设计和 API 定义，所有 Router 接口已定义并标记为 TODO 待实现。模型管理 UI 和 SD-Forge/Civitai 集成功能已完成。

## 技术栈

- 应用框架：Flet 0.28
- 服务：SD‑Forge WebUI API、Civitai API
- 配置：pydantic-settings
- 图像：Pillow
- 构建/运行：uv（目前仅支持 uv 工作流）

## 项目结构

```text
src/
  main.py                # Flet UI 应用入口
  app.py                 # 主应用视图：侧边导航 + 主内容区
  
  # UI 层（Flet）
  pages/
    model_manage_page.py # 模型管理页
    settings_page.py     # 设置页
  components/
    async_image.py       # 异步图片加载组件
    editable_text.py     # 可编辑文本组件
    model_card/          # 模型卡片组件
      __init__.py        # ModelCard 主组件
      example_image_dialog.py  # 示例图片对话框
      model_detail_dialog.py   # 模型详情对话框
  
  # MCP 层（Model Context Protocol）- FastAPI 风格
  routers/
    session.py           # 会话管理：创建/更新/删除会话（/session）
    file.py              # 文件管理：小说上传、漫画导出（/file）
    reader.py            # 阅读器：按行读取小说，章节梗概（/reader）
    actor.py             # 角色管理：角色设定、外貌、SD标签（/actor）
    memory.py            # 记忆系统：世界观、用户偏好、上下文（/memory）
    draw.py              # 绘图管理：提示词生成、图像生成、分镜组合（/draw）
  
  # 数据模型层
  schemas/
    session.py           # 会话相关模型（包含小说元数据）
    memory.py            # 记忆系统模型（MemoryEntry 键值对、ChapterSummary 章节摘要）
    actor.py             # 角色相关模型
    model_meta.py        # SD模型元数据
  
  # 服务层
  services/
    sd_forge.py          # SD‑Forge API 客户端
    civitai.py           # Civitai API 客户端
    model_meta.py        # 本地模型元数据管理
  
  # 配置与常量
  settings/
    config_manager.py    # 配置管理器（JSON 配置文件）
    sd_forge_setting.py  # SD‑Forge 配置
    civitai_setting.py   # Civitai 配置
  utils/
    path.py              # 路径工具
  constants/
    color.py             # UI 颜色常量
    ui_size.py           # UI 尺寸常量（图片、对话框、间距等）
    memory.py            # 记忆系统键名定义（novel_memory_description, user_memory_description）
    actor.py             # 角色系统标签定义（character_tags_description）

# 文档
docs/
  configuration.md           # 配置系统使用文档
  EDITABLE_TEXT_COMPONENT.md # 可编辑文本组件文档
  UI_SIZE_CONSTANTS.md       # UI 尺寸常量文档

# 配置文件
config.json                  # 应用配置文件（git ignore）
config.example.json          # 配置示例文件
```

## 环境要求

- Python 3.12+
- 本地或远程运行的 SD‑Forge / sd-webui（用于生成）
- 可访问互联网（用于 Civitai 元数据与示例图）

## 安装与运行（仅支持 uv）

```bash
uv run flet run              # 桌面模式
uv run flet run --web        # Web 模式
```

## 配置

### 配置方式

#### 方式 1：JSON 配置文件（推荐）

复制 `config.example.json` 为 `config.json` 并编辑：

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

或者直接在应用的**设置页面**中可视化编辑配置，修改后自动保存。

#### 方式 2：环境变量覆盖

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

```powershell
$env:SD_FORGE_SETTINGS__HOME = "C:\Users\<you>\sd-webui-forge"
$env:SD_FORGE_SETTINGS__BASE_URL = "http://127.0.0.1:7860"
$env:CIVITAI_SETTINGS__API_KEY = "<optional>"
```

详细配置说明请参阅 [docs/configuration.md](docs/configuration.md)。

## MCP 架构设计

NovelPanel 采用 **MCP (Model Context Protocol)** 架构，将小说转漫画的复杂流程模块化为6个核心路由器。

**技术实现：** 所有路由器基于 **FastAPI** 框架，使用 `APIRouter` 定义标准 REST API：

- 使用装饰器定义路由：`@router.post()`、`@router.get()`、`@router.put()`、`@router.delete()`
- 异步函数：所有处理函数使用 `async def`
- 类型注解：完整的请求/响应 Pydantic 模型
- 自动文档：支持 OpenAPI/Swagger 文档生成

### 路由器列表

### 1. **Session Router** (`/session`) - 会话管理

管理小说转漫画项目的生命周期。Session 模型集成了小说元数据（标题、作者、总行数等）。

**API端点：**

- `POST /session/create`: 创建新项目，初始化目录结构
- `GET /session/{session_id}`: 获取项目详情、进度和小说元数据
- `PUT /session/{session_id}/status`: 更新处理状态（analyzing→generating→completed）
- `GET /session/`: 列出所有会话（支持分页和状态过滤）
- `DELETE /session/{session_id}`: 删除会话及相关数据

**数据模型：** Session 包含小说元数据字段（`author`, `total_lines`），章节信息通过 Reader Router 管理。

**应用场景：** 用户开始新的小说转换任务时，系统自动创建会话，解析小说后更新元数据字段。

### 2. **File Router** (`/file`) - 文件管理

简化设计：只处理小说文件和生成图像的读写。

**API端点：**

- `PUT /file/novel`: 上传/保存小说文件（TXT）
- `GET /file/novel`: 获取小说文件
- `PUT /file/image`: 保存生成的图像（参数 line 指定行号）
- `GET /file/image`: 获取生成的图像（参数 line 指定行号）

**应用场景：** 
- 上传小说文本，自动检测编码并保存到会话目录
- 按行号存储和读取生成的图像，如 `storage/sessions/{session_id}/images/{line}.png`

### 3. **Reader Router** (`/reader`) - 阅读器

按行解析小说，每行对应一个段落和一张图片。管理章节结构和梗概。

**API端点：**

- `POST /reader/parse`: 解析 TXT 文件，按行分割并识别章节，更新 Session 元数据
- `GET /reader/line/{line_index}`: 读取第 n 行的内容（返回字符串）
- `GET /reader/line/{line_index}/chapter`: 获取第 n 行对应的章节索引
- `GET /reader/chapters`: 获取所有章节摘要列表
- `GET /reader/chapter/{chapter_index}`: 获取章节详情
- `GET /reader/chapter/{chapter_index}/summary`: 获取章节梗概
- `PUT /reader/chapter/{chapter_index}/summary`: 设置章节梗概（用于 AI 上下文）

**数据模型：**

- **ChapterSummary**: 章节索引、标题、梗概、起止行号
- 行内容直接返回字符串，无需额外模型

**应用场景：** 逐行读取小说，为每行生成一张图片，章节梗概提供上下文。

### 4. **Actor Router** (`/actor`) - 角色管理

简化设计：基础的 CRUD 操作和预定义标签查询。

**设计原则：**
- 简化模型：角色只包含 name 和 tags（字典）
- 纯文本值：所有 tags 的值都是纯文本字符串（列表类型用逗号分隔）
- 预定义标签：常用标签定义在 `constants.actor` 中（`character_tags_description`）

**API端点：**

**角色操作：**
- `POST /actor/create`: 创建角色
- `GET /actor/{character_id}`: 获取角色信息
- `GET /actor/`: 列出所有角色
- `PUT /actor/{character_id}`: 更新角色信息
- `DELETE /actor/{character_id}`: 删除角色

**预定义标签查询：**
- `GET /actor/tag-description`: 获取单个标签的描述（参数：tag）
- `GET /actor/tag-descriptions`: 获取所有预定义标签

**数据示例：**
```python
# 创建角色
{
    "name": "李云",
    "tags": {
        "别名": "云师兄, 小李",
        "角色定位": "主角",
        "性别": "男",
        "年龄": "18岁",
        "发型": "黑色长发",
        "服饰": "蓝色道袍",
        "性格": "沉稳冷静",
        "SD标签": "1boy, long black hair, blue robe"
    }
}
```

**应用场景：** 管理角色信息，用于生成图像时的提示词构建和角色一致性保证。

### 5. **Memory Router** (`/memory`) - 记忆系统

存储世界观、用户偏好等长期上下文。

**设计原则：**
- 简化设计：移除了 type、source、importance、metadata 等复杂字段
- 键值对存储：所有记忆使用 `MemoryEntry` 键值对存储（仅保留 key、value、description）
- 纯文本值：所有 value 统一使用纯文本字符串（列表类型用逗号分隔）
- 预定义键：常用键定义在 `constants.memory` 中（`novel_memory_description`、`user_memory_description`）
- 章节信息：通过 `ChapterSummary` 模型单独处理（也在 memory.py 中）

**API端点：**

- `POST /memory/create`: 创建记忆条目（key-value 对）
- `GET /memory/{memory_id}`: 获取记忆条目
- `GET /memory/query`: 检索相关记忆（重要情节、用户反馈）
- `PUT /memory/{memory_id}`: 更新记忆
- `DELETE /memory/{memory_id}`: 删除记忆
- `GET /memory/world-setting/{session_id}`: 获取世界观设定（聚合视图）
- `PUT /memory/world-setting/{session_id}`: 批量更新世界观设定
- `POST /memory/world-setting/{session_id}/extract`: AI 提取世界观（时代、地点、魔法体系）
- `GET /memory/preference/{session_id}`: 获取用户偏好（聚合视图）
- `PUT /memory/preference/{session_id}`: 批量更新用户偏好
- `GET /memory/session/{session_id}`: 获取完整上下文（供 AI 使用）
- `POST /memory/session/{session_id}/import`: 导入记忆数据

**数据示例：**
```python
# 存储世界观（使用中文键名）
{
    "作品类型": "修仙",
    "主题": "成长与复仇",
    "背景设定": "古代修仙世界，以五行灵力为核心的修炼体系",
    "主要地点": "云海山门, 天元城, 魔兽森林",
    "故事梗概": "少年李云从凡人逐步修炼成仙的历程"
}

# 存储用户偏好（使用中文键名）
{
    "艺术风格": "anime",
    "避免的标签": "nsfw, gore, horror",
    "喜欢的标签": "masterpiece, best quality, detailed",
    "补充说明": "希望画面色彩鲜艳，注重人物表情刻画"
}
```

**应用场景：** AI 生成提示词时自动应用世界观风格，记住用户不喜欢的标签。所有配置以纯文本形式存储，便于查看和修改。

### 6. **Draw Router** (`/draw`) - 绘图管理

简化设计：直接代理 SD-Forge API，所有接口添加 session_id 参数。

**API端点：**

**SD-Forge API 代理：**
- `GET /draw/loras`: 获取 LoRA 模型列表
- `GET /draw/sd-models`: 获取 SD 模型列表
- `GET /draw/options`: 获取 SD 选项配置
- `POST /draw/options`: 设置 SD 选项（切换模型）

**图像生成：**
- `POST /draw/txt2img`: 文生图（参数：session_id, batch_id, prompt, negative_prompt 等）
- `GET /draw/image`: 获取生成的图像（参数：session_id, batch_id, index）

**应用场景：** 
- 调用 SD-Forge 生成图像，按 batch_id 组织
- 图像保存到 `storage/sessions/{session_id}/batches/{batch_id}/{index}.png`
- 每个 batch_id 可以包含多张图像（batch_size 参数控制）

## 工作流程示例


```text
1. 用户上传小说《修仙小说.txt》
   └─> create_session() → session_id: "abc123"
   └─> upload_novel() → 触发 parse_novel()

2. 系统解析小说
   └─> parse_novel() → 按行分割，识别50章，共500行，更新 Session
   └─> get_session() → session.total_lines: 500, status.total_chapters: 50
   └─> get_chapters() → 获取所有章节摘要
   └─> extract_characters() → AI提取主角"李云"等5个角色
   └─> extract_world_setting() → AI识别世界观：
       {
         "作品类型": "修仙",
         "主题": "成长与复仇",
         "背景设定": "古代修仙世界，以五行灵力为核心的修炼体系",
         "主要地点": "云海山门, 天元城, 魔兽森林"
       }
   └─> put_chapter_summary(ch=0) → 存储"第一章：初入山门"的梗概

3. 逐行生成图片（每行 = 一张图）
   for line_index in range(500):
     a) get_line(line_index=0) → "李云站在山巅，俯瞰云海。"（字符串）
     b) get_line_chapter_index(line_index=0) → chapter_index: 0
     c) get_chapter_summary(ch=0) → "李云初入修仙门派..."（提供上下文）
     d) get_characters_in_scene() → ["李云"]
     e) AI生成提示词:
        positive: "1boy, long hair, blue robe, standing on mountain peak, ..."
        negative: "nsfw, gore"
        loras: {"cultivator_style": 0.8}
     f) txt2img(session_id="abc123", batch_id="line_0", prompt=...) → 生成图像
     g) get_image(session_id="abc123", batch_id="line_0", index=0) → 获取图像

4. 组合与导出
   └─> 收集所有行的图像，按顺序组合成漫画
```


## 现有功能

### ✅ 已实现


- **UI 层 (Flet)**
  - ✅ 模型管理页面：扫描本地 SD‑Forge 模型，展示带示例图的卡片
  - ✅ 设置页面：可视化编辑 Civitai 和 SD Forge 配置，自动保存
  - ✅ 异步图片加载组件：支持 loading 状态、错误处理、点击事件
  - ✅ 可编辑文本组件：单行/多行输入，点击编辑，失焦保存
  - ✅ 模型卡片组件：支持示例图浏览和详情查看
  - ✅ 模型详情对话框：展示元数据、大图预览、可编辑说明
  - ✅ 示例图片对话框：网格展示所有示例图，查看生成参数
  - ✅ 响应式网格布局，统一的 UI 尺寸系统

- **配置管理**
  - ✅ 配置管理器 (ConfigManager)：JSON 配置文件加载/保存
  - ✅ 应用启动时自动加载配置
  - ✅ 应用关闭时自动保存配置
  - ✅ 配置示例文件 (config.example.json)
  - ✅ 环境变量覆盖支持

- **Service 层**
  - ✅ Civitai 集成：自动获取模型元数据与示例图
  - ✅ SD‑Forge API 客户端：模型列表、选项设置、txt2img 生成
  - ✅ 模型元数据管理：本地缓存与批量下载、更新说明

- **Schema 层**
  - ✅ 会话模型 (Session)：包含小说元数据
  - ✅ 角色模型 (Character)：简化的标签字典设计
  - ✅ 记忆模型 (MemoryEntry, ChapterSummary)：键值对存储
  - ✅ 模型元数据 (ModelMeta, Example, GenerateArg)

- **Constants 层**
  - ✅ 角色标签定义 (character_tags_description)
  - ✅ 记忆键定义 (novel_memory_description, user_memory_description)
  - ✅ UI 颜色常量 (ModelTypeChipColor, BaseModelColor)
  - ✅ UI 尺寸常量 (图片、对话框、间距、Chip 等)

- **文档**
  - ✅ 配置系统使用文档 (docs/configuration.md)
  - ✅ 可编辑文本组件文档 (docs/EDITABLE_TEXT_COMPONENT.md)
  - ✅ UI 尺寸常量文档 (docs/UI_SIZE_CONSTANTS.md)
  - ✅ 更新日志 (CHANGELOG.md)

### 🚧 待实现（已定义 API 和 TODO 标记）

所有 MCP Router 接口已定义完成，函数体使用 `raise NotImplementedError()` 标记为待实现：

- **Session Router** (`/session`) - 7 个接口
  - POST /create, GET /{id}, GET /, PUT /{id}, DELETE /{id}, PUT /{id}/status, PUT /{id}/progress

- **File Router** (`/file`) - 4 个接口
  - PUT /novel, GET /novel, PUT /image, GET /image

- **Reader Router** (`/reader`) - 8 个接口
  - POST /parse, GET /line/{idx}, GET /line/{idx}/chapter
  - GET /chapters, GET /chapter/{idx}, GET /chapter/{idx}/summary, PUT /chapter/{idx}/summary

- **Actor Router** (`/actor`) - 7 个接口（2 个已实现）
  - POST /create, GET /{id}, GET /, PUT /{id}, DELETE /{id}
  - ✅ GET /tag-description, ✅ GET /tag-descriptions

- **Memory Router** (`/memory`) - 7 个接口（2 个已实现）
  - POST /create, GET /{id}, GET /query, PUT /{id}, DELETE /{id}
  - ✅ GET /key-description, ✅ GET /key-descriptions

- **Draw Router** (`/draw`) - 6 个接口
  - GET /loras, GET /sd-models, GET /options, POST /options
  - POST /generate, GET /image

**下一步：** 实现会话管理和文件处理，搭建数据库存储层

## 路线图

### Phase 1: MCP 核心实现（进行中）

- [x] 完成 MCP 架构设计
- [x] 定义所有 Router 接口和 Schema（36 个接口已定义）
- [x] 为所有未实现的接口添加 TODO 标记和 NotImplementedError
- [x] 实现 Actor Router 的预定义标签查询（2/7 接口）
- [x] 实现 Memory Router 的预定义键查询（2/7 接口）
- [x] 完成 UI 基础设施（模型管理、设置页面、通用组件）
- [x] 实现配置管理系统（JSON 配置文件）
- [ ] 搭建数据库存储层（SQLModel + SQLite）
- [ ] 实现 Session/File Router（11 个接口）
- [ ] 实现 Reader Router（小说解析，8 个接口）
- [ ] 实现 Actor Router（角色提取，5 个接口待完成）
- [ ] 实现 Memory Router（5 个接口待完成）
- [ ] 实现 Draw Router（提示词生成，6 个接口）

### Phase 2: AI 集成

- [ ] 接入 Grok/Claude 作为提示词规划引擎
- [ ] 实现角色外貌→SD标签的转换
- [ ] 实现场景描述→提示词的生成
- [ ] 优化提示词质量（A/B测试）

### Phase 3: UI 完善

- [ ] 会话管理界面
- [ ] 小说章节目录树
- [ ] 角色库编辑器
- [ ] 图像选择与评分界面
- [ ] 分镜拖拽排序
- [ ] 导出进度与预览

### Phase 4: 多引擎支持

- [ ] InvokeAI 集成
- [ ] ComfyUI 集成
- [ ] 引擎无缝切换
- [ ] 性能对比工具

### Phase 5: 高级功能

- [ ] ControlNet/IPAdapter 支持（参考图一致性）
- [ ] 批量生成优化
- [ ] 云端渲染支持
- [ ] 模板库（风格预设）

## 故障排查

- 列表为空：检查 `SD_FORGE_SETTINGS__HOME` 是否正确且包含 `models/*` 子目录。
- Civitai 拉取失败：检查网络与 `CIVITAI_SETTINGS__BASE_URL`；必要时配置 API Key。
- txt2img 报错：确认 SD‑Forge 正在运行且地址可达；检查采样器与分辨率限制。

## 开发说明

### 架构分层

1. **UI 层 (Flet)**: 负责用户交互和展示
2. **MCP 层 (Routers)**: 业务逻辑和流程编排，基于 FastAPI
3. **Service 层**: 与外部服务交互（SD-Forge、Civitai）
4. **Schema 层**: 数据模型定义（Pydantic）

### 开发规范

- **路由定义**：使用 FastAPI 的 `APIRouter`，每个路由文件创建独立的 router 实例

  ```python
  router = APIRouter(prefix="/session", tags=["会话管理"])
  
  @router.post("/create", response_model=Session)
  async def create_session(...) -> Session:
      pass
  ```

- **异步函数**：所有路由处理函数使用 `async def` 定义
- **类型注解**：完整的参数和返回值类型注解，使用 Pydantic 模型
- **参数验证**：路径参数直接定义，查询参数使用 `Query()` 添加验证和描述
- **Schema 设计**：仅定义数据存储模型，不创建 `*Create`、`*Update` 等请求模型
- **Session ID**：作为所有操作的上下文标识，通常作为第一个参数
- **错误处理**：使用 FastAPI 的 HTTPException 和 Pydantic ValidationError

### 测试运行

```bash
# 当前可运行：模型管理UI
uv run flet run

# MCP 实现后：完整流程
python -m src.routers.session  # 测试会话管理
```

### 添加新功能


1. 在 `schemas/` 定义数据模型
2. 在 `routers/` 定义业务接口
3. 在 `services/` 实现具体逻辑
4. 在 UI 层调用 Router 接口


### 注意事项

- 首次运行较慢：`ModelMetaService.flush*` 会下载元数据与示例图
- 配置文件 `config.json` 会在首次保存配置后自动创建
- MCP Router 接口已定义但尚未实现，调用会抛出 `NotImplementedError`
- 查看代码中的 `# TODO:` 标记可了解待实现功能
- MCP Router 需要配置 LLM API（Grok/Claude）才能使用 AI 功能（Phase 2）
- 图像生成需要 SD-Forge 运行在配置的地址（默认 `http://127.0.0.1:7860`）

### 代码质量

- ✅ 所有文件包含完整的 docstring 注释
- ✅ 所有函数包含参数和返回值说明
- ✅ 未实现的功能使用 `# TODO:` 标记和 `raise NotImplementedError()`
- ✅ 使用 pylint 进行代码质量检查
- ✅ 遵循 PEP 8 代码风格

## 许可

详见仓库根目录 LICENSE。

## 致谢

- Flet
- Stable Diffusion WebUI / SD‑Forge
- Civitai
