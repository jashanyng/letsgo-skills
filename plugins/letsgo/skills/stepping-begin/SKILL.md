---
name: "letsgo:stepping-begin"
description: 仅在显式调用时，把用户的需求当作明确需求建立步进会话，并立即给出第一步的完整内容。
disable-model-invocation: true
---

# letsgo: stepping begin

遵守[语言约定](../letsgo/references/language.md)、[步进会话](../letsgo/references/stepping/workflow.md)和[步骤输出格式](../letsgo/references/stepping/instruction-format.md)；其他规则按[letsgo 规则入口](../letsgo/SKILL.md)命中时读取。

建立新的步进会话，只展示第一步，不执行步骤。

1. 把用户的需求当作明确需求：不做需求评估、方案讨论或追问。存在多种理解时取最合理的一种，在第一步开头用一行写明“按此理解：……”；用户之后的纠正按返工处理。能从环境、文件或上下文核实的事实由智能体自行核实。
2. 按步骤粒度把任务拆成有独立完成条件的步骤，保存在内部会话状态中。
3. 直接展示第一步的完整具体操作、完成证据和停止条件，不提示控制选项。
