"""第 1 期练习：补全 run_agent 里的循环

做完在 stage-01 目录下运行：python test_agent.py
"""

import json

SYSTEM_PROMPT = "你是一个文件助手。需要了解文件内容时，调用 read_file 工具，不要猜。"


def tool_schemas(tools):
    """把我们的工具表转成模型接口要求的格式。"""
    return [
        {
            "type": "function",
            "function": {
                "name": name,
                "description": tool["description"],
                "parameters": tool["parameters"],
            },
        }
        for name, tool in tools.items()
    ]


def run_tool(tools, call):
    """执行模型请求的一次工具调用，永远返回字符串。

    出错时不抛异常，而是把错误写成文字还给模型，让它自己决定怎么办。
    """
    name = call["function"]["name"]
    tool = tools.get(name)
    if tool is None:
        return f"错误：没有名为 {name} 的工具"
    try:
        args = json.loads(call["function"].get("arguments") or "{}")
        return str(tool["run"](**args))
    except Exception as err:
        return f"错误：{err}"


def run_agent(call_model, tools, user_message, max_steps=5):
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_message},
    ]

    # TODO：写一个最多执行 max_steps 次的循环，每一轮做四件事：
    #
    # 1. 调用 call_model(messages, tool_schemas(tools)) 得到 reply，
    #    并把 reply 追加到 messages 里
    #
    # 2. 如果 reply 里没有 tool_calls（不存在或为空），
    #    返回 {"answer": reply.get("content"), "steps": 当前是第几轮, "messages": messages}
    #
    # 3. 否则，对 reply["tool_calls"] 里的每一个 call：
    #    用 run_tool(tools, call) 得到结果，
    #    再往 messages 追加
    #    {"role": "tool", "tool_call_id": call["id"], "content": 结果}
    #
    # 4. 循环结束还没有回答时，返回
    #    {"answer": None, "steps": max_steps, "messages": messages, "stopped": "max_steps"}

    raise NotImplementedError("TODO：还没有实现 run_agent 的循环")
