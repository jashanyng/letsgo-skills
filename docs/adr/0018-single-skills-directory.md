# 单一技能目录，基础规则并入隐式技能 letsgo

> 状态：技能列表已被 [ADR-0019](0019-write-an-article-skill.md) 修订（新增 `write-an-article`）。

修订 [ADR-0016](0016-support-antigravity.md) 的双目录分流与 [ADR-0017](0017-minimal-plugin.md) 的技能列表。

2026-11-20 决定插件只保留一份 `plugins/letsgo/skills/`，删除 Codex 专用副本 `skills-codex/`，并把 `_rules/`、`conventions` 与 `personal` 合并为隐式技能 `letsgo`。最终技能目录为 `letsgo`、`stepping-begin`、`stepping-doit`、`stepping-finish`。

当日实测三端对技能 `name` 的处理：

| `name` | Codex | Antigravity |
| --- | --- | --- |
| `stepping-begin` | `letsgo:stepping-begin` | `stepping-begin` |
| `letsgo:stepping-begin` | `letsgo:letsgo:stepping-begin` | `letsgo:stepping-begin` |
| `letsgo-stepping-begin` | `letsgo:letsgo-stepping-begin` | `letsgo-stepping-begin` |

Codex 总在 `name` 前加插件名，Antigravity 从不加（转换 Claude 清单时也不加），目录名对两者都不起作用；Claude Code 对 `letsgo:` 开头的 `name` 不重复加前缀。因此一份目录无法让三端调用名完全相同。

- stepping 技能的 `name` 写 `letsgo:<目录名>`：Claude Code 与 Antigravity 保持 `/letsgo:stepping-begin`，Codex 变为 `$letsgo:letsgo:stepping-begin`，菜单显示名仍由 `display_name`（`letsgo: stepping begin`）决定。
- 隐式技能 `name: letsgo`，`user-invocable: false`。Claude Code 可从斜杠菜单隐藏；Codex 与 Antigravity 没有隐藏机制，手动提到时只加载规则。
- 原 `_rules/` 的规则移到 `skills/letsgo/references/`，`INDEX.md` 的路由表并入 `letsgo/SKILL.md`；stepping 专用规则在 `references/stepping/`，stepping 技能以 `../letsgo/references/...` 引用。
- 原显式技能 `personal` 的流程保留为 `references/personal.md`，改由“用户要求创建或更新自己的 letsgo 私人资料”这一自然语言场景触发；写入前逐批确认不变。
- `agy plugin validate --strict` 会因 `name` 与目录名不一致给出警告；这是有意的取舍，非严格校验与安装均正常。

## Considered Options

- **保留 `skills-codex/` 双目录**：三端调用名完全一致，但每次修改都要同步两份。
- **`name` 不带前缀**：Codex 与 Claude Code 为 `letsgo:<名称>`，Antigravity 丢失前缀、易与其他插件重名。
- **`name` 用 `letsgo-<名称>`**：三端调用名都变化，Codex 与 Claude Code 中还会出现 `letsgo:letsgo-<名称>`。
- **符号链接共享**：`codex plugin add` 归档时忽略符号链接，不可行。

## Consequences

- 发布为 0.0.3；Codex 中 stepping 调用名、`personal` 的显式入口与 `conventions` 名称都发生变化。
- `scripts/validate.py` 要求技能目录正好为上述四个、禁止 `skills-codex/` 与 `_rules/` 复活，并按上述规则检查 `name` 与 `display_name`。
