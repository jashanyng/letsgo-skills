---
name: "letsgo:matt-flow"
description: 仅在显式调用时，借助 ask-matt 为用户需求现场评估并推荐 mattpocock-skills 技能或技能组合，自动串联无需用户判断的相邻步骤，并在多工单评估与门禁处给出极简可复制的提示词。
disable-model-invocation: true
---

# letsgo: matt flow

遵守[语言约定](../letsgo/references/language.md)、[matt 路线与门禁规范](../letsgo/references/matt-route.md)与[多工单编排与极简提示词](../letsgo/references/orchestration.md)；其他规则按[letsgo 规则入口](../letsgo/SKILL.md)命中时读取。

调用即授权：在本会话内读取并直接执行 mattpocock-skills 中设了 `disable-model-invocation: true` 的技能，范围限于路线图首步、下文“自动串联”及用户在门禁处的答复；首次回复给出路线图后直接开始执行第一步。

## 自动串联

以下情形不停下：

- `/to-spec` → `/to-tickets` → `/implement-spec`，在同一上下文中连续执行。
- 未设 `disable-model-invocation: true` 的技能（`/tdd`、`/code-review`、`/pr`、`/research` 等）按各自规则直接调用。
- `/diagnosing-bugs` 修复后运行 `/retro`，只给出建议。
- 发布到项目已配置的 Issue 跟踪器。

## 门禁

以下情形停下，等待用户：

- 访谈结束，确认已达成共识（路线确有待定分支时一并确认）。
- `/prototype` 得出结论。
- 决定采纳 `/retro` 的哪些建议。
- `/wayfinder` 的每个决策工单，以及 `/triage` 判定。
- 需要新会话或清空上下文：`/handoff`、逐单 `/implement`、上下文接近约 150k。

## 会话提示词

- 同一会话回复门禁时用户直接作答，无需再次调用。
- 需要新开会话或进入多工单实施前，先按上述多工单编排与极简提示词规范（`orchestration.md`）现场三档择优；每条提示词单独放入代码块并遵守最小上下文指针原则（通常 1 行，不重复抄写工单、spec、handoff 或仓库 `AGENTS.md` 已有信息）；依赖顺序、并行性、涉及仓库与门禁提醒写在代码块外极简注明。
- **脱离 `matt-flow` 前缀规则**：明确进入单一实施形态的新会话（单单 `/implement`、单仓 `/implement-spec`、或按当前宿主生成的原生多智能体一行指令）直接以目标原生指令开头，不再前置 `letsgo:matt-flow`；仅当新会话仍需自动串联多个设了 `disable-model-invocation: true` 的 matt 技能（如 `/handoff` 后继续主线规划串联）时，才以本技能显式调用开头（Claude Code 与 Antigravity 为 `/letsgo:matt-flow`，Codex 为 `$letsgo:letsgo:matt-flow`；Antigravity 只识别位于开头的命令）。
