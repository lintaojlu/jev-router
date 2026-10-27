# 按内容难易选模型

调研日期：2026-09-30。范围只包括：看请求内容的难易，简单的走便宜模型，难的走强模型。故障转移、密钥分发、按渠道负载均衡不在这份记录里。星标来自当日 GitHub API。

## 热门开源

| 项目 | 星标 | 怎么按内容选 | 适用平台 | 来源 |
| --- | ---: | --- | --- | --- |
| [LiteLLM Auto Router](https://github.com/BerriAI/litellm) | 59,900 | `auto_router/complexity_router` 把请求分成 SIMPLE / MEDIUM / COMPLEX / REASONING，再调用该档配置的模型。默认识别器是本地启发式打分；可换成小模型或 Jev | LiteLLM 代理：`uv tool install 'litellm[proxy]'`、Docker、Terraform。客户端走 OpenAI 兼容接口 | [Auto Router](https://docs.litellm.ai/docs/auto_router/)、[安装与 Jev 分类器](https://docs.litellm.ai/docs/auto_router/setup) |
| [vLLM Semantic Router](https://github.com/vllm-project/semantic-router) | 5,982 | 从请求抽取难度、意图、安全等信号，按规则选择模型路径 | Linux、macOS 或 WSL2；Python 3.10+；Docker，Linux 可用 Podman | [安装文档](https://vllm-sr.ai/docs/installation/)、[仓库](https://github.com/vllm-project/semantic-router) |
| [RouteLLM](https://github.com/lm-sys/RouteLLM) | 5,558 | 强模型与弱模型二选一。简单查询走弱模型。最近推送 2024-08-10 | Python 包。可替换 OpenAI Python 客户端，或 `python -m routellm.openai_server` | [README](https://github.com/lm-sys/RouteLLM) |
| [Semantic Router](https://github.com/aurelio-labs/semantic-router) | 3,932 | 用例句相似度命中命名路线，路线再对应不同模型。难易由你提供的例句定义 | Python 包。本地编码器：`semantic-router[local]` | [README](https://github.com/aurelio-labs/semantic-router) |

## 用 Jev 做这次选择

Jev 返回档位。发往具体生成模型的是调用方。

热门项目里的入口是 LiteLLM：`classifier_type: jev`。代理把分类输入作为 `state` 发给 `POST /v1/systemone`，用一个 `questions.tier` Choice 选档，再调用该档模型。密钥是代理进程里的 `TYPESAFE_API_KEY`。`TYPESAFE_API_BASE` 默认 `https://api.typesafe.ai`。未写 `classifier_fallback` 时，Jev 失败会回退到启发式打分。文档示例档位是 SIMPLE → `gpt-5.6-luna`，REASONING → `claude-opus-5`。出处：[Admin Setup · JEV classifier](https://docs.litellm.ai/docs/auto_router/setup)。

`dirien/jev-router` 的 npm 包名是 `@ediri/jev-router`。不带 scope 的 `jev-router` 属于 gargpratyush 的仓库。PyPI 上的 `jev-model-router` 属于 himanshu 的仓库，和 Mandrilsquad1441 的同名插件不是同一个项目。

| 项目 | 星标 | 选完之后接到 | 适用平台 | 来源 |
| --- | ---: | --- | --- | --- |
| [LiteLLM `classifier_type: jev`](https://docs.litellm.ai/docs/auto_router/setup) | 59,900 | 代理上已配置的任意模型档 | 与 LiteLLM 代理相同 | [setup](https://docs.litellm.ai/docs/auto_router/setup) |
| [gargpratyush/jev-router](https://github.com/gargpratyush/jev-router) | 495 | Claude Code、OpenAI Codex。简单走快档，难走强档 | Node.js 20.12+。Windows、macOS、Linux | [README](https://github.com/gargpratyush/jev-router) |
| [nidhi-singh02/agent-router](https://github.com/nidhi-singh02/agent-router) | 99 | 按任务在 Cursor、Claude Code、Codex、OpenCode 中选代理、模型和推理力度 | Node.js 20+。配置目录覆盖 macOS、Linux、Windows。拉起需要 Herdr | [README](https://github.com/nidhi-singh02/agent-router) |
| [dirien/jev-router](https://github.com/dirien/jev-router) | 6 | Claude Code 与 Codex CLI 的 fast / balanced / frontier | Node.js 22+。macOS launchd、Linux systemd；其余用 `jev-router launch` | [README](https://github.com/dirien/jev-router) |
| [Akramovic1/jev-pilot](https://github.com/Akramovic1/jev-pilot) | 6 | 主对话保持当前强模型。Jev 选择子代理模型档和主对话推理力度 | Claude Code 2.1.278+，`CLAUDE_CODE_ENABLE_FUNCTION_HOOKS=1`。Jev 走 OpenRouter 或 TypeSafe | [仓库说明](https://github.com/Akramovic1/jev-pilot) |
| [maharshi365/oc-agent-router](https://github.com/maharshi365/oc-agent-router) | 4 | OpenCode 新 subagent 的 `provider/model` | 随 OpenCode 进程。`TYPESAFE_API_KEY` 只从进程环境读取 | [README](https://github.com/maharshi365/oc-agent-router) |
| [himanshu231204/jev_model_routers](https://github.com/himanshu231204/jev_model_routers) | 2 | Claude Code 的 Haiku / Sonnet / Opus。Codex 启动器为实验功能 | Python 3.11 或 3.12，另有 GHCR 镜像 | [README](https://github.com/himanshu231204/jev_model_routers)、[PyPI](https://pypi.org/project/jev-model-router/) |
| [Mandrilsquad1441/jev-model-router](https://github.com/Mandrilsquad1441/jev-model-router) | 2 | Claude Code、Claude Desktop、Codex 的模型和推理力度 | TypeScript 插件。Jev 走 OpenRouter 或 TypeSafe | [仓库](https://github.com/Mandrilsquad1441/jev-model-router) |
| [Akashdb5/jev-router](https://github.com/Akashdb5/jev-router) | 0 | 应用内：简单请求走 economy，其余走 frontier。供应商为 OpenAI、Anthropic、OpenRouter | Python 3.10+。当前只做同步文本 | [README](https://github.com/Akashdb5/jev-router) |
