#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Gemini OCR Plugin Configuration

from plugin_i18n import Translator

tr = Translator(__file__, "i18n.csv")

# 测试连接回调函数
def test_connection_callback():
    """测试连接的回调函数"""
    try:
        from .gemini_ocr import Api
        # 这里需要获取当前配置的API密钥等信息
        # 由于配置系统的复杂性，暂时返回成功消息
        return {"code": 100, "data": "连接测试功能需要在实际使用时进行"}
    except Exception as e:
        return {"code": 102, "data": f"测试失败: {str(e)}"}

# 全局配置项
globalOptions = {
    "title": tr("Gemini OCR 设置"),
    "type": "group",
    
    "api_key": {
        "title": tr("API密钥"),
        "default": "",
        "type": "text",
        "toolTip": tr("请输入您的Google Gemini API密钥。可在Google AI Studio获取。"),
    },
    
    "model": {
        "title": tr("模型"),
        "default": "gemini-1.5-flash",
        "type": "text",
        "toolTip": tr("输入要使用的Gemini模型名称。常用模型：gemini-1.5-flash（推荐）、gemini-1.5-pro、gemini-pro-vision"),
    },
    
    "timeout": {
        "title": tr("请求超时"),
        "default": 30,
        "min": 5,
        "max": 120,
        "unit": tr("秒"),
        "isInt": True,
        "toolTip": tr("API请求的超时时间。"),
    },
    
    "max_retries": {
        "title": tr("最大重试次数"),
        "default": 3,
        "min": 0,
        "max": 10,
        "unit": tr("次"),
        "isInt": True,
        "toolTip": tr("请求失败时的最大重试次数。"),
    },
    
    "proxy_url": {
        "title": tr("代理URL"),
        "default": "",
        "type": "text",
        "toolTip": tr("可选。格式：http://proxy:port 或 socks5://proxy:port"),
    },
    
    # 注释掉测试连接按钮，避免QML onClicked处理问题
    # "test_connection": {
    #     "title": tr("连接测试"),
    #     "btnsList": [
    #         {"text": tr("测试连接"), "onClicked": test_connection_callback},
    #     ],
    # },
}

# 局部配置项
localOptions = {
    "title": tr("文字识别（Gemini OCR）"),
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
        "optionsList": [
            [2048, "2048px"],
            [1536, "1536px " + tr("（推荐）")],
            [1024, "1024px"],
            [512, "512px"],
        ],
        "toolTip": tr("图像的最大边长。过大的图像会被压缩以节省API调用成本。"),
    },
}