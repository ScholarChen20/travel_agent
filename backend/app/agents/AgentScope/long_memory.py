import os
import asyncio

from agentscope.message import Msg
from agentscope.memory import InMemoryMemory, Mem0LongTermMemory
from agentscope.agent import ReActAgent
from agentscope.embedding import DashScopeTextEmbedding
from agentscope.formatter import DashScopeChatFormatter
from agentscope.model import DashScopeChatModel
from agentscope.tool import Toolkit
from agentscope.rag import (
    TextReader,
    SimpleKnowledge,
    QdrantStore,
    Document,
    ImageReader,
)

# 创建 mem0 长期记忆实例
long_term_memory = Mem0LongTermMemory(
    agent_name="Friday",
    user_name="user_123",
    model=DashScopeChatModel(
        model_name="qwen-max-latest",
        api_key=os.environ.get("DASHSCOPE_API_KEY"),
        stream=False,
    ),
    embedding_model=DashScopeTextEmbedding(
        model_name="text-embedding-v2",
        api_key=os.environ.get("DASHSCOPE_API_KEY"),
    ),
    on_disk=False,
)

async def basic_usage():
    """基本使用示例"""
    # 记录记忆
    await long_term_memory.record([Msg("user", "我喜欢住民宿", "user")])

    # 检索记忆
    results = await long_term_memory.retrieve(
        [Msg("user", "我的住宿偏好", "user")],
    )
    print(f"检索结果: {results}")

agent = ReActAgent(
    name="Friday",
    sys_prompt="你是一个具有长期记忆功能的助手。",
    model=DashScopeChatModel(
        api_key=os.environ.get("DASHSCOPE_API_KEY"),
        model_name="qwen-max-latest",
    ),
    formatter=DashScopeChatFormatter(),
    toolkit=Toolkit(),
    memory=InMemoryMemory(),
    long_term_memory=long_term_memory,
    long_term_memory_mode="static_control",  # 使用 static_control 模式
)
async def retrieve_preferences():
    """Retrieve user preferences from long-term memory"""
    # 我们清空智能体的短期记忆，以避免造成干扰
    await agent.memory.clear()

    # 测试智能体是否会记住之前的对话
    msg2 = Msg("user", "我有什么偏好？简要的回答我", "user")
    await agent(msg2)

# asyncio.run(basic_usage())
asyncio.run(retrieve_preferences())