# Jev 截图下一步

给定一条已经确定的任务和一张屏幕截图，在本机做 OCR，再请 [Jev](https://docs.typesafe.ai/sdk/python/) 判断下一步该做什么。程序只输出建议和标注图，不移动鼠标，也不敲键盘。

Jev 不接收图片。截图里的像素和精确坐标留在本机；送出的状态只有任务说明、元素编号、文字和粗位置（例如「上部偏左」）。用法说明见 [docs/jev-research.md](docs/jev-research.md)。

## 调研文档

| 文档 | 内容 |
| --- | --- |
| [docs/llm-routing-survey.md](docs/llm-routing-survey.md) | 总览：按内容选模型、Jev 路由、编程代理供应商管理、五项能力对照 |
| [docs/model-routing-oss.md](docs/model-routing-oss.md) | 按内容难易选模型的开源清单 |
| [docs/coding-agent-providers.md](docs/coding-agent-providers.md) | Claude Code / Codex 等供应商统一管理与对比 |
| [docs/jev-research.md](docs/jev-research.md) | Jev API / SDK 与本 demo 的对应关系 |

## 准备

需要 macOS（Vision OCR）、Python 3.10+ 和 [uv](https://docs.astral.sh/uv/)。

```bash
uv sync
export TYPESAFE_API_KEY=...   # https://console.typesafe.ai/keys
```

变量名见 [.env.example](.env.example)。可选 `JEV_MODEL`，默认 `jev-latest`。

## 运行

```bash
uv run jev-next --task "打开系统设置里的显示器" --image examples/settings-display.png
uv run jev-next --task "打开系统设置里的显示器" --image ./shot.png
uv run jev-next --task "打开系统设置里的显示器" --capture
```

`--capture` 用 `screencapture -x` 把当前屏幕存下来再判断，仍然不会点击。需要屏幕录制权限。

没有密钥时，程序完成本机 OCR、写出将要发送的请求体后退出，退出码为 2，不会编造模型结果。

## 输出

每次运行在 `runs/<时间>/`：

| 文件 | 内容 |
| --- | --- |
| `elements.json` | OCR 元素、本机归一化框、粗位置。框的坐标系是 Vision 的左下角原点。 |
| `request_state.json` | 实际送给 Jev 的 state 和三个问题。state 里没有像素坐标。 |
| `decision.json` | 动作、目标、置信度、完成概率，以及中文建议。 |
| `annotated.png` | 全部文字框；被选中的目标用更粗的框标出。 |

`decision.json` 里：

- `operation.choice`：`click`、`type_text`、`scroll`、`wait`、`done`、`blocked`
- `target.choice`：元素 id（`e1` 起）或 `none`
- `goal_complete.noul`：可见画面证明任务已完成的概率
- `uncertain`：应用侧门槛认为不宜执行。动作或所需目标的置信度低于 0.4，或者动作是 `done` 但完成概率低于 0.6

`type_text` 只表示下一步应该输入，不生成要输入的文字。没有文字的图标按钮不会进入候选。元素超过 254 个时按 OCR 置信度截断，给 `none` 留出 Choice 的第 255 个选项。
