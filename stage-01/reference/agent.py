"""第 1 期参考实现：最小 Agent = 模型 + 工具 + 循环"""

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

    for step in range(1, max_steps + 1):
        # 1. 问模型：看完目前的对话，下一步做什么？
        reply = call_model(messages, tool_schemas(tools))
        messages.append(reply)

        # 2. 模型没有请求工具，说明它已经给出最终回答
        if not reply.get("tool_calls"):
            return {"answer": reply.get("content"), "steps": step, "messages": messages}

        # 3. 执行模型请求的每个工具，把结果放回对话
        for call in reply["tool_calls"]:
            result = run_tool(tools, call)
            messages.append(
                {"role": "tool", "tool_call_id": call["id"], "content": result}
            )
        # 4. 回到循环开头，让模型看着工具结果继续

    # 步数用完还没有回答：停下来，不让它无限跑
    return {
        "answer": None,
        "steps": max_steps,
        "messages": messages,
        "stopped": "max_steps",
    }
