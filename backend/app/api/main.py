"""FastAPI主应用"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from loguru import logger

from ..config import get_settings, validate_config, print_config
from ..database.mysql import get_mysql_db
from ..database.mongodb import get_mongodb_client
from ..database.redis_client import get_redis_client
from .routes import trip, poi, map as map_routes
from .routes import auth, plans, user, dialog

# 获取配置
settings = get_settings()

# 创建FastAPI应用
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="基于HelloAgents框架的智能旅行规划助手API",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins_list(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth.router, prefix="/api")  # 认证路由
app.include_router(user.router, prefix="/api")  # 用户管理路由
app.include_router(plans.router, prefix="/api")  # 计划管理路由
app.include_router(dialog.router, prefix="/api")  # 对话管理路由
app.include_router(trip.router, prefix="/api")  # 旅行规划路由
app.include_router(poi.router, prefix="/api")  # 景点查询路由
app.include_router(map_routes.router, prefix="/api")  # 地图服务路由

# 配置静态文件服务（用于访问上传的文件）
storage_path = Path("storage")
storage_path.mkdir(exist_ok=True)
app.mount("/storage", StaticFiles(directory=str(storage_path)), name="storage")


@app.on_event("startup")
async def startup_event():
    """应用启动事件"""
    print("\n" + "="*60)
    print(f"🚀 {settings.app_name} v{settings.app_version}")
    print("="*60)

    # 打印配置信息
    print_config()

    # 验证配置
    try:
        validate_config()
        print("\n✅ 配置验证通过")
    except ValueError as e:
        print(f"\n❌ 配置验证失败:\n{e}")
        print("\n请检查.env文件并确保所有必要的配置项都已设置")
        raise

    # 初始化数据库连接
    print("\n" + "="*60)
    print("📦 初始化数据库连接...")
    print("="*60)

    try:
        # 1. 初始化MySQL
        print("\n1️⃣ 连接MySQL...")
        mysql_db = get_mysql_db()
        if mysql_db.health_check():
            print(f"   ✅ MySQL连接成功: {settings.mysql_host}:{settings.mysql_port}/{settings.mysql_database}")
        else:
            print(f"   ❌ MySQL连接失败")
            raise Exception("MySQL健康检查失败")

        # 2. 初始化MongoDB
        print("\n2️⃣ 连接MongoDB...")
        mongodb_client = get_mongodb_client()
        if await mongodb_client.health_check():
            print(f"   ✅ MongoDB连接成功: {settings.mongodb_database}")
            # 创建索引
            await mongodb_client.create_indexes()
            print(f"   ✅ MongoDB索引创建完成")
        else:
            print(f"   ❌ MongoDB连接失败")
            raise Exception("MongoDB健康检查失败")

        # 3. 初始化Redis
        print("\n3️⃣ 连接Redis...")
        redis_client = get_redis_client()
        if await redis_client.ping():
            print(f"   ✅ Redis连接成功")
        else:
            print(f"   ❌ Redis连接失败")
            raise Exception("Redis健康检查失败")

        print("\n" + "="*60)
        print("✅ 所有数据库连接初始化完成")
        print("="*60)

    except Exception as e:
        logger.error(f"数据库初始化失败: {str(e)}")
        print(f"\n❌ 数据库初始化失败: {str(e)}")
        print("\n请检查数据库配置和连接状态")
        raise

    print("\n" + "="*60)
    print("📚 API文档: http://localhost:8000/docs")
    print("📖 ReDoc文档: http://localhost:8000/redoc")
    print("="*60 + "\n")


@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭事件"""
    print("\n" + "="*60)
    print("👋 应用正在关闭...")
    print("="*60)

    try:
        # 关闭数据库连接
        print("\n📦 关闭数据库连接...")

        # 1. 关闭MySQL
        mysql_db = get_mysql_db()
        mysql_db.close()
        print("   ✅ MySQL连接已关闭")

        # 2. 关闭MongoDB
        mongodb_client = get_mongodb_client()
        mongodb_client.close()
        print("   ✅ MongoDB连接已关闭")

        # 3. 关闭Redis
        redis_client = get_redis_client()
        await redis_client.close()
        print("   ✅ Redis连接已关闭")

        print("\n✅ 所有数据库连接已关闭")
    except Exception as e:
        logger.error(f"关闭数据库连接失败: {str(e)}")
        print(f"\n⚠️  关闭数据库连接时出现错误: {str(e)}")

    print("="*60 + "\n")


@app.get("/")
async def root():
    """根路径"""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "status": "running",
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get("/health")
async def health():
    """健康检查 - 包含数据库连接状态"""
    health_status = {
        "status": "healthy",
        "service": settings.app_name,
        "version": settings.app_version,
        "databases": {
            "mysql": "unknown",
            "mongodb": "unknown",
            "redis": "unknown"
        }
    }

    try:
        # 检查MySQL
        mysql_db = get_mysql_db()
        health_status["databases"]["mysql"] = "healthy" if mysql_db.health_check() else "unhealthy"
    except Exception as e:
        logger.error(f"MySQL健康检查失败: {str(e)}")
        health_status["databases"]["mysql"] = "unhealthy"
        health_status["status"] = "degraded"

    try:
        # 检查MongoDB
        mongodb_client = get_mongodb_client()
        health_status["databases"]["mongodb"] = "healthy" if await mongodb_client.health_check() else "unhealthy"
    except Exception as e:
        logger.error(f"MongoDB健康检查失败: {str(e)}")
        health_status["databases"]["mongodb"] = "unhealthy"
        health_status["status"] = "degraded"

    try:
        # 检查Redis
        redis_client = get_redis_client()
        health_status["databases"]["redis"] = "healthy" if await redis_client.ping() else "unhealthy"
    except Exception as e:
        logger.error(f"Redis健康检查失败: {str(e)}")
        health_status["databases"]["redis"] = "unhealthy"
        health_status["status"] = "degraded"

    # 如果所有数据库都不健康，标记为unhealthy
    if all(status == "unhealthy" for status in health_status["databases"].values()):
        health_status["status"] = "unhealthy"

    return health_status


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.api.main:app",
        host=settings.host,
        port=settings.port,
        reload=True
    )

