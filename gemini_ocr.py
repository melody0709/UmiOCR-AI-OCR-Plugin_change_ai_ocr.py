# -*- coding: utf-8 -*-
# Gemini OCR API Implementation

import json
import base64
import time
import re
from io import BytesIO
from PIL import Image

# 尝试导入google-genai库
try:
    from google import genai
    from google.genai import types
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False
    # 如果没有安装google-genai，使用REST API作为备选
    import urllib.request
    import urllib.parse
    import urllib.error

# 简化的HTTP请求类（备选方案）
class SimpleRequests:
    def __init__(self, timeout=30, proxy_url=None):
        self.timeout = timeout
        self.proxy_url = proxy_url
    
    def post(self, url, headers=None, data=None):
        """简化的POST请求实现"""
        try:
            # 准备请求
            req_data = data.encode('utf-8') if isinstance(data, str) else data
            req = urllib.request.Request(url, data=req_data, headers=headers or {})
            
            # 设置代理
            if self.proxy_url:
                proxy_handler = urllib.request.ProxyHandler({'http': self.proxy_url, 'https': self.proxy_url})
                opener = urllib.request.build_opener(proxy_handler)
                urllib.request.install_opener(opener)
            
            # 发送请求
            with urllib.request.urlopen(req, timeout=self.timeout) as response:
                response_data = response.read().decode('utf-8')
                return {
                    'status_code': response.getcode(),
                    'text': response_data,
                    'json': lambda: json.loads(response_data)
                }
        except Exception as e:
            return {
                'status_code': 500,
                'text': str(e),
                'json': lambda: {'error': str(e)}
            }

class Api:
    """Gemini OCR API类"""
    
    def __init__(self, globalArgd):
        """初始化API"""
        self.api_key = globalArgd.get('api_key', '')
        if not self.api_key:
            raise ValueError("API key cannot be empty")
        self.model = globalArgd.get('model', 'gemini-1.5-flash')
        self.timeout = globalArgd.get('timeout', 30)
        self.max_retries = globalArgd.get('max_retries', 3)
        self.proxy_url = globalArgd.get('proxy_url', '')
        
        # 初始化客户端（延迟到实际使用时验证API密钥）
        self.client = None
        self.use_genai = GENAI_AVAILABLE
        
        # 直接使用用户指定的模型名称
        self.model_name = self.model
        
        # 初始化REST API客户端
        self._init_rest_api()
        
        self.isInit = True
    
    def _init_rest_api(self):
        """初始化REST API客户端"""
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models"
        self.http_client = SimpleRequests(timeout=self.timeout, proxy_url=self.proxy_url)
    
    def _ensure_client_initialized(self):
        """确保客户端已初始化"""
        # 验证API密钥
        if not self.api_key:
            raise ValueError("[Error] Gemini API密钥不能为空")
        
        # 如果使用genai库且客户端未初始化
        if self.use_genai and self.client is None:
            try:
                self.client = genai.Client(api_key=self.api_key)
            except Exception as e:
                # 如果genai初始化失败，回退到REST API
                self.use_genai = False
                raise ValueError(f"[Error] Gemini API初始化失败: {str(e)}")

    def _prepare_image(self, image_bytes, max_size=None, quality=None):
        """准备图像数据"""
        try:
            # 打开图像
            image = Image.open(BytesIO(image_bytes))
            
            # 转换为RGB（如果需要）
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # 调整图像大小
            if max_size:
                # 计算缩放比例
                width, height = image.size
                max_dimension = max(width, height)
                
                if max_dimension > max_size:
                    scale = max_size / max_dimension
                    new_width = int(width * scale)
                    new_height = int(height * scale)
                    image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # 转换为字节
            output = BytesIO()
            
            # 设置质量
            if quality is None:
                quality = 85  # 默认质量
            elif quality == 'auto':
                quality = 85
            elif quality == 'high':
                quality = 95
            elif quality == 'medium':
                quality = 75
            elif quality == 'low':
                quality = 60
            
            image.save(output, format='JPEG', quality=quality, optimize=True)
            processed_bytes = output.getvalue()
            
            # 获取最终尺寸
            final_width, final_height = image.size
            
            return processed_bytes, final_width, final_height
            
        except Exception as e:
            raise ValueError(f"[Error] 图像处理失败: {str(e)}")
    
    def _encode_image_base64(self, image_bytes):
        """将图像编码为base64"""
        return base64.b64encode(image_bytes).decode('utf-8')
    
    def _build_prompt(self, language="auto", output_format="text_only"):
        """构建提示词"""
        # 基础提示
        base_prompt = "Please analyze this image and extract all visible text content."
        
        # 语言指定
        if language and language != "auto":
            language_map = {
                "zh": "Chinese",
                "en": "English", 
                "ja": "Japanese",
                "ko": "Korean",
                "fr": "French",
                "de": "German",
                "es": "Spanish",
                "ru": "Russian",
                "ar": "Arabic"
            }
            lang_name = language_map.get(language, language)
            base_prompt += f" Focus on {lang_name} text."
        
        # 输出格式指定
        if output_format == "with_coordinates":
            prompt = base_prompt + """

IMPORTANT: Please preserve the original text layout, including line breaks, paragraph spacing, and text alignment. For each line of text, provide the precise bounding box coordinates in the following format:

[x1,y1,x2,y2] text_content

Where:
- x1,y1 are the top-left coordinates
- x2,y2 are the bottom-right coordinates  
- text_content is the extracted text
- Coordinates should be integers in pixels
- Maintain the original line structure and paragraph breaks
- For empty lines or paragraph breaks, include them as separate entries
- Ensure text alignment and indentation are preserved

If no text is found, respond with: "No text detected in the image."
"""
        else:
            prompt = base_prompt + """

IMPORTANT: Please preserve the original text layout, including line breaks, paragraph spacing, and text alignment. Extract only the text content while maintaining:
- Original line breaks and paragraph structure
- Text indentation and alignment
- Spacing between paragraphs
- List formatting if present
- Title and heading hierarchy

Provide the extracted text exactly as it appears in the image, maintaining all formatting and structure.

If no text is found, respond with: "No text detected in the image."
"""
        
        return prompt
    
    def _call_genai_api(self, image_bytes, prompt, final_width, final_height):
        """使用google-genai库调用API"""
        try:
            self._ensure_client_initialized()
            
            # 编码图像
            image_base64 = self._encode_image_base64(image_bytes)
            
            # 构建请求
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=[
                    types.Content(
                        role="user",
                        parts=[
                            types.Part.from_text(prompt),
                            types.Part.from_inline_data(
                                mime_type="image/jpeg",
                                data=image_base64
                            )
                        ]
                    )
                ]
            )
            
            # 提取文本响应
            if response.candidates and len(response.candidates) > 0:
                candidate = response.candidates[0]
                if candidate.content and candidate.content.parts:
                    text_response = ""
                    for part in candidate.content.parts:
                        if hasattr(part, 'text') and part.text:
                            text_response += part.text
                    return text_response.strip()
            
            return "No text detected in the image."
            
        except Exception as e:
            raise ValueError(f"[Error] Gemini API调用失败: {str(e)}")
    
    def _call_rest_api(self, image_bytes, prompt, final_width, final_height):
        """使用REST API调用"""
        try:
            # 编码图像
            image_base64 = self._encode_image_base64(image_bytes)
            
            # 构建请求数据
            request_data = {
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
            
            # 发送请求
            url = f"{self.base_url}/{self.model_name}:generateContent?key={self.api_key}"
            headers = {
                'Content-Type': 'application/json'
            }
            
            response = self.http_client.post(
                url=url,
                headers=headers,
                data=json.dumps(request_data)
            )
            
            if response['status_code'] != 200:
                raise ValueError(f"API请求失败: {response['text']}")
            
            # 解析响应
            result = response['json']()
            
            if 'candidates' in result and len(result['candidates']) > 0:
                candidate = result['candidates'][0]
                if 'content' in candidate and 'parts' in candidate['content']:
                    text_response = ""
                    for part in candidate['content']['parts']:
                        if 'text' in part:
                            text_response += part['text']
                    return text_response.strip()
            
            return "No text detected in the image."
            
        except Exception as e:
            raise ValueError(f"[Error] REST API调用失败: {str(e)}")
    
    def _parse_text_with_coordinates(self, text_response, image_width=None, image_height=None):
        """解析包含坐标的文本响应"""
        results = []
        lines = text_response.split('\n')
        
        # 处理所有行，包括空行
        current_y = 10  # 起始Y坐标
        line_height = 20  # 基础行高
        
        for i, line in enumerate(lines):
            line = line.strip()
            
            # 处理空行（段落间距）
            if not line:
                results.append({
                    'text': '',
                    'box': [0, current_y, 0, current_y + 5]  # 空行用小高度表示段落间距
                })
                current_y += 15  # 段落间距
                continue
            
            # 尝试解析坐标格式: [x1,y1,x2,y2] text
            coord_match = re.match(r'\[(\d+),(\d+),(\d+),(\d+)\]\s*(.*)', line)
            
            if coord_match:
                # 找到坐标格式
                x1, y1, x2, y2, text = coord_match.groups()
                x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                
                # 验证坐标有效性
                if image_width and image_height:
                    x1 = max(0, min(x1, image_width))
                    y1 = max(0, min(y1, image_height))
                    x2 = max(x1, min(x2, image_width))
                    y2 = max(y1, min(y2, image_height))
                
                results.append({
                    'text': text.strip(),
                    'box': [x1, y1, x2, y2]
                })
                
                # 更新当前Y坐标
                current_y = max(current_y, y2 + 5)
            else:
                # 没有坐标，生成默认坐标
                text = line
                
                # 根据文本长度估算宽度
                char_width = 12  # 估算字符宽度
                estimated_width = len(text) * char_width
                
                # 智能调整行高和位置
                if len(text) <= 10:  # 可能是标题或短行
                    line_height = 25
                    current_y += 5  # 额外间距
                elif text.strip().startswith(('•', '-', '*', '1.', '2.', '3.')):  # 列表项
                    estimated_width += 20  # 缩进
                    x1 = 20
                else:
                    x1 = 10
                    line_height = 20
                
                # 确保坐标在图像范围内
                if image_width:
                    estimated_width = min(estimated_width, image_width - x1 - 10)
                if image_height:
                    current_y = min(current_y, image_height - line_height)
                
                x2 = x1 + estimated_width
                y2 = current_y + line_height
                
                results.append({
                    'text': text,
                    'box': [x1, current_y, x2, y2]
                })
                
                current_y = y2 + 5  # 行间距
        
        return results
    
    def _parse_text_only(self, text_response, image_width=None, image_height=None):
        """解析纯文本响应，生成默认坐标"""
        results = []
        
        # 处理原始行，包括空行
        original_lines = text_response.split('\n')
        
        # 计算基础参数
        non_empty_lines = [line for line in original_lines if line.strip()]
        total_lines = len(original_lines)
        
        # 使用图像尺寸或默认值
        img_width = image_width or 800
        img_height = image_height or 600
        
        # 动态计算行高
        if total_lines > 0:
            available_height = img_height - 40  # 留出上下边距
            base_line_height = max(15, min(30, available_height // total_lines))
        else:
            base_line_height = 20
        
        current_y = 20  # 起始Y坐标
        char_width = 10  # 估算字符宽度
        line_spacing = 5  # 固定行间距
        
        for line in original_lines:
            line_text = line.strip()
            
            # 处理空行（段落间距）
            if not line_text:
                results.append({
                    'text': '',
                    'box': [0, current_y, 0, current_y + 5]  # 空行用小高度表示段落间距
                })
                current_y += 15  # 段落间距
                continue
            
            # 根据文本长度动态调整宽度
            estimated_width = len(line_text) * char_width
            max_width = img_width - 40  # 留出左右边距
            text_width = min(estimated_width, max_width)
            
            # 智能调整行高和位置
            line_height = base_line_height
            x1 = 20  # 默认左边距
            
            if len(line_text) <= 10:  # 可能是标题或短行
                line_height = int(base_line_height * 1.2)
                current_y += 3  # 额外间距
            elif line_text.strip().startswith(('•', '-', '*', '1.', '2.', '3.')):  # 列表项
                x1 = 40  # 缩进
            
            x2 = x1 + text_width
            y2 = current_y + line_height
            
            # 确保坐标在图像范围内
            x2 = min(x2, img_width - 10)
            y2 = min(y2, img_height - 10)
            
            results.append({
                'text': line_text,
                'box': [x1, current_y, x2, y2]
            })
            
            current_y = y2 + line_spacing
        
        return results
    
    def _convert_genai_response_to_umi_format(self, text_response, output_format, final_width, final_height):
        """将Gemini API响应转换为Umi-OCR格式"""
        try:
            if not text_response or text_response.strip() == "No text detected in the image.":
                return {"code": 100, "data": []}
            
            # 根据输出格式解析响应
            if output_format == "with_coordinates":
                # 尝试解析坐标格式
                results = self._parse_text_with_coordinates(text_response, final_width, final_height)
            else:
                # 纯文本模式，生成默认坐标
                results = self._parse_text_only(text_response, final_width, final_height)
            
            # 过滤空文本结果
            filtered_results = []
            for result in results:
                if result['text'].strip():  # 只保留非空文本
                    filtered_results.append(result)
            
            return {"code": 100, "data": filtered_results}
            
        except Exception as e:
            return {"code": 102, "data": f"响应解析失败: {str(e)}"}
    
    def run(self, argd):
        """执行OCR识别"""
        try:
            # 获取参数
            image_bytes = argd.get("image_bytes")
            if not image_bytes:
                return {"code": 102, "data": "缺少图像数据"}
            
            language = argd.get("language", "auto")
            output_format = argd.get("output_format", "text_only")
            image_quality = argd.get("image_quality", "auto")
            max_image_size = argd.get("max_image_size", 1536)
            
            # 准备图像
            processed_image, final_width, final_height = self._prepare_image(
                image_bytes, 
                max_size=max_image_size, 
                quality=image_quality
            )
            
            # 构建提示词
            prompt = self._build_prompt(language, output_format)
            
            # 执行API调用（带重试）
            last_error = None
            for attempt in range(self.max_retries + 1):
                try:
                    if self.use_genai:
                        text_response = self._call_genai_api(processed_image, prompt, final_width, final_height)
                    else:
                        text_response = self._call_rest_api(processed_image, prompt, final_width, final_height)
                    
                    # 转换响应格式
                    return self._convert_genai_response_to_umi_format(text_response, output_format, final_width, final_height)
                    
                except Exception as e:
                    last_error = e
                    if attempt < self.max_retries:
                        time.sleep(1 * (attempt + 1))  # 递增延迟
                        continue
                    else:
                        break
            
            # 所有重试都失败
            return {"code": 102, "data": f"API调用失败: {str(last_error)}"}
            
        except Exception as e:
            return {"code": 102, "data": f"OCR处理失败: {str(e)}"}
