# 新增显式技能 swarm-up

> 状态：技能名称与执行节奏语义已由 [ADR-0026](0026-v360-skills-update.md) 修订（重命名为 `try-swarm`，仅决定是否采用多智能体协同而不干预任务执行节奏）。

修订 [ADR-0017](0017-minimal-plugin.md)、[ADR-0019](0019-write-an-article-skill.md) 与 [ADR-0020](0020-matt-flow-skill.md) 中关于插件技能数量的部分。

2026-11-22 决定新增显式技能 `swarm-up`（`name: "letsgo:swarm-up"`，菜单显示 `letsgo: swarm up`），在用户显式调用时，对现场任务按宽松标准与 Token 性价比评估是否适合采用宿主原生的多智能体协同来加快实施。插件技能由 6 个变为 7 个。

- **只允许显式调用**：`disable-model-invocation: true`、`allow_implicit_invocation: false`。调用消息给出需求时评估该需求，未给出时评估当前对话上下文中待实施的任务，空白会话时只问一句待执行的任务。
- **宽松偏积极的评估标准与 Token 性价比底线**：在可采用可不采用的临界情形下优先采用（只要可拆出 ≥2 个无写冲突的并行修改面、“主线实现 + 并行只读调研／测试／审查”或跨模块检索排查，且能明显缩短等待时间即判定为适合）。但当单智能体几步内即可完成、启用多智能体提速不明显却会因派生多份独立上下文消耗过多 Token，或属于单点微改、强顺序耦合写同一批文件时，判定为不适合。
- **宿主原生多智能体映射**：不引入第三方编排框架（如 `ruflo`），直接按宿主调用原生机制——Codex 使用 `multi_agent_v2`（及已配置的自定义角色如 `reviewer`），Claude Code 使用 `Agent Teams`（未开启实验特性或轻量只读并发时使用并行 `Task` 子代理），Antigravity 使用原生 `swarm` 工具（或轻量场景下的并行 `invoke_subagent`）。
- **简洁报告与不中断执行**：先用 1～2 行报告“适合／不适合”及原因与分工，随后不等待二次确认立即执行——适合时直接拉起多智能体并行推进（严格隔离文件写边界），不适合时直接由当前单智能体继续完成该需求。

## Considered Options

- **安装第三方多智能体框架（如 `ruflo`）**：子代理通过外部 HTTP API 直连大模型，无法复用宿主客户端的订阅额度、本地文件沙盒与已挂载 MCP，且数百个 MCP 工具会造成严重的上下文膨胀。
- **放入隐式技能 `letsgo` 自动触发**：每次普通对话都会增加判断负担，且容易在用户不需要并发时误触发多份上下文消耗 Token。
- **评估为“不适合”时仅报告并停下**：违背用户调用技能以加快完成任务的初衷，增加多余的对话轮次。

## Consequences

- 发布为 3.3.0（新增向后兼容功能）。
- `scripts/validate.py` 的 `EXPECTED_SKILLS` 加入 `swarm-up`，同步更新三端 `plugin.json`、`GLOSSARY.md`、`docs/authoring.md`、`AGENTS.md` 与 `README.md`。
