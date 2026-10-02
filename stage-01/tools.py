"""工具：模型自己读不了文件，只能"请求"我们替它读。

每个工具有三部分：给模型看的说明、参数格式、真正执行的函数。
"""

from pathlib import Path

WORKSPACE = (Path(__file__).parent / "workspace").resolve()


def read_file(path):
    full = (WORKSPACE / path).resolve()
    if WORKSPACE not in full.parents:
        raise ValueError("只能读取 workspace 目录里的文件")
    return full.read_text(encoding="utf-8")[:2000]


TOOLS = {
    "read_file": {
        "description": "读取 workspace 目录下的一个文本文件，返回文件内容",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "文件名，例如 notes.txt"},
            },
            "required": ["path"],
        },
        "run": read_file,
    },
}
