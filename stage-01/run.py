"""接上真实模型跑一次。

    python run.py "notes.txt 里写了什么？"                    用参考实现
    python run.py "notes.txt 里写了什么？" --agent practice   用你写的版本
"""

import argparse

from model import call_model
from test_agent import TARGETS, load_run_agent
from tools import TOOLS

parser = argparse.ArgumentParser()
parser.add_argument("question", nargs="?", default="notes.txt 里写了什么？")
parser.add_argument("--agent", choices=list(TARGETS), default="reference")
args = parser.parse_args()

run_agent = load_run_agent(args.agent)
result = run_agent(call_model, TOOLS, args.question)

# 打印执行轨迹：模型每一步做了什么
step = 0
for m in result["messages"]:
    if m["role"] == "assistant":
        step += 1
        if m.get("tool_calls"):
            for c in m["tool_calls"]:
                f = c["function"]
                print(f"第 {step} 步  模型请求工具 {f['name']} {f['arguments']}")
        else:
            print(f"第 {step} 步  模型回答")
    elif m["role"] == "tool":
        preview = m["content"][:60].replace("\n", " ")
        print(f"        工具返回 {preview}")

print()
print(result["answer"] or f"没有回答，stopped = {result.get('stopped')}")
