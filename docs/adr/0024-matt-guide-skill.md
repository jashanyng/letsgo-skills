# 新增显式技能 matt-guide

> 状态：已废除，被 [ADR-0026](0026-v360-skills-update.md) 取代。

修订 [ADR-0017](0017-minimal-plugin.md)、[ADR-0020](0020-matt-flow-skill.md) 与 [ADR-0022](0022-swarm-up-skill.md) 中关于插件技能数量与 matt 路由入口的部分；与 [ADR-0025](0025-git-wrap-skill.md) 一并使插件技能由 7 个增至 9 个，发布为 3.5.0。

2026-11-22 决定新增显式技能 `matt-guide`（`name: "letsgo:matt-guide"`，菜单显示 `letsgo: matt guide`），与既有显式技能 `matt-flow`（调用即授权、自动串联）形成对照，作为偏重人工显式接力触发的 mattpocock-skills 路线入口。

- **动机**：`matt-flow` 通过读取下游 `SKILL.md` 代为执行设了 `disable-model-invocation: true` 的技能以换取同会话自动串联，适合希望减少交互轮次的场景；但当用户希望每遇到要求显式调用的 matt 技能都由自己发出原生命令，从而最大化获得宿主客户端对显式斜杠／`$` 命令的原生技能注入、权限边界与上下文控制时，需要一条“不代跑显式技能、只做路线规划与显式接力”的独立入口。
- **授权边界与首轮特许读取**：`matt-guide` 只允许显式调用（`disable-model-invocation: true`、`allow_implicit_invocation: false`）。仅在首轮特许读取 `ask-matt`（以及为规划路线与核实 `disable-model-invocation` 属性而只读查阅候选技能的 `SKILL.md`），不以读取 `SKILL.md` 代替显式调用去执行设了 `disable-model-invocation: true` 的 matt 技能。
- **隐式技能自动触发**：未设 `disable-model-invocation: true` 的模型可调用技能（如 `/tdd`、`/diagnosing-bugs`、`/prototype`、`/code-review`、`/pr`、`/research`、`/wizard`）保持原生隐式自动触发，路线首步或相邻步为此类技能时直接执行；在用户已触发的显式技能内部，其依赖的模型可调用技能（如 `/grill-with-docs` 驱动的 `grilling` 与 `domain-modeling`、`/tdd` 关联的 `codebase-design`）照常自动触发。
- **显式接力与统一原生命令门禁**：凡遇到设了 `disable-model-invocation: true` 的技能或需要人工拍板的节点一律停下进入门禁（若路线第 1 步即要求显式调用，首次回复给出路线图后立即停在第 1 步门禁）。无论是同会话继续还是需要清空上下文／新开会话（如 `/handoff` 后或逐单 `/implement`），代码块提示词统一直接以目标原生 matt 技能命令开头（Claude Code 与 Antigravity 为 `/<技能>`，Codex 为 `$<技能>`，不前置 `letsgo:matt-guide`），最大化宿主原生技能注入效果；新会话提示词附言写明对应 handoff 文件或工单、工作目录与分支、完成标志及后续提醒。
- **共用规则抽取**：将 `matt-flow` 与 `matt-guide` 共用的技能读取校验、按需现场路线评估及门禁／收尾输出格式抽取至 `plugins/letsgo/skills/letsgo/references/matt-route.md`，`letsgo/SKILL.md` 注明该文件只供 `matt-flow` 与 `matt-guide` 读取，避免规则在两份技能定义中重复维护。

## Considered Options

- **仅保留 `matt-flow`，靠用户在需求中临时叮嘱“不要代跑”**：临时指令容易在长对话中被“调用即授权”规则冲淡，且每次都要手写附言，无法稳定提供原生接力行为。
- **在 `matt-guide` 的新会话提示词中也前置 `/letsgo:matt-guide`**：虽可让新会话重读路线规则，但会占据命令开头位置，使目标原生 matt 技能退居附言（Antigravity 只识别消息开头命令），削弱宿主原生技能激活效果。
- **在 `matt-guide/SKILL.md` 复制一份路线与门禁规范**：违反“一条规则只写在一个文件里”的共用原则，后续修改容易导致 `matt-flow` 与 `matt-guide` 行为分叉。

## Consequences

- 与 [ADR-0025](0025-git-wrap-skill.md) 一并发布为 3.5.0（向后兼容新增功能，`matt-flow` 既有“调用即授权、自动串联”语义不变）。
- `matt-flow` 不再是唯一的 matt 路由入口，[ADR-0020](0020-matt-flow-skill.md) 随之更新状态批注；`plugins/letsgo/skills/letsgo/references/matt-route.md` 成为两条路由共用的单一事实来源。
- `scripts/validate.py` 的 `EXPECTED_SKILLS` 增补 `matt-guide`，同步更新三端 `plugin.json`、`GLOSSARY.md`、`docs/authoring.md`、`AGENTS.md` 与 `README.md`。
