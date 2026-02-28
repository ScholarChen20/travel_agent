from hello_agents.protocols import A2AServer
from hello_agents.protocols.a2a.implementation import A2AClient, A2A_AVAILABLE

def create_calculator_agent():
    if not A2A_AVAILABLE:
        return None

    print("🧮 创建计算器智能体")

    calculator = A2AServer(
        name="Calculator",
        description="A calculator that can perform basic arithmetic operations.",
        version = "1.0.0",
        capabilities={
            "math": ["add", "subtract", "multiply", "divide"],
            "advanced": ["sqrt", "square", "cube"],
        }

    )

    # 添加基础计算技能
    @calculator.skill("add")
    def add_numbers(query: str) -> str:
        """加法计算"""
        try:
            # 简单解析 "计算 5 + 3" 格式
            parts = query.replace("计算", "").replace("加", "+").replace("加上", "+")
            if "+" in parts:
                numbers = [float(x.strip()) for x in parts.split("+")]
                result = sum(numbers)
                return f"计算结果: {' + '.join(map(str, numbers))} = {result}"
            else:
                return "请使用格式: 计算 5 + 3"
        except Exception as e:
            return f"计算错误: {e}"

    @calculator.skill("multiply")
    def multiply_numbers(query: str) -> str:
        """乘法计算"""
        try:
            parts = query.replace("计算", "").replace("乘以", "*").replace("×", "*")
            if "*" in parts:
                numbers = [float(x.strip()) for x in parts.split("*")]
                result = 1
                for num in numbers:
                    result *= num
                return f"计算结果: {' × '.join(map(str, numbers))} = {result}"
            else:
                return "请使用格式: 计算 5 * 3"
        except Exception as e:
            return f"计算错误: {e}"



    @calculator.skill("info")
    def get_info(query: str) -> str:
        """获取智能体信息"""
        return f"我是 {calculator.name}，可以进行基础数学计算。支持的技能: {list(calculator.skills.keys())}"

    print(f"✅ 计算器智能体创建成功，支持技能: {list(calculator.skills.keys())}")
    return calculator


cal_agent = create_calculator_agent()
if cal_agent:
    # 测试技能
    print("\n 测试智能体技能")
    test_queries = [
        "获取信息",
        "计算 10 + 10002",
        "计算 521 * 523",
    ]

    for query in test_queries:
        if "信息" in query:
            result = cal_agent.skills['info'](query)
        elif "+" in query:
            result = cal_agent.skills['add'](query)
        elif "*" in query:
            result = cal_agent.skills['multiply'](query)
        else:
            print(f"  {query}: {cal_agent.run(query)}")
            result = "未知查询类型"

        print(f"查询： {query}")
        print(f"结果： {result}")

