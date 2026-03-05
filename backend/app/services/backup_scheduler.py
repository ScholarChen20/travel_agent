"""
定时任务调度器
功能：定时执行数据备份等任务
"""

import os
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from loguru import logger
from pathlib import Path
import sys

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent))


class BackupScheduler:
    """备份任务调度器"""

    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.backup_dir = Path(__file__).parent.parent / "backups"
        self.backup_dir.mkdir(exist_ok=True)

    async def backup_task(self):
        """执行备份任务"""
        try:
            logger.info("=" * 60)
            logger.info("开始执行定时备份任务")
            logger.info("=" * 60)

            # 导入备份模块
            from scripts.backup.backup_databases import DatabaseBackup
            from app.config import get_settings

            settings = get_settings()

            # 创建备份实例
            backup = DatabaseBackup(str(self.backup_dir))

            # 配置数据库信息
            mysql_config = {
                "host": settings.mysql_host,
                "port": settings.mysql_port,
                "user": settings.mysql_user,
                "password": settings.mysql_password,
                "database": settings.mysql_database
            }

            mongodb_config = {
                "uri": f"mongodb://{settings.mongodb_user}:{settings.mongodb_password}@{settings.mongodb_host}:{settings.mongodb_port}",
                "database": settings.mongodb_database
            }

            redis_config = {
                "host": settings.redis_host,
                "port": settings.redis_port,
                "db": settings.redis_db,
                "password": settings.redis_password
            }

            # 执行备份
            results = backup.backup_all(mysql_config, mongodb_config, redis_config)

            logger.info("=" * 60)
            logger.info("定时备份任务完成")
            logger.info("=" * 60)

            return results

        except Exception as e:
            logger.error(f"定时备份任务执行失败: {e}", exc_info=True)
            return None

    def start(self):
        """启动调度器"""
        try:
            logger.info("启动定时任务调度器...")

            # 添加每天凌晨2点执行的备份任务
            self.scheduler.add_job(
                self.backup_task,
                trigger=CronTrigger(hour=2, minute=0, day_of_week='sun'), # 周一到周五
                id='daily_backup',
                name='每周周天数据库备份',
                replace_existing=True
            )

            # 启动调度器
            self.scheduler.start()

            logger.info("定时任务调度器启动成功")
            logger.info("已添加每周天凌晨2点的备份任务")

            # 显示所有任务
            jobs = self.scheduler.get_jobs()
            for job in jobs:
                logger.info(f"任务: {job.name} - 下次执行时间: {job.next_run_time}")

        except Exception as e:
            logger.error(f"启动定时任务调度器失败: {e}", exc_info=True)

    def stop(self):
        """停止调度器"""
        try:
            logger.info("停止定时任务调度器...")
            self.scheduler.shutdown()
            logger.info("定时任务调度器已停止")
        except Exception as e:
            logger.error(f"停止定时任务调度器失败: {e}", exc_info=True)


# 全局调度器实例
backup_scheduler = None


def get_scheduler():
    """获取调度器实例"""
    global backup_scheduler
    if backup_scheduler is None:
        backup_scheduler = BackupScheduler()
    return backup_scheduler


def start_scheduler():
    """启动调度器"""
    scheduler = get_scheduler()
    scheduler.start()


def stop_scheduler():
    """停止调度器"""
    global backup_scheduler
    if backup_scheduler is not None:
        backup_scheduler.stop()
        backup_scheduler = None


if __name__ == "__main__":
    import asyncio

    async def main():
        scheduler = BackupScheduler()
        scheduler.start()

        try:
            # 保持运行
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            scheduler.stop()

    asyncio.run(main())
