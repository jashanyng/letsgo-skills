# 新增显式技能 matt-flow

> 状态：2026-11-22 更新——路线规划明确按需求现场评估选用“适合的”单个技能或最小必要组合（不预设固定待定分支），门禁输出移除第 4 项“下一步”，Git 收尾引用随 [ADR-0021](0021-conditional-git-delivery.md) 对齐；2026-11-22 新增对照技能 `matt-guide` 并抽取共用规则 `matt-route.md`（[ADR-0024](0024-matt-guide-skill.md)），不再是唯一 matt 入口；2026-11-24 经 [ADR-0026](0026-v360-skills-update.md) 移除 `matt-guide`，`matt-flow` 恢复为唯一的 mattpocock-skills 自动串联入口，`matt-route.md` 回归仅供 `matt-flow` 读取。

修订 [ADR-0017](0017-minimal-plugin.md) 中“不引入流程概念、废除第三方技能登记”的部分，以及 [ADR-0019](0019-write-an-article-skill.md) 中技能数量的部分。

2026-11-21 决定新增显式技能 `matt-flow`（`name: "letsgo:matt-flow"`，菜单显示 `letsgo: matt flow`），作为把用户需求路由到 mattpocock-skills 的唯一入口。用户以它开头、后接需求即可，代替每次手工粘贴的附言；命令必须位于消息开头，因为 Antigravity 不识别位于末尾的命令（2026-11-21 实测，Claude Code 桌面端两种位置都可）。插件技能由 5 个变为 6 个。

- 技能路线完全取自 `ask-matt` 及各下游技能的 `SKILL.md`，letsgo 自身不定义任何阶段；mattpocock-skills 按“装了就用”引用，不登记为依赖，缺少时停止并说明安装方式。
- 授权边界：显式调用即授权在本会话读取并执行设了 `disable-model-invocation` 的 matt 技能，但只在两步之间无需用户判断时自动串联（`/to-spec` → `/to-tickets` → `/implement-spec`、可由模型调用的技能、`/diagnosing-bugs` 后的 `/retro`、发布到已配置的 Issue 跟踪器、Git 收尾）。访谈共识、原型结论、`/retro` 建议的取舍、`/wayfinder` 决策与 `/triage` 判定、需要新会话或清空上下文之处，以及 Git 收尾的停止情形，保留为门禁。
- 门禁输出首行沿用步进的进度标识，再写当前位置、代码块提示词、自动推进到何处、下一步或“整个需求已全部完成”；不使用步进的命令集与文件写入命令集。新会话提示词以本技能的显式调用开头，使新会话沿用同一规则。

## Considered Options

- **严格遵守 `disable-model-invocation`，每个技能都由用户手动调用**：对话轮次过多，用户无法离开。
- **全部自动串联**：会越过需要用户判断的节点；模型也无法自行清空上下文，逐单 `/implement` 无法正确执行。
- **在用户的需求后粘贴一段附言再调用 `/ask-matt`**：附言与规则分散在两处，无法随插件三端同步。
- **一条消息同时写 `/ask-matt` 与 letsgo 技能两个斜杠命令**：各宿主对第二个命令的识别不一致。

## Consequences

- 发布为 3.2.0（新增功能，不破坏已有调用）。
- `scripts/validate.py` 的 `EXPECTED_SKILLS` 加入 `matt-flow`；技能正文仍受 `RETIRED_TERMS` 约束。
- ADR-0017 废除的旧流程（需求分析、方案设计、方案实施等环节）仍然废除；matt-flow 只转述第三方技能自己的步骤。
