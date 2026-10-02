# 故障分析题：它为什么一直读同一个文件？

同事写了 `agent_broken.py`，接上真实模型后提问"notes.txt 里写了什么？"，
运行记录如下：

```
第 1 步  模型请求工具 read_file {"path": "notes.txt"}
第 2 步  模型请求工具 read_file {"path": "notes.txt"}
第 3 步  模型请求工具 read_file {"path": "notes.txt"}
第 4 步  模型请求工具 read_file {"path": "notes.txt"}
第 5 步  模型请求工具 read_file {"path": "notes.txt"}

没有回答，stopped = max_steps
```

工具本身没问题，单独调用 `read_file` 能正常读出内容。
（有些模型服务在这种情况下会直接报 400 错误，原因是同一个。）

## 请回答

1. bug 在哪一行？
2. 模型为什么每一步都做同样的事？它"看到"的对话里缺了什么？
3. 怎么改？改 `agent_broken.py`，然后用 `python test_agent.py broken` 验证。

想清楚再看 `ANSWER.md`。
