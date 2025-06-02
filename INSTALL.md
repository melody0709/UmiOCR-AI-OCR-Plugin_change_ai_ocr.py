# Gemini OCR 插件安装说明

## API调用方式

本插件支持两种API调用方式：

1. **google-genai库**（推荐）：官方Python库，稳定性更好
2. **REST API**：直接HTTP请求，无需额外依赖

## 基本安装

### 插件目录包含以下文件：
- `__init__.py` - 插件入口文件
- `gemini_ocr.py` - 核心实现文件
- `gemini_ocr_config.py` - 配置文件
- `i18n.csv` - 多语言文件
- `README.md` - 说明文档
- `INSTALL.md` - 安装说明

## 推荐安装方式（google-genai库）

### 方法1：使用pip安装
```bash
pip install google-genai
```

### 方法2：在Umi-OCR环境中安装
如果您使用的是Umi-OCR的独立环境：

1. 找到Umi-OCR的Python环境路径
2. 使用该环境的pip安装：
```bash
# Windows示例
"C:\path\to\Umi-OCR\python\python.exe" -m pip install google-genai

# Linux/Mac示例
/path/to/Umi-OCR/python/bin/python -m pip install google-genai
```

### 方法3：离线安装
如果无法联网安装，可以：

1. 在有网络的环境下载依赖包：
```bash
pip download google-genai -d ./packages
```

2. 将下载的包复制到目标环境并安装：
```bash
pip install --no-index --find-links ./packages google-genai
```

## 备用方式（REST API）

如果无法安装google-genai库，插件会自动使用内置的REST API方式，无需额外安装。

## 验证安装

安装完成后，在Umi-OCR中：
1. 重启软件
2. 在OCR设置中选择"Gemini OCR（云端）"
3. 配置API密钥
4. 点击"测试连接"验证

## 常见问题

### Q: 提示"google-genai库未安装"
A: 按照上述方法安装google-genai库，或使用REST API模式

### Q: 安装后仍然无法使用
A: 检查Python环境路径是否正确，确保在正确的环境中安装了依赖

### Q: 网络连接问题
A: 配置代理设置，或检查防火墙设置