# 答案

## 1. bug 在哪

```python
def add_tool_result(messages, call, result):
    messages = messages + [
        {"role": "tool", "tool_call_id": call["id"], "content": result}
    ]
```

`messages + [...]` 会生成一个**新列表**，然后只是把函数内部的 `messages`
这个名字指向了新列表。函数一结束，新列表就被丢掉了。
`run_agent` 里的那个 `messages` 从头到尾没有变过，工具结果从来没进过对话。

## 2. 模型为什么重复

模型没有记忆，每一步它只能看到我们发过去的 `messages`。
在它看来，对话是这样的：

- 用户问：notes.txt 里写了什么？
- 我请求了读文件
- （没有任何结果）

既然没看到结果，最合理的做法就是再请求一次。它没有"卡住"，
是我们没把结果给它。

## 3. 怎么改

用 `append` 直接修改原来的列表：

```python
def add_tool_result(messages, call, result):
    messages.append(
        {"role": "tool", "tool_call_id": call["id"], "content": result}
    )
```

## 这道题想让你记住的

- Agent 的全部"记忆"就是 `messages`。结果没放进去，就等于没发生。
- 看到 Agent 重复同一个动作，先查：上一步的结果有没有回到对话里。
- `max_steps` 在这里救了场：没有它，这个 bug 会一直烧钱跑下去。
