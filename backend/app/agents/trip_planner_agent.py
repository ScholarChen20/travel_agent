""""""

import json
import os
import time
import asyncio
import re
from typing import Dict, Any, List, Optional

from hello_agents import SimpleAgent, ReActAgent
from hello_agents.tools import MCPTool
from ..services.llm_service import get_llm
from ..models.schemas import TripRequest, TripPlan, DayPlan, Attraction, Meal, WeatherInfo, Location, Hotel
from ..config import get_settings
from ..services.rag import HybridRAGService, RAGSearchResult, get_hybrid_rag_service

# ============ Agent ============

ATTRACTION_AGENT_PROMPT = """

**:**
!!

**:**
maps_text_search,:
`[TOOL_CALL:amap_maps_text_search:keywords=,city=]`

**:**
: ""
: [TOOL_CALL:amap_maps_text_search:keywords=,city=]

: ""
: [TOOL_CALL:amap_maps_text_search:keywords=,city=]

**:**
1. ,
2. ,
3. 
"""

WEATHER_AGENT_PROMPT = """

**:**
!!

**:**
maps_weather,:
`[TOOL_CALL:amap_maps_weather:city=]`

**:**
: ""
: [TOOL_CALL:amap_maps_weather:city=]

: ""
: [TOOL_CALL:amap_maps_weather:city=]

**:**
1. ,
2. ,
"""

HOTEL_AGENT_PROMPT = """

**:**
!!

**:**
maps_text_search,:
`[TOOL_CALL:amap_maps_text_search:keywords=,city=]`

**:**
: ""
: [TOOL_CALL:amap_maps_text_search:keywords=,city=]

**:**
1. ,
2. ,
3. """"
"""

PLANNER_AGENT_PROMPT = """,

JSON:
```json
{
  "city": "",
  "start_date": "YYYY-MM-DD",
  "end_date": "YYYY-MM-DD",
  "days": [
    {
      "date": "YYYY-MM-DD",
      "day_index": 0,
      "description": "1",
      "transportation": "",
      "accommodation": "",
      "hotel": {
        "name": "",
        "address": "",
        "location": {"longitude": 116.397128, "latitude": 39.916527},
        "price_range": "300-500",
        "rating": "4.5",
        "distance": "2",
        "type": "",
        "estimated_cost": 400
      },
      "attractions": [
        {
          "name": "",
          "address": "",
          "location": {"longitude": 116.397128, "latitude": 39.916527},
          "visit_duration": 120,
          "description": "",
          "category": "",
          "ticket_price": 60
        }
      ],
      "meals": [
        {"type": "breakfast", "name": "", "description": "", "estimated_cost": 30},
        {"type": "lunch", "name": "", "description": "", "estimated_cost": 50},
        {"type": "dinner", "name": "", "description": "", "estimated_cost": 80}
      ]
    }
  ],
  "weather_info": [
    {
      "date": "YYYY-MM-DD",
      "day_weather": "",
      "night_weather": "",
      "day_temp": 25,
      "night_temp": 15,
      "wind_direction": "",
      "wind_power": "1-3"
    }
  ],
  "overall_suggestions": "",
  "budget": {
    "total_attractions": 180,
    "total_hotels": 1200,
    "total_meals": 480,
    "total_transportation": 200,
    "total": 2060
  }
}
```

**:**
1. weather_info
2. (°C)
3. 2-3
4. 
5. 
6. 
7. ****:
   - (ticket_price)
   - (estimated_cost)
   - (estimated_cost)
   - (budget)
"""


class MultiAgentTripPlanner:
    """"""

    def __init__(self):
        """"""
        print("[INFO] ...")

        try:
            settings = get_settings()
            self.llm = get_llm()

            # RAG
            self._rag_service: Optional[HybridRAGService] = None

            # MCP()
            print("  - MCP...")
            self.amap_tool = MCPTool(
                name="amap",
                description="",
                server_command=["uvx", "amap-mcp-server"],
                env={"AMAP_MAPS_API_KEY": os.getenv("AMAP_MAPS_API_KEY")},
                auto_expand=True
            )

            # Agent
            print("  - Agent...")
            self.attraction_agent = ReActAgent(
                name="",
                llm=self.llm,
                system_prompt=ATTRACTION_AGENT_PROMPT,
            )
            self.attraction_agent.add_tool(self.amap_tool)

            # Agent
            print("  - Agent...")
            self.weather_agent = SimpleAgent(
                name="",
                llm=self.llm,
                system_prompt=WEATHER_AGENT_PROMPT
            )
            self.weather_agent.add_tool(self.amap_tool)

            # Agent
            print("  - Agent...")
            self.hotel_agent = SimpleAgent(
                name="",
                llm=self.llm,
                system_prompt=HOTEL_AGENT_PROMPT
            )
            self.hotel_agent.add_tool(self.amap_tool)

            # Agent()
            print("  - Agent...")
            self.planner_agent = SimpleAgent(
                name="",
                llm=self.llm,
                system_prompt=PLANNER_AGENT_PROMPT
            )

            print("[OK] ")
            print(f"   Agent: {len(self.attraction_agent.list_tools())} ")
            print(f"   Agent: {len(self.weather_agent.list_tools())} ")
            print(f"   Agent: {len(self.hotel_agent.list_tools())} ")

        except Exception as e:
            print(f"[ERROR] : {str(e)}")
            import traceback
            traceback.print_exc()
            raise

    async def _get_rag_service(self) -> Optional[HybridRAGService]:
        """RAG"""
        if self._rag_service is None:
            try:
                self._rag_service = await get_hybrid_rag_service()
                print("[OK] RAG")
            except Exception as e:
                print(f"[WARN] RAG: {str(e)}")
                return None
        return self._rag_service

    def _remove_emoji(self, text: str) -> str:
        """emoji"""
        emoji_pattern = re.compile(
            "["
            "\U0001F600-\U0001F64F"  # emoticons
            "\U0001F300-\U0001F5FF"  # symbols & pictographs
            "\U0001F680-\U0001F6FF"  # transport & map symbols
            "\U0001F1E0-\U0001F1FF"  # flags
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
        RAG

        Args:
            query: 
            city: 
            n_results: 
            credibility_threshold: 

        Returns:
            
        """
        try:
            rag_service = await self._get_rag_service()
            if rag_service is None:
                return []

            # 
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
            print(f"[WARN] RAG: {str(e)}")
            return []

    def _format_rag_results_for_context(self, results: List[RAGSearchResult]) -> str:
        """
        RAG

        Args:
            results: RAG

        Returns:
            
        """
        if not results:
            return ""

        context_parts = []
        for i, result in enumerate(results, 1):
            # emoji
            title = self._remove_emoji(result.title)
            content = self._remove_emoji(result.content)

            # 
            if len(content) > 500:
                content = content[:500] + "..."

            context_parts.append(f"""
{i}(: {result.credibility:.2f})
: {title}
: {', '.join(result.tags[:5])}
: {content}
""")

        return "\n".join(context_parts)

    async def _get_rag_context(self, city: str, preferences: List[str] = None) -> str:
        """
        RAG

        Args:
            city: 
            preferences: 

        Returns:
            RAG
        """
        try:
            # 
            query_parts = [city]
            if preferences:
                query_parts.extend(preferences[:3])  # 3

            query = " ".join(query_parts)

            # 
            results = await self._search_rag_posts(
                query=query,
                city=city,
                n_results=8,
                credibility_threshold=0.2
            )

            if not results:
                print(f"[WARN] RAG {city} ")
                return ""

            # 
            context = self._format_rag_results_for_context(results)
            print(f"[OK] RAG {len(results)} ")

            return context

        except Exception as e:
            print(f"[WARN] RAG: {str(e)}")
            return ""
    
    async def plan_trip(self, request: TripRequest) -> TripPlan:
        """
        

        Args:
            request: 

        Returns:
            
        """
        try:
            print(f"\n{'='*60}")
            print(f"[START] ...")
            print(f": {request.city}")
            print(f": {request.start_date}  {request.end_date}")
            print(f": {request.travel_days}")
            print(f": {', '.join(request.preferences) if request.preferences else ''}")
            print(f"{'='*60}\n")

            # 0: RAG
            print("[STEP0] RAG...")
            rag_context = await self._get_rag_context(request.city, request.preferences)
            if rag_context:
                print(f"RAG: {len(rag_context)}")
            else:
                print("RAG")

            # 1: Agent
            print("[STEP1] ...")
            attraction_query = self._build_attraction_query(request)
            attraction_response = await asyncio.to_thread(self.attraction_agent.run, attraction_query)
            print(f": {attraction_response[:200]}...\n")

            # 2: Agent
            print("[STEP2] ...")
            weather_query = f"{request.city}"
            weather_response = await asyncio.to_thread(self.weather_agent.run, weather_query)
            print(f": {weather_response[:200]}...\n")

            # 3: Agent
            print("[STEP3] ...")
            hotel_query = f"{request.city}{request.accommodation}"
            hotel_response = await asyncio.to_thread(self.hotel_agent.run, hotel_query)
            print(f": {hotel_response[:200]}...\n")

            # 4: Agent
            print("[STEP4] ...")
            planner_query = self._build_planner_query(request, attraction_response, weather_response, hotel_response, rag_context)
            planner_response = await asyncio.to_thread(self.planner_agent.run, planner_query)
            print(f": {planner_response[:300]}...\n")

            # 
            trip_plan = self._parse_response(planner_response, request)

            print(f"{'='*60}")
            print(f"[OK] !")
            print(f"{'='*60}\n")

            return trip_plan

        except Exception as e:
            print(f"[ERROR] : {str(e)}")
            import traceback
            traceback.print_exc()
            return self._create_fallback_plan(request)
    
    def _build_attraction_query(self, request: TripRequest) -> str:
        """ - """
        keywords = []
        if request.preferences:
            # 
            keywords = request.preferences[0]
        else:
            keywords = ""

        # 
        query = f"amap_maps_text_search{request.city}{keywords}\n[TOOL_CALL:amap_maps_text_search:keywords={keywords},city={request.city}]"
        return query

    def _build_planner_query(self, request: TripRequest, attractions: str, weather: str, hotels: str = "", rag_context: str = "") -> str:
        """"""
        query = f"""{request.city}{request.travel_days}:

**:**
- : {request.city}
- : {request.start_date}  {request.end_date}
- : {request.travel_days}
- : {request.transportation}
- : {request.accommodation}
- : {', '.join(request.preferences) if request.preferences else ''}

**:**
{attractions}

**:**
{weather}

**:**
{hotels}
"""
        if rag_context:
            query += f"""
**RAG:**
{rag_context}

**RAG:**
1. RAG
2. RAG
3. RAG
4. RAG
"""

        query += """
**:**
1. 2-3
2. 
3. ()
4. 
5. JSON
6. 
"""
        if request.free_text_input:
            query += f"\n**:** {request.free_text_input}"

        return query
    
    def _parse_response(self, response: str, request: TripRequest) -> TripPlan:
        """
        Agent
        
        Args:
            response: Agent
            request: 
            
        Returns:
            
        """
        try:
            # JSON
            # JSON
            if "```json" in response:
                json_start = response.find("```json") + 7
                json_end = response.find("```", json_start)
                json_str = response[json_start:json_end].strip()
            elif "```" in response:
                json_start = response.find("```") + 3
                json_end = response.find("```", json_start)
                json_str = response[json_start:json_end].strip()
            elif "{" in response and "}" in response:
                # JSON
                json_start = response.find("{")
                json_end = response.rfind("}") + 1
                json_str = response[json_start:json_end]
            else:
                raise ValueError("JSON")
            
            # JSON
            data = json.loads(json_str)
            
            # TripPlan
            trip_plan = TripPlan(**data)
            
            return trip_plan
            
        except Exception as e:
            print(f"[WARN] : {str(e)}")
            print(f"   ")
            return self._create_fallback_plan(request)
    
    def _create_fallback_plan(self, request: TripRequest) -> TripPlan:
        """(Agent)"""
        from datetime import datetime, timedelta
        
        # 
        start_date = datetime.strptime(request.start_date, "%Y-%m-%d")
        
        # 
        days = []
        for i in range(request.travel_days):
            current_date = start_date + timedelta(days=i)
            
            day_plan = DayPlan(
                date=current_date.strftime("%Y-%m-%d"),
                day_index=i,
                description=f"{i+1}",
                transportation=request.transportation,
                accommodation=request.accommodation,
                attractions=[
                    Attraction(
                        name=f"{request.city}{j+1}",
                        address=f"{request.city}",
                        location=Location(longitude=116.4 + i*0.01 + j*0.005, latitude=39.9 + i*0.01 + j*0.005),
                        visit_duration=120,
                        description=f"{request.city}",
                        category=""
                    )
                    for j in range(2)
                ],
                meals=[
                    Meal(type="breakfast", name=f"{i+1}", description=""),
                    Meal(type="lunch", name=f"{i+1}", description=""),
                    Meal(type="dinner", name=f"{i+1}", description="")
                ]
            )
            days.append(day_plan)
        
        return TripPlan(
            city=request.city,
            start_date=request.start_date,
            end_date=request.end_date,
            days=days,
            weather_info=[],
            overall_suggestions=f"{request.city}{request.travel_days},"
        )


# 
_multi_agent_planner = None


def get_trip_planner_agent() -> MultiAgentTripPlanner:
    """()"""
    global _multi_agent_planner

    if _multi_agent_planner is None:
        _multi_agent_planner = MultiAgentTripPlanner()

    return _multi_agent_planner


# ============  ============

INTENT_DETECTION_PROMPT = """

**:**
1. trip_planning - 
2. info_query - ///
3. plan_modification - 
4. general_chat - 

**:**
: "3" -> trip_planning
: "" -> info_query
: "" -> info_query
: "" -> info_query
: "" -> info_query
: "" -> plan_modification
: "" -> general_chat

,"""


GENERAL_CHAT_PROMPT = """
1. 
2. 
3. 
4. 

****
RAG
1. 
2. 
3. 
4. 

"""


RAG_ENHANCED_INFO_PROMPT = """RAG

****
1. RAG
2. 
3. RAG""
4. 
5. """


class ConversationalMultiAgentTripPlanner(MultiAgentTripPlanner):
    """"""

    def __init__(self, dialog_service):
        """
        

        Args:
            dialog_service: 
        """
        super().__init__()
        self.dialog_service = dialog_service

        # Agent
        self.intent_agent = SimpleAgent(
            name="",
            llm=self.llm,
            system_prompt=INTENT_DETECTION_PROMPT
        )

        # RAGAgent
        try:
            self.rag_info_agent = SimpleAgent(
                name="RAG",
                llm=self.llm,
                system_prompt=RAG_ENHANCED_INFO_PROMPT
            )
            print("[OK] RAGAgent")
        except Exception as e:
            print(f"[WARN] RAGAgent: {str(e)}")
            self.rag_info_agent = None

        # Agent
        try:
            self.general_chat_agent = ReActAgent(
                name="",
                llm=self.llm,
                system_prompt=GENERAL_CHAT_PROMPT
            )
            print("[OK] ")
        except Exception as e:
            print(f"[ERROR] Agent: {str(e)}")
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
        

        Args:
            session_id: ID
            user_id: ID
            user_message: 

        Returns:
            Dict: 
        """
        try:
            # 1. 
            await self.dialog_service.add_message(
                session_id=session_id,
                role="user",
                content=user_message
            )

            # 2. 
            context = await self.dialog_service.get_session_context(session_id)

            # 3. 
            intent = await self._detect_intent(user_message, context)


            # 4. 
            if intent == "trip_planning":
                response = await self._handle_trip_planning(session_id, user_id, user_message, context)
            elif intent == "info_query":
                response = await self._handle_info_query(session_id, user_id, user_message, context)
            elif intent == "plan_modification":
                response = await self._handle_plan_modification(session_id, user_id, user_message, context)
            else:
                response = await self._handle_general_chat(session_id, user_id, user_message, context)

            # 5. 
            await self.dialog_service.add_message(
                session_id=session_id,
                role="assistant",
                content=response["message"],
                metadata={"intent": intent}
            )

            return response

        except Exception as e:
            print(f"[ERROR] : {str(e)}")
            import traceback
            traceback.print_exc()
            raise

    async def _detect_intent(self, user_message: str, context: Dict[str, Any]) -> str:
        """
        

        Args:
            user_message: 
            context: 

        Returns:
            str: 
        """
        try:
            # 
            query = f": {user_message}"

            #  to_thread 
            start_time = time.time()
            intent_response = await asyncio.to_thread(self.intent_agent.run, query)
            execution_time = (time.time() - start_time) * 1000

            # 
            await self.dialog_service.log_tool_call(
                session_id=context["session_id"],
                tool_name="intent_detection",
                input_params={"message": user_message},
                output_result=intent_response,
                execution_time_ms=execution_time,
                status="success"
            )

            # 
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
            print(f"[WARN] : {str(e)}")
            return "general_chat"

    def _extract_city_from_message(self, message: str) -> Optional[str]:
        """
        

        Args:
            message: 

        Returns:
            Optional[str]: None
        """
        # 
        cities = [
            "", "", "", "", "", "", "", "",
            "", "", "", "", "", "", "", "",
            "", "", "", "", "", "", "", "",
            "", "", "", "", "", "", "", "",
            "", "", "", "", "", "", "", ""
        ]

        # 
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
        RAG

        Args:
            session_id: ID
            user_id: ID
            user_message: 
            context: 

        Returns:
            Dict: 
        """
        try:
            start_time = time.time()

            # 
            city = self._extract_city_from_message(user_message)

            # RAG
            rag_context = ""
            if city:
                rag_results = await self._search_rag_posts(
                    query=f"{city}  ",
                    city=city,
                    n_results=5,
                    credibility_threshold=0.2
                )
                rag_context = self._format_rag_results_for_context(rag_results)

                await self.dialog_service.log_tool_call(
                    session_id=session_id,
                    tool_name="rag_trip_planning",
                    input_params={"city": city},
                    output_result=f" {len(rag_results)} ",
                    execution_time_ms=(time.time() - start_time) * 1000,
                    status="success"
                )

            # 
            if rag_context:
                response_message = f"""{city if city else ''}



{rag_context[:500] if len(rag_context) > 500 else rag_context}


1. 
2. 
3. """
            else:
                response_message = "\n1. \n2. \n3. \n4. "

            return {
                "session_id": session_id,
                "message": response_message,
                "intent": "trip_planning",
                "suggestions": ["3", "2", "4"]
            }

        except Exception as e:
            print(f"[ERROR] : {str(e)}")
            raise

    async def _handle_info_query(
        self,
        session_id: str,
        user_id: int,
        user_message: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        RAG

        Args:
            session_id: ID
            user_id: ID
            user_message: 
            context: 

        Returns:
            Dict: 
        """
        try:
            # 
            city = self._extract_city_from_message(user_message)

            # 
            if "" in user_message:
                if not city:
                    return {
                        "session_id": session_id,
                        "message": "",
                        "intent": "info_query",
                        "suggestions": ["", "", ""]
                    }

                start_time = time.time()
                weather_query = f"{city}"
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

                response_message = f"{city}\n{weather_response}"

            elif any(kw in user_message for kw in ["", "", "", "", "", "", "", "", "", "", ""]):
                # // - RAG
                start_time = time.time()

                # 1. RAG
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
                    output_result=f" {len(rag_results)} ",
                    execution_time_ms=execution_time_rag,
                    status="success"
                )

                # 2. 
                if rag_context:
                    # RAGRAGAgent
                    enhanced_query = f"""
{user_message}
{city if city else ""}

RAG
{rag_context}


"""
                    if self.rag_info_agent:
                        response_message = await asyncio.to_thread(
                            self.rag_info_agent.run, enhanced_query
                        )
                    else:
                        response_message = await asyncio.to_thread(
                            self.general_chat_agent.run, enhanced_query
                        )

                    execution_time_llm = (time.time() - start_time) * 1000
                    await self.dialog_service.log_tool_call(
                        session_id=session_id,
                        tool_name="rag_enhanced_llm",
                        input_params={"query": user_message},
                        output_result=response_message[:200],
                        execution_time_ms=execution_time_llm,
                        status="success"
                    )
                else:
                    # RAG
                    if city and any(kw in user_message for kw in ["", "", "", ""]):
                        attraction_query = f"{city}\n[TOOL_CALL:amap_maps_text_search:keywords=,city={city}]"
                        attraction_response = await asyncio.to_thread(self.attraction_agent.run, attraction_query)
                        response_message = f"{city}\n{attraction_response}"
                    else:
                        response_message = await asyncio.to_thread(
                            self.general_chat_agent.run,
                            f"{user_message}\n"
                        )

            else:
                # RAG
                rag_results = await self._search_rag_posts(
                    query=user_message,
                    city=city,
                    n_results=3,
                    credibility_threshold=0.2
                )

                rag_context = self._format_rag_results_for_context(rag_results)

                if rag_context:
                    enhanced_query = f"""
{user_message}

RAG
{rag_context}


"""
                    response_message = await asyncio.to_thread(
                        self.general_chat_agent.run, enhanced_query
                    )
                else:
                    response_message = await asyncio.to_thread(
                        self.general_chat_agent.run,
                        f"{user_message}\n"
                    )

            return {
                "session_id": session_id,
                "message": response_message,
                "intent": "info_query",
                "suggestions": ["", "", ""]
            }

        except Exception as e:
            print(f"[ERROR] : {str(e)}")
            raise

    async def _handle_plan_modification(
        self,
        session_id: str,
        user_id: int,
        user_message: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        

        Args:
            session_id: ID
            user_id: ID
            user_message: 
            context: 

        Returns:
            Dict: 
        """
        try:
            response_message = ""

            return {
                "session_id": session_id,
                "message": response_message,
                "intent": "plan_modification",
                "suggestions": ["", "", ""]
            }

        except Exception as e:
            print(f"[ERROR] : {str(e)}")
            raise

    async def _handle_general_chat(
        self,
        session_id: str,
        user_id: int,
        user_message: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        RAG

        Args:
            session_id: ID
            user_id: ID
            user_message: 
            context: 

        Returns:
            Dict: 
        """
        try:
            start_time = time.time()

            # 
            city = self._extract_city_from_message(user_message)

            # RAG
            rag_context = ""
            travel_keywords = ["", "", "", "", "", "", "", "", "", ""]
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
                        output_result=f" {len(rag_results)} ",
                        execution_time_ms=(time.time() - start_time) * 1000,
                        status="success"
                    )

            # 
            history = context.get("messages", [])[-6:]  # 3
            history_text = ""
            for msg in history:
                role = "" if msg.get("role") == "user" else ""
                history_text += f"{role}{msg.get('content', '')}\n"

            query = f"\n{history_text}\n{user_message}\n"

            if rag_context:
                query += f"\nRAG\n{rag_context}\n\n"

            query += "\n"

            response_message = await asyncio.to_thread(self.general_chat_agent.run, query)

            execution_time = (time.time() - start_time) * 1000
            await self.dialog_service.log_tool_call(
                session_id=session_id,
                tool_name="general_chat_llm",
                input_params={"message": user_message, "has_rag": bool(rag_context)},
                output_result=response_message[:200],
                execution_time_ms=execution_time,
                status="success"
            )

            return {
                "session_id": session_id,
                "message": response_message,
                "intent": "general_chat",
                "suggestions": ["", "", ""]
            }

        except Exception as e:
            print(f"[ERROR] : {str(e)}")
            raise


# 
_conversational_planner = None


def get_conversational_planner(dialog_service) -> ConversationalMultiAgentTripPlanner:
    """
    

    Args:
        dialog_service: 

    Returns:
        ConversationalMultiAgentTripPlanner: 
    """
    global _conversational_planner

    if _conversational_planner is None:
        _conversational_planner = ConversationalMultiAgentTripPlanner(dialog_service)

    return _conversational_planner

