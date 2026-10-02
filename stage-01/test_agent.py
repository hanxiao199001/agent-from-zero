"""测试用"假模型"：按剧本返回回复，不联网、不花钱。

    python test_agent.py              测你写的 practice/agent.py
    python test_agent.py reference    测参考实现
    python test_agent.py broken       测故障代码
"""

import copy
import importlib.util
import json
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).parent
TARGETS = {
    "practice": HERE / "practice" / "agent.py",
    "reference": HERE / "reference" / "agent.py",
    "broken": HERE / "debug" / "agent_broken.py",
}


def load_run_agent(target):
    spec = importlib.util.spec_from_file_location("agent_under_test", TARGETS[target])
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.run_agent


run_agent = None  # 在文件末尾按命令行参数加载


class FakeModel:
    """依次返回 script 里的回复，用完后重复最后一条。

    seen 记录每次调用时模型"看到"的对话快照。
    """

    def __init__(self, script):
        self.script = script
        self.seen = []

    def __call__(self, messages, tools):
        self.seen.append(copy.deepcopy(messages))
        index = min(len(self.seen) - 1, len(self.script) - 1)
        return copy.deepcopy(self.script[index])


def fake_tools():
    calls = []

    def read_file(path):
        calls.append({"path": path})
        if path == "missing.txt":
            raise FileNotFoundError("文件不存在")
        return "hello"

    tools = {
        "read_file": {
            "description": "读文件",
            "parameters": {"type": "object", "properties": {"path": {"type": "string"}}},
            "run": read_file,
        }
    }
    return tools, calls


def ask_tool(name, args, call_id="call_1"):
    return {
        "role": "assistant",
        "content": None,
        "tool_calls": [
            {
                "id": call_id,
                "type": "function",
                "function": {"name": name, "arguments": json.dumps(args)},
            }
        ],
    }


def say(content):
    return {"role": "assistant", "content": content}


def first_index(messages, condition):
    for i, m in enumerate(messages):
        if condition(m):
            return i
    return -1


class AgentTest(unittest.TestCase):
    def test_1_direct_answer(self):
        """1. 模型直接回答时：一步结束，不调用工具"""
        model = FakeModel([say("你好")])
        tools, calls = fake_tools()
        result = run_agent(model, tools, "你好")

        self.assertEqual(result["answer"], "你好")
        self.assertEqual(result["steps"], 1)
        self.assertEqual(len(model.seen), 1)
        self.assertEqual(calls, [])

    def test_2_tool_result_goes_back(self):
        """2. 模型请求工具时：执行工具，并把结果放回对话"""
        model = FakeModel(
            [ask_tool("read_file", {"path": "notes.txt"}), say("文件里写的是 hello")]
        )
        tools, calls = fake_tools()
        result = run_agent(model, tools, "读一下 notes.txt")

        self.assertEqual(calls, [{"path": "notes.txt"}], "工具应该被调用一次，参数正确")
        self.assertEqual(len(model.seen), 2, "模型应该被调用两次")

        second = model.seen[1]
        request_at = first_index(
            second, lambda m: m["role"] == "assistant" and m.get("tool_calls")
        )
        result_at = first_index(second, lambda m: m["role"] == "tool")
        self.assertNotEqual(request_at, -1, "第二次调用时，对话里应该有模型上一轮的工具请求")
        self.assertNotEqual(result_at, -1, "第二次调用时，对话里应该有工具结果")
        self.assertGreater(result_at, request_at, "工具结果应该排在工具请求之后")
        self.assertEqual(second[result_at]["tool_call_id"], "call_1")
        self.assertEqual(second[result_at]["content"], "hello")

        self.assertEqual(result["answer"], "文件里写的是 hello")
        self.assertEqual(result["steps"], 2)

    def test_3_stops_at_max_steps(self):
        """3. 模型一直请求工具时：到最大步数就停"""
        model = FakeModel([ask_tool("read_file", {"path": "notes.txt"})])
        tools, _ = fake_tools()
        result = run_agent(model, tools, "读", max_steps=3)

        self.assertEqual(len(model.seen), 3, "模型最多被调用 max_steps 次")
        self.assertIsNone(result["answer"])
        self.assertEqual(result.get("stopped"), "max_steps")

    def test_4_unknown_tool(self):
        """4. 模型请求了不存在的工具：不崩溃，把错误告诉模型"""
        model = FakeModel([ask_tool("delete_file", {}), say("我没有这个工具")])
        tools, _ = fake_tools()
        result = run_agent(model, tools, "删文件")

        tool_messages = [m for m in model.seen[1] if m["role"] == "tool"]
        self.assertTrue(tool_messages, "对话里应该有一条工具结果")
        self.assertIn("错误", tool_messages[0]["content"])
        self.assertEqual(result["answer"], "我没有这个工具")

    def test_5_tool_raises(self):
        """5. 工具执行出错：不崩溃，把错误告诉模型"""
        model = FakeModel(
            [ask_tool("read_file", {"path": "missing.txt"}), say("文件不存在")]
        )
        tools, _ = fake_tools()
        result = run_agent(model, tools, "读 missing.txt")

        tool_messages = [m for m in model.seen[1] if m["role"] == "tool"]
        self.assertTrue(tool_messages, "对话里应该有一条工具结果")
        self.assertIn("文件不存在", tool_messages[0]["content"])
        self.assertEqual(result["answer"], "文件不存在")


if __name__ == "__main__":
    target = "practice"
    if len(sys.argv) > 1 and sys.argv[1] in TARGETS:
        target = sys.argv.pop(1)
    print(f"正在测试：{TARGETS[target].relative_to(HERE)}\n")
    run_agent = load_run_agent(target)
    unittest.main(verbosity=2)
