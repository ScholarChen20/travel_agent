"""
语音输入服务

功能：
1. 语音转文字（Speech-to-Text）
2. 支持多种语音识别引擎

支持的引擎：
- OpenAI Whisper API（推荐）
- 本地Whisper模型
- Azure Speech Services
"""

import base64
import io
from typing import Optional, Literal
from loguru import logger

from ..config import get_settings


class VoiceService:
    """语音服务类"""

    def __init__(self, engine: Literal["openai", "local", "azure"] = "openai"):
        """
        初始化语音服务

        Args:
            engine: 语音识别引擎类型
        """
        self.settings = get_settings()
        self.engine = engine
        logger.info(f"语音服务已初始化 (引擎: {engine})")

    async def transcribe(
        self,
        audio_data: str,
        language: str = "zh"
    ) -> str:
        """
        语音转文字

        Args:
            audio_data: Base64编码的音频数据
            language: 语言代码（zh/en等）

        Returns:
            str: 识别的文本
        """
        try:
            # 解码Base64音频数据
            audio_bytes = base64.b64decode(audio_data)

            # 根据引擎类型调用不同的识别方法
            if self.engine == "openai":
                text = await self._transcribe_openai(audio_bytes, language)
            elif self.engine == "local":
                text = await self._transcribe_local(audio_bytes, language)
            elif self.engine == "azure":
                text = await self._transcribe_azure(audio_bytes, language)
            else:
                raise ValueError(f"不支持的引擎类型: {self.engine}")

            logger.info(f"语音识别成功: {text[:50]}...")
            return text

        except Exception as e:
            logger.error(f"语音识别失败: {str(e)}")
            raise

    async def _transcribe_openai(self, audio_bytes: bytes, language: str) -> str:
        """
        使用OpenAI Whisper API进行语音识别

        Args:
            audio_bytes: 音频字节数据
            language: 语言代码

        Returns:
            str: 识别的文本
        """
        try:
            import openai

            # 配置OpenAI客户端
            client = openai.OpenAI(api_key=self.settings.openai_api_key)

            # 创建临时文件对象
            audio_file = io.BytesIO(audio_bytes)
            audio_file.name = "audio.wav"

            # 调用Whisper API
            response = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                language=language
            )

            return response.text

        except Exception as e:
            logger.error(f"OpenAI Whisper识别失败: {str(e)}")
            raise

    async def _transcribe_local(self, audio_bytes: bytes, language: str) -> str:
        """
        使用本地Whisper模型进行语音识别

        Args:
            audio_bytes: 音频字节数据
            language: 语言代码

        Returns:
            str: 识别的文本
        """
        try:
            import whisper
            import tempfile
            import os

            # 保存音频到临时文件
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
                temp_file.write(audio_bytes)
                temp_path = temp_file.name

            try:
                # 加载Whisper模型（使用base���型，平衡速度和准确度）
                model = whisper.load_model("base")

                # 识别音频
                result = model.transcribe(temp_path, language=language)

                return result["text"]

            finally:
                # 删除临时文件
                if os.path.exists(temp_path):
                    os.remove(temp_path)

        except Exception as e:
            logger.error(f"本地Whisper识别失败: {str(e)}")
            raise

    async def _transcribe_azure(self, audio_bytes: bytes, language: str) -> str:
        """
        使用Azure Speech Services进行语音识别

        Args:
            audio_bytes: 音频字节数据
            language: 语言代码

        Returns:
            str: 识别的文本
        """
        try:
            import azure.cognitiveservices.speech as speechsdk

            # 配置Azure Speech
            speech_config = speechsdk.SpeechConfig(
                subscription=self.settings.azure_speech_key,
                region=self.settings.azure_speech_region
            )

            # 设置语言
            language_map = {"zh": "zh-CN", "en": "en-US"}
            speech_config.speech_recognition_language = language_map.get(language, "zh-CN")

            # 创建音频配置
            audio_stream = speechsdk.audio.PushAudioInputStream()
            audio_stream.write(audio_bytes)
            audio_stream.close()

            audio_config = speechsdk.audio.AudioConfig(stream=audio_stream)

            # 创建识别器
            speech_recognizer = speechsdk.SpeechRecognizer(
                speech_config=speech_config,
                audio_config=audio_config
            )

            # 执行识别
            result = speech_recognizer.recognize_once()

            if result.reason == speechsdk.ResultReason.RecognizedSpeech:
                return result.text
            elif result.reason == speechsdk.ResultReason.NoMatch:
                raise ValueError("无法识别语音")
            elif result.reason == speechsdk.ResultReason.Canceled:
                cancellation = result.cancellation_details
                raise ValueError(f"识别被取消: {cancellation.reason}")

        except Exception as e:
            logger.error(f"Azure Speech识别失败: {str(e)}")
            raise


# ========== 全局实例（单例模式） ==========

_voice_service: Optional[VoiceService] = None


def get_voice_service(engine: Literal["openai", "local", "azure"] = "openai") -> VoiceService:
    """
    获取全局语音服务实例（单例）

    Args:
        engine: 语音识别引擎类型

    Returns:
        VoiceService: 语音服务实例
    """
    global _voice_service
    if _voice_service is None:
        _voice_service = VoiceService(engine=engine)
    return _voice_service
