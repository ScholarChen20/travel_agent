"""
监控服务

功能：
1. 数据库健康检查
2. Redis健康检查
3. Agent健康检查
4. 性能指标统计
"""

import time
import psutil
from typing import Dict, Any, Optional
from loguru import logger

from ..database.mongodb import get_mongodb_client
from ..database.mysql import get_mysql_db
from ..database.redis_client import get_redis_client


class MonitoringService:
    """监控服务类"""

    def __init__(self):
        """初始化服务"""
        self.mysql_db = get_mysql_db()
        self.mongodb = get_mongodb_client()
        self.redis = get_redis_client()
        logger.info("监控服务已初始化")

    def check_database_health(self) -> Dict[str, Any]:
        """
        检查MySQL数据库健康状态

        Returns:
            Dict: {status: str, latency_ms: float, error: str}
        """
        try:
            start_time = time.time()

            # 执行简单查询测试连接
            if self.mysql_db.health_check():
                latency = (time.time() - start_time) * 1000

                return {
                    "status": "healthy",
                    "latency_ms": round(latency, 2),
                    "error": None
                }
            else:
                return {
                    "status": "unhealthy",
                    "latency_ms": 0,
                    "error": "Health check failed"
                }

        except Exception as e:
            logger.error(f"MySQL健康检查失败: {str(e)}")
            return {
                "status": "unhealthy",
                "latency_ms": 0,
                "error": str(e)
            }

    async def check_mongodb_health(self) -> Dict[str, Any]:
        """
        检查MongoDB健康状态

        Returns:
            Dict: {status: str, latency_ms: float, error: str}
        """
        try:
            start_time = time.time()

            # 执行ping测试连接
            if await self.mongodb.health_check():
                latency = (time.time() - start_time) * 1000

                return {
                    "status": "healthy",
                    "latency_ms": round(latency, 2),
                    "error": None
                }
            else:
                return {
                    "status": "unhealthy",
                    "latency_ms": 0,
                    "error": "Health check failed"
                }

        except Exception as e:
            logger.error(f"MongoDB健康检查失败: {str(e)}")
            return {
                "status": "unhealthy",
                "latency_ms": 0,
                "error": str(e)
            }

    async def check_redis_health(self) -> Dict[str, Any]:
        """
        检查Redis健康状态

        Returns:
            Dict: {status: str, latency_ms: float, error: str}
        """
        try:
            start_time = time.time()

            # 执行ping测试连接
            if await self.redis.ping():
                latency = (time.time() - start_time) * 1000

                return {
                    "status": "healthy",
                    "latency_ms": round(latency, 2),
                    "error": None
                }
            else:
                return {
                    "status": "unhealthy",
                    "latency_ms": 0,
                    "error": "Ping failed"
                }

        except Exception as e:
            logger.error(f"Redis健康检查失败: {str(e)}")
            return {
                "status": "unhealthy",
                "latency_ms": 0,
                "error": str(e)
            }

    async def check_agent_health(self) -> Dict[str, Any]:
        """
        检查Agent健康状态

        Returns:
            Dict: {status: str, response_time_ms: float, error: str}
        """
        try:
            from ..agents.trip_planner_agent import get_trip_planner_agent

            start_time = time.time()

            # 获取Agent实例（测试初始化）
            agent = get_trip_planner_agent()

            response_time = (time.time() - start_time) * 1000

            return {
                "status": "healthy",
                "response_time_ms": round(response_time, 2),
                "agent_name": agent.planner_agent.name,
                "tools_count": len(agent.planner_agent.list_tools()),
                "error": None
            }

        except Exception as e:
            logger.error(f"Agent健康检查失败: {str(e)}")
            return {
                "status": "unhealthy",
                "response_time_ms": 0,
                "error": str(e)
            }

    def get_performance_metrics(self) -> Dict[str, Any]:
        """
        获取性能指标

        Returns:
            Dict: 性能指标
        """
        try:
            # CPU使用率
            cpu_percent = psutil.cpu_percent(interval=1)

            # 内存使用
            memory = psutil.virtual_memory()

            # 磁盘使用
            disk = psutil.disk_usage('/')

            # 网络IO（如果可用）
            try:
                net_io = psutil.net_io_counters()
                network = {
                    "bytes_sent": net_io.bytes_sent,
                    "bytes_recv": net_io.bytes_recv,
                    "packets_sent": net_io.packets_sent,
                    "packets_recv": net_io.packets_recv
                }
            except:
                network = None

            return {
                "cpu": {
                    "percent": cpu_percent,
                    "count": psutil.cpu_count()
                },
                "memory": {
                    "total_mb": round(memory.total / (1024 * 1024), 2),
                    "used_mb": round(memory.used / (1024 * 1024), 2),
                    "available_mb": round(memory.available / (1024 * 1024), 2),
                    "percent": memory.percent
                },
                "disk": {
                    "total_gb": round(disk.total / (1024 * 1024 * 1024), 2),
                    "used_gb": round(disk.used / (1024 * 1024 * 1024), 2),
                    "free_gb": round(disk.free / (1024 * 1024 * 1024), 2),
                    "percent": disk.percent
                },
                "network": network
            }

        except Exception as e:
            logger.error(f"获取性能指标失败: {str(e)}")
            raise

    def check_disk_space(self, threshold_percent: float = 90.0) -> Dict[str, Any]:
        """
        检查磁盘空间

        Args:
            threshold_percent: 告警阈值（百分比）

        Returns:
            Dict: {status: str, usage_percent: float, warning: bool}
        """
        try:
            disk = psutil.disk_usage('/')
            usage_percent = disk.percent

            return {
                "status": "warning" if usage_percent >= threshold_percent else "ok",
                "usage_percent": usage_percent,
                "free_gb": round(disk.free / (1024 * 1024 * 1024), 2),
                "warning": usage_percent >= threshold_percent
            }

        except Exception as e:
            logger.error(f"检查磁盘空间失败: {str(e)}")
            return {
                "status": "error",
                "usage_percent": 0,
                "free_gb": 0,
                "warning": True,
                "error": str(e)
            }

    async def get_comprehensive_health(self) -> Dict[str, Any]:
        """
        获取综合健康状态

        Returns:
            Dict: 综合健康报告
        """
        try:
            # 检查所有组件
            mysql_health = self.check_database_health()
            mongodb_health = await self.check_mongodb_health()
            redis_health = await self.check_redis_health()
            agent_health = await self.check_agent_health()
            disk_status = self.check_disk_space()

            # 判断整体状态
            all_healthy = all([
                mysql_health["status"] == "healthy",
                mongodb_health["status"] == "healthy",
                redis_health["status"] == "healthy",
                agent_health["status"] == "healthy",
                disk_status["status"] == "ok"
            ])

            overall_status = "healthy" if all_healthy else "degraded"

            return {
                "overall_status": overall_status,
                "components": {
                    "mysql": mysql_health,
                    "mongodb": mongodb_health,
                    "redis": redis_health,
                    "agent": agent_health,
                    "disk": disk_status
                },
                "timestamp": time.time()
            }

        except Exception as e:
            logger.error(f"获取综合健康状态失败: {str(e)}")
            raise


# ========== 全局实例（单例模式） ==========

_monitoring_service: Optional[MonitoringService] = None


def get_monitoring_service() -> MonitoringService:
    """
    获取全局监控服务实例（单例）

    Returns:
        MonitoringService: 监控服务实例
    """
    global _monitoring_service
    if _monitoring_service is None:
        _monitoring_service = MonitoringService()
    return _monitoring_service
