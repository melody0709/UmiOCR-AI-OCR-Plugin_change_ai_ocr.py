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
    
    def start(self, argd):
        """启动引擎（对于API类型的OCR，通常不需要特殊启动过程）"""
        # 保存局部配置
        self.language = argd.get('language', 'auto')
        self.output_format = argd.get('output_format', 'text_only')
        return ""
    
    def stop(self):
        """停止引擎"""
        pass
    
    def testConnection(self):
        """测试API连接"""
        try:
            # 验证API密钥
            if not self.api_key:
                return {"code": 102, "data": "API密钥不能为空，请在全局设置中配置API密钥"}
            
            # 创建一个简单的测试图片（1x1像素的白色图片）
            test_image = Image.new('RGB', (1, 1), color='white')
            buffer = BytesIO()
            test_image.save(buffer, format='PNG')
            test_image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
            
            # 尝试使用genai库进行测试
            if self.use_genai:
                try:
                    self._ensure_client_initialized()
                    # 使用genai库进行简单的测试请求
                    response = self.client.models.generate_content(
                        model=self.model_name,
                        contents=[
                            types.Content(
                                parts=[
                                    types.Part.from_text("请识别这张图片中的文字，如果没有文字请回复'无文字'。"),
                                    types.Part.from_image_data(
                                        mime_type="image/png",
                                        data=base64.b64decode(test_image_base64)
                                    )
                                ]
                            )
                        ]
                    )
                    if response and response.text:
                        return {"code": 100, "data": "连接成功！API密钥有效，模型响应正常。"}
                    else:
                        return {"code": 102, "data": "连接失败：API响应为空"}
                except Exception as e:
                    # genai失败，尝试REST API
                    self.use_genai = False
            
            # 使用REST API进行测试
            try:
                url = f"{self.base_url}/{self.model_name}:generateContent?key={self.api_key}"
                
                payload = {
                    "contents": [{
                        "parts": [
                            {"text": "请识别这张图片中的文字，如果没有文字请回复'无文字'。"},
                            {
                                "inline_data": {
                                    "mime_type": "image/png",
                                    "data": test_image_base64
                                }
                            }
                        ]
                    }]
                }
                
                headers = {
                    'Content-Type': 'application/json'
                }
                
                response = self.http_client.post(
                    url,
                    headers=headers,
                    data=json.dumps(payload)
                )
                
                if response['status_code'] == 200:
                    result = response['json']()
                    if 'candidates' in result and len(result['candidates']) > 0:
                        return {"code": 100, "data": "连接成功！API密钥有效，模型响应正常。"}
                    else:
                        return {"code": 102, "data": "连接失败：API响应格式异常"}
                else:
                    error_msg = response['text']
                    if response['status_code'] == 401:
                        return {"code": 102, "data": "连接失败：API密钥无效或已过期"}
                    elif response['status_code'] == 403:
                        return {"code": 102, "data": "连接失败：API访问被拒绝，请检查API密钥权限"}
                    elif response['status_code'] == 429:
                        return {"code": 102, "data": "连接失败：API请求频率超限，请稍后重试"}
                    else:
                        return {"code": 102, "data": f"连接失败：HTTP {response['status_code']} - {error_msg}"}
                        
            except Exception as e:
                return {"code": 102, "data": f"连接失败：{str(e)}"}
                
        except Exception as e:
            return {"code": 102, "data": f"测试连接时发生错误：{str(e)}"}
    
    def runPath(self, imgPath: str):
        """通过图片路径进行OCR识别"""
        try:
            with open(imgPath, 'rb') as f:
                image_bytes = f.read()
            return self.runBytes(image_bytes)
        except Exception as e:
            return self._create_error_result(f"读取图片文件失败: {str(e)}")
    
    def runBytes(self, imageBytes):
        """通过图片字节流进行OCR识别"""
        try:
            # 将字节流转换为base64
            image_base64 = base64.b64encode(imageBytes).decode('utf-8')
            return self.runBase64(image_base64)
        except Exception as e:
            return self._create_error_result(f"处理图片字节流失败: {str(e)}")
    
    def runBase64(self, imageBase64):
        """通过base64编码的图片进行OCR识别"""
        try:
            # 确保客户端已初始化
            self._ensure_client_initialized()
            
            # 使用当前的局部配置
            argd = {
                'language': getattr(self, 'language', 'auto'),
                'output_format': getattr(self, 'output_format', 'text_only')
            }
            
            if self.use_genai:
                return self._run_with_genai(imageBase64, argd)
            else:
                return self._run_with_rest_api(imageBase64, argd)
        except Exception as e:
            return self._create_error_result(f"OCR识别失败: {str(e)}")
    
    def _run_with_genai(self, imageBase64, argd):
        """使用google-genai库进行OCR识别"""
        try:
            # 获取原始图片尺寸
            original_image_data = base64.b64decode(imageBase64)
            original_image = Image.open(BytesIO(original_image_data))
            original_width, original_height = original_image.size
            
            # 预处理图片并获取处理后的尺寸
            processed_base64, processed_size = self._preprocess_image(imageBase64, argd)
            processed_width, processed_height = processed_size
            
            # 将base64转换为字节数据
            image_bytes = base64.b64decode(processed_base64)
            
            # 构建提示词
            prompt = self._build_prompt(argd)
            
            # 发送请求并重试
            for attempt in range(self.max_retries + 1):
                try:
                    response = self.client.models.generate_content(
                        model=self.model_name,
                        contents=[
                            types.Part.from_bytes(
                                data=image_bytes,
                                mime_type='image/jpeg',
                            ),
                            prompt
                        ]
                    )
                    
                    if response.text:
                        return self._convert_genai_response_to_umi_format(response.text, argd, processed_width, processed_height, original_width, original_height)
                    else:
                        return self._create_empty_result()
                        
                except Exception as e:
                    if attempt == self.max_retries:
                        return self._create_error_result(f"API请求失败（已重试{self.max_retries}次）: {str(e)}")
                    time.sleep(1)  # 重试前等待1秒
            
            return self._create_error_result("API请求失败：超过最大重试次数")
            
        except Exception as e:
            return self._create_error_result(f"GenAI OCR识别失败: {str(e)}")
    
    def _run_with_rest_api(self, imageBase64, argd):
        """使用REST API进行OCR识别"""
        try:
            # 获取原始图片尺寸
            original_image_data = base64.b64decode(imageBase64)
            original_image = Image.open(BytesIO(original_image_data))
            original_width, original_height = original_image.size
            
            # 预处理图片并获取处理后的尺寸
            processed_base64, processed_size = self._preprocess_image(imageBase64, argd)
            processed_width, processed_height = processed_size
            
            # 构建请求
            prompt = self._build_prompt(argd)
            request_data = self._build_request_data(processed_base64, prompt)
            
            # 发送请求并重试
            for attempt in range(self.max_retries + 1):
                try:
                    response = self._send_request(request_data)
                    if response:
                        return self._convert_to_umi_format(response, argd, processed_width, processed_height, original_width, original_height)
                except Exception as e:
                    if attempt == self.max_retries:
                        return self._create_error_result(f"API请求失败（已重试{self.max_retries}次）: {str(e)}")
                    time.sleep(1)  # 重试前等待1秒
            
            return self._create_error_result("API请求失败：超过最大重试次数")
            
        except Exception as e:
            return self._create_error_result(f"REST API OCR识别失败: {str(e)}")
    
    def _preprocess_image(self, image_base64, argd):
        """预处理图片（调整大小、质量等）"""
        try:
            max_size = argd.get('max_image_size', 1536)
            quality = argd.get('image_quality', 'auto')
            
            # 解码base64图片
            image_data = base64.b64decode(image_base64)
            image = Image.open(BytesIO(image_data))
            
            # 调整图片大小
            if max(image.size) > max_size:
                ratio = max_size / max(image.size)
                new_size = (int(image.width * ratio), int(image.height * ratio))
                image = image.resize(new_size, Image.Resampling.LANCZOS)
            
            # 转换为RGB（如果需要）
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # 保存为JPEG格式
            output = BytesIO()
            jpeg_quality = 95 if quality == 'high' else 85 if quality == 'medium' else 75
            if quality == 'auto':
                jpeg_quality = 90
            
            image.save(output, format='JPEG', quality=jpeg_quality, optimize=True)
            processed_data = output.getvalue()
            
            return base64.b64encode(processed_data).decode('utf-8'), image.size
            
        except Exception as e:
            # 如果预处理失败，返回原始图片
            return image_base64
    
    def _build_prompt(self, argd):
        """构建OCR提示词"""
        language = argd.get('language', 'auto')
        output_format = argd.get('output_format', 'text_only')
        
        # 基础提示词
        prompt = "Please perform OCR (Optical Character Recognition) on this image and extract all visible text."
        
        # 语言指定
        if language != 'auto':
            language_map = {
                'zh': 'Chinese',
                'en': 'English', 
                'ja': 'Japanese',
                'ko': 'Korean',
                'fr': 'French',
                'de': 'German',
                'es': 'Spanish',
                'ru': 'Russian'
            }
            lang_name = language_map.get(language, language)
            prompt += f" Focus on {lang_name} text."
        
        # 输出格式
        if output_format == 'with_coordinates':
            prompt += " Please provide the text along with precise bounding box coordinates in the format: [x1,y1,x2,y2] text_content. CRITICAL LAYOUT REQUIREMENTS: 1) Preserve the EXACT original text layout, including line breaks, paragraph spacing, and text alignment as they appear in the image. 2) Each line of text should be treated as a separate entry with its own coordinates. 3) Maintain the relative positioning of text blocks (headers, paragraphs, lists, etc.). 4) For coordinate requirements: Use pixel coordinates where (0,0) is the top-left corner. x1,y1 = top-left corner, x2,y2 = bottom-right corner. Ensure x1 < x2 and y1 < y2. All coordinates must be within image boundaries and be positive integers."
        else:
            prompt += " Please provide only the extracted text content, maintaining the EXACT original layout, line breaks, paragraph structure, and text formatting as they appear in the image. Preserve spacing between paragraphs and the hierarchical structure of the text."
        
        prompt += " If no text is found, return an empty response."
        
        return prompt
    
    def _build_request_data(self, image_base64, prompt):
        """构建API请求数据"""
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
            }],
            "generationConfig": {
                "temperature": 0.1,
                "maxOutputTokens": 4096
            }
        }
    
    def _send_request(self, request_data):
        """发送API请求"""
        url = f"{self.base_url}/{self.model_name}:generateContent?key={self.api_key}"
        
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'Umi-OCR-GeminiPlugin/1.0'
        }
        
        response = self.http_client.post(
            url=url,
            headers=headers,
            data=json.dumps(request_data)
        )
        
        if response['status_code'] != 200:
            raise Exception(f"API请求失败，状态码: {response['status_code']}, 响应: {response['text']}")
        
        result = response['json']()
        
        if 'error' in result:
            raise Exception(f"API返回错误: {result['error']}")
        
        return result
    
    def _convert_to_umi_format(self, api_response, argd, image_width=None, image_height=None, original_width=None, original_height=None):
        """将Gemini REST API响应转换为Umi-OCR格式"""
        try:
            # 提取文本内容
            candidates = api_response.get('candidates', [])
            if not candidates:
                return self._create_empty_result()
            
            content = candidates[0].get('content', {})
            parts = content.get('parts', [])
            if not parts:
                return self._create_empty_result()
            
            text_content = parts[0].get('text', '').strip()
            if not text_content:
                return self._create_empty_result()
            
            output_format = argd.get('output_format', 'text_only')
            
            if output_format == 'with_coordinates':
                # 对于坐标模式，也需要传递图像尺寸用于坐标验证
                final_width = original_width if original_width else image_width
                final_height = original_height if original_height else image_height
                return self._parse_text_with_coordinates(text_content, final_width, final_height)
            else:
                # 对于纯文本模式，使用原始图片尺寸
                final_width = original_width if original_width else image_width
                final_height = original_height if original_height else image_height
                return self._parse_text_only(text_content, final_width, final_height)
                
        except Exception as e:
            return self._create_error_result(f"解析API响应失败: {str(e)}")
    
    def _convert_genai_response_to_umi_format(self, response_text, argd, image_width=None, image_height=None, original_width=None, original_height=None):
        """将google-genai库响应转换为Umi-OCR格式"""
        try:
            if not response_text.strip():
                return self._create_empty_result()
            
            # 根据输出格式处理
            output_format = argd.get('output_format', 'text_only')
            
            if output_format == 'with_coordinates':
                # 对于坐标模式，也需要传递图像尺寸用于坐标验证
                final_width = original_width if original_width else image_width
                final_height = original_height if original_height else image_height
                return self._parse_text_with_coordinates(response_text, final_width, final_height)
            else:
                # 对于纯文本模式，使用原始图片尺寸
                final_width = original_width if original_width else image_width
                final_height = original_height if original_height else image_height
                return self._parse_text_only(response_text, final_width, final_height)
                
        except Exception as e:
            return self._create_error_result(f"GenAI响应解析失败: {str(e)}")
    
    def _parse_text_with_coordinates(self, text_content, image_width=None, image_height=None):
        """解析包含坐标的文本，保持原始文本的行和段落结构"""
        lines = text_content.split('\n')
        result_data = []
        
        # 设置默认图片尺寸
        if image_width is None or image_height is None:
            image_width = 800
            image_height = 600
        
        # 用于生成默认坐标的参数
        default_line_height = 20
        default_margin_left = 20
        current_default_y = 20
        
        for line in lines:
            line = line.strip()
            if not line:
                # 空行增加段落间距
                current_default_y += default_line_height * 0.8
                continue
            
            # 尝试匹配坐标格式 [x1,y1,x2,y2] text
            coord_match = re.match(r'\[(\d+),(\d+),(\d+),(\d+)\]\s*(.+)', line)
            if coord_match:
                x1, y1, x2, y2, text = coord_match.groups()
                x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                
                # 坐标验证和校准
                x1, y1, x2, y2 = self._validate_and_fix_coordinates(x1, y1, x2, y2, image_width, image_height)
                
                result_data.append({
                    "text": text.strip(),
                    "box": [[x1, y1], [x2, y1], [x2, y2], [x1, y2]],
                    "score": 0.95
                })
            else:
                # 如果没有坐标，生成智能默认坐标，保持文本结构
                text_content = line
                
                # 根据文本长度估算宽度
                char_width = 12
                estimated_width = len(text_content) * char_width
                text_width = min(estimated_width, image_width - default_margin_left * 2)
                text_width = max(text_width, 30)
                
                # 根据文本特征调整行高和位置
                line_height = default_line_height
                
                # 检测标题或特殊格式
                if len(text_content) <= 10 and not any(char in text_content for char in '，。、；：'):
                    line_height = default_line_height * 1.3
                    current_default_y += default_line_height * 0.3
                elif text_content.startswith(('1.', '2.', '3.', '4.', '5.', '•', '-', '*')):
                    # 列表项可能需要缩进
                    if text_content.startswith(('•', '-', '*')):
                        default_margin_left += 15
                
                y_start = current_default_y
                y_end = y_start + line_height
                
                # 确保坐标在图片范围内
                if y_end > image_height - 20:
                    y_start = image_height - line_height - 20
                    y_end = image_height - 20
                
                result_data.append({
                    "text": text_content,
                    "box": [[default_margin_left, y_start], [default_margin_left + text_width, y_start], 
                            [default_margin_left + text_width, y_end], [default_margin_left, y_end]],
                    "score": 0.95
                })
                
                # 更新下一行位置
                current_default_y = y_end + max(3, default_line_height * 0.2)
                
                # 重置缩进
                if default_margin_left > 20:
                    default_margin_left = 20
        
        return {
            "code": 100,
            "data": result_data
        }
    
    def _parse_text_only(self, text_content, image_width=None, image_height=None):
        """解析纯文本结果（无坐标信息），保持原始文本的行和段落结构"""
        # 保持原始换行符，包括空行（段落间距）
        original_lines = text_content.split('\n')
        result_data = []
        
        # 如果没有提供图片尺寸，使用默认值
        if image_width is None or image_height is None:
            image_width = 800
            image_height = 600
        
        # 计算基础参数
        total_lines = len([line for line in original_lines if line.strip()])  # 只计算非空行
        base_line_height = max(18, image_height // max(total_lines * 1.5, 15))  # 更合理的行高计算
        margin_left = 20
        margin_top = 20
        char_width_estimate = base_line_height * 0.55  # 字符宽度估算
        
        current_y = margin_top
        
        for line in original_lines:
            # 处理空行（段落间距）
            if not line.strip():
                # 空行增加段落间距
                current_y += base_line_height * 0.8
                continue
            
            # 处理非空行
            line_text = line.strip()
            
            # 根据文字长度和内容特征调整格式
            estimated_text_width = len(line_text) * char_width_estimate
            text_width = min(estimated_text_width, image_width - margin_left * 2)
            text_width = max(text_width, 30)  # 最小宽度
            
            # 根据行的特征调整行高和位置
            line_height = base_line_height
            
            # 检测可能的标题或特殊格式（短行、数字开头等）
            if len(line_text) <= 10 and not any(char in line_text for char in '，。、；：'):
                # 可能是标题，稍微增加行高和间距
                line_height = base_line_height * 1.3
                current_y += base_line_height * 0.3  # 标题前增加间距
            elif line_text.startswith(('1.', '2.', '3.', '4.', '5.', '•', '-', '*')):
                # 列表项，保持正常行高但可能需要缩进
                if line_text.startswith(('•', '-', '*')):
                    margin_left += 15  # 列表项缩进
            
            y_start = current_y
            y_end = y_start + line_height
            
            # 确保坐标不超出图片边界
            if y_end > image_height - margin_top:
                y_start = image_height - line_height - margin_top
                y_end = image_height - margin_top
            
            result_data.append({
                "text": line_text,
                "box": [[margin_left, y_start], [margin_left + text_width, y_start], [margin_left + text_width, y_end], [margin_left, y_end]],
                "score": 0.95
            })
            
            # 更新下一行的Y坐标
            current_y = y_end + max(3, base_line_height * 0.2)  # 行间距
            
            # 重置缩进（如果有的话）
            if margin_left > 20:
                margin_left = 20
        
        return {
            "code": 100,
            "data": result_data
        }
    
    def _create_empty_result(self):
        """创建空结果（图中没有文字）"""
        return {
            "code": 101,
            "data": ""
        }
    
    def _create_error_result(self, error_msg):
        """创建错误结果"""
        return {
            'code': 102,
            'data': error_msg
        }
    
    def _validate_and_fix_coordinates(self, x1, y1, x2, y2, image_width, image_height):
        """验证和校准坐标
        
        Args:
            x1, y1, x2, y2: 原始坐标
            image_width, image_height: 图像尺寸
            
        Returns:
            tuple: 校准后的坐标 (x1, y1, x2, y2)
        """
        # 使用默认图像尺寸如果未提供
        if image_width is None or image_height is None:
            image_width = 800
            image_height = 600
        
        # 确保坐标为非负数
        x1 = max(0, x1)
        y1 = max(0, y1)
        x2 = max(0, x2)
        y2 = max(0, y2)
        
        # 确保坐标在图像边界内
        x1 = min(x1, image_width - 1)
        y1 = min(y1, image_height - 1)
        x2 = min(x2, image_width - 1)
        y2 = min(y2, image_height - 1)
        
        # 确保坐标顺序正确 (x1 < x2, y1 < y2)
        if x1 >= x2:
            # 如果x坐标顺序错误，交换它们
            x1, x2 = x2, x1
            # 确保至少有1像素的宽度
            if x1 == x2:
                x2 = min(x1 + 1, image_width - 1)
        
        if y1 >= y2:
            # 如果y坐标顺序错误，交换它们
            y1, y2 = y2, y1
            # 确保至少有1像素的高度
            if y1 == y2:
                y2 = min(y1 + 1, image_height - 1)
        
        # 确保边界框有最小尺寸（至少1x1像素）
        if x2 - x1 < 1:
            x2 = min(x1 + 1, image_width - 1)
        if y2 - y1 < 1:
            y2 = min(y1 + 1, image_height - 1)
        
        return x1, y1, x2, y2