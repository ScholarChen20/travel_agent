"""旅行规划API路由"""

import secrets
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends
from loguru import logger

from ...models.schemas import (
    TripRequest,
    TripPlanResponse,
    ErrorResponse
)
from ...agents.trip_planner_agent import get_trip_planner_agent
from ...middleware.auth_middleware import get_current_user_optional, CurrentUser
from ...services.travel_plan_service import get_travel_plan_service

router = APIRouter(prefix="/trip", tags=["旅行规划"])


@router.post(
    "/plan",
    response_model=TripPlanResponse,
    summary="生成旅行计划",
    description="根据用户输入的旅行需求,生成详细的旅行计划。支持匿名和登录用户。"
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
        # 判断用户类型
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

        # 获取Agent实例
        logger.debug("🔄 获取多智能体系统实例...")
        agent = get_trip_planner_agent()

        # 生成旅行计划
        logger.info("🚀 开始生成旅行计划...")
        trip_plan = agent.plan_trip(request)

        logger.info("✅ 旅行计划生成成功")

        # 如果用户已登录，保存计划到MongoDB
        plan_id = None
        session_id = None

        if is_authenticated:
            try:
                # 生成会话ID（为Phase 3对话系统准备）
                session_id = f"session_{secrets.token_urlsafe(16)}"

                # 保存计划
                plan_service = get_travel_plan_service()
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
                # 保存失败不影响返回计划
                logger.error(f"⚠️  保存计划失败: {str(e)}")

        # 构建响应
        response_data = trip_plan.model_dump()
        response_data["plan_id"] = plan_id  # 仅登录用户有此字段
        response_data["session_id"] = session_id  # 仅登录用户有此字段

        return TripPlanResponse(
            success=True,
            message="旅行计划生成成功" + (" (已保存)" if plan_id else ""),
            data=response_data
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
        # 检查Agent是否可用
        agent = get_trip_planner_agent()
        
        return {
            "status": "healthy",
            "service": "trip-planner",
            "agent_name": agent.agent.name,
            "tools_count": len(agent.agent.list_tools())
        }
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"服务不可用: {str(e)}"
        )

