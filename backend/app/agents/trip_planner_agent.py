"""多智能体旅行规划系统"""

import json
import os
import time
import asyncio
import re
from typing import Dict, Any, List, Optional

from hello_agents import SimpleAgent, ReActAgent
from hello_agents.tools import MCPTool
from hello_agents.tools.base import Tool, ToolParameter
from hello_agents.tools.registry import ToolRegistry
from ..services.llm_service import get_llm
from ..models.schemas import TripRequest, TripPlan, DayPlan, Attraction, Meal, WeatherInfo, Location, Hotel
from ..config import get_settings
from ..services.rag import HybridRAGService, RAGSearchResult, get_hybrid_rag_service


class MCPToolWrapper(Tool):
    """MCP工具包装器 - 解决hello_agents库中Tool抽象类实例化问题"""
    
    def __init__(self, name: str, description: str, mcp_tool, tool_name: str):
        super().__init__(name=name, description=description)
        self._mcp_tool = mcp_tool
        self._tool_name = tool_name
    
    def run(self, parameters: Dict[str, Any]) -> str:
        """执行工具"""
        return self._mcp_tool.run({
            "action": "call_tool",
            "tool_name": self._tool_name,
            "arguments": parameters
        })
    
    def get_parameters(self) -> List[ToolParameter]:
        """获取工具参数定义"""
        return [
            ToolParameter(
                name="input",
                type="string",
                description="输入参数",
                required=True
            )
        ]

# ============ Agent提示词 ============

ATTRACTION_AGENT_PROMPT = """你是景点搜索专家。你的任务是根据城市和用户偏好搜索合适的景点。

**重要提示:**
你必须使用工具来搜索景点!不要自己编造景点信息!

**工具调用格式:**
使用maps_text_search工具时,必须严格按照以下格式:
`[TOOL_CALL:amap_maps_text_search:keywords=景点关键词,city=城市名]`

**示例:**
用户: "搜索北京的历史文化景点"
你的回复: [TOOL_CALL:amap_maps_text_search:keywords=历史文化,city=北京]

用户: "搜索上海的公园"
你的回复: [TOOL_CALL:amap_maps_text_search:keywords=公园,city=上海]

**注意:**
1. 必须使用工具,不要直接回答
2. 格式必须完全正确,包括方括号和冒号
3. 参数用逗号分隔
"""

WEATHER_AGENT_PROMPT = """你是天气查询专家。你的任务是查询指定城市的天气信息。

**重要提示:**
你必须使用工具来查询天气!不要自己编造天气信息!

**工具调用格式:**
使用maps_weather工具时,必须严格按照以下格式:
`[TOOL_CALL:amap_maps_weather:city=城市名]`

**示例:**
用户: "查询北京天气"
你的回复: [TOOL_CALL:amap_maps_weather:city=北京]

用户: "上海的天气怎么样"
你的回复: [TOOL_CALL:amap_maps_weather:city=上海]

**注意:**
1. 必须使用工具,不要直接回答
2. 格式必须完全正确,包括方括号和冒号
"""

HOTEL_AGENT_PROMPT = """你是酒店推荐专家。你的任务是根据城市和景点位置推荐合适的酒店。

**重要提示:**
你必须使用工具来搜索酒店!不要自己编造酒店信息!

**工具调用格式:**
使用maps_text_search工具搜索酒店时,必须严格按照以下格式:
`[TOOL_CALL:amap_maps_text_search:keywords=酒店,city=城市名]`

**示例:**
用户: "搜索北京的酒店"
你的回复: [TOOL_CALL:amap_maps_text_search:keywords=酒店,city=北京]

**注意:**
1. 必须使用工具,不要直接回答
2. 格式必须完全正确,包括方括号和冒号
3. 关键词使用"酒店"或"宾馆"
"""

PLANNER_AGENT_PROMPT = """你是行程规划专家。你的任务是根据景点信息和天气信息,生成详细的旅行计划。

请严格按照以下JSON格式返回旅行计划:
```json
{
  "city": "城市名称",
  "start_date": "YYYY-MM-DD",
  "end_date": "YYYY-MM-DD",
  "days": [
    {
      "date": "YYYY-MM-DD",
      "day_index": 0,
      "description": "第1天行程概述",
      "transportation": "交通方式",
      "accommodation": "住宿类型",
      "hotel": {
        "name": "酒店名称",
        "address": "酒店地址",
        "location": {"longitude": 116.397128, "latitude": 39.916527},
        "price_range": "300-500元",
        "rating": "4.5",
        "distance": "距离景点2公里",
        "type": "经济型酒店",
        "estimated_cost": 400
      },
      "attractions": [
        {
          "name": "景点名称",
          "address": "详细地址",
          "location": {"longitude": 116.397128, "latitude": 39.916527},
          "visit_duration": 120,
          "description": "景点详细描述",
          "category": "景点类别",
          "ticket_price": 60
        }
      ],
      "meals": [
        {"type": "breakfast", "name": "早餐推荐", "description": "早餐描述", "estimated_cost": 30},
        {"type": "lunch", "name": "午餐推荐", "description": "午餐描述", "estimated_cost": 50},
        {"type": "dinner", "name": "晚餐推荐", "description": "晚餐描述", "estimated_cost": 80}
      ]
    }
  ],
  "weather_info": [
    {
      "date": "YYYY-MM-DD",
      "day_weather": "晴",
      "night_weather": "多云",
      "day_temp": 25,
      "night_temp": 15,
      "wind_direction": "南风",
      "wind_power": "1-3级"
    }
  ],
  "overall_suggestions": "总体建议",
  "budget": {
    "total_attractions": 180,
    "total_hotels": 1200,
    "total_meals": 480,
    "total_transportation": 200,
    "total": 2060
  }
}
```

**重要提示:**
1. weather_info数组必须包含每一天的天气信息
2. 温度必须是纯数字(不要带°C等单位)
3. 每天安排2-3个景点
4. 考虑景点之间的距离和游览时间
5. 每天必须包含早中晚三餐
6. 提供实用的旅行建议
7. **必须包含预算信息**:
   - 景点门票价格(ticket_price)
   - 餐饮预估费用(estimated_cost)
   - 酒店预估费用(estimated_cost)
   - 预算汇总(budget)包含各项总费用
"""


class MultiAgentTripPlanner:
    """多智能体旅行规划系统"""

    _instance: Optional['MultiAgentTripPlanner'] = None
    _initialized: bool = False

    def __new__(cls):
        """单例模式 - 确保只创建一个实例"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """初始化多智能体系统"""
        if self._initialized:
            return
        
        print("[INFO] 开始初始化多智能体旅行规划系统...")

        try:
            settings = get_settings()
            self.llm = get_llm()
            
            self._rag_service: Optional[HybridRAGService] = None
            self._tools_initialized = False
            self.amap_tool = None
            self.attraction_agent = None
            self.weather_agent = None
            self.hotel_agent = None
            self.planner_agent = None

            print("[OK] 多智能体系统基础初始化成功（工具延迟加载）")
            MultiAgentTripPlanner._initialized = True

        except Exception as e:
            print(f"[ERROR] 多智能体系统初始化失败: {str(e)}")
            import traceback
            traceback.print_exc()
            raise

    def _ensure_tools_initialized(self):
        """确保工具已初始化（延迟初始化）"""
        if self._tools_initialized:
            return
        
        try:
            print("[INFO] 延迟初始化MCP工具...")
            
            self.amap_tool = MCPTool(
                name="amap",
                description="高德地图服务",
                server_command=["uvx", "amap-mcp-server"],
                env={"AMAP_MAPS_API_KEY": os.getenv("AMAP_MAPS_API_KEY")},
                auto_expand=False
            )

            print("  - 创建景点搜索Agent...")
            self.attraction_agent = ReActAgent(
                name="景点搜索专家",
                llm=self.llm,
                system_prompt=ATTRACTION_AGENT_PROMPT
            )
            self._register_mcp_tools(self.attraction_agent, self.amap_tool)

            print("  - 创建天气查询Agent...")
            weather_registry = ToolRegistry()
            self._register_mcp_tools_to_registry(weather_registry, self.amap_tool)
            self.weather_agent = SimpleAgent(
                name="天气查询专家",
                llm=self.llm,
                system_prompt=WEATHER_AGENT_PROMPT,
                tool_registry=weather_registry
            )

            print("  - 创建酒店推荐Agent...")
            hotel_registry = ToolRegistry()
            self._register_mcp_tools_to_registry(hotel_registry, self.amap_tool)
            self.hotel_agent = SimpleAgent(
                name="酒店推荐专家",
                llm=self.llm,
                system_prompt=HOTEL_AGENT_PROMPT,
                tool_registry=hotel_registry
            )

            print("  - 创建行程规划Agent...")
            self.planner_agent = SimpleAgent(
                name="行程规划专家",
                llm=self.llm,
                system_prompt=PLANNER_AGENT_PROMPT
            )

            self._tools_initialized = True
            print("[OK] MCP工具初始化成功")

        except Exception as e:
            print(f"[ERROR] MCP工具初始化失败: {str(e)}")
            import traceback
            traceback.print_exc()
            raise
    
    def _register_mcp_tools_to_registry(self, registry: ToolRegistry, mcp_tool):
        """注册MCP工具到ToolRegistry"""
        try:
            if hasattr(mcp_tool, '_available_tools') and mcp_tool._available_tools:
                for tool_info in mcp_tool._available_tools:
                    wrapped_tool = MCPToolWrapper(
                        name=f"{mcp_tool.name}_{tool_info['name']}",
                        description=tool_info.get('description', ''),
                        mcp_tool=mcp_tool,
                        tool_name=tool_info['name']
                    )
                    registry.register_tool(wrapped_tool)
                print(f"    ✓ MCP工具 '{mcp_tool.name}' 已展开为 {len(mcp_tool._available_tools)} 个工具")
            else:
                registry.register_tool(mcp_tool)
                print(f"    ✓ MCP工具 '{mcp_tool.name}' 已注册")
        except Exception as e:
            print(f"    ⚠ MCP工具注册失败: {str(e)}")
            print("    → 将继续运行，但部分功能可能受限")
    
    def _register_mcp_tools(self, agent, mcp_tool):
        """注册MCP工具到Agent"""
        try:
            if hasattr(mcp_tool, '_available_tools') and mcp_tool._available_tools:
                for tool_info in mcp_tool._available_tools:
                    wrapped_tool = MCPToolWrapper(
                        name=f"{mcp_tool.name}_{tool_info['name']}",
                        description=tool_info.get('description', ''),
                        mcp_tool=mcp_tool,
                        tool_name=tool_info['name']
                    )
                    agent.tool_registry.register_tool(wrapped_tool)
                print(f"    ✓ MCP工具 '{mcp_tool.name}' 已展开为 {len(mcp_tool._available_tools)} 个工具")
            else:
                agent.tool_registry.register_tool(mcp_tool)
                print(f"    ✓ MCP工具 '{mcp_tool.name}' 已注册")
        except Exception as e:
            print(f"    ⚠ MCP工具注册失败: {str(e)}")
            print("    → 将继续运行，但部分功能可能受限")
    
    async def _get_rag_service(self) -> Optional[HybridRAGService]:
        """获取RAG服务实例（延迟初始化）"""
        if self._rag_service is None:
            try:
                self._rag_service = await get_hybrid_rag_service()
                print("[OK] RAG服务初始化成功")
            except Exception as e:
                print(f"[WARN] RAG服务初始化失败: {str(e)}")
                return None
        return self._rag_service

    def _remove_emoji(self, text: str) -> str:
        """移除emoji字符"""
        emoji_pattern = re.compile(
            "["
            "\U0001F600-\U0001F64F"
            "\U0001F300-\U0001F5FF"
            "\U0001F680-\U0001F6FF"
            "\U0001F1E0-\U0001F1FF"
            "\U00002702-\U000027B0"
            "\U000024C2-\U0001F251"
            "]+",
            flags=re.UNICODE
        )
        return emoji_pattern.sub('', text)

    async def _search_rag_posts(
        self,
        query: str,
        city: Optional[str] = None,
        n_results: int = 5,
        credibility_threshold: float = 0.2
    ) -> List[RAGSearchResult]:
        """
        从RAG向量数据库检索相关帖子

        Args:
            query: 查询文本
            city: 城市过滤（可选）
            n_results: 返回结果数量
            credibility_threshold: 置信度阈值

        Returns:
            检索结果列表
        """
        try:
            rag_service = await self._get_rag_service()
            if rag_service is None:
                return []

            # 执行检索
            if city:
                results = await rag_service.search_by_city(query, city, n_results)
            else:
                results = await rag_service.search(
                    query,
                    n_results=n_results,
                    credibility_threshold=credibility_threshold
                )

            return results

        except Exception as e:
            print(f"[WARN] RAG检索失败: {str(e)}")
            return []

    def _format_rag_results_for_context(self, results: List[RAGSearchResult]) -> str:
        """
        将RAG检索结果格式化为上下文文本

        Args:
            results: RAG检索结果

        Returns:
            格式化的上下文文本
        """
        if not results:
            return ""

        context_parts = []
        for i, result in enumerate(results, 1):
            # 移除emoji避免编码问题
            title = self._remove_emoji(result.title)
            content = self._remove_emoji(result.content)

            # 截断过长的内容
            if len(content) > 500:
                content = content[:500] + "..."

            context_parts.append(f"""
【参考游记{i}】(置信度: {result.credibility:.2f})
标题: {title}
标签: {', '.join(result.tags[:5])}
内容摘要: {content}
""")

        return "\n".join(context_parts)
    
    async def _get_rag_context(self, city: str, preferences: List[str] = None) -> str:
        """
        从RAG获取旅行上下文

        Args:
            city: 城市名称
            preferences: 用户偏好

        Returns:
            RAG上下文文本
        """
        try:
            # 构建查询
            query_parts = [city]
            if preferences:
                query_parts.extend(preferences[:3])

            query = " ".join(query_parts)

            # 检索相关帖子
            results = await self._search_rag_posts(
                query=query,
                city=city,
                n_results=8,
                credibility_threshold=0.2
            )

            if not results:
                print(f"[WARN] RAG未找到 {city} 相关帖子")
                return ""

            # 格式化结果
            context = self._format_rag_results_for_context(results)
            print(f"[OK] RAG获取 {len(results)} 条相关帖子")

            return context

        except Exception as e:
            print(f"[WARN] 获取RAG上下文失败: {str(e)}")
            return ""
    
    async def plan_trip(self, request: TripRequest) -> TripPlan:
        """
        使用多智能体协作生成旅行计划

        Args:
            request: 旅行请求

        Returns:
            旅行计划
        """
        try:
            self._ensure_tools_initialized()
            
            print(f"\n{'='*60}")
            print("[START] 开始多智能体协作规划旅行...")
            print(f"目的地: {request.city}")
            print(f"日期: {request.start_date} 至 {request.end_date}")
            print(f"天数: {request.travel_days}天")
            print(f"偏好: {', '.join(request.preferences) if request.preferences else '无'}")
            print(f"{'='*60}\n")

            # 步骤0: 从RAG获取旅行上下文（新增）
            print("[STEP0] 获取RAG旅行上下文...")
            rag_context = await self._get_rag_context(request.city, request.preferences)
            if rag_context:
                print(f"RAG上下文获取成功，长度: {len(rag_context)}")
            else:
                print("RAG上下文获取失败或为空，将使用基础规划")

            # 步骤1: 景点搜索Agent搜索景点
            print("[STEP1] 搜索景点...")
            attraction_query = self._build_attraction_query(request)
            attraction_response = await asyncio.to_thread(self.attraction_agent.run, attraction_query)
            print(f"景点搜索结果: {attraction_response[:200]}...\n")

            # 步骤2: 天气查询Agent查询天气
            print("[STEP2] 查询天气...")
            weather_query = f"请查询{request.city}的天气信息"
            weather_response = await asyncio.to_thread(self.weather_agent.run, weather_query)
            print(f"天气查询结果: {weather_response[:200]}...\n")

            # 步骤3: 酒店推荐Agent搜索酒店
            print("[STEP3] 搜索酒店...")
            hotel_query = f"请搜索{request.city}的{request.accommodation}酒店"
            hotel_response = await asyncio.to_thread(self.hotel_agent.run, hotel_query)
            print(f"酒店搜索结果: {hotel_response[:200]}...\n")

            # 步骤4: 行程规划Agent整合信息生成计划
            print("[STEP4] 生成行程计划...")
            planner_query = self._build_planner_query(request, attraction_response, weather_response, hotel_response, rag_context)
            planner_response = await asyncio.to_thread(self.planner_agent.run, planner_query)
            print(f"行程规划结果: {planner_response[:300]}...\n")

            # 解析最终计划
            trip_plan = self._parse_response(planner_response, request)

            print(f"{'='*60}")
            print("[OK] 旅行计划生成完成!")
            print(f"{'='*60}\n")

            return trip_plan

        except Exception as e:
            print(f"[ERROR] 生成旅行计划失败: {str(e)}")
            import traceback
            traceback.print_exc()
            return self._create_fallback_plan(request)
    
    def _build_attraction_query(self, request: TripRequest) -> str:
        """构建景点搜索查询 - 直接包含工具调用"""
        keywords = []
        if request.preferences:
            # 只取第一个偏好作为关键词
            keywords = request.preferences[0]
        else:
            keywords = "景点"

        # 直接返回工具调用格式
        query = f"请使用amap_maps_text_search工具搜索{request.city}的{keywords}相关景点。\n[TOOL_CALL:amap_maps_text_search:keywords={keywords},city={request.city}]"
        return query

    def _build_planner_query(self, request: TripRequest, attractions: str, weather: str, hotels: str = "", rag_context: str = "") -> str:
        """构建行程规划查询"""
        query = f"""请根据以下信息生成{request.city}的{request.travel_days}天旅行计划:

**基本信息:**
- 城市: {request.city}
- 日期: {request.start_date} 至 {request.end_date}
- 天数: {request.travel_days}天
- 交通方式: {request.transportation}
- 住宿: {request.accommodation}
- 偏好: {', '.join(request.preferences) if request.preferences else '无'}

**景点信息:**
{attractions}

**天气信息:**
{weather}

**酒店信息:**
{hotels}
"""
        if rag_context:
            query += f"""
**RAG参考信息（来自小红书真实游记）:**
{rag_context}

**RAG信息使用说明:**
1. 参考RAG中的热门景点推荐，优先安排评分高的景点
2. 参考RAG中的美食推荐，安排当地特色美食
3. 参考RAG中的酒店推荐，选择性价比高的住宿
4. 结合RAG中的旅行贴士，提供实用建议
"""

        query += """
**要求:**
1. 每天安排2-3个景点
2. 每天必须包含早中晚三餐
3. 每天推荐一个具体的酒店(从酒店信息中选择)
4. 考虑景点之间的距离和交通方式
5. 返回完整的JSON格式数据
6. 景点的经纬度坐标要真实准确
"""
        if request.free_text_input:
            query += f"\n**额外要求:** {request.free_text_input}"

        return query
    
    def _parse_response(self, response: str, request: TripRequest) -> TripPlan:
        """
        解析Agent响应
        
        Args:
            response: Agent响应文本
            request: 原始请求
            
        Returns:
            旅行计划
        """
        try:
            # 尝试从响应中提取JSON
            # 查找JSON代码块
            if "```json" in response:
                json_start = response.find("```json") + 7
                json_end = response.find("```", json_start)
                json_str = response[json_start:json_end].strip()
            elif "```" in response:
                json_start = response.find("```") + 3
                json_end = response.find("```", json_start)
                json_str = response[json_start:json_end].strip()
            elif "{" in response and "}" in response:
                # 直接查找JSON对象
                json_start = response.find("{")
                json_end = response.rfind("}") + 1
                json_str = response[json_start:json_end]
            else:
                raise ValueError("响应中未找到JSON数据")
            
            # 解析JSON
            data = json.loads(json_str)
            
            # 转换为TripPlan对象
            trip_plan = TripPlan(**data)
            
            return trip_plan
            
        except Exception as e:
            print(f"[WARN] 解析响应失败: {str(e)}")
            print(f"   将使用备用方案生成计划")
            return self._create_fallback_plan(request)
    
    def _create_fallback_plan(self, request: TripRequest) -> TripPlan:
        """创建备用计划(当Agent失败时)"""
        from datetime import datetime, timedelta
        
        # 解析日期
        start_date = datetime.strptime(request.start_date, "%Y-%m-%d")
        
        # 创建每日行程
        days = []
        for i in range(request.travel_days):
            current_date = start_date + timedelta(days=i)
            
            day_plan = DayPlan(
                date=current_date.strftime("%Y-%m-%d"),
                day_index=i,
                description=f"第{i+1}天行程",
                transportation=request.transportation,
                accommodation=request.accommodation,
                attractions=[
                    Attraction(
                        name=f"{request.city}景点{j+1}",
                        address=f"{request.city}市",
                        location=Location(longitude=116.4 + i*0.01 + j*0.005, latitude=39.9 + i*0.01 + j*0.005),
                        visit_duration=120,
                        description=f"这是{request.city}的著名景点",
                        category="景点"
                    )
                    for j in range(2)
                ],
                meals=[
                    Meal(type="breakfast", name=f"第{i+1}天早餐", description="当地特色早餐"),
                    Meal(type="lunch", name=f"第{i+1}天午餐", description="午餐推荐"),
                    Meal(type="dinner", name=f"第{i+1}天晚餐", description="晚餐推荐")
                ]
            )
            days.append(day_plan)
        
        return TripPlan(
            city=request.city,
            start_date=request.start_date,
            end_date=request.end_date,
            days=days,
            weather_info=[],
            overall_suggestions=f"这是为您规划的{request.city}{request.travel_days}日游行程,建议提前查看各景点的开放时间。"
        )


# 全局多智能体系统实例
_multi_agent_planner = None


def get_trip_planner_agent() -> MultiAgentTripPlanner:
    """获取多智能体旅行规划系统实例(单例模式)"""
    global _multi_agent_planner

    if _multi_agent_planner is None:
        _multi_agent_planner = MultiAgentTripPlanner()

    return _multi_agent_planner


# ============ 对话式多智能体系统 ============

INTENT_DETECTION_PROMPT = """你是意图识别专家。分析用户消息并识别意图类型。

**意图类型:**
1. trip_planning - 用户想要规划新的旅行
2. info_query - 用户查询景点/天气/酒店/美食信息，或询问某个地方的介绍
3. plan_modification - 用户想要修改已有计划
4. general_chat - 一般对话

**示例:**
用户: "我想去北京玩3天" -> trip_planning
用户: "故宫的门票多少钱" -> info_query
用户: "故宫有什么好玩的" -> info_query
用户: "介绍一下西湖" -> info_query
用户: "北京有哪些景点" -> info_query
用户: "把第二天的行程改一下" -> plan_modification
用户: "你好" -> general_chat

只返回意图类型,不要其他内容。"""


GENERAL_CHAT_PROMPT = """你是一个专业的智能旅行规划助手，拥有丰富的旅行知识。你能够：
1. 介绍各地景点、文化、美食、风俗
2. 解答旅行相关问题（签证、交通、住宿等）
3. 提供旅行建议和攻略
4. 进行友好的日常对话

**重要提示：**
当用户提供【RAG参考信息】时，你必须：
1. 优先使用这些真实的游记信息来回答问题
2. 不要编造不存在的信息
3. 结合参考信息给出实用建议
4. 如果参考信息不足，可以补充通用知识，但要说明来源

语气友好自然，用中文回答。"""


RAG_ENHANCED_INFO_PROMPT = """你是旅行信息查询专家。你的任务是根据用户问题和RAG检索到的真实游记信息，提供准确的回答。

**重要提示：**
1. 必须优先使用【RAG参考信息】中的真实内容
2. 不要编造不存在的信息
3. 如果RAG信息不足以回答问题，可以补充常识，但要明确标注"通用知识"
4. 回答要具体、实用，引用具体的游记内容
5. 语气友好自然，用中文回答"""


class ConversationalMultiAgentTripPlanner(MultiAgentTripPlanner):
    """对话式多智能体旅行规划系统"""

    def __init__(self, dialog_service):
        """
        初始化对话式系统

        Args:
            dialog_service: 对话服务实例
        """
        super().__init__()
        self.dialog_service = dialog_service

        # 创建意图识别Agent
        self.intent_agent = SimpleAgent(
            name="意图识别专家",
            llm=self.llm,
            system_prompt=INTENT_DETECTION_PROMPT
        )

        # 创建RAG增强的信息查询Agent
        try:
            self.rag_info_agent = SimpleAgent(
                name="RAG增强信息专家",
                llm=self.llm,
                system_prompt=RAG_ENHANCED_INFO_PROMPT
            )
            print("[OK] RAG增强信息Agent初始化成功")
        except Exception as e:
            print(f"[WARN] 创建RAG增强信息Agent失败: {str(e)}")
            self.rag_info_agent = None

        # 创建通用对话Agent（处理景点介绍、旅行问答等）
        try:
            self.general_chat_agent = ReActAgent(
                name="旅行问答专家",
                llm=self.llm,
                system_prompt=GENERAL_CHAT_PROMPT
            )
            print("[OK] 对话式多智能体系统初始化成功")
        except Exception as e:
            print(f"[ERROR] 创建通用对话Agent失败: {str(e)}")
            import traceback
            traceback.print_exc()
            raise

    async def chat(
        self,
        session_id: str,
        user_id: int,
        user_message: str
    ) -> Dict[str, Any]:
        """
        处理多轮对话

        Args:
            session_id: 会话ID
            user_id: 用户ID
            user_message: 用户消息

        Returns:
            Dict: 响应结果
        """
        try:
            # 1. 保存用户消息
            await self.dialog_service.add_message(
                session_id=session_id,
                role="user",
                content=user_message
            )

            # 2. 获取会话上下文
            context = await self.dialog_service.get_session_context(session_id)

            # 3. 意图识别
            intent = await self._detect_intent(user_message, context)


            # 4. 根据意图路由到对应处理器
            if intent == "trip_planning":
                response = await self._handle_trip_planning(session_id, user_id, user_message, context)
            elif intent == "info_query":
                response = await self._handle_info_query(session_id, user_id, user_message, context)
            elif intent == "plan_modification":
                response = await self._handle_plan_modification(session_id, user_id, user_message, context)
            else:
                response = await self._handle_general_chat(session_id, user_id, user_message, context)

            # 5. 保存助手响应
            await self.dialog_service.add_message(
                session_id=session_id,
                role="assistant",
                content=response["message"],
                metadata={"intent": intent}
            )

            return response

        except Exception as e:
            print(f"[ERROR] 对话处理失败: {str(e)}")
            import traceback
            traceback.print_exc()
            raise

    async def _detect_intent(self, user_message: str, context: Dict[str, Any]) -> str:
        """
        检测用户意图

        Args:
            user_message: 用户消息
            context: 会话上下文

        Returns:
            str: 意图类型
        """
        try:
            # 构建意图识别查询
            query = f"用户消息: {user_message}"

            # 使用 to_thread 避免阻塞事件循环
            start_time = time.time()
            intent_response = await asyncio.to_thread(self.intent_agent.run, query)
            execution_time = (time.time() - start_time) * 1000

            # 记录工具调用
            await self.dialog_service.log_tool_call(
                session_id=context["session_id"],
                tool_name="intent_detection",
                input_params={"message": user_message},
                output_result=intent_response,
                execution_time_ms=execution_time,
                status="success"
            )

            # 提取意图
            intent = intent_response.strip().lower()
            if "trip_planning" in intent:
                return "trip_planning"
            elif "info_query" in intent:
                return "info_query"
            elif "plan_modification" in intent:
                return "plan_modification"
            else:
                return "general_chat"

        except Exception as e:
            print(f"[WARN] 意图识别失败: {str(e)}")
            return "general_chat"

    def _extract_city_from_message(self, message: str) -> Optional[str]:
        """
        从用户消息中提取城市名

        Args:
            message: 用户消息

        Returns:
            Optional[str]: 城市名，如果未找到则返回None
        """
        # 常见城市列表
        cities = [
            "北京", "上海", "广州", "深圳", "杭州", "南京", "苏州", "成都",
            "重庆", "武汉", "西安", "天津", "青岛", "大连", "厦门", "宁波",
            "长沙", "郑州", "济南", "哈尔滨", "沈阳", "福州", "石家庄", "合肥",
            "南昌", "昆明", "贵阳", "兰州", "太原", "乌鲁木齐", "拉萨", "呼和浩特",
            "银川", "西宁", "海口", "三亚", "桂林", "丽江", "大理", "香格里拉"
        ]

        # 在消息中查找城市名
        for city in cities:
            if city in message:
                return city

        return None

    async def _handle_trip_planning(
        self,
        session_id: str,
        user_id: int,
        user_message: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        处理旅行规划请求（集成RAG检索）

        Args:
            session_id: 会话ID
            user_id: 用户ID
            user_message: 用户消息
            context: 会话上下文

        Returns:
            Dict: 响应结果
        """
        try:
            start_time = time.time()

            # 提取城市名
            city = self._extract_city_from_message(user_message)

            # 从RAG检索该城市的旅行攻略
            rag_context = ""
            if city:
                rag_results = await self._search_rag_posts(
                    query=f"{city} 旅行攻略 推荐",
                    city=city,
                    n_results=5,
                    credibility_threshold=0.2
                )
                rag_context = self._format_rag_results_for_context(rag_results)

                await self.dialog_service.log_tool_call(
                    session_id=session_id,
                    tool_name="rag_trip_planning",
                    input_params={"city": city},
                    output_result=f"找到 {len(rag_results)} 条相关攻略",
                    execution_time_ms=(time.time() - start_time) * 1000,
                    status="success"
                )

            # 构建响应消息
            if rag_context:
                response_message = f"""好的，我来帮您规划{city if city else '旅行'}！

根据小红书真实游记，我发现了一些热门推荐：

{rag_context[:500] if len(rag_context) > 500 else rag_context}

请告诉我更多详细信息：
1. 出发日期
2. 旅行天数
3. 您的偏好（如历史文化、自然风光、美食探索等）"""
            else:
                response_message = "好的，我来帮您规划旅行！请告诉我：\n1. 目的地城市\n2. 出发日期\n3. 旅行天数\n4. 您的偏好（如历史文化、自然风光等）"

            return {
                "session_id": session_id,
                "message": response_message,
                "intent": "trip_planning",
                "suggestions": ["北京3日游", "上海2日游", "成都4日游"]
            }

        except Exception as e:
            print(f"[ERROR] 处理旅行规划失败: {str(e)}")
            raise

    async def _handle_info_query(
        self,
        session_id: str,
        user_id: int,
        user_message: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        处理信息查询请求（集成RAG检索）

        Args:
            session_id: 会话ID
            user_id: 用户ID
            user_message: 用户消息
            context: 会话上下文

        Returns:
            Dict: 响应结果
        """
        try:
            # 提取城市名
            city = self._extract_city_from_message(user_message)

            # 判断查询类型
            if "天气" in user_message:
                if not city:
                    return {
                        "session_id": session_id,
                        "message": "请告诉我您想查询哪个城市的天气？",
                        "intent": "info_query",
                        "suggestions": ["北京天气", "上海天气", "南京天气"]
                    }

                start_time = time.time()
                weather_query = f"请查询{city}的天气信息"
                weather_response = await asyncio.to_thread(self.weather_agent.run, weather_query)
                execution_time = (time.time() - start_time) * 1000

                await self.dialog_service.log_tool_call(
                    session_id=session_id,
                    tool_name="weather_query",
                    input_params={"city": city},
                    output_result=weather_response,
                    execution_time_ms=execution_time,
                    status="success"
                )

                response_message = f"为您查询到{city}的天气信息：\n{weather_response}"

            elif any(kw in user_message for kw in ["景点", "门票", "好玩", "介绍", "推荐", "哪里好", "去哪", "参观", "美食", "攻略", "旅行"]):
                # 景点/美食/攻略查询 - 使用RAG增强
                start_time = time.time()

                # 1. 从RAG检索相关帖子
                rag_results = await self._search_rag_posts(
                    query=user_message,
                    city=city,
                    n_results=5,
                    credibility_threshold=0.2
                )

                rag_context = self._format_rag_results_for_context(rag_results)

                execution_time_rag = (time.time() - start_time) * 1000
                await self.dialog_service.log_tool_call(
                    session_id=session_id,
                    tool_name="rag_search",
                    input_params={"query": user_message, "city": city},
                    output_result=f"找到 {len(rag_results)} 条相关帖子",
                    execution_time_ms=execution_time_rag,
                    status="success"
                )

                # 2. 构建增强查询
                if rag_context:
                    enhanced_query = f"""
用户问题：{user_message}
城市：{city if city else "未知"}

【RAG参考信息】（来自小红书真实游记，置信度越高越可信）：
{rag_context}

请根据以上真实游记信息，回答用户的问题。如果信息不足，可以补充常识但要说明。
"""
                    if self.rag_info_agent:
                        response_message = await asyncio.to_thread(
                            self.rag_info_agent.run, enhanced_query
                        )
                    else:
                        response_message = await asyncio.to_thread(
                            self.general_chat_agent.run, enhanced_query
                        )
                else:
                    # 无RAG结果，尝试地图搜索或通用回答
                    if city and any(kw in user_message for kw in ["景点", "好玩", "去哪", "参观"]):
                        attraction_query = f"请搜索{city}的景点：\n[TOOL_CALL:amap_maps_text_search:keywords=景点,city={city}]"
                        attraction_response = await asyncio.to_thread(self.attraction_agent.run, attraction_query)
                        response_message = f"为您查询到{city}的景点信息：\n{attraction_response}"
                    else:
                        response_message = await asyncio.to_thread(
                            self.general_chat_agent.run,
                            f"用户问题：{user_message}\n请详细回答。"
                        )

            else:
                # 其他信息查询，先尝试RAG
                rag_results = await self._search_rag_posts(
                    query=user_message,
                    city=city,
                    n_results=3,
                    credibility_threshold=0.2
                )

                rag_context = self._format_rag_results_for_context(rag_results)

                if rag_context:
                    enhanced_query = f"""
用户问题：{user_message}

【RAG参考信息】：
{rag_context}

请根据以上信息回答用户问题。
"""
                    response_message = await asyncio.to_thread(
                        self.general_chat_agent.run, enhanced_query
                    )
                else:
                    response_message = await asyncio.to_thread(
                        self.general_chat_agent.run,
                        f"用户问题：{user_message}\n请详细回答。"
                    )

            return {
                "session_id": session_id,
                "message": response_message,
                "intent": "info_query",
                "suggestions": ["查询天气", "景点推荐", "美食攻略"]
            }

        except Exception as e:
            print(f"[ERROR] 处理信息查询失败: {str(e)}")
            raise

    async def _handle_plan_modification(
        self,
        session_id: str,
        user_id: int,
        user_message: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        处理计划修改请求

        Args:
            session_id: 会话ID
            user_id: 用户ID
            user_message: 用户消息
            context: 会话上下文

        Returns:
            Dict: 响应结果
        """
        try:
            response_message = "好的，我来帮您修改计划。请告诉我您想修改哪一天的行程？"

            return {
                "session_id": session_id,
                "message": response_message,
                "intent": "plan_modification",
                "suggestions": ["修改第一天", "修改第二天", "修改第三天"]
            }

        except Exception as e:
            print(f"[ERROR] 处理计划修改失败: {str(e)}")
            raise

    async def _handle_general_chat(
        self,
        session_id: str,
        user_id: int,
        user_message: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        处理一般对话（集成RAG检索）

        Args:
            session_id: 会话ID
            user_id: 用户ID
            user_message: 用户消息
            context: 会话上下文

        Returns:
            Dict: 响应结果
        """
        try:
            start_time = time.time()

            # 尝试从消息中提取城市名
            city = self._extract_city_from_message(user_message)

            # 从RAG检索相关内容（如果涉及旅行相关话题）
            rag_context = ""
            travel_keywords = ["旅行", "旅游", "玩", "景点", "美食", "酒店", "攻略", "推荐", "去哪", "行程"]
            if any(kw in user_message for kw in travel_keywords):
                rag_results = await self._search_rag_posts(
                    query=user_message,
                    city=city,
                    n_results=3,
                    credibility_threshold=0.2
                )
                rag_context = self._format_rag_results_for_context(rag_results)

                if rag_results:
                    await self.dialog_service.log_tool_call(
                        session_id=session_id,
                        tool_name="rag_chat_search",
                        input_params={"query": user_message, "city": city},
                        output_result=f"找到 {len(rag_results)} 条相关帖子",
                        execution_time_ms=(time.time() - start_time) * 1000,
                        status="success"
                    )

            # 构建带对话历史的查询
            history = context.get("messages", [])[-6:]  # 最近3轮对话
            history_text = ""
            for msg in history:
                role = "用户" if msg.get("role") == "user" else "助手"
                history_text += f"{role}：{msg.get('content', '')}\n"

            query = f"对话历史：\n{history_text}\n当前用户消息：{user_message}\n"

            if rag_context:
                query += f"\n【RAG参考信息】（来自真实游记）：\n{rag_context}\n\n请结合以上真实游记信息回答用户问题。"

            query += "\n请回答用户的问题。"

            response_message = await asyncio.to_thread(self.general_chat_agent.run, query)

            return {
                "session_id": session_id,
                "message": response_message,
                "intent": "general_chat",
                "suggestions": ["规划旅行", "查询景点", "美食推荐"]
            }

        except Exception as e:
            print(f"[ERROR] 处理一般对话失败: {str(e)}")
            raise

            return {
                "session_id": session_id,
                "message": response_message,
                "intent": "general_chat",
                "suggestions": ["规划旅行", "查询景点", "推荐酒店"]
            }

        except Exception as e:
            print(f"❌ 处理一般对话失败: {str(e)}")
            raise


# 全局对话式系统实例
_conversational_planner = None


def get_conversational_planner(dialog_service) -> ConversationalMultiAgentTripPlanner:
    """
    获取对话式多智能体系统实例

    Args:
        dialog_service: 对话服务实例

    Returns:
        ConversationalMultiAgentTripPlanner: 对话式系统实例
    """
    global _conversational_planner

    if _conversational_planner is None:
        _conversational_planner = ConversationalMultiAgentTripPlanner(dialog_service)

    return _conversational_planner

