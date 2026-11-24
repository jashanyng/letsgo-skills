---
name: "letsgo:stepping-finish"
description: 仅在显式调用时完成活跃步进会话范围内的全部剩余工作。
disable-model-invocation: true
---

# letsgo: stepping finish

遵守[语言约定](../letsgo/references/language.md)、[步进会话](../letsgo/references/stepping/workflow.md)和[步骤输出格式](../letsgo/references/stepping/instruction-format.md)；其他规则按[letsgo 规则入口](../letsgo/SKILL.md)命中时读取。

调用即授权智能体完成会话既定范围内的全部剩余步骤。

1. 确认存在活跃会话，按依赖关系逐步执行；只有互不依赖且授权边界相同的工作才并行。
2. 每个步骤都按其完成证据验证结果。必须由用户完成的步骤，停在该步并给出具体操作、完成证据和停止条件。
3. 全部成功后给出整体总结（已执行内容、验证结果、剩余风险），写明“整个任务已全部完成”；无法继续时停在已验证边界，说明失败证据、未完成项与所需的用户决定。
