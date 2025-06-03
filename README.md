# Gemini OCR Plugin for Umi-OCR

<div align="center">

![Gemini OCR Plugin](https://img.shields.io/badge/Gemini-OCR%20Plugin-blue?style=for-the-badge&logo=google)
![Umi-OCR](https://img.shields.io/badge/Umi--OCR-Compatible-green?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)

基于Google Gemini API的OCR插件，为Umi-OCR提供云端文字识别功能。

[安装指南](#安装步骤) • [配置说明](#配置说明) • [使用方法](#使用方法) • [故障排除](#故障排除)

</div>

## 关于 Umi-OCR

**Umi-OCR** 是一款免费、开源、可批量的离线OCR软件，支持截图OCR、批量OCR、PDF识别、二维码识别等功能。

- 🏠 **官方项目地址**：[hiroi-sora/Umi-OCR](https://github.com/hiroi-sora/Umi-OCR)
- 📖 **官方文档**：[Umi-OCR 使用文档](https://github.com/hiroi-sora/Umi-OCR/blob/main/docs/README.md)
- 💬 **官方QQ群**：735718516
- 🌟 **主要特点**：
  - 完全免费，无需联网
  - 支持多种OCR引擎
  - 批量处理能力强
  - 界面简洁易用
  - 支持插件扩展

本插件正是为Umi-OCR设计的云端OCR扩展，通过Google Gemini API提供更高精度的文字识别服务。

## 功能特点

- 🚀 **高精度识别**：基于Google最新的Gemini模型，支持多种语言文字识别
- 🌍 **多语言支持**：支持中文、英文、日文、韩文等多种语言
- ⚡ **多模型选择**：支持Gemini 1.5 Flash（快速）和Gemini 1.5 Pro（高精度）
- 📍 **坐标提取**：可选择输出文字的位置坐标信息
- 🔧 **灵活配置**：支持图像质量、尺寸、超时等多项参数调整
- 🌐 **代理支持**：支持HTTP/SOCKS5代理，适应不同网络环境
- 📝 **布局保持**：优化的文本解析逻辑，更好地保持原始文档结构

## 效果展示

### 识别效果对比

| 原图 | 识别结果 |
|------|----------|
| ![示例图片](https://via.placeholder.com/300x200/f0f0f0/333?text=原始图片) | ![识别结果](https://via.placeholder.com/300x200/e8f5e8/333?text=识别文本) |

### 坐标信息展示

```json
{
  "text": "识别的文字内容",
  "coordinates": {
    "x": 100,
    "y": 50,
    "width": 200,
    "height": 30
  }
}
```

## 安装要求

1. **Umi-OCR软件**：需要安装 [Umi-OCR](https://github.com/hiroi-sora/Umi-OCR) v2.0+
2. **Google Gemini API密钥**：需要在[Google AI Studio](https://aistudio.google.com/)获取API密钥
3. **网络连接**：需要能够访问Google API服务
4. **Python依赖**（可选）：推荐安装 `google-genai` 库以获得更好的稳定性

## 安装步骤

### 方法一：直接下载（推荐）

1. **下载插件**：
   ```bash
   git clone https://github.com/EatWorld/Umi-OCR-Gemini-Plugin.git
   ```
   或直接下载ZIP文件并解压

2. **复制到插件目录**：
   将所有文件复制到Umi-OCR的插件目录：
   ```
   UmiOCR-data/plugins/GeminiOCR/
   ```

3. **重启Umi-OCR**：重启软件以加载插件

4. **选择引擎**：在OCR引擎选择中找到"Gemini OCR（云端）"

### 方法二：手动安装

详细的手动安装步骤请参考 [INSTALL.md](./INSTALL.md) 文件。

## 配置说明

### 全局配置

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| **API密钥** | 在Google AI Studio获取的API密钥 | 空 |
| **模型选择** | gemini-1.5-flash（推荐）或 gemini-1.5-pro | gemini-1.5-flash |
| **请求超时** | API请求的超时时间（5-120秒） | 30秒 |
| **重试次数** | 请求失败时的重试次数（0-10次） | 3次 |
| **代理地址** | 可选的HTTP/SOCKS5代理设置 | 空 |

### 局部配置

| 配置项 | 说明 | 可选值 |
|--------|------|--------|
| **识别语言** | 指定文字语言可提高识别精度 | 自动检测、中文、英文等 |
| **输出格式** | 选择输出内容 | 仅文本、文字+坐标 |
| **图像质量** | 影响识别精度和传输速度 | 自动、高质量、中等、低质量 |
| **最大图像尺寸** | 控制上传图像的大小，影响API成本 | 2048像素 |

## 使用方法

### 1. 获取API密钥

<details>
<summary>点击展开详细步骤</summary>

1. 访问 [Google AI Studio](https://aistudio.google.com/)
2. 登录您的Google账户
3. 创建新项目或使用现有项目
4. 在API密钥页面生成新的API密钥
5. 复制API密钥备用

</details>

### 2. 配置插件

1. 在Umi-OCR中选择"Gemini OCR（云端）"
2. 在全局设置中输入API密钥
3. 根据需要调整其他参数
4. 点击"测试连接"验证配置

### 3. 开始识别

- **截图OCR**：使用快捷键截图并自动识别
- **批量OCR**：选择多个图片文件进行批量处理
- **PDF识别**：直接识别PDF文档中的文字

## 注意事项

> ⚠️ **重要提醒**

1. **API成本**：Gemini API按使用量计费，请注意控制使用频率
2. **网络要求**：需要稳定的网络连接访问Google服务
3. **图像大小**：建议设置合适的最大图像尺寸以控制成本
4. **隐私安全**：图像会上传到Google服务器进行处理
5. **速度限制**：云端API可能有速度限制，不适合大量并发请求

## 故障排除

### 常见问题

<details>
<summary>🔑 API密钥相关问题</summary>

**问题**：API密钥无效
- 检查密钥是否正确复制
- 确认API密钥权限和配额
- 验证Google AI Studio中的项目状态

</details>

<details>
<summary>🌐 网络连接问题</summary>

**问题**：网络连接失败
- 检查网络连接状态
- 尝试配置代理服务器
- 确认防火墙设置
- 测试是否能访问 `https://generativelanguage.googleapis.com`

</details>

<details>
<summary>📝 识别结果问题</summary>

**问题**：识别结果为空或不准确
- 检查图像是否包含清晰的文字
- 尝试调整图像质量设置
- 指定具体的识别语言
- 确保图像分辨率适中

</details>

<details>
<summary>⏱️ 性能问题</summary>

**问题**：请求超时或速度慢
- 增加超时时间设置
- 减小图像尺寸
- 检查网络速度
- 考虑使用代理服务器

</details>

### 错误代码说明

| 错误代码 | 说明 | 解决方案 |
|----------|------|----------|
| 400 | 请求参数错误 | 检查API密钥和请求格式 |
| 401 | 认证失败 | 验证API密钥是否正确 |
| 403 | 权限不足 | 检查API配额和权限 |
| 429 | 请求频率过高 | 降低请求频率或等待 |
| 500 | 服务器错误 | 稍后重试或联系支持 |

## 版本历史

### v1.0.0 (2024-06-03)
- ✨ 初始版本发布
- 🚀 支持基本的OCR识别功能
- 📍 支持坐标提取
- 🌍 支持多语言识别
- 🌐 支持代理配置
- 📝 增强文本布局保持功能

## 相关链接

- 🏠 [Umi-OCR 官方项目](https://github.com/hiroi-sora/Umi-OCR)
- 🔧 [Google AI Studio](https://aistudio.google.com/)
- 📚 [Gemini API 文档](https://ai.google.dev/docs)
- 💬 [Umi-OCR 官方QQ群](https://qm.qq.com/cgi-bin/qm/qr?k=XXX) (735718516)

## 许可证

本插件遵循 [MIT 许可证](./LICENSE)。详见LICENSE文件。

## 贡献

欢迎提交Issue和Pull Request来改进这个插件！

### 贡献指南

1. Fork 本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 支持

如果您在使用过程中遇到问题，请：

1. 📖 查看[故障排除](#故障排除)部分
2. 🐛 在GitHub上[提交Issue](https://github.com/EatWorld/Umi-OCR-Gemini-Plugin/issues)
3. 💬 访问[Umi-OCR官方社区](https://github.com/hiroi-sora/Umi-OCR)寻求帮助

---

<div align="center">

**如果这个插件对您有帮助，请给个 ⭐ Star 支持一下！**

 Made with ❤️ for [Umi-OCR](https://github.com/hiroi-sora/Umi-OCR) Community

</div>