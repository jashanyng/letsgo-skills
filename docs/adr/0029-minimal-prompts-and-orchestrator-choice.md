# 极简提示词、多工单编排择优与触发标签

修订 [ADR-0020](0020-matt-flow-skill.md)、[ADR-0026](0026-0.0.8-skills-update.md) 与 [ADR-0028](0028-guide-skill-and-rules-update.md) 中关于新会话提示词前缀与长度、多工单实施拆会话规则、`try-swarm` 与其他编排器的边界，以及 `guide` 提示词与触发方式展示的部分；插件技能总数保持 10 个，计划发布为 `0.0.13`。

2026-11-26 决定对 `letsgo` 插件做以下四项调整：

- **抽出单点共用规则 `plugins/letsgo/skills/letsgo/references/orchestration.md`**：供 `letsgo:matt-flow` 与 `letsgo:try-swarm` 共同引用（同步纳入 `scripts/validate.py` 路由校验）。
- **多工单实施三档择优（替代机械拆开多会话）**：严禁建议同时手动开启多个互不通信的顶层会话去跑带阻塞依赖的任务链；进入多工单实施前现场按“单仓库标准任务图 → 1 个会话 `/implement-spec`；跨多仓库／含人工中途门禁／需协调板 → 1 个宿主原生多智能体协调会话（由薄协调者按依赖拓扑派发 worker 逐单跑 `/implement`）；独立小单或强需逐单深度把关 → 拆分为逐单独立新会话”三档择优。
- **极简上下文指针与脱离 `matt-flow` 前缀**：门禁与新会话代码块提示词只保留最小上下文指针（通常 1 行），不抄写工单、spec、handoff 或仓库 `AGENTS.md` 中已有信息，依赖顺序与门禁提醒置于代码块外极简注明；明确进入单一实施形态的新会话（`/implement`、`/implement-spec` 或按当前宿主生成的原生多智能体一行指令）直接以原生指令开头、不再前置 `letsgo:matt-flow`，以便用户快速掌握后脱离插件手写。仅当新会话仍需自动串联多个设了 `disable-model-invocation: true` 的 matt 技能时，才以 `letsgo:matt-flow` 开头。
- **`try-swarm` 编排器互斥择优选一**：宿主原生多智能体与同类多代理／任务图编排器（如 `implement-spec`、`run_workflow` 等）绝不叠加启用；检测到重叠时按 `orchestration.md` 准则现场择优选一，在报告末尾附一句避坑提示`（两者同属编排器，下次择一即可）`并按所选结果直接衔接（选原生机制替代对方时禁止 worker 套娃调用原编排器；选对方编排器且用户已指名时直接按当前节奏推进，仅受显式限制无法直跑时给 1 行原生代码块）。
- **`guide` 6 类触发标签与停下必给极简接力代码块**：实读元数据后在过程说明行标注精确触发标签（`可隐式`、`仅显式`、`仅隐式`、`内部路由`、`MCP 直调`、`内置工具`）；任何停下等待用户确认、授权或接力的节点（含方案确认停下且后续为可隐式技能的场景）均须输出包裹在代码块中的极简接力提示词；不停下直接推进时不插播示范代码块；全部任务收尾时输出简洁、略宽松的复盘总结与独立复用参考提示词代码块。同步修正 [GLOSSARY.md](../../GLOSSARY.md) 中“隐式调用”的插件内限定范围并补充“内部路由”词条。

## Considered Options

- **继续建议一次手动开启多个带依赖的顶层会话并依赖用户逐个接力**：顶层会话间无原生唤醒通知机制，强行同时开启只会互等空耗或大幅增加用户人工协调负担；改为单个薄协调会话派发隔离上下文 worker（或单仓 `/implement-spec`）可在用户只开 1 个会话的前提下自动按依赖拓扑推进。
- **保留 `/letsgo:matt-flow` 前缀并把完整工作目录／完成标志抄进新会话代码块**：虽能让新会话自动继承 `matt-flow` 规则，但提示词过长、信息与工单/`AGENTS.md` 重复，且不利于用户熟悉后脱离插件独立手写原生极简命令。
- **在 `guide` 每次直接推进的中间也同步输出示范代码块**：容易与“需立即复制发送的接力代码块”混淆导致误发；改为过程停下节点必给当前可发送的极简接力代码块、收尾复盘再集中给出脱离 `guide` 的简洁说明与参考代码块，兼顾现场操作清晰度与迁移学习。

## Consequences

- `letsgo` 插件保持 10 个技能不变，计划校验通过后发布为 `0.0.13` 并同步更新本机三端客户端。
- 更新 `scripts/validate.py`（新增 `TRY_SWARM_ROUTES` 并在 `MATT_ROUTES` 增加 `../letsgo/references/orchestration.md` 校验）及单元测试 `scripts/tests/test_plugin_validation.py`。
- 同步修订 `GLOSSARY.md`、`docs/compatibility.md`、`docs/authoring.md`、`README.md` 与 `CHANGELOG.md`，并在被修订的 ADR-0020、ADR-0026、ADR-0028 顶部补充状态说明。
