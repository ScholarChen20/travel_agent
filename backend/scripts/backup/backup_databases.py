"""
数据备份脚本
功能：备份MySQL、MongoDB和Redis数据
支持Windows和Linux环境
"""

import os
import subprocess
import shutil
from datetime import datetime
from pathlib import Path
import gzip
import tarfile
import json
from loguru import logger
import sys
import platform

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


class DatabaseBackup:
    """数据库备份类"""

    def __init__(self, backup_dir: str = "backups"):
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(exist_ok=True)

        # 创建子目录
        self.mysql_backup_dir = self.backup_dir / "mysql"
        self.mongodb_backup_dir = self.backup_dir / "mongodb"
        self.redis_backup_dir = self.backup_dir / "redis"

        self.mysql_backup_dir.mkdir(exist_ok=True)
        self.mongodb_backup_dir.mkdir(exist_ok=True)
        self.redis_backup_dir.mkdir(exist_ok=True)

        # 保留天数
        self.retention_days = 30

        # 检测操作系统
        self.is_windows = platform.system() == "Windows"
        logger.info(f"操作系统: {platform.system()}")

    def backup_mysql(self, mysql_config: dict):
        """备份MySQL数据库"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = self.mysql_backup_dir / f"mysql_backup_{timestamp}.sql.gz"

            logger.info(f"开始MySQL备份...")
            logger.info(f"数据库: {mysql_config.get('database')}")

            # 检查mysqldump命令是否可用
            mysqldump_cmd = self._find_command("mysqldump")
            if not mysqldump_cmd:
                logger.error("未找到mysqldump命令，请确保MySQL客户端工具已安装")
                return None

            logger.info(f"使用mysqldump命令: {mysqldump_cmd}")

            # 构建mysqldump命令
            cmd = [
                mysqldump_cmd,
                f"--host={mysql_config.get('host', 'localhost')}",
                f"--port={mysql_config.get('port', 3306)}",
                f"--user={mysql_config.get('user', 'root')}",
                f"--password={mysql_config.get('password')}",
                "--single-transaction",
                "--routines",
                "--triggers",
                "--events",
                mysql_config.get("database")
            ]

            # 执行备份（不使用text=True，因为输出是二进制数据）
            result = subprocess.run(cmd, capture_output=True)

            if result.returncode == 0:
                # 直接写入gzip文件（不使用text模式）
                with gzip.open(backup_file, 'wb') as f:
                    f.write(result.stdout)

                backup_size = backup_file.stat().st_size
                logger.info(f"MySQL备份成功: {backup_file}")
                logger.info(f"备份大小: {backup_size} bytes")

                # 清理旧备份
                self._cleanup_old_backups(self.mysql_backup_dir, "*.sql.gz")

                return str(backup_file)
            else:
                error_msg = result.stderr.decode('utf-8', errors='ignore') if result.stderr else "未知错误"
                logger.error(f"MySQL备份失败: {error_msg}")
                return None

        except Exception as e:
            logger.error(f"MySQL备份异常: {e}", exc_info=True)
            return None

    def backup_mongodb(self, mongodb_config: dict):
        """备份MongoDB数据库（使用pymongo直接导出）"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = self.mongodb_backup_dir / f"mongodb_backup_{timestamp}.json.gz"

            logger.info(f"开始MongoDB备份...")
            logger.info(f"数据库: {mongodb_config.get('database')}")

            # 使用pymongo连接数据库
            from pymongo import MongoClient

            # 直接使用参数连接，避免URI编码问题
            client = MongoClient(
                host=mongodb_config.get('host'),
                port=mongodb_config.get('port'),
                username=mongodb_config.get('user'),
                password=mongodb_config.get('password'),
                authSource=mongodb_config.get('database'),
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=5000
            )
            db = client[mongodb_config.get('database')]

            # 测试连接
            try:
                client.admin.command('ping')
                logger.info("MongoDB连接成功")
            except Exception as e:
                logger.error(f"MongoDB连接失败: {e}")
                client.close()
                return None

            # 获取所有集合
            collections = db.list_collection_names()

            # 导出所有集合的数据
            backup_data = {}
            for collection_name in collections:
                try:
                    collection = db[collection_name]
                    documents = list(collection.find())
                    backup_data[collection_name] = documents
                    logger.info(f"已导出集合: {collection_name} ({len(documents)} 条文档)")
                except Exception as e:
                    logger.warning(f"导出集合 {collection_name} 失败: {e}")
                    backup_data[collection_name] = []

            # 将数据转换为JSON字符串
            json_data = json.dumps(backup_data, ensure_ascii=False, indent=2, default=str)

            # 压缩并保存备份文件
            with gzip.open(backup_file, 'wt', encoding='utf-8') as f:
                f.write(json_data)

            backup_size = backup_file.stat().st_size
            logger.info(f"MongoDB备份成功: {backup_file}")
            logger.info(f"备份大小: {backup_size} bytes")
            logger.info(f"备份集合数: {len(collections)}")

            # 关闭连接
            client.close()

            # 清理旧备份
            self._cleanup_old_backups(self.mongodb_backup_dir, "*.json.gz")

            return str(backup_file)

        except Exception as e:
            logger.error(f"MongoDB备份异常: {e}", exc_info=True)
            return None

    def backup_redis(self, redis_config: dict):
        """备份Redis数据（RDB文件）"""
        try:
            logger.info(f"开始Redis备份...")

            # Redis RDB文件通常在Redis数据目录中
            # 这里我们使用Redis的BGSAVE命令来触发后台保存
            import redis

            r = redis.Redis(
                host=redis_config.get('host', 'localhost'),
                port=redis_config.get('port', 6379),
                db=redis_config.get('db', 0),
                password=redis_config.get('password'),
                socket_timeout=5,
                socket_connect_timeout=5
            )

            # 测试连接
            try:
                r.ping()
                logger.info("Redis连接成功")
            except Exception as e:
                logger.error(f"Redis连接失败: {e}")
                return None

            # 触发后台保存
            r.bgsave()

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = self.redis_backup_dir / f"redis_backup_{timestamp}.rdb"

            # 等待后台保存完成
            last_save = r.lastsave()
            import time
            time.sleep(5)  # 等待5秒

            # 获取RDB文件内容
            # 注意：这里需要访问Redis服务器的RDB文件，通常需要直接复制文件
            # 由于Redis RDB文件通常在服务器上，这里只是示例

            logger.info(f"Redis备份触发成功（BGSAVE）")
            logger.info(f"请确保Redis配置了持久化（save配置）")

            # 清理旧备份
            self._cleanup_old_backups(self.redis_backup_dir, "*.rdb")

            return "Redis BGSAVE triggered"

        except Exception as e:
            logger.error(f"Redis备份异常: {e}", exc_info=True)
            return None

    def backup_all(self, mysql_config: dict, mongodb_config: dict, redis_config: dict):
        """备份所有数据库"""
        logger.info("=" * 60)
        logger.info("开始全量备份")
        logger.info("=" * 60)

        results = {
            "mysql": self.backup_mysql(mysql_config),
            "mongodb": self.backup_mongodb(mongodb_config),
            "redis": self.backup_redis(redis_config)
        }

        logger.info("=" * 60)
        logger.info("备份完成")
        logger.info(f"MySQL: {results['mysql']}")
        logger.info(f"MongoDB: {results['mongodb']}")
        logger.info(f"Redis: {results['redis']}")
        logger.info("=" * 60)

        return results

    def _find_command(self, command_name: str) -> str:
        """查找系统命令"""
        try:
            # 在Windows上使用where命令，在Linux上使用which命令
            if self.is_windows:
                result = subprocess.run(['where', command_name], capture_output=True, text=True)
            else:
                result = subprocess.run(['which', command_name], capture_output=True, text=True)

            if result.returncode == 0:
                return result.stdout.strip().split('\n')[0]
            else:
                return None
        except Exception as e:
            logger.warning(f"查找命令 {command_name} 失败: {e}")
            return None

    def _cleanup_old_backups(self, backup_dir: Path, pattern: str):
        """清理旧备份文件"""
        try:
            import time
            current_time = time.time()

            for backup_file in backup_dir.glob(pattern):
                file_age = current_time - backup_file.stat().st_mtime
                if file_age > (self.retention_days * 24 * 60 * 60):
                    backup_file.unlink()
                    logger.info(f"删除旧备份: {backup_file}")

        except Exception as e:
            logger.error(f"清理旧备份异常: {e}", exc_info=True)


def main():
    """主函数"""
    from app.config import get_settings

    settings = get_settings()

    # 创建备份实例
    backup = DatabaseBackup()

    # 配置数据库信息
    mysql_config = {
        "host": settings.mysql_host,
        "port": settings.mysql_port,
        "user": settings.mysql_user,
        "password": settings.mysql_password,
        "database": settings.mysql_database
    }

    mongodb_config = {
        "host": settings.mongodb_host,
        "port": settings.mongodb_port,
        "user": settings.mongodb_user,
        "password": settings.mongodb_password,
        "database": settings.mongodb_database
    }

    redis_config = {
        "host": settings.redis_host,
        "port": settings.redis_port,
        "db": settings.redis_db,
        "password": settings.redis_password
    }

    # 执行备份
    backup.backup_all(mysql_config, mongodb_config, redis_config)


if __name__ == "__main__":
    main()
