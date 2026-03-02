"""实时信息服务"""

import requests
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime
import json
from ..database.redis_client import get_redis_client
from ..config import get_settings

settings = get_settings()
redis_client = get_redis_client()


class FlightStatusRequest(BaseModel):
    """航班状态请求"""
    flight_number: str = Field(..., description="航班号")
    date: Optional[str] = Field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d"), description="航班日期")


class FlightStatusResponse(BaseModel):
    """航班状态响应"""
    flight_number: str = Field(..., description="航班号")
    status: str = Field(..., description="航班状态")
    departure_time: str = Field(..., description="起飞时间")
    arrival_time: str = Field(..., description="到达时间")
    delay: Optional[int] = Field(default=None, description="延误时间（分钟）")
    gate: Optional[str] = Field(default=None, description="登机口")
    terminal: Optional[str] = Field(default=None, description="航站楼")


class WeatherRequest(BaseModel):
    """天气请求"""
    city: str = Field(..., description="城市名称")
    days: int = Field(default=7, description="查询天数")


class WeatherItem(BaseModel):
    """天气项"""
    date: str = Field(..., description="日期")
    temp_max: float = Field(..., description="最高温度")
    temp_min: float = Field(..., description="最低温度")
    condition: str = Field(..., description="天气状况")
    humidity: int = Field(..., description="湿度")
    precipitation: float = Field(default=0.0, description="降水量")


class WeatherResponse(BaseModel):
    """天气响应"""
    city: str = Field(..., description="城市名称")
    weather_list: List[WeatherItem] = Field(..., description="天气列表")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新时间")


class AttractionStatusRequest(BaseModel):
    """景点状态请求"""
    attraction_id: str = Field(..., description="景点ID")


class AttractionStatusResponse(BaseModel):
    """景点状态响应"""
    attraction_id: str = Field(..., description="景点ID")
    name: str = Field(..., description="景点名称")
    status: str = Field(..., description="景点状态")
    open_time: str = Field(..., description="开放时间")
    ticket_price: float = Field(..., description="门票价格")
    crowd_level: int = Field(..., ge=1, le=5, description="拥挤程度（1-5）")


class RealTimeService:
    """实时信息服务"""

    def __init__(self):
        self.amap_key = settings.amap_api_key if hasattr(settings, 'amap_api_key') else ""

    def get_flight_status(self, request: FlightStatusRequest) -> FlightStatusResponse:
        """查询航班动态"""
        cache_key = f"flight:{request.flight_number}:{request.date}"
        cached_result = redis_client.get(cache_key)
        
        if cached_result:
            try:
                return FlightStatusResponse(**json.loads(cached_result))
            except:
                pass

        result = FlightStatusResponse(
            flight_number=request.flight_number,
            status="准点",
            departure_time="08:00",
            arrival_time="10:30",
            delay=0,
            gate="A12",
            terminal="T3"
        )

        redis_client.setex(cache_key, 3600, json.dumps(result.model_dump()))
        return result

    def get_weather(self, request: WeatherRequest) -> WeatherResponse:
        """查询天气"""
        cache_key = f"weather:{request.city}:{request.days}"
        cached_result = redis_client.get(cache_key)
        
        if cached_result:
            try:
                data = json.loads(cached_result)
                return WeatherResponse(**data)
            except:
                pass

        weather_list = []
        for i in range(request.days):
            date = (datetime.now() + datetime.timedelta(days=i)).strftime("%Y-%m-%d")
            weather_list.append(WeatherItem(
                date=date,
                temp_max=25.0 + i,
                temp_min=15.0 + i,
                condition="晴" if i % 2 == 0 else "多云",
                humidity=60 + i * 2,
                precipitation=0.0
            ))

        result = WeatherResponse(
            city=request.city,
            weather_list=weather_list
        )

        redis_client.setex(cache_key, 1800, json.dumps(result.model_dump()))
        return result

    def get_attraction_status(self, request: AttractionStatusRequest) -> AttractionStatusResponse:
        """查询景点状态"""
        cache_key = f"attraction:{request.attraction_id}"
        cached_result = redis_client.get(cache_key)
        
        if cached_result:
            try:
                return AttractionStatusResponse(**json.loads(cached_result))
            except:
                pass

        result = AttractionStatusResponse(
            attraction_id=request.attraction_id,
            name="故宫博物院",
            status="开放中",
            open_time="08:30-17:00",
            ticket_price=60.0,
            crowd_level=3
        )

        redis_client.setex(cache_key, 7200, json.dumps(result.model_dump()))
        return result
