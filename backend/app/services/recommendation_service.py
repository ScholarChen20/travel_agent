"""智能推荐服务"""

from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime
from loguru import logger
import json
import random

from ..database.mysql import get_mysql_db
from ..database.models import User, UserProfile
from ..database.mongodb import get_mongodb_client
from ..config import get_settings

settings = get_settings()


# ========== 请求模型 ==========

class RecommendationRequest(BaseModel):
    """推荐请求"""
    user_id: str = Field(..., description="用户ID")
    num_recommendations: int = Field(default=5, description="推荐数量")
    context: Optional[Dict[str, Any]] = Field(default=None, description="上下文信息")


# ========== 响应模型 ==========

class RecommendationItem(BaseModel):
    """推荐项"""
    id: str = Field(..., description="推荐项ID")
    title: str = Field(..., description="推荐项标题")
    description: str = Field(..., description="推荐项描述")
    score: float = Field(..., description="推荐得分")
    type: str = Field(..., description="推荐类型")
    image_url: Optional[str] = Field(default=None, description="图片URL")


class RecommendationResponse(BaseModel):
    """推荐响应"""
    recommendations: List[RecommendationItem] = Field(..., description="推荐列表")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新时间")


# ========== 服务类 ==========

class RecommendationService:
    """智能推荐服务类"""

    def __init__(self):
        """初始化服务"""
        self.mysql_db = get_mysql_db()
        self.mongodb_client = get_mongodb_client()
        # 延迟初始化Redis客户端
        self.redis = None
        self._init_redis()
        logger.info("推荐服务已初始化")

    def _init_redis(self):
        """初始化Redis客户端"""
        try:
            from ..database.redis_client import get_redis_client
            self.redis = get_redis_client()
            logger.debug("Redis客户端初始化成功")
        except Exception as e:
            logger.warning(f"Redis客户端初始化失败: {str(e)}")
            self.redis = None

    def _load_user_preferences(self) -> Dict:
        """从数据库加载用户偏好"""
        preferences = {}
        
        try:
            # 从MySQL数据库查询用户偏好
            with self.mysql_db.get_session() as session:
                # 查询所有用户及其档案
                users = session.query(User).all()
                
                for user in users:
                    user_id = str(user.id)
                    
                    # 获取用户档案
                    profile = session.query(UserProfile).filter(UserProfile.user_id == user.id).first()
                    
                    if profile:
                        # 从档案中获取旅行偏好和位置
                        travel_preferences = profile.travel_preferences or []
                        location = profile.location or ""
                        
                        preferences[user_id] = {
                            "preferences": travel_preferences,
                            "location": location
                        }
                    else:
                        # 如果没有档案，使用默认偏好
                        preferences[user_id] = {
                            "preferences": ["历史文化", "美食"],
                            "location": "北京"
                        }
                        
                logger.info(f"从数据库加载了{len(preferences)}个用户的偏好数据")
                
        except Exception as e:
            logger.error(f"从数据库加载用户偏好失败: {str(e)}")
            # 加载失败时使用默认数据
            preferences = {
                "user_1": {"preferences": ["自然风光", "美食"], "location": "北京"},
                "user_2": {"preferences": ["历史文化", "古建筑"], "location": "西安"},
                "user_3": {"preferences": ["海滨", "沙滩"], "location": "三亚"}
            }
            logger.warning("使用默认用户偏好数据")
            
        return preferences

    async def _load_poi_data(self) -> Dict:
        """加载景点数据"""
        pois = {}
        
        try:
            # 从MongoDB查询景点数据
            pois_collection = self.mongodb_client.pois
            poi_list = await pois_collection.find({}).to_list(length=None)
            
            for poi in poi_list:
                poi_id = str(poi["_id"])
                pois[poi_id] = {
                    "id": poi_id,
                    "name": poi["name"],
                    "description": poi["description"],
                    "category": poi["category"],
                    "location": poi["location"],
                    "score": poi["score"] or 0.0,
                    "image_url": poi.get("image_url")
                }
                
            logger.info(f"从MongoDB加载了{len(pois)}个景点数据")
            
        except Exception as e:
            logger.error(f"从MongoDB加载景点数据失败: {str(e)}")
            # 加载失败时使用默认数据
            pois = {
                "poi_1": {
                    "id": "poi_1",
                    "name": "大理古城",
                    "description": "大理古城是中国历史文化名城，有着悠久的历史和独特的白族文化",
                    "category": "历史文化",
                    "location": "云南大理",
                    "score": 4.8,
                    "image_url": "https://via.placeholder.com/300x200"
                },
                "poi_2": {
                    "id": "poi_2",
                    "name": "洱海",
                    "description": "洱海是云南第二大淡水湖，湖水清澈，风景秀丽",
                    "category": "自然风光",
                    "location": "云南大理",
                    "score": 4.9,
                    "image_url": "https://via.placeholder.com/300x200"
                },
                "poi_3": {
                    "id": "poi_3",
                    "name": "兵马俑",
                    "description": "兵马俑是世界第八大奇迹，是中国古代雕塑艺术的杰作",
                    "category": "历史文化",
                    "location": "陕西西安",
                    "score": 4.9,
                    "image_url": "https://via.placeholder.com/300x200"
                }
            }
            logger.warning("使用默认景点数据")
            
        return pois

    def _calculate_similarity(self, user_preferences: Dict, poi: Dict) -> float:
        """计算用户偏好与景点的相似度"""
        score = 0.0
        
        # 偏好匹配
        if "preferences" in user_preferences:
            user_prefs = user_preferences["preferences"]
            poi_category = poi["category"]
            
            # 检查是否有匹配的偏好
            for pref in user_prefs:
                if pref in poi_category:
                    score += 0.5
            
            # 位置匹配
            if "location" in user_preferences:
                user_location = user_preferences["location"]
                poi_location = poi["location"]
                
                if user_location in poi_location or poi_location in user_location:
                    score += 0.3
            
            # 评分加成
            score += poi["score"] / 10.0
            
            # 随机扰动
            score += random.uniform(0, 0.1)
            
            # 归一化
            score = min(score, 1.0)
            
        return score

    async def recommend(self, request: RecommendationRequest) -> RecommendationResponse:
        """生成推荐"""
        try:
            logger.info(f"为用户{request.user_id}生成推荐，数量: {request.num_recommendations}")
            
            # 加载用户偏好
            user_preferences = self._load_user_preferences()
            user_pref = user_preferences.get(request.user_id, {
                "preferences": ["自然风光", "美食"],
                "location": "北京"
            })
            
            # 加载景点数据
            poi_data = self._load_poi_data()
            
            # 计算相似度
            recommendations = []
            for poi_id, poi in poi_data.items():
                score = self._calculate_similarity(user_pref, poi)
                recommendations.append({
                    "id": poi_id,
                    "title": poi["name"],
                    "description": poi["description"],
                    "score": score,
                    "type": poi["category"],
                    "image_url": poi["image_url"]
                })
            
            # 按得分排序
            recommendations.sort(key=lambda x: x["score"], reverse=True)
            
            # 取前N个
            top_recommendations = recommendations[:request.num_recommendations]
            
            # 转换为推荐项
            recommendation_items = [
                RecommendationItem(**item)
                for item in top_recommendations
            ]
            
            # 缓存推荐结果
            if self.redis:
                try:
                    cache_key = f"recommendation:{request.user_id}"
                    await self.redis.set(cache_key, json.dumps([item.model_dump() for item in recommendation_items]), ex=3600)
                    logger.debug(f"推荐结果已缓存到Redis: {cache_key}")
                except Exception as e:
                    logger.warning(f"缓存推荐结果失败: {str(e)}")
            
            logger.info(f"为用户{request.user_id}成功生成{len(recommendation_items)}个推荐")
            
            return RecommendationResponse(
                recommendations=recommendation_items
            )
            
        except Exception as e:
            logger.error(f"生成推荐失败: {str(e)}")
            # 返回默认推荐
            return RecommendationResponse(
                recommendations=[
                    RecommendationItem(
                        id="default_1",
                        title="大理古城",
                        description="大理古城是中国历史文化名城，有着悠久的历史和独特的白族文化",
                        score=0.8,
                        type="历史文化"
                    ),
                    RecommendationItem(
                        id="default_2",
                        title="洱海",
                        description="洱海是云南第二大淡水湖，湖水清澈，风景秀丽",
                        score=0.75,
                        type="自然风光"
                    )
                ]
            )


# ========== 全局实例（单例模式） ==========

_recommendation_service: Optional[RecommendationService] = None


def get_recommendation_service() -> RecommendationService:
    """
    获取全局推荐服务实例（单例）

    Returns:
        RecommendationService: 推荐服务实例
    """
    global _recommendation_service
    if _recommendation_service is None:
        _recommendation_service = RecommendationService()
    return _recommendation_service
