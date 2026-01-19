"""MySQL数据库连接管理"""

from contextlib import contextmanager
from typing import Generator
from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from sqlalchemy.pool import Pool
from loguru import logger

# 声明式基类
Base = declarative_base()


class MySQLDatabase:
    """MySQL数据库连接管理器"""

    def __init__(self, database_url: str):
        """
        初始化MySQL数据库连接

        Args:
            database_url: 数据库连接URL，格式：mysql+pymysql://user:password@host:port/database
        """
        self.database_url = database_url

        # 创建数据库引擎
        self.engine = create_engine(
            database_url,
            pool_size=20,  # 连接池大小
            max_overflow=40,  # 超过pool_size后允许的最大连接数
            pool_pre_ping=True,  # 连接前先ping测试连接是否有效
            pool_recycle=3600,  # 连接回收时间（秒），防止MySQL 8小时超时
            echo=False,  # 不打印SQL语句（生产环境）
            pool_timeout=30,  # 获取连接的超时时间
        )

        # 创建会话工厂
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )

        # 设置连接池监听器
        self._setup_pool_listeners()

        logger.info(f"MySQL数据库引擎已创建：{self._safe_url()}")

    def _safe_url(self) -> str:
        """返回隐藏密码的安全URL（用于日志）"""
        parts = self.database_url.split('@')
        if len(parts) == 2:
            # mysql+pymysql://user:password@host:port/database
            user_part = parts[0].split('://')[0] + '://***'
            return f"{user_part}@{parts[1]}"
        return "***"

    def _setup_pool_listeners(self):
        """设置连接池事件监听器"""

        @event.listens_for(Pool, "connect")
        def receive_connect(dbapi_conn, connection_record):
            """连接建立时的回调"""
            logger.debug("MySQL连接池：新连接已建立")

        @event.listens_for(Pool, "checkout")
        def receive_checkout(dbapi_conn, connection_record, connection_proxy):
            """从连接池获取连接时的回调"""
            logger.debug("MySQL连接池：连接已被检出")

    @contextmanager
    def get_session(self) -> Generator[Session, None, None]:
        """
        获取数据库会话（上下文管理器）

        使用示例：
            with mysql_db.get_session() as session:
                user = session.query(User).filter_by(id=1).first()

        Yields:
            Session: SQLAlchemy会话对象
        """
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"MySQL事务失败，已回滚: {str(e)}")
            raise
        finally:
            session.close()

    def get_session_direct(self) -> Session:
        """
        直接获取数据库会话（需要手动管理）

        注意：使用后需要手动调用session.close()

        Returns:
            Session: SQLAlchemy会话对象
        """
        return self.SessionLocal()

    def create_all_tables(self):
        """
        创建所有表（基于Base.metadata）

        注意：仅用于开发环境，生产环境应使用迁移工具（如Alembic）
        """
        logger.info("开始创建所有数据库表...")
        Base.metadata.create_all(bind=self.engine)
        logger.info("所有数据库表创建完成")

    def drop_all_tables(self):
        """
        删除所有表（危险操作！）

        注意：仅用于开发/测试环境
        """
        logger.warning("删除所有数据库表（危险操作）")
        Base.metadata.drop_all(bind=self.engine)
        logger.info("所有数据库表已删除")

    def health_check(self) -> bool:
        """
        健康检查：测试数据库连接是否正常

        Returns:
            bool: True表示连接正常，False表示连接异常
        """
        try:
            with self.get_session() as session:
                session.execute(text("SELECT 1"))
            logger.debug("MySQL健康检查：连接正常")
            return True
        except Exception as e:
            logger.error(f"MySQL健康检查失败: {str(e)}")
            return False

    def close(self):
        """关闭数据库连接池"""
        if self.engine:
            self.engine.dispose()
            logger.info("MySQL连接池已关闭")


# 全局MySQL数据库实例（单例模式）
_mysql_db: MySQLDatabase = None


def get_mysql_db() -> MySQLDatabase:
    """
    获取全局MySQL数据库实例（单例）

    Returns:
        MySQLDatabase: 数据库实例
    """
    global _mysql_db
    if _mysql_db is None:
        raise RuntimeError("MySQL数据库未初始化，请先调用init_mysql_db()")
    return _mysql_db


def init_mysql_db(database_url: str) -> MySQLDatabase:
    """
    初始化全局MySQL数据库实例

    Args:
        database_url: 数据库连接URL

    Returns:
        MySQLDatabase: 数据库实例
    """
    global _mysql_db
    if _mysql_db is None:
        _mysql_db = MySQLDatabase(database_url)
    return _mysql_db
