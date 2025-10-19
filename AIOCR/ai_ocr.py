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
            default_headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'application/json, text/plain, */*',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
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

    def _run_dual_channel(self, image_base64):
        """检测-识别双通道主流程：Paddle 检测 + 大模型识别"""
        try:
            self._ensure_paddle_detector()
        except Exception as e:
            return {"code": 101, "data": f"[Error] {e}"}
        # 原图用于裁剪
        try:
            img = Image.open(BytesIO(base64.b64decode(image_base64))).convert('RGB')
        except Exception as e:
            return {"code": 102, "data": f"[Error] 原图解码失败: {e}"}
        # 调用检测器
        try:
            det = self.detector.runBase64(image_base64)
        except Exception as e:
            return {"code": 101, "data": f"[Error] 检测器调用失败: {e}"}
        if not isinstance(det, dict) or det.get('code') != 100 or not isinstance(det.get('data'), list):
            return {"code": det.get('code', 101), "data": det.get('data', '检测失败')}
        items = det.get('data', [])
        # 读取性能参数
        local = getattr(self, 'local_config', {})
        max_boxes = int(local.get('dual_max_boxes', 30))
        min_area = int(local.get('dual_min_area', 0))
        max_workers = int(local.get('dual_max_workers', self.max_concurrent))
        score_thr = float(local.get('dual_local_score_threshold', 0.92))
        pad = int(local.get('dual_crop_padding', 2))
        # 预过滤并限量
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
        filtered = []
        for it in items:
            box = it.get('box') or it.get('polygon') or it.get('points') or it.get('rect') or it.get('bbox')
            if not box:
                continue
            b = _bounds_from_box(box)
            if not b:
                continue
            x0, y0, x1, y1 = b
            # 面积过滤
            area = max(0, x1 - x0) * max(0, y1 - y0)
            if area < min_area:
                continue
            # 裁剪边缘补白
            x0 = max(0, x0 - pad)
            y0 = max(0, y0 - pad)
            x1 = min(img.width, x1 + pad)
            y1 = min(img.height, y1 + pad)
            filtered.append((it, box, (x0, y0, x1, y1)))
        if max_boxes > 0:
            filtered = filtered[:max_boxes]
        results = [None] * len(filtered)
        # 统一生成四点坐标
        def _poly_from_box(box, crop_wh=None):
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
            if not poly and crop_wh:
                cw, ch = crop_wh
                poly = [[0,0],[cw,0],[cw,ch],[0,ch]]
            return poly
        # 并发识别任务
        def _task(idx, it, box, rect):
            x0, y0, x1, y1 = rect
            try:
                crop = img.crop((x0, y0, x1, y1))
                buf = BytesIO()
                crop.save(buf, format='JPEG')
                crop_b64 = base64.b64encode(buf.getvalue()).decode('utf-8')
                # 本地高分直接采用，跳过AI识别
                local_text = it.get('text') or it.get('content') or ''
                local_score = it.get('score') or 0.0
                if local_text and isinstance(local_score, (int, float)) and local_score >= score_thr:
                    recognized = local_text
                else:
                    cfg = {
                        "language": local.get("language", "auto"),
                        "output_format": "text_only",
                    }
                    prompt = self._build_prompt(cfg)
                    response_text = self._send_request(crop_b64, prompt)
                    parsed = self.provider.parse_response(response_text)
                    recognized = self._extract_text_simple(parsed) or local_text
                poly = _poly_from_box(box, crop_wh=(crop.width, crop.height))
                results[idx] = {"text": recognized, "box": poly, "score": 1.0}
            except Exception:
                crop = img.crop((x0, y0, x1, y1))
                poly = _poly_from_box(box, crop_wh=(crop.width, crop.height))
                results[idx] = {"text": it.get('text') or it.get('content') or '', "box": poly, "score": 1.0}
        if not filtered:
            return {"code": 101, "data": "未检测到文本区域"}
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as ex:
            futs = []
            for i, (it, box, rect) in enumerate(filtered):
                futs.append(ex.submit(_task, i, it, box, rect))
            for f in futs:
                try:
                    f.result()
                except Exception:
                    pass
        # 对被面积过滤等原因遗漏的框，追加只用本地文本的快速结果，避免“少行”
        try:
            included_ids = set(id(it) for (it, _, _) in filtered)
            for it in items:
                if id(it) in included_ids:
                    continue
                box = it.get('box') or it.get('polygon') or it.get('points') or it.get('rect') or it.get('bbox')
                b = _bounds_from_box(box)
                if not b:
                    continue
                x0, y0, x1, y1 = b
                x0 = max(0, x0)
                y0 = max(0, y0)
                x1 = min(img.width, x1)
                y1 = min(img.height, y1)
                crop = img.crop((x0, y0, x1, y1))
                poly = _poly_from_box(box, crop_wh=(crop.width, crop.height))
                local_text = it.get('text') or it.get('content') or ''
                results.append({"text": local_text, "box": poly, "score": 1.0})
        except Exception:
            pass
        return {"code": 100, "data": results}

    def runBase64(self, imageBase64):
        """处理base64图片"""
        try:
            # 若启用双通道，则优先走 Paddle 检测 + 大模型识别
            if hasattr(self, 'local_config') and self.local_config.get('enable_dual_channel'):
                return self._run_dual_channel(imageBase64)
            # 预处理图像
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
            
            # 发送请求（默认重试3次）
            max_retries = 3
            
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
            prompt = f"""识别图片文字并返回坐标，语言：{lang_instruction}
输出JSON格式：{{"texts": [{{"text": "文字内容", "box": [[x1,y1],[x2,y2],[x3,y3],[x4,y4]]}}]}}
坐标为像素位置，左上角为原点。直接返回JSON，无其他内容。"""
        else:
            prompt = f"""识别图片中的文字，语言：{lang_instruction}。保持原有格式，直接返回文字内容。"""
        
        return prompt
    
    def _send_request(self, image_base64, prompt):
        """发送API请求"""
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
                            box = item.get("box") or item.get("bbox") or item.get("rect")
                        if box:
                            mapped_box = self._map_coordinates_to_original(box)
                            result_data.append({
                                "text": item.get("text", ""),
                                "box": mapped_box,
                                "score": 1.0
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
        """将坐标映射回原始图像尺寸，支持归一化与矩形格式"""
        # 没有原始尺寸，直接返回
        if not self.original_size:
            return box
        
        # 推断处理后尺寸
        proc_w, proc_h = None, None
        if self.processed_size:
            proc_w, proc_h = self.processed_size
        elif self.scale_ratio != 1.0:
            proc_w = int(self.original_size[0] * self.scale_ratio)
            proc_h = int(self.original_size[1] * self.scale_ratio)
        else:
            proc_w, proc_h = self.original_size
        
        def map_point(x, y):
            # 如果是归一化坐标（0..1），先映射到处理后尺寸
            if 0.0 <= x <= 1.0 and 0.0 <= y <= 1.0:
                x = x * proc_w
                y = y * proc_h
            # 映射回原始尺寸
            if self.scale_ratio and self.scale_ratio != 1.0:
                x = x / self.scale_ratio
                y = y / self.scale_ratio
            return [int(round(x)), int(round(y))]
        
        try:
            # 情况1：四点多边形 [[x1,y1],...]
            if isinstance(box, list) and len(box) == 4 and all(isinstance(p, (list, tuple)) and len(p) == 2 for p in box):
                return [map_point(p[0], p[1]) for p in box]
            
            # 情况2：矩形数组 [x, y, w, h]
            if isinstance(box, list) and len(box) == 4 and all(isinstance(v, (int, float)) for v in box):
                x, y, w, h = box
                p1 = map_point(x, y)
                p2 = map_point(x + w, y)
                p3 = map_point(x + w, y + h)
                p4 = map_point(x, y + h)
                return [p1, p2, p3, p4]
            
            # 情况3：字典矩形 {left, top, width, height} 或 {x, y, w, h}
            if isinstance(box, dict):
                x = box.get('left', box.get('x'))
                y = box.get('top', box.get('y'))
                w = box.get('width', box.get('w'))
                h = box.get('height', box.get('h'))
                if x is not None and y is not None and w is not None and h is not None:
                    p1 = map_point(x, y)
                    p2 = map_point(x + w, y)
                    p3 = map_point(x + w, y + h)
                    p4 = map_point(x, y + h)
                    return [p1, p2, p3, p4]
            
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
        
        # 按行分割文本
        lines = [line.strip() for line in content.split('\n') if line.strip()]
        
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

