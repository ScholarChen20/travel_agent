"""语音交互增强API路由"""

from fastapi import APIRouter, Depends, HTTPException
from ...services.voice_enhanced_service import (
    VoiceEnhancedService,
    VoiceCommandRequest,
    VoiceCommandResponse,
    VoiceRecognizeRequest,
    VoiceRecognizeResponse,
    VoiceSynthesizeRequest,
    VoiceSynthesizeResponse
)
from ...utils.response import ApiResponse, ResponseCode

router = APIRouter(prefix="/voice", tags=["语音交互增强"])


def get_voice_service() -> VoiceEnhancedService:
    """获取语音服务实例"""
    return VoiceEnhancedService()


@router.post("/recognize", summary="语音识别")
async def recognize_voice(
    request: VoiceRecognizeRequest,
    voice_service: VoiceEnhancedService = Depends(get_voice_service)
):
    """
    将语音转换为文本
    """
    try:
        result = voice_service.recognize_voice(request)
        return ApiResponse.success(data=result.model_dump())
    except Exception as e:
        raise HTTPException(
            status_code=ResponseCode.INTERNAL_ERROR,
            detail=f"语音识别失败: {str(e)}"
        )


@router.post("/synthesize", summary="语音合成")
async def synthesize_voice(
    request: VoiceSynthesizeRequest,
    voice_service: VoiceEnhancedService = Depends(get_voice_service)
):
    """
    将文本转换为语音
    """
    try:
        result = voice_service.synthesize_voice(request)
        return ApiResponse.success(data=result.model_dump())
    except Exception as e:
        raise HTTPException(
            status_code=ResponseCode.INTERNAL_ERROR,
            detail=f"语音合成失败: {str(e)}"
        )


@router.post("/command", summary="处理语音命令")
async def process_voice_command(
    request: VoiceCommandRequest,
    voice_service: VoiceEnhancedService = Depends(get_voice_service)
):
    """
    处理语音命令，识别意图并生成回复
    """
    try:
        result = voice_service.process_voice_command(request)
        return ApiResponse.success(data=result.model_dump())
    except Exception as e:
        raise HTTPException(
            status_code=ResponseCode.INTERNAL_ERROR,
            detail=f"处理语音命令失败: {str(e)}"
        )
