#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# AI OCR Plugin Configuration

from plugin_i18n import Translator

tr = Translator(__file__, "i18n.csv")

# 服务商配置映射
PROVIDER_CONFIGS = {
    "openai": {
        "api_base": "https://api.openai.com/v1",
        "model": "",  # 用户自定义
    },
    "gemini": {
        "api_base": "https://generativelanguage.googleapis.com/v1beta",
        "model": "",  # 用户自定义
    },
    "xai": {
        "api_base": "https://api.x.ai/v1",
        "model": "",  # 用户自定义
    },
    "openrouter": {
        "api_base": "https://openrouter.ai/api/v1",
        "model": "",  # 用户自定义
    },
    "siliconflow": {
        "api_base": "https://api.siliconflow.cn/v1",
        "model": "",  # 用户自定义
    },

    "doubao": {
        "api_base": "https://ark.cn-beijing.volces.com/api/v3",
        "model": "",  # 用户自定义
    },
}

# 获取服务商默认配置的辅助函数
def get_provider_default_api_base(provider):
    """获取指定服务商的默认API基础URL"""
    return PROVIDER_CONFIGS.get(provider, {}).get("api_base", "")

def get_provider_default_model(provider):
    """获取指定服务商的默认模型（现在返回空字符串，让用户自己填写）"""
    return ""

def update_provider_config(provider):
    """当服务商切换时，更新相关配置项的默认值"""
    try:
        # 获取新服务商的默认配置
        default_api_base = get_provider_default_api_base(provider)
        default_model = get_provider_default_model(provider)
        
        # 这里需要通过Umi-OCR的配置系统来更新其他配置项
        # 由于QML配置系统的限制，我们通过返回值来提示用户
        import sys
        if hasattr(sys.modules.get('__main__'), 'qmlapp'):
            qmlapp = sys.modules['__main__'].qmlapp
            if hasattr(qmlapp, 'popup'):
                message = f"已切换到 {provider}\n\n建议配置：\nAPI基础URL: {default_api_base}\n模型: {default_model}"
                qmlapp.popup.simple("服务商已切换", message)
        
        return None  # 不阻止配置变更
    except Exception as e:
        print(f"更新服务商配置时出错: {e}")
        return None

# 全局配置项 - 新的配置结构，为每个服务商单独设置API密钥和模型

globalOptions = {
    "title": tr("AI OCR 设置"),
    "type": "group",

    # 使用 a_ 前缀确保基础设置排在最前面
    "a_provider": {
        "title": tr("当前AI服务商"),
        "default": "openai",
        "optionsList": [
            ["openai", "OpenAI"],
            ["gemini", "Google Gemini"],
            ["xai", "xAI Grok"],
            ["openrouter", "OpenRouter (Claude)"],
            ["siliconflow", "硅基流动 (SiliconFlow)"],
            ["doubao", "豆包 (Doubao)"],
            ["alibaba", "阿里云百炼 (Alibaba)"],
            ["zhipu", "智谱AI (ZhipuAI)"],
            ["mineru", "MinerU"],
            ["ollama", "Ollama (支持自定义地址)"],
            ["lmstudio", "LM Studio (支持自定义地址)"],
        ],
        "toolTip": tr("选择当前要使用的AI服务商。所有服务商的配置都会保存，切换时无需重新输入。"),
    },
    "a_timeout": {
        "title": tr("请求超时"),
        "default": 30,
        "min": 5,
        "max": 120,
        "unit": tr("秒"),
        "isInt": True,
        "toolTip": tr("API请求的超时时间。"),
    },

    # 阿里云百炼配置
    "alibaba_api_key": {
        "title": tr("阿里云百炼 API密钥"),
        "default": "",
        "type": "text",
        "toolTip": tr("请输入阿里云百炼的API密钥"),
    },
    "alibaba_model": {
        "title": tr("阿里云百炼 模型"),
        "default": "qwen-vl-plus-2025-08-15",
        "type": "text",
        "toolTip": tr("阿里云百炼模型名称，如：qwen-vl-plus-2025-08-15"),
    },

    # 豆包配置
    "doubao_api_key": {
        "title": tr("豆包 API密钥"),
        "default": "",
        "type": "text",
        "toolTip": tr("请输入豆包的API密钥"),
    },
    "doubao_model": {
        "title": tr("豆包 模型"),
        "default": "Doubao-1.5-vision-pro-32k",
        "type": "text",
        "toolTip": tr("豆包模型名称，如：Doubao-1.5-vision-pro-32k"),
    },

    # Google Gemini配置
    "gemini_api_key": {
        "title": tr("Gemini API密钥"),
        "default": "",
        "type": "text",
        "toolTip": tr("请输入Google Gemini的API密钥"),
    },
    "gemini_model": {
        "title": tr("Gemini 模型"),
        "default": "gemini-2.5-flash",
        "type": "text",
        "toolTip": tr("Gemini模型名称，如：gemini-2.5-flash, gemini-1.5-pro"),
    },

    # OpenAI配置
    "openai_api_key": {
        "title": tr("OpenAI API密钥"),
        "default": "",
        "type": "text",
        "toolTip": tr("请输入OpenAI的API密钥"),
    },
    "openai_model": {
        "title": tr("OpenAI 模型"),
        "default": "gpt-5-mini",
        "type": "text",
        "toolTip": tr("OpenAI模型名称，如：gpt-5-mini, gpt-4o"),
    },

    # OpenRouter配置
    "openrouter_api_key": {
        "title": tr("OpenRouter API密钥"),
        "default": "",
        "type": "text",
        "toolTip": tr("请输入OpenRouter的API密钥"),
    },
    "openrouter_model": {
        "title": tr("OpenRouter 模型"),
        "default": "anthropic/claude-3.5-sonnet",
        "type": "text",
        "toolTip": tr("OpenRouter模型名称，如：anthropic/claude-3.5-sonnet, google/gemini-pro-vision"),
    },

    # 硅基流动配置
    "siliconflow_api_key": {
        "title": tr("硅基流动 API密钥"),
        "default": "",
        "type": "text",
        "toolTip": tr("请输入硅基流动的API密钥"),
    },
    "siliconflow_model": {
        "title": tr("硅基流动 模型"),
        "default": "Qwen/Qwen2.5-VL-32B-Instruct",
        "type": "text",
        "toolTip": tr("硅基流动模型名称，如：Qwen/Qwen2.5-VL-32B-Instruct, Qwen/Qwen2.5-VL-72B-Instruct"),
    },

    # xAI配置
    "xai_api_key": {
        "title": tr("xAI API密钥"),
        "default": "",
        "type": "text",
        "toolTip": tr("请输入xAI的API密钥"),
    },
    "xai_model": {
        "title": tr("xAI 模型"),
        "default": "grok-4",
        "type": "text",
        "toolTip": tr("xAI模型名称，如：grok-4"),
    },

    # 智谱AI配置
    "zhipu_api_key": {
        "title": tr("智谱AI API密钥"),
        "default": "",
        "type": "text",
        "toolTip": tr("请输入智谱AI的API密钥"),
    },
    "zhipu_model": {
        "title": tr("智谱AI 模型"),
        "default": "glm-4.5v",
        "type": "text",
        "toolTip": tr("智谱AI模型名称，如：glm-4.5v"),
    },

    # LM Studio配置
    "lmstudio_api_base": {
        "title": tr("LM Studio API地址"),
        "default": "http://localhost:1234/v1",
        "type": "text",
        "toolTip": tr("LM Studio服务地址，如：http://localhost:1234/v1 或 http://192.168.1.100:1234/v1"),
    },
    "lmstudio_api_key": {
        "title": tr("LM Studio API密钥"),
        "default": "",
        "type": "text",
        "toolTip": tr("LM Studio本地API密钥（可选，本地服务通常不需要）"),
    },
    "lmstudio_model": {
        "title": tr("LM Studio 模型"),
        "default": "llava",
        "type": "text",
        "toolTip": tr("LM Studio模型名称，如：llava, llava-1.5-7b-hf"),
    },

    # MinerU配置
    "mineru_api_key": {
        "title": tr("MinerU API密钥"),
        "default": "",
        "type": "text",
        "toolTip": tr("请输入MinerU的API密钥"),
    },
    "mineru_model": {
        "title": tr("MinerU 模型"),
        "default": "mineru-extract",
        "type": "text",
        "toolTip": tr("MinerU模型名称（注意：MinerU主要用于PDF/文档解析，不支持直接图片OCR）"),
    },

    # Ollama配置
    "ollama_api_base": {
        "title": tr("Ollama API地址"),
        "default": "http://localhost:11434/api",
        "type": "text",
        "toolTip": tr("Ollama服务地址，如：http://localhost:11434/api 或 http://192.168.1.100:11434/api"),
    },
    "ollama_api_key": {
        "title": tr("Ollama API密钥"),
        "default": "",
        "type": "text",
        "toolTip": tr("Ollama本地API密钥（可选，本地服务通常不需要）"),
    },
    "ollama_model": {
        "title": tr("Ollama 模型"),
        "default": "llava",
        "type": "text",
        "toolTip": tr("Ollama模型名称，如：llava, llava:7b, bakllava"),
    },

    # 使用 z_ 前缀确保高级设置排在最后
    "z_proxy_url": {
        "title": tr("代理URL"),
        "default": "",
        "type": "text",
        "toolTip": tr("可选。格式：http://proxy:port 或 socks5://proxy:port"),
        "advanced": True,
    },
    "z_max_concurrent": {
        "title": tr("最大并发数"),
        "default": 3,
        "min": 1,
        "max": 10,
        "unit": tr("个"),
        "isInt": True,
        "toolTip": tr("批量处理时的最大并发请求数。"),
        "advanced": True,
    },
}

# 局部配置项
localOptions = {
    "title": tr("文字识别（AI OCR）"),
    "type": "group",
    
    "language": {
        "title": tr("识别语言"),
        "default": "auto",
        "optionsList": [
            ["auto", tr("自动检测")],
            ["zh", tr("中文")],
            ["en", tr("英文")],
            ["ja", tr("日文")],
            ["ko", tr("韩文")],
            ["fr", tr("法文")],
            ["de", tr("德文")],
            ["es", tr("西班牙文")],
            ["ru", tr("俄文")],
            ["ar", tr("阿拉伯文")],
        ],
        "toolTip": tr("指定要识别的文字语言。自动检测适用于大多数情况。"),
    },
    
    "output_format": {
        "title": tr("输出格式"),
        "default": "text_only",
        "optionsList": [
            ["text_only", tr("仅文字")],
            ["with_coordinates", tr("文字+坐标")],
        ],
        "toolTip": tr("选择OCR结果的输出格式。坐标信息可用于定位文字位置。"),
    },
    
    "image_quality": {
        "title": tr("图像质量"),
        "default": "auto",
        "optionsList": [
            ["auto", tr("自动")],
            ["high", tr("高质量")],
            ["medium", tr("中等质量")],
            ["low", tr("低质量")],
        ],
        "toolTip": tr("图像压缩质量。高质量可能提高识别精度但增加传输时间。"),
    },
    
    "max_image_size": {
        "title": tr("最大图像尺寸"),
        "default": 1536,
        "optionsList": [
            [2048, "2048px"],
            [1536, "1536px " + tr("（推荐）")],
            [1024, "1024px"],
            [512, "512px"],
        ],
        "toolTip": tr("图像的最大边长。过大的图像会被压缩以节省API调用成本。"),
    },
}