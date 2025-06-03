# Gemini OCR 插件安装指南

## 概述

Gemini OCR 插件支持两种API调用方式：
1. **google-genai库** (推荐) - 官方Python SDK，更稳定可靠
2. **REST API** (备用) - 直接HTTP请求，无需额外依赖

插件会自动检测并优先使用google-genai库，如果不可用则自动回退到REST API。

## 安装步骤

### 1. 基础安装

插件文件已经包含在 `UmiOCR-data/plugins/GeminiOCR/` 目录中，包括：
- `__init__.py` - 插件入口
- `gemini_ocr_config.py` - 配置选项
- `gemini_ocr.py` - 核心API实现
- `i18n.csv` - 多语言翻译
- `README.md` - 使用说明
- `test_plugin.py` - 测试脚本

### 2. 安装google-genai库 (推荐)

为了获得最佳性能和稳定性，建议安装官方的google-genai库：

#### 方法一：使用pip安装
```bash
pip install google-genai
```

#### 方法二：在Umi-OCR环境中安装
如果Umi-OCR使用独立的Python环境，需要在对应环境中安装：

1. 找到Umi-OCR的Python可执行文件
2. 使用该Python安装库：
```bash
# 示例路径，请根据实际情况调整
"C:\path\to\UmiOCR\python.exe" -m pip install google-genai
```

#### 方法三：离线安装
如果网络受限，可以下载whl文件离线安装：

1. 在有网络的环境下载：
```bash
pip download google-genai
```

2. 将下载的文件复制到目标环境并安装：
```bash
pip install google-genai-*.whl
```

### 3. 获取API密钥

1. 访问 [Google AI Studio](https://aistudio.google.com/app/apikey)
2. 登录Google账号
3. 创建新的API密钥
4. 复制API密钥备用

### 4. 配置插件

1. 重启Umi-OCR
2. 在OCR引擎选择中找到"Gemini OCR"
3. 在全局设置中输入API密钥
4. 根据需要调整其他参数

## 验证安装

### 使用测试脚本

运行测试脚本验证安装：
```bash
cd "C:\Users\Administrator\Desktop\项目代码\Umi-OCR_Paddle_v2.1.5\UmiOCR-data\plugins\GeminiOCR"
python test_plugin.py
```

测试脚本会：
1. 检测google-genai库是否可用
2. 提示输入API密钥
3. 测试OCR功能
4. 显示识别结果

### 检查API类型

插件启动时会显示使用的API类型：
- `✓ API初始化成功，使用: google-genai库` - 使用官方SDK
- `✓ API初始化成功，使用: REST API` - 使用HTTP请求

## 故障排除

### google-genai库安装失败

**问题**: pip install google-genai 失败

**解决方案**:
1. 更新pip: `pip install --upgrade pip`
2. 使用国内镜像: `pip install -i https://pypi.tuna.tsinghua.edu.cn/simple google-genai`
3. 检查Python版本兼容性 (需要Python 3.8+)

### API密钥无效

**问题**: 提示API密钥错误

**解决方案**:
1. 确认API密钥正确复制
2. 检查API密钥是否已激活
3. 确认账号有足够的配额

### 网络连接问题

**问题**: 无法连接到Gemini API

**解决方案**:
1. 检查网络连接
2. 配置代理设置
3. 确认防火墙设置

### 插件无法加载

**问题**: Umi-OCR中看不到Gemini OCR选项

**解决方案**:
1. 确认插件文件完整
2. 重启Umi-OCR
3. 检查Python路径设置

## 性能优化

### 推荐配置

- **模型选择**: gemini-1.5-flash (速度快，成本低)
- **图片质量**: 85 (平衡质量和大小)
- **最大图片尺寸**: 4MB (避免超时)
- **超时时间**: 30秒
- **重试次数**: 3次

### 网络优化

如果网络不稳定，可以：
1. 增加超时时间到60秒
2. 增加重试次数到5次
3. 配置稳定的代理服务器

## 更新说明

### v1.1.0 新特性
- 支持google-genai官方库
- 自动API类型检测和回退
- 改进的错误处理
- 更好的性能和稳定性

### 升级步骤
1. 备份现有配置
2. 替换插件文件
3. 安装google-genai库 (可选)
4. 重启Umi-OCR

## 技术支持

如果遇到问题，请提供以下信息：
1. 操作系统版本
2. Python版本
3. Umi-OCR版本
4. 错误信息截图
5. 测试脚本输出

---

**注意**: 使用Gemini API需要Google账号和有效的API密钥。请确保遵守Google的使用条款和配额限制。