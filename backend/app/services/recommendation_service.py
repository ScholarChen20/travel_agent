"""智能推荐系统服务"""

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Dict, Optional
from pydantic import BaseModel, Field
from datetime import datetime
import json
from loguru import logger
from ..database.redis_client import get_redis_client
from ..database.mysql import get_mysql_db
from ..database.models import User, UserProfile
from ..config import get_settings

settings = get_settings()
redis_client = get_redis_client()
mysql_db = get_mysql_db()


class RecommendationRequest(BaseModel):
    """推荐请求"""
    user_id: Optional[str] = Field(None, description="用户ID")
    preferences: Optional[List[str]] = Field(None, description="兴趣标签列表")
    location: Optional[str] = Field(None, description="当前位置")
    limit: int = Field(default=10, description="返回数量")


class AttractionRecommendation(BaseModel):
    """景点推荐"""
    id: str = Field(..., description="景点ID")
    name: str = Field(..., description="景点名称")
    rating: float = Field(..., description="评分")
    distance: float = Field(..., description="距离")
    tags: List[str] = Field(..., description="标签")
    image_url: Optional[str] = Field(None, description="图片URL")


class RestaurantRecommendation(BaseModel):
    """餐厅推荐"""
    id: str = Field(..., description="餐厅ID")
    name: str = Field(..., description="餐厅名称")
    rating: float = Field(..., description="评分")
    cuisine: str = Field(..., description="菜系")
    price_range: str = Field(..., description="价格范围")


class HotelRecommendation(BaseModel):
    """酒店推荐"""
    id: str = Field(..., description="酒店ID")
    name: str = Field(..., description="酒店名称")
    rating: float = Field(..., description="评分")
    price: float = Field(..., description="价格")
    distance: float = Field(..., description="距离")


class RecommendationResponse(BaseModel):
    """推荐响应"""
    attractions: List[AttractionRecommendation] = Field(..., description="景点推荐")
    restaurants: List[RestaurantRecommendation] = Field(..., description="餐厅推荐")
    hotels: List[HotelRecommendation] = Field(..., description="酒店推荐")


class RecommendationService:
    """推荐系统服务"""

    def __init__(self):
        self.user_preferences = self._load_user_preferences()
        self.user_item_matrix = self._build_user_item_matrix()
        self.user_similarity = cosine_similarity(self.user_item_matrix) if self.user_item_matrix.size > 0 else np.array([])

    def _load_user_preferences(self) -> Dict:
        """从数据库加载用户偏好"""
        preferences = {}
        
        try:
            # 从MySQL数据库查询用户偏好
            with mysql_db.get_session() as session:
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

    def _build_user_item_matrix(self) -> np.ndarray:
        """构建用户-物品矩阵"""
        users = list(self.user_preferences.keys())
        items = self._get_all_items()
        if not users or not items:
            return np.array([])
        matrix = np.zeros((len(users), len(items)))
        for i, user in enumerate(users):
            for j, item in enumerate(items):
                matrix[i][j] = self._get_user_item_score(user, item)
        return matrix

    def _get_all_items(self) -> List[str]:
        """获取所有物品列表"""
        return ["故宫", "天安门", "长城", "全聚德", "北京饭店", "故宫博物馆"]

    def _get_user_item_score(self, user: str, item: str) -> float:
        """计算用户对物品的评分"""
        if user not in self.user_preferences:
            return 0.0
        user_prefs = self.user_preferences[user]["preferences"]
        score = 0.0
        if "故宫" in item and "历史文化" in user_prefs:
            score = 0.8
        if "全聚德" in item and "美食" in user_prefs:
            score = 0.9
        return score

    def _get_user_index(self, user_id: str) -> int:
        """获取用户索引"""
        users = list(self.user_preferences.keys())
        if user_id not in users:
            return 0
        return users.index(user_id)

    def _get_item_by_index(self, item_idx: int) -> str:
        """根据索引获取物品"""
        items = self._get_all_items()
        if item_idx < 0 or item_idx >= len(items):
            return ""
        return items[item_idx]

    def recommend(self, request: RecommendationRequest) -> RecommendationResponse:
        """获取推荐结果"""
        cache_key = f"recommendations:{request.user_id}:{request.location}:{request.limit}"
        cached_result = redis_client.get(cache_key)
        if cached_result:
            try:
                return RecommendationResponse(**json.loads(cached_result))
            except:
                pass

        user_id = request.user_id or "user_1"
        user_idx = self._get_user_index(user_id)
        
        # 如果用户ID存在于数据库中，获取用户的实际偏好
        if user_id in self.user_preferences:
            user_prefs = self.user_preferences[user_id]
            logger.info(f"使用用户{user_id}的实际偏好: {user_prefs}")
        else:
            logger.warning(f"用户{user_id}不存在，使用默认偏好")
        
        if self.user_similarity.size > 0 and user_idx < self.user_similarity.shape[0]:
            similarities = self.user_similarity[user_idx]
            scores = np.dot(similarities, self.user_item_matrix) / np.sum(similarities) if np.sum(similarities) > 0 else np.zeros_like(similarities)
        else:
            scores = np.zeros(len(self._get_all_items()))

        attractions = [
            AttractionRecommendation(
                id="attraction_1",
                name="故宫",
                rating=4.8,
                distance=2.5,
                tags=["历史文化", "古建筑"],
                image_url="https://example.com/gugong.jpg"
            )
        ]
        
        restaurants = [
            RestaurantRecommendation(
                id="restaurant_1",
                name="全聚德",
                rating=4.5,
                cuisine="北京烤鸭",
                price_range="¥200-300"
            )
        ]
        
        hotels = [
            HotelRecommendation(
                id="hotel_1",
                name="北京饭店",
                rating=4.7,
                price=800,
                distance=3.0
            )
        ]

        response = RecommendationResponse(
            attractions=attractions,
            restaurants=restaurants,
            hotels=hotels
        )

        redis_client.setex(cache_key, 3600, json.dumps(response.model_dump()))

        return response
