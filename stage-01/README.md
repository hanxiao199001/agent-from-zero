# 第 1 期：写出你的第一个 Agent

目标：跑通一个最小 Agent，看清三样东西：**模型、工具、执行循环**。

## 文件

| 文件 | 作用 |
| --- | --- |
| `model.py` | 调用模型接口（已写好） |
| `tools.py` | 一个工具：`read_file`（已写好） |
| `practice/agent.py` | **你要补全的文件**：执行循环 |
| `test_agent.py` | 5 个测试，用假模型，不需要 API Key |
| `debug/` | 一份写坏的 Agent 和一道故障分析题 |
| `reference/agent.py` | 参考答案，做完再看 |

## 步骤

下面的 `python` 在 macOS / Linux 上可能要写成 `python3`。

**1. 补全 `practice/agent.py` 里的 TODO，然后跑测试**

```bash
python test_agent.py
```

**2. 全部通过后，接上真实模型跑一次**

先设置三个环境变量（OpenAI 兼容格式，具体值以你用的模型服务商文档为准）：

```bash
# macOS / Linux
export LLM_BASE_URL=你的模型服务地址
export LLM_API_KEY=你的密钥
export LLM_MODEL=模型名
```

```powershell
# Windows PowerShell
$env:LLM_BASE_URL="你的模型服务地址"
$env:LLM_API_KEY="你的密钥"
$env:LLM_MODEL="模型名"
```

```bash
python run.py "notes.txt 里写了什么？" --agent practice
```

**3. 做故障分析题**

先读 `debug/QUESTION.md`，想清楚再看 `debug/ANSWER.md`。

## 过关标准

- `python test_agent.py` 5 个测试全部通过
- 能用自己的话回答：模型为什么需要看到工具结果才能继续？
