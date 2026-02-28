import asyncio
import json

import fakeredis
from sqlalchemy.ext.asyncio import create_async_engine

from agentscope.memory import (
    InMemoryMemory,
    AsyncSQLAlchemyMemory,
    RedisMemory,
)
from agentscope.message import Msg


async def redis_memory_example() -> None:
    """使用 RedisMemory 在 Redis 中存储消息的示例。"""
    global redis_pool
    redis_pool = ConnectionPool(
         host="localhost",
         port=6379,
         db=1,
         password=123456,
         decode_responses=True,
         max_connections=10,
         encoding="utf-8",
     )
    # 使用fakeredis进行内存测试，无需真实的 Redis 服务器
    fake_redis = fakeredis.aioredis.FakeRedis(decode_responses=True)
    # 创建 Redis 记忆
    memory = RedisMemory(
        # 使用fake redis进行演示
        connection_pool=redis_pool,
        # 也可以通过指定主机和端口连接到真实的Redis服务器
        host="localhost",
        port=6379,
        db=1,
        password='123456',
        user_id="user_1",
        session_id="session_1",
    )

    # 向记忆中添加消息
    await memory.add(
        Msg(
            "Alice",
            "生成一份关于AgentScope的报告",
            "user",
        ),
    )

    # 添加一条带有标记"hint"的提示消息
    await memory.add(
        Msg(
            "system",
            "<system-hint>首先创建一个计划来收集信息，然后逐步生成报告。</system-hint>",
            "system",
        ),
        marks="hint",
    )

    # 检索带有标记"hint"的消息
    msgs = await memory.get_memory(mark="hint")
    print("带有标记'hint'的消息：")
    for msg in msgs:
        print(f"- {msg}")

from redis.asyncio import ConnectionPool


# asyncio.run(redis_memory_example())

async def sqlalchemy_context_example() -> None:
    """使用 AsyncSQLAlchemyMemory 作为异步上下文管理器的示例。"""
    engine = create_async_engine("sqlite+aiosqlite:///./test_memory.db")
    async with AsyncSQLAlchemyMemory(
        engine_or_session=engine,
        user_id="user_1",
        session_id="session_1",
    ) as memory:
        await memory.add(
            Msg("Alice", "生成一份关于 AgentScope 的报告", "user"),
        )

        msgs = await memory.get_memory()
        print("记忆中的所有消息：")
        for msg in msgs:
            print(f"- {msg}")


async def in_memory_example():
    """使用InMemoryMemory在内存中存储消息的示例。"""
    memory = InMemoryMemory()
    await memory.add(
        Msg("Alice", "生成一份关于AgentScope的报告", "user"),
    )

    # 添加一条带有标记"hint"的提示消息
    await memory.add(
        [
            Msg(
                "system",
                "<system-hint>首先创建一个计划来收集信息，然后逐步生成报告。</system-hint>",
                "system",
            ),
        ],
        marks="hint",
    )

    msgs = await memory.get_memory(mark="hint")
    print("带有标记'hint'的消息：")
    for msg in msgs:
        print(f"- {msg}")

    # 所有存储的消息都可以通过 ``state_dict`` 和 ``load_state_dict`` 方法导出和加载。
    state = memory.state_dict()
    print("记忆的状态字典：")
    print(json.dumps(state, indent=2, ensure_ascii=False))

    # 通过标记删除消息
    deleted_count = await memory.delete_by_mark("hint")
    print(f"删除了 {deleted_count} 条带有标记'hint'的消息。")

    print("删除后的记忆状态字典：")
    state = memory.state_dict()
    print(json.dumps(state, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    # asyncio.run(sqlalchemy_context_example())
    asyncio.run(in_memory_example())