# 不使用事件钩子，由技能承载规则

2026-11-02 决定 letsgo 插件的任何功能都不再通过事件钩子实现，这也是今后版本必须遵守的硬性规定。插件只通过两端安装插件后提供的技能与规则资料生效，不依赖开发仓库：

- 显式技能按相对路径读取 `_rules/`，并各自执行私人资料门禁与[语言约定](../../plugins/letsgo/skills/_rules/spec/references/language.md)。
- 普通对话的通用规则由唯一的隐式技能 `letsgo:conventions` 承载：它的描述列出命中场景，正文指向 `_rules/INDEX.md` 的条件路由；Claude Code 中以 `user-invocable: false` 隐藏于斜杠菜单。

此决策取代 [ADR-0008](0008-plugin-runtime-and-personal-context.md) 中由 `SessionStart` 钩子注入规则入口与会话规则的部分，以及 Claude Code 的 `PostToolBatch` 语言提醒。私人资料门禁的适用范围与目录见 [ADR-0011](0011-classified-personal-context-and-task-gates.md)。

## 取舍与后果

- 隐式技能由模型判断后选用，命中稳定性低于会话开始时的强制注入；作为交换，插件不再需要 Codex 的钩子信任审阅，也没有每次会话的固定注入。
- 普通对话的回复语言交给用户在客户端自行设置；用户可以在个人配置中自行保留语言提醒钩子，它不属于插件。
- `scripts/validate.py` 拒绝插件中出现 `hooks/` 目录、钩子配置文件、清单的 `hooks` 字段或技能 frontmatter 的 `hooks`，使该规定在发布前被强制检查。
- 同一版本把 `letsgo:setup` 更名为 `letsgo:personal`：两端菜单在前缀同样匹配时名称较短者在前，主入口 `letsgo:letsgo` 必须保持最短名称，校验脚本同样检查。
