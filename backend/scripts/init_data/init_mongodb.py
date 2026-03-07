"""
MongoDB数据库初始化脚本

功能：
1. 创建所有集合
2. 创建索引
3. 验证连接
"""

import sys
import os
from pathlib import Path

# 设置UTF-8编码（Windows兼容）
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.errors import CollectionInvalid
from ..app.config import get_settings


def init_mongodb():
    """初始化MongoDB数据库"""
    settings = get_settings()

    print("="*60)
    print("🚀 开始初始化MongoDB数据库...")
    print("="*60)

    # 连接MongoDB
    print(f"\n📡 连接MongoDB: {settings.mongodb_host}:{settings.mongodb_port}")
    client = MongoClient(settings.mongodb_uri, serverSelectionTimeoutMS=5000)

    try:
        # 测试连接
        client.admin.command('ping')
        print("✅ MongoDB连接成功")
    except Exception as e:
        print(f"❌ MongoDB连接失败: {str(e)}")
        return False

    # 选择数据库
    db = client[settings.mongodb_database]
    print(f"📦 使用数据库: {settings.mongodb_database}")

    # ========== 创建集合 ==========
    print("\n" + "="*60)
    print("📁 创建集合...")
    print("="*60)

    collections = [
        "dialog_sessions",      # 对话会话
        "tool_call_logs",       # 工具调用日志
        "travel_plans",         # 旅行计划
        "agent_context_memory"  # Agent上下文记忆
    ]

    for collection_name in collections:
        try:
            db.create_collection(collection_name)
            print(f"  ✅ 创建集合: {collection_name}")
        except CollectionInvalid:
            print(f"  ⚠️  集合已存在: {collection_name}")

    # ========== 创建索引 ==========
    print("\n" + "="*60)
    print("🔍 创建索引...")
    print("="*60)

    # dialog_sessions索引
    print("\n  📊 dialog_sessions集合:")
    dialog_sessions = db.dialog_sessions
    dialog_sessions.create_index([("user_id", ASCENDING), ("last_message_at", DESCENDING)])
    print("    ✅ 创建索引: (user_id, last_message_at)")

    dialog_sessions.create_index([("session_id", ASCENDING)], unique=True)
    print("    ✅ 创建唯一索引: session_id")

    dialog_sessions.create_index([("status", ASCENDING), ("updated_at", DESCENDING)])
    print("    ✅ 创建索引: (status, updated_at)")

    # tool_call_logs索引
    print("\n  📊 tool_call_logs集合:")
    tool_call_logs = db.tool_call_logs
    tool_call_logs.create_index([("session_id", ASCENDING), ("created_at", DESCENDING)])
    print("    ✅ 创建索引: (session_id, created_at)")

    tool_call_logs.create_index([("user_id", ASCENDING), ("tool_name", ASCENDING), ("created_at", DESCENDING)])
    print("    ✅ 创建索引: (user_id, tool_name, created_at)")

    tool_call_logs.create_index([("created_at", DESCENDING)])
    print("    ✅ 创建索引: created_at")

    # travel_plans索引
    print("\n  📊 travel_plans集合:")
    travel_plans = db.travel_plans
    travel_plans.create_index([("user_id", ASCENDING), ("created_at", DESCENDING)])
    print("    ✅ 创建索引: (user_id, created_at)")

    travel_plans.create_index([("plan_id", ASCENDING)], unique=True)
    print("    ✅ 创建唯一索引: plan_id")

    travel_plans.create_index([("session_id", ASCENDING)])
    print("    ✅ 创建索引: session_id")

    travel_plans.create_index([("city", ASCENDING), ("start_date", DESCENDING)])
    print("    ✅ 创建索引: (city, start_date)")

    # agent_context_memory索引
    print("\n  📊 agent_context_memory集合:")
    agent_context_memory = db.agent_context_memory
    agent_context_memory.create_index([("session_id", ASCENDING), ("agent_name", ASCENDING)])
    print("    ✅ 创建索引: (session_id, agent_name)")

    # ========== 验证集合和索引 ==========
    print("\n" + "="*60)
    print("🔬 验证集合和索引...")
    print("="*60)

    existing_collections = db.list_collection_names()
    print(f"\n  📚 现有集合数量: {len(existing_collections)}")
    for col in existing_collections:
        indexes = list(db[col].list_indexes())
        print(f"    • {col}: {len(indexes)} 个索引")

    # 关闭连接
    client.close()

    print("\n" + "="*60)
    print("✅ MongoDB数据库初始化完成！")
    print("="*60)

    return True


if __name__ == "__main__":
    try:
        success = init_mongodb()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ 初始化失败: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
