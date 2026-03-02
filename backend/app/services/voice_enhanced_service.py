"""语音交互增强服务"""

import speech_recognition as sr
from gtts import gTTS
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
import json
import os
from ..database.redis_client import get_redis_client
from ..config import get_settings

settings = get_settings()
redis_client = get_redis_client()


class VoiceCommandRequest(BaseModel):
    """语音命令请求"""
    voice_data: str = Field(..., description="Base64编码的语音数据")
    language: str = Field(default="zh-CN", description="语言代码")


class VoiceCommandResponse(BaseModel):
    """语音命令响应"""
    recognized_text: str = Field(..., description="识别出的文本")
    intent: str = Field(..., description="识别出的意图")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="提取的参数")
    response_text: str = Field(..., description="回复文本")
    response_voice: Optional[str] = Field(None, description="Base64编码的回复语音")
    processed_at: datetime = Field(default_factory=datetime.now, description="处理时间")


class VoiceRecognizeRequest(BaseModel):
    """语音识别请求"""
    voice_data: str = Field(..., description="Base64编码的语音数据")
    language: str = Field(default="zh-CN", description="语言代码")


class VoiceRecognizeResponse(BaseModel):
    """语音识别响应"""
    recognized_text: str = Field(..., description="识别出的文本")
    language: str = Field(..., description="识别出的语言")
    confidence: float = Field(default=0.0, description="置信度")


class VoiceSynthesizeRequest(BaseModel):
    """语音合成请求"""
    text: str = Field(..., description="待合成的文本")
    language: str = Field(default="zh-CN", description="语言代码")


class VoiceSynthesizeResponse(BaseModel):
    """语音合成响应"""
    voice_data: str = Field(..., description="Base64编码的语音数据")
    text: str = Field(..., description="合成的文本")
    language: str = Field(..., description="语言")


class VoiceEnhancedService:
    """语音交互增强服务"""

    def __init__(self):
        self.language = "zh-CN"
        self.recognizer = sr.Recognizer()
        self.intent_patterns = {
            "plan_trip": ["规划", "旅行", "行程", "安排"],
            "search_poi": ["找", "搜索", "查询", "附近"],
            "check_weather": ["天气", "气温", "下雨", "晴天"],
            "get_budget": ["预算", "花费", "支出", "省钱"],
            "navigate": ["导航", "路线", "怎么去", "怎么走"],
            "general_help": ["帮助", "怎么", "什么", "你好"]
        }

    def recognize_voice(self, request: VoiceRecognizeRequest) -> VoiceRecognizeResponse:
        """语音识别"""
        cache_key = f"voice:recognize:{hash(request.voice_data)}:{request.language}"
        cached_result = redis_client.get(cache_key)
        
        if cached_result:
            try:
                return VoiceRecognizeResponse(**json.loads(cached_result))
            except:
                pass

        recognized_text = self._do_recognize(request.voice_data, request.language)
        
        result = VoiceRecognizeResponse(
            recognized_text=recognized_text,
            language=request.language,
            confidence=0.85
        )

        redis_client.setex(cache_key, 3600, json.dumps(result.model_dump(), default=str))
        return result

    def _do_recognize(self, voice_data: str, language: str) -> str:
        """执行语音识别"""
        return "这是模拟的语音识别结果"

    def synthesize_voice(self, request: VoiceSynthesizeRequest) -> VoiceSynthesizeResponse:
        """语音合成"""
        cache_key = f"voice:synthesize:{hash(request.text)}:{request.language}"
        cached_result = redis_client.get(cache_key)
        
        if cached_result:
            try:
                return VoiceSynthesizeResponse(**json.loads(cached_result))
            except:
                pass

        voice_data = self._do_synthesize(request.text, request.language)
        
        result = VoiceSynthesizeResponse(
            voice_data=voice_data,
            text=request.text,
            language=request.language
        )

        redis_client.setex(cache_key, 86400, json.dumps(result.model_dump(), default=str))
        return result

    def _do_synthesize(self, text: str, language: str) -> str:
        """执行语音合成"""
        return "base64_encoded_audio_data"

    def process_voice_command(self, request: VoiceCommandRequest) -> VoiceCommandResponse:
        """处理语音命令"""
        recognized_text = self._do_recognize(request.voice_data, request.language)
        intent = self._parse_intent(recognized_text)
        parameters = self._extract_parameters(recognized_text, intent)
        response_text = self._generate_response(intent, parameters, recognized_text)
        
        response_voice = None
        if response_text:
            response_voice = self._do_synthesize(response_text, request.language)
        
        return VoiceCommandResponse(
            recognized_text=recognized_text,
            intent=intent,
            parameters=parameters,
            response_text=response_text,
            response_voice=response_voice
        )

    def _parse_intent(self, text: str) -> str:
        """解析用户意图"""
        text_lower = text.lower()
        for intent, keywords in self.intent_patterns.items():
            for keyword in keywords:
                if keyword in text_lower:
                    return intent
        return "unknown"

    def _extract_parameters(self, text: str, intent: str) -> Dict[str, Any]:
        """提取参数"""
        parameters = {}
        
        if intent == "plan_trip":
            parameters["city"] = "北京"
            parameters["days"] = 3
        elif intent == "search_poi":
            parameters["keywords"] = text
        elif intent == "check_weather":
            parameters["city"] = "北京"
        
        return parameters

    def _generate_response(self, intent: str, parameters: Dict, original_text: str) -> str:
        """生成回复"""
        responses = {
            "plan_trip": "好的，我来帮您规划旅行。请告诉我您想去哪个城市，以及旅行的时间？",
            "search_poi": f"我正在帮您搜索{parameters.get('keywords', '相关地点')}...",
            "check_weather": f"{parameters.get('city', '北京')}今天天气晴朗，气温25度。",
            "get_budget": "让我帮您查看一下当前的旅行预算情况。",
            "navigate": "我来为您规划最佳路线。",
            "general_help": "您好！我是您的旅行助手，可以帮您规划旅行、查询景点、查看天气等。请问有什么可以帮您的？",
            "unknown": "抱歉，我没有理解您的意思。请您再说一遍好吗？"
        }
        
        return responses.get(intent, responses["unknown"])
