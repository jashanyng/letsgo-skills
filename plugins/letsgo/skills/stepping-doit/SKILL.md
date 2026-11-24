---
name: "letsgo:stepping-doit"
description: 仅在显式调用时执行活跃步进会话的当前步骤，并展示下一步。
disable-model-invocation: true
---

# letsgo: stepping doit

遵守[语言约定](../letsgo/references/language.md)、[步进会话](../letsgo/references/stepping/workflow.md)和[步骤输出格式](../letsgo/references/stepping/instruction-format.md)；其他规则按[letsgo 规则入口](../letsgo/SKILL.md)命中时读取。

调用即授权智能体完成当前步骤，且只完成当前步骤。

1. 确认存在活跃的当前步骤，核对其目标、范围和停止条件。
2. 按执行方式与边界完成该步；必须由用户完成时，给出完整说明并等待反馈，不当作已完成。
3. 报告实施内容与完成证据。失败时报告已验证边界并给出返工步骤，不推进。
4. 成功且还有后继步骤时，把它设为当前步骤并完整展示，不执行；没有后继步骤时给出整体小结并写明“整个任务已全部完成”。
