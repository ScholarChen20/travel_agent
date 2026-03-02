"""多语言翻译服务"""

import requests
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
import json
from ..database.redis_client import get_redis_client
from ..config import get_settings

settings = get_settings()
redis_client = get_redis_client()


class TextTranslationRequest(BaseModel):
    """文本翻译请求"""
    text: str = Field(..., description="待翻译文本")
    from_lang: str = Field(default="auto", description="源语言代码，auto为自动检测")
    to_lang: str = Field(..., description="目标语言代码")


class TextTranslationResponse(BaseModel):
    """文本翻译响应"""
    original_text: str = Field(..., description="原文")
    translated_text: str = Field(..., description="译文")
    from_lang: str = Field(..., description="源语言")
    to_lang: str = Field(..., description="目标语言")
    translated_at: datetime = Field(default_factory=datetime.now, description="翻译时间")


class VoiceTranslationRequest(BaseModel):
    """语音翻译请求"""
    voice_data: str = Field(..., description="Base64编码的语音数据")
    from_lang: str = Field(..., description="源语言")
    to_lang: str = Field(..., description="目标语言")


class VoiceTranslationResponse(BaseModel):
    """语音翻译响应"""
    recognized_text: str = Field(..., description="识别出的文本")
    translated_text: str = Field(..., description="翻译文本")
    from_lang: str = Field(..., description="源语言")
    to_lang: str = Field(..., description="目标语言")
    translated_at: datetime = Field(default_factory=datetime.now, description="翻译时间")


class TranslationService:
    """翻译服务"""

    def __init__(self):
        self.translation_api_key = ""
        self.supported_languages = {
            "zh": "中文",
            "en": "英文",
            "ja": "日文",
            "ko": "韩文",
            "fr": "法文",
            "de": "德文",
            "es": "西班牙文",
            "ru": "俄文"
        }

    def translate_text(self, request: TextTranslationRequest) -> TextTranslationResponse:
        """翻译文本"""
        cache_key = f"translation:text:{hash(request.text)}:{request.from_lang}:{request.to_lang}"
        cached_result = redis_client.get(cache_key)
        
        if cached_result:
            try:
                return TextTranslationResponse(**json.loads(cached_result))
            except:
                pass

        translated_text = self._do_translate(request.text, request.from_lang, request.to_lang)
        
        result = TextTranslationResponse(
            original_text=request.text,
            translated_text=translated_text,
            from_lang=request.from_lang,
            to_lang=request.to_lang
        )

        redis_client.setex(cache_key, 86400, json.dumps(result.model_dump(), default=str))
        return result

    def _do_translate(self, text: str, from_lang: str, to_lang: str) -> str:
        """执行翻译"""
        mock_translations = {
            "zh-en": {
                "你好": "Hello",
                "故宫": "Forbidden City",
                "北京": "Beijing"
            },
            "en-zh": {
                "Hello": "你好",
                "Forbidden City": "故宫",
                "Beijing": "北京"
            }
        }
        
        key = f"{from_lang}-{to_lang}"
        if key in mock_translations and text in mock_translations[key]:
            return mock_translations[key][text]
        
        return f"[Translated] {text}"

    def translate_voice(self, request: VoiceTranslationRequest) -> VoiceTranslationResponse:
        """翻译语音"""
        recognized_text = self._recognize_voice(request.voice_data, request.from_lang)
        translated_text = self._do_translate(recognized_text, request.from_lang, request.to_lang)
        
        return VoiceTranslationResponse(
            recognized_text=recognized_text,
            translated_text=translated_text,
            from_lang=request.from_lang,
            to_lang=request.to_lang
        )

    def _recognize_voice(self, voice_data: str, lang: str) -> str:
        """识别语音"""
        return "这是模拟的语音识别结果"

    def get_supported_languages(self) -> dict:
        """获取支持的语言列表"""
        return self.supported_languages
