"""
旅行计划管理路由

提供以下API：
- GET /api/plans - 查询用户的旅行计划列表
- GET /api/plans/{plan_id} - 获取计划详情
- PUT /api/plans/{plan_id} - 更新计划
- POST /api/plans/{plan_id}/favorite - 切换收藏状态
- POST /api/plans/{plan_id}/complete - 标记为已完成
- DELETE /api/plans/{plan_id} - 删除计划
- GET /api/plans/{plan_id}/export - 导出计划（JSON格式）
"""

from typing import Optional, List
from fastapi import APIRouter, HTTPException, status, Depends, Query
from pydantic import BaseModel, Field
from loguru import logger

from ...services.travel_plan_service import get_travel_plan_service
from ...middleware.auth_middleware import get_current_user, CurrentUser


router = APIRouter(prefix="/plans", tags=["旅行计划"])


# ========== 请求/响应模型 ==========

class PlanListResponse(BaseModel):
    """计划列表响应"""
    total: int = Field(..., description="总数")
    plans: List[dict] = Field(..., description="计划列表")


class PlanDetailResponse(BaseModel):
    """计划详情响应"""
    plan_id: str = Field(..., description="计划ID")
    user_id: int = Field(..., description="用户ID")
    city: str = Field(..., description="城市")
    start_date: str = Field(..., description="开始日期")
    end_date: Optional[str] = Field(None, description="结束日期")
    days: List[dict] = Field(..., description="每日行程")
    weather_info: Optional[List[dict]] = Field(default=[], description="天气信息")
    budget: Optional[dict] = Field(None, description="预算详情")
    overall_suggestions: Optional[str] = Field(None, description="总体建议")
    preferences: Optional[dict] = Field(default={}, description="用户偏好")
    is_favorite: bool = Field(default=False, description="是否收藏")
    is_completed: bool = Field(default=False, description="是否完成")
    created_at: str = Field(..., description="创建时间")
    updated_at: str = Field(..., description="更新时间")


class UpdatePlanRequest(BaseModel):
    """更新计划请求"""
    days: Optional[List[dict]] = Field(None, description="每日行程")
    budget: Optional[float] = Field(None, description="预算")
    preferences: Optional[dict] = Field(None, description="用户偏好")


class ToggleFavoriteRequest(BaseModel):
    """切换收藏请求"""
    is_favorite: bool = Field(..., description="是否收藏")


class MarkCompleteRequest(BaseModel):
    """标记完成请求"""
    is_completed: bool = Field(..., description="是否完成")


class MessageResponse(BaseModel):
    """通用消息响应"""
    message: str = Field(..., description="消息内容")


# ========== API端点 ==========

@router.get("", response_model=PlanListResponse)
async def get_user_plans(
    city: Optional[str] = Query(None, description="城市筛选"),
    is_favorite: Optional[bool] = Query(None, description="是否收藏筛选"),
    is_completed: Optional[bool] = Query(None, description="是否完成筛选"),
    limit: int = Query(20, ge=1, le=100, description="返回数量"),
    skip: int = Query(0, ge=0, description="跳过数量"),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    获取当前用户的旅行计划列表

    支持按城市、收藏状态、完成状态筛选
    支持分页
    """
    try:
        plan_service = get_travel_plan_service()

        logger.info(f"查询计划列表 - 用户ID: {current_user.id}, 用户名: {current_user.username}")

        # 查询计划列表
        plans = await plan_service.get_user_plans(
            user_id=current_user.id,
            city=city,
            is_favorite=is_favorite,
            is_completed=is_completed,
            limit=limit,
            skip=skip
        )

        logger.info(f"查询到 {len(plans)} 个计划")

        return PlanListResponse(
            total=len(plans),
            plans=plans
        )

    except Exception as e:
        logger.error(f"查询计划列表失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="查询计划列表失败"
        )


@router.get("/{plan_id}", response_model=PlanDetailResponse)
async def get_plan_detail(
    plan_id: str,
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    获取计划详情

    只能查看自己的计划
    """
    try:
        plan_service = get_travel_plan_service()

        # 查询计划
        plan = await plan_service.get_plan_by_id(plan_id, user_id=current_user.id)

        if not plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="计划不存在或无权访问"
            )

        # 确保必填字段存在
        if 'is_completed' not in plan or plan['is_completed'] is None:
            plan['is_completed'] = False
        if 'is_favorite' not in plan or plan['is_favorite'] is None:
            plan['is_favorite'] = False
        if 'preferences' not in plan or plan['preferences'] is None:
            plan['preferences'] = {}
        if 'weather_info' not in plan or plan['weather_info'] is None:
            plan['weather_info'] = []

        return PlanDetailResponse(**plan)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取计划详情失败: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取计划详情失败"
        )


@router.put("/{plan_id}", response_model=MessageResponse)
async def update_plan(
    plan_id: str,
    request: UpdatePlanRequest,
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    更新计划信息

    只能更新自己的计划
    """
    try:
        plan_service = get_travel_plan_service()

        # 构建更新字段
        updates = {}
        if request.days is not None:
            updates["days"] = request.days
        if request.budget is not None:
            updates["budget"] = request.budget
        if request.preferences is not None:
            updates["preferences"] = request.preferences

        if not updates:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="没有提供更新字段"
            )

        # 更新计划
        success = await plan_service.update_plan(
            plan_id=plan_id,
            user_id=current_user.id,
            updates=updates
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="计划不存在或更新失败"
            )

        logger.info(f"计划已更新: {plan_id} (用户: {current_user.username})")

        return MessageResponse(message="计划已更新")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新计划失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="更新计划失败"
        )


@router.post("/{plan_id}/favorite", response_model=MessageResponse)
async def toggle_favorite(
    plan_id: str,
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    切换计划收藏状态

    自动切换：如果已收藏则取消，如果未收藏则收藏
    """
    try:
        plan_service = get_travel_plan_service()

        # 先获取当前状态
        plan = await plan_service.get_plan_by_id(plan_id, user_id=current_user.id)
        if not plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="计划不存在"
            )

        # 切换收藏状态
        new_favorite_status = not plan.get('is_favorite', False)
        success = await plan_service.mark_favorite(
            plan_id=plan_id,
            user_id=current_user.id,
            is_favorite=new_favorite_status
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="计划不存在"
            )

        action = "已收藏" if new_favorite_status else "已取消收藏"
        logger.info(f"计划{action}: {plan_id} (用户: {current_user.username})")

        return MessageResponse(message=f"计划{action}")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"切换收藏状态失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="切换收藏状态失败"
        )


@router.post("/{plan_id}/complete", response_model=MessageResponse)
async def mark_complete(
    plan_id: str,
    request: MarkCompleteRequest,
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    标记计划完成状态

    标记为已完成或未完成
    """
    try:
        plan_service = get_travel_plan_service()

        # 标记完成
        success = await plan_service.mark_completed(
            plan_id=plan_id,
            user_id=current_user.id,
            is_completed=request.is_completed
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="计划不存在"
            )

        action = "已完成" if request.is_completed else "未完成"
        logger.info(f"计划标记为{action}: {plan_id} (用户: {current_user.username})")

        return MessageResponse(message=f"计划已标记为{action}")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"标记完成状态失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="标记完成状态失败"
        )


@router.delete("/{plan_id}", response_model=MessageResponse)
async def delete_plan(
    plan_id: str,
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    删除计划

    只能删除自己的计划
    """
    try:
        plan_service = get_travel_plan_service()

        # 删除计划
        success = await plan_service.delete_plan(
            plan_id=plan_id,
            user_id=current_user.id
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="计划不存在"
            )

        logger.info(f"计划已删除: {plan_id} (用户: {current_user.username})")

        return MessageResponse(message="计划已删除")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除计划失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="删除计划失败"
        )


@router.get("/{plan_id}/export")
async def export_plan(
    plan_id: str,
    format: str = Query("json", pattern="^(json|pdf)$", description="导出格式"),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    导出计划

    支持JSON和PDF格式（当前仅实现JSON）
    """
    try:
        plan_service = get_travel_plan_service()

        # 查询计划
        plan = await plan_service.get_plan_by_id(plan_id, user_id=current_user.id)

        if not plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="计划不存在或无权访问"
            )

        if format == "json":
            # 返回JSON格式
            return plan
        elif format == "pdf":
            # TODO: 实现PDF导出
            raise HTTPException(
                status_code=status.HTTP_501_NOT_IMPLEMENTED,
                detail="PDF导出功能尚未实现"
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"导出计划失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="导出计划失败"
        )
