"""FastAPI主应用"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from pathlib import Path
from loguru import logger

from ..config import get_settings, validate_config, print_config
from ..database.mysql import get_mysql_db, init_mysql_db
from ..database.mongodb import get_mongodb_client, init_mongodb_client
from ..database.redis_client import get_redis_client, init_redis_client
from .routes import trip, poi, map as map_routes
from .routes import auth, plans, user, dialog, social, admin

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
    allow_origins=settings.get_cors_origins_list() + ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# 全局异常处理器 - 确保所有错误响应都包含CORS头
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"全局异常捕获: {type(exc).__name__}: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": f"服务器内部错误: {str(exc)}"},
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Credentials": "true",
            "Access-Control-Allow-Methods": "*",
            "Access-Control-Allow-Headers": "*",
        }
    )

# 注册路由
app.include_router(auth.router, prefix="/api")  # 认证路由
app.include_router(user.router, prefix="/api")  # 用户管理路由
app.include_router(plans.router, prefix="/api")  # 计划管理路由
app.include_router(dialog.router, prefix="/api")  # 对话管理路由
app.include_router(social.router, prefix="/api")  # 社交功能路由
app.include_router(admin.router, prefix="/api")  # 管理后台路由
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
        init_mysql_db(settings.mysql_url)
        mysql_db = get_mysql_db()
        if mysql_db.health_check():
            print(f"   ✅ MySQL连接成功: {settings.mysql_host}:{settings.mysql_port}/{settings.mysql_database}")
        else:
            print(f"   ❌ MySQL连接失败")
            raise Exception("MySQL健康检查失败")

        # 2. 初始化MongoDB
        print("\n2️⃣ 连接MongoDB...")
        init_mongodb_client(settings.mongodb_uri, settings.mongodb_database)
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
        init_redis_client(settings.redis_url)
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
    """健康检查 - 包含数据库连接状态、磁盘空间、Agent状态"""
    from ..services.monitoring_service import get_monitoring_service

    try:
        monitoring_service = get_monitoring_service()
        health_report = await monitoring_service.get_comprehensive_health()
        return health_report
    except Exception as e:
        logger.error(f"健康检查失败: {str(e)}")
        return {
            "overall_status": "error",
            "error": str(e)
        }


@app.get("/metrics")
async def metrics():
    """性能指标 - CPU、内存、磁盘、网络"""
    from ..services.monitoring_service import get_monitoring_service

    try:
        monitoring_service = get_monitoring_service()
        metrics_data = monitoring_service.get_performance_metrics()
        return metrics_data
    except Exception as e:
        logger.error(f"获取性能指标失败: {str(e)}")
        return {
            "error": str(e)
        }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.api.main:app",
        host=settings.host,
        port=settings.port,
        reload=True
    )

