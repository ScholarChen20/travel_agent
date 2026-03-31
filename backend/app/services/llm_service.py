"""LLM"""
import os

from hello_agents import HelloAgentsLLM, SimpleAgent

# from ..config import get_settings

# LLM
_llm_instance = None


def get_llm() -> HelloAgentsLLM:
    """
    LLM()
    
    Returns:
        HelloAgentsLLM
    """
    global _llm_instance
    
    if _llm_instance is None:
        # settings = get_settings()
        
        #  Qwen 
        _llm_instance = HelloAgentsLLM(
            model='qwen-plus',
            api_key=os.getenv('DASHSCOPE_API_KEY'),
            base_url='https://dashscope.aliyuncs.com/compatible-mode/v1',
            provider='qwen'
        )

        # _llm_instance = HelloAgentsLLM(model='Qwen/Qwen2.5-72B-Instruct',
        #                                api_key='ms-7df9fd49-9a59-495d-bf50-f2922001f367',
        #                                base_url='https://api-inference.modelscope.cn/v1/',
        #                                provider='modelscope')

        print(f" LLM")
        print(f"   : {_llm_instance.provider}")
        print(f"   : {_llm_instance.model}")
        print(f"   API Key: {_llm_instance.api_key}")
        print(f"   Base URL: {_llm_instance.base_url}")
    
    return _llm_instance


def reset_llm():
    """LLM()"""
    global _llm_instance
    _llm_instance = None


if __name__ == '__main__':
    llm = get_llm()
    intent_agent = SimpleAgent(
        name="",
        llm=llm,
        system_prompt="""

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
    )

    response = intent_agent.run("3")
    print(response)