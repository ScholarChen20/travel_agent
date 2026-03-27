"""
RAG检索增强API路由
功能：
1. 景点、美食、酒店检索
2. 景点图片检索（兜底方案）
3. 数据索引管理
4. 健康检查
"""

from fastapi import APIRouter, Depends, Query, HTTPException, Body
from typing import Optional, List
from pydantic import BaseModel, Field
from loguru import logger

from ...services.rag import (
    RAGService,
    RAGSearchResult,
    get_rag_service
)
from ...utils.response import ApiResponse, ResponseCode

router = APIRouter(prefix="/rag", tags=["RAG检索增强"])


class SearchRequest(BaseModel):
    """搜索请求"""
    city: str = Field(..., description="城市名称", min_length=1, max_length=50)
    query: str = Field("", description="搜索关键词", max_length=200)
    n_results: int = Field(5, description="返回结果数量", ge=1, le=20)


class ImageSearchRequest(BaseModel):
    """图片搜索请求"""
    attraction_name: str = Field(..., description="景点名称", min_length=1, max_length=100)
    city: str = Field("", description="城市名称", max_length=50)
    n_results: int = Field(3, description="返回结果数量", ge=1, le=10)


class IndexResult(BaseModel):
    """索引结果"""
    success: bool
    message: str
    data: Optional[dict] = None


async def get_rag_service_instance() -> RAGService:
    """获取RAG服务实例"""
    return await get_rag_service()


@router.get("/health", summary="RAG服务健康检查")
async def health_check(
    rag_service: RAGService = Depends(get_rag_service_instance)
):
    """
    检查RAG服务健康状态
    
    返回各组件的健康状态：
    - embedding_service: 向量化服务状态
    - vector_store: 向量数据库状态
    - cache_size: 缓存大小
    """
    try:
        health = await rag_service.health_check()
        return ApiResponse.success(data=health)
    except Exception as e:
        logger.error(f"健康检查失败: {e}")
        return ApiResponse.internal_error(msg=str(e))


@router.get("/stats", summary="获取RAG统计信息")
async def get_stats(
    rag_service: RAGService = Depends(get_rag_service_instance)
):
    """
    获取RAG向量库统计信息
    
    返回：
    - documents_count: 文档数量
    - images_count: 图片数量
    - cache_size: 缓存大小
    """
    try:
        stats = rag_service.vector_store.get_collection_stats()
        stats['cache_size'] = len(rag_service._cache)
        return ApiResponse.success(data=stats)
    except Exception as e:
        logger.error(f"获取统计信息失败: {e}")
        return ApiResponse.internal_error(msg=str(e))


@router.get("/search/attractions", summary="搜索景点")
async def search_attractions(
    city: str = Query(..., description="城市名称", min_length=1, max_length=50),
    query: str = Query("", description="搜索关键词", max_length=200),
    n_results: int = Query(5, description="返回结果数量", ge=1, le=20),
    rag_service: RAGService = Depends(get_rag_service_instance)
):
    """
    搜索景点信息
    
    从RAG向量库中检索相关景点信息，用于：
    - 旅行报告生成增强
    - 景点推荐
    """
    try:
        results = await rag_service.search_attractions(
            city=city,
            query=query,
            n_results=n_results
        )
        
        return ApiResponse.success(data={
            "total": len(results),
            "city": city,
            "query": query,
            "results": [r.to_dict() for r in results]
        })
    except Exception as e:
        logger.error(f"搜索景点失败: {e}")
        return ApiResponse.internal_error(msg=f"搜索失败: {str(e)}")


@router.get("/search/food", summary="搜索美食")
async def search_food(
    city: str = Query(..., description="城市名称", min_length=1, max_length=50),
    query: str = Query("", description="搜索关键词", max_length=200),
    n_results: int = Query(5, description="返回结果数量", ge=1, le=20),
    rag_service: RAGService = Depends(get_rag_service_instance)
):
    """
    搜索美食推荐
    
    从RAG向量库中检索相关美食信息
    """
    try:
        results = await rag_service.search_food(
            city=city,
            query=query,
            n_results=n_results
        )
        
        return ApiResponse.success(data={
            "total": len(results),
            "city": city,
            "query": query,
            "results": [r.to_dict() for r in results]
        })
    except Exception as e:
        logger.error(f"搜索美食失败: {e}")
        return ApiResponse.internal_error(msg=f"搜索失败: {str(e)}")


@router.get("/search/hotels", summary="搜索酒店")
async def search_hotels(
    city: str = Query(..., description="城市名称", min_length=1, max_length=50),
    query: str = Query("", description="搜索关键词", max_length=200),
    n_results: int = Query(5, description="返回结果数量", ge=1, le=20),
    rag_service: RAGService = Depends(get_rag_service_instance)
):
    """
    搜索酒店推荐
    
    从RAG向量库中检索相关酒店信息
    """
    try:
        results = await rag_service.search_hotels(
            city=city,
            query=query,
            n_results=n_results
        )
        
        return ApiResponse.success(data={
            "total": len(results),
            "city": city,
            "query": query,
            "results": [r.to_dict() for r in results]
        })
    except Exception as e:
        logger.error(f"搜索酒店失败: {e}")
        return ApiResponse.internal_error(msg=f"搜索失败: {str(e)}")


@router.get("/search/images", summary="搜索景点图片")
async def search_attraction_images(
    attraction_name: str = Query(..., description="景点名称", min_length=1, max_length=100),
    city: str = Query("", description="城市名称", max_length=50),
    n_results: int = Query(3, description="返回结果数量", ge=1, le=10),
    rag_service: RAGService = Depends(get_rag_service_instance)
):
    """
    搜索景点图片（Unsplash兜底方案）
    
    当Unsplash无法获取图片时，从RAG向量库中检索相关景点图片
    """
    try:
        image_urls = await rag_service.search_attraction_images(
            attraction_name=attraction_name,
            city=city,
            n_results=n_results
        )
        
        return ApiResponse.success(data={
            "total": len(image_urls),
            "attraction_name": attraction_name,
            "city": city,
            "images": image_urls
        })
    except Exception as e:
        logger.error(f"搜索景点图片失败: {e}")
        return ApiResponse.internal_error(msg=f"搜索失败: {str(e)}")


@router.get("/context", summary="获取旅行上下文")
async def get_travel_context(
    city: str = Query(..., description="城市名称", min_length=1, max_length=50),
    preferences: str = Query("", description="用户偏好，逗号分隔", max_length=500),
    rag_service: RAGService = Depends(get_rag_service_instance)
):
    """
    获取旅行上下文（用于LLM增强）
    
    返回格式化的旅行参考信息，可直接注入到LLM提示词中
    """
    try:
        pref_list = [p.strip() for p in preferences.split(",") if p.strip()] if preferences else None
        
        context = await rag_service.get_travel_context(
            city=city,
            preferences=pref_list
        )
        
        return ApiResponse.success(data={
            "city": city,
            "preferences": pref_list,
            "context": context
        })
    except Exception as e:
        logger.error(f"获取旅行上下文失败: {e}")
        return ApiResponse.internal_error(msg=f"获取失败: {str(e)}")


@router.post("/cache/clear", summary="清空RAG缓存")
async def clear_cache(
    rag_service: RAGService = Depends(get_rag_service_instance)
):
    """
    清空RAG服务缓存
    
    用于在数据更新后刷新缓存
    """
    try:
        rag_service.clear_cache()
        return ApiResponse.success(msg="缓存已清空")
    except Exception as e:
        logger.error(f"清空缓存失败: {e}")
        return ApiResponse.internal_error(msg=str(e))


@router.post("/search/multi", summary="综合搜索")
async def multi_search(
    request: SearchRequest,
    rag_service: RAGService = Depends(get_rag_service_instance)
):
    """
    综合搜索景点、美食、酒店
    
    一次请求获取所有类型的推荐信息
    """
    try:
        attractions, foods, hotels = await rag_service.search_attractions(
            city=request.city,
            query=request.query,
            n_results=request.n_results
        ), await rag_service.search_food(
            city=request.city,
            query=request.query,
            n_results=request.n_results
        ), await rag_service.search_hotels(
            city=request.city,
            query=request.query,
            n_results=request.n_results
        )
        
        return ApiResponse.success(data={
            "city": request.city,
            "query": request.query,
            "attractions": {
                "total": len(attractions),
                "results": [r.to_dict() for r in attractions]
            },
            "foods": {
                "total": len(foods),
                "results": [r.to_dict() for r in foods]
            },
            "hotels": {
                "total": len(hotels),
                "results": [r.to_dict() for r in hotels]
            }
        })
    except Exception as e:
        logger.error(f"综合搜索失败: {e}")
        return ApiResponse.internal_error(msg=f"搜索失败: {str(e)}")
