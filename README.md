# Umi-OCR AI OCR 插件

## 🚀 项目简介

本插件为 **Umi-OCR** 提供多个主流AI模型的OCR 功能，支持主流 AI 服务提供商的视觉识别 API。作为离线 OCR 的强力补充，为用户提供更高精度、更广泛语言支持的云端文字识别服务。


## 🌟 支持的 AI 服务商

### 🌐 云端服务商
| 服务商 | 建议模型 | 特点 |
|--------|----------|------|
| **硅基流动 (SiliconFlow)** | Qwen/Qwen2.5-VL-32B-Instruct | 开源模型多，价格低，速度快，准确率超高，**最推荐** |
| **阿里云百炼 (Alibaba)** | qwen-vl-plus-2025-08-15 | 专业OCR模型，中文识别优秀 |
| **智谱AI (ZhipuAI)** | glm-4.5v | 国产大模型，多模态能力强 |
| **豆包(Doubao)** | Doubao-1.5-vision-pro-32k | 中文优化效果好，性价比高 |
| **OpenAI** | gpt-5-mini | 高精度，多语言支持 |
| **Google Gemini** | gemini-2.5-flash | 速度快，成本低 |
| **xAI Grok** | grok-4 | 创新模型，独特优势 |
| **OpenRouter** | anthropic/claude-3.5-sonnet | 统一接口，模型丰富 |
| **MinerU** | mineru-ocr | 专业OCR平台，文档识别强 |

### 🏠 本地服务商（离线识别）
| 服务商 | 建议模型 | 特点 |
|--------|----------|------|
| **Ollama** | llava, llava:7b, bakllava | 🔒 **完全离线**，隐私保护，免费使用 |
| **LM Studio** | llava, llava-1.5-7b-hf | 🔒 **完全离线**，图形界面友好，OpenAI兼容 |


## 📋 关于 Umi-OCR

**Umi-OCR** 是一款免费、开源、可批量的离线OCR软件，基于 PaddleOCR 开发。它具有以下特点：

[![GitHub stars](https://img.shields.io/github/stars/hiroi-sora/Umi-OCR?style=social)](https://github.com/hiroi-sora/Umi-OCR)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/)
[![Multi-AI](https://img.shields.io/badge/AI-Multi--Provider-orange.svg)]()

- 🆓 **完全免费**：无需付费，无广告，开源软件
- 📱 **界面友好**：现代化的图形界面，操作简单直观
- 🔄 **批量处理**：支持批量图片OCR，提高工作效率
- 🌐 **多语言支持**：支持中文、英文、日文、韩文等多种语言
- 🔌 **插件系统**：支持扩展插件，功能可定制
- 💻 **跨平台**：支持Windows、Linux等操作系统

**项目地址**：[https://github.com/hiroi-sora/Umi-OCR](https://github.com/hiroi-sora/Umi-OCR)

## 🎯 插件特色

### 为什么选择多厂商 AI OCR 插件？

- **🎯 精度提升**：利用最先进的多模态AI模型
- **🌍 语言覆盖**：支持更多语言和复杂文档格式
- **🔄 完美集成**：无缝融入Umi-OCR工作流程
- **⚡ 灵活选择**：可根据需要在离线和云端OCR间切换
- **🏢 多厂商支持**：避免单一依赖，提供更多选择
- **🔒 隐私保护**：支持本地离线识别，数据不上传
- **💰 成本控制**：本地服务免费，云端服务按需选择

## 📊 对比识别效果

### 设置界面
![设置界面](docs/images/00.jpg)

### 识别图片："对于及其复杂的手写信息，也能完美识别"
![识别图片](docs/images/1.png)

### PaddleOCR识别效果，结果很差劲
![PaddleOCR识别效果，很差劲](docs/images/2.jpg)

### WechatOCR识别效果，结果很差劲
![WechatOCR识别效果，很差劲](docs/images/3.jpg)

### AI OCR识别效果，非常完美
![AI OCR识别效果，完美！](docs/images/4.jpg)

## ✨ 功能特点

| 功能 | 描述 |
|------|------|
| 🚀 **高精度识别** | 基于最新的AI视觉模型，支持多种语言文字识别 |
| 🌍 **多语言支持** | 支持中文、英文、日文、韩文、法文、德文、西班牙文、俄文、阿拉伯文等 |
| ⚡ **多厂商选择** | 支持OpenAI、Gemini、xAI、OpenRouter、硅基流动、豆包等多个服务商 |
| 📍 **坐标提取** | 可选择输出文字的位置坐标信息 |
| 🔧 **灵活配置** | 支持图像质量、尺寸、超时等多项参数调整 |
| 🌐 **代理支持** | 支持HTTP/SOCKS5代理，适应不同网络环境 |
| 🔄 **智能重试** | 自动重试机制，提高识别成功率 |
| 🚀 **并发处理** | 支持批量图片并发识别，提高处理效率 |

## 📦 安装要求

1. **Umi-OCR软件**：需要安装 [Umi-OCR](https://github.com/hiroi-sora/Umi-OCR) v2.0+
2. **AI服务API密钥**：需要获取对应服务商的API密钥
3. **网络连接**：需要能够访问对应的AI服务
4. **Python环境**：Umi-OCR内置Python环境即可

## 🛠️ 安装步骤

1. 下载本项目的所有文件
2. 将整个 `AIOCR` 文件夹复制到 Umi-OCR 的插件目录：
   ```
   UmiOCR-data/plugins/AIOCR/
   ```
3. 重启 Umi-OCR 软件
4. 在OCR引擎选择中找到 "AI OCR（云端）"


## ⚙️ 配置说明

### 全局配置

| 配置项 | 说明 | 推荐值 |
|--------|------|--------|
| **当前AI服务商** | 选择要使用的AI服务提供商 | 根据需求选择 |
| **各服务商API密钥** | 每个服务商的专用API密钥 | 一次配置，永久保存 |
| **各服务商模型** | 每个服务商的专用模型名称 | 预设推荐值，可自定义 |
| **请求超时** | API请求的超时时间 | 30秒 |
| **代理URL** | HTTP/SOCKS5代理设置 | 按需配置 |
| **最大并发数** | 批量处理时的并发数 | 3-5个 |

### 🆕 本地服务配置

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| **Ollama 服务地址** | Ollama本地服务地址 | http://localhost:11434/api |
| **LM Studio 服务地址** | LM Studio本地服务地址 | http://localhost:1234/v1 |
| **本地模型名称** | 已下载的视觉模型名称 | llava |

### 新版本特性

**🎉 一次配置，永久使用**：
- 现在可以同时配置所有服务商的API密钥和模型
- 切换服务商时无需重新输入配置
- 每个服务商都有独立的配置字段和分组
- 预设了推荐的模型名称，开箱即用

**📱 优化的界面布局**：
- **顶部区域**：当前AI服务商选择、请求超时设置
- **配置区域**：按服务商分组，每组包含API密钥和模型名称（预设最佳默认模型）
- **高级设置**：代理URL、最大并发数等高级选项
- **智能重试**：内置3次重试机制，无需手动配置

**📋 各服务商推荐模型**：

#### 🌐 云端服务商
| 服务商 | 推荐模型 | 特点 |
|--------|----------|------|
| **硅基流动** | `Qwen/Qwen2.5-VL-32B-Instruct` | 开源模型，价格低，准确率高 |
| **阿里云百炼** | `qwen-vl-plus-2025-08-15` | 专业OCR模型，中文识别优秀 |
| **智谱AI** | `glm-4.5v` | 国产大模型，多模态能力强 |
| **豆包** | `Doubao-1.5-vision-pro-32k` | 中文优化，性价比高 |
| **OpenAI** | `gpt-5-mini` | 高精度，多语言支持 |
| **Google Gemini** | `gemini-2.5-flash` | 速度快，成本低 |
| **xAI** | `grok-4` | 创新模型，独特优势 |
| **OpenRouter** | `anthropic/claude-3.5-sonnet` | 统一接口，模型丰富 |
| **MinerU** | `mineru-ocr` | 专业OCR平台，文档识别强 |

#### 🏠 本地服务商（离线识别）
| 服务商 | 推荐模型 | 特点 |
|--------|----------|------|
| **Ollama** | `llava`, `llava:7b`, `bakllava` | 🔒 完全离线，隐私保护，免费使用 |
| **LM Studio** | `llava`, `llava-1.5-7b-hf` | 🔒 完全离线，图形界面友好 |

### 局部配置

| 配置项 | 说明 | 选项 |
|--------|------|------|
| **识别语言** | 指定文字语言可提高识别精度 | 自动检测/中文/英文等 |
| **输出格式** | 识别结果的输出格式 | 仅文字/文字+坐标 |
| **图像质量** | 影响识别精度和传输速度 | 自动/高/中/低 |
| **最大图像尺寸** | 控制上传图像的大小 | 1024/2048/4096像素 |

## 🔑 API密钥获取

### 硅基流动 (SiliconFlow)
1. 访问 [硅基流动](https://cloud.siliconflow.cn/)
2. 注册账号并获取API密钥
3. 支持多种开源视觉模型

### 豆包 (Doubao)
1. 访问 [火山引擎](https://console.volcengine.com/ark/)
2. 开通豆包服务并获取API密钥
3. 字节跳动自研多模态模型

### OpenAI
1. 访问 [OpenAI Platform](https://platform.openai.com/api-keys)
2. 登录账号并创建API密钥
3. 复制生成的密钥

### Google Gemini
1. 访问 [Google AI Studio](https://aistudio.google.com/app/apikey)
2. 登录Google账号
3. 创建新的API密钥

### xAI Grok
1. 访问 [xAI Console](https://console.x.ai/)
2. 注册并获取API密钥

### 阿里云百炼 (Alibaba)
1. 访问 [阿里云百炼平台](https://bailian.console.aliyun.com/)
2. 开通百炼服务并获取API密钥
3. 支持通义千问系列视觉模型

### 智谱AI (ZhipuAI)
1. 访问 [智谱AI开放平台](https://open.bigmodel.cn/)
2. 注册账号并创建API密钥
3. 国产大模型，多模态能力强

### MinerU
1. 访问 [MinerU平台](https://mineru.net/)
2. 注册账号并获取API密钥
3. 专业OCR平台，文档识别能力强

### OpenRouter
1. 访问 [OpenRouter](https://openrouter.ai/keys)
2. 注册账号并创建API密钥

## 🏠 本地服务安装指南

### Ollama (完全离线)
1. **安装Ollama**：
   ```bash
   # Linux/macOS
   curl -fsSL https://ollama.ai/install.sh | sh
   
   # Windows
   # 从 https://ollama.ai 下载安装包
   ```

2. **下载视觉模型**：
   ```bash
   # 下载llava模型（推荐）
   ollama pull llava
   
   # 或下载其他视觉模型
   ollama pull llava:7b
   ollama pull bakllava
   ```

3. **启动服务**：
   ```bash
   ollama serve
   # 服务将在 http://localhost:11434 启动
   ```

4. **在插件中配置**：
   - 服务商：选择 "Ollama (本地)"
   - 模型：填入已下载的模型名（如 llava）
   - API密钥：留空即可

### LM Studio (图形界面)
1. **下载安装**：
   - 访问 [LM Studio官网](https://lmstudio.ai/)
   - 下载并安装适合您系统的版本

2. **下载模型**：
   - 在LM Studio中搜索并下载支持视觉的模型
   - 推荐：`llava-1.5-7b-hf`, `llava-1.6-34b-hf`

3. **启动本地服务器**：
   - 在LM Studio中点击"本地服务器"
   - 选择已下载的视觉模型
   - 启动服务器（默认端口1234）

4. **在插件中配置**：
   - 服务商：选择 "LM Studio (本地)"
   - 模型：填入LM Studio中加载的模型名
   - API密钥：留空或填入"not-needed"

### 🔒 本地服务优势
- **完全离线**：无需网络连接，数据不上传
- **隐私保护**：所有处理在本地完成
- **免费使用**：无API调用费用
- **自主控制**：可选择和定制模型



## 📖 使用方法

### 1. 配置插件

**首次配置（推荐一次性配置所有服务商）**：
1. 在Umi-OCR中选择 "AI OCR（云端）"
2. 在全局设置中配置所有你要使用的服务商：
   - 填写 OpenAI API密钥和模型（如需要）
   - 填写 Gemini API密钥和模型（如需要）
   - 填写其他服务商的配置（如需要）
3. 选择当前要使用的AI服务商并点击**应用修改**

**日常使用**：
- 只需在"当前AI服务商"下拉菜单中切换并点击**应用修改**即可
- 无需重新输入API密钥和模型
- 所有配置都会自动保存

### 2. 开始识别

- 使用截图OCR、批量OCR等功能
- 插件会自动调用对应的AI API进行识别
- 支持与本地OCR引擎混合使用

## ⚠️ 注意事项

1. **API成本**：AI API按使用量计费，请注意控制使用频率
2. **网络要求**：需要稳定的网络连接访问AI服务
3. **图像大小**：建议设置合适的最大图像尺寸以控制成本
4. **隐私安全**：图像会直接上传到服务商服务器进行处理，插件作者不会得到你的任何图片和信息
5. **速度限制**：云端API可能有速度限制，不适合大量并发请求
6. **模型选择**：不同模型的精度和成本不同，请根据需求选择

## 🔧 故障排除

### 常见问题

| 问题 | 可能原因 | 解决方案 |
|------|----------|----------|
| API密钥无效 | 密钥错误或过期 | 检查密钥是否正确，确认权限和配额 |
| 网络连接失败 | 网络问题 | 检查网络连接，尝试配置代理 |
| 识别结果为空 | 图像质量问题 | 检查图像清晰度，调整质量设置 |
| 请求超时 | 网络延迟 | 增加超时时间，减小图像尺寸 |
| 模型不存在 | 模型名称错误 | 检查模型名称是否正确 |
| 服务商不可用 | 服务商问题 | 尝试切换到其他服务商 |

### 错误代码说明

- `code: 100`：识别成功
- `code: 200`：识别失败，错误信息在data字段中

### 获取帮助

如遇到问题，请检查：
1. Umi-OCR版本是否兼容
2. API密钥是否有效
3. 网络连接是否正常
4. 插件文件是否完整
5. 模型名称是否正确
6. 服务商服务是否正常

## 🔗 开发资源

### 🛠️ 框架和工具
- **Umi-OCR项目**：[https://github.com/hiroi-sora/Umi-OCR](https://github.com/hiroi-sora/Umi-OCR)
- **插件开发文档**：[https://github.com/hiroi-sora/Umi-OCR_plugins](https://github.com/hiroi-sora/Umi-OCR_plugins)
- **Ollama官网**：[https://ollama.ai/](https://ollama.ai/)
- **LM Studio官网**：[https://lmstudio.ai/](https://lmstudio.ai/)

### 🌐 云端服务API文档
- **OpenAI API文档**：[https://platform.openai.com/docs](https://platform.openai.com/docs)
- **Google Gemini API文档**：[https://ai.google.dev/gemini-api/docs](https://ai.google.dev/gemini-api/docs)
- **xAI API文档**：[https://docs.x.ai/](https://docs.x.ai/)
- **OpenRouter API文档**：[https://openrouter.ai/docs](https://openrouter.ai/docs)
- **阿里云百炼 API文档**：[https://help.aliyun.com/zh/dashscope/](https://help.aliyun.com/zh/dashscope/)
- **智谱AI API文档**：[https://open.bigmodel.cn/dev/api](https://open.bigmodel.cn/dev/api)
- **MinerU API文档**：[https://mineru.net/apiManage/docs](https://mineru.net/apiManage/docs)

## 📝 版本历史
- **v2.4.0**：🚀 **重大更新** - 新增本地离线识别支持！添加Ollama、LM Studio本地服务商，新增MinerU云端服务商，完全离线OCR成为可能。优化识别文字对齐，现在识别后的文字与原图蚊子位置只有轻微偏移。
- **v2.3.0**：新增阿里云百炼和智谱AI支持，更新所有服务商默认模型，优化界面布局，移除重试次数配置（内置3次）
- **v2.2.0**：支持一次性配置所有服务商，切换时无需重新输入API密钥和模型
- **v2.1.0**：增加支持硅基流动、豆包视觉模型
- **v2.0.0**：重构为多厂商AI OCR插件，支持OpenAI、Gemini、xAI、OpenRouter
- **v1.2.0**：支持Gemini 2.5 Flash和Pro预览版模型，优化识别精度
- **v1.1.0**：增加多语言支持，优化错误处理
- **v1.0.0**：初始版本，支持Gemini OCR功能



## 🤝 贡献

欢迎提交Issue和Pull Request来改进这个插件！


## 💖 支持

如果这个插件对您有帮助，请考虑：

- 给项目点个星⭐
- 分享给更多需要的人
- 提供反馈和建议
- 参与项目贡献

---

**感谢使用 Umi-OCR 多厂商 AI OCR 插件！**
