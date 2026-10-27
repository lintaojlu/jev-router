# 编程代理的 LLM 供应商统一管理

调研日期：2026-09-30。范围是开源项目：给 Claude Code、Codex 这类编程代理统一管理多家模型供应商。星标来自当日 GitHub API。

| 项目 | 星标 | 管什么 | 适用平台 | 来源 |
| --- | ---: | --- | --- | --- |
| [CC Switch](https://github.com/farion1231/cc-switch) | 138,944 | 桌面里添加并切换供应商，写回各代理配置。非 Anthropic 协议走本机路由，默认 `127.0.0.1:15721` | Windows、macOS、Linux。Tauri。Claude Code、Codex、OpenCode、OpenClaw、Grok | [README](https://github.com/farion1231/cc-switch)、[添加供应商](https://ccswitch.co/docs/providers-add.html) |
| [OmniRoute](https://github.com/diegosouzapw/OmniRoute) | 71,543 | 一个本地端点挂供应商目录、多账户和多层回退。默认 `http://localhost:20128/v1` | `npm i -g omniroute`，另有 Docker。`omniroute run` 可拉起 Claude Code、Codex、Aider、Goose、OpenCode、Qwen Code、Gemini CLI | [README](https://github.com/diegosouzapw/OmniRoute) |
| [Claude Code Router](https://github.com/musistudio/claude-code-router) | 37,486 | 本地网关：供应商预设、凭据池、协议探测、故障转移。网关默认 `127.0.0.1:3456` | 桌面：macOS（Apple Silicon 与 Intel）、Windows、Linux。CLI 需 Node.js 22+，另有 Docker。Claude Code、Codex、OpenCode、Pi、Kimi CLI 等 | [README](https://github.com/musistudio/claude-code-router) |
| [9Router](https://github.com/decolua/9router) | 30,069 | 一个入口后面做 40 多个供应商的账户轮询和自动回退。OmniRoute 从这条线长出来，两边都还在更新 | npm 全局包、Docker、Node。README 还写了 Cloudflare Workers。Claude Code、Codex、Cursor、Cline、Copilot | [README](https://github.com/decolua/9router) |
| [cc-switch-cli](https://github.com/SaladDay/cc-switch-cli) | 5,200 | 终端里管理供应商、MCP 和提示词，也可只为一次启动指定供应商 | Windows、macOS、Linux。Claude Code、Codex、Gemini CLI、OpenCode、Hermes、OpenClaw、Pi | [README](https://github.com/SaladDay/cc-switch-cli) |

许可证都是 MIT。

## 对比

三种做法：

- **改代理自己的配置。** CC Switch、cc-switch-cli。供应商存在本机档案里，启用后写回 Claude Code 或 Codex。协议对不上时才开本地转换。
- **代理固定打到本机网关。** Claude Code Router、9Router、OmniRoute。代理只配置一次本地地址。供应商、账户和回退都在网关里。
- **把订阅登录变成上游。** CLIProxyAPI。用 Claude、Codex、Gemini、Grok、Kimi 的登录态提供兼容接口，再交给上面两类工具。

| 项目 | 主功能 | 解决的问题 | 差异点 | 优势 | 代价 |
| --- | --- | --- | --- | --- | --- |
| CC Switch | 桌面里保存多份供应商，一键启用，并在 Anthropic Messages 与 OpenAI Chat / Responses 之间转换 | 每个代理各有一套配置；Codex 只认 Responses，很多供应商只提供 Chat Completions | 默认改代理配置。本地代理只在协议转换或 Codex OAuth 反代时需要开着 | Windows、macOS、Linux 图形界面。Claude Code 与 Codex 的供应商和模型映射在同一套文档里 | 非原生协议期间本地路由不能停。不做团队共用的远程网关 |
| cc-switch-cli | 终端里管理供应商、MCP 和提示词；可只为这一次启动指定供应商 | 切换要能写进脚本，且不强制改掉全局供应商 | 入口是 TUI 和命令 | `cc-switch start claude <id>` 只影响这一次启动 | 完成度低于桌面版 |
| Claude Code Router | 本地网关：供应商预设、凭据池、条件路由、故障转移、请求日志 | 多个代理共用一套供应商，并看到请求最终打到哪家 | 代理始终面对网关。控制面还管日志、成本和补能力 | 桌面、Node.js 22 CLI、Docker。日志能看到最终供应商和耗时 | 网关要常驻。CLI 需要 Node.js 22+ |
| 9Router | 一个入口接 40 多个供应商，账户轮询，并沿订阅、低价、免费回退 | 单个订阅或密钥打满后工具停住 | README 写了 Cloudflare Workers | npm 或 Docker。Cursor、Cline、Copilot 与 Claude Code、Codex 共用入口 | 与 OmniRoute 功能重叠 |
| OmniRoute | 更大的供应商目录、19 种路由策略、四层回退，并能直接拉起多个 CLI | 工具多、额度碎，希望一个端点按额度往下找 | 9Router 的后续大分支 | 一个地址覆盖的 CLI 最多。回退在网关里完成 | 表面大。免费额度和省 token 比例是项目自己的口径 |
| CLIProxyAPI | 把已登录的编程订阅收成兼容接口，多账户轮询 | 手里是订阅登录，没有按量 API 密钥 | 上游是登录态，下游才是编程代理 | 多把登录可以轮询 | 登录态失效或服务端改校验时会断 |

来源仍是上表中的仓库 README，以及 [CC Switch 添加供应商](https://ccswitch.co/docs/providers-add.html)。

## 把已登录的编程订阅收成一个供应商

[CLIProxyAPI](https://github.com/router-for-me/CLIProxyAPI)（53,603 星，MIT，Go）用 Claude Code、Codex、Gemini、Grok、Kimi 的登录态，对外提供 OpenAI、Claude、Gemini、Codex 兼容接口，并支持多账户轮询。官方建议配桌面客户端 EasyCLIProxyAPI。CC Switch 和其他编程代理再把地址指到这个本地服务。
