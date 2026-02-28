import asyncio
import json
import os

from agentscope.mcp import HttpStatefulClient, HttpStatelessClient
from agentscope.tool import Toolkit

stateful_client = HttpStatefulClient(
    # 用于标识 MCP 的名称
    name="mcp_services_stateful",
    transport="streamable_http",
    url=f"https://mcp.amap.com/mcp?key={os.environ['AMAP_MAPS_API_KEY']}",
)

stateless_client = HttpStatelessClient(
    # 用于标识 MCP 的名称
    name="mcp_services_stateless",
    transport="streamable_http",
    url=f"https://mcp.amap.com/mcp?key={os.environ['AMAP_MAPS_API_KEY']}",
)

toolkit = Toolkit()


async def example_register_stateless_mcp() -> None:
    """注册无状态客户端 MCP 工具的示例。"""
    # 从 MCP 服务器注册所有工具
    await toolkit.register_mcp_client(
        stateless_client,
        # group_name="map_services",  # 可选的组名
    )

    print("注册的 MCP 工具总数：", len(toolkit.get_json_schemas()))

    maps_geo = next(
        tool
        for tool in toolkit.get_json_schemas()
        if tool["function"]["name"] == "maps_geo"
    )
    print("\n示例 ``maps_geo`` 函数：")
    print(
        json.dumps(
            maps_geo,
            indent=4,
            ensure_ascii=False,
        ),
    )

async def example_remove_mcp_tool():
    """删除 MCP 工具的示例。"""
    print("移除前的工具总数", len(toolkit.get_json_schemas()))
    toolkit.remove_tool_function("maps_geo")
    print("移除后的工具总数", len(toolkit.get_json_schemas()))
    await toolkit.remove_mcp_clients(client_names=["mcp_services_stateless"])
    print("移除后的工具总数", len(toolkit.get_json_schemas()))

async def example_function_level_usage() -> None:
    """使用函数级别 MCP 工具的示例。"""
    func_obj = await stateless_client.get_callable_function(
        func_name="maps_geo",
        # 是否将工具结果包装到 AgentScope 的 ToolResponse 中
        wrap_tool_result=True,
    )

    # 您可以获取其名称、描述和 JSON schema
    print("函数名称：", func_obj.name)
    print("函数描述：", func_obj.description)
    print(
        "函数 JSON schema：",
        json.dumps(func_obj.json_schema, indent=4, ensure_ascii=False),
    )

    # 直接调用函数对象
    res = await func_obj(
        address="天安门广场",
        city="北京",
    )
    print("\n函数调用结果：")
    print(res)


if __name__ == '__main__':
    # asyncio.run(example_register_stateless_mcp())
    # asyncio.run(example_remove_mcp_tool())
    asyncio.run(example_function_level_usage())