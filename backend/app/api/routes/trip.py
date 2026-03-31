"""旅行规划API路由"""

import secrets
import asyncio
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, requests
from loguru import logger

from ...models.schemas import TripRequest
from ...agents.trip_planner_agent import get_trip_planner_agent
from ...middleware.auth_middleware import get_current_user_optional, CurrentUser
from ...services.travel_plan_service import get_travel_plan_service
from ...services.image_service import get_image_service
from ...utils.response import ApiResponse
from ...utils.cache_invalidator import get_cache_invalidator
from pyrate_limiter import Duration, Limiter, Rate
from fastapi_limiter.depends import RateLimiter
router = APIRouter(prefix="/trip", tags=["旅行规划"])

@router.post(
    "/plan",
    summary="生成旅行计划",
    description="根据用户输入的旅行需求,生成详细的旅行计划。支持匿名和登录用户。",
    dependencies=[Depends(RateLimiter(limiter=Limiter(Rate(2, Duration.SECOND * 10))))]  # 10秒内最多请求2次
)
async def plan_trip(
    request: TripRequest,
    current_user: Optional[CurrentUser] = Depends(get_current_user_optional)
):
    """
    生成旅行计划

    支持可选认证：
    - 匿名用户：生成计划并返回，不保存
    - 登录用户：生成计划，自动保存到MongoDB，返回plan_id

    Args:
        request: 旅行请求参数
        current_user: 当前用户（可选）

    Returns:
        旅行计划响应
    """
    try:
        is_authenticated = current_user is not None

        logger.info(
            f"{'='*60}\n"
            f"📥 收到旅行规划请求:\n"
            f"   城市: {request.city}\n"
            f"   日期: {request.start_date} - {request.end_date}\n"
            f"   天数: {request.travel_days}\n"
            f"   用户: {'已登录 (' + current_user.username + ')' if is_authenticated else '匿名'}\n"
            f"{'='*60}"
        )

        logger.debug("🔄 获取多智能体系统实例...")
        agent = get_trip_planner_agent()

        logger.info("🚀 开始生成旅行计划...")
        trip_plan = await agent.plan_trip(request)

        logger.info("✅ 旅行计划生成成功")

        logger.info("📸 开始获取景点图片...")
        await process_attraction_images(trip_plan, request.city)
        logger.info("✅ 景点图片处理完成")

        plan_id = None
        session_id = None

        if is_authenticated:
            try:
                session_id = f"session_{secrets.token_urlsafe(16)}"

                plan_service = get_travel_plan_service()
                cache_invalidator = get_cache_invalidator()

                # 先失效缓存
                await cache_invalidator.invalidate_content_stats_cache()
                await cache_invalidator.invalidate_business_stats_cache()

                plan_id = await plan_service.save_plan(
                    user_id=current_user.id,
                    session_id=session_id,
                    city=request.city,
                    start_date=request.start_date,
                    trip_plan=trip_plan.model_dump(),
                    preferences={
                        "travel_days": request.travel_days,
                        "end_date": request.end_date
                    }
                )

                logger.info(f"✅ 计划已保存: {plan_id} (用户: {current_user.username})")

            except Exception as e:
                logger.error(f"⚠️  保存计划失败: {str(e)}")

        response_data = trip_plan.model_dump()
        response_data["plan_id"] = plan_id
        response_data["session_id"] = session_id

        return ApiResponse.success(
            data=response_data,
            msg="旅行计划生成成功" + (" (已保存)" if plan_id else "")
        )

    except Exception as e:
        logger.error(f"❌ 生成旅行计划失败: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"生成旅行计划失败: {str(e)}"
        )


@router.get(
    "/health",
    summary="健康检查",
    description="检查旅行规划服务是否正常"
)
async def health_check():
    """健康检查"""
    try:
        agent = get_trip_planner_agent()

        return ApiResponse.success(
            data={
                "status": "healthy",
                "service": "trip-planner",
                "agent_name": agent.agent.name,
                "tools_count": len(agent.agent.list_tools())
            },
            msg="服务正常"
        )
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"服务不可用: {str(e)}"
        )


async def process_attraction_images(trip_plan, city: str):
    """
    处理旅行计划中的景点图片

    为每个景点获取图片并上传到 OSS

    Args:
        trip_plan: 旅行计划对象
        city: 城市名称
    """
    try:
        image_service = get_image_service()

        days = trip_plan.days if hasattr(trip_plan, 'days') else []

        tasks = []
        attraction_refs = []

        for day in days:
            if hasattr(day, 'attractions') and day.attractions:
                for attraction in day.attractions:
                    if not getattr(attraction, 'image_url', None):
                        attraction_name = getattr(attraction, 'name', '')
                        if attraction_name:
                            task = image_service.get_and_upload_attraction_image(
                                attraction_name,
                                city
                            )
                            tasks.append(task)
                            attraction_refs.append(attraction)

        if not tasks:
            logger.info("没有需要获取图片的景点")
            return

        logger.info(f"开始获取 {len(tasks)} 个景点的图片...")

        results = []
        for i in range(0, len(tasks), 5):
            batch = tasks[i:i+5]
            batch_results = await asyncio.gather(*batch, return_exceptions=True)
            results.extend(batch_results)

        success_count = 0
        for attraction, result in zip(attraction_refs, results):
            if isinstance(result, str) and result:
                attraction.image_url = result
                success_count += 1
            elif isinstance(result, Exception):
                logger.error(f"获取景点图片失败: {attraction.name}, 错误: {str(result)}")
            else:
                logger.warning(f"未获取到景点图片: {attraction.name}")

        logger.info(f"成功获取 {success_count}/{len(tasks)} 个景点的图片")

    except Exception as e:
        logger.error(f"处理景点图片失败: {str(e)}")
        # 不抛出异常，图片获取失败不应该影响整个旅行计划的生成
