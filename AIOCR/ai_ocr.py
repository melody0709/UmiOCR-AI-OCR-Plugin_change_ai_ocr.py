# -*- coding: utf-8 -*-
# AI OCR API Implementation with Multi-Provider Support

import json
import base64
import time
import re
import threading
import concurrent.futures
from io import BytesIO
from PIL import Image
import urllib.request
import urllib.parse
import urllib.error
import os
import importlib.util
import sys
import types

# Provider基类
class BaseProvider:
    """AI OCR服务提供商基类"""
    
    def __init__(self, api_key, api_base=None, model=None, timeout=30, proxy_url=None):
        self.api_key = api_key
        self.api_base = api_base
        self.model = model
        self.timeout = timeout
        self.proxy_url = proxy_url
        
    def get_default_api_base(self):
        """获取默认API基础URL"""
        raise NotImplementedError
        
    def get_default_model(self):
        """获取默认模型"""
        raise NotImplementedError
        
    def build_headers(self):
        """构建请求头"""
        raise NotImplementedError
        
    def build_payload(self, image_base64, prompt):
        """构建请求载荷"""
        raise NotImplementedError
        
    def parse_response(self, response_text):
        """解析响应"""
        raise NotImplementedError

# OpenAI Provider
class OpenAIProvider(BaseProvider):
    """OpenAI服务提供商"""
    
    def get_default_api_base(self):
        return "https://api.openai.com/v1"
        
    def get_default_model(self):
        return "gpt-5-mini"
        
    def build_headers(self):
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
    def build_payload(self, image_base64, prompt):
        return {
            "model": self.model or self.get_default_model(),
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_base64}"
                            }
                        }
                    ]
                }
            ],
            "max_tokens": 4000
        }
        
    def parse_response(self, response_text):
        try:
            data = json.loads(response_text)
            if "choices" in data and len(data["choices"]) > 0:
                content = data["choices"][0]["message"]["content"]
                return content
            else:
                return None
        except Exception as e:
            raise Exception(f"解析OpenAI响应失败: {str(e)}")

# Google Gemini Provider
class GeminiProvider(BaseProvider):
    def get_default_api_base(self):
        return "https://generativelanguage.googleapis.com/v1beta"
        
    def get_default_model(self):
        return ""
        
    def build_headers(self):
        return {
            "Content-Type": "application/json"
        }
        
    def build_payload(self, image_base64, prompt):
        return {
            "contents": [{
                "parts": [
                    {"text": prompt},
                    {
                        "inline_data": {
                            "mime_type": "image/jpeg",
                            "data": image_base64
                        }
                    }
                ]
            }]
        }
        
    def parse_response(self, response_text):
        try:
            data = json.loads(response_text)
            if "candidates" in data and len(data["candidates"]) > 0:
                content = data["candidates"][0]["content"]["parts"][0]["text"]
                return content
            else:
                return None
        except Exception as e:
            raise Exception(f"解析Gemini响应失败: {str(e)}")

# 硅基流动 Provider
class SiliconFlowProvider(BaseProvider):
    """硅基流动服务提供商"""
    
    def get_default_api_base(self):
        return "https://api.siliconflow.cn/v1"
        
    def get_default_model(self):
        return ""
        
    def build_headers(self):
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
    def build_payload(self, image_base64, prompt):
        return {
            "model": self.model or self.get_default_model(),
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_base64}"
                            }
                        }
                    ]
                }
            ],
            "max_tokens": 4000,
            "thinking": {
                "type": "disabled"
            }
        }
        
    def parse_response(self, response_text):
        try:
            data = json.loads(response_text)
            if "choices" in data and len(data["choices"]) > 0:
                content = data["choices"][0]["message"]["content"]
                return content
            else:
                return None
        except Exception as e:
            raise Exception(f"解析硅基流动响应失败: {str(e)}")

# 阿里云百炼模型（千问）Provider
# 阿里云百炼 Provider
class AlibabaProvider(BaseProvider):
    """阿里云百炼服务提供商"""
    
    def get_default_api_base(self):
        return "https://dashscope.aliyuncs.com/api/v1"
        
    def get_default_model(self):
        return ""
        
    def build_headers(self):
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
    def build_payload(self, image_base64, prompt):
        return {
            "model": self.model or self.get_default_model(),
            "input": {
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {"text": prompt},
                            {
                                "image": f"data:image/jpeg;base64,{image_base64}"
                            }
                        ]
                    }
                ]
            }
        }
        
    def parse_response(self, response_text):
        try:
            data = json.loads(response_text)
            # 阿里云百炼的响应格式
            if "output" in data:
                if "choices" in data["output"] and len(data["output"]["choices"]) > 0:
                    # 新版本API格式
                    content = data["output"]["choices"][0]["message"]["content"]
                    return self._extract_text_from_content(content)
                elif "text" in data["output"]:
                    # 旧版本API格式
                    content = data["output"]["text"]
                    return self._extract_text_from_content(content)
            return None
        except Exception as e:
            raise Exception(f"解析阿里云百炼响应失败: {str(e)}")
    
    def _extract_text_from_content(self, content):
        """从content中提取文本内容"""
        if content is None:
            return None
            
        # 如果是字符串，直接返回
        if isinstance(content, str):
            return content
            
        # 如果是列表，处理每个元素
        if isinstance(content, list):
            text_parts = []
            for item in content:
                if isinstance(item, str):
                    text_parts.append(item)
                elif isinstance(item, dict) and "text" in item:
                    text_parts.append(item["text"])
                elif isinstance(item, dict) and "content" in item:
                    text_parts.append(str(item["content"]))
                else:
                    # 如果是其他类型，尝试转换为字符串
                    text_parts.append(str(item))
            return ' '.join(text_parts)
            
        # 如果是字典，尝试提取文本字段
        if isinstance(content, dict):
            if "text" in content:
                return content["text"]
            elif "content" in content:
                return str(content["content"])
            else:
                # 如果没有明确的文本字段，返回整个字典的字符串表示
                return str(content)
                
        # 其他类型，转换为字符串
        return str(content)

# 豆包 Provider
class DoubaoProvider(BaseProvider):
    """豆包服务提供商"""
    
    def get_default_api_base(self):
        return "https://ark.cn-beijing.volces.com/api/v3"
        
    def get_default_model(self):
        return ""
        
    def build_headers(self):
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
    def build_payload(self, image_base64, prompt):
        return {
            "model": self.model or self.get_default_model(),
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_base64}"
                            }
                        }
                    ]
                }
            ],
            "max_tokens": 5000,
            # 添加思考模式配置，默认禁用深度思考
            "thinking": {
                "type": "disabled"
            }
        }
        
    def parse_response(self, response_text):
        try:
            data = json.loads(response_text)
            if "choices" in data and len(data["choices"]) > 0:
                content = data["choices"][0]["message"]["content"]
                return content
            else:
                return None
        except Exception as e:
            raise Exception(f"解析豆包响应失败: {str(e)}")

# OpenRouter Provider
class OpenRouterProvider(BaseProvider):
    def get_default_api_base(self):
        return "https://openrouter.ai/api/v1"
        
    def get_default_model(self):
        return ""
        
    def build_headers(self):
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "https://github.com/hiroi-sora/Umi-OCR",
            "X-Title": "Umi-OCR AI Plugin"
        }
        
    def build_payload(self, image_base64, prompt):
        return {
            "model": self.model or self.get_default_model(),
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_base64}"
                            }
                        }
                    ]
                }
            ]
        }
        
    def parse_response(self, response_text):
        try:
            data = json.loads(response_text)
            if "choices" in data and len(data["choices"]) > 0:
                content = data["choices"][0]["message"]["content"]
                return content
            else:
                return None
        except Exception as e:
            raise Exception(f"解析OpenRouter响应失败: {str(e)}")

# xAI Grok Provider
class XAIProvider(BaseProvider):
    def get_default_api_base(self):
        return "https://api.x.ai/v1"
        
    def get_default_model(self):
        return ""
        
    def build_headers(self):
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
    def build_payload(self, image_base64, prompt):
        return {
            "model": self.model or self.get_default_model(),
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_base64}"
                            }
                        }
                    ]
                }
            ]
        }
        
    def parse_response(self, response_text):
        try:
            data = json.loads(response_text)
            if "choices" in data and len(data["choices"]) > 0:
                content = data["choices"][0]["message"]["content"]
                return content
            else:
                return None
        except Exception as e:
            raise Exception(f"解析xAI响应失败: {str(e)}")

# 智谱AI Provider
class ZhipuProvider(BaseProvider):
    """智谱AI服务提供商"""

    def get_default_api_base(self):
        return "https://open.bigmodel.cn/api/paas/v4"

    def get_default_model(self):
        return ""
        
    def build_headers(self):
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
    def build_payload(self, image_base64, prompt):
        return {
            "model": self.model or self.get_default_model(),
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_base64}"
                            }
                        }
                    ]
                }
            ],
            "max_tokens": 4000,
            "thinking": {
                "type": "disabled"
            }
        }
        
    def parse_response(self, response_text):
        try:
            data = json.loads(response_text)
            if "choices" in data and len(data["choices"]) > 0:
                content = data["choices"][0]["message"]["content"]
                return content
            else:
                return None
        except Exception as e:
            raise Exception(f"解析智谱AI响应失败: {str(e)}")

# 新增：魔搭 Provider
class ModelScopeProvider(BaseProvider):
    """魔搭服务提供商"""

    def get_default_api_base(self):
        return "https://api-inference.modelscope.cn/v1"

    def get_default_model(self):
        return ""

    def build_headers(self):
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

    def build_payload(self, image_base64, prompt):
        return {
            "model": self.model or self.get_default_model(),
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_base64}"
                            }
                        }
                    ]
                }
            ],
            "max_tokens": 4000,
            "thinking": {
                "type": "disabled"
            }
        }

    def parse_response(self, response_text):
        try:
            data = json.loads(response_text)
            if "choices" in data and len(data["choices"]) > 0:
                content = data["choices"][0]["message"]["content"]
                return content
            else:
                return None
        except Exception as e:
            raise Exception(f"解析魔搭响应失败: {str(e)}")

# Ollama Provider (本地)
class OllamaProvider(BaseProvider):
    """Ollama本地服务提供商"""
    
    def get_default_api_base(self):
        return "http://localhost:11434/api"
        
    def get_default_model(self):
        return ""
        
    def build_headers(self):
        return {
            "Content-Type": "application/json"
        }
        
    def build_payload(self, image_base64, prompt):
        return {
            "model": self.model or self.get_default_model(),
            "prompt": prompt,
            "images": [image_base64],
            "stream": False
        }
        
    def parse_response(self, response_text):
        try:
            data = json.loads(response_text)
            if "response" in data:
                content = data["response"]
                return content
            else:
                return None
        except Exception as e:
            raise Exception(f"解析Ollama响应失败: {str(e)}")

# LM Studio Provider (本地)
class LMStudioProvider(BaseProvider):
    """LM Studio本地服务提供商"""
    
    def get_default_api_base(self):
        return "http://localhost:1234/v1"
        
    def get_default_model(self):
        return ""
        
    def build_headers(self):
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}" if self.api_key else "Bearer not-needed"
        }
        
    def build_payload(self, image_base64, prompt):
        return {
            "model": self.model or self.get_default_model(),
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_base64}"
                            }
                        }
                    ]
                }
            ],
            "max_tokens": 4000
        }
        
    def parse_response(self, response_text):
        try:
            data = json.loads(response_text)
            if "choices" in data and len(data["choices"]) > 0:
                content = data["choices"][0]["message"]["content"]
                return content
            else:
                return None
        except Exception as e:
            raise Exception(f"解析LM Studio响应失败: {str(e)}")


# Groq Provider
class GroqProvider(BaseProvider):
    """Groq服务提供商"""

    def get_default_api_base(self):
        return "https://api.groq.com/openai/v1"

    def get_default_model(self):
        # 1. 更换为支持图像的模型
        return "meta-llama/llama-4-scout-17b-16e-instruct"

    def build_headers(self):
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

    def build_payload(self, image_base64, prompt):
        # 2. 增加图像大小检查，符合Groq的4MB限制
        # base64编码后大小 = 原始二进制大小 * 1.333，因此原始大小上限为4MB / 1.333 ≈ 3MB
        max_base64_size = 4 * 1024 * 1024  # 4MB
        if len(image_base64) > max_base64_size:
            raise Exception("图像过大，Groq API要求base64编码图像不超过4MB")

        return {
            "model": self.model or self.get_default_model(),
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_base64}"
                            }
                        }
                    ]
                }
            ],
            "max_completion_tokens": 5000,
            "temperature": 0.2  # 3. 增加温度参数，提高稳定性
        }

    def parse_response(self, response_text):
        try:
            # 4. 增加响应内容检查
            if not response_text.strip():
                raise Exception("收到空响应")

            data = json.loads(response_text)

            # 5. 更详细的错误处理
            if "error" in data:
                raise Exception(f"API错误: {data['error'].get('message', str(data['error']))}")

            if "choices" in data and len(data["choices"]) > 0:
                content = data["choices"][0]["message"]["content"]
                return content
            else:
                return None
        except json.JSONDecodeError as e:
            # 6. 提供更详细的解析错误信息
            raise Exception(f"解析Groq响应失败: 无效的JSON格式。响应内容: {response_text[:100]}... 错误: {str(e)}")
        except Exception as e:
            raise Exception(f"解析Groq响应失败: {str(e)}")


# 无问芯穷 Provider
class InfinigenceProvider(BaseProvider):
    """无问芯穷服务提供商"""

    def get_default_api_base(self):
        return "https://cloud.infini-ai.com/maas/v1"

    def get_default_model(self):
        return ""

    def build_headers(self):
        return {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
            "Authorization": f"Bearer {self.api_key}"
        }

    def build_payload(self, image_base64, prompt):
        return {
            "model": self.model or self.get_default_model(),
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_base64}"
                            }
                        }
                    ]
                }
            ],
            "stream": False,
            "enable_thinking": False,
            "temperature": 0.7,
            "max_tokens": 5000
        }

    def parse_response(self, response_text):
        try:
            data = json.loads(response_text)
            if "choices" in data and len(data["choices"]) > 0:
                content = data["choices"][0]["message"]["content"]
                return content
            else:
                return None
        except Exception as e:
            raise Exception(f"解析无问芯穷响应失败: {str(e)}")


# Mistral Provider
class MistralProvider(BaseProvider):
    """Mistral AI服务提供商 (使用视觉模型)"""

    def get_default_api_base(self):
        return "https://api.mistral.ai/v1"

    def get_default_model(self):
        return "pixtral-12b-2409"  # 默认使用视觉模型

    def build_headers(self):
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

    def build_payload(self, image_base64, prompt):
        # 结构与OpenAI视觉模型完全兼容
        return {
            "model": self.model or self.get_default_model(),
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_base64}"
                            }
                        }
                    ]
                }
            ],
            "max_tokens": 5000,
            "stream": False  # 关键修复：明确禁用流式响应
        }

    def parse_response(self, response_text):
        # 响应格式与OpenAI视觉模型完全兼容
        # 增加健壮性：先检查响应是否为空
        if not response_text or not response_text.strip():
            raise Exception("解析Mistral响应失败: 服务器返回了空响应。")

        try:
            data = json.loads(response_text)
            if "choices" in data and len(data["choices"]) > 0:
                # 检查 content 是否为 None
                message = data["choices"][0].get("message", {})
                content = message.get("content")
                if content is not None:
                    return content
                else:
                    # 如果 content 为 null，则返回空结果而不是报错
                    return ""
            else:
                # 如果响应中没有 choices，检查是否有 error 字段
                if "error" in data:
                    error_msg = data["error"].get("message", str(data["error"]))
                    raise Exception(f"API返回错误: {error_msg}")
                return None
        except json.JSONDecodeError:
            # 关键调试优化：在JSON解析失败时，打印出服务器返回的原始内容（截取前500个字符）
            raise Exception(f"解析Mistral响应失败: 无效的JSON格式。服务器返回内容: {response_text[:500]}")
        except Exception as e:
            raise Exception(f"解析Mistral响应失败: {str(e)}")


# 书生AI Provider
"""书生AI服务提供商"""
class InternProvider(BaseProvider):
    """书生AI服务提供商"""

    def get_default_api_base(self):
        return "https://chat.intern-ai.org.cn/api/v1"

    def get_default_model(self):
        return "internvl3.5-241b-a28b"  # 默认使用多模态模型

    def build_headers(self):
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

    def build_payload(self, image_base64, prompt):
        payload = {
            "model": self.model or self.get_default_model(),
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_base64}"
                            }
                        }
                    ]
                }
            ],
            "max_tokens": 5000,
            "stream": False,  # 禁用流式响应
            "thinking_mode": False
        }

        # 对于intern-s1和intern-s1-mini模型，添加thinking_mode参数
        model = self.model or self.get_default_model()
        if model in ["intern-s1", "intern-s1-mini"]:
            # 可以根据需要设置为True或False，这里默认禁用
            payload["thinking_mode"] = False

        return payload

    def parse_response(self, response_text):
        try:
            # 检查响应是否为空
            if not response_text or not response_text.strip():
                raise Exception("服务器返回了空响应")

            data = json.loads(response_text)

            # 检查是否有错误信息
            if "error" in data:
                error_msg = data["error"].get("message", str(data["error"]))
                raise Exception(f"API错误: {error_msg}")

            if "choices" in data and len(data["choices"]) > 0:
                content = data["choices"][0]["message"]["content"]
                return content
            else:
                return None
        except json.JSONDecodeError:
            raise Exception(f"解析书生AI响应失败: 无效的JSON格式。服务器返回内容: {response_text[:500]}")
        except Exception as e:
            raise Exception(f"解析书生AI响应失败: {str(e)}")


# Provider工厂
class ProviderFactory:
    @staticmethod
    def create_provider(provider_name, api_key, api_base=None, model=None, timeout=30, proxy_url=None):
        providers = {
            "openai": OpenAIProvider,
            "gemini": GeminiProvider,
            "xai": XAIProvider,
            "openrouter": OpenRouterProvider,
            "siliconflow": SiliconFlowProvider,
            "doubao": DoubaoProvider,
            "alibaba": AlibabaProvider,
            "zhipu": ZhipuProvider,
            "ollama": OllamaProvider,
            "lmstudio": LMStudioProvider,
            "groq": GroqProvider,
            "infinigence": InfinigenceProvider,
            "mistral": MistralProvider,
            "modelscope": ModelScopeProvider,  # 新增：魔搭 Provider
            "intern": InternProvider,  # 新增：书生AI Provider

        }
        
        if provider_name not in providers:
            raise ValueError(f"不支持的服务提供商: {provider_name}")
        
        provider_class = providers[provider_name]
        
        # 如果没有提供api_base，使用内置的默认值
        if api_base is None:
            temp_provider = provider_class(api_key)
            api_base = temp_provider.get_default_api_base()
        
        # 模型由用户在配置中指定，不使用默认值
        if not model:
            raise ValueError(f"请在配置中指定 {provider_name} 的模型名称")
            
        return provider_class(api_key, api_base, model, timeout, proxy_url)

# HTTP请求工具类
class HTTPClient:
    def __init__(self, timeout=30, proxy_url=None):
        self.timeout = timeout
        self.proxy_url = proxy_url
    
    def post_multipart(self, url, headers=None, files=None, data=None):
        """发送 multipart/form-data POST请求（用于文件上传）"""
        import uuid
        import mimetypes
        
        try:
            # 生成边界字符串
            boundary = f"----WebKitFormBoundary{uuid.uuid4().hex}"
            boundary_bytes = boundary.encode('utf-8')
            
            # 构建 multipart/form-data 内容
            body_parts = []
            
            # 添加普通字段
            if data:
                for key, value in data.items():
                    part = b'--' + boundary_bytes + b'\r\n'
                    part += f'Content-Disposition: form-data; name="{key}"\r\n'.encode('utf-8')
                    part += b'\r\n'
                    part += str(value).encode('utf-8') + b'\r\n'
                    body_parts.append(part)
            
            # 添加文件字段
            if files:
                for field_name, file_data in files.items():
                    if isinstance(file_data, dict):
                        filename = file_data.get('filename', 'image.jpg')
                        content = file_data.get('content', b'')
                        content_type = file_data.get('content_type', 'image/jpeg')
                    else:
                        filename = 'image.jpg'
                        content = file_data
                        content_type = 'image/jpeg'
                    
                    part = b'--' + boundary_bytes + b'\r\n'
                    part += f'Content-Disposition: form-data; name="{field_name}"; filename="{filename}"\r\n'.encode('utf-8')
                    part += f'Content-Type: {content_type}\r\n'.encode('utf-8')
                    part += b'\r\n'
                    
                    # 确保内容是字节类型
                    if isinstance(content, str):
                        content = content.encode('utf-8')
                    elif isinstance(content, bytes):
                        pass  # 已经是字节类型
                    else:
                        content = str(content).encode('utf-8')
                    
                    part += content + b'\r\n'
                    body_parts.append(part)
            
            # 结束边界
            end_boundary = b'--' + boundary_bytes + b'--\r\n'
            body_parts.append(end_boundary)
            
            # 组装请求体
            body_bytes = b''.join(body_parts)
            
            # 设置请求头
            default_headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'application/json, text/plain, */*',
                'Content-Type': f'multipart/form-data; boundary={boundary}',
                'Content-Length': str(len(body_bytes))
            }
            
            if headers:
                # 不覆盖 Content-Type，因为 multipart 需要特定格式
                for key, value in headers.items():
                    if key.lower() != 'content-type':
                        default_headers[key] = value
            
            # 创建请求
            req = urllib.request.Request(url, data=body_bytes, headers=default_headers)
            
            # 创建 SSL 上下文
            import ssl
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            # 设置代理和 SSL
            if self.proxy_url:
                proxy_handler = urllib.request.ProxyHandler({
                    'http': self.proxy_url, 
                    'https': self.proxy_url
                })
                https_handler = urllib.request.HTTPSHandler(context=ssl_context)
                opener = urllib.request.build_opener(proxy_handler, https_handler)
            else:
                https_handler = urllib.request.HTTPSHandler(context=ssl_context)
                opener = urllib.request.build_opener(https_handler)
            
            # 发送请求
            response = opener.open(req, timeout=self.timeout)
            response_data = response.read()
            
            # 处理响应
            try:
                response_text = response_data.decode('utf-8')
            except UnicodeDecodeError:
                response_text = response_data.decode('utf-8', errors='ignore')
            
            return {
                'status_code': response.getcode(),
                'text': response_text
            }
            
        except urllib.error.HTTPError as e:
            error_data = e.read()
            try:
                error_text = error_data.decode('utf-8')
            except UnicodeDecodeError:
                error_text = error_data.decode('utf-8', errors='ignore')
            
            return {
                'status_code': e.code,
                'text': error_text
            }
        except Exception as e:
            raise Exception(f"Multipart HTTP请求失败: {str(e)}")
    
    def post(self, url, headers=None, data=None):
        """发送POST请求"""
        try:
            # 设置默认请求头
            try:
                import brotli  # 检测是否可用
                accept_encoding = 'gzip, deflate, br'
            except Exception:
                accept_encoding = 'gzip, deflate'
            default_headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'application/json, text/plain, */*',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': accept_encoding,
                'Connection': 'keep-alive',
                'Cache-Control': 'no-cache'
            }
            
            # 合并请求头
            if headers:
                default_headers.update(headers)
            
            # 准备请求数据
            req_data = data.encode('utf-8') if isinstance(data, str) else data
            req = urllib.request.Request(url, data=req_data, headers=default_headers)
            
            # 创建 SSL 上下文
            import ssl
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            # 设置代理和 SSL
            if self.proxy_url:
                proxy_handler = urllib.request.ProxyHandler({
                    'http': self.proxy_url, 
                    'https': self.proxy_url
                })
                https_handler = urllib.request.HTTPSHandler(context=ssl_context)
                opener = urllib.request.build_opener(proxy_handler, https_handler)
            else:
                https_handler = urllib.request.HTTPSHandler(context=ssl_context)
                opener = urllib.request.build_opener(https_handler)
            
            # 发送请求
            response = opener.open(req, timeout=self.timeout)
            response_data = response.read()
            
            # 处理压缩响应
            content_encoding = response.headers.get('Content-Encoding', '').lower()
            if content_encoding == 'gzip':
                import gzip
                response_data = gzip.decompress(response_data)
            elif content_encoding == 'deflate':
                import zlib
                response_data = zlib.decompress(response_data)
            elif content_encoding == 'br':
                # 尝试Brotli解压，未安装brotli库时忽略
                try:
                    import brotli
                    response_data = brotli.decompress(response_data)
                except Exception:
                    pass
            
            # 处理编码
            try:
                response_text = response_data.decode('utf-8')
            except UnicodeDecodeError:
                try:
                    response_text = response_data.decode('latin-1')
                except UnicodeDecodeError:
                    response_text = response_data.decode('utf-8', errors='ignore')
            
            return {
                'status_code': response.getcode(),
                'text': response_text
            }
        except urllib.error.HTTPError as e:
            error_data = e.read()
            
            # 处理错误响应的压缩
            content_encoding = e.headers.get('Content-Encoding', '').lower() if hasattr(e, 'headers') else ''
            if content_encoding == 'gzip':
                import gzip
                try:
                    error_data = gzip.decompress(error_data)
                except:
                    pass
            elif content_encoding == 'deflate':
                import zlib
                try:
                    error_data = zlib.decompress(error_data)
                except:
                    pass
            elif content_encoding == 'br':
                try:
                    import brotli
                    error_data = brotli.decompress(error_data)
                except Exception:
                    pass
            
            try:
                error_text = error_data.decode('utf-8')
            except UnicodeDecodeError:
                try:
                    error_text = error_data.decode('latin-1')
                except UnicodeDecodeError:
                    error_text = error_data.decode('utf-8', errors='ignore')
            
            return {
                'status_code': e.code,
                'text': error_text
            }
        except Exception as e:
            raise Exception(f"HTTP请求失败: {str(e)}")

# 主API类
class Api:
    def __init__(self, globalArgd):
        self.provider = None
        self.http_client = None
        # 兼容新旧键名
        self.max_concurrent = globalArgd.get("z_max_concurrent", globalArgd.get("max_concurrent", 3))
        self.executor = None
        
        # 保存全局配置
        self.global_config = globalArgd
        
        # 添加图像尺寸追踪变量
        self.original_size = None  # 保存原始图像尺寸
        self.processed_size = None # 保存预处理后的图像尺寸
        self.scale_ratio = 1.0     # 保存缩放比例
        # 检测-识别双通道：PaddleOCR 检测器句柄
        self.detector = None
        
        # 兼容新旧键名：a_provider 或 provider
        provider = self.global_config.get('a_provider') or self.global_config.get('provider')
        if not provider:
            provider = 'openai'
            self.global_config['a_provider'] = provider
        self.global_config['provider'] = provider  # 保持向后兼容
        
        print(f"AI OCR 插件初始化完成，当前服务商: {provider}")
        
    def start(self, argd):
        """启动API"""
        try:
            # 获取配置（兼容新旧键名）
            provider_name = self.global_config.get("a_provider", self.global_config.get("provider", "openai"))
            
            # 根据选择的服务商获取对应的API密钥和模型
            api_key = self.global_config.get(f"{provider_name}_api_key", "")
            model = self.global_config.get(f"{provider_name}_model", "")
            
            # 获取自定义 API 地址（如果有的话）
            api_base = self.global_config.get(f"{provider_name}_api_base", "")
            
            # 兼容新旧键名
            timeout = self.global_config.get("a_timeout", self.global_config.get("timeout", 30))
            proxy_url = self.global_config.get("z_proxy_url", self.global_config.get("proxy_url", ""))
            
            # 对于本地服务（Ollama、LM Studio），API密钥可以为空
            if not api_key and provider_name not in ["ollama", "lmstudio"]:
                return f"[Error] {provider_name} 的API密钥不能为空，请在设置中配置"
            
            if not model:
                return f"[Error] {provider_name} 的模型不能为空，请在设置中配置"
            
            # 创建Provider，如果用户配置了自定义API地址则使用，否则使用默认值
            self.provider = ProviderFactory.create_provider(
                provider_name, api_key, api_base if api_base else None, model, timeout, proxy_url
            )
            
            # 创建HTTP客户端
            self.http_client = HTTPClient(timeout, proxy_url)
            
            # 创建线程池
            self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=self.max_concurrent)
            
            # 保存局部配置
            self.local_config = argd
            
            return ""
        except Exception as e:
            return f"[Error] 启动失败: {str(e)}"
    
    def stop(self):
        """停止API"""
        if self.executor:
            self.executor.shutdown(wait=True)
            self.executor = None
        # 关闭 PaddleOCR 检测器（若存在）
        try:
            if hasattr(self, 'detector') and self.detector and hasattr(self.detector, 'stop'):
                self.detector.stop()
        except Exception:
            pass
    
    def testConnection(self):
        """测试连接"""
        try:
            # 创建一个简单的测试图像
            test_image = Image.new('RGB', (100, 50), color='white')
            buffer = BytesIO()
            test_image.save(buffer, format='JPEG')
            test_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
            
            # 发送测试请求
            result = self._run_ocr(test_base64, {"output_format": "text_only"})
            
            if result["code"] == 100 or result["code"] == 101:
                return {"code": 100, "data": "连接测试成功"}
            else:
                return {"code": 102, "data": result["data"]}
        except Exception as e:
            return {"code": 102, "data": f"连接测试失败: {str(e)}"}
    
    def runPath(self, imgPath: str):
        """处理图片路径"""
        try:
            with open(imgPath, 'rb') as f:
                image_bytes = f.read()
            return self.runBytes(image_bytes)
        except Exception as e:
            return self._create_error_result(f"读取图片失败: {str(e)}")
    
    def runBytes(self, imageBytes):
        """处理图片字节流"""
        try:
            image_base64 = base64.b64encode(imageBytes).decode('utf-8')
            return self.runBase64(image_base64)
        except Exception as e:
            return self._create_error_result(f"处理图片字节流失败: {str(e)}")
    
    def _ensure_paddle_detector(self):
        """加载并启动 PaddleOCR-json 检测器"""
        if getattr(self, 'detector', None):
            return
        try:
            base_dir = os.path.dirname(__file__)
            plugins_root = os.path.normpath(os.path.join(base_dir, '..'))
            detector_path = None
            # 先查找 AIOCR 内置的 Paddle 目录
            embedded_candidates = [
                os.path.join(base_dir, 'paddle_detector', 'PPOCR_umi.py'),
                os.path.join(base_dir, 'detectors', 'paddle', 'PPOCR_umi.py'),
                os.path.join(base_dir, 'vendor_paddle', 'PPOCR_umi.py'),
            ]
            for candidate in embedded_candidates:
                if os.path.isfile(candidate):
                    detector_path = candidate
                    break
            # 若未找到内置目录，再兼容多种外部目录名：如 win7_x64_PaddleOCR-json、PaddleOCR-json 等
            if not detector_path:
                for name in os.listdir(plugins_root):
                    try:
                        if 'PaddleOCR-json' in name:
                            candidate = os.path.join(plugins_root, name, 'PPOCR_umi.py')
                            if os.path.isfile(candidate):
                                detector_path = candidate
                                break
                    except Exception:
                        continue
            if not detector_path:
                raise RuntimeError('未找到 PaddleOCR-json 检测器。可选方案：将完整引擎目录打包到 AIOCR/paddle_detector，或放在 plugins/win7_x64_PaddleOCR-json')
            # 动态导入模块
            # 以临时包方式加载，确保相对导入可用
            pkg_name = 'AIOCR_embedded_paddle'
            pkg_path = os.path.dirname(detector_path)
            if pkg_name not in sys.modules:
                pkg = types.ModuleType(pkg_name)
                pkg.__path__ = [pkg_path]
                sys.modules[pkg_name] = pkg
            spec = importlib.util.spec_from_file_location(f'{pkg_name}.PPOCR_umi', detector_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            DetectorApi = getattr(module, 'Api', None)
            if DetectorApi is None:
                raise RuntimeError('PPOCR_umi.py 中未找到 Api 类')
            # 构造必要的全局参数，避免 KeyError
            default_global = {
                'enable_mkldnn': True,
                'cpu_threads': os.cpu_count() or 4,
                'ram_max': -1,
                'ram_time': 60,
            }
            self.detector = DetectorApi(default_global)
            # 启动引擎（局部参数可为空）
            err = self.detector.start({})
            if isinstance(err, str) and err.startswith('[Error]'):
                raise RuntimeError(err)
        except Exception as e:
            self.detector = None
            raise RuntimeError(f"PaddleOCR 检测器启动失败: {e}")

    def _crop_by_box(self, img, box):
        """根据检测框裁剪图像，支持矩形与四点多边形"""
        try:
            if isinstance(box, dict):
                x = box.get('x', box.get('left'))
                y = box.get('y', box.get('top'))
                w = box.get('w', box.get('width'))
                h = box.get('h', box.get('height'))
                if x is not None and y is not None and w is not None and h is not None:
                    x0, y0 = int(max(0, x)), int(max(0, y))
                    x1, y1 = int(min(img.width, x + w)), int(min(img.height, y + h))
                    return img.crop((x0, y0, x1, y1))
                pts = box.get('points') or box.get('polygon') or box.get('box')
            elif isinstance(box, (list, tuple)):
                if len(box) == 4 and all(isinstance(v, (int, float)) for v in box):
                    x, y, w, h = box
                    x0, y0 = int(max(0, x)), int(max(0, y))
                    x1, y1 = int(min(img.width, x + w)), int(min(img.height, y + h))
                    return img.crop((x0, y0, x1, y1))
                elif len(box) >= 4 and all(isinstance(p, (list, tuple)) and len(p) >= 2 for p in box):
                    pts = box
                else:
                    pts = None
            else:
                pts = None
            if pts:
                xs = [p[0] for p in pts]
                ys = [p[1] for p in pts]
                x0, y0 = int(max(0, min(xs))), int(max(0, min(ys)))
                x1, y1 = int(min(img.width, max(xs))), int(min(img.height, max(ys)))
                if x1 > x0 and y1 > y0:
                    return img.crop((x0, y0, x1, y1))
        except Exception:
            pass
        return img

    def _extract_text_simple(self, parsed):
        """抽取简单文本（用于裁剪后识别）"""
        if parsed is None:
            return ''
        if isinstance(parsed, str):
            return parsed.strip()
        if isinstance(parsed, dict):
            texts = parsed.get('texts') or parsed.get('items')
            if isinstance(texts, list):
                return '\n'.join(t.get('text') if isinstance(t, dict) else str(t) for t in texts)
            return parsed.get('text', '')
        if isinstance(parsed, list):
            return '\n'.join(str(x) for x in parsed)
        return str(parsed)


    def _run_paddle_first_correction(self, image_base64):
        """Paddle优先 + AI纠错：先本地识别行与框，再由AI校正文本。"""
        try:
            self._ensure_paddle_detector()
        except Exception as e:
            return {"code": 101, "data": f"[Error] {e}"}
        local = getattr(self, 'local_config', {})
        max_boxes = int(local.get('dual_max_boxes', 30))
        min_area = int(local.get('dual_min_area', 0))
        # 1) 先用Paddle识别获得文本与坐标（增加超时回退）
        paddle_timeout = int(local.get('paddle_timeout', 20))
        start_ts = time.time()
        try:
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as _executor:
                future = _executor.submit(self.detector.runBase64, image_base64)
                det = future.result(timeout=paddle_timeout)
            cost = round(time.time() - start_ts, 2)
            print(f"[AIOCR] Paddle识别完成，耗时 {cost}s")
        except concurrent.futures.TimeoutError:
            print(f"[AIOCR] Paddle识别超时({paddle_timeout}s)，回退到AI直出")
            return self._run_ocr(image_base64, self.local_config)
        except Exception as e:
            return {"code": 101, "data": f"Paddle识别异常: {str(e)}"}
        if not isinstance(det, dict) or det.get('code') != 100 or not isinstance(det.get('data'), list):
            return {"code": 101, "data": "Paddle识别失败"}
        items = det.get('data', [])
        if not items:
            return det
        # 2) 过滤并排序（按行中心y坐标）
        def _bounds_from_box(box):
            pts = None
            if isinstance(box, dict):
                x = box.get('x', box.get('left')); y = box.get('y', box.get('top'))
                w = box.get('w', box.get('width')); h = box.get('h', box.get('height'))
                if x is not None and y is not None and w is not None and h is not None:
                    return int(x), int(y), int(x + w), int(y + h)
                pts = box.get('points') or box.get('polygon') or box.get('box')
            elif isinstance(box, (list, tuple)):
                if len(box) == 4 and all(isinstance(v, (int, float)) for v in box):
                    x, y, w, h = box
                    return int(x), int(y), int(x + w), int(y + h)
                elif len(box) >= 4 and all(isinstance(p, (list, tuple)) and len(p) >= 2 for p in box):
                    pts = box
            if pts:
                xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
                return int(min(xs)), int(min(ys)), int(max(xs)), int(max(ys))
            return None
        def _poly_from_box(box):
            poly = None
            if isinstance(box, dict):
                poly = box.get('points') or box.get('polygon') or box.get('box')
                if not poly and all(k in box for k in ('left','top','width','height')):
                    l,t,w,h = box['left'], box['top'], box['width'], box['height']
                    poly = [[l,t],[l+w,t],[l+w,t+h],[l,t+h]]
            elif isinstance(box, (list, tuple)):
                if len(box) == 4 and all(isinstance(v, (int, float)) for v in box):
                    x,y,w,h = box
                    poly = [[x,y],[x+w,y],[x+w,y+h],[x,y+h]]
                elif len(box) >= 4 and all(isinstance(p, (list, tuple)) and len(p) >= 2 for p in box):
                    poly = [[p[0], p[1]] for p in box[:4]]
            return poly or []
        filtered = []
        for it in items:
            raw_box = it.get('box') or it.get('polygon') or it.get('points') or it.get('rect') or it.get('bbox')
            b = _bounds_from_box(raw_box)
            if not b:
                continue
            x0,y0,x1,y1 = b
            area = max(0, x1-x0) * max(0, y1-y0)
            if area < min_area:
                continue
            cy = (y0+y1)/2.0
            filtered.append({
                "text": (it.get('text') or it.get('content') or '').strip(),
                "box": _poly_from_box(raw_box),
                "center_y": cy,
            })
        filtered.sort(key=lambda v: v['center_y'])
        if max_boxes > 0:
            filtered = filtered[:max_boxes]
        # 新增：提前获取语言，便于AI回退
        language = local.get("language", "auto")
        if not filtered:
            # Paddle未检测到有效框，改用AI直出
            ai_only_coords = self._run_ocr(image_base64, {"output_format": "with_coordinates", "language": language})
            if isinstance(ai_only_coords, dict) and ai_only_coords.get("code") == 100 and isinstance(ai_only_coords.get("data"), list) and ai_only_coords.get("data"):
                return ai_only_coords
            ai_only_text = self._run_ocr(image_base64, {"output_format": "text_only", "language": language})
            if isinstance(ai_only_text, dict) and ai_only_text.get("code") == 100:
                return ai_only_text
            return det
        # 3) 构建纠错提示，将Paddle识别与坐标作为上下文提供给AI
        language = local.get("language", "auto")
        lang_map = {"auto": "自动检测语言","zh": "中文","en": "英文","ja": "日文","ko":"韩文","fr":"法文","de":"德文","es":"西班牙文","ru":"俄文","ar":"阿拉伯文"}
        lang_instruction = lang_map.get(language, "自动检测语言")
        candidates = [{"text": f["text"], "box": f["box"]} for f in filtered]
        try:
            ctx_json = json.dumps({"texts": candidates}, ensure_ascii=False)
        except Exception:
            # 构建纠错上下文失败，改用AI直出
            ai_only_coords = self._run_ocr(image_base64, {"output_format": "with_coordinates", "language": language})
            if isinstance(ai_only_coords, dict) and ai_only_coords.get("code") == 100:
                return ai_only_coords
            return self._run_ocr(image_base64, {"output_format": "text_only", "language": language})
        variant_note = ("严格禁止对中文进行繁体/简体转换、全角/半角转换、字符归一化；混合繁简时保持混合状态。逐字抄写图像字符，不要重写。示例：不要把 '台灣里体干' 改为 '臺灣裏體幹'，也不要相反。\n" if language in ("auto", "zh") else "")
        prompt = (
            f"请基于这张图片和PaddleOCR的识别结果进行纠错，语言：{lang_instruction}。\n"
            "保持每行数量与顺序不变，只修正识别错误，保留标点与空格。\n"
            + variant_note +
            "仅输出纯文本，每行一个，顺序与Paddle一致。\n"
            "不要解释或添加其他内容。\n"
            f"Paddle识别结果：```json\n{ctx_json}\n```"
        )
        # 4) 发送请求并解析为统一格式（稳健映射：文本由AI，坐标用Paddle）
        try:
            response_text = self._send_request(image_base64, prompt)
            parsed = self.provider.parse_response(response_text)
            # 4.1 获取AI纠正的纯文本行（不依赖坐标结构）
            text_only = self._convert_to_umi_format(parsed, {"output_format": "text_only"})
            ai_lines = []
            if isinstance(text_only, dict) and text_only.get("code") == 100 and isinstance(text_only.get("data"), list):
                ai_lines = [item.get("text", "") for item in text_only.get("data") if isinstance(item, dict) and item.get("text")]
            # 4.1.1 回退解析：若纯文本未提取到行，尝试解析JSON中的texts
            if not ai_lines:
                coord_fmt = self._convert_to_umi_format(parsed, {"output_format": "with_coordinates"})
                if isinstance(coord_fmt, dict) and coord_fmt.get("code") == 100 and isinstance(coord_fmt.get("data"), list):
                    ai_lines = [item.get("text", "") for item in coord_fmt["data"] if isinstance(item, dict) and item.get("text")]
            print(f"[AIOCR] AI纠错行数: {len(ai_lines)} / Paddle行数: {len(filtered)}")
            # 4.2 若AI纠错未返回行，尝试AI直出后匹配Paddle框
            if len(ai_lines) == 0:
                try:
                    print("[AIOCR] AI纠错为空，尝试AI直出(含坐标)匹配Paddle框")
                    ai_only_coords = self._run_ocr(image_base64, {"output_format": "with_coordinates", "language": language})
                    if isinstance(ai_only_coords, dict) and ai_only_coords.get("code") == 100 and isinstance(ai_only_coords.get("data"), list):
                        ai_text_count = sum(1 for it in ai_only_coords["data"] if isinstance(it, dict) and (it.get("text") or "").strip())
                        if ai_text_count > 0:
                            matched = self._match_ai_text_to_paddle_boxes(ai_only_coords["data"], items, max_boxes, min_area)
                            if matched:
                                return {"code": 100, "data": [{"text": m["text"], "box": m["box"], "score": m.get("score", 1.0)} for m in matched]}
                    print("[AIOCR] 坐标直出为空，尝试AI直出纯文本匹配Paddle框")
                    ai_only_text = self._run_ocr(image_base64, {"output_format": "text_only", "language": language})
                    if isinstance(ai_only_text, dict) and ai_only_text.get("code") == 100 and isinstance(ai_only_text.get("data"), list):
                        ai_text_count2 = sum(1 for it in ai_only_text["data"] if isinstance(it, dict) and (it.get("text") or "").strip())
                        if ai_text_count2 > 0:
                            matched2 = self._match_ai_text_to_paddle_boxes(ai_only_text["data"], items, max_boxes, min_area)
                            if matched2:
                                return {"code": 100, "data": [{"text": m["text"], "box": m["box"], "score": m.get("score", 1.0)} for m in matched2]}
                except Exception as _e:
                    print(f"[AIOCR] AI直出匹配失败: {str(_e)}")

                # 进一步回退：逐框裁剪并对每个框进行AI识别纠错
                try:
                    print("[AIOCR] AI直出仍为空，开始逐框裁剪识别纠错")
                    # 尝试解码原始图片
                    try:
                        raw_b64 = image_base64
                        if isinstance(raw_b64, str) and raw_b64.startswith("data:image"):
                            raw_b64 = raw_b64.split(",", 1)[-1]
                        img = Image.open(BytesIO(base64.b64decode(raw_b64)))
                    except Exception:
                        img = None
                    ai_crop_lines = []
                    if img:
                        for f in filtered:
                            crop = self._crop_by_box(img, f["box"])
                            buf = BytesIO()
                            crop.save(buf, format="PNG")
                            crop_b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
                            resp = self._run_ocr(crop_b64, {"output_format": "text_only", "language": language})
                            line_text = ""
                            if isinstance(resp, dict) and resp.get("code") == 100 and isinstance(resp.get("data"), list) and len(resp["data"]) > 0:
                                first = resp["data"][0]
                                line_text = (first.get("text") or "").strip() if isinstance(first, dict) else ""
                            ai_crop_lines.append(line_text)
                    non_empty = sum(1 for t in ai_crop_lines if t)
                    print(f"[AIOCR] 逐框纠错行数: {non_empty} / {len(filtered)}")
                    if non_empty > 0:
                        result_data = []
                        for idx, f in enumerate(filtered):
                            text = ai_crop_lines[idx] if idx < len(ai_crop_lines) and ai_crop_lines[idx] else f.get("text", "")
                            result_data.append({"text": text, "box": f["box"], "score": 1.0})
                        if result_data:
                            return {"code": 100, "data": result_data}
                except Exception as _e2:
                    print(f"[AIOCR] 逐框裁剪纠错失败: {str(_e2)}")
            # 4.3 统一组装输出：坐标始终使用Paddle，文本优先采用AI纠正
            result_data = []
            for idx, f in enumerate(filtered):
                text = ai_lines[idx] if idx < len(ai_lines) else f.get("text", "")
                result_data.append({"text": text, "box": f["box"], "score": 1.0})
            if result_data:
                return {"code": 100, "data": result_data}
            # AI完全失败则回退到Paddle结果
            return det
        except Exception:
            # AI纠错流程异常，改用AI直出
            ai_only_coords = self._run_ocr(image_base64, {"output_format": "with_coordinates", "language": language})
            if isinstance(ai_only_coords, dict) and ai_only_coords.get("code") == 100:
                return ai_only_coords
            return self._run_ocr(image_base64, {"output_format": "text_only", "language": language})
    def _run_paddle_fallback(self, image_base64):
        """Paddle回退模式：纯本地识别"""
        try:
            det = self.detector.runBase64(image_base64)
            if isinstance(det, dict) and det.get('code') == 100:
                return det
            else:
                return {"code": 101, "data": "Paddle识别失败"}
        except Exception as e:
            return {"code": 101, "data": f"Paddle识别异常: {str(e)}"}

    def _match_ai_text_to_paddle_boxes(self, ai_data, paddle_items, max_boxes, min_area):
        """智能匹配AI识别文本到Paddle检测框"""
        # 提取AI识别的文本行
        ai_texts = []
        for item in ai_data:
            text = item.get('text', '').strip()
            if text:
                ai_texts.append(text)

        # 如果AI没有产生任何文本，直接返回空列表，避免用Paddle文本伪装纠错成功
        if len(ai_texts) == 0:
            return []

        # 辅助：将各种格式的框转换为边界框 (x0,y0,x1,y1)
        def _bounds_from_box(box):
            if isinstance(box, dict):
                x = box.get('x', box.get('left'))
                y = box.get('y', box.get('top'))
                w = box.get('w', box.get('width'))
                h = box.get('h', box.get('height'))
                if x is not None and y is not None and w is not None and h is not None:
                    return int(x), int(y), int(x + w), int(y + h)
                pts = box.get('points') or box.get('polygon') or box.get('box')
            elif isinstance(box, (list, tuple)):
                if len(box) == 4 and all(isinstance(v, (int, float)) for v in box):
                    x, y, w, h = box
                    return int(x), int(y), int(x + w), int(y + h)
                elif len(box) >= 4 and all(isinstance(p, (list, tuple)) and len(p) >= 2 for p in box):
                    pts = box
                else:
                    pts = None
            else:
                pts = None
            if pts:
                xs = [p[0] for p in pts]
                ys = [p[1] for p in pts]
                return int(min(xs)), int(min(ys)), int(max(xs)), int(max(ys))
            return None

        # 辅助：统一生成四点坐标
        def _poly_from_box(box):
            poly = None
            if isinstance(box, dict):
                poly = box.get('points') or box.get('polygon') or box.get('box')
                if not poly and all(k in box for k in ('left','top','width','height')):
                    l,t,w,h = box['left'], box['top'], box['width'], box['height']
                    poly = [[l,t],[l+w,t],[l+w,t+h],[l,t+h]]
            elif isinstance(box, (list, tuple)):
                if len(box) == 4 and all(isinstance(v, (int, float)) for v in box):
                    x,y,w,h = box
                    poly = [[x,y],[x+w,y],[x+w,y+h],[x,y+h]]
                elif len(box) >= 4 and all(isinstance(p, (list, tuple)) and len(p) >= 2 for p in box):
                    poly = [[p[0], p[1]] for p in box[:4]]
            return poly

        # 过滤有效的Paddle框，并按Y排序
        valid_boxes = []
        for it in paddle_items:
            box = it.get('box') or it.get('polygon') or it.get('points') or it.get('rect') or it.get('bbox')
            b = _bounds_from_box(box)
            if not b:
                continue
            x0, y0, x1, y1 = b
            area = max(0, x1 - x0) * max(0, y1 - y0)
            if area < min_area:
                continue
            center_y = (y0 + y1) / 2.0
            local_text = (it.get('text') or it.get('content') or '').strip()
            valid_boxes.append({'box': box, 'center_y': center_y, 'local_text': local_text})

        valid_boxes.sort(key=lambda v: v['center_y'])
        if max_boxes > 0:
            valid_boxes = valid_boxes[:max_boxes]

        # 简单顺序匹配：AI文本优先，不足时用Paddle文本兜底
        results = []
        for i, vb in enumerate(valid_boxes):
            text = ai_texts[i] if i < len(ai_texts) else vb['local_text']
            poly = _poly_from_box(vb['box'])
            results.append({"text": text, "box": poly, "score": 1.0})

        return results
    def runBase64(self, imageBase64):
        """处理base64图片"""
        try:
            # 根据识别策略选择流程（不再需要启用开关）
            if hasattr(self, 'local_config'):
                strategy = self.local_config.get('dual_strategy', 'ai_high_precision_with_coordinates')
                # 含位置版：Paddle检测框 + AI纠错文本
                if strategy in ('ai_high_precision_with_coordinates', 'paddle_first_correction'):
                    return self._run_paddle_first_correction(imageBase64)
                # 纯文本：整图AI识别（预处理后）
                elif strategy == 'ai_high_precision_text_only':
                    local = getattr(self, 'local_config', {})
                    processed_base64 = self._preprocess_image(imageBase64)
                    # *** 修改：确保调用 _run_ocr 时传递 output_format: text_only ***
                    # (原代码) return self._run_ocr(processed_base64, {"output_format": "text_only", "language": local.get("language", "auto")})
                    # (优化) self.local_config 已经包含了 output_format，直接传递
                    return self._run_ocr(processed_base64, self.local_config)
                # 兜底：未知或旧值（如 'ai_first'）均按含位置版处理
                else:
                    return self._run_paddle_first_correction(imageBase64)
            # 预处理图像 (兜底情况)
            processed_base64 = self._preprocess_image(imageBase64)
            # 执行OCR
            return self._run_ocr(processed_base64, self.local_config)
        except Exception as e:
            return self._create_error_result(f"OCR处理失败: {str(e)}")
    
    def _preprocess_image(self, image_base64):
        """预处理图像"""
        try:
            # 解码图像获取尺寸信息
            image_data = base64.b64decode(image_base64)
            image = Image.open(BytesIO(image_data))
            self.original_size = image.size
            
            # 检查是否需要处理
            max_size = self.local_config.get("max_image_size", 1536)
            quality_setting = self.local_config.get("image_quality", "auto")
            
            need_resize = max(image.size) > max_size
            need_convert = image.mode != 'RGB'
            need_quality_adjust = quality_setting != "auto"
            
            # 如果不需要任何处理，直接返回原图
            if not (need_resize or need_convert or need_quality_adjust):
                self.scale_ratio = 1.0
                self.processed_size = self.original_size
                return image_base64
            
            # 只在需要时进行转换
            if need_convert:
                image = image.convert('RGB')
            
            # 只在需要时进行缩放
            if need_resize:
                self.scale_ratio = max_size / max(image.size)
                new_size = (int(image.size[0] * self.scale_ratio), int(image.size[1] * self.scale_ratio))
                image = image.resize(new_size, Image.Resampling.LANCZOS)
                self.processed_size = new_size
            else:
                self.scale_ratio = 1.0
                self.processed_size = image.size
            
            # 只在需要时调整质量
            if need_quality_adjust:
                quality_map = {"high": 95, "medium": 85, "low": 75}
                quality = quality_map.get(quality_setting, 85)
            else:
                quality = 85
            
            # 重新编码
            buffer = BytesIO()
            image.save(buffer, format='JPEG', quality=quality, optimize=True)
            return base64.b64encode(buffer.getvalue()).decode('utf-8')
            
        except Exception as e:
            # 预处理失败时保持原图
            self.processed_size = self.original_size
            self.scale_ratio = 1.0
            return image_base64
    
    def _run_ocr(self, image_base64, config):
        """执行OCR识别"""
        try:
            # 构建提示词
            prompt = self._build_prompt(config)
            
            # 发送请求（默认重试3次 -> 可配置，默认1次）
            max_retries = int(config.get("max_retries", 1))
            
            for attempt in range(max_retries + 1):
                try:
                    response_text = self._send_request(image_base64, prompt)
                    
                    # 解析响应
                    parsed_content = self.provider.parse_response(response_text)
                    
                    if parsed_content:
                        # 转换为Umi格式
                        return self._convert_to_umi_format(parsed_content, config)
                    else:
                        return self._create_empty_result()
                        
                except Exception as e:
                    if attempt == max_retries:
                        raise e
                    time.sleep(1)  # 重试前等待
                    
        except Exception as e:
            return self._create_error_result(str(e))
    
    def _build_prompt(self, config):
        """构建提示词"""
        language = config.get("language", "auto")
        output_format = config.get("output_format", "text_only")
        
        # 语言映射
        lang_map = {
            "auto": "自动检测语言",
            "zh": "中文",
            "en": "英文",
            "ja": "日文",
            "ko": "韩文",
            "fr": "法文",
            "de": "德文",
            "es": "西班牙文",
            "ru": "俄文",
            "ar": "阿拉伯文"
        }
        
        lang_instruction = lang_map.get(language, "自动检测语言")
        
        if output_format == "with_coordinates":
            # 坐标模式（JSON）保持不变
            prompt = f"""识别图片文字并返回坐标，语言：{lang_instruction}
输出JSON格式：{{"texts": [{{"text": "文字内容", "box": [[x1,y1],[x2,y2],[x3,y3],[x4,y4]]}}]}}
坐标为像素位置，左上角为原点。直接返回JSON，无其他内容。"""
        else:
            # ==========================================================
            # =========== 这是唯一的修改点 (Markdown + LaTeX 提示词) ===========
            # ==========================================================
            prompt = f"""请将图片中的所有内容（文本、表格、公式）完整地识别出来，并以 Markdown 格式返回。

请严格遵守以下规则：
1.  **表格：** 如果图片中包含表格，请必须使用 Markdown 表格语法将其格式化。
2.  **公式：** 如果图片中包含数学公式，请必须使用 LaTeX 格式将其包裹 (行内公式使用 $...$，块级公式使用 $$...$$)。
3.  **结构：** 保持合理的段落、标题和列表结构。
4.  **纯净：** 直接返回 Markdown 结果，不要包含任何解释性文字（如 "这是结果：" 或 "好的："），也不要使用 "```markdown" 代码块标记包裹整个结果。

语言：{lang_instruction}。"""
            # ==========================================================
            # ======================= 修改结束 =========================
            # ==========================================================
        
        if language in ("auto", "zh"):
            prompt += "\n严格禁止对中文进行繁体/简体转换、全角/半角转换、字符归一化；混合繁简时保持混合状态。逐字抄写图像字符，不要重写。示例：不要把 '台灣里体干' 改为 '臺灣裏體幹'，也不要相反。"
        
        return prompt
    
    def _send_request(self, image_base64, prompt):
        """发送API请求"""
        # 关键日志：记录提供商、模型与超时，便于定位卡顿
        try:
            provider_name = self.global_config.get("a_provider", self.global_config.get("provider", "unknown"))
        except Exception:
            provider_name = "unknown"
        print(f"[AIOCR] 调用 {provider_name} / 模型 {getattr(self.provider, 'model', None)} / 超时 {getattr(self.http_client, 'timeout', None)}s")
        # 构建请求URL
        api_base = self.provider.api_base or self.provider.get_default_api_base()
        provider_name = self.global_config.get("a_provider", self.global_config.get("provider", "openai"))
        
        if provider_name == "gemini":
            model = self.provider.model or self.provider.get_default_model()
            url = f"{api_base}/models/{model}:generateContent?key={self.provider.api_key}"
        elif provider_name == "alibaba":
            url = f"{api_base}/services/aigc/multimodal-generation/generation"
        elif provider_name == "zhipu":
            url = f"{api_base}/chat/completions"
        elif provider_name == "ollama":
            url = f"{api_base}/generate"
        elif provider_name == "lmstudio":
            url = f"{api_base}/chat/completions"
        elif provider_name == "mistral":
            url = f"{api_base}/chat/completions"  # Mistral OCR专用端点
        else:
            url = f"{api_base}/chat/completions"
        
        # 构建请求头和载荷
        headers = self.provider.build_headers()
        payload = self.provider.build_payload(image_base64, prompt)
        
        # 检查是否是 MinerU 的错误情况
        if isinstance(payload, dict) and payload.get("_mineru_error"):
            # MinerU 不支持直接图片 OCR，返回错误信息
            raise Exception(payload.get("error_message", "MinerU 不支持此操作"))
        else:
            # 所有服务商使用标准 JSON 请求
            response = self.http_client.post(url, headers, json.dumps(payload))
        
        if response['status_code'] != 200:
            raise Exception(f"API请求失败 (状态码: {response['status_code']}): {response['text']}")
        
        return response['text']
    
    def _convert_to_umi_format(self, content, config):
        """转换为Umi格式"""
        output_format = config.get("output_format", "text_only")
        
        if output_format == "with_coordinates":
            return self._parse_text_with_coordinates(content)
        else:
            return self._parse_text_only(content)

    def _extract_json_from_text(self, content):
        """从混杂文本中尽力提取JSON块（支持代码块与原始文本）"""
        try:
            if not isinstance(content, str):
                content = str(content)
            s = content.strip()
            # 1) 直接是JSON
            if s.startswith('{'):
                return json.loads(s)
            # 2) 代码块中的JSON
            m = re.search(r"```(?:json|JSON)?\s*(\{[\s\S]*?\})\s*```", content)
            if m:
                return json.loads(m.group(1))
            # 3) 文本里第一段花括号内容
            m2 = re.search(r"(\{[\s\S]*\})", content)
            if m2:
                candidate = m2.group(1)
                return json.loads(candidate)
        except Exception:
            return None
        return None

    def _parse_text_with_coordinates(self, content):
        """解析带坐标的文本"""
        try:
            # 确保content是字符串，但要正确处理不同类型
            if isinstance(content, list):
                # 如果是列表，尝试提取文本内容
                text_parts = []
                for item in content:
                    if isinstance(item, str):
                        text_parts.append(item)
                    elif isinstance(item, dict) and "text" in item:
                        text_parts.append(item["text"])
                    else:
                        text_parts.append(str(item))
                content = ' '.join(text_parts)
            elif isinstance(content, dict):
                # 如果是字典，尝试提取text字段
                if "text" in content:
                    content = content["text"]
                else:
                    content = str(content)
            elif not isinstance(content, str):
                content = str(content)
            
            # 尝试提取JSON（支持代码块与混杂文本）
            data = self._extract_json_from_text(content)
            if isinstance(data, dict):
                texts = None
                if "texts" in data and isinstance(data["texts"], list):
                    texts = data["texts"]
                elif "data" in data and isinstance(data["data"], dict) and "texts" in data["data"]:
                    texts = data["data"]["texts"]
                elif "result" in data and isinstance(data["result"], dict) and "texts" in data["result"]:
                    texts = data["result"]["texts"]
                
                if texts:
                    result_data = []
                    for item in texts:
                        box = None
                        if isinstance(item, dict):
                            box = (
                                item.get("box")
                                or item.get("box_2d")
                                or item.get("bbox")
                                or item.get("rect")
                                or item.get("points")
                                or item.get("polygon")
                            )
                        if box is not None:
                            mapped_box = self._map_coordinates_to_original(box)
                            result_data.append({
                                "text": item.get("text", ""),
                                "box": mapped_box,
                                "score": float(item.get("score", 1.0))
                            })
                    
                    if result_data:
                        return {"code": 100, "data": result_data}
                    else:
                        return self._create_empty_result()
            
            # 如果不是JSON格式，尝试解析纯文本
            return self._parse_text_only(content)
            
        except Exception:
            # 解析失败，当作纯文本处理
            return self._parse_text_only(content)
    
    def _map_coordinates_to_original(self, box):
        """将坐标映射回原始图像尺寸，并统一为四点多边形。
        兼容：四数数组(xywh/xyxy)、点集、多矩形数组、字典矩形与字符串格式。
        """
        # 推断处理后尺寸（允许原始尺寸缺失时仍做形状归一化）
        proc_w, proc_h = None, None
        if self.processed_size:
            proc_w, proc_h = self.processed_size
        elif self.scale_ratio and self.original_size:
            proc_w = int(self.original_size[0] * self.scale_ratio)
            proc_h = int(self.original_size[1] * self.scale_ratio)
        elif self.original_size:
            proc_w, proc_h = self.original_size
        
        def clamp_xy(x, y):
            x = int(round(x))
            y = int(round(y))
            if self.original_size:
                x = max(0, min(x, self.original_size[0]))
                y = max(0, min(y, self.original_size[1]))
            return [x, y]
        
        def map_point(x, y):
            # 归一化坐标（0..1）需要尺寸才能映射
            if proc_w is not None and proc_h is not None and 0.0 <= x <= 1.0 and 0.0 <= y <= 1.0:
                x = x * proc_w
                y = y * proc_h
            # 映射回原图尺寸（如果曾缩放）
            if self.scale_ratio and self.scale_ratio != 1.0:
                x = x / self.scale_ratio
                y = y / self.scale_ratio
            return clamp_xy(x, y)
        
        def poly_from_xywh(x, y, w, h):
            p1 = map_point(x, y)
            p2 = map_point(x + w, y)
            p3 = map_point(x + w, y + h)
            p4 = map_point(x, y + h)
            return [p1, p2, p3, p4]
        
        def poly_from_xyxy(x1, y1, x2, y2):
            p1 = map_point(x1, y1)
            p2 = map_point(x2, y1)
            p3 = map_point(x2, y2)
            p4 = map_point(x1, y2)
            return [p1, p2, p3, p4]
        
        def try_numbers_4(vals):
            x1, y1, a, b = vals
            # 判定 [x1,y1,x2,y2] vs [x,y,w,h]
            if proc_w is not None and proc_h is not None:
                if (a > proc_w or b > proc_h) or (x1 + a > proc_w or y1 + b > proc_h):
                    return poly_from_xyxy(x1, y1, a, b)
                return poly_from_xywh(x1, y1, a, b)
            if a > x1 and b > y1:
                return poly_from_xyxy(x1, y1, a, b)
            return poly_from_xywh(x1, y1, a, b)
        
        def union_rect(polys):
            xs = [p[0] for poly in polys for p in poly]
            ys = [p[1] for poly in polys for p in poly]
            if not xs or not ys:
                return None
            return poly_from_xyxy(min(xs), min(ys), max(xs), max(ys))
        
        try:
            # 字符串：提取数字
            if isinstance(box, str):
                nums = re.findall(r"-?\d+\.?\d*", box)
                nums = [float(n) for n in nums]
                if len(nums) == 4:
                    return try_numbers_4(nums)
                if len(nums) == 8:
                    pts = [[nums[i], nums[i+1]] for i in range(0, 8, 2)]
                    return [map_point(p[0], p[1]) for p in pts]
                return box
        
            # 字典：优先 points/polygon/box，其次矩形键
            if isinstance(box, dict):
                pts = box.get('points') or box.get('polygon') or box.get('box')
                if isinstance(pts, (list, tuple)) and len(pts) >= 4 and all(isinstance(p, (list, tuple)) and len(p) >= 2 for p in pts):
                    # 如果点数超过4个，按外接矩形归一
                    if len(pts) > 4:
                        xs = [p[0] for p in pts]
                        ys = [p[1] for p in pts]
                        return poly_from_xyxy(min(xs), min(ys), max(xs), max(ys))
                    return [map_point(p[0], p[1]) for p in pts[:4]]
                x = box.get('left', box.get('x'))
                y = box.get('top', box.get('y'))
                w = box.get('width', box.get('w'))
                h = box.get('height', box.get('h'))
                if all(v is not None for v in (x, y, w, h)):
                    return poly_from_xywh(x, y, w, h)
                # 支持 {x1,y1,x2,y2}
                x1 = box.get('x1'); y1 = box.get('y1'); x2 = box.get('x2'); y2 = box.get('y2')
                if all(v is not None for v in (x1, y1, x2, y2)):
                    return poly_from_xyxy(x1, y1, x2, y2)
                return box
        
            # 列表/元组：多种形状
            if isinstance(box, (list, tuple)):
                # 多个矩形 [[x1,y1,x2,y2], ...] 或 [[x,y,w,h], ...]
                if len(box) >= 1 and all(isinstance(b, (list, tuple)) and len(b) == 4 and all(isinstance(v, (int, float)) for v in b) for b in box):
                    polys = [try_numbers_4(list(b)) for b in box]
                    merged = union_rect(polys)
                    return merged or polys[0]
                # 四点坐标 [[x,y],...]
                if len(box) == 4 and all(isinstance(p, (list, tuple)) and len(p) == 2 for p in box):
                    return [map_point(p[0], p[1]) for p in box]
                # 扁平四数或八数
                if len(box) == 4 and all(isinstance(v, (int, float)) for v in box):
                    return try_numbers_4(list(box))
                if len(box) == 8 and all(isinstance(v, (int, float)) for v in box):
                    pts = [[box[i], box[i+1]] for i in range(0, 8, 2)]
                    return [map_point(p[0], p[1]) for p in pts]
                # 超过4个点的点集 -> 外接矩形
                if all(isinstance(p, (list, tuple)) and len(p) >= 2 for p in box):
                    xs = [p[0] for p in box]
                    ys = [p[1] for p in box]
                    return poly_from_xyxy(min(xs), min(ys), max(xs), max(ys))
        
            # 其他情况：直接返回原值
            return box
        except Exception:
            return box
    
    def _generate_estimated_boxes(self, lines):
        """为纯文本生成估算的边界框"""
        # 使用简化的计算以提高速度
        img_width, img_height = self.original_size if self.original_size else (800, 600)
        
        # 预计算常量
        line_height = min(30, img_height // max(len(lines), 1))
        margin_left = int(img_width * 0.05)
        margin_top = int(img_height * 0.05)
        max_width = int(img_width * 0.9)
        
        result_data = []
        y_offset = margin_top
        
        for line in lines:
            # 简化的宽度计算
            text_width = min(len(line) * 12, max_width)  # 减少字符宽度计算
            
            # 直接创建边界框
            box = [
                [margin_left, y_offset],
                [margin_left + text_width, y_offset],
                [margin_left + text_width, y_offset + line_height],
                [margin_left, y_offset + line_height]
            ]
            
            result_data.append({"text": line, "box": box, "score": 1.0})
            y_offset += int(line_height * 1.2)
        
        return result_data
    
    def _parse_text_only(self, content):
        """解析纯文本"""
        # 确保content是字符串，但要正确处理不同类型
        if isinstance(content, list):
            # 如果是列表，尝试提取文本内容
            text_parts = []
            for item in content:
                if isinstance(item, str):
                    text_parts.append(item)
                elif isinstance(item, dict) and "text" in item:
                    text_parts.append(item["text"])
                else:
                    text_parts.append(str(item))
            content = ' '.join(text_parts)
        elif isinstance(content, dict):
            # 如果是字典，尝试提取text字段
            if "text" in content:
                content = content["text"]
            else:
                content = str(content)
        elif not isinstance(content, str):
            content = str(content)
            
        # 清理内容
        content = content.strip()
        
        if not content:
            return self._create_empty_result()
        
        # ==================================================
        # =========== 这是第二个修改点 (Markdown 解析) ===========
        # ==================================================
        # 不再按行分割，而是将整个 content 视为一个单独的列表项
        lines = [content]
        
        if not lines:
            return self._create_empty_result()
        
        # 生成估算的边界框
        result_data = self._generate_estimated_boxes(lines)
        
        return {"code": 100, "data": result_data}
    
    def _create_empty_result(self):
        """创建空结果"""
        return {"code": 101, "data": ""}
    
    def _create_error_result(self, error_msg):
        """创建错误结果"""
        return {"code": 102, "data": f"[Error] {error_msg}"}