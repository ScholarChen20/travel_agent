"""多语言支持API路由"""

from fastapi import APIRouter, Depends, HTTPException
from ...services.translation_service import (
    TranslationService,
    TextTranslationRequest,
    TextTranslationResponse,
    VoiceTranslationRequest,
    VoiceTranslationResponse
)
from ...utils.response import ApiResponse, ResponseCode

router = APIRouter(prefix="/translate", tags=["多语言支持"])


def get_translation_service() -> TranslationService:
    """获取翻译服务实例"""
    return TranslationService()


@router.post("/text", summary="文本翻译")
async def translate_text(
    request: TextTranslationRequest,
    translation_service: TranslationService = Depends(get_translation_service)
):
    """
    翻译文本
    """
    try:
        result = translation_service.translate_text(request)
        return ApiResponse.success(data=result.model_dump())
    except Exception as e:
        raise HTTPException(
            status_code=ResponseCode.INTERNAL_ERROR,
            detail=f"文本翻译失败: {str(e)}"
        )


@router.post("/voice", summary="语音翻译")
async def translate_voice(
    request: VoiceTranslationRequest,
    translation_service: TranslationService = Depends(get_translation_service)
):
    """
    翻译语音
    """
    try:
        result = translation_service.translate_voice(request)
        return ApiResponse.success(data=result.model_dump())
    except Exception as e:
        raise HTTPException(
            status_code=ResponseCode.INTERNAL_ERROR,
            detail=f"语音翻译失败: {str(e)}"
        )


@router.get("/languages", summary="获取支持的语言列表")
async def get_supported_languages(
    translation_service: TranslationService = Depends(get_translation_service)
):
    """
    获取系统支持的所有语言列表
    """
    try:
        languages = translation_service.get_supported_languages()
        return ApiResponse.success(data=languages)
    except Exception as e:
        raise HTTPException(
            status_code=ResponseCode.INTERNAL_ERROR,
            detail=f"获取语言列表失败: {str(e)}"
        )
