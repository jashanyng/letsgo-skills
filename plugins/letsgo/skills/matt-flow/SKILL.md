---
name: "letsgo:matt-flow"
description: 仅在显式调用时，借助 ask-matt 为用户需求现场评估并选用适合的 mattpocock-skills 技能或最小必要组合，自动串联无需用户判断的相邻步骤，并在门禁处给出可直接使用的提示词。
disable-model-invocation: true
---

# letsgo: matt flow

遵守[语言约定](../letsgo/references/language.md)与[matt 路线与门禁规范](../letsgo/references/matt-route.md)；其他规则按[letsgo 规则入口](../letsgo/SKILL.md)命中时读取。

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
- 需要新开会话时，每条提示词各放一个代码块，以本技能显式调用开头、后接任务说明（Claude Code 与 Antigravity 为 `/letsgo:matt-flow`，Codex 为 `$letsgo:letsgo:matt-flow`；Antigravity 只识别位于开头的命令），使新会话沿用本技能的规则。
- 每条写明对应的 handoff 文件或工单、工作目录与分支、完成标志，标明哪些可以立即并行、哪些要等哪个会话完成；不同会话不得修改同一批文件。
