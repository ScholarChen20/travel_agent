"""抖音热点数据服务"""

import httpx
import re
from datetime import datetime
from typing import Dict, List, Optional
from loguru import logger

from ..database.mongodb import get_mongodb_client
from ..database.redis_client import get_redis_client


class DouyinService:
    """抖音热点数据服务类"""

    def __init__(self):
        """初始化抖音服务"""
        self.mongodb_client = get_mongodb_client()
        self.redis_client = get_redis_client()
        self.api_url = "https://uapis.cn/api/v1/misc/hotboard?type=douyin"
        self.mongodb_collection = "douyin_hotboard"

    @property
    def redis_key(self):
        """动态生成Redis key，包含当前日期"""
        return "douyin:hotboard:rank" + datetime.now().strftime("%Y%m%d")

    @property
    def current_date_id(self):
        """获取当前日期ID，用于MongoDB的_id"""
        return datetime.now().strftime("%Y%m%d")

    async def fetch_hotboard_data(self) -> Optional[Dict]:
        """
        获取抖音热点数据

        Returns:
            Dict: 抖音热点数据响应体，失败返回None
        """
        try:
            logger.info(f"开始获取抖音热点数据: {self.api_url}")
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(self.api_url)
                
                if response.status_code != 200:
                    logger.error(f"获取抖音热点数据失败: 状态码 {response.status_code}")
                    return None
                
                data = response.json()
                logger.info(f"成功获取抖音热点数据，共 {len(data.get('list', []))} 条热点")
                return data
                
        except httpx.RequestError as e:
            logger.error(f"获取抖音热点数据网络错误: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"获取抖音热点数据未知错误: {str(e)}")
            return None

    async def save_to_mongodb(self, data: Dict) -> bool:
        """
        保存原始数据到MongoDB

        Args:
            data: 抖音热点数据响应体

        Returns:
            bool: 是否保存成功
        """
        try:
            collection = self.mongodb_client.get_collection(self.mongodb_collection)
            
            # 获取当前日期ID
            date_id = self.current_date_id
            
            # 先删除当天已存在的记录
            delete_result = await collection.delete_one({"_id": date_id})
            if delete_result.deleted_count > 0:
                logger.info(f"已删除MongoDB中当天已存在的抖音热点数据: {date_id}")
            
            # 添加时间戳字段
            data['_id'] = date_id
            data['created_at'] = datetime.now()
            
            result = await collection.insert_one(data)
            logger.info(f"成功保存抖音热点数据到MongoDB: {result.inserted_id}")
            return True
            
        except Exception as e:
            logger.error(f"保存抖音热点数据到MongoDB失败: {str(e)}")
            return False

    def parse_hot_value(self, hot_value_str: str) -> float:
        """
        解析热度值字符串为数字

        Args:
            hot_value_str: 热度值字符串，如 "1131.6万"

        Returns:
            float: 解析后的热度值
        """
        try:
            # 提取数字部分
            match = re.search(r'([\d.]+)', hot_value_str)
            if not match:
                return 0.0
            
            value = float(match.group(1))
            
            # 如果包含"万"，乘以10000
            if "万" in hot_value_str:
                value *= 10000
            
            return value
            
        except Exception as e:
            logger.error(f"解析热度值失败: {str(e)}")
            return 0.0

    async def save_to_redis(self, hotboard_list: List[Dict]) -> bool:
        """
        保存热点数据到Redis（按热度值排序）

        Args:
            hotboard_list: 热点数据列表

        Returns:
            bool: 是否保存成功
        """
        try:
            # 使用Redis的Sorted Set来存储热度排名
            async with self.redis_client.client.pipeline() as pipe:
                # 先清空现有的排名
                await pipe.delete(self.redis_key)
                
                # 添加所有热点到Sorted Set
                for item in hotboard_list:
                    title = item.get('title', '')
                    hot_value_str = item.get('hot_value', '0')
                    hot_value = self.parse_hot_value(hot_value_str)
                    
                    if title and hot_value > 0:
                        # 使用负数作为分数，以便按降序排列
                        await pipe.zadd(self.redis_key, {title: -hot_value})
                
                # 执行所有命令
                await pipe.execute()
                
            logger.info(f"成功保存抖音热点数据到Redis，共 {len(hotboard_list)} 条")
            return True
            
        except Exception as e:
            logger.error(f"保存抖音热点数据到Redis失败: {str(e)}")
            return False

    async def process_hotboard_data(self) -> Dict:
        """
        处理抖音热点数据的完整流程

        Returns:
            Dict: 处理结果
        """
        try:
            # 1. 获取热点数据
            data = await self.fetch_hotboard_data()
            if not data:
                return {
                    "success": False,
                    "message": "获取抖音热点数据失败"
                }


            # 2. 保存到MongoDB
            mongodb_result = await self.save_to_mongodb(data)
            if not mongodb_result:
                logger.warning("保存到MongoDB失败，但继续处理")
            
            # 3. 保存到Redis
            hotboard_list = data.get('list', [])
            redis_result = await self.save_to_redis(hotboard_list)
            if not redis_result:
                logger.warning("保存到Redis失败，但继续处理")
            
            return {
                "success": True,
                "message": "处理抖音热点数据成功",
                "data": {
                    "total": len(hotboard_list),
                    "update_time": data.get('update_time'),
                    "saved_to_mongodb": mongodb_result,
                    "saved_to_redis": redis_result
                }
            }
            
        except Exception as e:
            logger.error(f"处理抖音热点数据失败: {str(e)}")
            return {
                "success": False,
                "message": f"处理失败: {str(e)}"
            }

    async def get_hotboard_rank(self, limit: int = 50) -> List[Dict]:
        """
        从Redis获取热点排名

        Args:
            limit: 返回数量限制

        Returns:
            List[Dict]: 热点排名列表
        """
        try:
            # 从Redis获取Sorted Set中的数据
            result = await self.redis_client.client.zrange(
                self.redis_key,
                0,
                limit - 1,
                withscores=True
            )
            if len(result) == 0:
                data = await self.process_hotboard_data()
                if not data.get('success'):
                    logger.info("处理抖音热点数据失败，请稍后再试")
                    return []

                # 再从redis中取数据
                result = await self.redis_client.client.zrange(
                    self.redis_key,
                    0,
                    limit - 1,
                    withscores=True
                )
            
            # 转换结果格式
            rank_list = []
            for index, (title, score) in enumerate(result, 1):
                # 恢复热度值（取绝对值）
                hot_value = abs(float(score))
                rank_list.append({
                    "rank": index,
                    "title": title,
                    "hot_value": hot_value
                })
            
            logger.info(f"成功获取抖音热点排名，共 {len(rank_list)} 条")
            return rank_list
            
        except Exception as e:
            logger.error(f"获取抖音热点排名失败: {str(e)}")
            return []


# 全局抖音服务实例（单例）
_douyin_service: Optional[DouyinService] = None


def get_douyin_service() -> DouyinService:
    """
    获取全局抖音服务实例（单例）

    Returns:
        DouyinService: 抖音服务实例
    """
    global _douyin_service
    if _douyin_service is None:
        _douyin_service = DouyinService()
    return _douyin_service
