# 配置系统说明

## 概述

NovelPanel 使用 JSON 格式的配置文件来管理应用设置。配置文件位于项目根目录的 `config.json`。

## 配置文件结构

```json
{
  "civitai": {
    "base_url": "https://civitai.com",
    "api_key": null,
    "timeout": 30.0
  },
  "sd_forge": {
    "base_url": "http://127.0.0.1:7860",
    "home": "C:\\path\\to\\sd-webui-forge",
    "timeout": 30.0,
    "generate_timeout": 120.0
  }
}
```

## 配置项说明

### Civitai 设置

- **base_url**: Civitai API 的基础 URL（默认：`https://civitai.com`）
- **api_key**: Civitai API 密钥（可选，用于访问私有内容）
- **timeout**: API 请求超时时间（秒，默认：30.0）

### SD Forge 设置

- **base_url**: SD Forge WebUI 的地址（默认：`http://127.0.0.1:7860`）
- **home**: SD Forge 的安装目录路径
- **timeout**: 普通 API 请求超时时间（秒，默认：30.0）
- **generate_timeout**: 图像生成请求超时时间（秒，默认：120.0）

## 使用方法

### 初次使用

1. 复制 `config.example.json` 为 `config.json`：
   ```bash
   cp config.example.json config.json
   ```

2. 编辑 `config.json`，填入你的实际配置

3. 启动应用，配置将自动加载

### 在应用中修改

1. 启动应用后，点击左侧导航栏的 **"设置"** 图标
2. 在设置页面中修改配置项
3. 点击 **"保存设置"** 按钮
4. 配置将立即生效并保存到 `config.json`

### 自动保存

- 应用启动时会自动加载 `config.json` 中的配置
- 应用关闭时会自动保存当前配置到 `config.json`
- 在设置页面点击保存按钮也会立即保存配置

## 注意事项

1. `config.json` 已添加到 `.gitignore`，不会被 Git 跟踪
2. 建议保留 `config.example.json` 作为配置模板参考
3. 如果配置文件不存在或格式错误，应用将使用默认配置
4. 修改 SD Forge 的 `home` 路径后，应用会根据该路径自动定位模型目录

## 默认值

如果配置文件不存在或某个配置项缺失，将使用以下默认值：

- **Civitai**:
  - base_url: `https://civitai.com`
  - api_key: `null`
  - timeout: `30.0`

- **SD Forge**:
  - base_url: `http://127.0.0.1:7860`
  - home: `C:\Users\zxb\Links\sd-webui-forge-aki-v1.0`
  - timeout: `30.0`
  - generate_timeout: `120.0`

## 故障排除

### 配置未生效

1. 检查 `config.json` 文件格式是否正确（使用 JSON 验证工具）
2. 查看应用日志，确认配置是否成功加载
3. 尝试删除 `config.json` 并重新创建

### 配置保存失败

1. 检查是否有文件写入权限
2. 确认 `config.json` 文件未被其他程序占用
3. 查看应用日志获取详细错误信息

