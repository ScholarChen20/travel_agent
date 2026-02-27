"""LLM服务模块"""

from hello_agents import HelloAgentsLLM, SimpleAgent

# from ..config import get_settings

# 全局LLM实例
_llm_instance = None


def get_llm() -> HelloAgentsLLM:
    """
    获取LLM实例(单例模式)
    
    Returns:
        HelloAgentsLLM实例
    """
    global _llm_instance
    
    if _llm_instance is None:
        # settings = get_settings()
        
        # 使用阿里云百炼 Qwen 模型（已验证可用）
        _llm_instance = HelloAgentsLLM(
            model='qwen-plus',
            api_key='sk-1c854040b85549a3be779d4e95665176',
            base_url='https://dashscope.aliyuncs.com/compatible-mode/v1',
            provider='qwen'
        )

        # _llm_instance = HelloAgentsLLM(model='Qwen/Qwen2.5-72B-Instruct',
        #                                api_key='ms-7df9fd49-9a59-495d-bf50-f2922001f367',
        #                                base_url='https://api-inference.modelscope.cn/v1/',
        #                                provider='modelscope')

        print(f"✅ LLM服务初始化成功")
        print(f"   提供商: {_llm_instance.provider}")
        print(f"   模型: {_llm_instance.model}")
        print(f"   API Key: {_llm_instance.api_key}")
        print(f"   Base URL: {_llm_instance.base_url}")
    
    return _llm_instance


def reset_llm():
    """重置LLM实例(用于测试或重新配置)"""
    global _llm_instance
    _llm_instance = None


if __name__ == '__main__':
    llm = get_llm()
    intent_agent = SimpleAgent(
        name="意图识别专家",
        llm=llm,
        system_prompt="""你是意图识别专家。分析用户消息并识别意图类型。

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
    )

    response = intent_agent.run("我想去北京玩3天")
    print(response)