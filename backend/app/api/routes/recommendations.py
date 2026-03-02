"""智能推荐系统API路由"""

from fastapi import APIRouter, Depends, Query, HTTPException
from typing import Optional, List
from ...services.recommendation_service import (
    RecommendationService,
    RecommendationRequest,
    RecommendationResponse
)
from ...utils.response import ApiResponse, ResponseCode

router = APIRouter(prefix="/recommendations", tags=["智能推荐系统"])


def get_recommendation_service() -> RecommendationService:
    """获取推荐服务实例"""
    return RecommendationService()


@router.get("/", summary="获取个性化推荐")
async def get_recommendations(
    user_id: Optional[str] = Query(None, description="用户ID"),
    preferences: Optional[str] = Query(None, description="兴趣标签，逗号分隔"),
    location: Optional[str] = Query(None, description="当前位置"),
    limit: int = Query(10, ge=1, le=50, description="返回数量"),
    recommendation_service: RecommendationService = Depends(get_recommendation_service)
):
    """
    获取个性化推荐，包括景点、餐厅、酒店等推荐
    """
    try:
        pref_list = preferences.split(",") if preferences else None
        request = RecommendationRequest(
            user_id=user_id,
            preferences=pref_list,
            location=location,
            limit=limit
        )
        result = recommendation_service.recommend(request)
        return ApiResponse.success(data=result.model_dump())
    except Exception as e:
        raise HTTPException(
            status_code=ResponseCode.INTERNAL_ERROR,
            detail=f"推荐系统错误: {str(e)}"
        )
