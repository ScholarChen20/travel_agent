"""实时信息服务"""

from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime
from loguru import logger
import json

from ..database.mysql import get_mysql_db
from ..database.models import User, UserProfile
from ..config import get_settings

settings = get_settings()


# ========== 请求模型 ==========

class RealTimeRequest(BaseModel):
    """实时信息请求"""
    user_id: str = Field(..., description="用户ID")
    location: Optional[str] = Field(default=None, description="当前位置")
    type: str = Field(default="all", description="信息类型")


# ========== 响应模型 ==========

class RealTimeItem(BaseModel):
    """实时信息项"""
    id: str = Field(..., description="信息ID")
    title: str = Field(..., description="信息标题")
    description: str = Field(..., description="信息描述")
    type: str = Field(..., description="信息类型")
    location: str = Field(..., description="位置")
    timestamp: datetime = Field(default_factory=datetime.now, description="时间戳")
    url: Optional[str] = Field(default=None, description="详情链接")


class RealTimeResponse(BaseModel):
    """实时信息响应"""
    items: List[RealTimeItem] = Field(..., description="实时信息列表")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新时间")


# ========== 服务类 ==========

class RealTimeService:
    """实时信息服务类"""

    def __init__(self):
        """初始化服务"""
        self.mysql_db = get_mysql_db()
        # 延迟初始化Redis客户端
        self.redis = None
        self._init_redis()
        logger.info("实时信息服务已初始化")

    def _init_redis(self):
        """初始化Redis客户端"""
        try:
            from ..database.redis_client import get_redis_client
            self.redis = get_redis_client()
            logger.debug("Redis客户端初始化成功")
        except Exception as e:
            logger.warning(f"Redis客户端初始化失败: {str(e)}")
            self.redis = None

    async def get_real_time_info(self, request: RealTimeRequest) -> RealTimeResponse:
        """获取实时信息"""
        try:
            logger.info(f"为用户{request.user_id}获取实时信息，类型: {request.type}")

            # 从Redis缓存获取实时信息
            if self.redis:
                cache_key = f"real_time:{request.user_id}:{request.type}"
                cached_info = await self.redis.get(cache_key)
                if cached_info:
                    info_data = json.loads(cached_info)
                    logger.debug("从Redis缓存获取实时信息")
                    return RealTimeResponse(**info_data)

            # 模拟实时信息数据
            items = [
                RealTimeItem(
                    id="traffic_1",
                    title="当前路况",
                    description="您当前位置附近的交通状况良好，没有拥堵",
                    type="traffic",
                    location="北京朝阳区",
                    url="https://traffic.example.com/chaoyang"
                ),
                RealTimeItem(
                    id="weather_1",
                    title="今日天气",
                    description="今日晴，气温15-25°C，适合出行",
                    type="weather",
                    location="北京",
                    url="https://weather.example.com/beijing"
                ),
                RealTimeItem(
                    id="event_1",
                    title="本地活动",
                    description="本周末有一场音乐节在奥林匹克公园举办",
                    type="event",
                    location="北京奥林匹克公园",
                    url="https://event.example.com/music-festival"
                )
            ]

            # 构建响应
            response = RealTimeResponse(
                items=items
            )

            # 缓存实时信息到Redis，过期时间5分钟
            if self.redis:
                cache_key = f"real_time:{request.user_id}:{request.type}"
                await self.redis.set(cache_key, json.dumps(response.model_dump(), ensure_ascii=False), ex=300)
                logger.debug(f"实时信息已缓存到Redis: {cache_key}")

            logger.info(f"为用户{request.user_id}成功获取实时信息，共{len(items)}条")
            return response

        except Exception as e:
            logger.error(f"获取实时信息失败: {str(e)}")
            # 返回空数据
            return RealTimeResponse(
                items=[]
            )


# ========== 全局实例（单例模式） ==========

_real_time_service: Optional[RealTimeService] = None


def get_real_time_service() -> RealTimeService:
    """
    获取全局实时信息服务实例（单例）

    Returns:
        RealTimeService: 实时信息服务实例
    """
    global _real_time_service
    if _real_time_service is None:
        _real_time_service = RealTimeService()
    return _real_time_service
