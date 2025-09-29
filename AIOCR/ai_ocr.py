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
# class OpenAIProvider(BaseProvider):
#     """OpenAI服务提供商"""
#     
#     def get_default_api_base(self):
#         return "https://api.openai.com/v1"
#         
#     def get_default_model(self):
#         return "gpt-4o"
#         
#     def build_headers(self):
#         return {
#             "Content-Type": "application/json",
#             "Authorization": f"Bearer {self.api_key}"
#         }
#         
#     def build_payload(self, image_base64, prompt):
#         return {
#             "model": self.model or self.get_default_model(),
#             "messages": [
#                 {
#                     "role": "user",
#                     "content": [
#                         {"type": "text", "text": prompt},
#                         {
#                             "type": "image_url",
#                             "image_url": {
#                                 "url": f"data:image/jpeg;base64,{image_base64}"
#                             }
#                         }
#                     ]
#                 }
#             ],
#             "max_tokens": 5000
#         }
#         
#     def parse_response(self, response_text):
#         try:
#             data = json.loads(response_text)
#             if "choices" in data and len(data["choices"]) > 0:
#                 content = data["choices"][0]["message"]["content"]
#                 return content
#             else:
#                 return None
#         except Exception as e:
#             raise Exception(f"解析OpenAI响应失败: {str(e)}")

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
            raise Exception(f"解析硅基流动响应失败: {str(e)}")

# 阿里云百炼 Provider
class AlibabaProvider(BaseProvider):
    """阿里云百炼服务提供商"""

    def get_default_api_base(self):
        # 已修正为兼容模式地址（问题1的修改）
        return "https://dashscope.aliyuncs.com/compatible-mode/v1"

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
            # 1. 移除`input`外层，将`messages`直接放在根节点
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},  # 明确文本类型
                        # 2. 图像内容使用`image_url`格式（符合OpenAI规范）
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_base64}"
                            }
                        }
                    ]
                }
            ],
            "parameters": {
                "max_tokens": 5000
            }
        }

    def parse_response(self, response_text):
        try:
            data = json.loads(response_text)
            # 兼容模式的响应结构与OpenAI一致，直接从根节点的`choices`提取内容
            if "choices" in data and len(data["choices"]) > 0:
                content = data["choices"][0]["message"]["content"]
                return content
            else:
                return None
        except Exception as e:
            raise Exception(f"解析阿里云百炼响应失败: {str(e)}")

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
# class XAIProvider(BaseProvider):
#     def get_default_api_base(self):
#         return "https://api.x.ai/v1"
#
#     def get_default_model(self):
#         return ""
#
#     def build_headers(self):
#         return {
#             "Content-Type": "application/json",
#             "Authorization": f"Bearer {self.api_key}"
#         }
#
#     def build_payload(self, image_base64, prompt):
#         return {
#             "model": self.model or self.get_default_model(),
#             "messages": [
#                 {
#                     "role": "user",
#                     "content": [
#                         {"type": "text", "text": prompt},
#                         {
#                             "type": "image_url",
#                             "image_url": {
#                                 "url": f"data:image/jpeg;base64,{image_base64}"
#                             }
#                         }
#                     ]
#                 }
#             ]
#         }
#
#     def parse_response(self, response_text):
#         try:
#             data = json.loads(response_text)
#             if "choices" in data and len(data["choices"]) > 0:
#                 content = data["choices"][0]["message"]["content"]
#                 return content
#             else:
#                 return None
#         except Exception as e:
#             raise Exception(f"解析xAI响应失败: {str(e)}")

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
            raise Exception(f"解析魔搭响应失败: {str(e)}")


# MinerU Provider
class MinerUProvider(BaseProvider):
    """MinerU服务提供商"""

    def get_default_api_base(self):
        return "https://mineru.net/api/v4"

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
            raise Exception(f"解析MinerU响应失败: {str(e)}")

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


# Groq Provider
# 修改GroqProvider类 (ai_ocr.py #startLine: 501 #endLine: 545)
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
            "thinking_mode":False
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
            # "openai": OpenAIProvider,
            "gemini": GeminiProvider,
            # "xai": XAIProvider,
            "openrouter": OpenRouterProvider,
            "siliconflow": SiliconFlowProvider,
            "doubao": DoubaoProvider,
            "alibaba": AlibabaProvider,
            "zhipu": ZhipuProvider,
            "mineru": MinerUProvider,
            "ollama": OllamaProvider,
            "groq": GroqProvider,
            "infinigence": InfinigenceProvider,
            "mistral": MistralProvider,
            "modelscope": ModelScopeProvider, # 新增：魔搭 Provider
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
        self.scale_ratio = 1.0     # 保存缩放比例

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
            
            # 兼容新旧键名
            timeout = self.global_config.get("a_timeout", self.global_config.get("timeout", 30))
            proxy_url = self.global_config.get("z_proxy_url", self.global_config.get("proxy_url", ""))
            
            if not api_key:
                return f"[Error] {provider_name} 的API密钥不能为空，请在设置中配置"
            
            if not model:
                return f"[Error] {provider_name} 的模型不能为空，请在设置中配置"
            
            # 创建Provider，使用内置的API基础URL
            self.provider = ProviderFactory.create_provider(
                provider_name, api_key, None, model, timeout, proxy_url
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
    
    def runBase64(self, imageBase64):
        """处理base64图片"""
        try:
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
                return image_base64

            # 只在需要时进行转换
            if need_convert:
                image = image.convert('RGB')

            # 只在需要时进行缩放
            if need_resize:
                self.scale_ratio = max_size / max(image.size)
                new_size = (int(image.size[0] * self.scale_ratio), int(image.size[1] * self.scale_ratio))
                image = image.resize(new_size, Image.Resampling.LANCZOS)
            else:
                self.scale_ratio = 1.0

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
            self.original_size = None
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
            url = f"{api_base}/chat/completions" #原地址：/services/aigc/text-generation/generation
        elif provider_name == "zhipu":
            url = f"{api_base}/chat/completions"
        elif provider_name == "mineru":
            url = f"{api_base}/extract/task"
        elif provider_name == "ollama":
            url = f"{api_base}/generate"
        elif provider_name == "mistral":
            url = f"{api_base}/chat/completions" # Mistral OCR专用端点
        else:
            url = f"{api_base}/chat/completions"
        
        # 构建请求头和载荷
        headers = self.provider.build_headers()
        payload = self.provider.build_payload(image_base64, prompt)
        
        # 发送请求
        response = self.http_client.post(url, headers, json.dumps(payload))
        
        if response['status_code'] != 200:
            # raise Exception(f"API请求失败 (状态码: {response['status_code']}): {response['text']}")
            error_msg = f"Groq API错误 (状态码: {response['status_code']}): {response['text']}"
            # 补充常见错误提示
            if response['status_code'] == 413:
                error_msg += "（可能是图像过大，超过4MB限制）"
            elif response['status_code'] == 400:
                error_msg += "（可能是分辨率超限或格式错误）"
            raise Exception(error_msg)
        
        return response['text']
    
    def _convert_to_umi_format(self, content, config):
        """转换为Umi格式"""
        output_format = config.get("output_format", "text_only")
        
        if output_format == "with_coordinates":
            return self._parse_text_with_coordinates(content)
        else:
            return self._parse_text_only(content)
    
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

            # 尝试解析JSON
            if content.strip().startswith('{'):
                data = json.loads(content)
                if "texts" in data and isinstance(data["texts"], list):
                    result_data = []
                    for item in data["texts"]:
                        if "text" in item and "box" in item:
                            # 映射坐标到原始图像尺寸
                            mapped_box = self._map_coordinates_to_original(item["box"])
                            result_data.append({
                                "text": item["text"],
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
        """将坐标映射回原始图像尺寸"""
        # 快速检查：如果没有缩放或无原始尺寸信息，直接返回
        if not self.original_size or self.scale_ratio == 1.0:
            return box

        # 快速映射：批量处理坐标
        try:
            mapped_box = []
            for point in box:
                if isinstance(point, (list, tuple)) and len(point) == 2:
                    x, y = point
                    mapped_box.append([int(x / self.scale_ratio), int(y / self.scale_ratio)])
                else:
                    mapped_box.append(point)
            return mapped_box
        except:
            # 如果映射失败，返回原坐标
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
