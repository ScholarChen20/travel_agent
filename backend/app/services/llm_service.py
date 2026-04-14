"""LLM服务模块"""

import os

from hello_agents import HelloAgentsLLM, SimpleAgent

# from ..config import get_settings

# LLM单例实例
_llm_instance = None


def get_llm() -> HelloAgentsLLM:
    """
    获取LLM实例（单例模式）
    
    Returns:
        HelloAgentsLLM
    """
    global _llm_instance
    
    if _llm_instance is None:
        # settings = get_settings()
        
        # Qwen模型配置
        _llm_instance = HelloAgentsLLM(
            model='qwen-plus',
            api_key=os.getenv('DASHSCOPE_API_KEY'),
            base_url='https://dashscope.aliyuncs.com/compatible-mode/v1',
            provider='qwen',
            timeout=300  # 设置超时时间为300秒（5分钟），用于复杂任务如旅行计划生成
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
        print(f"   Timeout: {_llm_instance.timeout}秒")
    
    return _llm_instance


def reset_llm():
    """重置LLM实例"""
    global _llm_instance
    _llm_instance = None


if __name__ == '__main__':
    llm = get_llm()
    intent_agent = SimpleAgent(
        name="",
        llm=llm,
        system_prompt="""

**意图分类：**
1. trip_planning - 旅行规划
2. info_query - 信息查询
3. plan_modification - 计划修改
4. general_chat - 日常对话

**示例：**
: "我想去北京玩3天" -> trip_planning
: "故宫什么时候开门" -> info_query
: "天气怎么样" -> info_query
: "把第二天的行程改一下" -> plan_modification
: "你好" -> general_chat

请根据用户输入判断意图并返回对应的分类。
"""
    )

    response = intent_agent.run("3")
    print(response)