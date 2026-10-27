# LLM 模型路由与编程代理供应商管理调研

调研日期：2026-09-30。星标来自当日 GitHub API。平台只记录各仓库 README、安装文档或 Release 资产写明的运行面。

本仓库另有：

- [jev-research.md](jev-research.md)：Jev 用法与本仓库只读 demo 的对应关系
- [model-routing-oss.md](model-routing-oss.md)：按内容难易选模型的开源清单
- [coding-agent-providers.md](coding-agent-providers.md)：编程代理供应商管理与对比

本文把后两份结论收成一份总览，并补上五项能力对照。

## 1. 结论摘要

| 目标 | 结论 |
| --- | --- |
| 按内容难易选模型（简单 → 便宜，难 → 强） | 热门开源：LiteLLM Auto Router、vLLM Semantic Router、RouteLLM、Aurelio Semantic Router |
| 用 Jev 做这次选择 | 热门项目里只有 LiteLLM 的 `classifier_type: jev`；另有一批接编码代理的小仓库 |
| 官方演示对应的可运行项目 | [prismhq/jev-router](https://github.com/prismhq/jev-router)：LiteLLM 上的 Jev 钩子，客户端只写 `jev-router` |
| 编程代理统一管供应商 | CC Switch（改配置）、Claude Code Router / 9Router / OmniRoute（本机网关）、CLIProxyAPI（订阅登录变接口） |
| 五项都要：统一供应商 + GUI + 按内容选路由 + Jev + 统计花费 | **只有 LiteLLM** 全部满足 |

按内容切模型，请求必须经过能改写模型名的本机进程。「改代理配置」类工具（如 CC Switch）换的是整段会话供应商，不会按单条内容判断。

## 2. 按内容难易选模型

### 2.1 热门开源

| 项目 | 星标 | 怎么按内容选 | 适用平台 |
| --- | ---: | --- | --- |
| [LiteLLM Auto Router](https://github.com/BerriAI/litellm) | 59,900 | `complexity_router` 分成 SIMPLE / MEDIUM / COMPLEX / REASONING，再调用该档模型。默认识别器是本地启发式；可换成小模型或 Jev | Python 代理：`uv`、Docker、Terraform。客户端走 OpenAI 兼容接口 |
| [vLLM Semantic Router](https://github.com/vllm-project/semantic-router) | 5,982 | 抽取难度、意图、安全等信号，按规则选模型路径 | Linux、macOS 或 WSL2；Python 3.10+；Docker / Podman |
| [RouteLLM](https://github.com/lm-sys/RouteLLM) | 5,558 | 强模型与弱模型二选一。最近推送 2024-08-10 | Python 包或本地 OpenAI 兼容服务 |
| [Semantic Router](https://github.com/aurelio-labs/semantic-router) | 3,932 | 例句相似度命中命名路线，路线再对应模型 | Python 包；本地编码器需 `semantic-router[local]` |

### 2.2 用 Jev 做这次选择

Jev 只返回档位。真正调用 gpt-5-mini 或 claude-opus 的是调用方。

热门入口：[LiteLLM `classifier_type: jev`](https://docs.litellm.ai/docs/auto_router/setup)。代理把问题发给 TypeSafe `POST /v1/systemone`，用 Choice 选档，再调用该档模型。密钥是代理进程的 `TYPESAFE_API_KEY`。文档示例：SIMPLE → `gpt-5.6-luna`，REASONING → `claude-opus-5`。

官方演示页 [Model routing](https://jevtypesafeai.com/decide/use-cases/model-routing) 对应的可运行仓库是 [prismhq/jev-router](https://github.com/prismhq/jev-router)（约 15 星）：基于 LiteLLM 的 OpenAI 兼容代理，客户端只发 `model: "jev-router"`。

独立仓库（按星标）：

| 项目 | 星标 | 接到的产品 | 适用平台 | Jev 选完之后 |
| --- | ---: | --- | --- | --- |
| [gargpratyush/jev-router](https://github.com/gargpratyush/jev-router) | 495 | Claude Code、Codex | Node.js 20.12+；Windows、macOS、Linux | 本机回环代理改写当次请求的模型名并转发；同轮工具循环不再问 Jev |
| [nidhi-singh02/agent-router](https://github.com/nidhi-singh02/agent-router) | 99 | Cursor、Claude Code、Codex、OpenCode | Node.js 20+；需 Herdr 窗格 | **没有网关**；拼启动命令拉起代理，选择只作用于新开的这一次 |
| [dirien/jev-router](https://github.com/dirien/jev-router) | 6 | Claude Code、Codex CLI | Node.js 22+；macOS launchd / Linux systemd | 本机代理按档改写模型。npm 包名 `@ediri/jev-router` |
| [Akramovic1/jev-pilot](https://github.com/Akramovic1/jev-pilot) | 6 | Claude Code 插件 | Claude Code 2.1.278+，function hooks | 主对话保持强模型；Jev 选子代理档位和推理力度 |
| [maharshi365/oc-agent-router](https://github.com/maharshi365/oc-agent-router) | 4 | OpenCode 新 subagent | 随 OpenCode 进程 | 创建子会话前改 `provider/model` |
| [himanshu231204/jev_model_routers](https://github.com/himanshu231204/jev_model_routers) | 2 | Claude Code | Python 3.11 / 3.12 | 本机代理按轮次选 Haiku / Sonnet / Opus |
| [Mandrilsquad1441/jev-model-router](https://github.com/Mandrilsquad1441/jev-model-router) | 2 | Claude Code、Claude Desktop、Codex | TypeScript 插件 | 选模型和推理力度 |
| [Akashdb5/jev-router](https://github.com/Akashdb5/jev-router) | 0 | OpenAI / Anthropic / OpenRouter SDK | Python 3.10+ | 应用内：简单走 economy，其余走 frontier |

注意：不带 scope 的 npm 包名 `jev-router` 属于 gargpratyush；dirien 的是 `@ediri/jev-router`。PyPI `jev-model-router` 属于 himanshu，与 Mandrilsquad1441 同名插件不是同一项目。

#### gargpratyush/jev-router：选完之后会怎样

会自动改掉**这一次**发出去的请求。这里的「网关」是 `jev-claude` / `jev-codex` 临时拉起的本机回环代理，不会写进 LiteLLM 或其他网关。

1. Claude Code / Codex 把模型设成 `jev-router`，请求打到本机代理。
2. 代理把本轮用户原文、当前档位和大约上下文长度发给 Jev。
3. 本机策略可覆盖结果（提示词里写 `use opus`、低置信度不降级等）。
4. 代理把 `jev-router` 改成该档具体模型 ID，再转发到 Anthropic / OpenAI；响应原样流回。
5. 同轮工具循环复用钉住的模型；在 `/model` 改选具体模型后停止路由，直到再选回 Jev Router。

#### nidhi-singh02/agent-router：选完之后会怎样

不会改写在途请求。`router run` 在启动前决定代理、模型和推理力度，再让 Herdr 新开窗格并送入任务。没有 TypeSafe 密钥时直接失败，没有降级路径。

## 3. 编程代理的供应商统一管理

### 3.1 三种做法

| 做法 | 项目 | 请求怎么走 |
| --- | --- | --- |
| 改代理自己的配置 | CC Switch、cc-switch-cli | 供应商存在本机档案；启用后写回 Claude Code / Codex。协议对不上才开本地转换 |
| 代理固定打到本机网关 | Claude Code Router、9Router、OmniRoute | 代理只配置一次本地地址；供应商、账户、回退都在网关里 |
| 把订阅登录变成上游 | CLIProxyAPI | 用 Claude / Codex / Gemini / Grok / Kimi 登录态提供兼容接口，再交给上面两类 |

按内容切模型需要第二种（或同类「请求经本机改写」）。第一种换的是会话级供应商，不看单条内容。

### 3.2 项目清单

| 项目 | 星标 | 管什么 | 适用平台 |
| --- | ---: | --- | --- |
| [CC Switch](https://github.com/farion1231/cc-switch) | 138,944 | 桌面添加/切换供应商，写回各代理配置。默认路由 `127.0.0.1:15721` | Windows、macOS、Linux（Tauri） |
| [OmniRoute](https://github.com/diegosouzapw/OmniRoute) | 71,543 | 本地端点 + 供应商目录 + 多层回退。默认 `localhost:20128/v1` | npm / Docker；可拉起 Claude Code、Codex 等 |
| [CLIProxyAPI](https://github.com/router-for-me/CLIProxyAPI) | 53,603 | 订阅登录 → OpenAI / Claude / Gemini / Codex 兼容接口 | Go；常配桌面客户端 |
| [Claude Code Router](https://github.com/musistudio/claude-code-router) | 37,486 | 供应商、凭据池、条件路由、故障转移、日志。默认 `127.0.0.1:3456` | 桌面 + Node.js 22+ CLI + Docker |
| [9Router](https://github.com/decolua/9router) | 30,069 | 40+ 供应商账户轮询；订阅 → 低价 → 免费回退 | npm / Docker / Node；也可 Workers |
| [cc-switch-cli](https://github.com/SaladDay/cc-switch-cli) | 5,200 | 终端版供应商 / MCP / 提示词管理 | Windows、macOS、Linux |

### 3.3 对比

| 项目 | 主功能 | 解决的问题 | 优势 | 代价 |
| --- | --- | --- | --- | --- |
| CC Switch | 图形切换供应商与协议转换 | 每个代理各一套配置；Codex 只认 Responses | 三端桌面；Claude / Codex 文档一体 | 本地路由要常开；不做远程团队网关 |
| cc-switch-cli | TUI / CLI 切换 | 要写进脚本且不改全局 | 可只影响单次启动 | 完成度低于桌面版 |
| Claude Code Router | 常驻网关 + 控制面 | 多代理共用供应商并看日志 | 桌面 / CLI / Docker；有费用估算 | 网关常驻；CLI 需 Node 22+ |
| 9Router | 额度用尽后自动降级 | 单订阅打满后工具停住 | 多工具共用入口 | 与 OmniRoute 重叠 |
| OmniRoute | 更大目录与更多策略 | 工具多、额度碎 | 覆盖 CLI 最多 | 口径偏项目自述；排错看回退层 |
| CLIProxyAPI | 登录态变接口 | 没有按量 API Key | 多账户轮询 | 登录失效会断 |

## 4. 五项能力对照

需求：① 统一管理不同 provider ② 有 GUI ③ 可根据内容选路由 ④ 使用了 Jev ⑤ 可统计模型花费。

星标取自 2026-09-30 前后核对值；「部分」见表下说明。

| 项目 | Star | URL | 中文简介 | ① 统一供应商 | ② GUI | ③ 按内容选路由 | ④ 使用 Jev | ⑤ 统计花费 |
| --- | ---: | --- | --- | --- | --- | --- | --- | --- |
| LiteLLM | 59,912 | https://github.com/BerriAI/litellm | 自建代理。Auto Router 按难易分档；界面可选 Jev；记录各模型花费与相对「始终用最强」的节省 | 是 | 是 | 是 | 是 | 是 |
| OmniRoute | 71,560 | https://github.com/diegosouzapw/OmniRoute | 本地入口 + 控制台。可按任务类型/规模改模型；判断是本地规则，不调用 Jev | 是 | 是 | 是 | 否 | 是 |
| Claude Code Router | 37,487 | https://github.com/musistudio/claude-code-router | 编程代理本地网关。供应商与日志一体；路由是条件规则，不是难易分类 | 是 | 是 | 部分 | 否 | 是 |
| New API | 49,134 | https://github.com/QuantumNous/new-api | 聚合分发与密钥管理网站。按渠道计费，不看请求内容 | 是 | 是 | 否 | 否 | 是 |
| 9Router | 30,070 | https://github.com/decolua/9router | 编程工具共用入口；按额度回退；控制台有用量估算 | 是 | 是 | 否 | 否 | 是 |
| Bifrost | 8,463 | https://github.com/maximhq/bifrost | Go 网关 + 网页。故障转移与用量预算，不按内容选模型 | 是 | 是 | 否 | 否 | 是 |
| vLLM Semantic Router | 5,984 | https://github.com/vllm-project/semantic-router | 信号驱动选路径；有控制台；不用 Jev，也无按模型账单 | 是 | 是 | 是 | 否 | 否 |
| prismhq/jev-router | 15 | https://github.com/prismhq/jev-router | LiteLLM 钩子：客户端只写一个模型名，Jev 按内容选。仓库无自带界面 | 是 | 否 | 是 | 是 | 部分 |
| gargpratyush/jev-router | 498 | https://github.com/gargpratyush/jev-router | Claude Code / Codex 本机代理；每轮问 Jev 选快/强档。无多供应商管理、无 GUI、无花费汇总 | 否 | 否 | 是 | 是 | 否 |

说明：

- Claude Code Router「部分」：可按请求头/正文写规则（例如出现某词就换模型），没有「简单走便宜、难走强」的分类器。
- prismhq/jev-router「部分」花费：下游生成由 LiteLLM 记账；问 Jev 那次直连 TypeSafe，不进同一本账。
- LiteLLM：内置 Jev 分档可在开源代理使用；自定义判断说明文档标为企业版能力。

## 5. 怎么选（实用）

| 场景 | 建议 |
| --- | --- |
| 本机图形里换供应商 | CC Switch |
| 切换要写进脚本 | cc-switch-cli |
| 多代理共用一个本地地址，并要看日志 | Claude Code Router |
| 额度常打满、工具多 | OmniRoute（或 9Router） |
| 手里是订阅登录、没有按量 Key | 先 CLIProxyAPI，再交给上面工具 |
| 要按内容难易选模型，且要 GUI + 花费 + Jev | LiteLLM Auto Router（`classifier_type: jev`） |
| 只要 Claude Code / Codex 按轮次用 Jev 选档 | gargpratyush/jev-router |
| 要对照官方演示自己搭 LiteLLM 钩子 | prismhq/jev-router |

## 6. 来源

- 各仓库 README 与 GitHub API 星标（2026-09-30）
- [LiteLLM Auto Router / JEV classifier](https://docs.litellm.ai/docs/auto_router/setup)
- [Jev Model routing 演示](https://jevtypesafeai.com/decide/use-cases/model-routing)
- [CC Switch 添加供应商](https://ccswitch.co/docs/providers-add.html)
- [Intent and model routing（System One）](https://systemonemodels.org/use-cases/workflow-control/intent-and-model-routing/)
