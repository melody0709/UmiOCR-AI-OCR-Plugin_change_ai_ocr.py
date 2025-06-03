#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gemini OCR插件测试脚本
用于测试Gemini OCR插件的功能
支持google-genai库和REST API两种方式
"""

import os
import sys
import base64
from PIL import Image
import io

# 添加插件目录到Python路径
plugin_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, plugin_dir)

# 检查google-genai库是否可用
try:
    import google.genai as genai
    import google.genai.types as types
    GENAI_AVAILABLE = True
    print("✓ google-genai库可用")
except ImportError:
    GENAI_AVAILABLE = False
    print("⚠ google-genai库不可用，将使用REST API")

# 导入插件模块
try:
    from gemini_ocr_config import globalOptions, localOptions
    from gemini_ocr import Api
except ImportError as e:
    print(f"导入插件模块失败: {e}")
    sys.exit(1)

def test_plugin():
    """测试插件功能"""
    print("=== Gemini OCR插件测试 ===")
    print(f"API库状态: {'google-genai库' if GENAI_AVAILABLE else 'REST API'}")
    
    # 获取API密钥
    api_key = input("\n请输入您的Gemini API密钥: ").strip()
    if not api_key:
        print("错误：API密钥不能为空")
        return False
    
    # 配置全局参数
    global_config = {
        'api_key': api_key,
        'model': 'gemini-1.5-flash',
        'timeout': 30,
        'max_retries': 3,
        'proxy_url': ''
    }
    
    # 配置本地参数
    local_config = {
        'language': 'auto',
        'output_format': 'text_only',
        'image_quality': 85,
        'max_image_size': 4194304
    }
    
    try:
        # 初始化API
        print("\n正在初始化Gemini OCR API...")
        api = Api(global_config)
        
        # 显示使用的API类型
        api_type = "google-genai库" if hasattr(api, 'use_genai') and api.use_genai else "REST API"
        print(f"✓ API初始化成功，使用: {api_type}")
        
        # 启动引擎
        result = api.start(local_config)
        if result:
            print(f"启动失败: {result}")
            return False
        
        # 测试图片路径
        while True:
            image_path = input("请输入测试图片路径（或输入'quit'退出）: ").strip()
            if image_path.lower() == 'quit':
                break
                
            if not os.path.exists(image_path):
                print("错误：图片文件不存在")
                continue
            
            print(f"正在识别图片: {image_path}")
            print("请稍候...")
            
            # 执行OCR
            result = api.runPath(image_path)
            
            # 显示结果
            print("\n=== 识别结果 ===")
            if result.get('code') == 100:
                data = result.get('data', [])
                if data:
                    print(f"识别到 {len(data)} 行文字:")
                    for i, item in enumerate(data, 1):
                        text = item.get('text', '')
                        print(f"{i}. {text}")
                else:
                    print("未识别到任何文字")
            else:
                error_msg = result.get('data', '未知错误')
                print(f"识别失败: {error_msg}")
            
            print("\n" + "="*50 + "\n")
        
        # 停止引擎
        api.stop()
        print("测试完成！")
        return True
        
    except Exception as e:
        print(f"测试过程中发生错误: {str(e)}")
        return False

def test_base64():
    """测试base64功能"""
    print("\n=== Base64 测试 ===")
    
    # 创建一个简单的测试图片（1x1像素的白色PNG）
    test_base64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=="
    
    api_key = input("请输入您的Gemini API密钥（用于base64测试）: ").strip()
    if not api_key:
        print("跳过base64测试")
        return
    
    global_config = {
        'api_key': api_key,
        'model': 'gemini-1.5-flash',
        'timeout': 30,
        'max_retries': 3,
        'proxy_url': ''
    }
    
    try:
        api = Api(global_config)
        api.start({})
        
        print("正在测试base64识别...")
        result = api.runBase64(test_base64)
        
        print("Base64测试结果:")
        print(f"Code: {result.get('code')}")
        print(f"Data: {result.get('data')}")
        
        api.stop()
        
    except Exception as e:
        print(f"Base64测试失败: {str(e)}")

def show_config_info():
    """显示配置信息"""
    print("=== 插件配置信息 ===")
    print("\n全局配置项:")
    for key, config in globalOptions.items():
        if isinstance(config, dict) and 'title' in config:
            print(f"  {key}: {config['title']}")
    
    print("\n局部配置项:")
    for key, config in localOptions.items():
        if isinstance(config, dict) and 'title' in config:
            print(f"  {key}: {config['title']}")
    print()

if __name__ == "__main__":
    show_config_info()
    
    choice = input("选择测试类型 (1: 图片路径测试, 2: Base64测试, 3: 两者都测试): ").strip()
    
    if choice in ['1', '3']:
        test_plugin()
    
    if choice in ['2', '3']:
        test_base64()
    
    print("\n测试脚本结束")