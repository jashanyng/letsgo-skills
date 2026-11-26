# 变更日志（Changelog）

本文件记录 `letsgo` 插件与本仓库所有公开可见的版本变更，作为每次版本更新说明（Release Notes）的唯一事实源。日常未发版改动应先记入 `## [Unreleased]`；执行 `scripts/release.sh <version>` 时会自动归档到对应版本标题下。

## [Unreleased]

## [0.0.13] - 2026-11-26

### 新增

- **多工单编排与极简提示词共用规则（`references/orchestration.md`）**（[ADR-0029](docs/adr/0029-minimal-prompts-and-orchestrator-choice.md)）：建立 `matt-flow` 与 `try-swarm` 共用的三档实施形态择优规范（单仓任务图用 `/implement-spec`，跨仓／含人工门禁／需协调板用 1 个宿主原生多智能体协调会话，独立小单或需逐单深度把关才拆新会话），禁止建议同时手动开启多个带阻塞依赖的顶层会话。

### 变更

- **极简提示词与脱离 `matt-flow` 前缀**（[ADR-0029](docs/adr/0029-minimal-prompts-and-orchestrator-choice.md)）：`matt-flow` 在门禁与新会话提示词采用最小上下文指针原则（通常 1 行，不抄写工单、spec、handoff 或 `AGENTS.md` 已有信息，依赖与门禁提醒放在代码块外）；进入单一实施形态的新会话按当前宿主直接输出原生极简指令，不再前置 `letsgo:matt-flow`。
- **`try-swarm` 编排器互斥择优选一**（[ADR-0029](docs/adr/0029-minimal-prompts-and-orchestrator-choice.md)）：当同时指定 `implement-spec`、`run_workflow` 等同类编排器时，禁止叠加并现场择优选一，在极简报告末尾提示避免下次重复叠加；选原生机制替代时禁止 worker 套娃调用原编排器。
- **`guide` 触发标签与停下接力代码块规范**（[ADR-0029](docs/adr/0029-minimal-prompts-and-orchestrator-choice.md)）：过程说明行按实读元数据标注 6 类触发标签（`可隐式`、`仅显式`、`仅隐式`、`内部路由`、`MCP 直调`、`内置工具`）；任何停下等待确认、授权或接力的节点均给出极简可复制代码块提示词，直接推进时不插播示范代码块；收尾输出简洁复盘总结与独立复用参考提示词代码块。

## [0.0.12] - 2026-11-26

### 新增

- **沉淀 `try-swarm` 协作约定**：在 `plugins/letsgo/skills/try-swarm/SKILL.md` 中新增防 stall 误报（worker 发起预计超 1 分钟的后台长任务前先发不含 `@` 的简短状态备忘，coordinator 遇 monitor 的 `[stall]` 通知先核查活跃成员与后台长任务再决定是否干预）与大型跨仓并行审查（≥3 个大型多端仓并行推进时推荐拆分 2 位独立 verifier 分流）两条协同约定。

## [0.0.11] - 2026-11-25

### 变更

- **`skill-walk` 更名并扩展为 `guide`**（[ADR-0028](docs/adr/0028-guide-skill-and-rules-update.md)）：将显式技能 `letsgo:skill-walk` 升级为 `letsgo:guide`（菜单显示 `letsgo: guide`），覆盖范围从用户指定的技能扩展为当前宿主客户端具备的各类能力（skill、MCP 工具与内置工具）。支持按“本次消息明确指定 > 上下文明确选用 > 默认全部能力”识别能力范围，经两段低耗筛选后直接推进可自动或直接调用的能力，对需显式调用的技能默认停下给出原生命令提示词（调用时显式授权也可代为执行），范围外明显更合适时直接采用并标 `（范围外）`，缺少必要支持时检索宿主市场且只报告不安装。
- **放松 `matt-flow` 选型措辞**（[ADR-0028](docs/adr/0028-guide-skill-and-rules-update.md)）：更新 `matt-flow` 描述及 `references/matt-route.md` 路线图规则，移除“最小必要”“最小技能序列”等限制性措辞，改为按当前需求的复杂度、清晰度与上下文状态现场评估并推荐单个技能或完整主线等合适技能组合。

### 移除

- **移除拷问收敛门禁（`references/grill-gate.md`）**（[ADR-0028](docs/adr/0028-guide-skill-and-rules-update.md)）：删除 `plugins/letsgo/skills/letsgo/references/grill-gate.md`，并从 `letsgo/SKILL.md` 的 `description` 与路由表中移除对应条目；`grilling`、`grill-me` 与 `grill-with-docs` 收敛后不再由插件隐式门禁拦截。

### 迁移说明

- 原 `/letsgo:skill-walk`（Codex：`$letsgo:letsgo:skill-walk`）已迁移为 `/letsgo:guide`（Codex：`$letsgo:letsgo:guide`）。
- 如需在 `grilling`、`grill-me` 或 `grill-with-docs` 收敛后只报告不实施，请在调用时显式声明，例如：`/grill-with-docs …（方案明确后只报告，不实施）`。

## [0.0.10] - 2026-11-25

### 规范与基线

- **统一裸 `x.y.z` 版本号与市场锁定基线**（[ADR-0027](docs/adr/0027-bare-xyz-versioning.md)）：三端清单（`.claude-plugin/plugin.json`、`.codex-plugin/plugin.json`、`.antigravity-plugin/plugin.json`）的 `version`、市场清单（`.claude-plugin/marketplace.json`、`.agents/plugins/marketplace.json`）的 `source.ref` 以及 Git 发布标签统一采用无 `v` 前缀的裸 `x.y.z`；明确当前处于 `0.0.x` 制作期且默认仅递增 `z`，修改 `x` 或 `y` 须经维护者同意并传入 `scripts/release.sh --allow-xy-bump`。
- **三端共用 10 技能结构基线**（[ADR-0017](docs/adr/0017-minimal-plugin.md)、[ADR-0018](docs/adr/0018-single-skills-directory.md)、[ADR-0025](docs/adr/0025-git-wrap-skill.md)、[ADR-0026](docs/adr/0026-0.0.8-skills-update.md)）：Codex、Claude Code 与 Antigravity 共用唯一 `plugins/letsgo/skills/` 目录，收敛为 1 个隐式基础规则技能（`letsgo`）与 9 个显式技能（`stepping-begin`、`stepping-doit`、`stepping-finish`、`write-an-article`、`matt-flow`、`prove-it`、`skill-walk`、`try-swarm`、`git-wrap`）。
- **无事件钩子硬性约束与校验门禁**（[ADR-0010](docs/adr/0010-no-hooks-skills-carry-rules.md)）：插件不使用 `hooks/`、`rules/` 目录或任何宿主事件钩子，全部规则与行为通过技能与 `references/` 承载，并由 `scripts/validate.py` 与 `scripts/tests/` 强制门禁校验。
- **运行时载荷隔离**：版本演进与发版治理规范仅保存在仓库根级与 `docs/` 下，不写入 `plugins/letsgo/` 插件载荷；私人资料仅保存于用户本机 `~/.agents/letsgo/personal/`。
