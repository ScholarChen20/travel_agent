import agentscope
from agentscope.message import (
    Msg,
    Base64Source,
    TextBlock,
    ThinkingBlock,
    ImageBlock,
    AudioBlock,
    VideoBlock,
    ToolUseBlock,
    ToolResultBlock,
)
import json
from agentscope.agent import ReActAgent, AgentBase
from agentscope.formatter import DashScopeChatFormatter
from agentscope.memory import InMemoryMemory
from agentscope.message import Msg
from agentscope.model import DashScopeChatModel
import asyncio
import os

from agentscope.tool import Toolkit, execute_python_code
async def creating_react_agent():
    toolkit = Toolkit()
    toolkit.register_tool_function(execute_python_code) # 注册 python 代码执行工具

    jarvis = ReActAgent(
        name = "Jarvis",
        sys_prompt= """你是一个名为贾维斯的人工智能机器人，你是为钢铁侠量身定做的机器人，你可以识别主人的一切指令要求并快速分析所有结果""",
        model = DashScopeChatModel(
            api_key='sk-1c854040b85549a3be779d4e95665176111',
            model_name="qwen-max",
            stream=True,
            enable_thinking=True,
        ),
        formatter=DashScopeChatFormatter(),
        memory=InMemoryMemory(),
        toolkit=toolkit,
    )
    msg = Msg(
        name="user",
        content="你好！Jarvis，用 Python 运行 Hello World。",
        role="user",
    )

    await jarvis(msg)

def mag():
    msg = Msg(
        name="Jarvis",
        role="assistant",
        content=[
            TextBlock(
                type="text",
                text="这是一个包含 base64 编码数据的多模态消息。",
            ),
            ImageBlock(
                type="image",
                source=Base64Source(
                    type="base64",
                    media_type="image/jpeg",
                    data="/9j/4AAQSkZ...",
                ),
            ),
            AudioBlock(
                type="audio",
                source=Base64Source(
                    type="base64",
                    media_type="audio/mpeg",
                    data="SUQzBAAAAA...",
                ),
            ),
            VideoBlock(
                type="video",
                source=Base64Source(
                    type="base64",
                    media_type="video/mp4",
                    data="AAAAIGZ0eX...",
                ),
            ),
        ],
    )

    msg_thinking = Msg(
        name="Jarvis",
        role="assistant",
        content=[
            ThinkingBlock(
                type="thinking",
                thinking="我正在为 AgentScope 构建一个思考块的示例。",
            ),
            TextBlock(
                type="text",
                text="这是一个思考块的示例。",
            ),
        ],
    )

    msg_tool_call = Msg(
        name="Jarvis",
        role="assistant",
        content=[
            ToolUseBlock(
                type="tool_use",
                id="343",
                name="get_weather",
                input={
                    "location": "Beijing",
                },
            ),
        ],
    )

    msg_tool_res = Msg(
        name="system",
        role="system",
        content=[
            ToolResultBlock(
                type="tool_result",
                id="343",
                name="get_weather",
                output="北京的天气是晴天，温度为 25°C。",
            ),
        ],
    )
    serialized_msg = msg.to_dict()

    print(type(serialized_msg))
    print(json.dumps(serialized_msg, indent=4, ensure_ascii=False))

if __name__ == '__main__':
    asyncio.run(creating_react_agent())  # asyncio表示异步执行

