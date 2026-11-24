# 精简插件：只保留基础规则、私人资料与步进技能

> 状态：技能列表与 `_rules/` 布局已被 [ADR-0018](0018-single-skills-directory.md) 修订；技能数量再经 [ADR-0019](0019-write-an-article-skill.md) 修订；流程概念与第三方技能登记的禁令经 [ADR-0020](0020-matt-flow-skill.md) 为 `matt-flow` 修订；技能数量再经 [ADR-0022](0022-swarm-up-skill.md) 修订；技能数量与共用规则范围再经 [ADR-0024](0024-matt-guide-skill.md) 与 [ADR-0025](0025-git-wrap-skill.md) 修订；技能列表、数量与规则范围再经 [ADR-0026](0026-v360-skills-update.md) 修订（移除 `matt-guide`，`swarm-up` 改为 `try-swarm`，新增 `prove-it`、`skill-walk` 及 `grill-gate.md`，共 10 个技能）。

取代 [ADR-0012](0012-task-types-delivery-and-flow.md) 与 [ADR-0013](0013-verification-depth-choice.md)，并修订 [ADR-0016](0016-support-antigravity.md) 中关于主入口与技能数量的部分。

2026-11-20 决定把 letsgo 插件精简为 5 个技能：隐式的 `conventions`（基础规则入口）、`personal`（私人资料）与 `stepping-begin`、`stepping-doit`、`stepping-finish`（步进指导）。删除主入口 `letsgo` 及 `oneshot-completion`、`tell-me`、`script-this-task`、`generate-scripts`、`obsidian-note`、`overview`、`study-skill`、`retell-skill`、`readme-guide`。

同时废除插件设计原则及其全部概念：任务流程（需求分析、方案设计、方案实施三个阶段及其环节，含更早的“目标定位 → 需求审议 → 方案共定 → 实施申请 → 开工清障 → 自主实施”）、需求类型与类型分组、交付方式、分类行、技能登记表、访谈分流、第三方技能登记，以及动手前由用户选择的九级验证深度。

- `stepping-begin` 把用户需求当作明确需求：不评估、不讨论方案、不追问；有多种理解时取最合理的一种并在第一步写明，纠正按返工处理。验证由智能体按改动风险自选，写进最后一步并如实报告。
- `_rules/` 改为平铺：共用与用户级规则（语言、私人资料与远程连接、浏览器、代码输出、文件位置、变更安全、Git 收尾、故障报告）直接放在 `_rules/`，步进专用规则放在 `_rules/stepping/`。
- 不再在 `stepping-begin` 中自动运行 `codegraph init`；是否建立索引由用户决定。
- 不再迁移旧版 `~/.agents/letsgo/personal.md`。

## Considered Options

- **保留任务流程，只删技能**：流程概念会继续约束仅剩的技能，与“直接执行明确需求”的目标冲突。
- **把三个 stepping 技能合成一个带参数的技能**：技能数更少，但调用变长，且显式控制不如三个独立命令清楚。
- **去掉 `conventions`**：插件更小，但不能使用事件钩子（[ADR-0010](0010-no-hooks-skills-carry-rules.md)），普通对话将不再应用任何基础规则。

## Consequences

- 发布为不兼容版本 3.0.0；三端更新后旧技能消失。
- `scripts/validate.py` 去掉任务流程、登记表、第三方依赖与工作树相关检查，保留清单、双目录同步、链接、无钩子与私人内容检查。
- 历史 ADR 保留原文作为记录；与本决定冲突之处以本 ADR 为准。
