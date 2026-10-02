"""模型：把对话和工具清单发给模型，拿回它的回复。

用的是 OpenAI 兼容的 chat/completions 格式，多数模型服务都支持。
只用标准库，不需要安装任何包。
"""

import json
import os
import urllib.error
import urllib.request


def call_model(messages, tools):
    base_url = os.environ.get("LLM_BASE_URL")
    api_key = os.environ.get("LLM_API_KEY")
    model = os.environ.get("LLM_MODEL")
    if not (base_url and api_key and model):
        raise RuntimeError("请先设置环境变量 LLM_BASE_URL、LLM_API_KEY、LLM_MODEL")

    body = json.dumps({"model": model, "messages": messages, "tools": tools})
    request = urllib.request.Request(
        base_url.rstrip("/") + "/chat/completions",
        data=body.encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer " + api_key,
        },
    )

    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            data = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as err:
        detail = err.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"模型接口返回 {err.code}: {detail}") from None

    # 回复长这样：{"role": "assistant", "content": "...", "tool_calls": [...]}
    return data["choices"][0]["message"]
